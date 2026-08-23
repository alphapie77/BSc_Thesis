# Appendix G — Configuration, environment, and bibliography provenance

## G.1 Configuration-to-result map

| Scientific component | Frozen configuration | Canonical evidence |
|---|---|---|
| Backbone sensitivity | `configs/s3_backbone.yaml` | `results/s3_backbone_ablation.*`, per-seed CSV |
| Verifier-A | `configs/s3c_verifier_a.yaml` | `results/s3c_verifier_a.*`, `artifacts/verifier_a.joblib` |
| Verifier-B | `configs/s3d_verifier_b.yaml` | `results/s3d_verifier_b.*`, `artifacts/verifier_b.joblib` |
| Symbolic scorer | `configs/s35_symbolic.yaml` | `results/s35_symbolic.*`, `artifacts/symbolic_scorer.joblib` |
| R1 retrieval index | `configs/s4_index.yaml` | `results/s4_index_manifest.*`, `data/rag/r1_index/` |
| Neural threshold | `configs/s4_tau.yaml` | `results/s4_tau_frontier.json`, maximum traces |
| Phase-5 generation | `configs/s5_main_bn.yaml` | sealed 5,400-case archive and generation manifest |
| Verifier-B scoring | `configs/s5_score_bn.yaml` | 5,400 B-score rows and score manifest |
| Main inference | `configs/s5_analysis_bn.yaml` | master table, paired statistics, analysis JSON |
| Goodhart analysis | `configs/s5_goodhart_bn.yaml` | attempt and paired-transition tables |
| Diversity/length | `configs/s5_diversity_realism_bn.yaml` | diversity, length-JS and preflight files |
| MAUVE sensitivity | `configs/s5_mauve_bn.yaml` | 20-cell LaBSE-feature table and report |
| Human evaluation | `configs/s5_human_eval_bn.yaml` | 300 responses, summaries and ingestion manifest |

Every table in the thesis is a rendered view of these evidence files. Result
files remain the authority where rounding differs.

## G.2 Principal frozen hyperparameters and checkpoints

| Component | Frozen checkpoint/settings |
|---|---|
| Embedding/retrieval | `sentence-transformers/LaBSE`; cosine; top 10; Region-A R1 only |
| Verifier-A | frozen LaBSE, normalized embeddings, L2 logistic regression, C=1.0, maximum 2,000 iterations, temperature 0.1092 |
| Verifier-B | `csebuetnlp/banglabert`; seed 42 artifact; learning rate 2×10⁻⁵, four epochs, batch 16, maximum length 128, temperature 1.0995 |
| Symbolic scorer | standardized logistic regression; 11 enabled non-IDF features; five-fold CV |
| Writer | `google/gemma-3-12b-it`; NF4; maximum 80 new tokens; temperature 0.8; top-p 0.9; batch 1 |
| Hosted judge | `gemma-4-26b-a4b-it`; seed 42; high thinking; structured output; maximum 512 output tokens |
| Neural loop | τ=0.4384071; maximum three Writer attempts |
| Symbolic loop | τ=0.18166513482099075; maximum three Writer attempts |
| Blind resampling | maximum five candidates; realized-generator-FLOP matching; Verifier-A prefix selection |
| Inference | 10,000 paired bootstrap resamples; 95% intervals; Benjamini–Hochberg family; McNemar binary check |

## G.3 Runtime-to-result map

| Runtime evidence | Work attributed to it |
|---|---|
| `results/env_snapshot.json` | Local preprocessing and document-side scoring |
| `results/env_snapshot_s2_kaggle.json` | S2 clustering and construct geometry |
| `results/env_snapshot_s3_kaggle.json` and S3 result provenance | Backbone/verifier development |
| `results/env_snapshot_s4dev_kaggle.json` | Initial S4 development surface |
| `results/env_snapshot_s4dev_lenctl_kaggle.json` | Length-controlled development surface |
| `results/env_snapshot_s4w_kaggle.json` | Symbolic-weight sensitivity scoring |
| `results/env_snapshot_s4tau_kaggle.json` | Neural threshold frontier |
| `results/env_snapshot_s5_bn_kaggle.json` | Final 5,400-case generation surface |
| Human report provenance | Human-response ingestion and analysis |

The final S5 snapshot records commit `22124a8`, Tesla T4, transformers 5.15.0
and scikit-learn 1.9.0. A smoke-test or predecessor snapshot is not substituted
for the producing runtime. Exact consolidated GPU hours remain unreported
unless derived from archived timestamps by a separate auditable script.

## G.4 Archive identity and isolation

The frozen generation surface has 5,400 unique registered keys: 90 plots × two
levels × ten conditions × three paired seeds. The separate score manifest
matches the source-generation hash and contains 5,400 Verifier-B scores.
Verifier-B is absent from generation; Gold-300 and R2 are absent from retrieval;
the RAG index contains R1 only. Superseded and diagnostic calls retain separate
paths and cannot silently resume into the active archive.

## G.5 Bibliography audit

The thesis-facing bibliography is `docs/references_ieee.bib`. It contains 143
unique entries; the 55 entries cited by Chapters 1–7 are ordered first by first
appearance and all active citation keys resolve. `docs/reference_key_map_full.csv`
retains the complete key/order audit. Bibliography order is presentation
metadata, not scientific evidence.
