# Chapter 3 — Data, Corpus Audit, and Construct Validation

## 3.1 Research design and the data-privilege contract

This chapter reports the empirical foundation of the study: what the data are,
what was found to be wrong with them, and what remained defensible afterwards.
It is placed before the framework chapter because the target construct had to
survive examination before any generator could be evaluated against it. Had the
construct failed, the framework would have had nothing to condition on, and the
remaining chapters would not have been written.

The work proceeds in seven registered stages, and the ordering is a
methodological control rather than a matter of convenience. Stage S0 audits the
raw workbook against the claims made about it, writing nothing. Stage S1 cleans
the corpus under rules fixed in advance. Stage S2 tests whether unsupervised
structure in the cleaned corpus reflects anything about audiences, and it is
here that the analysis was redirected. Stage S3 trains the two verifiers on
disjoint data. Stage S4 fits thresholds, weights and prompts on a development
subset only. Stage S5 executes the frozen generation surface. Stage S6 scores
that surface with the verifier that was withheld from the loop. The critical
property of this order is that every decision taken at one stage is recorded
before the next stage can supply a reason to revise it. In particular, the
frozen split map is written after the S2 outcome is on record, so the split
cannot be tuned to a result that already exists.

Two textual resources support the study and they are never joined. The Bangla
review corpus supplies observations for construct development, retrieval
examples and verifier training. The Bangla Wikipedia plot corpus supplies film
synopses that serve as generation inputs. No review is ever treated as belonging
to a particular synopsis, for the plain reason that the review data contain no
movie identifier of any kind. A film-to-review mapping would have been the most
natural design for pre-release response modelling, and its impossibility is
reported here rather than approximated by title-matching against text, because
in-text film names are rare and matching them would manufacture a linkage the
data do not contain.

Three data privileges are fixed for the whole study and are stated once, here,
rather than repeated at each point of use. Gold-300 is reserved for evaluation
and enters no training procedure, no retrieval index, no prompt and no threshold
fit. The retrieval index and Verifier-A are built from R1 alone. Verifier-B is
trained from R2 alone and never participates in generation or in any acceptance
decision; it scores the completed surface in S6 and nothing else. These are not
implementation conveniences. Without the R1/R2 separation the later
verifier-divergence analysis would compare an evaluator against a system that
had already been optimised against that same evaluator, and the resulting
agreement would measure nothing. Chapter 4 describes how the third privilege is
enforced mechanically rather than by discipline.

## 3.2 Data lineage and the isolation walls

Table 3.1 traces every row from the source workbook to the partition it ends up
in, together with the wall that governs its use. The intended graphical form of
this lineage, Figure 3.1, is deferred at the author's request; the table carries
the same content, and no claim in this chapter depends on the figure.

**Table 3.1. Frozen data lineage, partition composition and isolation walls**

| Stage | Artifact | n | Region A / B | Governing constraint |
|---|---|---:|---|---|
| Source | `Raw ... .xlsx`, sheet `Sheet1` | 5,000 | 1,999 / 3,001 | Opened read-only; SHA-256 and byte size fixed; never written to |
| S1 | `data/cleaned/bn_clean.csv` | 4,730 | 1,910 / 2,820 | Whitespace-only normalisation; Bangla characters preserved exactly |
| S2 | near-duplicate-controlled surface | 4,625 | 1,897 / 2,728 | LaBSE cosine ≥ 0.95 removed; threshold registered before use |
| Split | Gold-300 (G) | 300 | 123 / 177 | Evaluation only: no training, no index, no prompt, no threshold fit |
| Split | R1 | 2,162 | 886 / 1,276 | Sole source of the retrieval index and of Verifier-A |
| Split | R1 development subset | 200 | 82 / 118 | Drawn inside R1; not a fourth top-level part |
| Split | R2 | 2,163 | 888 / 1,275 | Sole source of Verifier-B, which never enters the loop |
| Stimuli | `data/plots_bn.csv` | 120 | — | Generation input only; never enters clustering or verifier training |

Three facts in Table 3.1 are worth stating in prose because they are easy to
misread. First, the development subset is contained in R1 rather than carved out
of it, so R1 remains 2,162 rows in the frozen split and 1,962 denotes its
non-development remainder; the three top-level parts have zero overlap. Second,
the split is stratified jointly on sentiment and on corpus region, and it
matches the corpus within 0.1 percentage points on both, with
`input_sha256 = 295c839c…` recorded in the split map so the surface it was drawn
from is identifiable. Third, the region column referenced throughout the table
is not a property of the reviews as collected; it is the outcome of the source
audit reported in Section 3.5, and it is carried in the split map precisely
because that audit made it a variable the design has to control.

Two measurement conventions recur below. The adjusted Rand index (ARI) [@b39]
measures agreement between two partitions after correction for chance
agreement, and is zero for independent partitions and one for identical ones.
The area under the receiver-operating-characteristic curve (AUC) measures how
well a single scalar quantity separates a binary label, and is 0.5 for a
quantity that carries no information about it. Where an association between two
binary variables is reported, the φ coefficient is used, which for a 2 × 2 table
is Pearson's correlation between the two indicators.

## 3.3 Primary review corpus and read-only audit

The primary corpus is version 3 of the Mendeley Data resource *Raw Bangla Movie
Review Comment Dataset for Sentiment Analysis and Natural Language Processing*
[@b4], specifically the `Sheet1` worksheet of the distributed workbook. Its byte
identity is fixed by SHA-256
`8f972734fc3629427cdf8d01716aa817f7b325410b2fdd0f26cbc2e68506db9f` and a size of
195,186 bytes. The hash is not ceremonial. Every stable `review_id` in this
study has the form `bn_<row index>`, zero-padded to four digits and taken from
the row position in this exact file, so a reordered or extended replacement
would silently change what every downstream identifier denotes while leaving all
counts intact. Fixing the hash converts that failure from silent to loud.

