"""S4.5a — the `w` sensitivity fit.

These pin the things that would be wrong silently: the AUC's direction, the
reconstruction of `p1` from the Critic's asymmetric score, grouping by plot in
the held-out test, and the mapping from measurements to the three
pre-committed outcomes.
"""

from __future__ import annotations

import sys
import json
import tempfile
from copy import deepcopy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.eval.fit_w import (  # noqa: E402
    InputContractError,
    auc,
    classify,
    curve,
    marginal_value,
    validate_inputs,
    verdict_flip_share,
)

CFG = yaml.safe_load((ROOT / "configs" / "s4_w.yaml").read_text(encoding="utf-8"))
SRC = (ROOT / "src" / "eval" / "fit_w.py").read_text(encoding="utf-8")
PREFLIGHT_SRC = (ROOT / "src" / "eval" / "preflight_w.py").read_text(encoding="utf-8")
CRITIC_SRC = (ROOT / "src" / "agents" / "critic.py").read_text(encoding="utf-8")
RUNNER = json.loads(
    (ROOT / "notebooks" / "s4_fit_w_kaggle.ipynb").read_text(encoding="utf-8")
)


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


def _write_archive(path: Path, n: int = 2, *, omit: str | None = None):
    rows = []
    for i in range(n):
        row = {
            "key": f"k{i}", "plot_id": f"P{i}", "arm": "bn",
            "target_level": i % 2, "text": f"text {i}",
        }
        if omit:
            row.pop(omit)
        rows.append(row)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def _validation_cfg(root: Path) -> dict:
    cfg = deepcopy(CFG)
    cfg["validation"]["expected_unique_generations_per_condition"] = 2
    cfg["inputs"] = [
        {"name": "length_controlled", "generations_jsonl": str(root / "lc.jsonl")},
        {"name": "free_length", "generations_jsonl": str(root / "free.jsonl")},
    ]
    return cfg


def test_all_declared_archives_are_mandatory():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        cfg = _validation_cfg(root)
        _write_archive(root / "lc.jsonl")
        try:
            validate_inputs(cfg)
        except InputContractError as exc:
            assert "free_length" in str(exc) and "missing" in str(exc)
        else:
            raise AssertionError("a missing registered condition was silently skipped")


def test_archive_count_and_fields_are_contracts():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        cfg = _validation_cfg(root)
        _write_archive(root / "lc.jsonl")
        _write_archive(root / "free.jsonl", n=1)
        try:
            validate_inputs(cfg)
        except InputContractError as exc:
            assert "1 unique generations" in str(exc)
        else:
            raise AssertionError("a short archive was accepted")

        _write_archive(root / "free.jsonl", omit="text")
        try:
            validate_inputs(cfg)
        except InputContractError as exc:
            assert "text" in str(exc)
        else:
            raise AssertionError("a malformed archive was accepted")


def test_runtime_and_pickle_mismatch_are_hard_failures():
    assert CFG["runtime"]["scikit_learn"] == "1.9.0"
    assert "required_sklearn_version" in CRITIC_SRC
    assert "symbolic scorer pickle version mismatch" in CRITIC_SRC
    assert "missing -- skipped" not in SRC


def test_w_preflight_is_read_only_and_keeps_the_evaluator_wall():
    assert "write_result" not in PREFLIGHT_SRC
    assert "write_text" not in PREFLIGHT_SRC
    assert "verifier_b" not in PREFLIGHT_SRC
    assert "validate_inputs" in PREFLIGHT_SRC


def test_w_runner_has_one_checkout_and_fails_on_command_errors():
    source = "\n".join(
        "".join(cell.get("source", [])) for cell in RUNNER["cells"]
        if cell.get("cell_type") == "code"
    )
    assert "/repo/repo" not in source
    assert "/kaggle/working/wfit_repo" in source
    assert "scikit-learn==1.9.0" in source
    assert "subprocess.run" in source and "check=True" in source
    assert "run_devplots.py" not in source
