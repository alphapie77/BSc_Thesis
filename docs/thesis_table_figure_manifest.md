# Thesis table and figure manifest

**Audit date:** 2026-08-23
**Scope:** Bangla cinema response generation. This manifest introduces no
analysis and authorizes no generation rerun.

## Selection rule

A table or figure stays in the main thesis only when it does at least one of
four jobs: defines the research claim, proves an isolation/reproducibility wall,
reports a load-bearing result, or makes a limitation visible beside that result.
Implementation traces, full hyperparameters, per-seed rows and secondary
diagnostics belong in the appendix. The local diagnostic interface is not a
Phase-5 result and receives no main-results figure.

## Main-text tables

| ID | Purpose | Source of truth | State | Required action |
|---|---|---|---|---|
| Table 1.1 | RQ, evidence status and bounded answer | `docs/thesis_rq_evidence_map.md` | Present in Chapter 1 | Four-row summary reports only the active thesis questions. |
| Table 2.1 | Position against adjacent work | Chapter 2 and cited primary records | Present in draft | Retain; final copy-edit only. |
| Table 3.1 | Corpus audit, cleaning, split and source-confound facts | `s0_data_xray.md`, `s1_cleaning_log.json`, split map, `s2c_region_split.md` | Present in Chapter 3 | Distinguishes raw, clean and deduplicated n and the source-confound finding. |
| Table 3.2 | Region-A evidence versus Region-B negative control | `s2d/s2e/s2f` A and B reports | Present in Chapter 3 | Shows stability, clusterability, length and replication diagnostics together. |
| Table 3.3 | Human-validation attempt 1 versus attempt 2 | `g300_agreement.md`, `intrusion_agreement.md` | Present in Chapter 3 | Failed ordinal instrument remains beside successful comparative instrument. |
| Table 4.1 | Backbone ablation and circularity baseline | `s3_backbone_ablation.*`, `s3b_baselines.*` | Present in Chapter 4 | Fine-tuned arms and cheap baselines are combined; no backbone-superiority claim. |
| Table 5.1 | Exact ten-condition intervention matrix | frozen Phase-5 config/runner and Chapter 5 | Present in Chapter 5 | Shows examples, gate/selector, feedback, logical-call ceiling and B-outside-loop wall. |
| Table 5.2 | Neural/symbolic weight study | `s4_w_sensitivity.*`, `s35_symbolic.*` | Present in Chapter 5 | Reports `w=1` folds and `PRECOMMITMENT_UNRESOLVED`; no hybrid-win language. |
| Table 6.1 | Complete 20-cell outcome and cost table | `s5_main_bn_master_table.csv` | Present in draft | Keep as the primary result table. |
| Table 6.2 | Nine registered paired comparisons against zero-shot | `s5_main_bn_paired_statistics.csv` | Present in draft | Includes delta, CI, p and BH q; no unregistered active-vs-active tests. |
| Table 6.3 | Blinded human-evaluation summary | `s5_human_eval_bn_report.json`, summary CSV | Present in draft | Shows pooled/per-rater accuracy, agreement, alpha and CI; not system ranking. |
| Table 6.4 | Length-matched sensitivity and coverage | `s5_main_bn_length_matched.*` | Present in draft | Coverage appears beside matched accuracy to expose post-treatment selection. |
| Table 7.1 | Validity-threat matrix | Chapter 7 and STATUS verified facts | Present in Chapter 7 | Covers construct/internal/external/statistical/measurement/human/ethics risks. |
| Table 7.2 | Final RQ verdicts | `docs/thesis_rq_evidence_map.md` | Present in Chapter 7 | Uses qualified/mixed language for the four active questions. |

## Main-text figures