The workbook holds 5,000 rows and two columns, `Movie Review` and `Sentiment`.
It carries neither a movie-title column nor any row-level source field. The
consequence for the research design was stated in Section 3.1; the consequence
for provenance is stated here. The dataset's collector, contacted during the
audit, recalled gathering organic comments in the same way throughout but
retained no collection log. That recollection cannot be reconciled with the
file's own internal layout, described in Section 3.5. The protocol had
pre-committed that a computed test supersedes recall-based provenance where the
two disagree, so this study reports a Mendeley-hosted Bangla review corpus whose
row-level collection provenance is unrecoverable — not a verified sample of
organic Bangla audience opinion. That is a weaker claim than the dataset's own
description supports, and it is the claim the evidence permits.

Because the pipeline specification recorded eleven quantitative claims about
this workbook before it was ever opened, the audit could be run as a
verification rather than a description. Table 3.2 gives the result. Eight
claims reproduced exactly and three did not, and in each of the three the
specification was corrected to the observed value rather than the observation
being explained away.

**Table 3.2. Read-only audit of the eleven registered S0 claims**

| Quantity | Claimed | Observed | Outcome |
|---|---:|---:|---|
| `n_rows` | 5,000 | 5,000 | match |
| `label_counts` (0/1/2) | 1,665 / 1,664 / 1,670 | 1,665 / 1,664 / 1,670 | match |
| `exact_duplicates` | 204 | 204 | match |
| `normalized_duplicates` | 205 | 206 | **corrected** |
| `short_reviews_lt3_words` | 72 | 72 | match |
| `null_rows` | 1 | 2 | **corrected** |
| `usable_n` | 4,722 | 4,732 | **corrected** |
| `median_words` | 8 | 8 | match |
| `max_words` | 84 | 84 | match |
| `emoji_rows` | 0 | 0 | match |
| `url_or_mention_rows` | 0 | 0 | match |

The three corrections are not independent, and the way they interlock is the
most informative part of the audit. The claimed `usable_n` of 4,722 is
reproduced exactly by subtracting the three drop sets from 5,000 as though they
were disjoint: 2 + 72 + 204 = 278, and 5,000 − 278 = 4,722. That arithmetic
already used two null rows, while the same specification table reported one, so
the specification was internally inconsistent with its own total and the defect
lay in the reporting of `null_rows` rather than in the handling of nulls. The
subtraction also double-counts the ten rows that are both duplicates and shorter
than three words. Computing the union once rather than summing the parts gives
268, and therefore a usable count of 4,732. Under the normalised duplicate
definition the same computation gives a union of 270 and a usable count of
4,730, and both variants are reported because the choice between them is a
cleaning decision and not an auditing one.

Each measured quantity is tied to an explicit definition so that the table is
reproducible: a word is a whitespace-delimited token with no tokeniser,
stemmer or stopword list involved; a null row has missing or whitespace-only
text or a missing label; an exact duplicate is an occurrence beyond the first of
an identical string; a normalised duplicate applies Unicode NFC, whitespace
collapse and stripping as a comparison key only, never to the stored text. Two
further observations are recorded without being claim-checked: six rows carry an
orphan `U+FE0F` variation selector with no pictographic character attached,
which is why the emoji count is zero rather than six, and mean length differs
markedly by label at 8.19, 11.85 and 8.84 words for classes 0, 1 and 2. The
second of these becomes relevant in Section 3.5.

The corpus is short-text. Mean length is 9.63 words, the median is 8, the
minimum is 1, and only twelve of 5,000 reviews reach fifty words. Every
subsequent methodological choice in this study is constrained by that fact, and
the scientific risk it creates — that a sentence encoder applied to eight-word
opinions will principally recover sentiment — is the reason the trap-checks in
Section 3.6 were registered before any clustering was run.

## 3.4 Cleaning and the frozen partition

Cleaning is rule-based, ordered, and deliberately conservative about Bangla
orthography. No character is normalised, nothing is transliterated, no stemming
or stopword removal is applied, and no TF–IDF transformation appears anywhere in
the main pipeline. LaBSE and BanglaBERT are contextual encoders and are degraded
rather than helped by such preprocessing, so the only text modification
performed is whitespace collapse, which touched 254 rows. Table 3.3 gives the
cascade in execution order with the count removed at each step.

**Table 3.3. S1 cleaning cascade, in execution order**

| # | Step | Rows in | Removed | Rows out | Note |
|---:|---|---:|---:|---:|---|
| 1 | `drop_null` | 5,000 | 2 | 4,998 | One missing text, one missing label |
| 2 | `strip_url_html_mentions` | 4,998 | 0 | 4,998 | Zero matches; step retained for reproducibility |
| 3 | `normalize_whitespace` | 4,998 | 0 | 4,998 | 254 rows modified; whitespace only |
| 4 | `drop_exact_duplicates` | 4,998 | 205 | 4,793 | First occurrence kept |
| 5 | `drop_normalized_duplicates` | 4,793 | 1 | 4,792 | NFC + collapse used as key; text unchanged |
| 6 | `drop_short` | 4,792 | 62 | 4,730 | Fewer than three whitespace tokens |
| — | **`bn_clean.csv`** | — | **270** | **4,730** | Class counts 1,513 / 1,599 / 1,618 |

