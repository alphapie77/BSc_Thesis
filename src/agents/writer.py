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

#: Providers, keyed by name. Both are addressed through their OpenAI-compatible
#: chat-completions endpoint, so ONE code path serves both and the provider is a
#: config value rather than a fork.
#:
#: Why a provider is a first-class field rather than a detail: `2605.19537`
#: names the inference BACKEND a silent hyperparameter affecting reproducibility.
#: Two providers serving the same weights are not the same measurement, so the
#: provider is recorded on every generation and a comparison may never mix them.
#: ref: docs/protocol.md, 2026-08-12 provider deviation.
PROVIDERS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "models_url": "https://api.groq.com/openai/v1/models",
        "key_env": "GROQ_API_KEY",
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "models_url": "https://generativelanguage.googleapis.com/v1beta/openai/models",
        "key_env": "GOOGLE_API_KEY",
    },
    "mistral": {
        "url": "https://api.mistral.ai/v1/chat/completions",
        "models_url": "https://api.mistral.ai/v1/models",
        "key_env": "MISTRAL_API_KEY",
    },
    "nvidia": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "models_url": "https://integrate.api.nvidia.com/v1/models",
        "key_env": "NVIDIA_API_KEY",
    },
    "cerebras": {
        "url": "https://api.cerebras.ai/v1/chat/completions",
        "models_url": "https://api.cerebras.ai/v1/models",
        "key_env": "CEREBRAS_API_KEY",
    },
}

#: ⚠️ FREE-TIER LIMITS ARE NOT RECORDED HERE, ON PURPOSE.
#:
#: On 2026-08-11/12 three separate blog claims about free tiers failed against
#: the vendor's own documentation: Groq's Llama models were reported deprecated
#: and are Production; Cerebras was reported at "1M tokens/day free" and its
#: pricing page says a $5 trial; Mistral was reported at "1B tokens/month" and
#: its own docs say only "a free API tier with restrictive rate limits".
#:
#: **This corner of the ecosystem is documented by blogs, not by vendors.** So
#: no number from a secondary source enters this file. `provider_preflight.py`
#: reads the real limits from the account's own response headers, and those are
#: what any plan is built on.

#: Kept for the existing call sites; the provider table is the source of truth.
COMPLETIONS_URL = PROVIDERS["groq"]["url"]

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

#: The longest `Retry-After` this will obey before giving up instead.
#:
#: Honouring the provider's own number is right for a per-minute limit and
#: WRONG for a per-DAY one: an exhausted daily budget can return a Retry-After
#: of an hour or more, and sleeping on it turns a run into a silent hang with no
#: output and no way to tell it apart from a crash. That happened on
#: 2026-08-11. Above this the run STOPS and says why -- and because every
#: generation is already on disk, stopping costs nothing but the current call.
MAX_HONOURED_RETRY_AFTER = 120.0

#: Starting guess only. The real per-minute limit is READ FROM THE RESPONSE
#: HEADERS (`x-ratelimit-limit-tokens`) and replaces this on the first call.
#: Hard-coding it was wrong twice over: the observed header said 12,000, not
#: the 6,000 assumed, so the pacer slept 59 s it did not need to -- and a
#: provider is entitled to change the number without telling us.
FREE_TIER_TPM = 6000

#: Characters per token for our prompts. **MEASURED, not assumed**: 3,434
#: prompt chars produced 3,710 prompt tokens across the pilot's first 27
#: generations, i.e. **0.93 chars/token -- roughly one token per Bangla
#: character**. The earlier value of 2.5 under-estimated spend by 2.7x, which
#: is why the pacer could not keep the run inside the budget.
#: ref: docs/protocol.md, 2026-08-11 tokenizer-fertility deviation.
CHARS_PER_TOKEN = 0.93

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
    provider: str = "groq"
    rate_limits: dict = field(default_factory=dict)
    transport_retries: int = 0
    provenance: dict = field(default_factory=dict)
    # Phase-5 logical identity. Optional so frozen Phase-4 archives keep their
    # schema and old call sites remain valid.
    condition: str | None = None
    replicate_seed: int | None = None
    call_role: str | None = None


