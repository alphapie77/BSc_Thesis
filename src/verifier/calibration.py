"""S3.4 -- calibration, deliberately kept small and descriptive.

Pre-registered in `docs/protocol.md` section "S3.4 pre-commitment" (5 bins,
bootstrap CI, figure labelled descriptive) and section "S3.3 pre-commitment"
(which makes this stage *mandatory* for Verifier-A after the "natively
calibrated" claim was withdrawn on 2026-08-11).

Two design points worth stating, because both are places where a more
sophisticated choice would be worse rather than better:

**Five bins, not ten.** The dev slice is 82 rows. Ten bins gives ~8 samples per
bin and the ECE estimate is then dominated by binning noise. `guo2017calibration`
popularised 10 bins on datasets three orders of magnitude larger; carrying the
number over unexamined is how a sample-size problem becomes a figure.

**Temperature scaling, not an adaptive calibrator.** Balanya et al. (2022) show
expressive calibrators fail under data scarcity while simple scaling stays
robust, and Guo et al. (2025) attribute that failure to variance from
insufficient validation data. So the *simple* method here is the literature's
recommendation at this n, not a concession to effort.

**The temperature is fitted on dev-82 and reported as fitted there.** There is
no second slice at this n, and an in-sample temperature labelled in-sample is
honest where a held-out one would be fiction. Every ECE-after number in this
project therefore carries that label.

No numpy, no scipy, no torch: this file must run in the CPU dry-run before any
heavy install, and a reviewer should be able to read it end to end.
"""

from __future__ import annotations

import math
import random
from dataclasses import asdict, dataclass

#: Pre-registered in protocol.md (2026-08-08 S3.4 amendment). Changing this
#: without editing that section first is a protocol breach.
N_BINS = 5

#: Bootstrap resamples for the CI around ECE and Brier. Matches compare.py.
N_RESAMPLES = 10_000


def _sigmoid(z: float) -> float:
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


def _logit(p: float, eps: float = 1e-12) -> float:
    p = min(1.0 - eps, max(eps, p))
    return math.log(p / (1.0 - p))


def expected_calibration_error(
    y_true: list[int], p_pos: list[float], *, n_bins: int = N_BINS
) -> float:
    """Equal-width-bin ECE on the *confidence of the predicted class*.

    Binary task, so confidence is max(p, 1-p) and the prediction is p >= 0.5.
    Empty bins contribute nothing, which is the standard convention and the
    reason the number drifts downward as bins outnumber samples -- the argument
    for five bins rather than ten at n = 82.
    """
    n = len(y_true)
    if n == 0:
        raise ValueError("cannot compute ECE on an empty set")
    bins: list[list[tuple[float, int]]] = [[] for _ in range(n_bins)]
    for y, p in zip(y_true, p_pos):
        pred = 1 if p >= 0.5 else 0
        conf = p if pred == 1 else 1.0 - p
        idx = min(n_bins - 1, int(conf * n_bins))
        bins[idx].append((conf, 1 if pred == y else 0))
    ece = 0.0
    for b in bins:
        if not b:
            continue
        acc = sum(c for _, c in b) / len(b)
        conf = sum(cf for cf, _ in b) / len(b)
        ece += (len(b) / n) * abs(acc - conf)
    return ece


def brier_score(y_true: list[int], p_pos: list[float]) -> float:
    """Mean squared error of the positive-class probability."""
    return sum((p - y) ** 2 for y, p in zip(y_true, p_pos)) / len(y_true)


def negative_log_likelihood(y_true: list[int], p_pos: list[float], eps: float = 1e-12) -> float:
    total = 0.0
    for y, p in zip(y_true, p_pos):
        p = min(1.0 - eps, max(eps, p))
        total += -math.log(p if y == 1 else 1.0 - p)
    return total / len(y_true)


def reliability_bins(
    y_true: list[int], p_pos: list[float], *, n_bins: int = N_BINS
) -> list[dict]:
    """Per-bin (count, mean confidence, empirical accuracy) for the figure.

    Returned as data rather than drawn, so the reliability diagram in Ch.4 is
    generated from a result file and not from a live model.
    """
    bins: list[list[tuple[float, int]]] = [[] for _ in range(n_bins)]
    for y, p in zip(y_true, p_pos):
        pred = 1 if p >= 0.5 else 0
        conf = p if pred == 1 else 1.0 - p
        bins[min(n_bins - 1, int(conf * n_bins))].append((conf, 1 if pred == y else 0))
    out = []
    for i, b in enumerate(bins):
        lo, hi = i / n_bins, (i + 1) / n_bins
        out.append(
            {
                "bin": f"[{lo:.1f}, {hi:.1f})",
                "n": len(b),
                "mean_confidence": (sum(c for c, _ in b) / len(b)) if b else None,
                "empirical_accuracy": (sum(c for _, c in b) / len(b)) if b else None,
            }
        )
    return out


