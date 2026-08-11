#!/usr/bin/env python3
"""Does the key work, and do the registered models exist on THIS account?

Turns `protocol.md` §S4 decision 3's rule -- *"model IDs are read from the live
catalogue with a retrieval date, never from memory"* -- into something the repo
executes rather than something a person remembers. Today it caught two things a
search summary got wrong, and a catalogue changes faster than a thesis is
written.

WHAT IT CHECKS, AND WHY EACH ONE HAS BURNED SOMEBODY
----------------------------------------------------
1. **The key loads and authenticates.** Cheapest possible failure to find now
   rather than 40 minutes into a generation run.
2. **Every registered model ID is actually served to this account.** A model ID
   that is correct in the docs and absent from your account fails at call time,
   not at config time. The pilot pair was already re-registered once because
   `qwen/qwen3.6-27b` turned out to be Preview.
3. **Rate-limit headers are captured to a result file.** The runtime plan rests
   on 6,000 TPM (free) versus 250K TPM (developer), and which tier this account
   is on is currently an assumption. Groq returns the real numbers in response
   headers; an assumption that can be measured should not stay an assumption.

Costs no generation tokens: `GET /models` is a catalogue read.

⚠️ Prints no secret. The key reaches `requests` and nothing else, and any text
written out passes through `redact()` first.

Run:  python src/agents/groq_preflight.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import write_result  # noqa: E402
from src.common.secrets import redact, require  # noqa: E402

MODELS_URL = "https://api.groq.com/openai/v1/models"

#: Re-registered 2026-08-11 after the live catalogue showed Qwen is a PREVIEW
#: model, which Groq documents as removable "at short notice" -- unacceptable for
#: an experiment that runs for weeks and must be reproducible.
#: ref: docs/protocol.md, deviations log 2026-08-11, and §S4 decision 3.
REGISTERED = {
    "pilot_arm_a": "llama-3.3-70b-versatile",
    "pilot_arm_b": "openai/gpt-oss-20b",
    "fallback_if_throughput_binds": "llama-3.1-8b-instant",
}

#: Headers Groq uses to report the account's real limits. Read rather than
#: assumed: the free/developer distinction changes the runtime plan by ~40x.
LIMIT_HEADERS = (
    "x-ratelimit-limit-requests",
    "x-ratelimit-limit-tokens",
    "x-ratelimit-remaining-requests",
    "x-ratelimit-remaining-tokens",
)


def main() -> int:
    key = require("GROQ_API_KEY")

    import requests

    try:
        resp = requests.get(
            MODELS_URL,
            headers={"Authorization": f"Bearer {key}"},
            timeout=30,
        )
    except Exception as exc:  # noqa: BLE001 - report, do not mask
        print(redact(f"REQUEST FAILED: {type(exc).__name__}: {exc}"))
        return 1

    if resp.status_code == 401:
        print(
            "AUTH FAILED (401). The key in .env is not accepted.\n"
            "  Check for a stray quote or trailing space, or create a new key\n"
            "  at console.groq.com -> API Keys. Revoke the old one."
        )
        return 1
    if resp.status_code != 200:
        print(redact(f"HTTP {resp.status_code}: {resp.text[:300]}"))
        return 1

    served = sorted(m["id"] for m in resp.json().get("data", []))
    limits = {h: resp.headers.get(h) for h in LIMIT_HEADERS if resp.headers.get(h)}

    print(f"auth OK. {len(served)} models served to this account.\n")
    missing = []
    for role, model_id in REGISTERED.items():
        ok = model_id in served
        print(f"  {'OK ' if ok else 'MISSING'}  {role:30s} {model_id}")
        if not ok:
            missing.append(model_id)

    if limits:
        print("\naccount rate limits, as reported by the API:")
        for k, v in limits.items():
            print(f"  {k:34s} {v}")
    else:
        print("\n⚠️ no rate-limit headers returned on this endpoint; the tier "
              "must be confirmed from a generation call instead.")

    write_result(
        {
            "auth_ok": True,
            "n_models_served": len(served),
            "registered": REGISTERED,
            "registered_all_present": not missing,
            "missing": missing,
            "rate_limit_headers": limits,
            "models_served": served,
        },
        "results/s4_groq_preflight.json",
        config_path=None,
    )
    print("\nwrote results/s4_groq_preflight.json")

    if missing:
        print(
            "\n🔴 A REGISTERED MODEL IS NOT AVAILABLE TO THIS ACCOUNT.\n"
            "   Do not substitute one silently. The pilot pair is pre-registered\n"
            "   in protocol.md §S4 decision 3; changing it needs a deviation row,\n"
            "   as the Qwen-is-Preview change got on 2026-08-11."
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
