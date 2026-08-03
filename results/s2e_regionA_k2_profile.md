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

- **Config:** `configs/s2e_profile.yaml` · **n:** 1897 (region A, post-dedup) · **K:** 2
- **Generated (UTC):** 2026-08-03T16:13:19.040756+00:00 · **Commit:** `730de20136ae8e572f8340701c405477258a64e9`
- **Seed:** 42 · Cluster sizes: **1143** / **754**
  (60.3% / 39.7%)
- **Guard passed:** this run reproduced G1's own silhouette (0.053404) and
  ARI vs Sentiment (0.152152) to within 1e-06, so
  these are the labels G1 selected — not merely *a* K=2 solution.
- **Nothing is trained.** AUC and Cliff's delta are rank statistics; the
  log-odds prior is fixed, not estimated. Rules 7 and 10 intact.

## Why this step exists at all

G1 established two things and left a third unanswered.

**Established:** the cut is reproducible (prediction strength 0.860, bootstrap
ARI 0.940 ± 0.029), and it is **not** the sentiment split (ARI 0.1522,
Band 1).

**Also established, and easy to overlook:** there are no separated groups here
to find. Silhouette 0.0534, a gap statistic that rises monotonically and is
satisfied at no K, and HDBSCAN classifying **100%** of points as noise. The
recorded reading is *a highly reproducible bisection of a space with no
separated groups*.

**Unanswered:** a reproducible bisection of a continuum is exactly what K-Means
produces when it cuts along the single dominant direction of variation. **What
is that direction?** This step asks — before 300 human annotations are spent
finding out the expensive way.

## Verdict

**LENGTH_CONFOUNDED** — `length_auc` =
0.6764, in [0.65,
0.75).

Length is a **major but not sole** component of the cut. Under RQ1-D, G-300 may
proceed on two conditions, neither optional: the annotation guideline is written
so that annotators cannot succeed by reading length alone, and **length is
reported next to every persona claim in the thesis** — main text, not a
footnote.

## The decisive table: can a surface feature do the encoder's job?

AUC is reported **directionless** — `max(auc, 1-auc)` — because which half
K-Means labels 0 is an artefact of initialisation, not a property of the data.
0.5 means the feature cannot tell the halves apart at all; 1.0 means it
separates them perfectly. Cliff's delta is the same information on a 0-centred
scale, included because AUC's floor of 0.5 is routinely misread.

| feature         |   auc_directionless |   cliffs_delta |   mean_cluster0 |   mean_cluster1 |   median_cluster0 |   median_cluster1 |
|:----------------|--------------------:|---------------:|----------------:|----------------:|------------------:|------------------:|
| n_chars         |              0.6810 |         0.3621 |         73.9440 |         49.2241 |           59.0000 |           37.0000 |
| n_words         |              0.6764 |         0.3529 |         13.1190 |          8.8528 |           11.0000 |            7.0000 |
| n_danda         |              0.5744 |         0.1487 |          0.8408 |          0.4960 |            0.0000 |            0.0000 |
| has_danda       |              0.5613 |         0.1226 |          0.4462 |          0.3236 |            0.0000 |            0.0000 |
| punct_per_token |              0.5563 |         0.1126 |          0.1177 |          0.0979 |            0.0833 |            0.0000 |
| mean_word_len   |              0.5453 |         0.0905 |          4.7484 |          4.6457 |            4.6364 |            4.5000 |
| first_person    |              0.5428 |         0.0857 |          0.1732 |          0.0875 |            0.0000 |            0.0000 |
| n_comma         |              0.5322 |         0.0643 |          0.4584 |          0.2573 |            0.0000 |            0.0000 |
| has_comma_run   |              0.5104 |         0.0208 |          0.0420 |          0.0212 |            0.0000 |            0.0000 |
| n_exclaim       |              0.5047 |         0.0094 |          0.0691 |          0.0438 |            0.0000 |            0.0000 |
| has_digit       |              0.5011 |         0.0022 |          0.0035 |          0.0013 |            0.0000 |            0.0000 |
| n_question      |              0.5010 |         0.0019 |          0.0201 |          0.0212 |            0.0000 |            0.0000 |
| has_latin       |              0.5004 |         0.0009 |          0.0009 |          0.0000 |            0.0000 |            0.0000 |

