# S2e — What is the K = 2 partition made of? (region A)

> **Interpretation was pre-registered in `docs/protocol.md` (RQ1-D) before this
> script existed.** Read that section first.
>
> ### The honest label on this analysis
>
> **Exploratory in origin, pre-registered in interpretation.** The decision to
> profile came *after* seeing G1's table, so this is not a confirmatory test and
> is not reported as one. What was fixed before the numbers were known is what
> each outcome would be taken to **mean** — because with a stable K already in
> hand, any difference found between the halves will look like a persona unless
> somebody wrote down in advance what would *not* count as one.

- **Config:** `configs/s2e_profile_regionB.yaml` · **n:** 2728 (region A, post-dedup) · **K:** 2
- **Generated (UTC):** 2026-08-08T14:32:18.472581+00:00 · **Commit:** `833d57b40365d65cf6dfa67cfbd46a6bfa7454d1`
- **Seed:** 42 · Cluster sizes: **1348** / **1380**
  (49.4% / 50.6%)
- **Guard passed:** this run reproduced G1's own silhouette (0.039358) and
  ARI vs Sentiment (0.010704) to within 1e-06, so
  these are the labels G1 selected — not merely *a* K=2 solution.
- **Nothing is trained.** AUC and Cliff's delta are rank statistics; the
  log-odds prior is fixed, not estimated. Rules 7 and 10 intact.

## Why this step exists at all

G1 established two things and left a third unanswered.

**Established:** the cut is reproducible (prediction strength 0.860, bootstrap
ARI 0.940 ± 0.029), and it is **not** the sentiment split (ARI 0.0107,
Band 1).

**Also established, and easy to overlook:** there are no separated groups here
to find. Silhouette 0.0394, a gap statistic that rises monotonically and is
satisfied at no K, and HDBSCAN classifying **100%** of points as noise. The
recorded reading is *a highly reproducible bisection of a space with no
separated groups*.

**Unanswered:** a reproducible bisection of a continuum is exactly what K-Means
produces when it cuts along the single dominant direction of variation. **What
is that direction?** This step asks — before 300 human annotations are spent
finding out the expensive way.

## Verdict

**NOT_LENGTH** — `length_auc` = 0.5498 <
0.65.

The cut is not primarily about how much people wrote. Under RQ1-D this
**removes the cheapest alternative explanation and does nothing more**. It is
not evidence that the halves are personas; G-300 remains the arbiter, exactly as
in RQ1 Band 1.

## The decisive table: can a surface feature do the encoder's job?

AUC is reported **directionless** — `max(auc, 1-auc)` — because which half
K-Means labels 0 is an artefact of initialisation, not a property of the data.
0.5 means the feature cannot tell the halves apart at all; 1.0 means it
separates them perfectly. Cliff's delta is the same information on a 0-centred
scale, included because AUC's floor of 0.5 is routinely misread.

| feature         |   auc_directionless |   cliffs_delta |   mean_cluster0 |   mean_cluster1 |   median_cluster0 |   median_cluster1 |
|:----------------|--------------------:|---------------:|----------------:|----------------:|------------------:|------------------:|
| mean_word_len   |              0.5806 |         0.1613 |          5.6940 |          5.4211 |            5.5714 |            5.3333 |
| punct_per_token |              0.5554 |         0.1108 |          0.2138 |          0.1973 |            0.2000 |            0.2000 |
| n_words         |              0.5498 |         0.0996 |          8.8494 |          9.0290 |            8.0000 |            8.0000 |
| n_chars         |              0.5237 |         0.0475 |         56.9280 |         55.8087 |           49.0000 |           51.0000 |
| n_danda         |              0.5116 |         0.0231 |          1.1632 |          1.1072 |            1.0000 |            1.0000 |
| has_danda       |              0.5054 |         0.0108 |          0.9970 |          0.9862 |            1.0000 |            1.0000 |
| first_person    |              0.5050 |         0.0101 |          0.0030 |          0.0130 |            0.0000 |            0.0000 |
| n_comma         |              0.5015 |         0.0030 |          0.5445 |          0.5123 |            0.0000 |            0.0000 |
| has_latin       |              0.5011 |         0.0022 |          0.0000 |          0.0022 |            0.0000 |            0.0000 |
| n_exclaim       |              0.5008 |         0.0015 |          0.0037 |          0.0022 |            0.0000 |            0.0000 |
| n_question      |              0.5004 |         0.0007 |          0.0000 |          0.0007 |            0.0000 |            0.0000 |
| has_digit       |              0.5004 |         0.0007 |          0.0007 |          0.0014 |            0.0000 |            0.0000 |
| has_comma_run   |              0.5000 |         0.0000 |          0.0000 |          0.0000 |            0.0000 |            0.0000 |

