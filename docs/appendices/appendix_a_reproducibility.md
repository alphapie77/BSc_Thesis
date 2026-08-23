# Appendix A — Reproducibility and execution contract

## A.1 Repository-wide invariants

- Global seed: 42 through `src/common/seed.py`.
- Frozen review split: Gold-300=300, R1=2,162, R2=2,163.
- Gold-300 is evaluation-only; RAG uses R1 only; Verifier-B never enters
  generation.
- Main generation replicates: 42, 43 and 44 as paired sensitivity blocks.
- Every canonical result is config-addressed and carries runtime provenance.
- The frozen 5,400-generation surface is not regenerated for reporting.

## A.2 Data and artifact lineage

| Stage | Input | Canonical output/evidence |
|---|---|---|
| Raw audit | immutable 5,000-row workbook | `results/s0_data_xray.md` |
| Cleaning | raw workbook | `data/cleaned/bn_clean.csv`; `s1_cleaning_log.json` |
| Split freeze | 4,625 near-duplicate-controlled rows | `data/splits/split_map_v1.json` |
| Axis study | Region-A/R1 geometry and human instruments | S2 reports; G-300 and intrusion reports |
| Verifier-A | 804 R1 rows | frozen LaBSE + L2 logistic artifact; S3c report |
| Verifier-B | 888 R2 rows | fine-tuned BanglaBERT artifact; S3d report |
| RAG index | 886 Region-A R1 rows | R1-only index manifest, 534/352 by level |
| Main generation | 90 eval plots × 2 levels × 10 conditions × 3 seeds | 5,400-case sealed archive |
| Outcome scoring | sealed cases + Verifier-B | 5,400 score rows and score manifest |
| Post-run analysis | sealed cases/scores | master, paired, Goodhart, length and realism artifacts |
| Human evaluation | frozen 100-item balanced subset | 300 judgments and registered report |

## A.3 Runtime environments

| Work | Environment evidence | Principal hardware/standing |
|---|---|---|
| Local preprocessing and document scoring | `results/env_snapshot.json` | Windows local environment |
| S2 clustering | `results/env_snapshot_s2_kaggle.json` | Kaggle Tesla T4; host-native scientific stack |
| S3 verifier training | `results/env_snapshot_s3_kaggle.json` | Kaggle Tesla T4 |
| S4 development generation/scoring | `env_snapshot_s4*` files | Kaggle Tesla T4; producing snapshot selected per result |
| S5 final generation | `results/env_snapshot_s5_bn_kaggle.json` | Kaggle Tesla T4; transformers 5.15.0, scikit-learn 1.9.0 |
| S5 human scoring | provenance inside human report | Windows local environment |

Environment snapshots must be cited by the result they produced; the local
lock file is not retroactively treated as the Kaggle environment.

## A.4 Main generation configuration

- Writer: `google/gemma-3-12b-it`, NF4.
- Sampling: `max_new_tokens=80`, temperature 0.8, top-p 0.9.
- Uniform output instruction: at most 20 words at either requested level.
- Verifier-A threshold: 0.4384071; maximum three Writer attempts.
- Symbolic threshold: 0.18166513482099075; maximum three attempts.
- Hosted judge: `gemma-4-26b-a4b-it`, structured PASS/FAIL, seed 42,
  high thinking, maximum 512 output tokens and maximum three judgments.
- Blind resampling: maximum five candidates; Verifier-A selects the best prefix
  inside the realized neural-plus-symbolic token budget.

## A.5 Statistical contract

- Primary outcome: Verifier-B target probability.
- Primary family: nine paired condition-versus-zero-shot comparisons.
- Pairing key: plot × target level × replicate seed.
- Uncertainty: 10,000-resample paired bootstrap, 95% interval.
- Multiplicity: Benjamini–Hochberg across the frozen family.
- Binary paired check: McNemar test.
- No post-hoc active-condition inferential comparison is added.

## A.6 Remaining reporting item

Exact consolidated GPU wall-clock hours were not registered as a canonical
result and are not reconstructed from memory. Hardware, call counts, runtime
snapshots and producing commits are reported; any later compute-hours total must
be derived from archived timestamps with an explicit script before publication.
