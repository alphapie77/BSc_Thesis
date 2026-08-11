#!/usr/bin/env python3
"""What is tau optimising? The cost model, written out and computed.

Open decision 19. Sabbir, 2026-08-11: *"dekho paper e kivabe deya oita hishab
kore koro"* -- take the formulation the paper gives and actually compute it,
rather than describing it.

THE PAPER'S FORMULATION (`kotte2026ucci`, SS3, Thm 1)
--------------------------------------------------
    min_pi  E[C_pi(x)]   s.t.   E[Acc_pi(x)] >= target

and they prove a THRESHOLD policy on the calibrated score is optimal for this
-- but only *given* the constraint. That qualifier is the whole point of this
file.

OUR LOOP, ADAPTED
-----------------
SS4.2's loop, per plot:

    attempt 1 : Writer call
                PASS -> stop
                FAIL -> Reflector call, then attempt 2
    attempt 2 : same
    attempt 3 : PASS, or emit best-of-3 with gave_up=True. No Reflector after
                the last attempt -- there is nothing left to feed.

The Researcher makes NO LLM call (deterministic tool-caller, SS4.2), so it does
not enter the cost. Writer and Reflector each cost one call; we count calls
rather than currency because Groq's free tier makes money the wrong unit and
call count is what actually binds.

Let q(tau) = P(hybrid score >= tau) for one attempt. Then

    E[calls]    = 1 + 2(1-q) + 2(1-q)^2
    P(accepted) = 1 - (1-q)^3
    cost_per_accepted = E[calls] / P(accepted)

🔴 THE RESULT THAT MATTERS, AND IT IS A NEGATIVE ONE
----------------------------------------------------
Minimising cost_per_accepted alone is **degenerate**: it is monotonically
decreasing in q, so it is minimised at q = 1, i.e. **tau = 0 -- accept
everything on the first try**. A loop that never rejects is the cheapest loop.

So SS4.5's *"operating point (first-pass 60-70%)"* cannot be derived from a cost
objective, because the cost objective on its own says 100%. The pass rate is
not an optimum; it is a **constraint standing in for a quality floor that was
never written down.**

This is the same defect as the struck `0.6/0.4` weight: a number with a value
and no criterion. UCCI's Theorem 1 needs BOTH halves, and we have one.

WHAT WOULD FIX IT
-----------------
A quality floor measured by **Verifier-B**, never A -- A is inside the loop, so
constraining the loop by its own judge is the Goodhart failure inviolable rule
6 exists to prevent. Then tau is whatever meets the floor most cheaply, and
Thm 1 applies.

⚠️ q(tau) CANNOT BE MEASURED YET. It is a property of *generated* text, and
Phase 4 has produced none. `kapur2026length` show the length/specificity
relation differs between human and machine text, so the dev-82 human reviews
are NOT a stand-in. The dev-82 curve printed below is therefore labelled
NOT A RESULT and exists only to show the machinery runs and the shape is real.

Usage:  python src/eval/tau_objective.py
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEV_PRED = REPO / "results" / "s3c_verifier_a_dev_predictions.csv"
MAX_ATTEMPTS = 3


def expected_calls(q: float, max_attempts: int = MAX_ATTEMPTS) -> float:
    """Expected LLM calls per plot: one Writer per attempt, one Reflector per
    FAIL except after the final attempt."""
    calls = 0.0
    for k in range(max_attempts):
        reach = (1.0 - q) ** k          # P(still going at attempt k+1)
        calls += reach                  # the Writer call
        if k < max_attempts - 1:
            calls += reach * (1.0 - q)  # Reflector, only if this attempt fails
    return calls


def p_accepted(q: float, max_attempts: int = MAX_ATTEMPTS) -> float:
    return 1.0 - (1.0 - q) ** max_attempts


def main() -> int:
    print(__doc__.split("Usage:")[0])
    print("=" * 72)
    print("THE COST CURVE, computed from the formula above")
    print("=" * 72)
    print(f"{'q (per-attempt pass)':>22} {'E[calls]':>10} {'P(accept)':>10} "
          f"{'calls/accepted':>15}")
    for q in (0.10, 0.30, 0.50, 0.60, 0.65, 0.70, 0.80, 0.90, 0.99):
        c, a = expected_calls(q), p_accepted(q)
        print(f"{q:>22.2f} {c:>10.3f} {a:>10.4f} {c / a:>15.3f}")

    print()
    print("🔴 cost_per_accepted falls monotonically as q rises, so minimising")
    print("   it alone selects q = 1, i.e. tau = 0. The cheapest loop is the")
    print("   one that never rejects anything.")
    print()
    print("   SS4.5's 60-70% first-pass target is therefore NOT an optimum.")
    print("   It is a constraint standing in for an unstated quality floor.")
    print("   Decision 19 has to supply the floor, or relabel the target as a")
    print("   convention rather than a derived operating point.")

    # ----------------------------------------------------------------
    # Illustration only. See the docstring: this is human review text, and
    # kapur2026length says it does not transfer to generated text.
    # ----------------------------------------------------------------
    if not DEV_PRED.exists():
        print(f"\n(dev predictions not found at {DEV_PRED}; skipping shape demo)")
        return 0

    rows = list(csv.DictReader(DEV_PRED.open(encoding="utf-8-sig")))
    scores = sorted(float(r["p_cluster1"]) for r in rows)
    n = len(scores)

    print()
    print("=" * 72)
    print("⚠️  NOT A RESULT -- shape demonstration on dev-82 HUMAN reviews")
    print("    q(tau) for generated text is unmeasured. This only shows that")
    print("    quantile spacing reaches operating points a uniform grid misses.")
    print("=" * 72)

    def q_at(tau: float) -> float:
        return sum(1 for s in scores if s >= tau) / n

    uniform = [0.30 + 0.05 * i for i in range(14)]
    quantile = [scores[int(round(p * (n - 1)))] for p in
                [i / 13 for i in range(14)]]

    for name, grid in (("uniform 0.30-0.95", uniform),
                       ("quantile-spaced", quantile)):
        qs = [q_at(t) for t in grid]
        distinct = len(set(qs))
        print(f"\n{name:>20}: {distinct:2d} distinct pass-rates out of "
              f"{len(grid)} thresholds")
        print(f"{'':>20}  q = " + " ".join(f"{v:.2f}" for v in qs))

    print()
    print("The uniform grid spends thresholds where no items lie. Quantile")
    print("spacing puts one threshold between each pair of observed scores,")
    print("which is where the operating points actually are.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
