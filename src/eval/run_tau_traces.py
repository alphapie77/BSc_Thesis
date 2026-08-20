#!/usr/bin/env python3
"""Generate the 60 three-attempt S4.5b traces and score them with Verifier-B.

Attempt 1 is reused byte-for-byte from the committed length-controlled Bangla
archive. Writer/Reflector retry calls are append-only and resumable. Verifier-B
loads only after all agent components and the generator have been released.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.agents.critic import Critic  # noqa: E402
from src.agents.graph import run_loop  # noqa: E402
from src.agents.reflector import Reflector  # noqa: E402
from src.agents.researcher import Researcher  # noqa: E402
from src.agents.run_pilot import load_dev_plots  # noqa: E402
from src.agents.writer import generation_key  # noqa: E402
from src.common.provenance import stamp, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402


def _rows(path: str | Path) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def _by_key(path: str | Path) -> dict[str, dict]:
    out = {}
    for row in _rows(path):
        out.setdefault(row["key"], row)  # append-only: first completed call wins
    return out


class CachedWriter:
    """Reuse attempt 1 and already archived retries before making a new call."""

    def __init__(self, base, cache: dict[str, dict], initial: dict[tuple[str, int], dict],
                 model: str, provider: str):
        self.base, self.cache, self.initial = base, cache, initial
        self.model, self.provider = model, provider

    def generate(self, *, prompt, plot_id, target_level, attempt, **kwargs):
        if attempt == 1 and (plot_id, target_level) in self.initial:
            return SimpleNamespace(text=self.initial[(plot_id, target_level)]["text"])
        key = generation_key(plot_id, target_level, attempt, "bn", self.model,
                             provider=self.provider)
        if key in self.cache:
            return SimpleNamespace(text=self.cache[key]["text"])
        generated = self.base.generate(
            prompt=prompt, plot_id=plot_id, target_level=target_level,
            attempt=attempt, **kwargs
        )
        # LocalWriter has already appended; cache the minimal value immediately.
        self.cache[key] = {"key": key, "text": generated.text}
        return generated


class CachedReflectorGenerator:
    """Give reflector calls a distinct archive key from Writer calls."""

    def __init__(self, cached: CachedWriter):
        self.cached = cached

    def __call__(self, *, prompt, plot_id, target_level, attempt, **kwargs):
        generated = self.cached.generate(
            prompt=prompt,
            plot_id=f"REFLECT:{plot_id}",
            target_level=target_level,
            attempt=attempt,
            **kwargs,
        )
        return generated.text


def main() -> int:
    set_seed()  # inviolable global-seed rule; first action in the entry point
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s4_tau_traces.yaml")
    ap.add_argument("--model-path", required=True)
    ap.add_argument("--verifier-b-path", required=True)
    args = ap.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))

    initial_rows = [
        r for r in _rows(cfg["input"]["attempt1_jsonl"])
        if r["arm"] == "bn" and int(r["attempt"]) == 1
    ]
    initial = {(r["plot_id"], int(r["target_level"])): r for r in initial_rows}
    expected = int(cfg["sample"]["n_plots"]) * len(cfg["sample"]["levels"])
    if len(initial) != expected:
        raise SystemExit(f"attempt-1 archive: expected {expected} Bangla cases, found {len(initial)}")

    idx = yaml.safe_load(Path("configs/s4_index.yaml").read_text(encoding="utf-8"))["index"]
    researcher = Researcher(
        idx["persist_dir"], idx["collection"], idx["encoder"], device="cpu"
    )
    critic = Critic(
        required_sklearn_version=str(cfg["runtime"]["scikit_learn"]),
        encoder_device="cpu",
    )

    from src.agents.local_writer import LocalWriter
    calls_path = cfg["output"]["calls_jsonl"]
    base = LocalWriter(
        cfg["model"], arm="bn", jsonl_path=calls_path,
        batch_size=int(cfg["runtime"]["batch_size"]),
        quantization=cfg["runtime"]["quantization"],
        max_new_tokens=int(cfg["runtime"]["max_new_tokens"]),
        model_path=args.model_path,
    )
    cached = CachedWriter(
        base, _by_key(calls_path), initial, cfg["model"], cfg["provider"]
    )
    reflector = Reflector(CachedReflectorGenerator(cached), arm="bn")

    cases = []
    plots = load_dev_plots(int(cfg["sample"]["n_plots"]))
    for p in plots:
        for level in cfg["sample"]["levels"]:
            result = run_loop(
                plot_id=p["plot_id"], plot=p["synopsis"], target_level=int(level),
                researcher=researcher, writer=cached, critic=critic,
                reflector=reflector, tau=1.0, arm="bn",
                force_all_attempts=True, length_controlled=True,
            )
            attempts = [*result.state.trace, result.state.snapshot()]
            cases.append({
                "plot_id": p["plot_id"],
                "target_level": int(level),
                "arm": "bn",
                "policy": "FORCED_3",
                "attempts": attempts,
            })
            print(f"trace {len(cases):02d}/{expected}: {p['plot_id']} L{level}", flush=True)

    # The independent evaluator never co-resides with the loop or generator.
    del reflector, cached, base, critic, researcher
    import gc
    gc.collect()
    try:
        import torch
        torch.cuda.empty_cache()
    except Exception:
        pass

    from src.eval.verifier_b_score import target_probabilities
    flat = [(case, a) for case in cases for a in case["attempts"]]
    b_scores = target_probabilities(
        [a["draft"] for _, a in flat],
        [case["target_level"] for case, _ in flat],
        artifact_path=cfg["verifier_b"]["artifact"],
        weights_path=args.verifier_b_path,
        batch_size=int(cfg["verifier_b"]["batch_size"]),
    )
    for (_, attempt), score in zip(flat, b_scores):
        attempt["verifier_b_score"] = score

    meta = stamp(args.config, {"policy": "FORCED_3", "evaluator": "Verifier-B"})
    text = "".join(json.dumps({**case, "provenance": meta}, ensure_ascii=False) + "\n"
                   for case in cases)
    write_text_lf(cfg["output"]["max_traces_jsonl"], text)
    print(f"wrote {len(cases)} complete traces -> {cfg['output']['max_traces_jsonl']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
