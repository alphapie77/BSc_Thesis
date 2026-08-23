# Chapter 3 — Research Methodology, Data, and Construct Validation

## 3.1 Research design and data roles

This study follows a staged empirical design in which the target construct is
examined before any generator is evaluated. The sequence is deliberate. First,
the primary Bangla review corpus is audited, cleaned, and partitioned under
frozen data privileges. Second, unsupervised structure is tested for source,
sentiment, length, stability, and clusterability. Third, the surviving
distinction is evaluated with human judgments and converted into an operational
two-level axis. Only after those stages are complete may the labels be used for
retrieval, verifier development, or controlled generation.

Two textual resources have separate roles. The review corpus supplies
observations for construct development, retrieval examples, and verifier
training. The Bangla Wikipedia plot corpus supplies film synopses used as
generation inputs. The resources are never joined as though a review belonged
to a particular plot, because the review data contain no movie identifier.
This separation prevents a convenient but unsupported film–review mapping from
entering the experiment.

The methodology also enforces three data walls. Gold-300 is reserved for
evaluation; R1 supplies the retrieval index and Verifier-A; R2 supplies
Verifier-B. R2 cannot enter retrieval, and Verifier-B cannot enter generation.
These restrictions are methodological controls rather than implementation
details: without them, the later verifier-divergence analysis would compare an
evaluator with a system that had already optimized against it.

## 3.2 Primary review corpus and read-only audit

The primary corpus was obtained from version 3 of the Mendeley Data resource
*Raw Bangla Movie Review Comment Dataset for Sentiment Analysis and Natural
Language Processing* [@b4]. The
source is the `Sheet1` worksheet of `Raw Bangla Movie Review Comment Dataset for
Sentiment Analysis and Natural Language Processing.xlsx`. Its byte identity is
fixed by SHA-256
`8f972734fc3629427cdf8d01716aa817f7b325410b2fdd0f26cbc2e68506db9f`
and a size of 195,186 bytes. The hash matters because each stable `review_id` is
derived from the row position in this exact workbook; a reordered replacement
would silently change what every downstream ID denotes.

The workbook contains 5,000 rows and two columns, `Movie Review` and
`Sentiment`. It contains neither a movie-title column nor a row-level source
field. Consequently, the reviews cannot be mapped to films and a held-out-film
split is impossible. The collector recalled gathering organic comments from
multiple places but retained no collection log. That recollection and the
observed source discontinuity described in Section 3.5 cannot be reconciled;
the thesis therefore reports a Mendeley-hosted Bangla review corpus with
unrecoverable underlying row-level provenance, not a verified sample of
organic Bangla audience opinion.

The raw sentiment class counts are 1,665, 1,664, and 1,670, with one row lacking
a sentiment label. A read-only audit reproduced eight of eleven pipeline claims
and corrected three: there are two rows containing a null field rather than
one, 206 normalized duplicate occurrences rather than 205, and naive
subtraction had double-counted overlaps among null, duplicate and short-review
filters. Median length is eight whitespace-delimited words; there are no
detected URL/mention rows and no emoji rows under the registered measurement.

Cleaning preserves Bangla characters. It removes two null rows, normalizes only
whitespace, removes 205 exact duplicate occurrences plus one additional
normalized duplicate, and removes 62 remaining texts shorter than three words.
The resulting `bn_clean.csv` contains 4,730 reviews with class counts
1,513/1,599/1,618. No stemming, stopword removal, or TF–IDF transformation is
used.

Throughout this chapter, the adjusted Rand index (ARI) measures agreement
between partitions, while area under the receiver-operating-characteristic
curve (AUC) measures how strongly a scalar diagnostic recovers a binary label.

**Table 3.1. Corpus audit, cleaning, partition and source-confound facts**

| Stage or diagnostic | Verified value | Scientific consequence |
|---|---:|---|
| Raw workbook | 5,000 rows; sentiment 1,665/1,664/1,670 | Starting corpus; no movie-title or source column |
| Raw audit | 2 null rows; 206 normalized duplicate occurrences; median 8 words | Corrects the original pipeline claims and avoids overlap double-counting |
| Cleaned corpus | 4,730 rows; sentiment 1,513/1,599/1,618 | Whitespace-only normalization; no stemming, stopword removal or main-pipeline TF–IDF |
| Near-duplicate-controlled split surface | 4,625 rows | Frozen surface used by Gold/R1/R2 assignment |
| Gold-300 | 300 rows | Evaluation-only; absent from training, RAG, prompts and threshold fitting |
| R1 / R2 | 2,162 / 2,163 rows | RAG and Verifier-A use R1; outcome-only Verifier-B trains on R2 |
| Full-corpus ARI: region / sentiment | 0.4813 / 0.1793 | Apparent full-corpus clusters primarily recover corpus source |
| Binary source recovery | 93.3% accuracy; ARI 0.7487; φ 0.861 | Full-corpus partition rejected as an audience-persona result |

