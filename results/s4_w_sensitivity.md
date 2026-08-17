# S4.5a — `w` as a sensitivity curve

> `w` is **not** given a value here. `protocol.md` §S4 decision 1 registers it as a curve, and the curve is the deliverable. The three outcomes below were pre-committed on 2026-08-11, before any generation existed.

> 🔴 **Verdict audit:** the Kaggle measurements below are unchanged, but the original outcome mapper did not cover the observed sensitive-curve/held-out-tie combination. The audit state below supersedes the emitted `SYMBOLIC_INERT` labels.

> ⚠️ **The label is the level that was REQUESTED.** These numbers measure agreement with the instruction, not whether the text really sits at that level — the generator's compliance is assumed and cannot be checked without annotation. **No axis-control claim is made from this file.**

> ⚠️ **The baseline is not 0.5.** A word count alone recovers the requested level at AUC 0.91–0.99 (S4.dev-LC), so the reference for any hybrid score is the length-only probe, printed in every table below.

## length_controlled (n = 120)

| point | `w` | AUC vs requested level |
|---|---|---|
| symbolic only | 0.00 | 0.3417 |
| best on the grid | 1.00 | 0.8333 |
| neural only | 1.00 | 0.8333 |

| length-only probe (the real baseline) | AUC |
|---|---|
| bn | 0.9111 |
| en | 0.9928 |

**Verdict sensitivity to `w`:** 50.8% of generations change PASS/FAIL somewhere across the range (τ at the median hybrid; τ itself is decision 19's argmax and is not selected here).

**Held-out marginal value** (5 folds, grouped by plot): mixture beats neural-only in **0** folds, ties in 5, loses in 0. Mean ΔAUC **+0.0000**. `w` chosen per fold: [1.0, 1.0, 1.0, 1.0, 1.0].

### Audit state: `PRECOMMITMENT_UNRESOLVED`

**This is not a fourth scientific outcome.** The curve is not flat, so `SYMBOLIC_INERT` does not apply; the held-out test does not favour the symbolic term, so `SYMBOLIC_EARNS_ITS_PLACE` does not apply; and neural-only never beats the selected mixture, so `SYMBOLIC_HARMS` does not apply. The registered rule does not resolve this combination.

**Consequence:** no hybrid-accuracy claim and no single `w` is selected. The symbolic component remains available for its separately registered failed-rule-naming role; this result does not establish predictive value.
## free_length (n = 120)

| point | `w` | AUC vs requested level |
|---|---|---|
| symbolic only | 0.00 | 0.0656 |
| best on the grid | 1.00 | 0.8658 |
| neural only | 1.00 | 0.8658 |

| length-only probe (the real baseline) | AUC |
|---|---|
| bn | 0.9894 |
| en | 1.0000 |

**Verdict sensitivity to `w`:** 39.2% of generations change PASS/FAIL somewhere across the range (τ at the median hybrid; τ itself is decision 19's argmax and is not selected here).

**Held-out marginal value** (5 folds, grouped by plot): mixture beats neural-only in **0** folds, ties in 5, loses in 0. Mean ΔAUC **+0.0000**. `w` chosen per fold: [1.0, 1.0, 1.0, 1.0, 1.0].

### Audit state: `PRECOMMITMENT_UNRESOLVED`

**This is not a fourth scientific outcome.** The curve is not flat, so `SYMBOLIC_INERT` does not apply; the held-out test does not favour the symbolic term, so `SYMBOLIC_EARNS_ITS_PLACE` does not apply; and neural-only never beats the selected mixture, so `SYMBOLIC_HARMS` does not apply. The registered rule does not resolve this combination.

**Consequence:** no hybrid-accuracy claim and no single `w` is selected. The symbolic component remains available for its separately registered failed-rule-naming role; this result does not establish predictive value.
