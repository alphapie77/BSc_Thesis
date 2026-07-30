# S2b — Register probe: is `Sentiment == 2` a different kind of text?

> ### ⚠️ EXPLORATORY — not a confirmatory test
>
> The hypothesis behind this probe came from **reading the data after S2**, not
> from the pre-registration. No threshold here was fixed in advance, and no
> claim in this file may be reported as a confirmed finding. It exists to decide
> whether a confirmatory test is worth registering, and to put a specific,
> answerable question to the data collector. Registered as exploratory in
> `docs/protocol.md` (Deviations log, 2026-07-30).

- **Config:** `configs/s2b_register_probe.yaml` · **Input:** `data/cleaned/bn_clean.csv` (4730 rows)
- **Generated (UTC):** 2026-07-30T14:22:52.243354+00:00 · **Commit:** `1d100a9e2e8f91ae111a82ef996fad8b6cae607e-dirty`
- **Nothing is trained.** AUC is a rank statistic with no fitted parameters, so
  inviolable rule 10 is untouched.

## Why this probe exists

S2 produced clusters that do **not** reproduce the sentiment partition
(ARI 0.179) yet are moderately associated with it (Cramér's V 0.410). Refolding
that crosstab as *cluster 0 vs rest* × *Sentiment 2 vs rest* gives
**φ = 0.565** — a stronger association than the full three-way table — and only
**12 of 1,572** class-2 items land in cluster 0.

`docs/protocol.md` RQ1 Band 3 already names this confound: clusters recovering
**the source of the text** rather than any persona. `docs/STATUS.md` called it
*untestable in principle*, because venue was never retained at collection
(provenance fact (c)).

**Venue was not retained — but writing style survives in the text itself.** That
is what this probe measures.

## The design constraint that makes this argument work

Every feature is **orthographic or structural**: character counts, punctuation,
length. None of them can express an opinion about a film. A lexical feature
would be worthless here — a word like *দুর্বল* predicts a negative label *and* a
register at once, so separating with it would prove nothing.

So if these features separate class 2 from the rest, the classes differ in
**form**, not in what they say about films. `first_person` is the one judgement
call (a closed pronoun set, reporting voice rather than polarity); it is listed
separately so a sceptical reader can discount it without touching the rest.

## Separation by feature (AUC)

AUC 0.5 = the feature cannot tell the groups apart. Far from 0.5 in either
direction = it can.

| feature         |    auc |   separation |   mean_class2 |   mean_others |
|:----------------|-------:|-------------:|--------------:|--------------:|
| punct_per_token | 0.7510 |       0.5020 |        0.2229 |        0.1380 |
| n_comma         | 0.7401 |       0.4801 |        0.7732 |        0.3053 |
| has_danda       | 0.6893 |       0.3785 |        1.0000 |        0.6215 |
| n_danda         | 0.6235 |       0.2469 |        1.1100 |        0.8776 |
| mean_word_len   | 0.5959 |       0.1919 |        5.3817 |        5.1352 |
| first_person    | 0.4539 |       0.0922 |        0.0000 |        0.0922 |
| n_words         | 0.4834 |       0.0332 |        8.9302 |       10.3821 |
| n_exclaim       | 0.4881 |       0.0238 |        0.0000 |        0.0386 |
| has_comma_run   | 0.4897 |       0.0206 |        0.0000 |        0.0206 |
| n_question      | 0.4948 |       0.0103 |        0.0006 |        0.0129 |
| n_chars         | 0.5044 |       0.0088 |       55.3269 |       61.1761 |
| has_latin       | 0.5006 |       0.0012 |        0.0019 |        0.0006 |
| has_digit       | 0.4997 |       0.0007 |        0.0012 |        0.0019 |

The separations here are **moderate, not decisive** — the best single
feature reaches only 0.751. Reported as measured; the strong evidence is
in the two sections below, not in this table.

Strongest single feature: **`punct_per_token`**, AUC **0.7510**.

## Structural impossibilities — the decisive table

AUC is the wrong summary for a **rare** binary feature. Something present in 9%
of one group and 0% of another barely moves a rank statistic, yet "0 out of
1,618" is categorical. So each binary feature is also reported as: how many
class-2 items *would* carry it, if the class were drawn from the same
population as the others?

| feature       |   rate_in_others_% |   expected_in_focal |   observed_in_focal |   log10_p_if_same_population |
|:--------------|-------------------:|--------------------:|--------------------:|-----------------------------:|
| first_person  |               9.22 |               149.2 |                   0 |                        -68   |
| n_exclaim     |               2.38 |                38.5 |                   0 |                        -16.9 |
| has_comma_run |               2.06 |                33.3 |                   0 |                        -14.6 |
| has_danda     |              62.15 |              1005.5 |                1618 |                       -334.3 |

`log10_p_if_same_population` is the base-10 log of the probability of seeing a
count that extreme under the other classes' own rate. These are not marginal
p-values; they leave floating point behind entirely.

**Not one of the 1,618 class-2 texts contains a first-person pronoun,
an exclamation mark, or a run of commas — and every single one carries a দাঁড়ি.**
Four independent structural absolutes. No opinion about films makes a writer
avoid the word *আমি* 1,618 times in a row.

Note the definition: `first_person` is exact-token matching against a closed
pronoun set (আমি, আমার, আমাকে, আমরা, আমাদের, আমায়). First-person *verb* forms
(দেখলাম, লাগলো) are not counted, and a looser substring match finds a small
non-zero rate — so read this as "no first-person pronoun", not "no first-person
voice whatsoever".

## Lexical richness at an equal token budget

Unique word types in a fixed sample of 12,000
tokens, bootstrapped 200×. Equal budget is the
point: a class with more text trivially shows more distinct words, so raw counts
compare nothing.

|   class |   total_tokens |   types_at_budget |      sd |
|--------:|---------------:|------------------:|--------:|
|  0.0000 |     13053.0000 |         3577.0350 | 11.9446 |
|  1.0000 |     19256.0000 |         3303.4400 | 26.1742 |
|  2.0000 |     14449.0000 |         1772.2900 | 11.5562 |

Class 2 draws on **1772** distinct types per
12,000 tokens, against
3577 and 3303 for the other
classes. A vocabulary roughly half the size at identical length is not a
property of holding a neutral opinion; it is a property of how the text was
produced.

## Binary rates, with 95% Wilson intervals

Wilson rather than the normal approximation because one rate sits at exactly
100%, where the textbook interval collapses to zero width and overstates
certainty.

| feature       |   class |   rate_% |   ci95_lo_% |   ci95_hi_% |
|:--------------|--------:|---------:|------------:|------------:|
| has_danda     |       0 |  58.0304 |     55.5264 |     60.4937 |
| has_danda     |       1 |  66.0413 |     63.6841 |     68.3216 |
| has_danda     |       2 | 100.0000 |     99.7631 |    100.0000 |
| first_person  |       0 |   6.2128 |      5.1039 |      7.5436 |
| first_person  |       1 |  12.0700 |     10.5635 |     13.7584 |
| first_person  |       2 |   0.0000 |      0.0000 |      0.2369 |
| has_comma_run |       0 |   1.4541 |      0.9622 |      2.1918 |
| has_comma_run |       1 |   2.6266 |      1.9490 |      3.5313 |
| has_comma_run |       2 |   0.0000 |      0.0000 |      0.2369 |
| has_latin     |       0 |   0.0000 |      0.0000 |      0.2533 |
| has_latin     |       1 |   0.1251 |      0.0343 |      0.4549 |
| has_latin     |       2 |   0.1854 |      0.0631 |      0.5437 |

## Near-duplicate endpoints by class

|   Sentiment |   in_corpus_% |   in_near_dup_endpoints_% |   over_representation_x |
|------------:|--------------:|--------------------------:|------------------------:|
|      0.0000 |       32.0000 |                   25.5000 |                  0.8000 |
|      1.0000 |       33.8000 |                   24.4000 |                  0.7200 |
|      2.0000 |       34.2000 |                   50.1000 |                  1.4600 |

## What this does and does not show

**Shows:** class 2 differs from classes 0 and 1 on features that carry no
sentiment content, and the S2 clustering separates it far more sharply than it
separates sentiment.

**Does not show:** *why*. At least three explanations fit equally well, and this
data cannot choose between them:

1. class 2 was **synthetically generated** to fill the ~1,665-per-class
   quota (genuinely neutral film comments are rare on social media — people post
   when they feel strongly);
2. class 2 was **collected from a different venue** — a blog or review
   site, where formal register is native;
3. class 2 was **written by hand** by the annotator as neutral examples.

All three contradict provenance fact (c) ("bulk pull from Facebook groups and
YouTube channels"), and under **all three** the clusters track provenance rather
than persona. Distinguishing them requires the data collector, not more
statistics: see `docs/provenance_query.md`.

**Until it is answered, no persona claim resting on the three-class structure
can be defended.**
