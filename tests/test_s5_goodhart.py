from src.eval.analyze_s5_goodhart_bn import summaries


def _case(key, condition, attempts):
    return {"key": key, "condition": condition, "attempt_scores": attempts}


def test_goodhart_reports_selection_controlled_adjacent_transitions():
    scores = [
        _case("a", "rag_neural_loop", [
            {"attempt": 1, "verifier_a_target_probability": .4, "verifier_b_target_probability": .3},
            {"attempt": 2, "verifier_a_target_probability": .8, "verifier_b_target_probability": .5},
        ]),
        _case("b", "rag_neural_loop", [
            {"attempt": 1, "verifier_a_target_probability": .6, "verifier_b_target_probability": .6},
        ]),
    ]
    curve, paired = summaries(scores)
    assert [(x["attempt"], x["n_cases"]) for x in curve] == [(1, 2), (2, 1)]
    assert paired == [{
        "condition": "rag_neural_loop", "from_attempt": 1, "to_attempt": 2,
        "n_paired_cases": 1, "mean_a_delta": .4, "mean_b_delta": .2,
        "mean_a_minus_b_delta": .2,
        "interpretation": "same cases only; positive gap delta indicates widening A−B gap",
    }]
