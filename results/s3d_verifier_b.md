# S3.3b — Verifier-B (S6 evaluation only; never in the loop)

**Verdict `COMPETENT_EVALUATOR`**

`csebuetnlp/banglabert`, the S3.2 **recipe** retrained on **R2, n = 888** ({0: 531, 1: 357}); evaluated on **dev-82** ({0: 53, 1: 29}).

- **dev macro-F1 0.9597** (the persisted seed-42 model).
- Across 5 seeds: **0.9674 ± 0.0158** — reported as a sensitivity band, not as a score distribution for model comparison (Bethard 2022).
- One dev item = **0.0122** macro-F1.
- Learning rate **2e-05**, hyperparameters selected: **none — one lr, taken from pipeline §3.1**.
- Artifact chosen by **global_seed, pre-declared; NOT best-of-five**.

## The wall, and what it is made of

| | Verifier-A | Verifier-B |
|---|---|---|
| Data | R1 (804) | **R2 (888)** — disjoint by the frozen split |
| Pretraining | LaBSE, multilingual | BanglaBERT, Bangla-native ELECTRA |
| Adaptation | frozen + linear head | fine-tuned end to end |
| Tokenizer | LaBSE | BanglaBERT |

The original design separated A and B **only by split**. After decision 16
the separation is methodological as well — which `mahmoud2026rubric` make
the standard, and which `wang2026hacking` justify by naming
evaluator–policy co-adaptation as a mechanism of reward hacking.

⚠️ S3.2's BanglaBERT arm scored 0.9647 — **on R1**. It is a different model on different data and is quoted here as
context only, never as a before/after pair with the number above.

🔴 **No claim that either verifier is better may be made from dev-82.** At
0.0122 per item the expected A−B difference is under two reviews, and
that limit was pre-committed before either was trained.

## S3.4 calibration — **descriptive**

Temperature **1.0995**, fitted on dev-82 (in-sample; no second slice exists at this n).

| | before | after |
|---|---|---|
| ECE (5 bins) | 0.0164 | 0.0100 |
| Brier | 0.0278 | 0.0273 |
| NLL | 0.1101 | 0.1088 |

ΔECE = **+0.0065**, bootstrap 95% CI **[-0.0066, +0.0070]** → **`CALIBRATION_NOT_ESTABLISHED`**.

**Pre-committed null statement fires:** *calibration could not be
established at this sample size.*