| ID | Purpose | Source of truth | State | Required action |
|---|---|---|---|---|
| Figure 3.1 | Frozen data lineage and G/R1/R2 isolation | split map and pipeline contracts | Missing | Draw a schematic; show G eval-only and RAG=R1 only. |
| Figure 3.2 | Axis evidence and negative-control diagnostic | Region-A/B `s2d/s2e/s2f` artifacts | Missing | Multi-panel plot in original embedding/metric spaces; UMAP is optional and visualization-only. |
| Figure 4.1 | Dual-verifier training and isolation wall | Chapter 4, split map, verifier configs | Placed in Chapter 4 | Shows Gold exclusion, R1/R2 separation, shared-dev qualification and B's outcome-only privilege wall. |
| Figure 4.2 | Calibration before/after | `s3c_verifier_a*`, `s3d_verifier_b*` | Data present, figure missing | Show A improvement and B null together; label dev/in-sample descriptive standing. |
| Figure 5.1 | Bounded four-role workflow state graph | implemented loop and Chapter 5 | Placed in Chapter 5 | Shows Researcher → Writer → Critic → Reflector, weak-evidence query revision, retry routing, max-three bound and B outside graph. |
| Figure 5.2 | Threshold frontier and development dynamics | `s4_tau_frontier.json`, `s4_loop_dynamics.json`, `docs/figures/s4_loop_dynamics.svg` | Placed in Chapter 5 | Caption distinguishes selected τ from the forced-three endpoint and development from the frozen main run. |
| Figure 6.1 | Attempt dynamics and A-minus-B Goodhart diagnostic | `s5_main_bn_goodhart_figure.png` + manifest | Placed in Chapter 6 | Audited caption distinguishes failure-selected means from valid transitions. |
| Figure 6.2 | Separate realism diagnostics | `s5_main_bn_realism_figure.png` + manifest | Placed in Chapter 6 | Caption and prose preserve LaBSE-feature/small-sample warning and no composite score. |

## Appendix-only material

| Artifact | Why it is not in the main narrative |
|---|---|
| Complete configs, hyperparameters and environment-to-result mapping | Present in Appendices A and G. |
| Per-seed verifier and Phase-5 supplementary rows | Present in Appendix F; seeds are sensitivity/pairing blocks, not independent studies. |
| Exact symbolic rule catalogue and failure taxonomy | Present in Appendix E; the eight-case single-coder deviation remains visible. |
| Exact Goodhart adjacent-transition rows and sample sizes | Present in Appendix F; the main figure carries the interpretation. |
| Diversity, length-JS and LaBSE-MAUVE numeric tables | Present in Appendix F with the MAUVE standing retained. |
| Prompt templates and trace policy | Present in Appendix E; complete sealed traces remain the authority rather than a favourable hand-picked example. |
| Full bibliography audit map | Appendix G points to the 143-entry audit map; metadata provenance is not a thesis result. |
| Post-run local interface | Present in Appendix H and explicitly excluded from experimental evidence. |

## Explicit exclusions

- No audience-demographic, persona, cluster-type or box-office figure.
- No sentiment-JS panel: an independent registered generated-text sentiment
  scorer does not exist.
- No film-level realism plot: reviews cannot be mapped to films.
- No interface screenshot in the main experimental results. If retained, the
  diagnostic demo belongs in an implementation appendix and must be labelled
  as post-run software using a different live model path.
- No new composite score or post-hoc ranking of the ten conditions.

## Build order

1. ✅ Insert the two already-final Phase-5 PNGs and replace Chapter 6 placeholder
   wording.
2. ✅ Render Tables 6.2--6.4 directly from their audited result files.
3. ✅ Build and place Figures 4.1 and 5.1, because the verifier wall and
   multi-agent routing are central to the title and defence.
4. Build Chapter 3 evidence figures and Figure 4.2; all Chapter 3 tables are now present.
5. ✅ All 14 main-text tables are placed. Final pagination/formatting waits for
   the university thesis template.

Every numeric rendering must retain its source artifact and rounding rule in a
manifest. Existing 5,400 generations are frozen and must not be rerun.
