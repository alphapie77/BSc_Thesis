# S3.2 — verifier backbone ablation

> ⛔ **DRY RUN — NOT A RESULT.** Predictions came from a deterministic
> length-threshold stub, not from any trained model. This file exists to
> prove the plumbing works before GPU time is spent.

**Verdict: `TIE`**

- train n = **804** {0: 481, 1: 323} · dev n = **82** {0: 53, 1: 29}
- seeds: [42, 43, 44, 45, 46] · decision rule: **paired bootstrap** (10000 resamples, BH at α=0.05)
- Gold-300 rows touched: **0**. R2 not read (role A → R1).

⚠️ The winner is selected on **weak-label macro-F1 — label *reproduction*,
not validity.** No human-validated accuracy exists for any verifier
(deviation of 2026-08-08). Any defence of the backbone choice must say so.

## Mean macro-F1 (± SD across seeds — sensitivity, not the decision rule)

SD is over the 5 seeds **at the selected learning rate**, not over all 10 runs.
⚠️ The learning rate was selected by best mean on this same dev set, so the
levels below are **not clean held-out estimates** and must not be quoted as such.

| Arm | mean macro-F1 | SD | selected lr |
|---|---|---|---|
| `banglabert` | 0.3854 | 0.0044 | 2e-05 |
| `indicbertv2` | 0.3744 | 0.0231 | 2e-05 |
| `muril` | 0.3621 | 0.0209 | 2e-05 |
| `setfit_labse` | 0.3617 | 0.0171 | 2e-05 |
| `mbert` | 0.3603 | 0.0232 | 2e-05 |
| `xlmr` | 0.3499 | 0.0180 | 2e-05 |
| `bert_nli` | 0.3431 | 0.0209 | 2e-05 |

## Pairwise paired bootstrap

| A | B | diff | 95% CI | p | significant (BH) |
|---|---|---|---|---|---|
| `banglabert` | `xlmr` | +0.0457 | [-0.0278, +0.1147] | 0.2092 | no |
| `banglabert` | `muril` | +0.0394 | [-0.0204, +0.0933] | 0.1750 | no |
| `banglabert` | `mbert` | +0.0394 | [-0.0204, +0.0933] | 0.1750 | no |
| `banglabert` | `indicbertv2` | +0.0081 | [-0.0481, +0.0526] | 0.6954 | no |
| `banglabert` | `setfit_labse` | +0.0394 | [-0.0204, +0.0933] | 0.1750 | no |
| `banglabert` | `bert_nli` | +0.0549 | [-0.0313, +0.1337] | 0.1830 | no |
| `xlmr` | `muril` | -0.0063 | [-0.0482, +0.0418] | 0.7518 | no |
| `xlmr` | `mbert` | -0.0063 | [-0.0482, +0.0418] | 0.7518 | no |
| `xlmr` | `indicbertv2` | -0.0375 | [-0.0910, +0.0195] | 0.1734 | no |
| `xlmr` | `setfit_labse` | -0.0063 | [-0.0482, +0.0418] | 0.7518 | no |
| `xlmr` | `bert_nli` | +0.0092 | [-0.0371, +0.0522] | 0.6562 | no |
| `muril` | `mbert` | +0.0000 | [+0.0000, +0.0000] | 1.0000 | no |
| `muril` | `indicbertv2` | -0.0313 | [-0.0650, -0.0070] | 0.0320 | no |
| `muril` | `setfit_labse` | +0.0000 | [+0.0000, +0.0000] | 1.0000 | no |
| `muril` | `bert_nli` | +0.0155 | [-0.0491, +0.0743] | 0.5832 | no |
| `mbert` | `indicbertv2` | -0.0313 | [-0.0650, -0.0070] | 0.0320 | no |
| `mbert` | `setfit_labse` | +0.0000 | [+0.0000, +0.0000] | 1.0000 | no |
| `mbert` | `bert_nli` | +0.0155 | [-0.0491, +0.0743] | 0.5832 | no |
| `indicbertv2` | `setfit_labse` | +0.0313 | [+0.0070, +0.0650] | 0.0320 | no |
| `indicbertv2` | `bert_nli` | +0.0467 | [-0.0245, +0.1138] | 0.1796 | no |
| `setfit_labse` | `bert_nli` | +0.0155 | [-0.0491, +0.0743] | 0.5832 | no |

## Tie — and it was pre-registered as the likely outcome

No arm significantly beats every other. Per protocol.md §S3.2 the tie is
**reported as the result**, and the tie-break `['smallest_params', 'banglabert']`
is applied on non-performance grounds. The thesis must state that **the
backbone choice was not determined by the data.**
