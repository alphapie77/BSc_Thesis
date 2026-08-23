# Chapter 3 — Data and Engagement-Specificity Axis

## 3.1 Raw corpus and audit

The raw Bangla sentiment workbook contains 5,000 rows and two columns: review
text and sentiment. The class counts are 1,665, 1,664, and 1,670. A read-only
audit reproduced eight of eleven pipeline claims and corrected three: there are
two null rows rather than one, 206 normalized duplicate occurrences rather than
205, and naive subtraction had double-counted overlaps among null, duplicate,
and short-review filters. Median length is eight whitespace-delimited words;
there are no detected URL/mention rows and no emoji rows under the registered
measurement.

Cleaning preserves Bangla characters. It removes two null rows, normalizes only
whitespace, removes 205 exact duplicate occurrences plus one additional
normalized duplicate, and removes 62 remaining texts shorter than three words.
The resulting `bn_clean.csv` contains 4,730 reviews with class counts
1,513/1,599/1,618. No stemming, stopword removal, or TF–IDF transformation is
used.

## 3.2 Frozen data partition

Near-duplicate handling produces a 4,625-row deduplicated surface for the frozen
split. `split_map_v1.json` assigns Gold-300 = 300, R1 = 2,162, and R2 = 2,163;
a registered 200-row development surface is drawn within that contract rather
than added as a fourth disjoint partition. The three top-level parts have zero overlap. The split is stratified on
sentiment and corpus region and matches the corpus within 0.1 percentage points
on both variables. Gold-300 is evaluation-only; it never enters training,
retrieval, prompts, or threshold tuning. The RAG index uses R1 only.

## 3.3 Why full-corpus clusters were rejected

The first LaBSE/K-means analysis produced ARI 0.1793 with sentiment. A subsequent
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

## 3.4 Region-A clusterability

Analysis continued on the organic region-A subset (n=1,897). K=2 is the only
candidate from K=2–8 that clears the preregistered prediction-strength threshold
(0.860; K=3 = 0.669), and its bootstrap ARI is 0.940 ± 0.029. Stability alone,
however, is not evidence of natural groups. Silhouette peaks at only 0.053, the
gap statistic rises monotonically and selects no K, and HDBSCAN labels 100% of
points as noise. The defensible interpretation is a reproducible bisection of a
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

## 3.5 Human validation attempt 1

The first Gold-300 instrument used a 0–3 ordinal engagement-specificity rating.
It failed its preregistered reliability gate: ordinal Krippendorff alpha was
0.4970, below 0.667. Exact agreement was 75.5% and within-one agreement 98.7%,
but 68% and 76% of the two annotators' ratings collapsed onto the single value
2. Gate 2 was not computed. Gwet AC1 = 0.871 is not used as rescue evidence
because prevalence skew can inflate it. The outcome is `UNRELIABLE` and
inconclusive, not a negative finding about the construct.

## 3.6 Comparative validation attempt 2

The second instrument replaced ratings with comparative intrusion judgments.
Every set was length-matched within two words, and annotators were not told a
verbal construct label. The two annotators achieved 39/50 = 0.780 and 42/50 =
0.840 against 0.25 chance, both with p < 1e-15. In a separate direction test,
both achieved 34/40 = 0.850 against 0.50 chance. A length-only heuristic scored
0.16, below chance. The preregistered `HUMANLY_PERCEPTIBLE` outcome therefore
fires.

This study establishes that humans can perceive the cut and that its direction
is engagement specificity. It does not convert the continuous geometry into
discrete audience types. The operational labels used downstream are therefore
**Level 0** and **Level 1**, not persona identities.

## 3.7 Operational definition

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

## 3.8 Chapter summary

The data do not support discovered audience personas. They support a
human-recognizable engagement-specificity axis cut obtained after rejecting a
source-confounded full-corpus partition and documenting weak clusterability,
length association, failed rating-scale validation, and a successful
comparative task. This bounded construct is the target used by the verifiers and
generation experiments.
