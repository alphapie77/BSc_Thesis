# Appendix F — Supplementary numerical results

This appendix is mechanically rendered from the audited CSV files named
under each table. Seeds are sensitivity or pairing blocks, not independent
studies. No value in this appendix is recomputed from model outputs.

## F.1 Verifier per-seed sensitivity

**Table F.1. Backbone-ablation macro-F1 by learning rate and seed**

| Backbone | Learning rate | Seed | Macro-F1 |
|---|---|---|---|
| banglabert | 2e-05 | 42 | 0.9866 |
| banglabert | 2e-05 | 43 | 0.9448 |
| banglabert | 2e-05 | 44 | 0.9347 |
| banglabert | 2e-05 | 45 | 0.9448 |
| banglabert | 2e-05 | 46 | 0.9737 |
| banglabert | 3e-05 | 42 | 0.9729 |
| banglabert | 3e-05 | 43 | 0.9590 |
| banglabert | 3e-05 | 44 | 0.9733 |
| banglabert | 3e-05 | 45 | 0.9316 |
| banglabert | 3e-05 | 46 | 0.9866 |
| xlmr | 2e-05 | 42 | 0.9590 |
| xlmr | 2e-05 | 43 | 0.9172 |
| xlmr | 2e-05 | 44 | 0.8809 |
| xlmr | 2e-05 | 45 | 0.7288 |
| xlmr | 2e-05 | 46 | 0.9729 |
| xlmr | 3e-05 | 42 | 0.9733 |
| xlmr | 3e-05 | 43 | 0.9303 |
| xlmr | 3e-05 | 44 | 0.9303 |
| xlmr | 3e-05 | 45 | 0.9303 |
| xlmr | 3e-05 | 46 | 0.9155 |
| muril | 2e-05 | 42 | 0.8849 |
| muril | 2e-05 | 43 | 0.9608 |
| muril | 2e-05 | 44 | 0.9866 |
| muril | 2e-05 | 45 | 0.9303 |
| muril | 2e-05 | 46 | 0.9448 |
| muril | 3e-05 | 42 | 0.9590 |
| muril | 3e-05 | 43 | 0.9590 |
| muril | 3e-05 | 44 | 0.9733 |
| muril | 3e-05 | 45 | 0.8746 |
| muril | 3e-05 | 46 | 0.9448 |
| mbert | 2e-05 | 42 | 0.9474 |
| mbert | 2e-05 | 43 | 0.9316 |
| mbert | 2e-05 | 44 | 0.9590 |
| mbert | 2e-05 | 45 | 0.9316 |
| mbert | 2e-05 | 46 | 0.9316 |
| mbert | 3e-05 | 42 | 0.9458 |
| mbert | 3e-05 | 43 | 0.9004 |
| mbert | 3e-05 | 44 | 0.9303 |
| mbert | 3e-05 | 45 | 0.8849 |
| mbert | 3e-05 | 46 | 0.9866 |
| indicbertv2 | 2e-05 | 42 | 0.9590 |
| indicbertv2 | 2e-05 | 43 | 0.9729 |
| indicbertv2 | 2e-05 | 44 | 0.9303 |
| indicbertv2 | 2e-05 | 45 | 0.9448 |
| indicbertv2 | 2e-05 | 46 | 0.9729 |
| indicbertv2 | 3e-05 | 42 | 0.9590 |
| indicbertv2 | 3e-05 | 43 | 0.9590 |
| indicbertv2 | 3e-05 | 44 | 0.9729 |
| indicbertv2 | 3e-05 | 45 | 0.9303 |
| indicbertv2 | 3e-05 | 46 | 0.9590 |
| bert_nli | 2e-05 | 42 | 0.9590 |
| bert_nli | 2e-05 | 43 | 0.9172 |
| bert_nli | 2e-05 | 44 | 0.9172 |
| bert_nli | 2e-05 | 45 | 0.9172 |
| bert_nli | 2e-05 | 46 | 0.9024 |
| bert_nli | 3e-05 | 42 | 0.9328 |
| bert_nli | 3e-05 | 43 | 0.9458 |
| bert_nli | 3e-05 | 44 | 0.9448 |
| bert_nli | 3e-05 | 45 | 0.9172 |
| bert_nli | 3e-05 | 46 | 0.9086 |
| setfit_labse | 2e-05 | 42 | 0.9590 |
| setfit_labse | 2e-05 | 43 | 0.9590 |
| setfit_labse | 2e-05 | 44 | 0.9590 |
| setfit_labse | 2e-05 | 45 | 0.9590 |
| setfit_labse | 2e-05 | 46 | 0.9590 |
| setfit_labse | 3e-05 | 42 | 0.9590 |
| setfit_labse | 3e-05 | 43 | 0.9590 |
| setfit_labse | 3e-05 | 44 | 0.9590 |
| setfit_labse | 3e-05 | 45 | 0.9590 |
| setfit_labse | 3e-05 | 46 | 0.9590 |

