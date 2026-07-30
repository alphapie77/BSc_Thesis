# Plot harvest — bn.wikipedia

- **Config:** `configs/plots_scrape.yaml` · **Generated (UTC):** 2026-07-30T15:59:34.159447+00:00
- **Commit:** `cc93be6ea9790b816ee13d1c3b9f1349fe2f1d3b` · **API calls:** 158

## Yield

| | |
|---|---|
| candidate articles discovered | 1225 |
| passed the quality gate | **67** |
| rejected | 1158 |

### Why articles were rejected

| Reason | Count |
|---|---|
| no plot section | 1148 |
| under 3 sentences | 5 |
| under 120 chars | 5 |

Most bn.wikipedia film articles are stubs, so a large "no plot section" count is
expected rather than a fault. It matters only if the survivors fall below 130.

### By seed category

| Category | Plots |
|---|---|
| বিষয়শ্রেণী:বাংলা ভাষার চলচ্চিত্র | 46 |
| বিষয়শ্রেণী:বাংলাদেশী চলচ্চিত্র | 21 |

## Licence — an obligation, not a note

Text is **CC BY-SA 4.0** from bn.wikipedia: reusable **with attribution and
share-alike**. Every row carries `revision_id` and `revision_timestamp`, so the
exact revision used is citable and a reviewer can fetch it. **The dataset card
must carry the attribution before anything is published.**

## Sentence-length distribution

| Statistic | Sentences |
|---|---|
| min | 3 |
| median | 9 |
| max | 12 |

## What still needs a human

The gate is mechanical: it counts characters and sentences. It cannot tell a
plot summary from a production-history paragraph that happened to sit under a
matching heading. **Read the sampled 130 before using them.** Anything that is
not a plot gets deleted, and the sample is redrawn — not patched by hand.