## 3.3 Cleaning and frozen data partition

After rule-based cleaning, near-duplicate handling uses LaBSE cosine similarity
at the preregistered 0.95
threshold and produces a 4,625-row deduplicated surface for the frozen split.
The threshold removes 105 rows and is retained despite the reported 0.90/0.98
sensitivity results; it is not retuned after observing clustering. The frozen
`split_map_v1.json` assigns Gold-300 = 300, R1 = 2,162, and R2 = 2,163.
A registered 200-row development subset is drawn from within R1; it is not a
fourth disjoint top-level partition. Thus R1 remains 2,162 in the frozen split,
while 1,962 denotes its non-development remainder. The three top-level parts
have zero overlap. The split is stratified on sentiment and corpus region and
matches the corpus within 0.1 percentage points on both variables. Gold-300 is
evaluation-only; it never enters training, retrieval, prompts or threshold
tuning. The RAG index uses R1 only, and Verifier-B is trained only from R2.

## 3.4 Plot corpus and experimental stimuli

The secondary corpus serves a different function: generation stimuli come from
Bangla Wikipedia film articles rather than from the review corpus. A
category-based MediaWiki-API harvester
discovered 3,135 candidate articles and extracted plot-like sections under a
mechanical quality gate: Bangla script, at least 120 characters, and 3–12
sentences, with longer sections truncated only at sentence boundaries. Of the
candidates, 124 passed the mechanical gate; 3,011 were rejected, primarily
because 2,925 had no plot section. The mechanical survivors were then read to
remove production-history or non-film pages that could pass surface checks.

The resulting `plots_bn.csv` is frozen at 120 synopses. A one-time seed-42 split
assigns 30 development plots and 90 evaluation plots. Development plots support
prompt, weight and threshold work; the 90 evaluation plots define the frozen
Phase-5 surface. All 120 rows carry source URL, Wikipedia revision ID and
timestamp, and CC BY-SA 4.0 licence metadata. The plot corpus is committed so
the exact stimuli cannot drift between development and evaluation. Plot text is
generation input only: it is never inserted into review clustering or verifier
training. Appendix D attributes every retained article and exact revision and
records the 2026-07-31 harvest date.

## 3.5 Why full-corpus clusters were rejected

The first LaBSE/K-means analysis used contextual sentence embeddings [@b3].
K-means candidates are fitted in the original embedding space; Uniform Manifold
Approximation and Projection (UMAP) is never a
clustering space. Near-duplicate sensitivity is reported at thresholds 0.90,
0.95 and 0.98 rather than used to choose the most favorable result. The frozen
0.95 analysis produced ARI 0.1793 with sentiment. A subsequent
source audit found that the workbook combines two stylistically different
corpora and that 60% of rows carry a uniform non-organic signature. Cluster
membership associates much more strongly with corpus region than sentiment:
ARI(region) = 0.4813 versus ARI(sentiment) = 0.1793. In a binary recast, the
partition identifies corpus source with 93.3% accuracy (ARI 0.7487, phi 0.861).
The full-corpus clusters are therefore a corpus detector and are not used as
personas.

The original collection provenance cannot be reconstructed: the collector
reported that reviews came organically from many sources but retained no
row-level source metadata. This limitation is reported rather than resolved by
guessing.

## 3.6 Region-A construct discovery and negative control

Analysis continued on the organic region-A subset (n=1,897). K=2 is the only
candidate from K=2–8 that clears the preregistered prediction-strength threshold
[@b38] (0.860; K=3 = 0.669), and its adjusted-Rand stability [@b39] is
0.940 ± 0.029 under bootstrap resampling. Stability alone,
however, is not evidence of natural groups. Silhouette peaks at only 0.053, the
gap statistic [@b40] rises monotonically and selects no K, and Hierarchical
Density-Based Spatial Clustering of Applications with Noise (HDBSCAN), using
the hierarchical density formulation and its software implementation
[@b41; @b42],
labels 100% of points as noise. The silhouette criterion follows Rousseeuw
[@b43]. The defensible interpretation is a reproducible bisection of a
continuum.

The K=2 cut is moderately length-confounded: length AUC is 0.6764. Cluster 1 is
approximately 33% shorter but about 18% richer in word types at a matched token
budget, suggesting a contrast between formulaic reaction and concise specific
engagement. A preregistered residual analysis finds a +9.80 percentage-point
lift after accounting for sentiment and length, classified as
`RESIDUAL_SURVIVES`, but only 0.2 points from its cutoff. Length adds only 0.53
points after sentiment is known, and the richness inversion holds in all four
sentiment/length bands. These are weak supporting signals, not evidence of two
discrete populations.

Region B functions as a negative control. Its K=2 solution is stable
(prediction strength 0.818; bootstrap ARI 0.962) but does not reproduce the
Region-A signature: length AUC is 0.550, the richness inversion appears in only
one of four bands, silhouette is 0.039, and 96.7% of observations are HDBSCAN
noise. Stability can therefore pass on a contentless geometric cut.

