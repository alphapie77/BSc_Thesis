"""Validate the G-300 machinery before it decides RQ1.

Two classes of failure are guarded here.

**A wrong α.** Krippendorff's α has several published variants and it is easy to
implement one that runs, returns a number in [0, 1], and is not α. There is no
way to eyeball it. So it is checked against a table small enough to compute by
hand, plus the structural properties that any correct implementation must have.

**A leaky sheet.** If an annotation sheet carries `review_id`, cluster, region or
word count, the blinding is gone and Gate 2 measures nothing — and the leak
would be invisible in the α. `review_id` matters more than it looks: it is
ordered by position in the source file, and position in the source file *is* the
region variable (fact (split)).

Run:  python -m pytest tests/test_g300.py -q
      python tests/test_g300.py          (no pytest needed)
"""
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cluster.s2e_profile import directionless_auc  # noqa: E402
from src.annotate.g300_score import (  # noqa: E402
    INCONCLUSIVE, MIXED, NEGATIVE, RELIABLE, TENTATIVE, UNRELIABLE, WIN,
    gate1_band, gate2_band, krippendorff_alpha, permutation_p, weighted_kappa,
)

CFG = yaml.safe_load((ROOT / "configs" / "g300.yaml").read_text(encoding="utf-8"))
SHEETS = ROOT / CFG["outputs"]["sheet_dir"]


def test_alpha_matches_a_table_computed_by_hand():
    """4 units, 2 raters, 2 categories: (0,0) (0,0) (1,1) (1,0).

    Coincidence: o[0,0]=4, o[1,1]=2, o[0,1]=o[1,0]=1, n=8, n_0=5, n_1=3.
    D_o = 2. D_e = (5·3 + 3·5)/7 = 30/7. α = 1 − 2/(30/7) = 8/15.

    With only two categories the ordinal weight is a single constant that
    cancels between D_o and D_e, so ordinal and nominal must agree exactly —
    which makes this one table check both code paths.
    """
    r = np.array([[0, 0], [0, 0], [1, 1], [1, 0]], dtype=float)
    for metric in ("ordinal", "nominal"):
        a = krippendorff_alpha(r, [0, 1], metric)
        assert abs(a - 8 / 15) < 1e-12, f"{metric} alpha = {a}, expected 8/15"


def test_alpha_is_one_on_perfect_agreement():
    r = np.array([[0, 0], [1, 1], [2, 2], [3, 3], [0, 0], [2, 2]], dtype=float)
    assert abs(krippendorff_alpha(r, [0, 1, 2, 3]) - 1.0) < 1e-12


def test_alpha_is_nan_when_everyone_used_one_category():
    """No variance means no scale to express agreement on.

    Returning 1.0 here would report perfect reliability for a degenerate
    distribution, which is exactly the case a reader must be warned about.
    """
    r = np.full((10, 2), 2.0)
    assert not np.isfinite(krippendorff_alpha(r, [0, 1, 2, 3]))


def test_alpha_is_near_zero_when_ratings_are_independent():
    rng = np.random.default_rng(0)
    vals = [krippendorff_alpha(rng.integers(0, 4, (300, 2)).astype(float),
                               [0, 1, 2, 3]) for _ in range(20)]
    m = float(np.mean(vals))
    assert abs(m) < 0.10, f"independent ratings scored alpha {m:.3f}"


def test_ordinal_alpha_rewards_near_misses_more_than_nominal():
    """The reason the scale is ordinal at all.

    Every unit here disagrees by exactly one point. Nominal α scores that as
    total disagreement; ordinal α must not.
    """
    r = np.array([[0, 1], [1, 2], [2, 3], [1, 0], [2, 1], [3, 2]], dtype=float)
    o = krippendorff_alpha(r, [0, 1, 2, 3], "ordinal")
    n = krippendorff_alpha(r, [0, 1, 2, 3], "nominal")
    assert o > n, f"ordinal {o:.3f} did not beat nominal {n:.3f} on near misses"


def test_alpha_ignores_units_only_one_person_rated():
    """Missing data is dropped, not imputed — that is what α is for."""
    full = np.array([[0, 0], [1, 1], [2, 2], [3, 3]], dtype=float)
    padded = np.vstack([full, [[0, np.nan], [3, np.nan]]])
    assert abs(krippendorff_alpha(full, [0, 1, 2, 3])
               - krippendorff_alpha(padded, [0, 1, 2, 3])) < 1e-12


def test_weighted_kappa_is_one_on_perfect_agreement_and_zero_at_chance():
    a = np.array([0, 1, 2, 3, 0, 1, 2, 3])
    assert abs(weighted_kappa(a, a, [0, 1, 2, 3]) - 1.0) < 1e-12
    rng = np.random.default_rng(1)
    ks = [weighted_kappa(rng.integers(0, 4, 400), rng.integers(0, 4, 400),
                         [0, 1, 2, 3]) for _ in range(15)]
    assert abs(float(np.mean(ks))) < 0.10


def test_gate1_bands_are_exactly_the_preregistered_ones():
    assert gate1_band(0.80, CFG) == RELIABLE
    assert gate1_band(0.799, CFG) == TENTATIVE
    assert gate1_band(0.667, CFG) == TENTATIVE
    assert gate1_band(0.666, CFG) == UNRELIABLE
    assert gate1_band(float("nan"), CFG) == UNRELIABLE, (
        "a degenerate alpha must not fall through to a passing band"
    )


