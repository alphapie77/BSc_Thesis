"""Unit tests for prefix replay, FORCED_3, and the Kaggle runtime contract."""
import json
from pathlib import Path

from src.eval.fit_tau import _emit, candidate_thresholds, fit


ROOT = Path(__file__).resolve().parents[1]


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


def test_tau_notebook_installs_and_gates_the_registered_nf4_runtime():
    """The runner refuses every version except the one used by attempt 1.

    This test exists because the first published notebook installed 5.14.1
    while LocalWriter required 5.15.0; unit-testing the runner alone missed the
    contradiction and made Save & Run All fail only after model setup.
    """
    notebook = json.loads(
        (ROOT / "notebooks" / "s4_tau_kaggle.ipynb").read_text(encoding="utf-8")
    )
    source = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    )
    writer = (ROOT / "src" / "agents" / "local_writer.py").read_text(
        encoding="utf-8"
    )
    assert "transformers==5.15.0" in source
    assert "transformers.__version__=='5.15.0'" in source
    assert "tau_repo_8178f26" in source
    assert "8178f26c6eeaa90f49562a313a7799074e5d51c7" in source
    assert "checkout','--detach',RUNNER_COMMIT" in source
    assert 'REQUIRED_NF4_TRANSFORMERS = "5.15.0"' in writer
