# S2 Pilot — near-duplicate removal and the ARI trap-check

**Pilot, not a frozen result. This step writes no split map.**
`data/splits/split_map_v1.json` is created in a later step, deliberately after
this outcome is on record so the split cannot be tuned to it.

- **Config:** `configs/s2_pilot_regionA.yaml`
- **Input:** `data/cleaned/bn_clean.csv` (1910 rows, `n_after_rule_based_cleaning`)
- **Embeddings:** `sentence-transformers/LaBSE`, L2-normalized, max_seq_length
  64
- **Clustering:** K-Means K=3,
  n_init=10,
  random_state=42, in LaBSE space (rule 9: UMAP
  is visualization-only and is not used here)
- **Seed:** 42
- **Generated (UTC):** 2026-08-03T10:55:44.722777+00:00
- **Git commit:** `cf8d5cfc191d60c972ba14fe4815b818627794aa-dirty`

## Trap-check result at the primary threshold (0.95)

| Quantity | Value |
|---|---|
| near-duplicate pairs at ≥ 0.95 | 13 |
| rows removed as near-duplicates | 13 |
| **surviving n** | **1897** |
| cluster sizes | 0:560 / 1:738 / 2:599 |
| **ARI(cluster, Sentiment)** | **0.1804** |
| chi2 (df 2) | 564.49 (p = 2.64e-123) |
| Cramér's V | 0.5455 |
| **Pre-registered band** | **Band 1** (protocol.md RQ1) |
| **Verdict** | **NOT_SENTIMENT_ALIGNED** |

**NOT_SENTIMENT_ALIGNED (Band 1).** ARI 0.1804 < 0.2: the clusters are not aligned with the sentiment axis. **This is not evidence that the personas are valid** — only that they are not a sentiment rediscovery. G-300 human validation remains the arbiter (protocol.md RQ1, Band 1).

### Cluster × region

_Not scored: this run covers a single region, so there is nothing to separate._

### Cluster degeneracy check

**Not degenerate.** Cluster shares (cluster 0: 29.5%, cluster 1: 38.9%, cluster 2: 31.6%) are all within the 5%–70% band, so the K-Means solution is interpretable and the ARI below is meaningful.

### Cluster × Sentiment crosstab (primary threshold)

| Cluster | Sentiment 0 | Sentiment 1 | Row total |
|---|---|---|---|
| 0 | 64 | 496 | 560 |
| 1 | 396 | 342 | 738 |
| 2 | 484 | 115 | 599 |
| **Total** | **944** | **953** | **1897** |

χ² = 564.49 on 2 df, p = 2.64e-123;
**Cramér's V = 0.5455**.

Read these two together with ARI, not instead of it. χ² only tests whether the
clusters are *associated* with sentiment at all — at n ≈ 1897 it will
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
| **Before dedup** (all rows) | 1910 | 0.1760 | 0.5395 | no |
| **After dedup** (t = 0.95) | 1897 | 0.1804 | 0.5455 | no |
| **Δ (after − before)** | -13 | +0.0044 | +0.0060 | — |

## Off-diagonal cosine distribution

All 1,823,095 distinct pairs (strict upper triangle),
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
| 50th percentile (median) | 0.2885 |
| 90th percentile | 0.4645 |
| 95th percentile | 0.5151 |
| 99th percentile | 0.6160 |
| 99.9th percentile | 0.7464 |
| **maximum** | **0.993260** |

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
| — (no dedup) | — | 0 | 1910 | 0.1760 | — | 0.5395 | no | Band 1 · NOT_SENTIMENT_ALIGNED |
| 0.90 | 61 | 38 | 1872 | 0.1826 | +0.0066 | 0.5467 | no | Band 1 · NOT_SENTIMENT_ALIGNED |
| 0.95 **(primary)** | 13 | 13 | 1897 | 0.1804 | +0.0044 | 0.5455 | no | Band 1 · NOT_SENTIMENT_ALIGNED |
| 0.98 | 7 | 7 | 1903 | 0.1777 | +0.0017 | 0.5431 | no | Band 1 · NOT_SENTIMENT_ALIGNED |

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
- **Every pair is logged** — `data/cleaned/near_dup_pairs_regionA.csv` lists all pairs at or above the
  lowest swept threshold, with the cosine, which thresholds each pair is above,
  whether the higher-id row was removed at the primary threshold, and both
  review texts so the removals can be eyeballed.
- **ARI is computed on survivors** at each threshold, against the `Sentiment`
  column of the surviving rows.
- Class balance after S1 is **not** uniform (1513/1599/1618); see
  `docs/dataset_card.md`. ARI is chance-corrected, so this does not bias it.