def generation_key(
    plot_id: str, target_level: int, attempt: int, arm: str, model: str,
    provider: str = "groq",
) -> str:
    """Identity of a generation, for resume. Provider, model and arm are in it.

    Including them means switching provider, arm or model does not silently
    reuse a generation produced under different conditions -- which would look
    like a completed run and be a mixed one. The PROVIDER is in the key for the
    same reason it is a field: two backends serving the same weights are not the
    same measurement (`2605.19537`).
    """
    return f"{plot_id}|L{target_level}|a{attempt}|{arm}|{provider}:{model}"


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
        provider: str = "groq",
        tpm_budget: int | None = FREE_TIER_TPM,
    ):
        if provider not in PROVIDERS:
            raise ValueError(f"provider must be one of {sorted(PROVIDERS)}, got {provider!r}")
        self.model = model
        self.arm = arm
        self.provider = provider
        self._endpoint = PROVIDERS[provider]["url"]
        self.jsonl_path = Path(jsonl_path)
        self._key = require(PROVIDERS[provider]["key_env"])
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

        key = generation_key(plot_id, target_level, attempt, self.arm,
                             self.model, self.provider)
        # ~2.5 chars per token is deliberately pessimistic for Bangla: the
        # tokenizer fertility is an unmeasured covariate of our own (SS1.2), so
        # the pacer over-estimates rather than under-estimates its spend.
        estimated = int(len(prompt) / CHARS_PER_TOKEN) + max_tokens
        slept = self._pace(estimated)
        if slept > 1.0:
            print(f"    pacing: slept {slept:.0f}s to stay under "
                  f"{self._tpm} TPM", flush=True)
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
                self._endpoint,
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
                asked = (
                    float(wait)
                    if wait and wait.replace(".", "", 1).isdigit()
                    else None
                )
                if asked is not None and asked > MAX_HONOURED_RETRY_AFTER:
                    limits = {h: resp.headers.get(h) for h in LIMIT_HEADERS
                              if resp.headers.get(h)}
                    raise RuntimeError(
                        f"Groq asked for a {asked:.0f}s wait ({asked/60:.0f} min). "
                        "That is a per-DAY budget, not a per-minute one -- a "
                        "per-minute limit resets in under a minute.\n"
                        f"  headers: {limits}\n"
                        "  Every generation so far is already on disk; re-running "
                        "the same command resumes from there.\n"
                        "  Options: wait for the daily reset, or move to the Groq "
                        "Developer plan (zero minimum spend, ~40x the limits)."
                    )
                delay = asked if asked is not None else BACKOFF_BASE_SECONDS * (2**retries)
                # Jitter: a fixed schedule makes every worker retry in lockstep.
                delay += random.uniform(0, 0.5)
                # Say so. Silence during a long sleep is indistinguishable from
                # a hang, which is exactly how this failure presented.
                print(f"    [{resp.status_code}] waiting {delay:.0f}s "
                      f"(retry {retries + 1}/{MAX_TRANSPORT_RETRIES})", flush=True)
                time.sleep(delay)
                retries += 1
                continue
            raise RuntimeError(
                redact(f"Groq HTTP {resp.status_code} after {retries} retries: "
                       f"{resp.text[:300]}")
            )

        data = resp.json()
        choice = data["choices"][0]
        # Adopt the provider's own limit once it tells us. Reading beats
        # guessing, and this is the number the pacer is trying to respect.
        header_tpm = resp.headers.get("x-ratelimit-limit-tokens")
        if header_tpm and header_tpm.isdigit():
            self._tpm = int(header_tpm)

        usage = data.get("usage", {})
        self._spend.append((time.monotonic(), int(usage.get("total_tokens", estimated))))

        gen = Generation(
            key=key,
            plot_id=plot_id,
            target_level=target_level,
            attempt=attempt,
            arm=self.arm,
            model=self.model,
            provider=self.provider,
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
