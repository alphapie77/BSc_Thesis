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

#: Fixed, recorded, and NOT tuned. See the module docstring: this is a
#: provenance field. 8 is chosen to fit a 1B model plus ~4k-token prompts on a
#: single 16 GB T4 with headroom; if it must change, it changes for every arm at
#: once and the change is logged.
DEFAULT_BATCH_SIZE = 8


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
        max_new_tokens: int = 200,
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

        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        # Left padding: with right padding a batched generate() continues from
        # pad tokens for the shorter prompts and produces garbage. Silent, and
        # it looks like a bad model rather than a bad harness.
        self.tokenizer.padding_side = "left"

        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, dtype=self._dtype, device_map="auto"
        )
        self.model.eval()

        self._env = {
            "provider": "local",
            "model_id": model_id,
            "dtype": dtype,
            "batch_size": batch_size,
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

    def generate_batch(self, items: list[dict]) -> list[Generation]:
        """Generate for a list of {prompt, plot_id, target_level, attempt}."""
        import torch

        texts = [self._render_chat(it["prompt"]) for it in items]
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
                key=generation_key(
                    it["plot_id"], it["target_level"], it.get("attempt", 1),
                    self.arm, self.model_id, "local",
                ),
                plot_id=it["plot_id"],
                target_level=it["target_level"],
                attempt=it.get("attempt", 1),
                arm=self.arm,
                model=self.model_id,
                provider="local",
                prompt=it["prompt"],
                text=text,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                seed=SEED,
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
            "target_level": target_level, "attempt": attempt,
        }])[0]