**Read the top row first.** If it is a length or punctuation feature with a high
AUC, the encoder found something a ruler could have found.

## Binary rates, with 95% Wilson intervals

Wilson rather than the normal approximation: these rates can sit at or near 0%
and 100%, where the textbook interval collapses to zero width and overstates
certainty.

| feature       |   cluster |    n |   rate_% |   ci95_lo_% |   ci95_hi_% |
|:--------------|----------:|-----:|---------:|------------:|------------:|
| has_danda     |         0 | 1348 |    99.70 |       99.24 |       99.88 |
| has_danda     |         1 | 1380 |    98.62 |       97.86 |       99.12 |
| first_person  |         0 | 1348 |     0.30 |        0.12 |        0.76 |
| first_person  |         1 | 1380 |     1.30 |        0.83 |        2.05 |
| has_comma_run |         0 | 1348 |     0.00 |       -0.00 |        0.28 |
| has_comma_run |         1 | 1380 |     0.00 |        0.00 |        0.28 |
| has_latin     |         0 | 1348 |     0.00 |       -0.00 |        0.28 |
| has_latin     |         1 | 1380 |     0.22 |        0.07 |        0.64 |
| has_digit     |         0 | 1348 |     0.07 |        0.01 |        0.42 |
| has_digit     |         1 | 1380 |     0.14 |        0.04 |        0.53 |

## Lexical richness at an equal token budget

Unique word types in a fixed sample of 4,000
tokens, bootstrapped 30×. Equal budget is the
whole point: the larger half would trivially show more distinct words otherwise,
and the comparison would mean nothing.

|   cluster |   n_reviews |   total_tokens |   types_at_budget |      sd |
|----------:|------------:|---------------:|------------------:|--------:|
|    0.0000 |   1348.0000 |     11929.0000 |         1186.3333 | 16.5576 |
|    1.0000 |   1380.0000 |     12460.0000 |         1181.2667 | 16.5910 |

## Sentiment composition of each half

Counts:

|   cluster_k2 |   0 |   1 |   2 |
|-------------:|----:|----:|----:|
|            0 | 336 | 304 | 708 |
|            1 | 204 | 312 | 864 |

Row percentages:

|   cluster_k2 |    0 |    1 |    2 |
|-------------:|-----:|-----:|-----:|
|            0 | 24.9 | 22.6 | 52.5 |
|            1 | 14.8 | 22.6 | 62.6 |

ARI against Sentiment is 0.0107, so this is **not** a relabelling of the
sentiment classes — but the composition is reported in full anyway, because
"not identical to sentiment" and "independent of sentiment" are different
claims and only the first is established.

## Distinctive vocabulary — a reading aid, not evidence

Log-odds ratio with an informative Dirichlet prior (Monroe, Colaresi & Quinn
2008), z-scored, over whitespace tokens. **No stemming, no stopword removal, no
TF-IDF** — Monroe's prior shrinks each word toward its corpus-wide rate in
proportion to how rare it is, which is precisely why stopword removal is
unnecessary and why this method was chosen over the alternatives. Inviolable
rule 7 intact.

**Under RQ1-D, no claim in the thesis may rest on these lists.** They are here
so a human can look at the two halves and form a judgement; ranked terms are not
a test.

### Terms characteristic of cluster 0

