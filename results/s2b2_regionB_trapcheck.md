# S2 Pilot — near-duplicate removal and the ARI trap-check

**Pilot, not a frozen result. This step writes no split map.**
`data/splits/split_map_v1.json` is created in a later step, deliberately after
this outcome is on record so the split cannot be tuned to it.

- **Config:** `configs/s2_pilot_regionB.yaml`
- **Input:** `data/cleaned/bn_clean.csv` (2820 rows, `n_after_rule_based_cleaning`)
- **Embeddings:** `sentence-transformers/LaBSE`, L2-normalized, max_seq_length
  64
- **Clustering:** K-Means K=3,
  n_init=10,
  random_state=42, in LaBSE space (rule 9: UMAP
  is visualization-only and is not used here)
- **Seed:** 42
- **Generated (UTC):** 2026-08-08T14:09:21.892447+00:00
- **Git commit:** `833d57b40365d65cf6dfa67cfbd46a6bfa7454d1`

## Trap-check result at the primary threshold (0.95)

| Quantity | Value |
|---|---|
| near-duplicate pairs at ≥ 0.95 | 106 |
| rows removed as near-duplicates | 92 |
| **surviving n** | **2728** |
| cluster sizes | 0:820 / 1:1214 / 2:694 |
| **ARI(cluster, Sentiment)** | **0.0172** |
| chi2 (df 4) | 69.86 (p = 2.43e-14) |
| Cramér's V | 0.1132 |
| **Pre-registered band** | **Band 1** (protocol.md RQ1) |
| **Verdict** | **NOT_SENTIMENT_ALIGNED** |

**NOT_SENTIMENT_ALIGNED (Band 1).** ARI 0.0172 < 0.2: the clusters are not aligned with the sentiment axis. **This is not evidence that the personas are valid** — only that they are not a sentiment rediscovery. G-300 human validation remains the arbiter (protocol.md RQ1, Band 1).

### Cluster × region

_Not scored: this run covers a single region, so there is nothing to separate._

### Cluster degeneracy check

**Not degenerate.** Cluster shares (cluster 0: 30.1%, cluster 1: 44.5%, cluster 2: 25.4%) are all within the 5%–70% band, so the K-Means solution is interpretable and the ARI below is meaningful.

### Cluster × Sentiment crosstab (primary threshold)

| Cluster | Sentiment 0 | Sentiment 1 | Sentiment 2 | Row total |
|---|---|---|---|---|
| 0 | 239 | 176 | 405 | 820 |
| 1 | 176 | 288 | 750 | 1214 |
| 2 | 125 | 152 | 417 | 694 |
| **Total** | **540** | **616** | **1572** | **2728** |

χ² = 69.86 on 4 df, p = 2.43e-14;
**Cramér's V = 0.1132**.

Read these two together with ARI, not instead of it. χ² only tests whether the
clusters are *associated* with sentiment at all — at n ≈ 2728 it will
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
| **Before dedup** (all rows) | 2820 | 0.0170 | 0.1108 | no |
| **After dedup** (t = 0.95) | 2728 | 0.0172 | 0.1132 | no |
| **Δ (after − before)** | -92 | +0.0002 | +0.0024 | — |

## Off-diagonal cosine distribution

All 3,974,790 distinct pairs (strict upper triangle),
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
| 50th percentile (median) | 0.4448 |
| 90th percentile | 0.5786 |
| 95th percentile | 0.6172 |
| 99th percentile | 0.6940 |
| 99.9th percentile | 0.7937 |
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
| — (no dedup) | — | 0 | 2820 | 0.0170 | — | 0.1108 | no | Band 1 · NOT_SENTIMENT_ALIGNED |
| 0.90 | 387 | 286 | 2534 | 0.0182 | +0.0012 | 0.1099 | no | Band 1 · NOT_SENTIMENT_ALIGNED |
| 0.95 **(primary)** | 106 | 92 | 2728 | 0.0172 | +0.0002 | 0.1132 | no | Band 1 · NOT_SENTIMENT_ALIGNED |
| 0.98 | 32 | 31 | 2789 | 0.0178 | +0.0008 | 0.1167 | no | Band 1 · NOT_SENTIMENT_ALIGNED |

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
- **Every pair is logged** — `data/cleaned/near_dup_pairs_regionB.csv` lists all pairs at or above the
  lowest swept threshold, with the cosine, which thresholds each pair is above,
  whether the higher-id row was removed at the primary threshold, and both
  review texts so the removals can be eyeballed.
- **ARI is computed on survivors** at each threshold, against the `Sentiment`
  column of the surviving rows.
- Class balance after S1 is **not** uniform (1513/1599/1618); see
  `docs/dataset_card.md`. ARI is chance-corrected, so this does not bias it.
