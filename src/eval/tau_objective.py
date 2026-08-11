#!/usr/bin/env python3
"""tau selection, done the way `kotte2026ucci` do it. Decision 19, settled.

Sabbir, 2026-08-11: *"abar amar shiddhanto ki vai. tmk paper dekhte bolsi
emnei nki. paper er moto kora lagbe."* -- the point of reading the paper was
that the paper supplies the method. He is right; the previous version of this
file computed the cost curve and then handed him a menu of three options,
which is the opposite of what was asked.

⚠️ PROVENANCE: Sabbir delegated; the choice and reasoning below are Claude's,
endorsed not authored -- recorded that way in protocol.md, as for decisions
12, 14 and 16.

WHAT THE PAPER ACTUALLY DOES (kotte2026ucci, SS3 and Fig. 2)
----------------------------------------------------------
    min_pi E[C_pi(x)]   s.t.   E[Acc_pi(x)] >= target

and, crucially: *"Given a target accuracy tau in [alpha_s, alpha_l]"*. The
constraint is **bounded by two measured endpoints** -- the cheap system's
accuracy and the expensive system's. It is not a number anyone picks out of
the air. They then publish the entire Pareto frontier and compare methods **at
matched operating points**.

OUR TRANSLATION -- both endpoints are things SS5.1 already measures
------------------------------------------------------------------
tau controls how strict the Critic is, so the two ends of tau ARE the two ends
of the cost/quality range:

    alpha_lo  tau = 0. The Critic never rejects; the first draft ships.
              Exactly SS5.1 row 1 (zero-shot, no loop). 1 call.
    alpha_hi  tau = 1. Every plot runs all 3 attempts and emits best-of-3.
              The maximum-cost end of our own system.

**Quality at both ends is measured by Verifier-B, never Verifier-A.**
Verifier-A is inside the loop; constraining the loop by its own judge is
precisely the Goodhart collapse inviolable rule 6 exists to prevent. This is
the one place our setup is *stricter* than UCCI's, which has no such wall.

THE HEADLINE OPERATING POINT, WITH NO FREE CONSTANT
---------------------------------------------------
UCCI pick 0.91 between 0.847 and 0.932 -- 74.1% of the way up the achievable
range. That fraction is a deployment choice they were entitled to make and we
are not: picking our own would reintroduce exactly the hand-written constant
this project spent 2026-08-11 removing.

So the headline tau is defined by an argmax with **nothing to choose**:

    tau* = argmax_tau  [ quality(tau) - alpha_lo ] / E[calls](tau)

the point buying the most quality per LLM call. It is derived, reproducible,
and has no tunable parameter. **The full frontier is reported regardless** --
that is the deliverable, as in their Fig. 2 -- so naming tau* hides nothing
and a reader who prefers another operating point can read it off.

THE COST MODEL, from SS4.2's loop
--------------------------------
Writer call per attempt; Reflector per FAIL except after the last (nothing
left to feed); Researcher is free -- SS4.2 makes it a deterministic
tool-caller. With q = per-attempt pass rate and 3 attempts:

    E[calls]  = 1 + 2(1-q) + 2(1-q)^2
    P(accept) = 1 - (1-q)^3

🔴 Why the constraint is not optional: cost-per-accepted is monotonically
decreasing in q (16.310 at q=0.10 down to 1.020 at q=0.99), so minimising cost
ALONE selects q=1, tau=0 -- the cheapest loop never rejects anything. The
objective without the constraint is degenerate. That is the whole reason
SS4.5's "first-pass 60-70%" could never have been derived: it was a constraint
wearing an optimum's clothes.

WHAT CANNOT BE RUN YET
----------------------
quality(tau) needs generations, and Phase 4 has produced none. This file
therefore ships the *procedure*, pre-registered before any number exists, plus
a synthetic demonstration that the selection rule behaves. `kapur2026length`
rule out using dev-82 human reviews as a stand-in for generated text.

Usage:  python src/eval/tau_objective.py
"""
from __future__ import annotations

import csv
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEV_PRED = REPO / "results" / "s3c_verifier_a_dev_predictions.csv"
MAX_ATTEMPTS = 3


def expected_calls(q: float, max_attempts: int = MAX_ATTEMPTS) -> float:
    """Expected LLM calls per plot under SS4.2's loop."""
    calls = 0.0
    for k in range(max_attempts):
        reach = (1.0 - q) ** k
        calls += reach
        if k < max_attempts - 1:
            calls += reach * (1.0 - q)
    return calls


def p_accepted(q: float, max_attempts: int = MAX_ATTEMPTS) -> float:
    return 1.0 - (1.0 - q) ** max_attempts