| word      |   count_c0 |   count_c1 |   log_odds_delta |      z |
|:----------|-----------:|-----------:|-----------------:|-------:|
| গল্পের      |        311 |         62 |            1.583 | 11.968 |
| গল্পে       |         95 |         15 |            1.778 |  6.805 |
| চরিত্রগুলোর |         87 |         11 |            1.971 |  6.641 |
| অভিনয়     |         65 |         13 |            1.564 |  5.411 |
| সংলাপগুলো  |         52 |          5 |            2.200 |  5.171 |
| চরিত্রের    |         58 |         11 |            1.611 |  5.164 |
| সংলাপ     |         77 |         26 |            1.081 |  4.922 |
| চরিত্রগুলো  |         51 |          9 |            1.676 |  4.901 |
| নয়।       |         70 |         23 |            1.106 |  4.757 |
| যে        |         86 |         34 |            0.932 |  4.738 |
| এবং       |        210 |        134 |            0.480 |  4.434 |
| দর্শকের    |         37 |          7 |            1.612 |  4.122 |
| নয়,       |         32 |          6 |            1.620 |  3.839 |
| সঙ্গে       |         56 |         22 |            0.937 |  3.834 |
| অভিনয়     |         28 |          2 |            2.437 |  3.772 |
| গল্পটা     |         45 |         16 |            1.030 |  3.653 |
| আছে,      |         46 |         17 |            0.994 |  3.610 |
| নাটকীয়    |         25 |          2 |            2.347 |  3.576 |
| এত        |         57 |         26 |            0.795 |  3.451 |
| কেমিস্ট্রি    |         23 |          3 |            1.940 |  3.400 |
| চরিত্রদের  |         22 |          3 |            1.901 |  3.314 |
| দর্শক      |         29 |          8 |            1.267 |  3.295 |
| সাথে      |         42 |         17 |            0.908 |  3.250 |
| সুন্দরভাবে  |         40 |         16 |            0.919 |  3.198 |
| আবেগ      |         58 |         29 |            0.708 |  3.192 |
| চরিত্র     |         39 |         16 |            0.895 |  3.101 |
| সমস্যা      |         21 |          5 |            1.402 |  2.941 |
| অপ্রয়োজনীয় |         17 |          2 |            2.028 |  2.939 |
| ছোট       |         31 |         12 |            0.950 |  2.876 |
| স্বাভাবিক,  |         17 |          3 |            1.673 |  2.826 |

### Terms characteristic of cluster 1

| word     |   count_c0 |   count_c1 |   log_odds_delta |       z |
|:---------|-----------:|-----------:|-----------------:|--------:|
| সিনেমার  |         76 |        772 |           -2.148 | -19.629 |
| সিনেমা   |         10 |        192 |           -2.602 |  -9.450 |
| সিনেমায়  |          3 |         79 |           -2.811 |  -5.913 |
| দেখে     |         15 |         68 |           -1.391 |  -5.106 |
| মুভির     |          2 |         54 |           -2.825 |  -4.876 |
| পুরো      |         35 |         94 |           -0.905 |  -4.713 |
| একটা     |         14 |         55 |           -1.259 |  -4.380 |
| এই       |          2 |         36 |           -2.544 |  -4.089 |
| আবহ      |          3 |         35 |           -2.209 |  -4.083 |
| একটি     |          9 |         41 |           -1.394 |  -3.965 |
| পর       |          4 |         32 |           -1.893 |  -3.852 |
| সিনেমাটি |          1 |         34 |           -2.967 |  -3.796 |
| সিনেমাটা |          1 |         32 |           -2.930 |  -3.701 |
| টোন      |          5 |         30 |           -1.641 |  -3.604 |
| ছবির     |          1 |         29 |           -2.869 |  -3.551 |
| না।      |        153 |        229 |           -0.351 |  -3.431 |
| ক্যামেরার  |          3 |         22 |           -1.817 |  -3.168 |
| কাজ      |         13 |         37 |           -0.957 |  -3.064 |
| সিনেমা।  |          4 |         22 |           -1.563 |  -3.037 |
| মুভিটা    |          0 |         30 |           -3.868 |  -3.003 |
| বাংলা     |          2 |         19 |           -2.038 |  -2.996 |
| এমন      |          9 |         29 |           -1.073 |  -2.912 |
| সেট      |         10 |         30 |           -1.006 |  -2.848 |
| শেষে     |          5 |         21 |           -1.318 |  -2.766 |
| হয়নি।    |         19 |         43 |           -0.741 |  -2.763 |
| সময়      |         10 |         29 |           -0.975 |  -2.744 |
| ছবি      |          1 |         16 |           -2.454 |  -2.740 |
| —        |          6 |         22 |           -1.193 |  -2.692 |
| হলো      |          1 |         15 |           -2.405 |  -2.659 |
| সিনেমায়  |          0 |         23 |           -3.868 |  -2.629 |