**Read the top row first.** If it is a length or punctuation feature with a high
AUC, the encoder found something a ruler could have found.

## Binary rates, with 95% Wilson intervals

Wilson rather than the normal approximation: these rates can sit at or near 0%
and 100%, where the textbook interval collapses to zero width and overstates
certainty.

| feature       |   cluster |    n |   rate_% |   ci95_lo_% |   ci95_hi_% |
|:--------------|----------:|-----:|---------:|------------:|------------:|
| has_danda     |         0 | 1143 |    44.62 |       41.76 |       47.51 |
| has_danda     |         1 |  754 |    32.36 |       29.12 |       35.78 |
| first_person  |         0 | 1143 |    17.32 |       15.24 |       19.63 |
| first_person  |         1 |  754 |     8.75 |        6.94 |       10.99 |
| has_comma_run |         0 | 1143 |     4.20 |        3.18 |        5.52 |
| has_comma_run |         1 |  754 |     2.12 |        1.31 |        3.42 |
| has_latin     |         0 | 1143 |     0.09 |        0.02 |        0.49 |
| has_latin     |         1 |  754 |     0.00 |        0.00 |        0.51 |
| has_digit     |         0 | 1143 |     0.35 |        0.14 |        0.90 |
| has_digit     |         1 |  754 |     0.13 |        0.02 |        0.75 |

## Lexical richness at an equal token budget

Unique word types in a fixed sample of 4,000
tokens, bootstrapped 30×. Equal budget is the
whole point: the larger half would trivially show more distinct words otherwise,
and the comparison would mean nothing.

|   cluster |   n_reviews |   total_tokens |   types_at_budget |      sd |
|----------:|------------:|---------------:|------------------:|--------:|
|    0.0000 |   1143.0000 |     14995.0000 |         1623.3667 | 21.3518 |
|    1.0000 |    754.0000 |      6675.0000 |         1913.2000 | 19.5165 |

## Sentiment composition of each half

Counts:

|   cluster_k2 |   0 |   1 |
|-------------:|----:|----:|
|            0 | 384 | 759 |
|            1 | 560 | 194 |

Row percentages:

|   cluster_k2 |    0 |    1 |
|-------------:|-----:|-----:|
|            0 | 33.6 | 66.4 |
|            1 | 74.3 | 25.7 |

ARI against Sentiment is 0.1522, so this is **not** a relabelling of the
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

| word    |   count_c0 |   count_c1 |   log_odds_delta |     z |
|:--------|-----------:|-----------:|-----------------:|------:|
| মুভি     |        337 |         10 |            2.203 | 9.113 |
| সিনেমা  |        217 |         17 |            1.537 | 6.933 |
| অনেক    |        219 |         27 |            1.168 | 6.239 |
| এই      |        272 |         48 |            0.859 | 5.839 |
| সুন্দর    |        209 |         32 |            0.981 | 5.549 |
| মুভিটা   |        105 |          4 |            2.040 | 5.055 |
| একটা    |        199 |         35 |            0.859 | 4.989 |
| ছবি     |        232 |         56 |            0.574 | 4.046 |
| ছবিটা   |         63 |          2 |            2.148 | 3.913 |
| একটি    |         63 |          4 |            1.688 | 3.814 |
| মুভির    |         59 |          1 |            2.465 | 3.734 |
| বাংলা    |         81 |         11 |            1.080 | 3.635 |
| ছবির    |         70 |          9 |            1.126 | 3.453 |
| দেখি    |         52 |          4 |            1.542 | 3.384 |
| সেরা    |         61 |          7 |            1.221 | 3.352 |
| অসাধারণ |        169 |         42 |            0.546 | 3.316 |
| খুব      |        148 |         36 |            0.565 | 3.187 |
| দেখা    |         64 |          9 |            1.049 | 3.180 |
| মুভি।    |         35 |          1 |            2.206 | 2.912 |
| ধন্যবাদ  |         41 |          4 |            1.354 | 2.871 |
| আমার    |        128 |         32 |            0.539 | 2.857 |
| সত্যি     |         47 |          6 |            1.131 | 2.834 |
| দেখেছি  |         33 |          1 |            2.173 | 2.829 |
| সিনেমার |         43 |          5 |            1.209 | 2.801 |
| ছবি।    |         31 |          1 |            2.136 | 2.743 |
| বাস্তব   |         30 |          2 |            1.650 | 2.616 |
| বার     |         46 |          7 |            0.980 | 2.593 |
| আজ      |         29 |          2 |            1.624 | 2.562 |
| ভাল     |         32 |          3 |            1.385 | 2.559 |
| এমন     |         65 |         14 |            0.673 | 2.406 |