Step 2 removed nothing, which is worth reporting rather than deleting: a corpus
of social-media film comments containing zero URLs, zero HTML fragments and zero
`@` mentions is already mildly unusual, and it is the first of several
indications that not all of these rows reached the workbook by the route the
dataset description implies.

The cleaning cascade breaks the corpus balance, and the cleaning log says so
explicitly rather than leaving it to be discovered downstream. The raw file is
curated to near-uniform class sizes; the drops fall unevenly, with 152, 65 and
52 rows lost from classes 0, 1 and 2 respectively plus the single unlabelled
row. No downstream step may therefore assume a balanced corpus. Chance-corrected
statistics such as ARI are unaffected by this, which is one reason they are
preferred here over raw agreement.

Near-duplicate control is applied after rule-based cleaning, using cosine
similarity between L2-normalised LaBSE embeddings [@b3] at a threshold of 0.95
that was registered before the clustering it feeds. Pairs are enumerated
exhaustively over the strict upper triangle in row blocks rather than by
approximate nearest-neighbour search, so no pair is missed; within a
near-duplicate group the row with the lowest `review_id` survives, and a
candidate is compared only against rows already kept, which prevents a removed
row from evicting a third row through a transitive chain. Every pair at or above
the lowest swept threshold is logged with both review texts so the removals can
be inspected directly.

At the primary threshold the procedure removes 105 rows and leaves the 4,625-row
surface on which the frozen split is drawn. That figure is reproduced
independently by the two per-region runs, which remove 13 rows from region A and
92 from region B, and whose pair counts of 13 and 106 sum to the 119 pairs found
on the full corpus. Table 3.4 reports the sensitivity of the trap-check to this
threshold, and it must be read carefully because it does not say the same thing
everywhere.

**Table 3.4. Sensitivity of the sentiment trap-check to the near-duplicate threshold**

All rows use the K = 3 pilot clustering, which is the configuration the
trap-check was registered against; the K = 2 solutions examined from Section 3.6
onward give different ARI values and are reported separately in Table 3.7.

| Surface | Threshold | Rows removed | Surviving n | ARI vs sentiment | Registered verdict |
|---|---|---:|---:|---:|---|
| Full corpus | none | 0 | 4,730 | 0.1792 | Band 1 · `NOT_SENTIMENT_ALIGNED` |
| Full corpus | 0.90 | 325 | 4,405 | 0.2181 | **Band 2 · `PARTIAL_OVERLAP`** |
| Full corpus | 0.95 (primary) | 105 | 4,625 | 0.1793 | Band 1 · `NOT_SENTIMENT_ALIGNED` |
| Full corpus | 0.98 | 38 | 4,692 | 0.1784 | Band 1 · `NOT_SENTIMENT_ALIGNED` |
| Region A | 0.90 | 38 | 1,872 | 0.1826 | Band 1 · `NOT_SENTIMENT_ALIGNED` |
| Region A | 0.95 (primary) | 13 | 1,897 | 0.1804 | Band 1 · `NOT_SENTIMENT_ALIGNED` |
| Region A | 0.98 | 7 | 1,903 | 0.1777 | Band 1 · `NOT_SENTIMENT_ALIGNED` |
| Region B | 0.90 | 286 | 2,534 | 0.0182 | Band 1 · `NOT_SENTIMENT_ALIGNED` |
| Region B | 0.95 (primary) | 92 | 2,728 | 0.0172 | Band 1 · `NOT_SENTIMENT_ALIGNED` |
| Region B | 0.98 | 31 | 2,789 | 0.0178 | Band 1 · `NOT_SENTIMENT_ALIGNED` |

`NOT_SENTIMENT_ALIGNED` is the registered label for ARI below 0.2 against the
sentiment column, and it licenses only the negative statement that the partition
is not a rediscovery of sentiment; it is not evidence that the partition is
meaningful. The sweep was included so that a threshold-dependent conclusion
could not be presented as a robust one, and on the full corpus the conclusion
*is* threshold-dependent: at 0.90 the ARI crosses the pre-registered boundary
and the verdict changes to `PARTIAL_OVERLAP`, which would have required a
residual test. This is disclosed rather than omitted. Its practical weight is
limited, because Section 3.5 rejects the full-corpus partition on entirely
separate grounds, but it constitutes a second and independent reason not to rest
any claim on that partition. Within each region, where the analysis actually
lives, the verdict is constant across all three thresholds, and the largest
movement in ARI across the sweep is 0.005 in region A and 0.001 in region B.
The 0.95 threshold is therefore retained as registered and is not retuned after
seeing the clustering.

## 3.5 Why full-corpus clustering was rejected: the source signature

The first construct analysis embedded the whole cleaned corpus with LaBSE [@b3]
and fitted K-means with three components in the original embedding space. UMAP
is used in this study for visualisation only and never as a clustering space,
because distances after a non-linear manifold projection are not the distances
the clustering objective was defined on. The partition was non-degenerate, with
cluster shares of 39.2, 30.9 and 29.9 per cent, and it passed the sentiment
trap-check at ARI 0.1793. On its own that reads as a promising result.

It is not one. Scored against a variable that describes where in the source file
a review sits, the same partition reaches ARI 0.4813 — substantially more
agreement with file position than with what the review says, and the ordering
holds at every swept threshold. Recast as a binary question, cluster 0 against
the rest and region A against region B, the partition identifies which corpus a
review came from with 93.3 per cent accuracy, ARI 0.7487 and φ 0.861. The
encoder had recovered provenance. Cluster 0 held 1,814 reviews of which only 12
carried the neutral label, while region A after cleaning held 1,910 reviews of
which none did; the correspondence is close enough that the reading is
unavoidable once the region variable exists.