## The reviews themselves — this is the part to read

Everything above is scaffolding for this section. Read the two blocks and ask
one question: **do these read like two kinds of viewer, or like two lengths of
the same viewer?**

#### Cluster 0 — the 12 reviews closest to its centre

| id | Sentiment | words | review |
|---|---|---|---|
| `bn_2129` | 2 | 7 | কাহিনীর গঠন বেশ সোজাসাপ্টা ছিল, চমক কম। |
| `bn_2006` | 2 | 8 | অভিনয় ভালো ছিল, কিন্তু গল্পে টান ছিল না। |
| `bn_2367` | 2 | 7 | গল্পের কাঠামো ঠিক ছিল, কিন্তু চমকপ্রদ না। |
| `bn_2478` | 2 | 9 | গল্পের ধারা ছিল স্বাভাবিক, বড় কোনো চমক ছিল না। |
| `bn_4753` | 2 | 5 | গল্প বাস্তবধর্মী, পুরোপুরি বাস্তব নয়। |
| `bn_4811` | 2 | 6 | গল্প কিছুটা বাস্তবধর্মী, পুরোপুরি বাস্তব নয়। |
| `bn_4499` | 2 | 23 | সিনেমার গল্প বেশ সরল, কোনো বড় চমক নেই। অভিনয় ঠিক আছে, ভিজ্যুয়াল ভালো লাগলেও খুব বেশি প্রভাব ফেলেনি। মিউজিক সাধারণ, গল্পের সঙ্গে মানানসই। |
| `bn_2586` | 2 | 10 | সিনেমার চরিত্রগুলো বাস্তবধর্মী, তবে কোনো চরিত্র খুব বিশেষ হয়ে ওঠেনি। |
| `bn_4931` | 2 | 11 | গল্প কিছুটা বাস্তবধর্মী, পুরোপুরি বাস্তব নয়, দর্শক সহজে অনুধাবন করতে পারে। |
| `bn_2666` | 2 | 9 | ছবিটার গল্প খুব সাধারণ ছিল, তবে ঠিকঠাকভাবে বলা হয়েছে। |
| `bn_2028` | 2 | 7 | সিনেমাটির চিত্রনাট্য খুবই সাধারণ, কিন্তু চরিত্রগুলো বাস্তবধর্মী। |
| `bn_4439` | 2 | 7 | গল্পের থিম পরিষ্কার, তবে বেশি আকর্ষণ নেই। |

#### Cluster 1 — the 12 reviews closest to its centre

| id | Sentiment | words | review |
|---|---|---|---|
| `bn_2093` | 2 | 8 | সিনেমার গল্পটা মোটামুটি ছিল, বিশেষ কিছু মনে হয়নি। |
| `bn_2180` | 2 | 8 | সিনেমার আবহ ভালো ছিল, গল্প তেমন মন কাড়েনি। |
| `bn_2232` | 2 | 10 | সিনেমার গল্পটা ঠিকঠাক ছিল, কিন্তু খুব বিশেষ কিছু মনে হয়নি। |
| `bn_2946` | 2 | 10 | সিনেমার আবহ পুরোটাই একরকম ছিল, কোনো দৃশ্য বিশেষভাবে আলাদা লাগেনি। |
| `bn_2390` | 2 | 9 | সিনেমার সিনেমাটোগ্রাফি ঠিকঠাক ছিল, বিশেষ কিছু চোখে পড়ে না। |
| `bn_2685` | 2 | 7 | সিনেমার ট্রানজিশন ঠিকঠাক ছিল, খুব মসৃণ না। |
| `bn_2272` | 2 | 7 | সিনেমার গ্রাফিক্স ঠিক ছিল, কিন্তু চমকপ্রদ না। |
| `bn_2300` | 2 | 8 | সিনেমার পরিবেশ ভালো ছিল, শব্দ মাঝেমাঝে স্পষ্ট না। |
| `bn_2404` | 2 | 8 | সিনেমার কোনো দৃশ্য অসহ্য লাগেনি, সবকিছু সহনীয় ছিল। |
| `bn_2869` | 2 | 8 | সিনেমায় দৃশ্যান্তর ভালো ছিল, কিছুটা মন্থর মনে হয়েছে। |
| `bn_2335` | 2 | 10 | সিনেমার গল্প খুব সরল ছিল, বড় কোনো বাঁক ছিল না। |
| `bn_2234` | 2 | 9 | মুভির লোকেশনগুলো সুন্দর ছিল, তবে খুব বেশি আকর্ষণীয় না। |

