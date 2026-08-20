#!/usr/bin/env python3
"""Writer that runs the model locally instead of calling an API. §4.2 component 2.

WHY THIS EXISTS, AND WHY IT IS BETTER THAN THE API PATH
-------------------------------------------------------
`writer.py`'s module docstring records a concession forced by hosted inference:
`2601.17768` traces API non-determinism to floating-point non-associativity
combined with **dynamic batching**, so batch composition depends on other
tenants' traffic. We had to write *"replicable in distribution, not reproducible
bit-for-bit"*.

**Running locally removes that.** We choose the batch, we set the seed, we own
the stack. The concession is narrowed to the part that is genuinely irreducible
(GPU floating-point order), and the recorded environment makes even that
checkable. For a repo whose whole argument is that its numbers can be
re-derived, this is not a cost-saving measure that happens to help — it is the
better methodology that also happens to be free.

⚠️ **Batch size is part of the provenance, not a tuning knob.** Changing it
changes the order of floating-point reductions and therefore, in principle, the
outputs. It is recorded on every generation and must not vary within a
comparison.

WHAT IS DELIBERATELY IDENTICAL TO THE API PATH
-----------------------------------------------
Sampling parameters, the JSONL archive, the resume key, redaction, and the
`Generation` record. Only the transport changes, so a switch of provider cannot
quietly change anything else — and `provider` is in the key, so archives from
two backends can never be merged by accident.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.writer import (  # noqa: E402
    SEED,
    TEMPERATURE,
    TOP_P,
    Generation,
    append_generation,
    generation_key,
)
from src.common.provenance import stamp  # noqa: E402

#: One item is the realized S4 path: both historical runners called
#: ``generate()``, which wraps ``generate_batch([item])``. The former default 8
#: was only constructor metadata and never a realized batch. S5 passes 1
#: explicitly and this default now tells the truth for new call sites.
DEFAULT_BATCH_SIZE = 1
REQUIRED_NF4_TRANSFORMERS = "5.15.0"


class LocalWriter:
    """Same contract as `Writer`, with the model in-process."""

    def __init__(
        self,
        model_id: str,
        *,
        arm: str = "bn",
        jsonl_path: str | Path,
        batch_size: int = DEFAULT_BATCH_SIZE,
        dtype: str = "float16",
        quantization: str | None = None,
        max_new_tokens: int = 80,
        model_path: str | None = None,
    ):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.model_id = model_id
        self.arm = arm
        self.provider = "local"
        self.jsonl_path = Path(jsonl_path)
        self.batch_size = batch_size
        self.max_new_tokens = max_new_tokens

        # T4 is Turing (sm_75): no bfloat16 and no FlashAttention-2. Gemma-3
        # ships bf16 weights, so they are cast to fp16 here -- a known risk for
        # the Gemma family, which is why the notebook's first cell generates and
        # PRINTS a sample before anything else runs.
        self._dtype = getattr(torch, dtype)
        torch.manual_seed(SEED)

        # `model_path` separates WHERE the weights load from (a Kaggle Models
        # mount, a local cache) from WHAT the model IS (`model_id`, which is the
        # provenance and part of every generation key). The JSONL always records
        # model_id; the load location is an environment fact and goes in _env.
        load_src = model_path or model_id
        self.tokenizer = AutoTokenizer.from_pretrained(load_src)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        # Left padding: with right padding a batched generate() continues from
        # pad tokens for the shorter prompts and produces garbage. Silent, and
        # it looks like a bad model rather than a bad harness.
        self.tokenizer.padding_side = "left"

        kw = {"dtype": self._dtype, "device_map": "auto"}
        if quantization:
            # CHECKED BEFORE THE LOAD, not after. transformers does not raise
            # when bitsandbytes is absent: it drops the quantization_config and
            # loads in fp16 -- 12.19B at ~24 GB against a 16 GB card -- so the
            # first symptom is an OOM 90 seconds in, with a traceback pointing
            # at CUDA rather than at the missing package. Twice on 2026-08-15.
            try:
                from transformers.utils import is_bitsandbytes_available
                available = is_bitsandbytes_available()
            except ImportError:  # older transformers
                try:
                    import bitsandbytes  # noqa: F401
                    available = True
                except ImportError:
                    available = False
            # transformers 5.0.0 (Kaggle's stock build) does not apply the
            # 4-bit config even with bitsandbytes present: it loads fp16 and
            # says nothing. The pilot ran on 5.15.0, where it works. Checked
            # because "bitsandbytes is installed" was true in BOTH the working
            # and the failing session, so availability alone is not the test.
            try:
                import transformers
                from packaging.version import parse as _V
                if _V(transformers.__version__) != _V(REQUIRED_NF4_TRANSFORMERS):
                    raise RuntimeError(
                        f"transformers {transformers.__version__} does not match "
                        f"the registered nf4 runtime {REQUIRED_NF4_TRANSFORMERS}. "
                        "The archive's generations were produced on that exact "
                        "version -- see results/env_snapshot_s4_kaggle.json. "
                        "Install the registered version before continuing."
                    )
            except ImportError:
                pass
            if not available:
                raise RuntimeError(
                    f"{quantization!r} quantisation was requested and "
                    "bitsandbytes is not available to transformers. Refusing to "
                    "load: without it the model loads in fp16, which is both a "
                    "different memory footprint and a DIFFERENT NUMERICAL PATH "
                    "from every other generation in this archive. Install a "
                    "bitsandbytes build matching this torch, or run on a card "
                    "that fits the unquantised model and register the change."
                )
            # 12.19B in fp16 is ~24 GB against a T4's 16 GB. Quantisation must be
            # IDENTICAL across arms or the comparison measures the quantiser.
            from transformers import BitsAndBytesConfig

            kw["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=self._dtype,
                bnb_4bit_quant_type=quantization,
                bnb_4bit_use_double_quant=True,
            )
            kw.pop("dtype")
        self.model = AutoModelForCausalLM.from_pretrained(load_src, **kw)
        self.model.eval()

        # A REQUESTED quantisation that did not happen must not pass silently.
        # On 2026-08-15 a 12B model requested as nf4 loaded at ~24 GB and died
        # of OOM mid-load; the traceback pointed at CUDA, not at the cause. If
        # bitsandbytes is missing or the config is ignored, the model still
        # "loads" -- in fp16, at 3.4x the memory -- and the only symptom is a
        # crash somewhere further on. Checked here, where the cause is legible.
        if quantization:
            loaded_4bit = bool(getattr(self.model, "is_loaded_in_4bit", False)) or (
                getattr(self.model.config, "quantization_config", None) is not None
            )
            if not loaded_4bit:
                try:
                    import bitsandbytes  # noqa: F401
                    hint = "bitsandbytes imports, so the config was ignored"
                except ImportError:
                    hint = "bitsandbytes is NOT installed in this environment"
                raise RuntimeError(
                    f"{quantization!r} quantisation was requested and the loaded "
                    f"model is not quantised -- {hint}. Refusing to continue: an "
                    "unquantised load is a different memory footprint AND a "
                    "different numerical path from every other generation in "
                    "this archive."
                )

        self._env = {
            "provider": "local",
            "model_id": model_id,
            "model_path": model_path,
            "dtype": dtype,
            "quantization": quantization,
            "batch_size": batch_size,
            "max_new_tokens": max_new_tokens,
            "device": str(next(self.model.parameters()).device),
            "torch": torch.__version__,
            "cuda": torch.version.cuda,
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        }

    def _render_chat(self, prompt: str) -> str:
        """Apply the model's own chat template.

        Not optional and not cosmetic: Gemma-3 expects `<start_of_turn>` turns,
        and feeding a raw string to an instruction-tuned model silently produces
        continuation rather than instruction-following. Both arms share a base,
        so both use the same template — but it is read from each model's own
        tokenizer rather than hard-coded, because assuming they match is the
        kind of assumption this project keeps getting caught by.
        """
        return self.tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True,
        )

    def _render_messages(self, messages: list[dict]) -> str:
        if not messages or any(
            m.get("role") not in {"user", "assistant", "system"}
            or not isinstance(m.get("content"), str)
            for m in messages
        ):
            raise ValueError("messages must contain valid role/content strings")
        return self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

    def generate_batch(self, items: list[dict]) -> list[Generation]:
        """Generate for a list of {prompt, plot_id, target_level, attempt}."""
        import torch

        if not items or len(items) > self.batch_size:
            raise ValueError(
                f"generate_batch received {len(items)} items; registered batch "
                f"size is {self.batch_size}"
            )
        seeds = {int(it.get("sample_seed", SEED)) for it in items}
        if len(seeds) != 1:
            raise ValueError("one local batch cannot mix sampling seeds")
        sample_seed = next(iter(seeds))
        torch.manual_seed(sample_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(sample_seed)
        texts = [
            self._render_messages(it["messages"])
            if it.get("messages") is not None
            else self._render_chat(it["prompt"])
            for it in items
        ]
        enc = self.tokenizer(
            texts, return_tensors="pt", padding=True, add_special_tokens=False
        ).to(self.model.device)

        with torch.no_grad():
            out = self.model.generate(
                **enc,
                do_sample=True,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                max_new_tokens=self.max_new_tokens,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        gens: list[Generation] = []
        prompt_len = enc["input_ids"].shape[1]
        for it, seq in zip(items, out):
            completion = seq[prompt_len:]
            text = self.tokenizer.decode(completion, skip_special_tokens=True).strip()
            n_completion = int((completion != self.tokenizer.pad_token_id).sum())
            gen = Generation(
                key=it.get("key") or generation_key(
                    it["plot_id"], it["target_level"], it.get("attempt", 1),
                    self.arm, self.model_id, "local",
                ),
                plot_id=it["plot_id"],
                target_level=it["target_level"],
                attempt=it.get("attempt", 1),
                arm=self.arm,
                model=self.model_id,
                provider="local",
                prompt=(it.get("prompt") or __import__("json").dumps(
                    it["messages"], ensure_ascii=False
                )),
                text=text,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                seed=sample_seed,
                # Recorded, and it matters: a completion that stops at the cap
                # was truncated, and a truncated comment is not a short comment.
                finish_reason=("length" if n_completion >= self.max_new_tokens
                               else "stop"),
                usage={
                    "prompt_tokens": int(prompt_len),
                    "completion_tokens": n_completion,
                    "total_tokens": int(prompt_len) + n_completion,
                },
                provenance=stamp(config_path=None, extra=self._env),
                condition=it.get("condition"),
                replicate_seed=it.get("replicate_seed"),
                call_role=it.get("call_role"),
            )
            append_generation(gen, self.jsonl_path)
            gens.append(gen)
        return gens

    def generate(self, *, prompt: str, plot_id: str, target_level: int,
                 attempt: int = 1, **kw) -> Generation:
        """Single-item convenience, so the loop can use this interchangeably.

        ⚠️ A batch of one is NOT the same computation as one item inside a batch
        of eight -- the reduction order differs. Whichever the pilot uses, Phase 5
        must use the same, and `batch_size` is recorded on every generation so a
        mismatch is visible rather than inferred.
        """
        return self.generate_batch([{
            "prompt": prompt, "plot_id": plot_id,
            "target_level": target_level, "attempt": attempt, **kw,
        }])[0]

    def generate_messages(
        self, *, messages: list[dict], plot_id: str, target_level: int,
        attempt: int = 1, **kw
    ) -> Generation:
        """Role-sensitive Phase-5 call; messages are archived verbatim as JSON."""
        return self.generate_batch([{
            "messages": messages, "plot_id": plot_id,
            "target_level": target_level, "attempt": attempt, **kw,
        }])[0]