That variable exists because of a separate audit whose result is more
consequential than the clustering it displaced. The workbook is not one corpus.
It is two, concatenated, and the join is at raw row 1999. Table 3.5 gives the
profile of the two regions and the four features on which they do not merely
differ but are incompatible.

**Table 3.5. The two-corpus source signature**

| Panel A — register profile | Region A (rows 0–1998) | Region B (rows 1999–4999) |
|---|---:|---:|
| n | 1,999 | 3,001 |
| দাঁড়ি-terminated | 38.7% | 99.2% |
| Contains a first-person pronoun | 13.5% | 0.8% |
| Contains an exclamation mark | 3.4% | 0.3% |
| Contains a comma run | 3.3% | 0.0% |
| Median words | 9.0 | 8.0 |
| Word types per 1,000 tokens | 255.0 | 127.6 |

| Panel B — structural impossibilities on the 1,618 class-2 rows | Rate elsewhere | Expected | Observed | log₁₀ *p* |
|---|---:|---:|---:|---:|
| First-person pronoun | 9.22% | 149.2 | **0** | −68.0 |
| Exclamation mark | 2.38% | 38.5 | **0** | −16.9 |
| Comma run | 2.06% | 33.3 | **0** | −14.6 |
| দাঁড়ি present | 62.15% | 1,005.5 | **1,618** | −334.3 |

Panel A establishes that the two halves are written differently. Panel B
establishes that the difference is not a matter of degree. Among the 1,618
cleaned neutral-class rows — all of which lie inside region B — not one contains
a first-person pronoun, not one contains an exclamation mark, and not one
contains a run of commas, while every single one is terminated by a দাঁড়ি. The
log₁₀ *p* column gives the base-ten logarithm of the probability of a count that
extreme under the rate observed in the remaining rows; these are not marginal
significance levels but arithmetic statements about counts. No population of
people writing about films avoids the word আমি 1,618 consecutive times. The
first-person measurement uses exact matching against a closed pronoun set
(আমি, আমার, আমাকে, আমরা, আমাদের, আমায়) and does not count first-person verb
inflections such as দেখলাম, so the finding is properly read as the absence of
first-person pronouns rather than the absence of a first-person voice.

Three further observations fix the interpretation. First, the transition is a
step and not a drift: the rolling hundred-row দাঁড়ি rate stands at 29 per cent at
row 1949, reaches 43 per cent at 1974, 60 per cent at 1999 and 100 per cent by
row 2049, after which it does not fall. A changing population of commenters
produces a gradient over thousands of rows, not a saturation over fifty.
Second, the signature belongs to the region and not to the label. Rows
3000–3664 carry label 1 and rows 3665–4330 carry label 0, yet both sit at 96.5
and 99.8 per cent দাঁড়ি respectively with first-person rates of 3.5 and 0.0 per
cent, while rows 499–896, also label 0, sit at 32.4 per cent দাঁড়ি and 9.0 per
cent first-person. Sentiment therefore cannot be the grouping variable. Third,
the neutral class is perfectly nested inside the second corpus: all 1,670
neutral rows are in region B and region A contains none.

That third fact explains a superseded finding, which is reported here rather
than deleted because the shape of the error is instructive. An earlier probe
asked whether the neutral class was a different kind of text and answered yes,
on measurements that remain correct. The interpretation was wrong: what looked
like a property of a semantic class was a property of a region of a file, and it
had been misread as semantic only because the class and the region coincide
exactly. Its measurements survive in Panel B; its conclusion does not. The
general lesson — that a class-conditioned measurement cannot distinguish a
property of the class from a property of the rows that happen to carry it — is
the reason the region variable is now a stratification variable in the frozen
split rather than a footnote.

What produced region B is not adjudicated. The register is inconsistent with
organically collected comment threads, and that negative statement is all the
argument requires: a corpus whose rows cannot plausibly be audience writing
cannot ground a claim about audience language, so the construct analysis is
restricted to region A. Attributing region B positively to a specific process —
machine translation, a normalising ingest pipeline, template expansion, or
language-model generation — would require distinguishing between those
possibilities, and eleven orthographic and structural features measured on
eight-word texts cannot do so. The most a reader is asked to accept is that
these rows were produced by some uniform automated process, and that claim rests
on the counts in Panel B rather than on any citation.

Region A survives as a usable corpus. It is smaller and binary, with 1,910
cleaned rows in two sentiment classes, but its register is consistent with
audience writing and it is the corpus on which everything that follows is built.

## 3.6 Region-A construct discovery and the Region-B negative control

Within region A, K-means was fitted for every K from two to eight on the
1,897-row near-duplicate-controlled surface, and the candidate solutions were
judged against four criteria registered in advance. Prediction strength [@b38]
measures how reliably a clustering trained on one half of the data assigns the
other half consistently, with 0.8 the conventional threshold for a supported K.
Bootstrap ARI measures whether resampling reproduces the same partition.
Silhouette [@b43] measures separation relative to within-cluster spread. The gap
statistic [@b40] compares within-cluster dispersion against a uniform reference
distribution. Table 3.6 reports all four across the sweep for both regions.

**Table 3.6. Clusterability and stability sweep, K = 2 to 8**

