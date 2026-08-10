# S3.5 -- symbolic scorer (PILOT: F1/IDF enabled)

> ⛔ **PILOT, NOT A RESULT.** This run enables **F1 (IDF)**, which inviolable rule 7 permits *only* as an explicitly-labelled cheap proxy in a pilot, **never in a result**. Nothing in this file may be quoted in the thesis, a paper, or a results table. It exists to measure what rule 7 costs, so the cost is known rather than assumed.

Fitted on **82** dev rows, **14** features (**5.86** rows per feature). F1/IDF enabled: **True**.

| Estimate | macro-F1 |
|---|---|
| Resubstitution (**OPTIMISTIC -- fitted and scored on the same 82 rows**) | 0.7909 |
| Stratified 5-fold CV (**the honest number**) | 0.6949 +/- 0.0532 |
| Majority baseline | 0.3926 |

## Leave-one-family-out (CV)

| Family | CV without it | Delta | Registered gameable? |
|---|---|---|---|
| F1_idf | 0.5150 | +0.1798 | no |
| F6_richness | 0.6736 | +0.0213 | no |
| F3_ortho | 0.6856 | +0.0093 | **yes** |
| F2_length | 0.6916 | +0.0033 | **yes** |
| F4_connective | 0.7140 | -0.0191 | **yes** |
| F5_sentiment | 0.7299 | -0.0350 | **yes** |

> A contribution concentrated in the **gameable** families is pre-registered as a **negative result about the hybrid design**: it is exactly the part a generator could fake once the Reflector names the failing rule (section 4.2). See `docs/protocol.md`, S3.5 pre-commitment.
