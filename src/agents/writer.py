#!/usr/bin/env python3
"""Writer -- the only generative component. §4.2 component 2.

THE THING THAT SHAPED THIS FILE
-------------------------------
§4.2 says "temp 0.8, top_p 0.9, **seed logged**", which reads as though logging
the seed makes a run repeatable. **For a hosted API it does not.** `2601.17768`
(LLM-42, UW/Microsoft): non-determinism arises from floating-point
non-associativity combined with **dynamic batching** -- so batch composition
depends on other tenants' traffic on Groq's servers, which we do not control,
cannot record, and cannot hold fixed. `2604.22411` closes the escape route:
even at T = 0, identical inputs can diverge.

So the seed is still sent and logged, and it is **not** the reproducibility
guarantee. **The archived generation is.** Every completed generation is
appended to JSONL *as it completes*, and that file is a primary artifact:
a trace that cannot be regenerated must never be deleted. Registered in
`protocol.md`, 2026-08-11.

That also solves a second problem for free. At free-tier throughput the full
Phase 5 is ~30 hours of wall clock; a run that cannot resume loses hours to any
429 or dropped connection. S3.2 attempt 1 lost ~4 GPU-hours crashing at arm 6
of 7 because its checkpoint did not survive. Append-as-you-go means a re-run
skips what is already on disk.

WHAT THIS FILE REFUSES TO DO
----------------------------
- It does not score. That is the Critic's, and the Critic is deterministic.
- It does not retry the *loop*. It retries the *HTTP call* on 429/5xx. Those are
  different things: loop attempts cost quality signal and are counted in
  E[calls]; transport retries are not and must never be, or decision 19's cost
  model silently inflates.
"""

from __future__ import annotations

import json
import random
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import stamp  # noqa: E402
from src.common.secrets import redact, require  # noqa: E402

COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"

#: §4.2, verbatim and not tuned here. Recorded as conventional-but-unTUNED:
#: `2408.13586` is the standard for selecting these, `2407.01082` (min-p)
#: criticises top-p outright, and min-p is not exposed by this API -- so the
#: pair is retained and its status stated rather than defended.
#: ref: docs/protocol.md deviations 2026-08-11, docs/research_pipeline_en.md §4.2
TEMPERATURE = 0.8
TOP_P = 0.9

#: Inviolable rule 2's global seed, sent to the API and logged. NOT a
#: reproducibility guarantee -- see the module docstring.
SEED = 42

#: Transport-level retry only. These are NOT loop attempts and are never counted
#: in E[calls]; conflating them would inflate decision 19's cost model.
MAX_TRANSPORT_RETRIES = 6
BACKOFF_BASE_SECONDS = 2.0

#: Free-tier tokens per minute, measured rather than assumed: the pilot's
#: observed throughput matched 6,000 TPM and not the developer tier's 250,000.
#: ref: results/s4_groq_preflight.json + the 2026-08-11 rate-limit deviation.
FREE_TIER_TPM = 6000

#: Spend at most this share of the budget, so a burst does not trip the limit
#: on the boundary. Not tuned -- it is headroom, and the cost of being wrong in
#: the generous direction is a 429 and an exponential backoff, which is strictly
#: worse than waiting a few seconds.
TPM_SAFETY_FRACTION = 0.85

#: Rate-limit headers Groq returns on completions. Captured on every call
#: because the account tier is still unknown and it changes the runtime plan by
#: ~40x -- the /models endpoint does not report them (s4_groq_preflight).
LIMIT_HEADERS = (
    "x-ratelimit-limit-requests",
    "x-ratelimit-limit-tokens",
    "x-ratelimit-remaining-requests",
    "x-ratelimit-remaining-tokens",
    "x-ratelimit-reset-requests",
    "x-ratelimit-reset-tokens",
    "retry-after",
)


@dataclass
class Generation:
    """One completed generation, with everything needed to interpret it later.

    This IS the reproducibility artifact, so it records what a re-run cannot
    recover: the exact prompt, the model string, the sampling parameters, and
    the provider's own response identifiers.
    """

    key: str
    plot_id: str
    target_level: int
    attempt: int
    arm: str
    model: str
    prompt: str
    text: str
    temperature: float
    top_p: float
    seed: int
    finish_reason: str | None
    usage: dict = field(default_factory=dict)
    response_id: str | None = None
    system_fingerprint: str | None = None
    rate_limits: dict = field(default_factory=dict)
    transport_retries: int = 0
    provenance: dict = field(default_factory=dict)


def generation_key(plot_id: str, target_level: int, attempt: int, arm: str, model: str) -> str:
    """Identity of a generation, for resume. Model and arm are part of it.

    Including them means switching arm or model does not silently reuse a
    generation produced under different conditions -- which would look like a
    completed run and be a mixed one.
    """
    return f"{plot_id}|L{target_level}|a{attempt}|{arm}|{model}"


