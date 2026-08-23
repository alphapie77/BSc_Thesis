# S5 Bangla thesis-ready reporting tables

**UTC:** `2026-08-23T09:30:13.715784+00:00`  
**Producing commit:** `0bda93f10055191bd9942108b7b343092f8b72c2`  
**Standing:** formatting-only view of audited tables; no inference recomputed.

## Main table — Verifier-B outcome scoring

| Condition | Level | n | Mean target p | Binary accuracy | Mean calls | Mean tokens | Gave-up |
|---|---:|---:|---:|---:|---:|---:|---:|
| blind_resampling | 0 | 270 | 0.6485 | 0.6444 | 1.456 | 1385.5 | 0.0000 |
| blind_resampling | 1 | 270 | 0.8995 | 0.9407 | 1.326 | 1115.3 | 0.0000 |
| external_role_self_critique | 0 | 270 | 0.6109 | 0.6111 | 3.000 | 3085.4 | 0.0000 |
| external_role_self_critique | 1 | 270 | 0.8806 | 0.9222 | 3.000 | 2757.6 | 0.0000 |
| gemma4_26b_a4b_judge_loop | 0 | 270 | 0.6286 | 0.6296 | 1.389 | 1339.2 | 0.0111 |
| gemma4_26b_a4b_judge_loop | 1 | 270 | 0.8450 | 0.8815 | 1.033 | 869.2 | 0.0000 |
| intrinsic_self_critique | 0 | 270 | 0.6791 | 0.6815 | 3.000 | 3086.7 | 0.0000 |
| intrinsic_self_critique | 1 | 270 | 0.8809 | 0.9222 | 3.000 | 2757.8 | 0.0000 |
| rag_neural_loop | 0 | 270 | 0.6890 | 0.6889 | 1.904 | 1511.5 | 0.0926 |
| rag_neural_loop | 1 | 270 | 0.9124 | 0.9630 | 1.681 | 1231.2 | 0.0556 |
| rag_neural_symbolic_feedback | 0 | 270 | 0.7323 | 0.7333 | 1.889 | 1510.3 | 0.0630 |
| rag_neural_symbolic_feedback | 1 | 270 | 0.9123 | 0.9593 | 1.630 | 1215.3 | 0.0593 |
| rag_only | 0 | 270 | 0.5314 | 0.5185 | 1.000 | 955.1 | 0.0000 |
| rag_only | 1 | 270 | 0.8358 | 0.8704 | 1.000 | 840.8 | 0.0000 |
| rag_symbolic_loop | 0 | 270 | 0.5314 | 0.5185 | 1.022 | 969.3 | 0.0000 |
| rag_symbolic_loop | 1 | 270 | 0.8176 | 0.8519 | 3.630 | 2409.4 | 0.5333 |
| static_few_shot | 0 | 270 | 0.6109 | 0.6037 | 1.000 | 823.0 | 0.0000 |
| static_few_shot | 1 | 270 | 0.8100 | 0.8407 | 1.000 | 766.1 | 0.0000 |
| zero_shot | 0 | 270 | 0.3513 | 0.3296 | 1.000 | 590.3 | 0.0000 |
| zero_shot | 1 | 270 | 0.7794 | 0.8074 | 1.000 | 601.4 | 0.0000 |

## Planned paired statistics — each condition vs zero-shot

| Condition | Pairs | Delta target p | 95% CI | Bootstrap p | BH q | McNemar p |
|---|---:|---:|---:|---:|---:|---:|
| rag_neural_symbolic_feedback | 540 | +0.2570 | [+0.2151, +0.2987] | 0.00019998 | 0.00019998 | 1.46143e-28 |
| rag_neural_loop | 540 | +0.2354 | [+0.1934, +0.2772] | 0.00019998 | 0.00019998 | 2.69773e-25 |
| intrinsic_self_critique | 540 | +0.2147 | [+0.1711, +0.2584] | 0.00019998 | 0.00019998 | 9.61886e-21 |
| blind_resampling | 540 | +0.2087 | [+0.1664, +0.2510] | 0.00019998 | 0.00019998 | 6.9051e-20 |
| external_role_self_critique | 540 | +0.1804 | [+0.1381, +0.2231] | 0.00019998 | 0.00019998 | 9.50945e-16 |
| gemma4_26b_a4b_judge_loop | 540 | +0.1715 | [+0.1282, +0.2149] | 0.00019998 | 0.00019998 | 1.65717e-13 |
| static_few_shot | 540 | +0.1451 | [+0.1001, +0.1897] | 0.00019998 | 0.00019998 | 1.65618e-09 |
| rag_only | 540 | +0.1182 | [+0.0753, +0.1618] | 0.00019998 | 0.00019998 | 3.18376e-07 |
| rag_symbolic_loop | 540 | +0.1091 | [+0.0649, +0.1524] | 0.00019998 | 0.00019998 | 2.8644e-06 |

## Blinded human validation — frozen 100-item subset

| Scope | n | Target-match accuracy | 95% item-bootstrap CI |
|---|---:|---:|---:|
| Annotator A | 100 | 0.9100 | [0.8500, 0.9600] |
| Annotator B | 100 | 0.9300 | [0.8800, 0.9800] |
| Annotator C | 100 | 0.9000 | [0.8400, 0.9500] |
| Pooled | 300 | 0.9133 | [0.8667, 0.9567] |

Raw three-way agreement: **0.8800**.  
Nominal Krippendorff alpha: **0.8405** (95% item-bootstrap CI [0.7473, 0.9200]).  
Both requested levels received 137/150 correct judgments. These ratings validate human recoverability of the requested engagement-specificity level on the balanced subset; they do not validate audience prediction or rank systems.

## Reporting constraints

- Verifier-B calibration improvement was not established; report this beside outcome scores.
- Seeds 42/43/44 are paired blocking/sensitivity factors, not independent study replications.
- Human validation covers a frozen balanced 100-item subset, not all 5,400 generated outputs.
- The English mirror is deferred and is not represented by an invented or partial column.
- The registered dev-plot mini-ablations are not represented by this main-run table and are not inferred post hoc.