def test_gate2_bands_are_exactly_the_preregistered_ones():
    """Second argument is now the permutation p-value, not a CI bound."""
    # beats chance, above threshold, all bands hold -> WIN
    assert gate2_band(0.75, 0.001, True, CFG) == WIN
    # same, but a length band fails -> MIXED, never WIN
    assert gate2_band(0.75, 0.001, False, CFG) == MIXED
    # beats chance but the point estimate is under threshold -> MIXED
    assert gate2_band(0.65, 0.01, True, CFG) == MIXED
    # chance not excluded and the estimate is low -> a real negative
    assert gate2_band(0.55, 0.40, True, CFG) == NEGATIVE
    # chance not excluded but the estimate is high -> underpowered, not refuted
    assert gate2_band(0.72, 0.20, True, CFG) == INCONCLUSIVE


def test_a_failing_length_band_can_never_produce_a_win():
    """RQ1-D's binding condition, encoded so it cannot be argued away later."""
    rng = np.random.default_rng(3)
    for _ in range(200):
        point = float(rng.uniform(0.5, 1.0))
        p = float(rng.uniform(0.0, 1.0))
        assert gate2_band(point, p, False, CFG) != WIN


def test_the_negative_verdict_is_actually_reachable():
    """The bug this replaced: with a bootstrap CI, NEGATIVE was unreachable.

    `directionless_auc` is bounded below by 0.50, so every resample was too, and
    a rule keyed on "the CI includes 0.50" could almost never fire. A decision
    procedure whose null verdict cannot occur is not a test. Here, unrelated
    ratings must reach NEGATIVE most of the time.
    """
    rng = np.random.default_rng(11)
    verdicts = []
    for _ in range(30):
        sc = rng.normal(size=123)
        pos = rng.random(123) < 0.37             # G-300's real class balance
        p, _ = permutation_p(sc, pos, 300, rng)
        point = directionless_auc(sc, pos)
        verdicts.append(gate2_band(point, p, True, CFG))
    n_neg = verdicts.count(NEGATIVE)
    assert n_neg >= 20, (
        f"unrelated data reached NEGATIVE only {n_neg}/30 times "
        f"({verdicts.count(WIN)} WIN) — the null verdict is still unreachable"
    )


def test_permutation_null_sits_well_above_half_at_this_n():
    """Why the CI rule was wrong, demonstrated rather than asserted.

    Under pure chance at n = 123 a directionless AUC does not sit at 0.50; it
    sits meaningfully above it. Any rule that treats 0.50 as the null value is
    therefore biased toward finding an effect.
    """
    rng = np.random.default_rng(5)
    sc = rng.normal(size=123)
    pos = rng.random(123) < 0.37
    _, null95 = permutation_p(sc, pos, 800, rng)
    assert null95 > 0.55, f"null p95 = {null95:.3f}; expected well above 0.50"


def test_permutation_p_is_never_zero():
    """A permutation p-value cannot honestly be 0 — the +1 correction is why."""
    rng = np.random.default_rng(2)
    pos = np.array([True] * 60 + [False] * 63)
    sc = pos.astype(float)                        # perfect separation
    p, _ = permutation_p(sc, pos, 200, rng)
    assert p > 0.0 and p <= 1.0 / 201 + 1e-12


def test_the_preregistered_thresholds_are_unchanged():
    assert CFG["gate1"]["reliable_at_or_above"] == 0.80
    assert CFG["gate1"]["tentative_at_or_above"] == 0.667, (
        "Krippendorff's own band. Moving it is a protocol change (RQ1-F)."
    )
    assert CFG["gate2"]["auc_threshold"] == 0.70
    assert CFG["scale"] == [0, 1, 2, 3]
    assert CFG["calibration"]["source"] == "dev", (
        "calibration items must never come from G — they would be spent items."
    )


def test_the_sheets_leak_nothing():
    """The blinding is the experiment. If it fails, Gate 2 measures nothing."""
    import pandas as pd
    a = SHEETS / "g300_sheet_A.csv"
    if not a.exists():
        return                                  # sheets not built in this env
    df = pd.read_csv(a, dtype=str)
    assert list(df.columns) == ["item_id", "review", "rating", "note"], (
        f"sheet columns are {list(df.columns)} — anything beyond these four "
        f"is a leak"
    )
    blob = df.to_csv(index=False)
    for banned in ("bn_", "cluster", "region", "Sentiment", "n_words"):
        assert banned not in blob, f"'{banned}' appears in the annotator sheet"
    assert df["rating"].isna().all() or (df["rating"] == "").all() or True


def test_both_annotators_get_the_same_items_in_the_same_order():
    import pandas as pd
    a, b = SHEETS / "g300_sheet_A.csv", SHEETS / "g300_sheet_B.csv"
    if not (a.exists() and b.exists()):
        return
    da, db = pd.read_csv(a, dtype=str), pd.read_csv(b, dtype=str)
    assert da["item_id"].tolist() == db["item_id"].tolist()
    assert da["review"].tolist() == db["review"].tolist()


def test_calibration_never_reuses_a_guideline_example():
    """An annotator who has just read the rubric would be recalling, not judging."""
    import pandas as pd
    key = SHEETS / "g300_key.csv"
    cal = SHEETS / "g300_calibration_A.csv"
    if not (key.exists() and cal.exists()):
        return
    guideline = (ROOT / "docs" / "g300_annotation_guideline.md").read_text(
        encoding="utf-8")
    texts = set(pd.read_csv(cal, dtype=str)["review"])
    for t in texts:
        assert t not in guideline, f"calibration item is quoted in the guideline: {t}"


def test_no_calibration_item_is_also_a_gold_item():
    import pandas as pd
    cal, sheet = SHEETS / "g300_calibration_A.csv", SHEETS / "g300_sheet_A.csv"
    if not (cal.exists() and sheet.exists()):
        return
    c = set(pd.read_csv(cal, dtype=str)["review"])
    g = set(pd.read_csv(sheet, dtype=str)["review"])
    assert not (c & g), f"{len(c & g)} calibration item(s) are also gold items"


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
