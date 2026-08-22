import pandas as pd
import pytest

from src.annotate.s5_human_eval_score import (
    HumanEvalScoreError, nominal_krippendorff_alpha, summarize, validate_responses,
)


def _key():
    return pd.DataFrame({"item_id": [f"H{i:03d}" for i in range(100)],
                         "case_key": [f"k{i}" for i in range(100)],
                         "plot_id": [f"p{i}" for i in range(100)],
                         "condition": ["c"] * 100, "replicate_seed": [42] * 100,
                         "target_level": [i % 2 for i in range(100)]})


def _responses():
    return pd.DataFrame([{"annotator": a, "item_id": f"H{i:03d}", "response": i % 2}
                         for a in "ABC" for i in range(100)])


def test_response_surface_is_exact_and_scored():
    joined = validate_responses(_key(), _responses(), ("A", "B", "C"))
    assert len(joined) == 300
    assert joined["correct"].mean() == 1.0


def test_missing_or_abstaining_response_is_rejected():
    with pytest.raises(HumanEvalScoreError, match="surface mismatch"):
        validate_responses(_key(), _responses().iloc[:-1], ("A", "B", "C"))
    bad = _responses().astype({"response": "string"}); bad.loc[0, "response"] = "U"
    with pytest.raises(HumanEvalScoreError, match="forced binary"):
        validate_responses(_key(), bad, ("A", "B", "C"))


def test_nominal_alpha_endpoints():
    assert nominal_krippendorff_alpha(pd.DataFrame([[0, 0, 0], [1, 1, 1]]).to_numpy()) == 1.0
    assert nominal_krippendorff_alpha(pd.DataFrame([[0, 1, 0], [1, 0, 1]]).to_numpy()) < 0


def test_summary_has_precommitted_intervals_and_target_disagreement():
    joined = validate_responses(_key(), _responses(), ("A", "B", "C"))
    rows, report = summarize(joined, n_boot=100, confidence=.95)
    annotator_rows = [r for r in rows if r["scope"] == "annotator"]
    assert all(r["accuracy_ci_low"] == r["accuracy_ci_high"] == 1.0 for r in annotator_rows)
    assert set(report["confusion_by_target_level"]) == {"target_level_0", "target_level_1"}
    assert report["disagreement_by_target_level"]["target_level_0"]["split_2_to_1_items"] == 0
