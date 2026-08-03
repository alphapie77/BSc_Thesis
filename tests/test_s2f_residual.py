"""Validate the S2f statistics against cases with a known answer.

`cell_majority_accuracy` is the one that needs guarding hardest, because its
failure mode is flattering. It is a resubstitution estimate, so it can only ever
overstate; a bug that makes it overstate *further* would push the verdict toward
"the cheap variables explain everything" — the conclusion that kills the persona
claim. A bug in the other direction would manufacture a residual out of nothing.
Both directions are tested.

Run:  python -m pytest tests/test_s2f_residual.py -q
      python tests/test_s2f_residual.py          (no pytest needed)
"""
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cluster.s2f_residual import (  # noqa: E402
    EXPLAINED, PARTIAL, RESIDUAL, cell_majority_accuracy, phi, verdict_c,
)

CFG = yaml.safe_load((ROOT / "configs" / "s2f_residual.yaml").read_text(encoding="utf-8"))


def test_phi_matches_the_hand_computed_s2e_table():
    """The S2e cluster × Sentiment table, whose φ was computed independently.

    ARI on this same table is 0.1522. The gap between the two is the entire
    reason S2f exists, so the φ side of it is pinned here.
    """
    got = phi(384, 759, 560, 194)
    assert abs(abs(got) - 0.3981) < 5e-4, f"phi = {got:.4f}, expected |0.3981|"


def test_phi_is_zero_for_independence_and_one_for_perfect_association():
    assert abs(phi(50, 50, 50, 50)) < 1e-12
    assert abs(abs(phi(100, 0, 0, 100)) - 1.0) < 1e-12
    assert not np.isfinite(phi(10, 10, 0, 0)), "an empty margin must give nan"


def test_cell_majority_accuracy_is_perfect_when_cells_determine_the_label():
    cells = np.array(["a", "a", "a", "b", "b", "b"])
    y = np.array([0, 0, 0, 1, 1, 1])
    acc, base = cell_majority_accuracy(cells, y)
    assert acc == 1.0 and base == 0.5


def test_cell_majority_accuracy_falls_back_to_the_baseline_when_cells_are_useless():
    """Cells that carry no information must not appear to explain anything.

    With a single cell the majority rule IS the baseline, so the lift is zero.
    A non-zero lift here would mean the estimator invents explanation.
    """
    y = np.array([0] * 70 + [1] * 30)
    acc, base = cell_majority_accuracy(np.array(["only"] * 100), y)
    assert acc == base == 0.7, f"acc {acc}, base {base}"


def test_cell_majority_accuracy_never_goes_below_the_baseline():
    """Splitting into more cells can only ever help a resubstitution estimate.

    This is the property that makes the number an UPPER bound, and it is exactly
    why the report has to say so. If this test ever fails, the estimator is not
    doing what the report claims about it.
    """
    rng = np.random.default_rng(0)
    for _ in range(40):
        y = (rng.random(200) < 0.4).astype(int)
        cells = rng.integers(0, 6, 200).astype(str)
        acc, base = cell_majority_accuracy(cells, y)
        assert acc >= base - 1e-12


def test_cell_majority_accuracy_is_perfect_when_every_cell_is_a_singleton():
    """The degenerate case the caveat exists for: one row per cell scores 100%.

    Nothing is explained; the estimator has simply memorised the labels. Pinned
    so nobody later reads a high lift as evidence without the caveat.
    """
    y = np.array([0, 1, 0, 1, 1])
    acc, _ = cell_majority_accuracy(np.arange(5).astype(str), y)
    assert acc == 1.0


def test_verdict_c_bands_are_exactly_the_preregistered_ones():
    assert verdict_c(25.0, CFG) == EXPLAINED
    assert verdict_c(24.99, CFG) == PARTIAL
    assert verdict_c(10.0, CFG) == PARTIAL
    assert verdict_c(9.99, CFG) == RESIDUAL
    assert verdict_c(0.0, CFG) == RESIDUAL


def test_the_preregistered_thresholds_are_unchanged():
    """A silent edit here is a change to RQ1-E, so it fails loudly instead.

    The observed lift was 9.8 pp against the 10.0 cutoff — 0.2 pp away. That
    makes this file's job unusually load-bearing: moving the cutoff by a
    rounding error would flip the published verdict.
    """
    assert CFG["test_c"]["partial_at_or_above"] == 10.0, (
        "the RESIDUAL/PARTIAL cutoff moved. The observed lift is 9.8 pp, so "
        "this edit would flip the verdict. Protocol change (RQ1-E) -> log it."
    )
    assert CFG["test_c"]["explained_at_or_above"] == 25.0
    assert CFG["test_a"]["independent_at_or_above"] == 0.60
    assert CFG["test_b"]["independent_at_or_above"] == 0.20
    assert CFG["length_bands"]["n_quantiles"] == 4, (
        "band count changed. Test C's lift depends on it, and 9.8 vs 10.0 is "
        "close enough that re-binning could flip the verdict."
    )


def test_s2f_reads_s2e_and_expects_the_same_n():
    assert CFG["input_assignments"] == "results/s2e_regionA_k2_assignments.csv"
    assert CFG["expected_n"] == 1897


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed} passed, {failed} failed (of {len(fns)})")
    raise SystemExit(1 if failed else 0)
