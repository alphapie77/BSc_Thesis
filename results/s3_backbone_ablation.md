# S3.2 — verifier backbone ablation

**Verdict: `TIE`** · robustness (pooled across learning rates, no selection): `TIE` — **agree**

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
| `banglabert` | 0.9647 | 0.0209 | 3e-05 |
| `setfit_labse` | 0.9590 | 0.0000 | 2e-05 |
| `indicbertv2` | 0.9560 | 0.0156 | 3e-05 |
| `muril` | 0.9421 | 0.0391 | 3e-05 |
| `mbert` | 0.9402 | 0.0125 | 2e-05 |
| `xlmr` | 0.9360 | 0.0219 | 3e-05 |
| `bert_nli` | 0.9298 | 0.0165 | 3e-05 |

## Pairwise paired bootstrap

| A | B | diff | 95% CI | p | significant (BH) |
|---|---|---|---|---|---|
| `banglabert` | `xlmr` | +0.0426 | [+0.0000, +0.0973] | 0.0960 | no |
| `banglabert` | `muril` | +0.0139 | [+0.0000, +0.0457] | 0.7338 | no |
| `banglabert` | `mbert` | +0.0413 | [+0.0000, +0.0941] | 0.0966 | no |
| `banglabert` | `indicbertv2` | +0.0139 | [-0.0310, +0.0669] | 0.7922 | no |
| `banglabert` | `bert_nli` | +0.0401 | [+0.0000, +0.0908] | 0.0960 | no |
| `banglabert` | `setfit_labse` | +0.0139 | [+0.0000, +0.0457] | 0.7338 | no |
| `xlmr` | `muril` | -0.0287 | [-0.0746, +0.0000] | 0.2652 | no |
| `xlmr` | `mbert` | -0.0013 | [-0.0593, +0.0551] | 0.9486 | no |
| `xlmr` | `indicbertv2` | -0.0287 | [-0.0897, +0.0275] | 0.4550 | no |
| `xlmr` | `bert_nli` | -0.0025 | [-0.0703, +0.0649] | 0.8592 | no |
| `xlmr` | `setfit_labse` | -0.0287 | [-0.0746, +0.0000] | 0.2652 | no |
| `muril` | `mbert` | +0.0274 | [+0.0000, +0.0724] | 0.2702 | no |
| `muril` | `indicbertv2` | +0.0000 | [-0.0569, +0.0575] | 1.0000 | no |
| `muril` | `bert_nli` | +0.0262 | [-0.0267, +0.0828] | 0.4444 | no |
| `muril` | `setfit_labse` | +0.0000 | [+0.0000, +0.0000] | 1.0000 | no |
| `mbert` | `indicbertv2` | -0.0274 | [-0.0851, +0.0267] | 0.4478 | no |
| `mbert` | `bert_nli` | -0.0012 | [-0.0566, +0.0545] | 0.9516 | no |
| `mbert` | `setfit_labse` | -0.0274 | [-0.0724, +0.0000] | 0.2702 | no |
| `indicbertv2` | `bert_nli` | +0.0262 | [-0.0402, +0.0941] | 0.5456 | no |
| `indicbertv2` | `setfit_labse` | +0.0000 | [-0.0575, +0.0569] | 1.0000 | no |
| `bert_nli` | `setfit_labse` | -0.0262 | [-0.0827, +0.0267] | 0.4444 | no |

## Tie — and it was pre-registered as the likely outcome

No arm significantly beats every other. Per protocol.md §S3.2 the tie is
**reported as the result**, and the tie-break `['smallest_params', 'banglabert']`
is applied on non-performance grounds. The thesis must state that **the
backbone choice was not determined by the data.**