Source: `results/s3_backbone_per_seed.csv`.

**Table F.2. Verifier-B macro-F1 and error count by seed**

| Verifier-B seed | Learning rate | Macro-F1 | Errors |
|---|---|---|---|
| 42 | 2e-05 | 0.9597 | 3 |
| 43 | 2e-05 | 0.9729 | 2 |
| 44 | 2e-05 | 0.9733 | 2 |
| 45 | 2e-05 | 0.9448 | 4 |
| 46 | 2e-05 | 0.9866 | 1 |

Source: `results/s3d_verifier_b_per_seed.csv`. The persisted artifact is
seed 42 by the preregistered global-seed rule, not the best seed.

## F.2 Phase-5 per-replicate descriptive outcomes

**Table F.3. Verifier-B outcomes by condition, requested level, and replicate block**

| Condition | Level | Replicate seed | n | Mean Verifier-B target probability | Binary success rate |
|---|---|---|---|---|---|
| blind_resampling | 0 | 42 | 90 | 0.630338 | 0.6222 |
| blind_resampling | 0 | 43 | 90 | 0.668863 | 0.6778 |
| blind_resampling | 0 | 44 | 90 | 0.646404 | 0.6333 |
| blind_resampling | 1 | 42 | 90 | 0.892829 | 0.9333 |
| blind_resampling | 1 | 43 | 90 | 0.885303 | 0.9333 |
| blind_resampling | 1 | 44 | 90 | 0.920434 | 0.9556 |
| external_role_self_critique | 0 | 42 | 90 | 0.570000 | 0.5667 |
| external_role_self_critique | 0 | 43 | 90 | 0.632074 | 0.6333 |
| external_role_self_critique | 0 | 44 | 90 | 0.630765 | 0.6333 |
| external_role_self_critique | 1 | 42 | 90 | 0.881658 | 0.9222 |
| external_role_self_critique | 1 | 43 | 90 | 0.892978 | 0.9444 |
| external_role_self_critique | 1 | 44 | 90 | 0.867089 | 0.9000 |
| gemma4_26b_a4b_judge_loop | 0 | 42 | 90 | 0.579815 | 0.5778 |
| gemma4_26b_a4b_judge_loop | 0 | 43 | 90 | 0.603868 | 0.6000 |
| gemma4_26b_a4b_judge_loop | 0 | 44 | 90 | 0.702062 | 0.7111 |
| gemma4_26b_a4b_judge_loop | 1 | 42 | 90 | 0.837600 | 0.8778 |
| gemma4_26b_a4b_judge_loop | 1 | 43 | 90 | 0.814747 | 0.8556 |
| gemma4_26b_a4b_judge_loop | 1 | 44 | 90 | 0.882754 | 0.9111 |
| intrinsic_self_critique | 0 | 42 | 90 | 0.678181 | 0.6778 |
| intrinsic_self_critique | 0 | 43 | 90 | 0.694725 | 0.7000 |
| intrinsic_self_critique | 0 | 44 | 90 | 0.664542 | 0.6667 |
| intrinsic_self_critique | 1 | 42 | 90 | 0.852250 | 0.8778 |
| intrinsic_self_critique | 1 | 43 | 90 | 0.891510 | 0.9444 |
| intrinsic_self_critique | 1 | 44 | 90 | 0.899060 | 0.9444 |
| rag_neural_loop | 0 | 42 | 90 | 0.653337 | 0.6444 |
| rag_neural_loop | 0 | 43 | 90 | 0.714338 | 0.7222 |
| rag_neural_loop | 0 | 44 | 90 | 0.699465 | 0.7000 |
| rag_neural_loop | 1 | 42 | 90 | 0.904518 | 0.9556 |
| rag_neural_loop | 1 | 43 | 90 | 0.891473 | 0.9556 |
| rag_neural_loop | 1 | 44 | 90 | 0.941338 | 0.9778 |
| rag_neural_symbolic_feedback | 0 | 42 | 90 | 0.702784 | 0.7000 |
| rag_neural_symbolic_feedback | 0 | 43 | 90 | 0.757679 | 0.7667 |
| rag_neural_symbolic_feedback | 0 | 44 | 90 | 0.736510 | 0.7333 |
| rag_neural_symbolic_feedback | 1 | 42 | 90 | 0.917034 | 0.9667 |
| rag_neural_symbolic_feedback | 1 | 43 | 90 | 0.893635 | 0.9444 |
| rag_neural_symbolic_feedback | 1 | 44 | 90 | 0.926378 | 0.9667 |
| rag_only | 0 | 42 | 90 | 0.517410 | 0.5000 |
| rag_only | 0 | 43 | 90 | 0.516725 | 0.5111 |
| rag_only | 0 | 44 | 90 | 0.559998 | 0.5444 |
| rag_only | 1 | 42 | 90 | 0.836554 | 0.8778 |
| rag_only | 1 | 43 | 90 | 0.804175 | 0.8444 |
| rag_only | 1 | 44 | 90 | 0.866703 | 0.8889 |
| rag_symbolic_loop | 0 | 42 | 90 | 0.517489 | 0.5000 |
| rag_symbolic_loop | 0 | 43 | 90 | 0.516649 | 0.5111 |
| rag_symbolic_loop | 0 | 44 | 90 | 0.559998 | 0.5444 |
| rag_symbolic_loop | 1 | 42 | 90 | 0.830554 | 0.8667 |
| rag_symbolic_loop | 1 | 43 | 90 | 0.765877 | 0.8000 |
| rag_symbolic_loop | 1 | 44 | 90 | 0.856325 | 0.8889 |
| static_few_shot | 0 | 42 | 90 | 0.610919 | 0.6111 |
| static_few_shot | 0 | 43 | 90 | 0.647524 | 0.6444 |
| static_few_shot | 0 | 44 | 90 | 0.574309 | 0.5556 |
| static_few_shot | 1 | 42 | 90 | 0.779449 | 0.8000 |
| static_few_shot | 1 | 43 | 90 | 0.826034 | 0.8667 |
| static_few_shot | 1 | 44 | 90 | 0.824602 | 0.8556 |
| zero_shot | 0 | 42 | 90 | 0.427593 | 0.4111 |
| zero_shot | 0 | 43 | 90 | 0.338297 | 0.3111 |
| zero_shot | 0 | 44 | 90 | 0.287888 | 0.2667 |
| zero_shot | 1 | 42 | 90 | 0.774456 | 0.7889 |
| zero_shot | 1 | 43 | 90 | 0.771330 | 0.8000 |
| zero_shot | 1 | 44 | 90 | 0.792540 | 0.8333 |

