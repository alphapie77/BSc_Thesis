"""Unit tests for S4.6 dynamics and failure-packet selection."""
from src.eval.build_s4_failure_sheet import build_rows
from src.eval.report_s4_dynamics import analyse, normalized_edit_distance
from src.eval.score_s4_failure_taxonomy import compare


def _case(plot, level, gate, b, drafts=None):
    drafts = drafts or ["ক", "কথা", "কথাটা"]
    return {
        "plot_id": plot,
        "target_level": level,
        "attempts": [
            {
                "attempt": i + 1,
                "gate_score": gate[i],
                "symbolic_score": 0.2 + 0.1 * i,
                "verifier_b_score": b[i],
                "draft": drafts[i],
            }
            for i in range(3)
        ],
    }


def test_normalized_edit_distance_edges_and_symmetry():
    assert normalized_edit_distance("", "") == 0.0
    assert normalized_edit_distance("", "abc") == 1.0
    assert normalized_edit_distance("abc", "adc") == 1 / 3
    assert normalized_edit_distance("abc", "adc") == normalized_edit_distance("adc", "abc")


def test_stopping_counts_are_not_emitted_best_attempt_counts():
    cases = [
        _case("p0", 0, [0.8, 0.1, 0.2], [0.4, 0.3, 0.2]),
        _case("p1", 1, [0.1, 0.8, 0.2], [0.1, 0.7, 0.2]),
        _case("p2", 1, [0.1, 0.2, 0.3], [0.9, 0.1, 0.2]),
    ]
    out = analyse(cases, 0.5)
    policy = out["global"]["policy"]
    assert policy["accepted_stop_counts"] == {"1": 1, "2": 1, "3": 0}
    assert policy["emitted_attempt_counts"] == {"1": 1, "2": 1, "3": 1}
    assert policy["gave_up_count"] == 1


def test_oracle_is_never_below_a_selected_forced_three():
    cases = [
        _case("p0", 0, [0.8, 0.1, 0.2], [0.2, 0.9, 0.3]),
        _case("p1", 1, [0.1, 0.8, 0.2], [0.1, 0.7, 0.9]),
    ]
    oracle = analyse(cases, 0.5)["global"]["oracle_diagnostic"]
    assert oracle["best_of_three_b_oracle"] >= oracle["forced3_a_selected_b"]
    assert oracle["status"].startswith("post_hoc")


def test_ab_direction_crosstab_preserves_proxy_disagreement():
    cases = [
        _case("p0", 0, [0.1, 0.9, 0.2], [0.8, 0.1, 0.2]),
        _case("p1", 1, [0.1, 0.2, 0.3], [0.1, 0.2, 0.3]),
    ]
    cross = analyse(cases, 0.5)["global"]["transitions"][0]["a_b_direction_crosstab"]
    assert cross == {"a_up__b_down": 1, "a_up__b_up": 1}


def test_failure_sheet_contains_only_three_time_gate_failures_and_blank_codes():
    cases = [
        _case("p0", 0, [0.1, 0.2, 0.3], [0.2, 0.3, 0.4]),
        _case("p1", 1, [0.1, 0.8, 0.2], [0.2, 0.3, 0.4]),
    ]
    plots = [
        {"plot_id": "p0", "title_bn": "শূন্য", "synopsis": "কাহিনি শূন্য"},
        {"plot_id": "p1", "title_bn": "এক", "synopsis": "কাহিনি এক"},
    ]
    rows = build_rows(cases, plots, 0.5)
    assert [row["case_id"] for row in rows] == ["p0:L0"]
    assert rows[0]["emitted_attempt"] == 3
    assert rows[0]["emitted_draft"] == "কথাটা"
    assert rows[0]["wrong_sentiment"] == ""
    assert rows[0]["other_label"] == ""


def test_taxonomy_agreement_keeps_degenerate_kappa_explicit():
    base = {
        "case_id": "p0:L0", "wrong_sentiment": "0", "too_short": "0",
        "off_topic": "0", "template_repeat": "0",
        "register_or_honorific": "0", "other": "0",
    }
    result, disagreements = compare([base], [base])
    assert result["micro_binary_agreement"] == 1.0
    assert result["micro_binary_cohen_kappa"] is None
    assert disagreements == []


def test_taxonomy_scorer_emits_only_actual_disagreements():
    left = {
        "case_id": "p0:L0", "wrong_sentiment": "0", "too_short": "1",
        "off_topic": "0", "template_repeat": "0",
        "register_or_honorific": "0", "other": "0",
    }
    right = {**left, "too_short": "0", "other": "yes"}
    result, disagreements = compare([left], [right])
    assert result["n_disagreements"] == 2
    assert {(row["category"], row["coder_a"], row["coder_b"])
            for row in disagreements} == {("too_short", 1, 0), ("other", 0, 1)}