| K | Region A silhouette | Region A gap | Region A prediction strength | Region A bootstrap ARI | Region B silhouette | Region B gap | Region B prediction strength | Region B bootstrap ARI |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 0.0534 | 0.9498 | **0.8605** | 0.9399 ± 0.0290 | 0.0394 | 0.8907 | **0.8183** | 0.9624 ± 0.0362 |
| 3 | 0.0146 | 0.9700 | 0.6692 | 0.9094 ± 0.0454 | 0.0329 | 0.9152 | 0.6589 | 0.8808 ± 0.2426 |
| 4 | 0.0112 | 0.9857 | 0.4153 | 0.5305 ± 0.1782 | 0.0285 | 0.9342 | 0.6709 | 0.9065 ± 0.1088 |
| 5 | 0.0182 | 0.9986 | 0.3749 | 0.6466 ± 0.2134 | 0.0280 | 0.9508 | 0.4306 | 0.7388 ± 0.1910 |
| 6 | 0.0117 | 1.0122 | 0.3637 | 0.6715 ± 0.1616 | 0.0299 | 0.9627 | 0.4400 | 0.8152 ± 0.1476 |
| 7 | 0.0172 | 1.0224 | 0.3542 | 0.7548 ± 0.0972 | 0.0247 | 0.9760 | 0.3697 | 0.7037 ± 0.1535 |
| 8 | 0.0103 | 1.0323 | 0.3145 | 0.6417 ± 0.0980 | 0.0273 | 0.9854 | 0.3122 | 0.6651 ± 0.1050 |

Only K = 2 clears the prediction-strength threshold, in either region, and it
does so decisively: 0.8605 against 0.6692 for the next candidate in region A.
Bootstrap resampling reproduces the two-way partition at ARI 0.940 ± 0.029.
Read alone, that pair of numbers looks like the discovery of two groups.

It is not, and the remaining columns are the reason. Silhouette peaks at 0.0534,
which is close to the value expected when points sit at comparable distances
from both centroids. The gap statistic rises monotonically across the entire
sweep and therefore selects no K at all, since the criterion requires a local
maximum. HDBSCAN, run with the hierarchical density formulation [@b41] and its
reference implementation [@b42], is permitted to choose its own number of
clusters and to designate points as noise; in region A it labels 100 per cent of
points as noise, which is to say it finds no region of the space dense enough to
call a cluster. Three of the four criteria therefore return nothing, and only
stability returns a strong value.

Stability without separation has a specific interpretation, and recent
methodological work makes it explicit. Pinto et al. [@b73], analysing K-means on
simulated and real psychometric data, report solutions that are highly stable —
k = 2, silhouette approximately 0.31, ARI 0.999 ± 0.001, sizes 50.6 and 49.4 per
cent on 8,360 respondents — while arguing that such solutions are "better
interpreted as geometric stratifications of a latent psychological continuum
rather than as evidence for discrete subtypes", and stating the principle
directly: "Stability, therefore, is not equivalent to validity." Cornelissen et
al. [@b74] reach the same conclusion in a different domain, showing that an
established four-type melodic-contour typology was an artefact of k-means
placing centroids near the leading principal axes "for entirely mathematical,
not musical reasons". The defensible reading of Table 3.6 is accordingly that
K = 2 is a reproducible bisection of a continuum, not a discovery of two
populations. This is why the terminology of this thesis speaks of an axis with
two levels, and why the words *persona*, *audience type* and *subgroup* do not
appear as claims anywhere in it.

The bisection is also entangled with length. Length AUC for the region-A cut is
0.6764, which fires the registered `LENGTH_CONFOUNDED` label: length is a major
but not sole component of the cut. The two halves differ in a direction that is
the opposite of the obvious one. At an equal 4,000-token budget, bootstrapped
thirty times, the shorter half draws 1,913.2 ± 19.5 distinct word types while
the longer half draws 1,623.4 ± 21.4, even though the shorter half averages 8.85
words against 13.12. Equal-budget comparison is essential here, since the larger
half would trivially show more types otherwise. A half that writes at greater
length from a smaller vocabulary is the signature of formulaic writing; a half
that writes briefly from a larger one is the signature of saying something
particular. The two halves also differ in voice, with first-person pronouns in
17.3 per cent of the longer half against 8.8 per cent of the shorter, and in
sentiment composition, at 66 per cent positive against 74 per cent negative.

Because length is implicated, a residual analysis was registered before it was
run: does the cut retain predictive content once sentiment and length are both
known? Using cell-majority prediction, the marginal rate is 60.25 per cent;
sentiment alone lifts it to 69.53, length band alone to 65.47, and both together
to 70.06. The lift attributable to the cut is therefore 9.81 percentage points,
which fires `RESIDUAL_SURVIVES` — but the registered cutoff is 10.0, so the
verdict clears by 0.2 points and must be reported as weak wherever it appears.
Length contributes only 0.53 points once sentiment is known. Two further
diagnostics were registered with it. Within each sentiment class separately,
length still separates the two halves at AUC 0.6115 and 0.6567, so the length
association is not an artefact of sentiment; within each of four length
quartiles separately, the association between the cut and its profile holds at
|φ| between 0.3133 and 0.4112, so it is not an artefact of length. The richness
inversion also holds inside all four length quartiles at a common 1,100-token
budget, which is the strongest available evidence that the halves differ in kind
and not only in size. It should be noted that this analysis is by
resubstitution, under which a low lift is strong evidence and a high one is a
ceiling rather than a measurement; the lift reported here is low.

