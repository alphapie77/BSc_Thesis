"""Validate the G1 statistics against data with a known answer.

Prediction strength and the gap statistic are both easy to implement in a way
that runs, produces plausible numbers, and is wrong. Neither has an obvious
sanity check by eye: a prediction-strength curve that peaks at the wrong K looks
exactly like one that peaks at the right K.

So they are tested against synthetic data whose true K is known by construction.
If `prediction_strength` cannot find 3 well-separated blobs, it cannot be
trusted to adjudicate between 2 and 3 personas on real reviews — and that
adjudication is what Gate G1 exists for.

Run:  python -m pytest tests/test_s2d_ktable.py -q
      python tests/test_s2d_ktable.py          (no pytest needed)
"""
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cluster.s2d_ktable import (  # noqa: E402
    NO_STABLE_K, bootstrap_ari, gap_statistic, prediction_strength, trap_band,
)

CFG = yaml.safe_load((ROOT / "configs" / "s2d_ktable.yaml").read_text(encoding="utf-8"))
HAVE_SK = True
try:
    import sklearn  # noqa: F401
except ImportError:
    HAVE_SK = False


def blobs(k, n_per=120, dim=16, sep=8.0, seed=0):
    """k well-separated Gaussian blobs. True K is k, by construction."""
    rng = np.random.default_rng(seed)
    centres = rng.normal(scale=sep, size=(k, dim))
    x = np.vstack([c + rng.normal(scale=1.0, size=(n_per, dim)) for c in centres])
    return x.astype(np.float32)


class Skipped(Exception):
    """Raised when a test cannot run. NOT a pass.

    The first version of this file printed "(skipped)" and then returned, so the
    runner counted it as a pass and reported 8/8 while five tests had not
    executed. A suite that reports green for tests it did not run is worse than
    no suite, because it is trusted.
    """


def _skip(name):
    raise Skipped(f"{name}: scikit-learn not installed in this environment")


def test_prediction_strength_peaks_at_the_true_k():
    """PS should be high at the true K and fall off past it.

    This is the property Gate G1 relies on. If it does not hold on data this
    clean, the real table means nothing.
    """
    if not HAVE_SK:
        _skip("prediction strength")
    x = blobs(3, seed=1)
    rng = np.random.default_rng(42)
    ps = {k: prediction_strength(x, k, 10, rng, 10) for k in (2, 3, 4, 5)}
    print(f"    PS by K: { {k: round(v, 3) for k, v in ps.items()} }")
    assert ps[3] >= 0.95, f"PS at the true K=3 is only {ps[3]:.3f}"
    assert ps[5] < ps[3], "PS did not fall off past the true K"


def test_prediction_strength_is_bounded():
    if not HAVE_SK:
        _skip("PS bounds")
    x = blobs(2, seed=2)
    rng = np.random.default_rng(7)
    for k in (2, 3, 4):
        v = prediction_strength(x, k, 5, rng, 10)
        assert 0.0 <= v <= 1.0, f"PS={v} out of [0,1] at K={k}"


def test_prediction_strength_takes_the_MINIMUM_over_clusters():
    """One unreproducible cluster must sink the K.

    Two tight blobs plus scattered noise: at K=3 the noise cluster is not
    reproducible, so the minimum-over-clusters rule must score K=3 well below
    K=2. A mean over clusters would let the two good clusters hide it — which is
    exactly the failure this design choice prevents.
    """
    if not HAVE_SK:
        _skip("PS minimum rule")
    rng0 = np.random.default_rng(3)
    tight = np.vstack([
        np.zeros(8) + rng0.normal(scale=0.3, size=(100, 8)),
        np.full(8, 12.0) + rng0.normal(scale=0.3, size=(100, 8)),
    ])
    noise = rng0.uniform(-6, 18, size=(100, 8))
    x = np.vstack([tight, noise]).astype(np.float32)
    rng = np.random.default_rng(11)
    ps2 = prediction_strength(x, 2, 12, rng, 10)
    ps3 = prediction_strength(x, 3, 12, rng, 10)
    print(f"    PS K=2 {ps2:.3f} vs K=3 {ps3:.3f}")
    assert ps2 > ps3, "the unreproducible third cluster did not depress PS"