Source: deterministic grouping of `results/s5_main_bn_scored_cases.csv`;
each row is 90 held-out plots. These replicate rows are descriptive
sensitivity blocks and are not treated as three independent studies.

## F.3 Same-case Goodhart transitions

**Table F.4. Selection-aware adjacent-attempt transitions among continuing cases**

| Condition | Transition | Paired cases | Δ Verifier-A | Δ Verifier-B | Δ(A−B) | Standing |
|---|---|---|---|---|---|---|
| rag_neural_loop | 1→2 | 147 | 0.483451 | 0.300649 | 0.182802 | same cases only; positive gap delta indicates widening A−B gap |
| rag_neural_loop | 2→3 | 67 | 0.367439 | 0.252603 | 0.114836 | same cases only; positive gap delta indicates widening A−B gap |
| rag_neural_symbolic_feedback | 1→2 | 147 | 0.538132 | 0.396651 | 0.141481 | same cases only; positive gap delta indicates widening A−B gap |
| rag_neural_symbolic_feedback | 2→3 | 58 | 0.396509 | 0.250530 | 0.145979 | same cases only; positive gap delta indicates widening A−B gap |
| rag_symbolic_loop | 1→2 | 193 | -0.059357 | -0.017133 | -0.042224 | same cases only; positive gap delta indicates widening A−B gap |
| rag_symbolic_loop | 2→3 | 165 | 0.019885 | 0.018489 | 0.001396 | same cases only; positive gap delta indicates widening A−B gap |

Source: `results/s5_main_bn_goodhart_paired_transitions.csv`. These are
selection-aware adjacent transitions among continuing failed cases, not
population effects over all 540 cases in a condition.

## F.4 Diversity and short-output diagnostics

**Table F.5. Short-output and lexical-diversity diagnostics by condition and requested level**

