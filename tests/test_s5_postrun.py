from pathlib import Path

import numpy as np
import pytest

from src.eval.analyze_s5_bn import benjamini_hochberg, mcnemar_exact, paired_bootstrap
from src.eval.score_s5_bn import S5ScoreError, _emitted_text, validate_cases
from src.eval.s5_contract import CONDITIONS, load_eval_plots


ROOT = Path(__file__).resolve().parents[1]


def _case(seed, plot_id, level, condition):
    return {
        "key": f"S5BN|s{seed}|{plot_id}|L{level}|{condition}",
        "plot_id": plot_id, "replicate_seed": seed, "target_level": level,
        "condition": condition, "language": "bn", "verifier_b_score": None,
        "result": {"emitted": {"text": "বাংলা লেখা"}},
        "provenance": {"verifier_b_loaded": False},
    }


def test_postrun_requires_the_full_frozen_surface_and_b_wall():
    plots = load_eval_plots(ROOT / "data/plots/plots_bn.csv")
    rows = [_case(seed, p.plot_id, level, condition) for seed in (42, 43, 44)
            for p in plots for level in (0, 1) for condition in CONDITIONS]
    validate_cases(rows, plots=plots, seeds=(42, 43, 44))
    rows[0]["provenance"]["verifier_b_loaded"] = True
    with pytest.raises(S5ScoreError, match="B wall"):
        validate_cases(rows, plots=plots, seeds=(42, 43, 44))


def test_emitted_text_supports_simple_and_loop_results():
    assert _emitted_text({"key": "a", "result": {"emitted": {"text": "x"}}}) == "x"
    assert _emitted_text({"key": "b", "result": {"emitted": {"generation": {"text": "y"}}}}) == "y"


def test_statistics_helpers_are_deterministic_and_conservative():
    rng = np.random.default_rng(42)
    point, lo, hi, p = paired_bootstrap(np.array([0.2, 0.1, 0.3]), n=1000, rng=rng, confidence=.95)
    assert point == pytest.approx(.2)
    assert lo > 0 and hi >= point and 0 < p <= 1
    assert benjamini_hochberg([.01, .04, .03]) == pytest.approx([.03, .04, .04])
    assert mcnemar_exact(0, 0) == 1.0
    assert mcnemar_exact(10, 0) < .01