### Terms characteristic of cluster 1

| word    |   count_c0 |   count_c1 |   log_odds_delta |      z |
|:--------|-----------:|-----------:|-----------------:|-------:|
| অভিনয়   |         71 |         87 |           -0.972 | -6.219 |
| না      |        144 |        120 |           -0.604 | -4.997 |
| কি      |         89 |         85 |           -0.732 | -4.940 |
| হাসতে   |          8 |         24 |           -1.813 | -4.608 |
| হাসি    |          4 |         19 |           -2.233 | -4.283 |
| নায়ক    |         16 |         24 |           -1.159 | -3.681 |
| জয়া     |          3 |         13 |           -2.150 | -3.527 |
| খান     |          5 |         13 |           -1.679 | -3.297 |
| কিছুই    |          9 |         16 |           -1.320 | -3.253 |
| পারলাম  |          7 |         14 |           -1.432 | -3.180 |
| এর      |         53 |         45 |           -0.617 | -3.112 |
| নাই     |         18 |         22 |           -0.964 | -3.103 |
| নায়িকা  |          4 |         11 |           -1.731 | -3.068 |
| বাজে    |         29 |         29 |           -0.772 | -3.008 |
| লাগে    |         30 |         29 |           -0.740 | -2.905 |
| কাজ     |          5 |         11 |           -1.521 | -2.905 |
| কাহিনী  |         17 |         20 |           -0.927 | -2.875 |
| করছে    |          3 |          9 |           -1.812 | -2.819 |
| অভিনেতা |          7 |         12 |           -1.285 | -2.773 |
| নাকি    |          7 |         12 |           -1.285 | -2.773 |
| লাগছে   |          7 |         12 |           -1.285 | -2.773 |
| নায়ক    |          1 |          8 |           -2.687 | -2.757 |
| ছাড়া    |          2 |          8 |           -2.076 | -2.751 |
| ফালতু    |         23 |         23 |           -0.772 | -2.677 |
| বাবা    |          4 |          9 |           -1.542 | -2.645 |
| বুঝলাম   |          4 |          9 |           -1.542 | -2.645 |
| আছে     |         28 |         26 |           -0.701 | -2.633 |
| নায়িকা  |          1 |          7 |           -2.573 | -2.595 |
| অভিনয়ের |          1 |          7 |           -2.573 | -2.595 |
| শাকিব   |          7 |         11 |           -1.202 | -2.549 |

## The reviews themselves — this is the part to read

Everything above is scaffolding for this section. Read the two blocks and ask
one question: **do these read like two kinds of viewer, or like two lengths of
the same viewer?**

#### Cluster 0 — the 12 reviews closest to its centre

| id | Sentiment | words | review |
|---|---|---|---|
| `bn_0496` | 1 | 11 | সত্যি অসাধারণ একটি মুভি,,। তবে এই সিনেমার গান গুলো খুব সুন্দর |
| `bn_0366` | 1 | 4 | অনেক সুন্দর একটা মুভি |
| `bn_1237` | 1 | 3 | মুভিটা খুবই ভালো |
| `bn_0357` | 1 | 11 | মুভিটা অনেক ভালো লাগলো অসাধারণ মুভি অনেক আগে দেখেছি আবার দেখলাম |
| `bn_1426` | 1 | 8 | ভীষণ সুন্দর একটা সিনেমা.. খুব খুব ভালো লাগলো.. |
| `bn_0352` | 1 | 10 | অসাধারণ একটি মুভি অনেক অনেক বেশি ভালো লাগলো মুভিটা দেখে |
| `bn_0248` | 1 | 9 | খুব সুন্দর একটা ছবি, মজা পাইলাম মুভি টা দেখে |
| `bn_1358` | 1 | 7 | অসাধারণ সুন্দর একটা মুভি,,, খুব ভালো লাগলো |
| `bn_1352` | 1 | 3 | সত্যি অসাধারণ মুভিটা |
| `bn_1168` | 1 | 4 | অপূর্ব সুন্দর লাগলো মুভিটা। |
| `bn_0151` | 1 | 4 | অপূর্ব সুন্দর একটি সিনেমা। |
| `bn_1055` | 1 | 4 | মুভি টা অসম্ভব সুন্দর |