**Table 3.2. Region-A axis evidence and Region-B negative control**

| Diagnostic | Region A | Region B | Interpretation |
|---|---:|---:|---|
| n | 1,897 | 2,833 | Separate corpus regions, not interchangeable replications |
| Selected K | 2 | 2 | Algorithmic bisections only |
| Prediction strength | 0.860 | 0.818 | Both clear the registered 0.80 stability threshold |
| Bootstrap ARI | 0.940 ± 0.029 | 0.962 | Both appear highly stable |
| Silhouette | 0.053 | 0.039 | Very weak separation in both regions |
| Gap statistic | No K selected | No supporting K | No positive clusterability evidence |
| HDBSCAN noise | 100% | 96.7% | Density-based structure is absent/negligible |
| Length AUC | 0.6764 | 0.550 | Region-A cut is length-confounded; signature does not replicate |
| Richness inversion across bands | 4/4 | 1/4 | Region-A content profile fails replication in Region B |
| Final standing | Reproducible continuum cut | Stable-looking negative control | Stability is necessary, not sufficient, for validity |

## 3.7 Human validation attempt 1: ordinal ratings

The first instrument used Gold-300 and asked two annotators to assign a 0–3
engagement-specificity rating. Of 600 possible item ratings, 598 were returned.
The instrument failed its preregistered reliability gate: ordinal Krippendorff
alpha [@b31] was 0.4970, below 0.667. Exact agreement was 75.5% and within-one
agreement 98.7%, but 68% and 76% of the annotators' ratings collapsed onto the
single value 2. Gate 2 was therefore not computed. Gwet AC1 = 0.871 is not used
as rescue evidence: AC1 was designed for high-agreement/prevalence settings
[@b44], but subsequent analysis shows that it is not a substitute for kappa and
can rise mechanically with prevalence skew [@b45]. The registered
outcome is `UNRELIABLE`: the instrument is inconclusive, not evidence that the
construct itself is absent.

## 3.8 Human validation attempt 2: comparative judgments

The second instrument replaced ratings with comparative intrusion judgments,
following the reliability motivation for comparative annotation [@b29]. It
used fresh Region-A R1 material and excluded every Gold-300 item, so the failed
instrument was not silently recycled. Each four-item set was length-matched
within two words, and annotators were not told a verbal construct label. The
two annotators achieved 39/50 = 0.780 and 42/50 = 0.840 against 0.25 chance,
both with p < 1×10⁻¹⁵. In a separate direction test, both achieved 34/40 =
0.850 against 0.50 chance. A length-only heuristic scored 0.16, below chance.
The preregistered `HUMANLY_PERCEPTIBLE` outcome therefore fires.

This study establishes that humans can perceive the cut and that its direction
is engagement specificity. It does not convert the continuous geometry into
discrete audience types. The operational labels used downstream are therefore
**Level 0** and **Level 1**, not persona identities.

**Table 3.3. Human validation of the engagement-specificity construct**

| Instrument | Sample/task | Reliability or performance | Confound check | Registered standing |
|---|---|---|---|---|
| Attempt 1: 0–3 ordinal rating | Gold-300; 598/600 ratings from two annotators | Ordinal α=0.4970; exact agreement 75.5%; within-one 98.7% | Ratings collapsed at value 2 (68%/76%); Gate 2 not run | `UNRELIABLE`; inconclusive, not negative |
| Attempt 2: four-way intrusion | 50 length-matched sets per annotator | 39/50=0.780 and 42/50=0.840 vs 0.25 chance; both p<1×10⁻¹⁵ | Maximum two-word span; length-only heuristic=0.16 | `HUMANLY_PERCEPTIBLE` |
| Attempt 2: direction check | 40 judgments per annotator | Both 34/40=0.850 vs 0.50 chance | Construct label withheld during intrusion task | Direction identified as engagement specificity |

## 3.9 Operational definition of the axis

Level 0 is a general or formulaic response that may mention a film element but
does not develop a specific observation. Level 1 engages with a particular
aspect, event, relation, or construction element. Praise, criticism, emotional
intensity, and length can occur at either level. The definition is prototype-
based and includes a comparative swap test because the human evidence validates
a relative distinction, not an absolute checklist.

The two directions are checked against data: Level 1 averages 8.85 words and
414 types per 1,000 tokens, while Level 0 averages 13.12 words and 269 types per
1,000. The unintuitive shorter-but-richer direction is kept; it is not rewritten
to match expectations.

## 3.10 Chapter summary

The methodology does not support discovered audience personas. It supports a
human-recognizable engagement-specificity cut obtained only after rejecting a
source-confounded full-corpus partition and documenting weak clusterability,
length association, a failed rating-scale instrument, and a successful
comparative task on fresh data. This bounded construct—not sentiment, length,
or an assumed audience type—is the target used by the verifiers and generation
experiments developed in the following chapters.
