# S2c — The corpus is two corpora, joined at row 1999

> ### ⚠️ EXPLORATORY — and it supersedes `s2b_register_probe.md`
>
> `s2b` asked whether **class 2** is a different kind of text and answered yes.
> That was true but **mis-framed**. Class 2 exists only in the second half of the
> raw file, so what looked like a property of the neutral *class* is a property
> of a *region of the file*. Rows 3665–4330 are labelled **0 (negative)** and
> carry the same uniform signature; rows 499–896, also labelled 0, do not.
>
> Read this file instead of s2b's conclusions. s2b's measurements stand; its
> interpretation does not.

- **Config:** `configs/s2c_region_split.yaml` · **Generated (UTC):** 2026-07-30T14:39:48.405969+00:00
- **Commit:** `9179537f91adc2314978898c3dddba7ae56da138`
- The raw `.xlsx` is opened **read-only** (inviolable rule 1).

## The finding

The source file is **not** one corpus. It is two, concatenated:

| region    |    n |   danda_% |   first_person_% |   exclaim_% |   comma_run_% |   median_words |   types_per_1k_tokens |
|:----------|-----:|----------:|-----------------:|------------:|--------------:|---------------:|----------------------:|
| A_organic | 1999 |      38.7 |             13.5 |         3.4 |           3.3 |            9.0 |                 255.0 |
| B_uniform | 3001 |      99.2 |              0.8 |         0.3 |           0.0 |            8.0 |                 127.6 |

Region **B_uniform** is **3,001 of 5,000 rows — 60% of the
corpus.** It carries a signature no organically collected comment thread
produces: **99.2%** of its rows are দাঁড়ি-terminated against
38.7% in region A_organic, **0.8%** contain a
first-person pronoun against 13.5%, and it draws
**128** word types per 1,000 tokens against
255.

## Label composition — the giveaway

| row_0     |   unlabelled |   0.0 |   1.0 |   2.0 |
|:----------|-------------:|------:|------:|------:|
| A_organic |            1 |   999 |   999 |     0 |
| B_uniform |            0 |   666 |   665 |  1670 |

**Region A_organic contains no class-2 rows at all.** Every one of the 1,670 neutral
reviews sits in region B_uniform. That is why `s2b` read the split as a property of
class 2: the neutral class is perfectly nested inside the second corpus.

## The seam is sharp, not gradual

Rolling 100-row mean of the দাঁড়ি rate across raw row order:

|    row |   danda_%_rolling |   label |
|-------:|------------------:|--------:|
| 1849.0 |              18.0 |     0.0 |
| 1874.0 |              23.0 |     0.0 |
| 1899.0 |              28.0 |     0.0 |
| 1924.0 |              26.0 |     0.0 |
| 1949.0 |              29.0 |     0.0 |
| 1974.0 |              43.0 |     0.0 |
| 1999.0 |              60.0 |     2.0 |
| 2024.0 |              81.0 |     2.0 |
| 2049.0 |             100.0 |     2.0 |
| 2074.0 |             100.0 |     2.0 |
| 2099.0 |             100.0 |     2.0 |
| 2124.0 |             100.0 |     2.0 |
| 2149.0 |             100.0 |     2.0 |

A gradual drift would suggest a changing population of commenters. A step
function over ~50 rows suggests two files pasted together.

## Per-run breakdown

Contiguous label runs of ≥ 50 rows. Note rows 3665–4330 and 3000–3664: **label 0
and label 1**, deep in region B_uniform, both carrying the region's signature rather
than their class's.

| rows      |   label |    n |   danda_% |   first_person_% |   exclaim_% |   comma_run_% |   median_words |   types_per_1k_tokens |
|:----------|--------:|-----:|----------:|-----------------:|------------:|--------------:|---------------:|----------------------:|
| 0-498     |       1 |  499 |      36.3 |             20.2 |         1.2 |           3.0 |           11.0 |                 298.4 |
| 499-896   |       0 |  398 |      32.4 |              9.0 |         3.0 |           1.0 |            7.0 |                 399.1 |
| 898-998   |       0 |  101 |      31.7 |             10.9 |         5.0 |           1.0 |            6.0 |                 609.5 |
| 999-1498  |       1 |  500 |      54.4 |             14.6 |         6.0 |           5.6 |           11.0 |                 358.5 |
| 1499-1998 |       0 |  500 |      32.0 |              9.6 |         2.8 |           3.4 |            7.0 |                 442.5 |
| 1999-2999 |       2 | 1001 |     100.0 |              0.0 |         0.0 |           0.0 |            8.0 |                 184.0 |
| 3000-3664 |       1 |  665 |      96.5 |              3.5 |         1.2 |           0.0 |            8.0 |                 240.2 |
| 3665-4330 |       0 |  666 |      99.8 |              0.0 |         0.0 |           0.0 |            7.0 |                 239.8 |
| 4331-4999 |       2 |  669 |     100.0 |              0.0 |         0.0 |           0.0 |            9.0 |                 144.3 |

## How the cleaned corpus inherits it

| region    |    0 |    1 |    2 |   All |
|:----------|-----:|-----:|-----:|------:|
| A_organic |  948 |  962 |    0 |  1910 |
| B_uniform |  565 |  637 | 1618 |  2820 |
| All       | 1513 | 1599 | 1618 |  4730 |

## What this does to S2

The S2 clustering put **1,814** items in cluster 0 — 823 class-0, 979 class-1,
and only **12** class-2. Region A_organic after cleaning holds **1,910** items — 948
class-0, 962 class-1, **0** class-2. Those two groups are close enough that the
obvious reading is that **cluster 0 is approximately region A_organic**: the encoder
recovered which file a review came from.

This cannot be confirmed here, because `s2_pilot.py` does not persist cluster
assignments — the decisive number, `ARI(cluster_labels, region)`, requires a
re-run that saves them. **Until that is computed, the correspondence is
suggestive, not established.**

## Consequences

1. **Every result computed over the full corpus is confounded by this split**,
   including the S2 trap-check itself.
2. The RQ1 persona claim cannot rest on three-class structure that is
   substantially a two-corpus structure.
3. Provenance fact (c) — "bulk pull from Facebook groups and YouTube channels" —
   cannot describe region B_uniform. The collector's recollection (2026-07-30: "same
   way") is **inconsistent with the file's own layout**. This is not evidence of
   bad faith: there is no written collection log (fact (a)), the recollection is
   old, and a second source merged in at assembly time is easy to forget.
   `docs/protocol.md` already pre-committed that a computed test **supersedes**
   the recall-based provenance table where the two disagree.
4. **Region A_organic is still a usable corpus**: 1,910
   cleaned rows, organic register, two classes. Smaller and binary, but real.