| Condition | Level | n | Under 4 words | Rate | Distinct-1 | Distinct-2 | Self-BLEU-4 |
|---|---|---|---|---|---|---|---|
| blind_resampling | 0 | 270 | 0 | 0.0000 | 0.2218 | 0.5155 | 0.4546 |
| blind_resampling | 1 | 270 | 0 | 0.0000 | 0.2930 | 0.6045 | 0.4077 |
| external_role_self_critique | 0 | 270 | 115 | 0.4259 | 0.2768 | 0.6127 | 0.1511 |
| external_role_self_critique | 1 | 270 | 2 | 0.0074 | 0.3326 | 0.7282 | 0.1370 |
| gemma4_26b_a4b_judge_loop | 0 | 270 | 0 | 0.0000 | 0.2198 | 0.5035 | 0.4542 |
| gemma4_26b_a4b_judge_loop | 1 | 270 | 0 | 0.0000 | 0.2861 | 0.6001 | 0.4029 |
| intrinsic_self_critique | 0 | 270 | 84 | 0.3111 | 0.2704 | 0.5968 | 0.2083 |
| intrinsic_self_critique | 1 | 270 | 1 | 0.0037 | 0.3321 | 0.7264 | 0.1620 |
| rag_neural_loop | 0 | 270 | 2 | 0.0074 | 0.2354 | 0.5448 | 0.3748 |
| rag_neural_loop | 1 | 270 | 0 | 0.0000 | 0.3108 | 0.6410 | 0.3349 |
| rag_neural_symbolic_feedback | 0 | 270 | 4 | 0.0148 | 0.2336 | 0.5425 | 0.3867 |
| rag_neural_symbolic_feedback | 1 | 270 | 0 | 0.0000 | 0.2979 | 0.6407 | 0.3427 |
| rag_only | 0 | 270 | 0 | 0.0000 | 0.2311 | 0.5219 | 0.4555 |
| rag_only | 1 | 270 | 0 | 0.0000 | 0.2850 | 0.5977 | 0.4073 |
| rag_symbolic_loop | 0 | 270 | 0 | 0.0000 | 0.2318 | 0.5230 | 0.4500 |
| rag_symbolic_loop | 1 | 270 | 0 | 0.0000 | 0.2918 | 0.6400 | 0.3091 |
| static_few_shot | 0 | 270 | 0 | 0.0000 | 0.2366 | 0.5426 | 0.3977 |
| static_few_shot | 1 | 270 | 0 | 0.0000 | 0.2894 | 0.6324 | 0.3022 |
| zero_shot | 0 | 270 | 0 | 0.0000 | 0.2105 | 0.4996 | 0.4771 |
| zero_shot | 1 | 270 | 0 | 0.0000 | 0.2734 | 0.6140 | 0.3639 |

Source: `results/s5_main_bn_diversity.csv`.

## F.5 Length-distribution and LaBSE-feature MAUVE sensitivity

**Table F.6. Length-distribution divergence and LaBSE-feature MAUVE sensitivity**

| Condition | Level | Generated n | Real length-reference n | Length JS | MAUVE generated/real n | LaBSE-feature MAUVE |
|---|---|---|---|---|---|---|
| blind_resampling | 0 | 270 | 1143 | 0.236376 | 270/270 | 0.035995 |
| blind_resampling | 1 | 270 | 754 | 0.552552 | 270/270 | 0.015138 |
| external_role_self_critique | 0 | 270 | 1143 | 0.368736 | 270/270 | 0.024529 |
| external_role_self_critique | 1 | 270 | 754 | 0.359107 | 270/270 | 0.020354 |
| gemma4_26b_a4b_judge_loop | 0 | 270 | 1143 | 0.237477 | 270/270 | 0.017435 |
| gemma4_26b_a4b_judge_loop | 1 | 270 | 754 | 0.582997 | 270/270 | 0.013434 |
| intrinsic_self_critique | 0 | 270 | 1143 | 0.298927 | 270/270 | 0.029529 |
| intrinsic_self_critique | 1 | 270 | 754 | 0.376801 | 270/270 | 0.022116 |
| rag_neural_loop | 0 | 270 | 1143 | 0.169423 | 270/270 | 0.025234 |
| rag_neural_loop | 1 | 270 | 754 | 0.499222 | 270/270 | 0.016449 |
| rag_neural_symbolic_feedback | 0 | 270 | 1143 | 0.153390 | 270/270 | 0.021785 |
| rag_neural_symbolic_feedback | 1 | 270 | 754 | 0.541754 | 270/270 | 0.014256 |
| rag_only | 0 | 270 | 1143 | 0.225011 | 270/270 | 0.013202 |
| rag_only | 1 | 270 | 754 | 0.560520 | 270/270 | 0.011841 |
| rag_symbolic_loop | 0 | 270 | 1143 | 0.218508 | 270/270 | 0.019630 |
| rag_symbolic_loop | 1 | 270 | 754 | 0.547908 | 270/270 | 0.018270 |
| static_few_shot | 0 | 270 | 1143 | 0.247843 | 270/270 | 0.021710 |
| static_few_shot | 1 | 270 | 754 | 0.576778 | 270/270 | 0.014991 |
| zero_shot | 0 | 270 | 1143 | 0.228054 | 270/270 | 0.010463 |
| zero_shot | 1 | 270 | 754 | 0.611987 | 270/270 | 0.020130 |

Sources: `results/s5_main_bn_length_js.csv` and
`results/s5_main_bn_labse_mauve.csv`. MAUVE uses LaBSE features with
270 generated and 270 real texts per cell; it is a small-sample
sensitivity analysis and is not comparable to default GPT-2-feature MAUVE.
No sentiment-JS value is supplied because no independent registered
generated-text sentiment scorer exists.
