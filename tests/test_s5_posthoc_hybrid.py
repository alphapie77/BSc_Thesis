import pytest

from src.eval.analyze_s5_posthoc_hybrid_bn import (
    PosthocContrastError,
    pair_conditions,
)


def _row(condition, *, plot="BN001", level=0, seed=42, probability=.5,
         success=1, calls=1, tokens=100):
    return {
        "key": f"S5BN|s{seed}|{plot}|L{level}|{condition}",
        "condition": condition,
        "plot_id": plot,
        "target_level": level,
        "replicate_seed": seed,
        "verifier_b_target_probability": probability,
        "verifier_b_binary_success": success,
        "logical_generator_calls": calls,
        "logical_generator_tokens": tokens,
    }


def test_pair_conditions_matches_only_exact_case_keys():
    rows = []
    for seed in (42, 43, 44):
        for plot_number in range(90):
            for level in (0, 1):
                plot = f"BN{plot_number:03d}"
                rows.extend([
                    _row("rag_neural_symbolic_feedback", plot=plot, level=level, seed=seed),
                    _row("rag_neural_loop", plot=plot, level=level, seed=seed),
                ])
    pairs = pair_conditions(rows, "rag_neural_symbolic_feedback", "rag_neural_loop")
    assert len(pairs) == 540
    assert all(t["plot_id"] == c["plot_id"] for t, c in pairs)

    rows.pop()
    with pytest.raises(PosthocContrastError, match="missing comparator"):
        pair_conditions(rows, "rag_neural_symbolic_feedback", "rag_neural_loop")


def test_pair_conditions_rejects_unknown_or_identical_conditions():
    with pytest.raises(PosthocContrastError, match="distinct frozen conditions"):
        pair_conditions([], "missing", "rag_neural_loop")
    with pytest.raises(PosthocContrastError, match="distinct frozen conditions"):
        pair_conditions([], "rag_neural_loop", "rag_neural_loop")