#### Cluster 1 — the 12 reviews closest to its centre

| id | Sentiment | words | review |
|---|---|---|---|
| `bn_0800` | 0 | 16 | না আছে গল্প না আছে অভিনয় না আছে গান না আছে ভালো কোন দৃশ্যপট হায়রে সিনেমা |
| `bn_1852` | 0 | 5 | এ ছবির পরিচালক ভালো না |
| `bn_0855` | 0 | 5 | কাহিনী টা অনেক হাস্যকর ছিল |
| `bn_1831` | 0 | 4 | নায়িকাকে সুন্দর লাগে না |
| `bn_1808` | 0 | 4 | ছবির মানে বুজলাম না |
| `bn_1963` | 0 | 7 | ছবি দেখে কি বলব বুঝতে পারছি না |
| `bn_0972` | 0 | 7 | গল্পটা বুঝতে পারলাম না। কি থেকে কি |
| `bn_0741` | 0 | 5 | ছবির কোনো কাহিনীই নাই ফালতু |
| `bn_0504` | 0 | 5 | এসব ছবি আমার পছন্দ নয় |
| `bn_0729` | 0 | 7 | এরকম ন্যাকা নায়ক আমি কোথাও দেখি নাই |
| `bn_1652` | 0 | 3 | গল্পটা ভালো লাগেনি |
| `bn_1625` | 0 | 7 | আমি জাস্ট কথা বুঝতে পারলাম না নায়কের |

## How sharp is the boundary?

Margin = distance to the other centroid minus distance to one's own. Near zero
means the review could have gone either way; the assignment is a coin flip that
the seed happened to settle. Median margin **0.0644**,
and **15.2%** of reviews sit within 0.02 of
the boundary.

| id | cluster | margin | words | review |
|---|---|---|---|---|
| `bn_0135` | 1 | 0.0002 | 21 | কি নিখুঁত অভিনয় যেমন শিল্পী তেমন কণ্ঠ কি গান আবার যদি এরকম সিনেমা বানানো হতো মনটা কেঁদে ওঠলো আবার দেখার পরে |
| `bn_1046` | 1 | 0.0010 | 11 | প্রথম দিক দিয়ে এত সুন্দর হবে ভাবিনি। এ কথায় অসাধারণ ছিলো। |
| `bn_0815` | 0 | 0.0011 | 16 | কত কি যে দেখা বাকি আছে। তেমন কিছু না এখন এই কাহিনী দিয়ে মুভি বানাতে বসছে |
| `bn_1251` | 0 | 0.0012 | 5 | চার সতিনের ঘর সিনেমাটা ইমোশনাল |
| `bn_1780` | 1 | 0.0014 | 15 | বিনোদন এত হইছে যে আমি এতক্ষন সংগাহীন ছিলাম৷এখন যাকে দেখি তারেই হিরো আলম মনে হয়৷ |
| `bn_1968` | 0 | 0.0014 | 10 | এইসব খারাপ ছবির বিরুদ্ধে নায়ক মান্না ভাই প্রতিবাদ করে গ্যাছে। |
| `bn_0155` | 0 | 0.0016 | 3 | সুন্দর সামাজিক ফ্লিম। |
| `bn_0515` | 0 | 0.0016 | 10 | ছবি টা অনেক টাই মান্না ভাইয়ের কপি করা আমি কনফার্ম |
| `bn_1090` | 1 | 0.0016 | 21 | দারুন দারুন দারুন, অনেকদিন বাদে এত্ত সুচারু অভিনয় পূর্ণ , অনবদ্য সংলাপ সমৃদ্ধ গল্পের তৃপ্তিকর পরিসমাপ্তির স্বাদ মন প্রাণ ভরে নিলাম। |
| `bn_1265` | 0 | 0.0017 | 8 | এই মুভিতে দিঘি ও ডিপজলের অভিনয় ছিল বেষ্ট |

If a large share of the corpus sits near the boundary, that is the silhouette of
0.0534 made concrete — the halves are two sides of one crowd, not two crowds.

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
