"""S4.5a — the `w` sensitivity fit.

These pin the things that would be wrong silently: the AUC's direction, the
reconstruction of `p1` from the Critic's asymmetric score, grouping by plot in
the held-out test, and the mapping from measurements to the three
pre-committed outcomes.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.eval.fit_w import (  # noqa: E402
    auc,
    classify,
    curve,
    marginal_value,
    verdict_flip_share,
)

CFG = yaml.safe_load((ROOT / "configs" / "s4_w.yaml").read_text(encoding="utf-8"))
SRC = (ROOT / "src" / "eval" / "fit_w.py").read_text(encoding="utf-8")


def _row(plot, level, neural, symbolic, arm="bn", words=10):
    return {"key": f"{plot}|{level}", "plot_id": plot, "arm": arm,
            "target_level": level, "n_words": words,
            "neural": neural, "symbolic": symbolic}


def test_auc_direction_and_ties():
    assert auc([1.0], [0.0]) == 1.0
    assert auc([0.0], [1.0]) == 0.0
    assert auc([0.5], [0.5]) == 0.5


def test_p1_is_reconstructed_from_the_asymmetric_score():
    """The Critic returns P(y = target_level), so a level-0 score of 0.9 means
    p1 = 0.1. Comparing the raw scores across classes would make a PERFECT
    scorer look like chance, because both classes would score high.
    """
    perfect = [_row("A", 1, 1.0, 1.0), _row("B", 0, 1.0, 1.0)]
    assert curve(perfect, [1.0])[0]["auc"] == 1.0
    inverted = [_row("A", 1, 0.0, 0.0), _row("B", 0, 0.0, 0.0)]
    assert curve(inverted, [1.0])[0]["auc"] == 0.0


def test_the_grid_spans_the_whole_range_including_both_endpoints():
    """w=0 and w=1 are the two points the marginal-value test is defined
    against, and the pipeline's old 0.5-0.8 grid presupposed the answer."""
    assert CFG["grid"]["w_min"] == 0.0
    assert CFG["grid"]["w_max"] == 1.0


def test_marginal_value_never_splits_a_plot_across_folds():
    """Both levels of a plot share a synopsis and ten exemplars."""
    scored = [_row(f"P{i}", lvl, 0.6, 0.4)
              for i in range(10) for lvl in (0, 1)]
    mv = marginal_value(scored, [0.0, 0.5, 1.0], 5)
    assert mv["n_folds"] == 5
    assert CFG["marginal_value"]["group_by"] == "plot_id"
    assert 'r["plot_id"] not in held' in SRC


def test_flat_scores_give_no_verdict_sensitivity():
    scored = [_row("A", 1, 0.7, 0.7), _row("B", 0, 0.7, 0.7)]
    assert verdict_flip_share(scored, [0.0, 0.5, 1.0]) == 0.0


def test_the_three_outcomes_are_the_registered_ones():
    """Wording matters: these strings are quoted in protocol.md §S4 decision 1
    and in the thesis, so a rename here silently breaks the pre-registration."""
    for name in ("SYMBOLIC_EARNS_ITS_PLACE", "SYMBOLIC_INERT", "SYMBOLIC_HARMS"):
        assert name in SRC
    mv_bad = {"folds_mixture_beats_neural_only": 0, "folds_neural_only_better": 5,
              "folds_tied": 0, "n_folds": 5}
    assert classify(0.3, mv_bad) == "SYMBOLIC_HARMS"
    mv_good = {"folds_mixture_beats_neural_only": 4, "folds_neural_only_better": 1,
               "folds_tied": 0, "n_folds": 5}
    assert classify(0.3, mv_good) == "SYMBOLIC_EARNS_ITS_PLACE"
    mv_flat = {"folds_mixture_beats_neural_only": 0, "folds_neural_only_better": 0,
               "folds_tied": 5, "n_folds": 5}
    assert classify(0.0, mv_flat) == "SYMBOLIC_INERT"


def test_inert_retains_the_symbolic_term():
    """Registered in decision 1: on `SYMBOLIC_INERT` the term stays, because the
    Reflector needs something that can name a failing rule. The report must say
    so rather than leaving the reader to infer a removal."""
    assert "RETAINED" in SRC
    assert "Reflector" in SRC


def test_no_single_w_is_written_anywhere():
    """The whole defect this step exists to avoid is a hand-written weight."""
    assert "0.6" not in CFG.get("grid", {}).values().__str__()
    assert "w_default" not in SRC and "DEFAULT_W" not in SRC


def test_verifier_b_is_unreachable_from_this_module():
    """Inviolable rule 6 — the fit uses the in-loop verifier only."""
    assert "verifier_b" not in SRC
