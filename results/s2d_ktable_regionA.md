# S2d — Gate G1: the master K-table (region A)

> **Interpretation was pre-registered in `docs/protocol.md` (RQ1-C) before this
> table existed.** Read that section before reading these numbers. The
> three-persona design is the hypothesis; this is the test.

- **Config:** `configs/s2d_ktable.yaml` · **n:** 1897 (region A, post-dedup)
- **Generated (UTC):** 2026-08-03T11:10:12.862436+00:00 · **Commit:** `cf8d5cfc191d60c972ba14fe4815b818627794aa-dirty`
- **Seed:** 42 · K range: [2, 3, 4, 5, 6, 7, 8]

## Verdict

**Selected K = 2** — the largest K with prediction
strength ≥ 0.8 (PS = 0.860), per pipeline §2.2.
Bootstrap ARI 0.940 ± 0.029.
Trap-check at this K: **NOT_SENTIMENT_ALIGNED**
(ARI vs Sentiment = 0.1522).

⚠️ **K = 2 means the three-persona design gives way.** Region A has two sentiment classes, so the obvious worry is that these clusters *are* the sentiment split — the `ari_vs_sentiment` column settles that and is reported either way. K=3 is retained as the theory-motivated secondary (pipeline §2.2).

## The full table — reported whole, no cherry-picking

|   K |   silhouette |   calinski_harabasz |   davies_bouldin |    gap |   gap_se |   prediction_strength |   bootstrap_ari_mean |   bootstrap_ari_sd |       gmm_bic |   ari_vs_sentiment |   min_cluster_share |   max_cluster_share | trap_band             |
|----:|-------------:|--------------------:|-----------------:|-------:|---------:|----------------------:|---------------------:|-------------------:|--------------:|-------------------:|--------------------:|--------------------:|:----------------------|
|   2 |       0.0534 |             74.4684 |           4.9794 | 0.9498 |   0.0008 |                0.8605 |               0.9399 |             0.0290 | -6125017.4708 |             0.1522 |              0.3975 |              0.6025 | NOT_SENTIMENT_ALIGNED |
|   3 |       0.0146 |             58.9775 |           4.9471 | 0.9700 |   0.0006 |                0.6692 |               0.9094 |             0.0454 | -6152251.8359 |             0.1804 |              0.2952 |              0.3890 | NOT_SENTIMENT_ALIGNED |
|   4 |       0.0112 |             50.4167 |           4.7551 | 0.9857 |   0.0007 |                0.4153 |               0.5305 |             0.1782 | -6167742.7507 |             0.1274 |              0.1877 |              0.3411 | NOT_SENTIMENT_ALIGNED |
|   5 |       0.0182 |             45.7785 |           4.5739 | 0.9986 |   0.0008 |                0.3749 |               0.6466 |             0.2134 | -6182903.5564 |             0.1148 |              0.1249 |              0.2578 | NOT_SENTIMENT_ALIGNED |
|   6 |       0.0117 |             42.3962 |           4.3855 | 1.0122 |   0.0010 |                0.3637 |               0.6715 |             0.1616 | -6197719.0145 |             0.0848 |              0.1112 |              0.2409 | NOT_SENTIMENT_ALIGNED |
|   7 |       0.0172 |             39.7588 |           4.2488 | 1.0224 |   0.0007 |                0.3542 |               0.7548 |             0.0972 | -6201327.2798 |             0.0835 |              0.0917 |              0.1950 | NOT_SENTIMENT_ALIGNED |
|   8 |       0.0103 |             36.9494 |           4.0410 | 1.0323 |   0.0008 |                0.3145 |               0.6417 |             0.0980 | -6210424.6437 |             0.0733 |              0.0865 |              0.1581 | NOT_SENTIMENT_ALIGNED |

**How to read it.** `prediction_strength` is the decision variable; everything
else is context. `bootstrap_ari_mean` is stability (pipeline §2.2: **stability
beats compactness**). `silhouette` and `davies_bouldin` measure compactness and
will often disagree with stability — that disagreement is expected and is
reported rather than resolved by preference. `trap_band` applies the same RQ1
bands at every K: **a K can be perfectly stable and still be a rediscovery of
the sentiment split**, which is why both columns are here.

## HDBSCAN — an independent opinion on K

- **k_found**: 0
- **noise_fraction**: 1.0
- **ari_vs_sentiment**: 0.0

HDBSCAN chooses its own K and is allowed to call points noise. If it lands near
the selected K, that is strong independent evidence. A large noise fraction is
itself a finding: it would mean a substantial part of the corpus belongs to no
persona at all.

## What this step does NOT settle

Stability is not validity. A stable K means the partition is reproducible, not
that its groups are **audience personas**. That question is G-300's, with three
annotators and κ/α, and nothing in this table can pre-empt it.
