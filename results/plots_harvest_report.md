# Plot harvest — bn.wikipedia

- **Config:** `configs/plots_scrape.yaml` · **Generated (UTC):** 2026-07-30T16:28:22.367920+00:00
- **Commit:** `1c971d3c5b1e4314768103adc03707d0a743d53a` · **API calls:** 554

## Yield

| | |
|---|---|
| candidate articles discovered | 2820 |
| passed the quality gate | **110** |
| rejected | 2710 |

### Why articles were rejected

| Reason | Count |
|---|---|
| no plot section | 2690 |
| under 3 sentences | 15 |
| under 120 chars | 5 |

Most bn.wikipedia film articles are stubs, so a large "no plot section" count is
expected rather than a fault. It matters only if the survivors fall below 130.

### Headings on articles that yielded nothing

Tallied so a shortfall is diagnosed from the corpus rather than by guessing at
the heading list again. If a plot-like heading appears high here, add its stem
to `plot_heading_stems` and re-run with `--reset`.

| Heading | Articles |
|---|---|
| তথ্যসূত্র | 221 |
| বহিঃসংযোগ | 182 |
| সঙ্গীত | 58 |
| অভিনয়শিল্পী | 35 |
| পুরস্কার | 34 |
| অভিনয়ে | 32 |
| মুক্তি | 31 |
| শ্রেষ্ঠাংশে | 24 |
| চলচ্চিত্রের তালিকা | 24 |
| কর্মজীবন | 20 |
| আরও দেখুন | 19 |
| চলচ্চিত্র | 18 |
| কুশীলব | 16 |
| অভিনয় | 16 |
| নির্মাণ | 14 |
| অভিনয়শিল্পীদল | 12 |
| সংগীত | 9 |
| টেলিভিশন | 9 |
| ব্যক্তিগত জীবন | 9 |
| প্রারম্ভিক জীবন | 9 |
| গানের তালিকা | 8 |
| কাহিনী সংক্ষেপ | 8 |
| প্রযোজনা | 7 |
| চলচ্চিত্রসমূহ | 7 |
| চিত্রগ্রহণ | 6 |

### By seed category

| Category | Plots |
|---|---|
| বিষয়শ্রেণী:বাংলা ভাষার চলচ্চিত্র | 53 |
| বিষয়শ্রেণী:বাংলাদেশী চলচ্চিত্র | 35 |
| বিষয়শ্রেণী:পশ্চিমবঙ্গের চলচ্চিত্র | 22 |

## Licence — an obligation, not a note

Text is **CC BY-SA 4.0** from bn.wikipedia: reusable **with attribution and
share-alike**. Every row carries `revision_id` and `revision_timestamp`, so the
exact revision used is citable and a reviewer can fetch it. **The dataset card
must carry the attribution before anything is published.**

## Sentence-length distribution

| Statistic | Sentences |
|---|---|
| min | 3 |
| median | 8 |
| max | 12 |

## What still needs a human

The gate is mechanical: it counts characters and sentences. It cannot tell a
plot summary from a production-history paragraph that happened to sit under a
matching heading. **Read the sampled 130 before using them.** Anything that is
not a plot gets deleted, and the sample is redrawn — not patched by hand.
