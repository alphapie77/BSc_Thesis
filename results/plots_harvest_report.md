# Plot harvest — bn.wikipedia

- **Config:** `configs/plots_scrape.yaml` · **Generated (UTC):** 2026-07-31T16:56:57.951181+00:00
- **Commit:** `ba05361fbfbe9528a351666ff4ed26929b955d79` · **API calls:** 924

## Yield

| | |
|---|---|
| candidate articles discovered | 3135 |
| passed the quality gate | **124** |
| rejected | 3011 |

### Why articles were rejected

| Reason | Count |
|---|---|
| no plot section | 2925 |
| person article, not a film | 65 |
| under 3 sentences | 15 |
| under 120 chars | 6 |

Most bn.wikipedia film articles are stubs, so a large "no plot section" count is
expected rather than a fault. It matters only if the survivors fall below 130.

### Headings on articles that yielded nothing

Tallied so a shortfall is diagnosed from the corpus rather than by guessing at
the heading list again. If a plot-like heading appears high here, add its stem
to `plot_heading_stems` and re-run with `--reset`.

| Heading | Articles |
|---|---|
| তথ্যসূত্র | 180 |
| বহিঃসংযোগ | 153 |
| সঙ্গীত | 49 |
| অভিনয়শিল্পী | 40 |
| মুক্তি | 38 |
| অভিনয়ে | 31 |
| শ্রেষ্ঠাংশে | 28 |
| পুরস্কার | 23 |
| কুশীলব | 21 |
| নির্মাণ | 16 |
| আরও দেখুন | 16 |
| কাহিনী | 13 |
| অভিনয় | 12 |
| সাউন্ডট্র্যাক | 10 |
| অভিনয়শিল্পীদল | 9 |
| সংগীত | 8 |
| কাহিনী সংক্ষেপ | 8 |
| গানের তালিকা | 7 |
| প্রযোজনা | 7 |
| সাউন্ডট্রাক | 7 |
| মুক্তিপ্রাপ্ত চলচ্চিত্র সমূহ | 6 |
| চলচ্চিত্র | 6 |
| কাহিনি সংক্ষেপ | 5 |
| পুরস্কার ও মনোনয়ন | 5 |
| কলাকুশলী | 5 |

### By seed category

| Category | Plots |
|---|---|
| বিষয়শ্রেণী:বাংলা ভাষার চলচ্চিত্র | 66 |
| বিষয়শ্রেণী:বাংলাদেশী চলচ্চিত্র | 57 |
| বিষয়শ্রেণী:পশ্চিমবঙ্গের চলচ্চিত্র | 1 |

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
