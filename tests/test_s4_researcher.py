"""Pin the Researcher's retry contract. It is checkable, so it is checked.

§4.2: "the original persona+plot query ALWAYS stays anchored; feedback keywords
only AUGMENT, never replace." The failure this prevents is query drift — three
attempts chasing the Reflector's last sentence, retrieving exemplars less and
less related to the plot. That reads in the results as the loop failing to
improve, when what actually happened is retrieval decaying, and nothing in
`trace` would distinguish the two without this guarantee.

No chromadb and no encoder are needed here: the anchoring and overlap logic are
pure functions, deliberately separated from the I/O for exactly that reason.

Run:  python -m pytest tests/test_s4_researcher.py -q
      python tests/test_s4_researcher.py          (no pytest needed)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agents.researcher import (  # noqa: E402
    OVERLAP_DISABLE_BELOW,
    TOP_K,
    build_query,
    overlap,
)

PLOT = "একটি গ্রামের ছেলে শহরে এসে সংগীতশিল্পী হতে চায়।"


def test_retry_query_keeps_the_original_as_a_prefix():
    base = build_query(PLOT)
    retry = build_query(PLOT, ["অভিনয়", "গান"])
    assert retry.startswith(base), (
        "the original query is not a prefix of the retry query — feedback has "
        "replaced rather than augmented, which is the query drift §4.2 forbids"
    )


def test_feedback_augments_rather_than_replaces():
    retry = build_query(PLOT, ["অভিনয়"])
    assert PLOT.strip() in retry and "অভিনয়" in retry


def test_empty_and_whitespace_feedback_changes_nothing():
    """A Reflector that returns nothing useful must not perturb retrieval."""
    base = build_query(PLOT)
    assert build_query(PLOT, []) == base
    assert build_query(PLOT, ["", "   "]) == base


def test_overlap_is_none_on_the_first_attempt():
    assert overlap(None, ("a", "b")) is None, (
        "attempt 1 has no previous retrieval; reporting 0.0 would be read as "
        "'re-retrieval changed everything' in the §4.6 dynamics table"
    )


def test_overlap_arithmetic():
    assert overlap(("a", "b", "c", "d"), ("a", "b", "c", "d")) == 1.0
    assert overlap(("a", "b"), ("c", "d")) == 0.0
    assert overlap(("a", "b", "c", "d"), ("a", "b", "x", "y")) == 0.5


def test_the_routing_trigger_is_the_spec_value_not_a_new_constant():
    """§4.2 supplies 50%; this file may not invent its own threshold."""
    assert OVERLAP_DISABLE_BELOW == 0.50
    assert TOP_K == 10


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