def fit_temperature(
    y_true: list[int], p_pos: list[float], *, lo: float = 0.05, hi: float = 20.0
) -> float:
    """Temperature minimising NLL of sigmoid(logit(p) / T), by golden section.

    Golden section rather than gradient descent because the objective is
    one-dimensional, smooth and unimodal in log T, and a 40-line deterministic
    search has no learning rate to justify. T > 1 softens confidence, T < 1
    sharpens it.
    """
    logits = [_logit(p) for p in p_pos]

    def nll(t: float) -> float:
        return negative_log_likelihood(y_true, [_sigmoid(z / t) for z in logits])

    a, b = math.log(lo), math.log(hi)
    inv_phi = (math.sqrt(5.0) - 1.0) / 2.0
    c, d = b - inv_phi * (b - a), a + inv_phi * (b - a)
    fc, fd = nll(math.exp(c)), nll(math.exp(d))
    for _ in range(200):
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - inv_phi * (b - a)
            fc = nll(math.exp(c))
        else:
            a, c, fc = c, d, fd
            d = a + inv_phi * (b - a)
            fd = nll(math.exp(d))
        if abs(b - a) < 1e-10:
            break
    return math.exp((a + b) / 2.0)


def apply_temperature(p_pos: list[float], temperature: float) -> list[float]:
    return [_sigmoid(_logit(p) / temperature) for p in p_pos]


@dataclass(frozen=True)
class CalibrationReport:
    n: int
    n_bins: int
    temperature: float
    ece_before: float
    ece_after: float
    ece_delta: float
    ece_delta_ci_low: float
    ece_delta_ci_high: float
    brier_before: float
    brier_after: float
    nll_before: float
    nll_after: float
    verdict: str
    bins_before: list
    bins_after: list
    temperature_fitted_on: str

    def to_dict(self) -> dict:
        return asdict(self)


def calibrate(
    y_true: list[int],
    p_pos: list[float],
    *,
    n_bins: int = N_BINS,
    n_resamples: int = N_RESAMPLES,
    seed: int = 42,
    fitted_on: str = "dev-82 (in-sample; no second slice exists at this n)",
) -> CalibrationReport:
    """Full S3.4 stage, including the pre-committed null verdict.

    The verdict is `CALIBRATION_NOT_ESTABLISHED` whenever the bootstrap CI of the
    ECE improvement contains zero. That statement was pre-committed on
    2026-08-08, before any verifier existed, precisely so that "temperature
    scaling helped a bit" could not be written from a number smaller than its
    own uncertainty.
    """
    t = fit_temperature(y_true, p_pos)
    p_cal = apply_temperature(p_pos, t)

    ece_b = expected_calibration_error(y_true, p_pos, n_bins=n_bins)
    ece_a = expected_calibration_error(y_true, p_cal, n_bins=n_bins)

    # Paired on items: each resample scores before and after on the SAME rows,
    # for the same reason compare.py pairs its bootstrap -- item difficulty is
    # the dominant variance component at n = 82.
    rng = random.Random(seed)
    n = len(y_true)
    deltas = []
    for _ in range(n_resamples):
        idx = [rng.randrange(n) for _ in range(n)]
        yt = [y_true[i] for i in idx]
        deltas.append(
            expected_calibration_error(yt, [p_pos[i] for i in idx], n_bins=n_bins)
            - expected_calibration_error(yt, [p_cal[i] for i in idx], n_bins=n_bins)
        )
    ordered = sorted(deltas)
    lo = ordered[int(0.025 * n_resamples)]
    hi = ordered[min(n_resamples - 1, int(0.975 * n_resamples))]

    verdict = (
        "CALIBRATION_NOT_ESTABLISHED"
        if lo <= 0.0 <= hi
        else "CALIBRATION_IMPROVED"
        if lo > 0.0
        else "CALIBRATION_DEGRADED"
    )

    return CalibrationReport(
        n=n,
        n_bins=n_bins,
        temperature=t,
        ece_before=ece_b,
        ece_after=ece_a,
        ece_delta=ece_b - ece_a,
        ece_delta_ci_low=lo,
        ece_delta_ci_high=hi,
        brier_before=brier_score(y_true, p_pos),
        brier_after=brier_score(y_true, p_cal),
        nll_before=negative_log_likelihood(y_true, p_pos),
        nll_after=negative_log_likelihood(y_true, p_cal),
        verdict=verdict,
        bins_before=reliability_bins(y_true, p_pos, n_bins=n_bins),
        bins_after=reliability_bins(y_true, p_cal, n_bins=n_bins),
        temperature_fitted_on=fitted_on,
    )
