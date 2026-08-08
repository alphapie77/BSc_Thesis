# S2d — Gate G1: the master K-table (region A)

> **Interpretation was pre-registered in `docs/protocol.md` (RQ1-C) before this
> table existed.** Read that section before reading these numbers. The
> three-persona design is the hypothesis; this is the test.

- **Config:** `configs/s2d_ktable_regionB.yaml` · **n:** 2728 (region A, post-dedup)
- **Generated (UTC):** 2026-08-08T14:32:10.900906+00:00 · **Commit:** `833d57b40365d65cf6dfa67cfbd46a6bfa7454d1`
- **Seed:** 42 · K range: [2, 3, 4, 5, 6, 7, 8]

## Verdict

**Selected K = 2** — the largest K with prediction
strength ≥ 0.8 (PS = 0.818), per pipeline §2.2.
Bootstrap ARI 0.962 ± 0.036.
Trap-check at this K: **NOT_SENTIMENT_ALIGNED**
(ARI vs Sentiment = 0.0107).

⚠️ **K = 2 means the three-persona design gives way.** Region A has two sentiment classes, so the obvious worry is that these clusters *are* the sentiment split — the `ari_vs_sentiment` column settles that and is reported either way. K=3 is retained as the theory-motivated secondary (pipeline §2.2).

## The full table — reported whole, no cherry-picking

|   K |   silhouette |   calinski_harabasz |   davies_bouldin |    gap |   gap_se |   prediction_strength |   bootstrap_ari_mean |   bootstrap_ari_sd |       gmm_bic |   ari_vs_sentiment |   min_cluster_share |   max_cluster_share | trap_band             |
|----:|-------------:|--------------------:|-----------------:|-------:|---------:|----------------------:|---------------------:|-------------------:|--------------:|-------------------:|--------------------:|--------------------:|:----------------------|
|   2 |       0.0394 |            107.8235 |           5.0031 | 0.8907 |   0.0006 |                0.8183 |               0.9624 |             0.0362 | -9361769.1647 |             0.0107 |              0.4941 |              0.5059 | NOT_SENTIMENT_ALIGNED |
|   3 |       0.0329 |             90.7379 |           4.6003 | 0.9152 |   0.0007 |                0.6589 |               0.8808 |             0.2426 | -9416387.6968 |             0.0172 |              0.2544 |              0.4450 | NOT_SENTIMENT_ALIGNED |
|   4 |       0.0285 |             80.5277 |           4.4073 | 0.9342 |   0.0005 |                0.6709 |               0.9065 |             0.1088 | -9455950.8118 |             0.0550 |              0.2302 |              0.2812 | NOT_SENTIMENT_ALIGNED |
|   5 |       0.0280 |             73.0999 |           4.1170 | 0.9508 |   0.0006 |                0.4306 |               0.7388 |             0.1910 | -9492659.0597 |             0.0702 |              0.1767 |              0.2390 | NOT_SENTIMENT_ALIGNED |
|   6 |       0.0299 |             67.5931 |           4.0312 | 0.9627 |   0.0006 |                0.4400 |               0.8152 |             0.1476 | -9523537.0611 |             0.0683 |              0.1147 |              0.2071 | NOT_SENTIMENT_ALIGNED |
|   7 |       0.0247 |             62.7290 |           3.9235 | 0.9760 |   0.0006 |                0.3697 |               0.7037 |             0.1535 | -9538495.1612 |             0.0510 |              0.1004 |              0.1891 | NOT_SENTIMENT_ALIGNED |
|   8 |       0.0273 |             58.1784 |           3.8265 | 0.9854 |   0.0006 |                0.3122 |               0.6651 |             0.1050 | -9553319.0175 |             0.0419 |              0.0620 |              0.1782 | NOT_SENTIMENT_ALIGNED |

**How to read it.** `prediction_strength` is the decision variable; everything
else is context. `bootstrap_ari_mean` is stability (pipeline §2.2: **stability
beats compactness**). `silhouette` and `davies_bouldin` measure compactness and
will often disagree with stability — that disagreement is expected and is
reported rather than resolved by preference. `trap_band` applies the same RQ1
bands at every K: **a K can be perfectly stable and still be a rediscovery of
the sentiment split**, which is why both columns are here.

## HDBSCAN — an independent opinion on K

- **k_found**: 2
- **noise_fraction**: 0.966642228739003
- **ari_vs_sentiment**: -0.029440014311516428

HDBSCAN chooses its own K and is allowed to call points noise. If it lands near
the selected K, that is strong independent evidence. A large noise fraction is
itself a finding: it would mean a substantial part of the corpus belongs to no
persona at all.

## What this step does NOT settle

Stability is not validity. A stable K means the partition is reproducible, not
that its groups are **audience personas**. That question is G-300's, with three
annotators and κ/α, and nothing in this table can pre-empt it.
