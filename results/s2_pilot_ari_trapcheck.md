# S2 Pilot — near-duplicate removal and the ARI trap-check

**Pilot, not a frozen result. This step writes no split map.**
`data/splits/split_map_v1.json` is created in a later step, deliberately after
this outcome is on record so the split cannot be tuned to it.

- **Config:** `configs/s2_pilot.yaml`
- **Input:** `data/cleaned/bn_clean.csv` (4730 rows, `n_after_rule_based_cleaning`)
- **Embeddings:** `sentence-transformers/LaBSE`, L2-normalized, max_seq_length
  64
- **Clustering:** K-Means K=3,
  n_init=10,
  random_state=42, in LaBSE space (rule 9: UMAP
  is visualization-only and is not used here)
- **Seed:** 42
- **Generated (UTC):** 2026-08-03T10:55:16.764695+00:00
- **Git commit:** `cf8d5cfc191d60c972ba14fe4815b818627794aa`

## Trap-check result at the primary threshold (0.95)

| Quantity | Value |
|---|---|
| near-duplicate pairs at ≥ 0.95 | 119 |
| rows removed as near-duplicates | 105 |
| **surviving n** | **4625** |
| cluster sizes | 0:1814 / 1:1427 / 2:1384 |
| **ARI(cluster, Sentiment)** | **0.1793** |
| chi2 (df 4) | 1558.05 (p = 0) |
| Cramér's V | 0.4104 |
| **Pre-registered band** | **Band 1** (protocol.md RQ1) |
| **Verdict** | **NOT_SENTIMENT_ALIGNED** |

**NOT_SENTIMENT_ALIGNED (Band 1).** ARI 0.1793 < 0.2: the clusters are not aligned with the sentiment axis. **This is not evidence that the personas are valid** — only that they are not a sentiment rediscovery. G-300 human validation remains the arbiter (protocol.md RQ1, Band 1).

### Cluster × region — is this sentiment, or file of origin?

`results/s2c_region_split.md` established that the source `.xlsx` is two corpora
joined at raw row 1999, with sharply different register on either side. If the
encoder is separating those two corpora rather than anything about audiences,
this table is where it shows.

| Cluster | A_organic | B_uniform | Row total |
|---|---|---|---|
| 0 | 1700 | 114 | 1814 |
| 1 | 119 | 1308 | 1427 |
| 2 | 78 | 1306 | 1384 |

| Scored against | ARI |
|---|---|
| `Sentiment` | 0.1793 |
| **`region`** | **0.4813** |
| `Sentiment`, before dedup | 0.1792 |
| `region`, before dedup | 0.4790 |

**ARI(cluster, region) = 0.4813 EXCEEDS ARI(cluster, Sentiment) = 0.1793.** The clustering agrees more with which half of the source file a review came from than with what the review says. Any persona reading of these clusters is unsupported until the corpus is restricted to one region: the structure being recovered is provenance.


### Cluster degeneracy check

**Not degenerate.** Cluster shares (cluster 0: 39.2%, cluster 1: 30.9%, cluster 2: 29.9%) are all within the 5%–70% band, so the K-Means solution is interpretable and the ARI below is meaningful.

### Cluster × Sentiment crosstab (primary threshold)

| Cluster | Sentiment 0 | Sentiment 1 | Sentiment 2 | Row total |
|---|---|---|---|---|
| 0 | 823 | 979 | 12 | 1814 |
| 1 | 412 | 318 | 697 | 1427 |
| 2 | 249 | 272 | 863 | 1384 |
| **Total** | **1484** | **1569** | **1572** | **4625** |

χ² = 1558.05 on 4 df, p = 0;
**Cramér's V = 0.4104**.

Read these two together with ARI, not instead of it. χ² only tests whether the
clusters are *associated* with sentiment at all — at n ≈ 4625 it will
reach significance on associations far too weak to matter, so its p-value is
close to useless here. Cramér's V gives the association's strength on a 0–1
scale, and ARI gives agreement corrected for chance. A high V with a low ARI
means the clusters lean on sentiment without reproducing its partition — that
combination is a caveat, not a pass.

## Does near-duplicate removal itself move the trap-check?

