# S3.2b — the baselines S3.2 should have had

**Verdict: `CIRCULARITY_CONFIRMED`**

- dev n = **82**, so one item = **0.0122** macro-F1.
  Every gap below is also given in items, because at this n a difference
  of 0.03 is three reviews and should be read that way.

| Reference point | macro-F1 |
|---|---|
| majority class | 0.3926 |
| length rule (fitted on TRAIN) | 0.6197 |
| **frozen LaBSE + logistic regression** | **0.9866** |
| best fine-tuned arm (`banglabert`) | 0.9647 |

**Best arm − frozen probe = -0.0219 (-1.8 dev items).**

## ⛔ The ablation measured the label's construction

A frozen linear probe on the encoder that GENERATED the label matches
the best fine-tuned arm to within one dev item. Every arm in S3.2 was
recovering a boundary that already existed in LaBSE space.

**Consequences, per protocol.md §S3.2b:**
- The seven-arm table may support **no claim about backbones**. It is
  reported as a demonstration that the label is linearly recoverable.
- The `TIE` verdict stands but is re-explained: the arms are
  indistinguishable because the task is near-saturated by construction,
  not because backbones are interchangeable in general.
- **Verifier-A should be reconsidered**: if a logistic regression on
  frozen embeddings matches a fine-tuned BanglaBERT, the fine-tuning is
  not earning its cost inside the Phase 4 loop.
