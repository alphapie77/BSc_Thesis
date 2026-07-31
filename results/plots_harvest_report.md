# Plot harvest — bn.wikipedia

- **Config:** `configs/plots_scrape.yaml` · **Generated (UTC):** 2026-07-31T13:28:06.993680+00:00
- **Commit:** `b061046574134b08b2345b495e8531755b441baa` · **API calls:** 807

## Yield

| | |
|---|---|
| candidate articles discovered | 2995 |
| passed the quality gate | **132** |
| rejected | 2863 |

### Why articles were rejected

| Reason | Count |
|---|---|
| no plot section | 2848 |
| under 3 sentences | 8 |
| under 120 chars | 6 |
| over 2000 chars | 1 |

Most bn.wikipedia film articles are stubs, so a large "no plot section" count is
expected rather than a fault. It matters only if the survivors fall below 130.

### Headings on articles that yielded nothing

Tallied so a shortfall is diagnosed from the corpus rather than by guessing at
the heading list again. If a plot-like heading appears high here, add its stem
to `plot_heading_stems` and re-run with `--reset`.

| Heading | Articles |
|---|---|
| তথ্যসূত্র | 227 |
| বহিঃসংযোগ | 198 |
| সঙ্গীত | 54 |
| পুরস্কার | 34 |
| অভিনয়শিল্পী | 33 |
| মুক্তি | 32 |
| শ্রেষ্ঠাংশে | 30 |
| অভিনয়ে | 28 |
| চলচ্চিত্রের তালিকা | 28 |
| কর্মজীবন | 23 |
| চলচ্চিত্র | 18 |
| কুশীলব | 17 |
| আরও দেখুন | 17 |
| নির্মাণ | 14 |
| অভিনয় | 14 |
| অভিনয়শিল্পীদল | 12 |
| কাহিনী | 11 |
| ব্যক্তিগত জীবন | 11 |
| টেলিভিশন | 10 |
| প্রারম্ভিক জীবন | 10 |
| গানের তালিকা | 9 |
| চলচ্চিত্র তালিকা | 8 |
| সংগীত | 7 |
| আরো দেখুন | 7 |
| কাহিনী সংক্ষেপ | 6 |

### By seed category

| Category | Plots |
|---|---|
| বিষয়শ্রেণী:বাংলা ভাষার চলচ্চিত্র | 88 |
| বিষয়শ্রেণী:বাংলাদেশী চলচ্চিত্র | 41 |
| বিষয়শ্রেণী:পশ্চিমবঙ্গের চলচ্চিত্র | 3 |

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
