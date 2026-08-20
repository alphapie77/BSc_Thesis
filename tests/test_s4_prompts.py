"""Pin shared-template parity without conflating zero-shot and RAG-only.

§5.1 row 3, not row 1, is α_lo: the frozen attempt-1 archive contains ten RAG
exemplars. Row 1 and row 3 still share one base renderer so the axis requirement
cannot drift — the artefact Huang et al. §5 document.

Run:  python -m pytest tests/test_s4_prompts.py -q
      python tests/test_s4_prompts.py          (no pytest needed)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agents.prompts import (  # noqa: E402
    EXPECTED_EXEMPLARS,
    PromptContractError,
    load_definition,
    render,
    row1_prompt,
)

PLOT = "একটি গ্রামের ছেলে শহরে এসে সংগীতশিল্পী হতে চায়।"
TEN = tuple(f"উদাহরণ {i}" for i in range(EXPECTED_EXEMPLARS))


def test_row1_is_the_zero_shot_renderer_with_nothing_added():
    """Row 1 is zero-shot and must stay distinct from RAG-only row 3."""
    for arm in ("bn", "en"):
        a = row1_prompt(plot=PLOT, target_level=1, arm=arm)
        b = render(plot=PLOT, target_level=1, arm=arm, exemplars=(), feedback=None)
        assert a == b, f"[{arm}] row 1 is not the zero-shot render"
        rag = render(plot=PLOT, target_level=1, arm=arm, exemplars=TEN)
        assert rag != a and "উদাহরণ 0" in rag


def test_stripping_exemplars_and_feedback_recovers_row1_byte_for_byte():
    """The shared base survives; exemplars/feedback remain real differences."""
    full = render(
        plot=PLOT, target_level=1, exemplars=TEN,
        previous_draft="আগের মন্তব্য", feedback="আরও নির্দিষ্ট করো",
    )
    stripped = render(plot=PLOT, target_level=1, exemplars=(), feedback=None)
    assert stripped == row1_prompt(plot=PLOT, target_level=1)
    # And the loop prompt must be a strict superset in content, not a rewrite:
    # every line of row 1 has to survive into the loop prompt.
    for line in stripped.splitlines():
        if line.strip():
            assert line in full, f"row-1 line vanished from the loop prompt: {line!r}"


def test_the_definition_comes_from_the_docs_artifact_not_from_code():
    """§4.2 requires the definition 'verbatim from Phase 2'."""
    for arm in ("bn", "en"):
        d = load_definition(arm)
        assert len(d) > 200, f"[{arm}] definition suspiciously short: {len(d)}"
        assert d in render(plot=PLOT, target_level=1, arm=arm)


def test_missing_markers_raise_rather_than_render_an_empty_definition(tmp_path=None):
    """A prompt with no definition looks like a working Writer producing junk."""
    import tempfile
    p = Path(tempfile.mkdtemp()) / "no_markers.md"
    p.write_text("nothing here", encoding="utf-8")
    try:
        load_definition("bn", path=p)
    except PromptContractError:
        return
    raise AssertionError("missing markers did not raise")


def test_short_retrieval_is_refused():
    """§4.2 fixes ten exemplars; a top-6 prompt is a different prompt."""
    try:
        render(plot=PLOT, target_level=1, exemplars=("a", "b"))
    except PromptContractError:
        return
    raise AssertionError("a 2-exemplar prompt was accepted")


def test_retired_vocabulary_never_reaches_a_prompt():
    """'persona' and bare 'cluster' were retired 2026-08-10 (decision 12)."""
    for arm in ("bn", "en"):
        text = render(plot=PLOT, target_level=1, arm=arm, exemplars=TEN).lower()
        for banned in ("persona", "audience type", "cluster"):
            assert banned not in text, f"[{arm}] retired term {banned!r} in the prompt"


def test_both_arms_demand_bangla_output():
    """The registered invariant of the language pilot: output is always Bangla."""
    assert "বাংলায়" in render(plot=PLOT, target_level=1, arm="bn")
    assert "in Bangla" in render(plot=PLOT, target_level=1, arm="en")


def test_the_prompt_actually_states_which_level_to_write():
    """Caught after 8 tests passed: `target_level` was validated and discarded.

    The definition block describes BOTH levels, so a prompt that never names the
    target leaves the model to pick one. Every generation would still look
    well-formed, the Critic would score it against a level nobody asked for, and
    the axis-control result would be noise with no visible cause.
    """
    from src.agents.prompts import BN_DIGITS

    for level in (0, 1):
        bn = render(plot=PLOT, target_level=level, arm="bn")
        # Bengali digits, matching the definition's own headings. With ASCII
        # digits the prompt would say "স্তর 1" while pointing at a section
        # headed "স্তর ১", leaving the model to infer they are the same thing.
        assert f"স্তর {BN_DIGITS[level]}" in bn, f"bn prompt lacks level {level}"
        assert f"স্তর {level}" not in bn, (
            f"bn prompt uses an ASCII digit for the level; the definition "
            f"headings use Bengali digits and the two must match"
        )
        en = render(plot=PLOT, target_level=level, arm="en")
        assert f"Level {level}" in en, f"en prompt lacks level {level}"


def test_the_target_line_follows_the_definition_not_precedes_it():
    """Ordering is a design choice, per 2601.08070 (negative constraints).

    Naming the target first would have the model read the two-level contrast
    already knowing its side, turning the other level's description into a list
    of things to avoid — the negative constraint smuggled in by ordering.
    """
    text = render(plot=PLOT, target_level=1)
    assert text.index(load_definition("bn")) < text.index("তোমাকে লিখতে হবে")


def test_level_must_be_0_or_1():
    try:
        render(plot=PLOT, target_level=2)
    except PromptContractError:
        return
    raise AssertionError("K=3 level accepted; K has been 2 since 2026-08-03")


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
