"""The S3.2 decision rule: paired bootstrap + Benjamini-Hochberg.

Why this file exists at all, since "pick the highest mean macro-F1" is one line:
Bethard (2022) surveys 85 ACL Anthology papers and names *varying only the
random seed to build score distributions for performance comparison* a risky
use of seeds -- which is precisely what picking the arm with the best
mean +/- SD does. Sensitivity measurement is a safe use, so seed spread is still
reported; it is just not what decides anything.

The comparison is **paired on evaluation items**, not on seeds. Two arms are
compared by resampling the dev items with replacement and recomputing both arms'
scores on the same resample, which controls for item difficulty -- the dominant
source of variance at n=82.

Pre-registered in `docs/protocol.md` section "S3.2 pre-commitment". Do not edit
the defaults here without editing that section first; the tests check they agree.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

#: Pre-registered in protocol.md. Changing either is a protocol deviation.
N_RESAMPLES = 10_000
ALPHA = 0.05


def macro_f1(y_true: list[int], y_pred: list[int], labels: tuple[int, ...] = (0, 1)) -> float:
    """Unweighted mean of per-class F1. No sklearn dependency, so this runs in
    the CPU dry-run before any heavy install."""
    f1s = []
    for c in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == c and p == c)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != c and p == c)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == c and p != c)
        denom = 2 * tp + fp + fn
        f1s.append(0.0 if denom == 0 else 2 * tp / denom)
    return sum(f1s) / len(f1s)


@dataclass(frozen=True)
class PairedResult:
    arm_a: str
    arm_b: str
    observed_diff: float
    p_value: float
    ci_low: float
    ci_high: float
    n_items: int
    n_resamples: int


def paired_bootstrap(
    y_true: list[int],
    pred_a: list[int],
    pred_b: list[int],
    *,
    arm_a: str = "A",
    arm_b: str = "B",
    n_resamples: int = N_RESAMPLES,
    seed: int = 42,
) -> PairedResult:
    """Two-sided paired bootstrap on macro-F1 difference (arm_a - arm_b).

    The p-value is the proportion of resamples in which the difference reverses
    sign or vanishes, doubled for two-sidedness and clamped to <= 1.0. A
    difference of exactly zero counts against significance, which is the
    conservative choice.
    """
    n = len(y_true)
    if not (len(pred_a) == len(pred_b) == n):
        raise ValueError("y_true, pred_a and pred_b must be the same length")
    if n == 0:
        raise ValueError("cannot bootstrap an empty evaluation set")

    observed = macro_f1(y_true, pred_a) - macro_f1(y_true, pred_b)
    rng = random.Random(seed)
    diffs = []
    for _ in range(n_resamples):
        idx = [rng.randrange(n) for _ in range(n)]
        yt = [y_true[i] for i in idx]
        diffs.append(macro_f1(yt, [pred_a[i] for i in idx]) - macro_f1(yt, [pred_b[i] for i in idx]))

    if observed >= 0:
        tail = sum(1 for d in diffs if d <= 0)
    else:
        tail = sum(1 for d in diffs if d >= 0)
    p = min(1.0, 2.0 * tail / n_resamples)

    ordered = sorted(diffs)
    lo = ordered[int(0.025 * n_resamples)]
    hi = ordered[min(n_resamples - 1, int(0.975 * n_resamples))]
    return PairedResult(arm_a, arm_b, observed, p, lo, hi, n, n_resamples)


def benjamini_hochberg(p_values: list[float], alpha: float = ALPHA) -> list[bool]:
    """Return, per input p-value, whether it is rejected at FDR `alpha`.

    Order is preserved: `out[i]` corresponds to `p_values[i]`. With 7 arms there
    are 21 pairwise comparisons, and uncorrected testing at 0.05 would expect
    about one spurious "winner" per run -- which is exactly the number a reader
    would seize on.
    """
    m = len(p_values)
    if m == 0:
        return []
    order = sorted(range(m), key=lambda i: p_values[i])
    rejected = [False] * m
    k_max = -1
    for rank, i in enumerate(order, start=1):
        if p_values[i] <= alpha * rank / m:
            k_max = rank
    for rank, i in enumerate(order, start=1):
        if rank <= k_max:
            rejected[i] = True
    return rejected


def verdict(
    arm_names: list[str],
    mean_scores: dict[str, float],
    significant_pairs: set[tuple[str, str]],
) -> str:
    """Map the test outcome onto the pre-registered bands in protocol.md.

    Returns one of: SINGLE_WINNER, TIE, NEAR_CHANCE_PENDING.
    The near-chance band is decided by the caller against the observed scores --
    this function only distinguishes a resolved winner from an unresolved field,
    because that is the distinction the bootstrap can make.
    """
    best = max(arm_names, key=lambda a: mean_scores[a])
    beats_all = all(
        (best, other) in significant_pairs or (other, best) in significant_pairs
        for other in arm_names
        if other != best
    )
    return "SINGLE_WINNER" if beats_all else "TIE"
