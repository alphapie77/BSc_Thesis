"""Pin the Writer's archive contract. The archive IS the reproducibility artifact.

Phase 4 generations cannot be reproduced by re-running: `2601.17768` traces the
non-determinism to floating-point non-associativity plus **dynamic batching**,
so batch composition depends on other tenants' traffic on Groq's servers — not
something a logged seed can hold fixed. `2604.22411` shows even T=0 diverges.

That makes the JSONL a primary artifact rather than an analysis convenience, and
these tests guard the properties that make it one: keys are stable, resume
works, a half-written line does not destroy a run, and no secret survives into
the file.

No network needed — the I/O helpers are pure by design.

Run:  python -m pytest tests/test_s4_writer.py -q
      python tests/test_s4_writer.py          (no pytest needed)
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agents.writer import (  # noqa: E402
    SEED,
    TEMPERATURE,
    TOP_P,
    Generation,
    append_generation,
    completed_keys,
    generation_key,
)


def _gen(**kw) -> Generation:
    base = dict(
        key="k", plot_id="BN001", target_level=1, attempt=1, arm="bn",
        model="llama-3.3-70b-versatile", prompt="p", text="t",
        temperature=TEMPERATURE, top_p=TOP_P, seed=SEED, finish_reason="stop",
    )
    base.update(kw)
    return Generation(**base)


def _tmp() -> Path:
    return Path(tempfile.mkdtemp()) / "gen.jsonl"


def test_the_key_includes_model_and_arm():
    """Resume must not reuse a generation made under different conditions.

    Without model and arm in the key, switching the pilot arm would find the
    old generations 'already done' — a mixed run that looks like a complete one.
    """
    a = generation_key("BN001", 1, 1, "bn", "llama-3.3-70b-versatile")
    assert a != generation_key("BN001", 1, 1, "en", "llama-3.3-70b-versatile")
    assert a != generation_key("BN001", 1, 1, "bn", "openai/gpt-oss-20b")
    assert a != generation_key("BN001", 1, 2, "bn", "llama-3.3-70b-versatile")


def test_append_then_resume_round_trips():
    path = _tmp()
    assert completed_keys(path) == set()
    append_generation(_gen(key="k1"), path)
    append_generation(_gen(key="k2"), path)
    assert completed_keys(path) == {"k1", "k2"}


def test_a_half_written_final_line_does_not_destroy_the_run():
    """A run killed mid-write leaves a partial line. That must be survivable.

    Refusing to start would turn a recoverable interruption into a lost run —
    the exact failure append-as-you-go exists to prevent, and the shape that
    cost S3.2 attempt 1 ~4 GPU-hours.
    """
    path = _tmp()
    append_generation(_gen(key="k1"), path)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write('{"key": "k2", "text": "trunca')
    assert completed_keys(path) == {"k1"}


def test_no_secret_survives_into_the_archive():
    """The trace records everything, which is what makes it dangerous."""
    key = "gsk_abcdefghijklmnopqrstuvwxyz"
    os.environ["GROQ_API_KEY"] = key
    path = _tmp()
    append_generation(_gen(key="k1", text=f"leaked {key} here"), path)
    body = path.read_text(encoding="utf-8")
    assert key not in body, "the API key survived into the JSONL archive"
    assert "REDACTED" in body


def test_archive_is_valid_jsonl_and_utf8_bangla_survives():
    path = _tmp()
    bangla = "ছবিটা অসাধারণ ছিল, নায়িকার অভিনয় মন ছুঁয়ে গেছে।"
    append_generation(_gen(key="k1", text=bangla), path)
    line = path.read_text(encoding="utf-8").strip()
    assert json.loads(line)["text"] == bangla, "Bangla text did not round-trip"


def test_sampling_params_are_the_spec_values():
    """§4.2 fixes these; this file may not quietly retune them."""
    assert (TEMPERATURE, TOP_P, SEED) == (0.8, 0.9, 42)


def test_every_generation_records_what_a_rerun_cannot_recover():
    """The archive replaces reproducibility, so it must carry the conditions."""
    fields = set(vars(_gen()))
    for needed in ("prompt", "model", "temperature", "top_p", "seed",
                   "usage", "response_id", "rate_limits", "provenance"):
        assert needed in fields, f"archive does not record {needed!r}"


def _run_all() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL  {fn.__name__}\n        {exc}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run_all())
