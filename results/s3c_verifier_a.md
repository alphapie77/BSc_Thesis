# S3.3a — Verifier-A (the in-loop gate)

**frozen sentence-transformers/LaBSE + L2 logistic**, trained on **R1, n = 804** ({0: 481, 1: 323}), evaluated on **dev-82** ({0: 53, 1: 29}).

- dev macro-F1 **0.9866** — **1 error(s) on 82 items**.
- One dev item = **0.0122** macro-F1. Read every
  gap below in items, not in decimal places.
- Reproduces S3.2b's measured **0.9866** for the same
  model on the same rows, which is the point of running the check.
- Hyperparameters selected: **none -- C, penalty and max_iter are library defaults fixed in the config, per protocol.md S3.3 decision 1**.

## What this number is NOT

It is **label reproduction**, not persona detection. `cluster_k2` was
produced by k-means on LaBSE embeddings, so a linear probe on those same
embeddings is the label's own generating geometry asked to reproduce
itself (S3.2b, `CIRCULARITY_CONFIRMED`). The label is nonetheless real —
RQ1-H showed humans perceive the distinction at 0.78/0.84 against 0.25
chance — it is simply *linear in LaBSE space*.

⚠️ **The stated weakness, kept in the open:** a verifier that is a linear
function of LaBSE may be trivially gameable by a generator scored in that
same space. That is why Verifier-B is a different family on different data,
and it is the failure RQ5 exists to detect.

## S3.4 calibration — **descriptive**

Temperature **0.1092**, fitted on dev-82 (in-sample; no second slice exists at this n).

| | before | after |
|---|---|---|
| ECE (5 bins) | 0.1184 | 0.0054 |
| Brier | 0.0306 | 0.0093 |
| NLL | 0.1515 | 0.0282 |

ΔECE = **+0.1130**, bootstrap 95% CI **[+0.0743, +0.1349]** → **`CALIBRATION_IMPROVED`**.

🔴 **Context for this table (protocol.md, 2026-08-11).** Decision 16
originally defended Verifier-A as *natively calibrated*. That clause was
withdrawn: `zhang2026tabpfn` measure logistic heads on frozen encoders
across 22,820 episodes and find them **best on accuracy, near-worst on
ECE and NLL**. The choice of Verifier-A stands; that sentence does not.

