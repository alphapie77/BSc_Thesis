# Thesis research-question evidence map

**Frozen working title:** *A Neuro-Symbolic Multi-Agent Framework for
Pre-Release Audience Response Generation in Bangla Cinema: A
Verifier-in-the-Loop Approach*

**Audit date:** 2026-08-23
**Purpose:** bind every research question to existing audited evidence, its
defensible conclusion, and its planned thesis presentation. This document does
not introduce a new analysis or authorize a generation rerun.

## Terminology and source conflict

The normative pipeline's original RQ1 asks whether *personas* can be discovered.
That wording was superseded by the later registered evidence and terminology
decision recorded in `docs/STATUS.md`: silhouette 0.053, a monotonically rising
gap statistic and 100% HDBSCAN noise do not support discrete clusters or
audience types. The thesis therefore studies a reproducible two-level cut
through an engagement-specificity continuum. `cluster_k2` remains only a frozen
variable name. This map uses the current Chapter 1 wording and preserves the
negative clusterability result rather than silently rewriting it as discovery.

## Summary map

| RQ | Current question | Evidential status | Defensible one-sentence answer | Main chapter |
|---|---|---|---|---|
| RQ1 | Can a meaningful response distinction be recovered from unlabeled Bangla reviews and validated as stable and human-recognizable? | **Qualified support** | A reproducible Region-A cut is human-recognizable as engagement specificity under length-matched comparative judgment, but it is a continuum cut rather than a discovered persona/cluster and does not replicate structurally in Region B. | 3 |
| RQ2 | Does an external trained verifier improve target-level controllability over zero-shot, few-shot, RAG-only and self-critique baselines? | **Supported within the completed Bangla arm, with attribution limits** | Verifier-guided conditions improve held-out Verifier-B target scores over zero-shot and requested levels are human-recoverable, but several non-verifier controls also improve and the study does not establish audience prediction. | 6–7 |
| RQ3 | Does adding symbolic validation improve on neural-only and symbolic-only mechanisms? | **Mixed / incremental value unresolved** | Symbolic-only gating is weak; neural gating with symbolic feedback performs strongly, but no registered neural-plus-symbolic versus neural-only inferential contrast exists, so hybrid superiority cannot be claimed. | 5–7 |
| RQ4 | Does iteration against Verifier-A create measurable divergence from an independent Verifier-B? | **Supported as a diagnostic, not human-quality decline** | On continuing failed cases, neural-loop revisions widen the A–B score gap in the direction expected under proxy overoptimization; Verifier-B is an independent held-out proxy, not ground truth. | 6–7 |

## RQ1 — construct recovery and human recognizability

### Load-bearing evidence

- Full-corpus confound: `results/s2_cluster_assignments.csv` and
  `results/s2c_region_split.md`; the apparent clusters predominantly recover
  corpus source, including 93.3% binary source-identification accuracy.
- Region-A stability and clusterability: `results/s2d_ktable_regionA.md`;
  K=2 prediction strength 0.860 and bootstrap ARI 0.940 ± 0.029 coexist with
  silhouette 0.053, no gap-selected K and 100% HDBSCAN noise.
- Construct profiling and confound checks:
  `results/s2e_regionA_k2_profile.md` and
  `results/s2f_regionA_k2_residual.md`; length AUC 0.6764 and weak residual lift
  +9.80 percentage points are descriptive profiling, not post-clustering
  inferential proof.
- Negative control: `results/s2d_ktable_regionB.md`,
  `results/s2e_regionB_k2_profile.md` and
  `results/s2f_regionB_k2_residual.md`; the Region-A signature does not
  replicate even though a stable-looking Region-B bisection is recoverable.
- Failed ordinal instrument: `results/g300_agreement.md`; ordinal alpha 0.4970,
  so its downstream validity gate was not run.
- Successful comparative human validation: `results/intrusion_agreement.md`;
  annotator performance 0.780 and 0.840 against 0.25 chance, construct check
  0.850 for both annotators, items length-matched within two words, and the
  length heuristic scores 0.16.

### Claim boundary

The evidence supports a human-recognizable engagement-specificity distinction.
It does **not** support discovered personas, natural audience types, separated
clusters, or film-level audience prediction. Stability is reported as a
property of the algorithmic cut, not proof of natural categories.

### Thesis presentation

- Table 3.1: data audit and source-confound results.
- Figure 3.1: frozen G/R1/R2 data lineage and isolation walls.
- Figure 3.2: multi-panel clusterability, stability and confound diagnostics.
- Table 3.2: Region-A/Region-B axis evidence and negative control.
- Table 3.3: ordinal-instrument failure and comparative-validation success.

## RQ2 — external verification and controllability

### Load-bearing evidence

- Frozen 20-cell results: `results/s5_main_bn_master_table.csv` and
  `results/s5_main_bn_reporting_tables_v2.md`.
