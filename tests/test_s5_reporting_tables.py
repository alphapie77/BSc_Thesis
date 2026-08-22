import pandas as pd
import pytest

from src.eval.render_s5_reporting_tables_bn import ReportingTableError, render


def _frames():
    conditions = [f"c{i}" for i in range(10)]
    master = pd.DataFrame([{"condition": c, "target_level": level, "n": 270,
        "verifier_b_mean_target_probability": .6, "verifier_b_binary_accuracy": .7,
        "mean_generator_calls": 1.5, "mean_generator_tokens": 900, "gave_up_rate": 0}
        for c in conditions for level in (0, 1)])
    paired = pd.DataFrame([{"condition": c, "baseline": "zero_shot", "n_pairs": 540,
        "b_probability_delta": .1, "ci_low": .05, "ci_high": .15, "bootstrap_p": .001,
        "bh_q_bootstrap_p": .002, "mcnemar_p": .003} for c in conditions[:9]])
    return master, paired


def test_render_contains_exact_tables():
    text = render(*_frames(), {"timestamp_utc": "now", "git_commit": "clean"})
    assert text.count("| c") == 29
    assert "no inference recomputed" in text


def test_render_rejects_duplicate_master_cell():
    master, paired = _frames()
    master.iloc[-1] = master.iloc[0]
    with pytest.raises(ReportingTableError, match="duplicate"):
        render(master, paired, {"timestamp_utc": "now", "git_commit": "clean"})
