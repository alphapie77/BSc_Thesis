"""Unit tests for prefix replay and explicit FORCED_3 semantics."""
from src.eval.fit_tau import _emit, candidate_thresholds, fit


def _case(plot, level, gate, b):
    return {
        "plot_id": plot,
        "target_level": level,
        "attempts": [
            {"attempt": i + 1, "gate_score": gate[i], "symbolic_score": 0.5,
             "verifier_b_score": b[i], "draft": f"d{i + 1}"}
            for i in range(3)
        ],
    }


def test_threshold_replays_prefix_and_counts_writer_plus_reflector_calls():
    c = _case("p", 0, [0.2, 0.7, 0.9], [0.1, 0.2, 0.3])
    assert _emit(c, 0.5)[0]["attempt"] == 2
    assert _emit(c, 0.5)[1] == 3


def test_tau_one_is_not_the_forced_three_endpoint():
    c = _case("p", 0, [1.0, 0.2, 0.3], [0.1, 0.2, 0.3])
    assert _emit(c, 1.0)[0]["attempt"] == 1
    assert _emit(c, 1.0)[1] == 1
    assert _emit(c, None)[1] == 5


def test_forced_three_uses_best_gate_and_earliest_tie():
    c = _case("p", 0, [0.8, 0.8, 0.1], [0.1, 0.9, 0.2])
    emitted, calls, gave_up = _emit(c, None)
    assert emitted["attempt"] == 1 and calls == 5 and not gave_up


def test_grid_comes_from_observed_scores_and_includes_zero():
    c = _case("p", 0, [0.2, 0.7, 1.0], [0.1, 0.2, 0.3])
    assert candidate_thresholds([c]) == [0.0, 0.2, 0.7, 1.0]


def test_symbolic_scores_do_not_change_frontier_or_selection():
    cases = [
        _case("p0", 0, [0.2, 0.7, 0.9], [0.2, 0.8, 0.7]),
        _case("p1", 1, [0.3, 0.8, 0.6], [0.3, 0.9, 0.5]),
    ]
    a = fit(cases, shuffles=20)
    for c in cases:
        for attempt in c["attempts"]:
            attempt["symbolic_score"] = 1.0 - attempt["symbolic_score"]
    b = fit(cases, shuffles=20)
    assert a["selection"] == b["selection"]
    assert a["frontier"] == b["frontier"]
