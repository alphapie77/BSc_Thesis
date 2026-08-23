"""Live two-level demo over the registered R1/Verifier-A loop.

The live Writer is hosted Gemma-4 and is explicitly not the Gemma-3 Writer that
produced S5. User plots and provider payloads are not persisted.
"""

from __future__ import annotations

import hashlib
import os
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import requests
import yaml

# The demo is PyTorch-only. Prevent an unrelated local Keras 3 installation
# from being auto-imported by Transformers before sentence-transformers loads.
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("USE_TF", "0")

from src.agents.critic import Critic
from src.agents.graph import run_loop
from src.agents.reflector import Reflector
from src.agents.researcher import Researcher
from src.agents.writer import Generation
from src.common.secrets import require
from src.common.seed import set_seed
from src.eval.gemini_judge import INTERACTIONS_URL, interaction_text

set_seed()


class DemoError(RuntimeError):
    pass


@dataclass(frozen=True)
class DemoGeneration:
    text: str
    usage: dict
    response_id: str | None
    model: str


class LiveGemmaWriter:
    """Minimal Interactions transport with no archive and no hidden fallback."""

    def __init__(self, config: dict, *, session=requests):
        self.model = config["model"]
        self.seed = int(config["seed"])
        self.thinking_level = config["thinking_level"]
        self.max_output_tokens = int(config["max_output_tokens"])
        self.timeout = int(config["request_timeout_seconds"])
        self.api_key = require("GOOGLE_API_KEY")
        self.session = session

    def _call(self, prompt: str) -> DemoGeneration:
        body = {
            "model": self.model,
            "input": prompt,
            "generation_config": {
                "seed": self.seed,
                "thinking_level": self.thinking_level,
                "max_output_tokens": self.max_output_tokens,
            },
        }
        response = self.session.post(
            INTERACTIONS_URL,
            headers={"x-goog-api-key": self.api_key, "Content-Type": "application/json"},
            json=body,
            timeout=self.timeout,
        )
        if response.status_code != 200:
            raise DemoError(f"Gemma API returned HTTP {response.status_code}")
        raw = response.json()
        if raw.get("status") != "completed":
            raise DemoError(f"Gemma interaction was not completed: {raw.get('status')!r}")
        return DemoGeneration(
            text=interaction_text(raw).strip(),
            usage=raw.get("usage", {}),
            response_id=raw.get("id"),
            model=raw.get("model", self.model),
        )

    def generate(self, *, prompt: str, plot_id: str, target_level: int,
                 attempt: int = 1, **_: Any) -> Generation:
        out = self._call(prompt)
        return Generation(
            key=f"demo|{plot_id}|L{target_level}|a{attempt}|{self.model}",
            plot_id=plot_id,
            target_level=target_level,
            attempt=attempt,
            arm="bn",
            model=self.model,
            prompt=prompt,
            text=out.text,
            temperature=0.0,
            top_p=1.0,
            seed=self.seed,
            finish_reason="completed",
            usage=out.usage,
            response_id=out.response_id,
            provider="gemini",
            provenance={"standing": "live_demo_not_scientific_result"},
        )


class DemoService:
    def __init__(self, config_path: str | Path = "configs/demo.yaml"):
        cfg = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
        self.cfg = cfg
        rag = cfg["rag"]
        self.researcher = Researcher(
            rag["persist_dir"], rag["collection"], rag["encoder"], device="cpu"
        )
        v = cfg["verifier"]
        self.critic = Critic(
            verifier_a_path=v["verifier_a"],
            symbolic_path=v["symbolic_scorer"],
            required_sklearn_version=v["required_sklearn"],
            encoder_device="cpu",
        )
        # Both registered components use normalized LaBSE. Sharing the exact
        # encoder avoids loading the same 471M model twice; no score changes.
        self.critic._encoder = self.researcher._encoder
        self.writer = LiveGemmaWriter(cfg["writer"])
        self.reflector = Reflector(
            lambda **kw: self.writer.generate(**kw).text, arm="bn"
        )
        self.tau = float(v["tau"])
        self._lock = threading.Lock()

    @staticmethod
    def _plot_id(plot: str, request_id: str) -> str:
        digest = hashlib.sha256(f"{request_id}\0{plot}".encode("utf-8")).hexdigest()
        return f"LIVE-{digest[:12]}"

    def generate(self, *, plot: str, target_levels: list[int], request_id: str) -> dict:
        if not plot.strip():
            raise DemoError("plot must not be empty")
        if len(plot) > 6000:
            raise DemoError("plot exceeds the 6000-character live-demo limit")
        if not target_levels or any(level not in (0, 1) for level in target_levels):
            raise DemoError("target_levels must contain level 0 and/or level 1")
        plot_id = self._plot_id(plot.strip(), request_id)
        outputs = []
        # The shared LaBSE model is not assumed thread-safe. One demo request at
        # a time also avoids burst-spending the account quota.
        with self._lock:
            for level in target_levels:
                result = run_loop(
                    plot_id=plot_id,
                    plot=plot.strip(),
                    target_level=level,
                    researcher=self.researcher,
                    writer=self.writer,
                    critic=self.critic,
                    reflector=self.reflector,
                    tau=self.tau,
                    arm="bn",
                    length_controlled=True,
                )
                attempts = [*result.state.trace, result.state.snapshot()]
                outputs.append({
                    "target_level": level,
                    "final": result.emitted,
                    "attempts": attempts,
                    "gave_up": result.gave_up,
                    "writer_calls": result.writer_calls,
                    "reflector_calls": result.reflector_calls,
                    "llm_calls": result.llm_calls,
                    "faithfulness": {
                        "status": "not_independently_validated",
                        "automated_claim": False,
                    },
                })
        return {
            "request_id": request_id,
            "plot_id": plot_id,
            "outputs": outputs,
            "backend": {
                "live_writer": self.writer.model,
                "reported_s5_writer": "google/gemma-3-12b-it",
                "rag": "R1-only, same-level top-10",
                "gate": "Verifier-A",
                "tau": self.tau,
                "verifier_b_loaded": False,
                "standing": "live_demo_not_scientific_result",
            },
        }
