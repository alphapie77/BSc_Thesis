# S3.5 -- symbolic scorer

Fitted on **82** dev rows, **11** features (**7.45** rows per feature). F1/IDF enabled: **False**.

| Estimate | macro-F1 |
|---|---|
| Resubstitution (**OPTIMISTIC -- fitted and scored on the same 82 rows**) | 0.6570 |
| Stratified 5-fold CV (**the honest number**) | 0.5150 +/- 0.0713 |
| Majority baseline | 0.3926 |

## Leave-one-family-out (CV)

| Family | CV without it | Delta | Registered gameable? |
|---|---|---|---|
| F3_ortho | 0.4503 | +0.0647 | **yes** |
| F6_richness | 0.4764 | +0.0386 | no |
| F5_sentiment | 0.5338 | -0.0188 | **yes** |
| F4_connective | 0.5339 | -0.0189 | **yes** |
| F2_length | 0.6232 | -0.1082 | **yes** |

> A contribution concentrated in the **gameable** families is pre-registered as a **negative result about the hybrid design**: it is exactly the part a generator could fake once the Reflector names the failing rule (section 4.2). See `docs/protocol.md`, S3.5 pre-commitment.