Region B serves as a negative control, and its function is to test whether the
diagnostics above can be passed by a cut with no content. On the 2,728-row
region-B surface, K = 2 is again selected and again looks stable, at prediction
strength 0.8183 and bootstrap ARI 0.9624 — higher stability than region A. None
of the content signatures replicate. Length AUC is 0.5498, which fires `NOT_LENGTH`
rather than the confound label; the strongest of eleven surface features reaches
only 0.5806; at a 4,000-token budget the two halves draw 1,186.3 ± 16.6 and
1,181.3 ± 16.6 types, so the richness inversion does not merely weaken but
disappears; the median assignment margin is 0.0583 with 12.2 per cent of points
within 0.02 of the boundary; and HDBSCAN labels 96.7 per cent of points as
noise. Its residual analysis returns a 7.2-point lift, but both independence
diagnostics fail — the within-sentiment length AUC falls to 0.5276, giving
`ENTANGLED`, and the within-band association drops to |φ| = 0.0828 in one band —
and the richness inversion holds in only one of four bands. Log-odds profiling
with an informative Dirichlet prior [@b56] separates the two region-B halves on
whether they are built around গল্প or around সিনেমা, which is to say on template
family rather than on anything a viewer chose to say.

Table 3.7 places the two regions side by side. The comparison is the chapter's
central methodological claim: every criterion that region A passes on stability
alone, region B also passes, and only the content criteria distinguish them.

**Table 3.7. Region-A axis evidence against the Region-B negative control**

| Diagnostic | Region A | Region B | Reading |
|---|---:|---:|---|
| n on the split surface | 1,897 | 2,728 | Separate corpora, not replications of one another |
| Selected K | 2 | 2 | Algorithmic bisection in both |
| Prediction strength | 0.8605 | 0.8183 | Both clear the registered 0.8 threshold |
| Bootstrap ARI | 0.9399 ± 0.0290 | 0.9624 ± 0.0362 | Region B is the *more* stable of the two |
| Silhouette | 0.0534 | 0.0394 | Negligible separation in both |
| Gap statistic | selects no K | selects no K | No positive clusterability evidence |
| HDBSCAN noise fraction | 100% | 96.7% | No density structure in either |
| ARI vs sentiment, at K = 2 | 0.1522 | 0.0107 | Neither cut is a sentiment rediscovery |
| Length AUC | 0.6764 (`LENGTH_CONFOUNDED`) | 0.5498 (`NOT_LENGTH`) | Region A's cut tracks length; region B's does not |
| Types at 4,000 tokens (short / long half) | 1,913 / 1,623 | 1,186 / 1,181 | Inversion present in A, absent in B |
| Residual lift over sentiment and length | +9.81 pp (`RESIDUAL_SURVIVES`, weak) | +7.2 pp, diagnostics fail | Region A's residual is independent of both confounds; region B's is not |
| Richness inversion across length quartiles | 4 of 4 | 1 of 4 | The profile replicates internally only in region A |
| Standing | Reproducible cut through a continuum | Stable but contentless cut | Stability is necessary and not sufficient |

## 3.7 What the geometry could not settle

The diagnostics in Section 3.6 establish that the region-A cut is reproducible,
that it is not a restatement of sentiment, and that it retains weak content
after length is accounted for. They cannot establish that it corresponds to
anything a person would recognise. A cut can be geometrically reproducible and
semantically empty, as region B demonstrates within this study and as Pinto et
al. [@b73] and Cornelissen et al. [@b74] demonstrate outside it. The protocol
therefore made human judgement the arbiter of RQ1 and pre-committed the claim to
be made under each outcome before any annotation was collected. The intended
graphical summary of the clusterability and confound diagnostics, Figure 3.2, is
deferred at the author's request; Tables 3.6 and 3.7 carry its content.

Two human studies follow. The first failed, and it is reported in full because a
failed instrument that is quietly replaced is indistinguishable from an
instrument chosen after seeing which one worked. Both used two annotators rather
than the three the protocol originally specified, which is a registered
deviation; both were run under the consent and ethics arrangements documented in
Appendix B, with adult volunteers, voluntary informed consent, no honorarium,
private identities and coded responses. Appendix B also records the risk that
recruiting university batchmates creates, namely that a relationship-based
convenience sample can feel social pressure to agree, and it makes no claim of
institutional review or exemption.

## 3.8 Human validation attempt 1: ordinal ratings, and why the gate failed

The first instrument drew on Gold-300 and asked each annotator to assign an
engagement-specificity rating on a four-point ordinal scale from 0 to 3. Of 600
possible item ratings, 598 were returned, with 298 items rated by both
annotators. Because only 123 of the 300 frozen Gold items fall in region A, and
the split map is frozen and was not regenerated to improve this, the substantive
gate would have run on that subset with correspondingly reduced power — a
consequence recorded as a number rather than absorbed silently.

The instrument did not reach its substantive gate. Ordinal Krippendorff's α
[@b31] was 0.4970 against a registered reliability floor of 0.667, firing
`UNRELIABLE`. Surface agreement looked far better than that: exact agreement was
75.5 per cent and within-one agreement 98.7 per cent. The gap between those
figures and α is the whole diagnosis. The two annotators placed 202 of 298 and
227 of 298 ratings on the single value 2, so the distribution was nearly
degenerate, and agreement that arises because both raters almost always choose
the same category carries very little information. Chance-corrected coefficients
are constructed precisely to discount that situation, and here it did. Nominal α
was 0.4324 and linearly weighted Cohen's κ 0.4456, both consistent with α rather
than with raw agreement.

Gwet's AC1 computed on the same ratings is 0.8705, and it is not used as rescue
evidence. AC1 was designed for exactly this configuration, high agreement with
skewed prevalence [@b44], and it would license the conclusion the registered
gate refused. Subsequent analysis shows that it is not a substitute for κ and
can rise mechanically with prevalence skew [@b45], so selecting it after seeing
that α failed would be choosing the coefficient by its answer. The registered
verdict stands. It is important to state what `UNRELIABLE` does and does not
mean: the instrument was inconclusive, and that is not evidence that the
construct is absent. A rating scale that collapses cannot detect a distinction
that exists.