def select_tau(frontier: list[tuple[float, float, float]]) -> dict:
    """The pre-registered selection rule.

    frontier: list of (tau, quality_by_verifier_B, expected_calls), where the
    tau = 0 row is alpha_lo (no rejection) and the last row is alpha_hi.

    Returns the headline operating point and the endpoints that bound it.
    """
    if len(frontier) < 2:
        raise ValueError("frontier needs at least the two endpoints")
    alpha_lo = frontier[0][1]
    alpha_hi = max(row[1] for row in frontier)

    best = None
    for tau, quality, calls in frontier:
        if calls <= 0:
            continue
        efficiency = (quality - alpha_lo) / calls
        if best is None or efficiency > best["efficiency"]:
            best = {"tau": tau, "quality": quality, "calls": calls,
                    "efficiency": efficiency}

    achievable = alpha_hi - alpha_lo
    best["alpha_lo"] = alpha_lo
    best["alpha_hi"] = alpha_hi
    best["fraction_of_achievable"] = (
        (best["quality"] - alpha_lo) / achievable if achievable > 0 else None
    )
    return best


def main() -> int:
    print(__doc__.split("Usage:")[0])

    print("=" * 72)
    print("COST MODEL -- why the constraint is mandatory")
    print("=" * 72)
    print(f"{'q':>8} {'E[calls]':>10} {'P(accept)':>11} {'calls/accepted':>16}")
    for q in (0.10, 0.30, 0.50, 0.65, 0.80, 0.99):
        c, a = expected_calls(q), p_accepted(q)
        print(f"{q:>8.2f} {c:>10.3f} {a:>11.4f} {c / a:>16.3f}")
    print("\nMonotone decreasing -> unconstrained optimum is tau = 0.")
    print("The quality constraint is what makes the problem well posed.")

    print()
    print("=" * 72)
    print("SELECTION RULE -- synthetic demonstration, NOT A RESULT")
    print("  quality(tau) requires generations; Phase 4 has produced none.")
    print("  Numbers below are invented to show the rule behaves sensibly.")
    print("=" * 72)

    # Synthetic: quality rises with strictness then saturates; calls grow.
    demo = []
    for tau, q_pass, quality in [
        (0.00, 1.00, 0.620),   # alpha_lo -- first draft always ships
        (0.20, 0.90, 0.681),
        (0.40, 0.75, 0.734),
        (0.60, 0.55, 0.769),
        (0.80, 0.35, 0.784),
        (1.00, 0.00, 0.790),   # alpha_hi -- always 3 attempts, best-of-3
    ]:
        demo.append((tau, quality, expected_calls(q_pass)))

    print(f"{'tau':>6} {'VerifierB':>11} {'E[calls]':>10} {'gain/call':>11}")
    for tau, quality, calls in demo:
        print(f"{tau:>6.2f} {quality:>11.3f} {calls:>10.3f} "
              f"{(quality - demo[0][1]) / calls:>11.4f}")

    chosen = select_tau(demo)
    print(f"\n  alpha_lo (row 1, no loop)      = {chosen['alpha_lo']:.3f}")
    print(f"  alpha_hi (always 3, best-of-3) = {chosen['alpha_hi']:.3f}")
    print(f"  headline tau*                  = {chosen['tau']:.2f}")
    print(f"    quality {chosen['quality']:.3f} at {chosen['calls']:.3f} calls, "
          f"{chosen['fraction_of_achievable']:.1%} of achievable gain")
    print("\n  The full frontier above is the reported deliverable, as in")
    print("  kotte2026ucci Fig. 2. tau* names a point on it; it hides nothing.")

    if DEV_PRED.exists():
        rows = list(csv.DictReader(DEV_PRED.open(encoding="utf-8-sig")))
        scores = sorted(float(r["p_cluster1"]) for r in rows)
        n = len(scores)
        uni = [sum(1 for s in scores if s >= 0.30 + 0.05 * i) / n
               for i in range(14)]
        qs = [sum(1 for s in scores if s >= scores[int(round(p * (n - 1)))]) / n
              for p in [i / 13 for i in range(14)]]
        print()
        print("=" * 72)
        print("GRID CHECK on dev-82 (NOT A RESULT -- human text, not generated)")
        print("=" * 72)
        print(f"  uniform 0.30-0.95 reaches pass-rates "
              f"{min(uni):.2f}-{max(uni):.2f}  ({len(set(uni))} distinct)")
        print(f"  quantile-spaced   reaches pass-rates "
              f"{min(qs):.2f}-{max(qs):.2f}  ({len(set(qs))} distinct)")
        print("  -> thresholds are placed at observed scores, not on a fixed grid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