- Nine planned paired comparisons against zero-shot:
  `results/s5_main_bn_paired_statistics.csv`; every registered active condition
  has a positive target-probability delta whose interval excludes zero.
- Largest registered zero-shot delta: neural gate with symbolic feedback,
  +0.2570 with 95% CI [0.2151, 0.2987]. This is a comparison with zero-shot,
  not with the neural-only loop.
- Independent outcome score: Verifier-B is trained on R2 and never enters the
  generation loop; its calibration improvement was not established.
- Blinded human validation: `results/s5_human_eval_bn_report.json`; pooled
  target-match accuracy 0.9133, 95% item-bootstrap CI [0.8667, 0.9567], raw
  agreement 0.88 and nominal alpha 0.8405. The frozen 100-item subset validates
  requested-level recoverability, not a ranking of all 20 cells.

### Claim boundary

RQ2 is supported for Bangla axis-level controllability. Because few-shot, RAG,
self-critique, hosted judging and blind resampling also improve over zero-shot,
the result does not show that only the proposed loop works. Verifier scores
measure reproduction of the constructed label; human judgments establish
recoverability of the requested level, not audience prediction, general quality
or plot faithfulness over all 5,400 outputs.

### Thesis presentation

- Figure 4.1: dual-verifier training and isolation wall.
- Figure 5.1: bounded four-role workflow and retry routing.
- Table 5.1: exact ten-condition intervention matrix.
- Table 6.1: 20 condition-by-level outcome cells.
- Table 6.2: nine planned paired comparisons against zero-shot.
- Table 6.3: blinded human-validation summary, kept separate from system ranking.

## RQ3 — neural and symbolic validation

### Load-bearing evidence

- Development weight study: `results/s35_symbolic.md` and the registered S4.5a
  result. Neural-only was selected in every held-out fold; mixture-minus-neural
  mean AUC delta was 0.0000, while verdicts still changed across the weight
  curve. The pre-registered interpretation remains unresolved rather than being
  forced into a favorable category.
- Main experiment: `results/s5_main_bn_master_table.csv`. Symbolic-only gating
  is weak and costly, especially at Level 1; neural-plus-symbolic feedback has
  the largest registered effect against zero-shot.
- Inferential limitation: the frozen family contains no direct
  neural-plus-symbolic versus neural-only contrast.

### Claim boundary

Symbolic diagnostics are defensible as feedback that names observable failure
modes. They are not established as an independently predictive gate, and the
incremental causal benefit of symbolic feedback beyond the neural loop remains
unresolved. No post-hoc superiority test is added.

### Thesis presentation

- Table 5.2 or Appendix: weight-sensitivity outcomes and unresolved verdict.
- Table 6.1: descriptive neural-only, symbolic-only and combined cells.
- Chapter 7: explicit distinction between strong combined performance and
  unproven incremental symbolic benefit.

## RQ4 — verifier divergence and Goodhart diagnostic

### Load-bearing evidence

- `results/s5_main_bn_goodhart_paired_transitions.csv` and
  `results/s5_main_bn_goodhart_report.json`.
- Neural loop: A–B gap change +0.182802 from attempts 1→2 (n=147) and
  +0.114836 from 2→3 (n=67).
- Neural plus symbolic feedback: +0.141481 (n=147) and +0.145979 (n=58).
- Symbolic loop: −0.042224 (n=193) and +0.001396 (n=165).
- `results/s5_main_bn_goodhart_figure.png` keeps failure-selected attempt means
  separate from valid same-case adjacent transitions.

### Claim boundary

The widening A–B gap is consistent with proxy overoptimization. It is not proof
that human quality declined, does not make Verifier-B an oracle, and applies to
the continuing failed-case transitions rather than all 540 cases in each
condition. Verifier-B's calibration improvement was not established and is
reported beside the diagnostic.

### Thesis presentation

- Figure 6.1: audited Goodhart diagnostic figure.
- Table 6.4 or Appendix: exact adjacent-transition values and sample sizes.
- Chapter 7: proxy-divergence interpretation and residual validity threats.

## Cross-question safeguards

1. Gold-300 remains evaluation-only.
2. RAG uses R1 only; R2 never enters retrieval.
3. Verifier-B never enters generation, threshold selection or retry routing.
4. Seeds 42/43/44 are paired blocking/sensitivity factors, not independent
   study replications.
5. Length-matched S5 results are sensitivity evidence with coverage reported;
   they cannot rank conditions or establish length-neutral control.
6. No result in this map authorizes rerunning the frozen 5,400 generations.

## Integration checklist

- [x] Replace the obsolete persona wording in the normative pipeline through an
  explicit dated amendment; historical protocol remains unchanged.
- [x] Render the summary map as Chapter 1 Table 1.1.
- [x] Render the final bounded answers as Chapter 7 Table 7.2.
- [x] Use the artifact list above to build figure/table manifests.