Two causes were identified, and only one was diagnosed at the time. The first is
the collapse just described. The second, recognised later, is that the ordinal
instrument required the construct to be named in advance and the name was
supplied by the analysis rather than by the annotators; if the name was wrong,
the instrument fails even when the underlying distinction is real. Both causes
point away from rating scales, and the literature had already said so:
Kiritchenko and Mohammad [@b29] showed that comparative judgements are more
reliable than rating scales for exactly this kind of intensity annotation. That
finding was available before the first instrument was designed and was not
consulted, which is recorded in the protocol's deviations log as a process
failure rather than presented as a discovery.

## 3.9 Human validation attempt 2: comparative intrusion judgments

The second instrument abandoned ratings for a forced-choice intrusion task, in
which the annotator sees four reviews of which three come from one side of the
cut and one from the other, and identifies the intruder. The design answers both
diagnosed causes at once. It replaces an absolute scale with a comparative
judgement, following the reliability argument in [@b29], and it never names the
construct, so the annotator is not required to accept the analysis's own
description of what distinguishes the two halves.

Fifty sets of four were drawn from region A with every Gold-300 item excluded,
so the failed instrument's material was not silently recycled and the evaluation
partition was left intact. Within each set the four reviews are length-matched
to within a two-word span. This is the design decision the study most depends
on, because the region-A cut is length-confounded at AUC 0.6764: matching on
length removes the confound by construction rather than by adjustment, so the
binding condition — that annotators must not be able to succeed on length alone
— is satisfied before any data are collected rather than argued afterwards. A
length-only heuristic scores 0.16 on the same sets, below the 0.25 chance rate.

Both annotators performed far above chance. One identified 39 of 50 intruders,
an accuracy of 0.780 with a 95 per cent Wilson interval of [0.648, 0.872]; the
other identified 42 of 50, an accuracy of 0.840 with interval [0.715, 0.917].
Against the 0.25 chance rate the exact one-sided binomial tail probabilities are
5.7 × 10⁻¹⁵ and 3.0 × 10⁻¹⁸. Both clear the registered 0.45 bar by a wide
margin, firing `HUMANLY_PERCEPTIBLE`. The pooled figure of 81 of 100 is
reported for completeness but is not the test, because the two annotators saw
the same fifty sets and the hundred trials are therefore not independent; the
per-annotator rows are the honest tests and both pass on their own.

The annotators chose the same option on 70.0 per cent of sets. That figure is
close to the 0.667 expected if two raters of this accuracy erred independently,
which is the relevant check: near-perfect agreement would have suggested the
pair were responding in lockstep to some shared surface cue, and agreement at
chance-consistent levels suggests instead that they were each solving the task.
Both annotators reported afterwards that the items looked alike to them, and
both scored close to 0.8. The distinction is perceptible without being readily
articulable, which is a property of the construct worth stating plainly rather
than smoothing over.

A second block tested direction rather than detection. Given a pair of reviews
from opposite sides of the cut and asked which one talks about something
particular in the film, each annotator answered 34 of 40 correctly, an accuracy
of 0.850 with Wilson interval [0.709, 0.929] and exact one-sided *p* =
4.2 × 10⁻⁶ against a 0.50 chance rate, with agreement at 75.0 per cent. This
block identifies the direction of the axis as engagement specificity rather than
merely confirming that a difference exists.

**Table 3.8. Human validation of the engagement-specificity axis**

| Instrument | Task and sample | Result | Confound control | Registered verdict |
|---|---|---|---|---|
| Attempt 1 | 0–3 ordinal rating; Gold-300; 598 of 600 ratings, 298 items doubly rated | Ordinal α = 0.4970 vs 0.667 floor; exact agreement 75.5%; within-one 98.7% | None available; 202/298 and 227/298 ratings collapsed onto the value 2 | `UNRELIABLE` — inconclusive, not negative |
| Attempt 2, detection | Four-way intrusion; 50 sets from region A excluding Gold-300 | 39/50 = 0.780, [0.648, 0.872], *p* = 5.7 × 10⁻¹⁵; 42/50 = 0.840, [0.715, 0.917], *p* = 3.0 × 10⁻¹⁸ | Sets length-matched within 2 words; length-only heuristic scores 0.16 vs 0.25 chance | `HUMANLY_PERCEPTIBLE` |
| Attempt 2, direction | Forced-choice pairs; 40 per annotator | Both 34/40 = 0.850, [0.709, 0.929], *p* = 4.2 × 10⁻⁶ | Construct label withheld throughout the detection block | Direction identified as engagement specificity |

Two limits of this evidence are stated here so that later chapters need not
restate them. Two annotators is a small panel, disagreements were not
adjudicated, and the gold rating in attempt 1 is the mean of two judgements
rather than a consensus. And a positive intrusion result establishes that the
distinction is perceptible; it does not convert a continuum into two discrete
kinds of viewer, and no such conversion is claimed.

## 3.10 Operational definition of the engagement-specificity axis

The construct that survives is a two-level axis of engagement specificity,
defined comparatively and prototypically rather than by checklist, because the
human evidence validates a relative distinction and a checklist would assert
more than was tested. Level 0 states an opinion without specificity: the comment
calls the film good or bad and stops, and it may be emphatic, repetitive,
intense, or even name an element — the story, the acting, the songs, the
direction, a character, a scene — but it stops at the naming. The diagnostic
question is whether the comment could be pasted under almost any film with
nothing about it changing. Level 1 takes hold of one particular thing in the
film and attaches a reaction to it: why it felt that way, what it is being
compared against, what was expected, what actually happened on watching. The
diagnostic question is whether the comment stops working under a different film.
Praise and criticism occur at both levels, as do short and long comments, and
both levels are ordinary colloquial Bangla (চলিত) of the kind written in Facebook
and YouTube comments. The instrument used with annotators is the Bangla text of
this definition, reproduced verbatim in `docs/axis_definition.md` as স্তর ০ and
স্তর ১; the English above is a native re-rendering of the same content rather
than a translation, since literal translation is a documented failure mode for
instrument text.

