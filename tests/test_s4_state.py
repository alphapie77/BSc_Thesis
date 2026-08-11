"""Pin the loop state's history guarantees. §4.6 cannot be recomputed later.

The attempt distribution, the per-attempt score growth, and the hand-coded
taxonomy of 50 three-time failures are all read off `trace`. If `trace` is
wrong, those analyses are wrong in a way no downstream check can detect — and
regenerating the data means paying for every generation again.

Run:  python -m pytest tests/test_s4_state.py -q
      python tests/test_s4_state.py          (no pytest needed)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agents.state import MAX_ATTEMPTS, LoopState  # noqa: E402


def _state(**kw) -> LoopState:
    return LoopState(plot_id="BN001", plot="…", target_level=1, **kw)


def test_trace_entries_are_independent_snapshots():
    """The bug this exists to catch reads as a finding, not as a crash.

    With a shallow copy every trace row aliases the live lists, so all three
    attempts display the final attempt's values — which looks exactly like
    "the loop changed nothing across attempts", a publishable-sounding claim
    produced by a copying error.
    """
    s = _state()
    s.retrieved = ["a", "b"]
    s.draft = "draft 1"
    s.hybrid = 0.10
    s.failed_rules = ["F2_length"]
    s.advance()

    s.retrieved.append("c")
    s.draft = "draft 2"
    s.hybrid = 0.90
    s.failed_rules.append("F5_sentiment")

    first = s.trace[0]
    assert first["draft"] == "draft 1", "trace lost the first draft"
    assert first["retrieved"] == ["a", "b"], (
        f"trace row aliases live state: {first['retrieved']}"
    )
    assert first["failed_rules"] == ["F2_length"]
    assert first["hybrid"] == 0.10


def test_advance_clears_scores_so_a_stale_pass_cannot_survive():
    s = _state()
    s.draft, s.hybrid, s.verdict = "d1", 0.9, "PASS"
    s.neural_score, s.symbolic_score = 0.9, 0.9
    s.advance()
    assert s.verdict is None and s.hybrid is None, (
        "a previous attempt's verdict survived into the next attempt — a stale "
        "PASS would then be attributed to a draft it never scored"
    )


def test_advance_refuses_past_the_cap():
    s = _state()
    s.hybrid = 0.1
    for _ in range(MAX_ATTEMPTS - 1):
        s.advance()
        s.hybrid = 0.1
    assert s.attempt == MAX_ATTEMPTS
    try:
        s.advance()
    except RuntimeError:
        return
    raise AssertionError(
        "advance() went past the cap. §4.2 emits best-of-3 at attempt 3; it "
        "does not retry, and an extra attempt would corrupt E[calls]."
    )


def test_best_of_three_picks_the_highest_hybrid():
    s = _state()
    s.draft, s.hybrid = "d1", 0.20
    s.advance()
    s.draft, s.hybrid = "d2", 0.80
    s.advance()
    s.draft, s.hybrid = "d3", 0.50
    best = s.best_of_trace()
    assert best["draft"] == "d2", f"picked {best['draft']!r}"


def test_ties_break_toward_the_earliest_attempt():
    """A tie means the extra calls bought nothing, and the metric must say so.

    Decision 19's τ objective divides quality by E[calls]. Breaking ties toward
    the later attempt would credit the loop with an improvement it did not make
    while charging the calls it did make.
    """
    s = _state()
    s.draft, s.hybrid = "d1", 0.60
    s.advance()
    s.draft, s.hybrid = "d2", 0.60
    assert s.best_of_trace()["attempt"] == 1


def test_finalize_sets_gave_up():
    s = _state()
    s.draft, s.hybrid = "d1", 0.3
    best = s.finalize_give_up()
    assert s.gave_up is True and best["draft"] == "d1"


def test_state_carries_no_w_and_no_tau():
    """protocol.md §S4 decisions 1 and 2: neither has a value, and a default
    written here would silently become one the first time something read it."""
    fields = set(vars(_state()))
    leaked = {f for f in fields if f in {"w", "tau", "threshold", "weight"}}
    assert not leaked, f"state carries un-registered decision constants: {leaked}"


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