def completed_keys(jsonl_path: str | Path) -> set[str]:
    """Keys already on disk. Corrupt trailing lines are skipped, not fatal.

    A run killed mid-write leaves a partial final line. Refusing to start
    because of it would turn a recoverable interruption into a lost run, which
    is the failure this whole append-as-you-go design exists to avoid.
    """
    path = Path(jsonl_path)
    if not path.exists():
        return set()
    keys: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            keys.add(json.loads(line)["key"])
        except Exception:
            continue
    return keys


def append_generation(gen: Generation, jsonl_path: str | Path) -> None:
    """Append one generation, redacted, with a trailing newline. Flushed."""
    path = Path(jsonl_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = redact(json.dumps(asdict(gen), ensure_ascii=False))
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(payload + "\n")
        fh.flush()


class Writer:
    """One generative call per invocation. No loop logic lives here."""

    def __init__(
        self,
        model: str,
        *,
        arm: str = "bn",
        jsonl_path: str | Path,
        tpm_budget: int | None = FREE_TIER_TPM,
    ):
        self.model = model
        self.arm = arm
        self.jsonl_path = Path(jsonl_path)
        self._key = require("GROQ_API_KEY")
        self._tpm = tpm_budget
        # (timestamp, tokens) for the last minute. Pacing PROACTIVELY is much
        # cheaper than reacting to 429s: the reactive path costs a wasted
        # request plus an exponential backoff that quickly reaches 32 and 64
        # seconds, so a run that trips the limit repeatedly spends most of its
        # wall clock asleep having already been refused.
        self._spend: list[tuple[float, int]] = []

    def _pace(self, estimated_tokens: int) -> float:
        """Sleep just long enough to stay inside the budget. Returns seconds."""
        if not self._tpm:
            return 0.0
        budget = self._tpm * TPM_SAFETY_FRACTION
        now = time.monotonic()
        self._spend = [(t, n) for t, n in self._spend if now - t < 60.0]
        used = sum(n for _, n in self._spend)
        if used + estimated_tokens <= budget or not self._spend:
            return 0.0
        # Wait until the oldest entry falls out of the window.
        wait = 60.0 - (now - self._spend[0][0]) + 0.25
        if wait > 0:
            time.sleep(wait)
        return max(wait, 0.0)

    def generate(
        self,
        *,
        prompt: str,
        plot_id: str,
        target_level: int,
        attempt: int = 1,
        max_tokens: int = 200,
    ) -> Generation:
        """`max_tokens` is 200, not 512.

        A viewer comment is tens of tokens; the corpus median is 8 WORDS. 512
        was generous for no reason, and on a token-metered free tier generosity
        is paid for in wall clock. It is still several times the longest thing
        the corpus contains, so it cannot truncate a plausible generation --
        `finish_reason` is recorded per generation and would show it if it did.
        """
        import requests

        key = generation_key(plot_id, target_level, attempt, self.arm, self.model)
        # ~2.5 chars per token is deliberately pessimistic for Bangla: the
        # tokenizer fertility is an unmeasured covariate of our own (SS1.2), so
        # the pacer over-estimates rather than under-estimates its spend.
        estimated = len(prompt) // 2 + max_tokens
        self._pace(estimated)
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "seed": SEED,
            "max_tokens": max_tokens,
        }

        retries = 0
        while True:
            resp = requests.post(
                COMPLETIONS_URL,
                headers={
                    "Authorization": f"Bearer {self._key}",
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=120,
            )
            if resp.status_code == 200:
                break
            if resp.status_code in (429, 500, 502, 503, 504) and retries < MAX_TRANSPORT_RETRIES:
                # Honour the provider's own Retry-After when given; guessing a
                # shorter wait just spends the next request on another 429.
                wait = resp.headers.get("retry-after")
                delay = (
                    float(wait)
                    if wait and wait.replace(".", "", 1).isdigit()
                    else BACKOFF_BASE_SECONDS * (2**retries)
                )
                # Jitter: a fixed schedule makes every worker retry in lockstep.
                delay += random.uniform(0, 0.5)
                time.sleep(delay)
                retries += 1
                continue
            raise RuntimeError(
                redact(f"Groq HTTP {resp.status_code} after {retries} retries: "
                       f"{resp.text[:300]}")
            )

        data = resp.json()
        choice = data["choices"][0]
        usage = data.get("usage", {})
        self._spend.append((time.monotonic(), int(usage.get("total_tokens", estimated))))

        gen = Generation(
            key=key,
            plot_id=plot_id,
            target_level=target_level,
            attempt=attempt,
            arm=self.arm,
            model=self.model,
            prompt=prompt,
            text=choice["message"]["content"].strip(),
            temperature=TEMPERATURE,
            top_p=TOP_P,
            seed=SEED,
            finish_reason=choice.get("finish_reason"),
            usage=usage,
            response_id=data.get("id"),
            system_fingerprint=data.get("system_fingerprint"),
            rate_limits={h: resp.headers.get(h) for h in LIMIT_HEADERS if resp.headers.get(h)},
            transport_retries=retries,
            provenance=stamp(config_path=None),
        )
        append_generation(gen, self.jsonl_path)
        return gen