The direction of the axis is checked against the data using the equal-budget
figures from Section 3.6: at a matched 4,000-token budget the Level 1 half draws
1,913 types against Level 0's 1,623, while averaging 8.85 words against 13.12.
Raw type-token ratios over the two unequal corpora put the same contrast at 414
against 269 types per thousand tokens, and that pair is reported only as
confirmation of direction. It is not the reportable figure, because type-token
ratio falls as a corpus grows and the two halves differ in total size, which
inflates the gap. The counter-intuitive shorter-but-richer direction is retained
as measured and is not rewritten to match the expectation that engagement should
produce longer text.

Three constraints on how this construct may be described are fixed here and hold
for the remainder of the thesis. The permitted vocabulary is axis, gradient, the
cut, and level; the operational labels are Level 0 and Level 1. The variable
name `cluster_k2` survives in code and in the frozen split map, where renaming
it would invalidate the map, but it is not a claim about structure and bare
"cluster" is not used as one in the text. And the axis is not sentiment: Level 0
is 66 per cent positive and Level 1 is 74 per cent negative, so the two are
correlated and not identical, which is the reason the trap-check was registered
in the first place rather than assumed to pass.

One limitation is recorded at the point where the construct is defined rather
than deferred to the limitations chapter, because it bounds what the later
experiments can claim. In the *generated* text produced by the framework in
Chapter 5, the axis level remains recoverable from length alone at AUC 0.91 to
0.99. The axis as realised by a language model is therefore substantially a
length manipulation, whatever it is in human writing, and no claim of
length-neutral axis control is made anywhere in this thesis.

## 3.11 Plot corpus and experimental stimuli

The generation stimuli come from a separate corpus, for the reason given in
Section 3.1: without a movie identifier in the review data, no review can supply
the film that a generated response is a response to. Film synopses were
harvested from Bangla Wikipedia through the MediaWiki API across three seed
categories — বাংলা ভাষার চলচ্চিত্র contributing 66 articles, বাংলাদেশী চলচ্চিত্র 57, and
পশ্চিমবঙ্গের চলচ্চিত্র one — using 924 API calls and yielding 3,135 candidate
articles.

The candidates passed through a mechanical quality gate requiring Bangla script,
at least 120 characters, and between three and twelve sentences, with longer
plot sections truncated only at sentence boundaries. Of the 3,135 candidates,
124 passed and 3,011 were rejected: 2,925 had no plot section at all, 65 were
person articles rather than film articles, 15 fell below the sentence minimum
and 6 below the character minimum. The mechanical survivors were then read
individually, because a production-history section or a non-film page can pass
every surface check, and the harvest report states this requirement explicitly
rather than treating the gate as sufficient.

The resulting corpus is frozen at 120 synopses with retained sentence counts
ranging from three to twelve and a median of nine. A one-time seed-42 split
assigns 30 development plots and 90 evaluation plots; development plots support
prompt, weight and threshold work, and the 90 evaluation plots define the frozen
Phase-5 surface of 5,400 cases described in Chapter 5. Every row carries its
source URL, the exact Wikipedia revision identifier and timestamp, and CC BY-SA
4.0 licence metadata, and the corpus is committed to the repository so the
stimuli cannot drift between development and evaluation. Appendix D attributes
every retained article and revision and records the harvest date of 31 July
2026. Plot text is generation input only and enters no clustering, no retrieval
index and no verifier training set.

## 3.12 Chapter summary and the RQ1 verdict

The empirical foundation of this study is narrower than the one it set out to
build, and the narrowing is the chapter's principal result. Of 5,000 raw
reviews, 4,730 survive cleaning and 4,625 form the frozen split surface. Of
those, only 1,897 — the region-A subset — are admissible for construct work,
because the source workbook proved to be two corpora joined at row 1999 and
three-fifths of it carries a register that cannot be organic audience writing.
The first clustering result, which appeared to find three audience groupings,
was a corpus detector operating at 93.3 per cent accuracy.

Within region A, RQ1 resolves as follows. There are no discovered audience
personas, and no such claim is made. There is a reproducible bisection of a
continuum, selected at K = 2 by prediction strength 0.8605 and reproduced at
bootstrap ARI 0.940, which is not a restatement of sentiment (ARI 0.1522) and
which retains a weak but confound-independent residual of 9.81 percentage points
over sentiment and length together. Silhouette, the gap statistic and HDBSCAN
give it no support, and a region-B control passes every stability test while
failing every content test, which fixes the correct reading of stability. Two
human annotators detect the cut at 0.780 and 0.840 on length-matched material
against a 0.25 chance rate, and identify its direction at 0.850 each against a
0.50 chance rate, after an ordinal instrument on the same construct had failed
its reliability gate at α = 0.4970.

What the following chapters may therefore condition on is a two-level axis of
engagement specificity that is reproducible in geometry, perceptible to human
judges, and bounded in three specific ways: it is a cut through a continuum
rather than a partition into kinds, it is correlated with both sentiment and
length rather than independent of them, and in generated text it remains
recoverable from length alone. Every use of the axis in Chapters 4 through 7
inherits those three limits.
