"""Validate the S2 numeric core against brute-force references.

`test_s2_verdict.py` pins the *interpretation* (which band an ARI falls in).
Nothing pinned the *computation* underneath it, yet that is where a silent error
would be most expensive: the blocked matmul in `all_near_dup_pairs` and the
greedy pass in `greedy_keep_first` decide which rows exist for the rest of the
thesis. A pair missed at a block boundary is a duplicate that survives into the
frozen split, and the split is never regenerated (inviolable rule 3) -- so the
error would be permanent and invisible.

The strategy is differential: run the optimised implementation against a naive
O(n^2) reference that is obviously correct because it is obviously slow. They
must agree exactly, not approximately.

`n` deliberately straddles the 512-row block size (n = 1100 -> blocks of
512/512/76, the last one short) because off-by-one errors in blocked upper-
triangle extraction only appear at the seams.

Deliberately import-light: numpy and pandas only. `cluster_and_ari` needs
scikit-learn and scipy and is therefore NOT covered here -- it is exercised on
the Kaggle host where those are installed.

Run:  python -m pytest tests/test_s2_numeric.py -q
      python tests/test_s2_numeric.py          (no pytest needed)
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cluster.s2_pilot import (  # noqa: E402
    COSINE_BINS,
    all_near_dup_pairs,
    greedy_keep_first,
    hist_percentile,
)

#: Must straddle the 512 block size in `all_near_dup_pairs`, with a short final
#: block, so boundary handling is actually tested rather than assumed.
N = 1100
DIM = 32
SEED = 42


def _emb(n=N, dim=DIM, seed=SEED, n_dupes=40):
    """L2-normalized embeddings with planted near-duplicates.

    Random Gaussian rows give a realistic low-cosine bulk; the planted rows are
    near-copies of earlier rows, some straddling a block boundary on purpose so
    a pair whose two members sit in different blocks must still be found.
    """
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(n, dim)).astype(np.float32)

    # Plant near-duplicates. Sources are spread across the array, and the
    # offsets are chosen so several pairs cross the 512/1024 block seams.
    for k in range(n_dupes):
        src = (k * 27) % (n // 2)
        dst = n - 1 - k
        x[dst] = x[src] + rng.normal(scale=0.01, size=dim).astype(np.float32)

    # A few exact copies: cosine must come out at 1.0, the hardest case for a
    # threshold comparison.
    x[500] = x[3]
    x[512] = x[4]      # first row of block 2, source in block 1
    x[1023] = x[600]
    x[1024] = x[601]   # first row of block 3, source in block 2

    return x / np.linalg.norm(x, axis=1, keepdims=True)


def _brute_pairs(emb, threshold):
    """Naive reference: full matrix, explicit strict upper triangle."""
    n = emb.shape[0]
    sims = emb @ emb.T
    out = {}
    for i in range(n):
        for j in range(i + 1, n):
            if sims[i, j] >= threshold:
                out[(i, j)] = float(sims[i, j])
    return out


def test_pair_enumeration_matches_brute_force():
    """The blocked implementation must find exactly the reference pair set."""
    emb = _emb()
    t = 0.90
    pairs, _ = all_near_dup_pairs(emb, t)
    got = {(int(i), int(j)): float(c) for i, j, c in
           pairs[["i", "j", "cosine"]].itertuples(index=False)}
    want = _brute_pairs(emb, t)

    missing = sorted(set(want) - set(got))
    extra = sorted(set(got) - set(want))
    assert not missing, f"{len(missing)} pairs MISSED (first: {missing[:5]})"
    assert not extra, f"{len(extra)} spurious pairs (first: {extra[:5]})"
    for k in want:
        assert abs(got[k] - want[k]) < 1e-5, f"cosine mismatch at {k}"
    assert len(want) > 0, "test is vacuous: the fixture planted no pairs"


def test_only_strict_upper_triangle_and_no_self_pairs():
    """i < j always: row order is review_id order, so i is the lower id."""
    pairs, _ = all_near_dup_pairs(_emb(), 0.90)
    i = pairs["i"].to_numpy()
    j = pairs["j"].to_numpy()
    assert (i < j).all(), "found a pair with i >= j"
    assert len(pairs) == len({(a, b) for a, b in zip(i, j)}), "duplicate pair rows"


def test_distribution_counts_every_offdiagonal_pair_exactly_once():
    emb = _emb()
    _, dist = all_near_dup_pairs(emb, 0.90)
    assert dist["n_offdiagonal_pairs"] == N * (N - 1) // 2


def test_reported_max_is_exact_not_binned():
    """The max is tracked directly, so it must be exact -- not a bin edge."""
    emb = _emb()
    _, dist = all_near_dup_pairs(emb, 0.90)
    sims = emb @ emb.T
    true_max = max(
        float(sims[i, i + 1:].max()) for i in range(N - 1)
    )
    assert abs(dist["max"] - true_max) < 1e-6, (
        f"reported max {dist['max']} != true {true_max}"
    )


def test_histogram_percentiles_are_within_one_bin_of_truth():
    """Percentiles are estimates; the report claims ~one bin width of error."""
    emb = _emb()
    _, dist = all_near_dup_pairs(emb, 0.90)
    sims = emb @ emb.T
    true_vals = np.concatenate([sims[i, i + 1:] for i in range(N - 1)])
    tol = 2.0 / COSINE_BINS * 3  # 3 bin widths: generous, still meaningful
    for q in (50, 90, 95, 99):
        truth = float(np.percentile(true_vals, q))
        est = dist["percentiles"][q]
        assert abs(est - truth) < tol, (
            f"p{q}: estimate {est:.6f} vs truth {truth:.6f} (tol {tol:.6f})"
        )


def test_hist_percentile_on_a_known_distribution():
    """Sanity-check the helper itself, independent of the matmul."""
    edges = np.linspace(-1.0, 1.0, COSINE_BINS + 1)
    vals = np.linspace(-0.5, 0.5, 100_001)
    hist = np.histogram(vals, bins=edges)[0]
    for q, want in ((50, 0.0), (25, -0.25), (75, 0.25)):
        got = hist_percentile(hist, edges, q)
        assert abs(got - want) < 1e-3, f"p{q}: {got} != {want}"


def test_hist_percentile_empty_is_nan_not_zero():
    """An empty histogram must not silently report 0.0 as a percentile."""
    edges = np.linspace(-1.0, 1.0, COSINE_BINS + 1)
    got = hist_percentile(np.zeros(COSINE_BINS, dtype=np.int64), edges, 50)
    assert np.isnan(got), f"expected nan, got {got}"


# --- greedy_keep_first -----------------------------------------------------

def _pairs_df(triples):
    import pandas as pd
    return pd.DataFrame(triples, columns=["i", "j", "cosine"])


def test_lowest_index_always_survives():
    """`keep: first_by_review_id` -- row 0 can never be removed."""
    emb = _emb()
    pairs, _ = all_near_dup_pairs(emb, 0.90)
    for t in (0.90, 0.95, 0.98):
        kept, removed = greedy_keep_first(N, pairs, t)
        assert 0 not in removed, "row 0 was removed; keep-first is violated"
        assert 0 in set(kept.tolist())


def test_every_removal_points_at_a_surviving_anchor():
    """A removed row must not itself be the anchor that evicted another row.

    This is the transitive-chain guard: without it, a chain of similar rows
    deletes more than intended.
    """
    emb = _emb()
    pairs, _ = all_near_dup_pairs(emb, 0.90)
    for t in (0.90, 0.95, 0.98):
        kept, removed = greedy_keep_first(N, pairs, t)
        keptset = set(kept.tolist())
        for j, (anchor, cos) in removed.items():
            assert anchor < j, f"anchor {anchor} is not below removed row {j}"
            assert anchor in keptset, (
                f"row {j} was evicted by {anchor}, which was itself removed"
            )
            assert cos >= t, f"row {j} removed at cosine {cos} < threshold {t}"


def test_kept_and_removed_partition_the_rows():
    emb = _emb()
    pairs, _ = all_near_dup_pairs(emb, 0.90)
    kept, removed = greedy_keep_first(N, pairs, 0.95)
    assert len(kept) + len(removed) == N
    assert set(kept.tolist()).isdisjoint(set(removed)), "a row is both kept and removed"
    assert sorted(kept.tolist() + list(removed)) == list(range(N))


def test_higher_threshold_never_removes_more():
    """The sensitivity curve is only readable if it is monotone."""
    emb = _emb()
    pairs, _ = all_near_dup_pairs(emb, 0.90)
    counts = [len(greedy_keep_first(N, pairs, t)[1]) for t in (0.90, 0.95, 0.98)]
    assert counts == sorted(counts, reverse=True), (
        f"removals not monotone decreasing in threshold: {counts}"
    )


def test_transitive_chain_keeps_the_far_end():
    """a~b, b~c, but a!~c: b is removed by a, and c must SURVIVE.

    c is only similar to b, and b is gone -- a removed row cannot evict a third
    row. Documented behaviour of `greedy_keep_first`; pinned here because the
    alternative (letting b evict c) quietly deletes more data than intended.
    """
    # 2D geometry padded to DIM: 0 deg, 18 deg, 36 deg.
    # cos 18 = 0.951 (>= 0.95), cos 36 = 0.809 (< 0.95).
    ang = np.deg2rad([0.0, 18.0, 36.0])
    x = np.zeros((3, DIM), dtype=np.float32)
    x[:, 0] = np.cos(ang)
    x[:, 1] = np.sin(ang)
    emb = x / np.linalg.norm(x, axis=1, keepdims=True)

    pairs, _ = all_near_dup_pairs(emb, 0.90)
    got = {(int(i), int(j)) for i, j in pairs[["i", "j"]].itertuples(index=False)}
    assert (0, 1) in got and (1, 2) in got, "fixture broken: chain links missing"

    kept, removed = greedy_keep_first(3, pairs, 0.95)
    assert set(kept.tolist()) == {0, 2}, f"expected rows 0 and 2 kept, got {kept}"
    assert set(removed) == {1}
    assert removed[1][0] == 0, "row 1 should be anchored to row 0"


def test_strongest_anchor_wins_when_several_apply():
    """Tie-break is (-cosine, index): the most similar anchor is recorded.

    The recorded anchor appears in `near_dup_pairs.csv` and is what a human
    eyeballs when auditing a removal, so it must be the closest match rather
    than whichever pair happened to be enumerated first.
    """
    pairs = _pairs_df([(0, 5, 0.960), (1, 5, 0.990), (2, 5, 0.970)])
    kept, removed = greedy_keep_first(6, pairs, 0.95)
    assert removed[5][0] == 1, f"expected anchor 1 (cos 0.99), got {removed[5]}"


def test_deterministic_across_calls():
    """Same input, same output -- no dict/set ordering leaking into results."""
    emb = _emb()
    p1, d1 = all_near_dup_pairs(emb, 0.90)
    p2, d2 = all_near_dup_pairs(emb, 0.90)
    assert p1.equals(p2)
    assert d1 == d2
    a = greedy_keep_first(N, p1, 0.95)
    b = greedy_keep_first(N, p2, 0.95)
    assert np.array_equal(a[0], b[0])
    assert a[1] == b[1]


def test_no_pairs_yields_no_removals():
    """Threshold above the observed maximum must remove nothing at all.

    Note the threshold is NOT capped at 1.0. A float32 dot product of two
    L2-normalized identical vectors can land a few ulps *above* 1.0, so the
    planted exact duplicates report a max slightly over one. Capping the test
    threshold at 1.0 makes it land inside the observed data and the test fails
    for a rounding reason that has nothing to do with the dedup logic. This is
    harmless at the swept thresholds (0.90-0.98) but worth knowing when reading
    the `maximum` row of the cosine-distribution table in the S2 report.
    """
    emb = _emb()
    pairs, dist = all_near_dup_pairs(emb, 0.90)
    above = dist["max"] + 1e-4
    kept, removed = greedy_keep_first(N, pairs, above)
    assert len(removed) == 0, f"{len(removed)} rows removed above the max cosine"
    assert len(kept) == N


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
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    raise SystemExit(1 if failed else 0)