## How sharp is the boundary?

Margin = distance to the other centroid minus distance to one's own. Near zero
means the review could have gone either way; the assignment is a coin flip that
the seed happened to settle. Median margin **0.0583**,
and **12.2%** of reviews sit within 0.02 of
the boundary.

| id | cluster | margin | words | review |
|---|---|---|---|---|
| `bn_4734` | 1 | 0.0005 | 14 | সিনেমার ভিজ্যুয়াল ও লোকেশন যথেষ্ট মানানসই, খুব দৃষ্টিনন্দন না হলেও গল্পের পরিবেশকে সমর্থন করে। |
| `bn_3617` | 1 | 0.0006 | 5 | সিনেমার চরিত্রগুলোর অভিনয় খুব প্রাকৃতিক। |
| `bn_3362` | 1 | 0.0006 | 15 | বাংলা সিনেমায় এমন সুন্দর স্ক্রিপ্ট সত্যিই বিরল। গল্পে নতুনত্ব ছিল এবং এটি বেশ আকর্ষণীয়ও লাগছে। |
| `bn_4186` | 1 | 0.0011 | 12 | সিনেমাটির আবহ এতটাই ফাঁপা যে চরিত্রগুলোর সঙ্গে কোনো সংযোগই তৈরি হয় না। |
| `bn_3742` | 0 | 0.0012 | 8 | সিনেমার সংলাপ প্রায়শই অপ্রাসঙ্গিক এবং দর্শককে বিভ্রান্ত করে। |
| `bn_4374` | 0 | 0.0012 | 28 | সিনেমার ফ্লো মাঝারি। কিছু অংশ ধীর মনে হয়েছে। চরিত্রগুলো ঠিক আছে, তবে গভীরতা সীমিত। মিউজিক মানানসই, ভিজ্যুয়াল ঠিকঠাক। সংলাপ সাধারণ, গল্পের বার্তা বোঝা সহজ। একবার দেখার মতো সিনেমা। |
| `bn_3200` | 1 | 0.0014 | 34 | ছবির প্রতিটি চরিত্রের আলাদা গুরুত্ব রয়েছে এবং সবগুলো মিলিয়ে পুরো সিনেমাটিকে ভারসাম্যপূর্ণ করেছে। সংলাপ, মিউজিক, আবহ এবং ভিজ্যুয়াল সবকিছু একসাথে মিলিত হয়ে দর্শককে এক অসাধারণ অভিজ্ঞতা দেয়। এটি নিখুঁত একটি পরিবারের জন্য উপযুক্ত সিনেমা। |
| `bn_4188` | 0 | 0.0016 | 11 | অনেক দৃশ্য এত লম্বা করা হয়েছে যে দেখার সময় ক্লান্ত লাগছে। |
| `bn_2349` | 1 | 0.0018 | 6 | ছবির সংলাপ সহজ এবং প্রাঞ্জল ছিল। |
| `bn_3563` | 1 | 0.0018 | 12 | সিনেমার থিম শিক্ষণীয়, কিন্তু এটি কখনও চাপে রাখে না; স্বাভাবিকভাবে অনুভূত হয়। |

If a large share of the corpus sits near the boundary, that is the silhouette of
0.0394 made concrete — the halves are two sides of one crowd, not two crowds.

## What this step does NOT settle — in either direction

1. **That the halves are personas.** No statistic here can establish that. Only
   G-300, with three annotators and κ/α, can.
2. **That the halves are *not* personas, because a surface feature separates
   them.** Real personas plausibly differ in length and punctuation. A
   `LENGTH_DOMINATED` verdict shows the persona claim is **unsupported**, not
   that it is false — a weaker statement, and the one the thesis must make.
3. **Anything at all from the vocabulary lists on their own.**

## What to do next

The verdict above selects the branch, and both branches were written before the
number was known. Whichever applies, the outstanding decision is Sabbir's, not a
statistic's: **STATUS open decision 12** — the title and framing say *three
personas* throughout the pipeline, the pre-defence report and the conference
draft, and that language now needs revisiting for two, and qualifying for what
"persona" is here allowed to mean.