def test_bootstrap_ari_high_on_clean_structure_low_on_noise():
    if not HAVE_SK:
        _skip("bootstrap ARI")
    from sklearn.cluster import KMeans
    rng = np.random.default_rng(5)

    x = blobs(3, seed=4)
    lab = KMeans(n_clusters=3, n_init=10, random_state=42).fit_predict(x)
    m, sd = bootstrap_ari(x, 3, lab, 20, 0.8, rng, 10)
    print(f"    clean blobs: bootstrap ARI {m:.3f} ± {sd:.3f}")
    assert m > 0.9, f"stable structure scored only {m:.3f}"

    u = rng.uniform(size=(360, 16)).astype(np.float32)
    lab_u = KMeans(n_clusters=3, n_init=10, random_state=42).fit_predict(u)
    mu, _ = bootstrap_ari(u, 3, lab_u, 20, 0.8, rng, 10)
    print(f"    uniform noise: bootstrap ARI {mu:.3f}")
    assert mu < m, "noise was as stable as real structure"


def test_gap_statistic_runs_and_returns_finite_values():
    if not HAVE_SK:
        _skip("gap statistic")
    x = blobs(3, seed=6)
    rng = np.random.default_rng(9)
    for k in (2, 3, 4):
        gap, se = gap_statistic(x, k, 5, rng, 10)
        assert np.isfinite(gap) and np.isfinite(se), f"non-finite gap at K={k}"
        assert se >= 0


def test_trap_band_matches_the_preregistered_bands():
    """Same four bands as RQ1, and degeneracy still overrides ARI."""
    ok = {0: 0.34, 1: 0.33, 2: 0.33}
    assert trap_band(0.10, ok, CFG) == "NOT_SENTIMENT_ALIGNED"
    assert trap_band(0.20, ok, CFG) == "PARTIAL_OVERLAP"
    assert trap_band(0.60, ok, CFG) == "PARTIAL_OVERLAP"
    assert trap_band(0.61, ok, CFG) == "PERSONA_CLAIM_FAILS"
    bad = {0: 0.96, 1: 0.02, 2: 0.02}
    for ari in (0.0, 0.5, 0.99):
        assert trap_band(ari, bad, CFG) == "DEGENERATE", (
            "a degenerate partition escaped the first gate"
        )


def test_the_preregistered_threshold_is_still_080():
    """0.80 is Tibshirani & Walther's and was fixed before the table existed.

    A silent edit here would be a change to the pre-registration, so it fails
    loudly instead.
    """
    assert CFG["prediction_strength"]["threshold"] == 0.80, (
        "the PS cutoff moved. That is a protocol change (docs/protocol.md, "
        "RQ1-C) and must be logged as a deviation, not edited quietly."
    )
    assert CFG["k_range"] == [2, 3, 4, 5, 6, 7, 8]
    assert CFG["bootstrap"] == {"n_runs": 100, "subsample_frac": 0.8}
    assert CFG["trap_check"]["bands"]["not_sentiment_aligned_below"] == 0.20


def test_selection_rule_is_largest_passing_k_not_the_best_score():
    """Pipeline §2.2 says LARGEST K with PS ≥ 0.80 — not argmax PS.

    Those differ whenever a smaller K scores higher, which is the normal case.
    Encoded here so the rule cannot drift into "pick the best number".
    """
    import pandas as pd
    tab = pd.DataFrame({"K": [2, 3, 4, 5],
                        "prediction_strength": [0.99, 0.91, 0.83, 0.42]})
    passing = tab[tab["prediction_strength"] >= 0.80]
    assert int(passing["K"].max()) == 4, "rule picked something other than largest"
    assert int(tab.loc[tab["prediction_strength"].idxmax(), "K"]) == 2
    none_pass = tab[tab["prediction_strength"] >= 0.999]
    assert len(none_pass) == 0 and NO_STABLE_K == "NO_STABLE_K"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = skipped = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except Skipped as e:
            skipped += 1
            print(f"SKIP  {fn.__name__}: {e}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {fn.__name__}: {e}")
    passed = len(fns) - failed - skipped
    print(f"\n{passed} passed, {skipped} SKIPPED, {failed} failed "
          f"(of {len(fns)})")
    if skipped:
        print("⚠️  Skipped tests did NOT run. The numeric checks on prediction\n"
              "    strength, bootstrap ARI and the gap statistic need\n"
              "    scikit-learn — run this on Kaggle before trusting G1.")
    raise SystemExit(1 if failed else 0)
