from pathlib import Path

import pandas as pd

from src.eval.plot_s5_goodhart_bn import build_figure


def test_goodhart_figure_renders_two_registered_panels(tmp_path: Path):
    conditions = ["rag_neural_loop", "rag_symbolic_loop", "rag_neural_symbolic_feedback"]
    attempts = pd.DataFrame([
        {"condition": c, "attempt": a, "n_cases": 10-a,
         "mean_verifier_a": .5 + .1*a, "mean_verifier_b": .5 + .05*a}
        for c in conditions for a in (1, 2, 3)
    ])
    transitions = pd.DataFrame([
        {"condition": c, "from_attempt": a, "to_attempt": a+1,
         "n_paired_cases": 8-a, "mean_a_minus_b_delta": .02*a}
        for c in conditions for a in (1, 2)
    ])
    out = tmp_path / "figure.png"
    build_figure(attempts, transitions, out,
                 provenance={"git_commit": "test-clean"})
    assert out.read_bytes().startswith(b"\x89PNG")
    assert out.stat().st_size > 10_000