Near-duplicates create tight artificial groups that K-Means can latch onto, so
the trap-check is reported both before and after removal. If ARI shifts
materially, the dedup threshold is doing real work on the headline number and
must be reported as such rather than treated as housekeeping.

| Stage | n | ARI | Cramér's V | Degenerate? |
|---|---|---|---|---|
| **Before dedup** (all rows) | 4730 | 0.1792 | 0.4111 | no |
| **After dedup** (t = 0.95) | 4625 | 0.1793 | 0.4104 | no |
| **Δ (after − before)** | -105 | +0.0001 | -0.0007 | — |

## Off-diagonal cosine distribution

All 11,184,085 distinct pairs (strict upper triangle),
accumulated as a histogram during the same blocked matmul — the full n × n
matrix is never materialised. Percentiles are estimated from that histogram
(bin width 1e-04, interpolated within the containing bin), so
they carry a resolution limit of roughly one bin width in the dense middle of
the distribution; in the sparse upper tail the limit is instead the gap between
neighbouring pair values, which can exceed a bin width. The **maximum is exact**
— it is tracked directly, not read off the histogram — and the threshold sweep
below uses exact cosines throughout, so no removal decision depends on these
estimates.

| Statistic | Cosine |
|---|---|
| 50th percentile (median) | 0.3511 |
| 90th percentile | 0.5224 |
| 95th percentile | 0.5678 |
| 99th percentile | 0.6529 |
| 99.9th percentile | 0.7561 |
| **maximum** | **0.999758** |

This is the context the thresholds are chosen against. If the 99.9th percentile
already sits above a swept threshold, that threshold is cutting into the bulk of
the distribution rather than trimming a duplicate tail — it is then removing
merely *similar* short reviews, not duplicates, and the choice needs defending.
With a median of 8 words, high baseline cosine between unrelated reviews is
expected, so this table must be checked before the primary threshold is trusted.

## Sensitivity to the near-duplicate threshold

The threshold is a judgement call, so it is reported as a curve rather than a
single number. If the verdict column is not constant across these rows, the
trap-check conclusion depends on an arbitrary choice and must be reported that
way.

| Threshold | Pairs ≥ t | Rows removed | Surviving n | ARI | ΔARI vs no-dedup | Cramér's V | Degenerate | Verdict |
|---|---|---|---|---|---|---|---|---|
| — (no dedup) | — | 0 | 4730 | 0.1792 | — | 0.4111 | no | Band 1 · NOT_SENTIMENT_ALIGNED |
| 0.90 | 449 | 325 | 4405 | 0.2181 | +0.0388 | 0.4766 | no | Band 2 · PARTIAL_OVERLAP + RESIDUAL_TEST_REQUIRED |
| 0.95 **(primary)** | 119 | 105 | 4625 | 0.1793 | +0.0001 | 0.4104 | no | Band 1 · NOT_SENTIMENT_ALIGNED |
| 0.98 | 39 | 38 | 4692 | 0.1784 | -0.0008 | 0.4100 | no | Band 1 · NOT_SENTIMENT_ALIGNED |

## Method notes

- **Pair enumeration** — full pairwise cosine over L2-normalized embeddings
  (cosine = dot product), strict upper triangle only, computed in row blocks to
  bound memory. No approximate neighbour search, so no recall loss.
- **Which row survives** — rows are sorted by `review_id` and a row `j` is
  removed only when it is ≥ threshold to an already-**kept** row `i < j`. The
  lowest `review_id` in a near-duplicate cluster therefore always survives
  (`keep: first_by_review_id`). Comparing against kept rows only
  stops a removed row from evicting a third row, which would delete more than
  intended in transitive chains.
- **Every pair is logged** — `data/cleaned/near_dup_pairs.csv` lists all pairs at or above the
  lowest swept threshold, with the cosine, which thresholds each pair is above,
  whether the higher-id row was removed at the primary threshold, and both
  review texts so the removals can be eyeballed.
- **ARI is computed on survivors** at each threshold, against the `Sentiment`
  column of the surviving rows.
- Class balance after S1 is **not** uniform (1513/1599/1618); see
  `docs/dataset_card.md`. ARI is chance-corrected, so this does not bias it.
