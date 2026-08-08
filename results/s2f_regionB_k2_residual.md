# S2f — The residual test: is the K = 2 cut just valence and verbosity?

> **Interpretation was pre-registered in `docs/protocol.md` (RQ1-E) before this
> script existed.** Read that section first.
>
> ### Why this ran when the pre-registration did not require it
>
> RQ1 Band 2 makes a residual test mandatory at ARI ≥ 0.20. S2e reports
> **0.1522** — Band 1 — so nothing was owed. It ran anyway because ARI is the
> wrong instrument for this association, and this project has been misled by it
> once already (`s2b_register_probe.md`: φ 0.565 against V 0.410). The same 2×2
> that gives ARI 0.1522 gives **φ = 0.3981** and a 19.3-point accuracy lift.
>
> **This does not move the corpus into Band 2 and revises no band assignment.**
> It is voluntary and additional, and it is labelled that way everywhere.

- **Config:** `configs/s2f_residual_regionB.yaml` · **n:** 2728 (region A, post-dedup, K = 2)
- **Generated (UTC):** 2026-08-08T14:32:22.631074+00:00 · **Commit:** `833d57b40365d65cf6dfa67cfbd46a6bfa7454d1`
- **Seed:** 42 · Marginal cluster-1 share: **50.6%**
- **No embedding required.** This runs off S2e's assignments and the cleaned
  text. **Nothing is trained** — AUC and φ are rank/contingency statistics and
  richness is sampling at a fixed budget. Rules 7 and 10 intact.

## Verdict — Test C, the decisive one

**RESIDUAL_SURVIVES** — lift **+7.2 pp** <
10.0.

Most of the partition is explained by **neither** variable. Whatever LaBSE is
cutting on, it is not valence and not verbosity — and under RQ1-E that makes
G-300 the right place to spend, because no cheaper instrument has explained the
cut.

**This does not show the halves are personas.** It shows the two cheapest
explanations have been eliminated: a stronger position than S2e left us in, and
a weaker one than a persona claim requires.

### Which variable is actually doing the work?

"Sentiment and length together" is not a useful summary when one of them may be
doing all the work, and the joint number cannot tell you which. Same estimator,
three cell definitions:

| conditioning_on             |   accuracy_% |   lift_pp |
|:----------------------------|-------------:|----------:|
| nothing (marginal baseline) |         50.6 |       0.0 |
| Sentiment only              |         55.4 |       4.8 |
| length band only            |         54.9 |       4.3 |
| both (the 8 cells)          |         57.8 |       7.2 |

**Read the gap between the last two rows.** That is what length adds *once
sentiment is already known* — and it is the honest measure of the length
confound at the level of prediction, as opposed to the level of correlation that
S2e's `length_auc` reports.

### The number, with the caveat that must always travel with it

Cell-majority accuracy **57.8%** against a marginal baseline of
**50.6%** → lift **+7.2 pp**.

⚠️ **This is a resubstitution estimate.** Each cell's majority is read from the
same rows it is scored on, so it **overstates** how much sentiment and length
explain. That is the useful direction of error: it makes the "cheap variables
explain everything" verdict *easier* to reach, so a **low** lift is strong
evidence, while a high one is a ceiling rather than a measurement.

### The eight cells

| cell            |   n |   cluster1_share_% |   cell_majority |   deviation_from_marginal_pp |
|:----------------|----:|-------------------:|----------------:|-----------------------------:|
| S0|(10.0, 84.0] | 100 |               41.0 |               0 |                          9.6 |
| S0|(2.999, 6.0] | 190 |               33.7 |               0 |                         16.9 |
| S0|(6.0, 8.0]   | 143 |               38.5 |               0 |                         12.1 |
| S0|(8.0, 10.0]  | 107 |               41.1 |               0 |                          9.5 |
| S1|(10.0, 84.0] | 213 |               57.3 |               1 |                          6.7 |
| S1|(2.999, 6.0] | 233 |               42.1 |               0 |                          8.5 |
| S1|(6.0, 8.0]   |  94 |               46.8 |               0 |                          3.8 |
| S1|(8.0, 10.0]  |  76 |               63.2 |               1 |                         12.6 |
| S2|(10.0, 84.0] | 267 |               49.4 |               0 |                          1.1 |
| S2|(2.999, 6.0] | 342 |               47.4 |               0 |                          3.2 |
| S2|(6.0, 8.0]   | 555 |               56.9 |               1 |                          6.4 |
| S2|(8.0, 10.0]  | 408 |               62.3 |               1 |                         11.7 |

A cell share near the marginal 50.6% means that knowing a review's
sentiment and length tells you nothing about which half it landed in. Shares
near 0 or 100 mean the opposite.

## Test A — does length separate the halves *within* a sentiment class?

Directionless AUC of `n_words` against cluster, computed separately per
sentiment class. Reported figure is the **minimum**: length is only
"independent" if it works in *both* classes.

|   Sentiment |         n |   auc_length_vs_cluster |   mean_words_cluster0 |   mean_words_cluster1 |
|------------:|----------:|------------------------:|----------------------:|----------------------:|
|      0.0000 |  540.0000 |                  0.5511 |                7.6577 |                8.2745 |
|      1.0000 |  616.0000 |                  0.5770 |                9.2763 |               10.3686 |
|      2.0000 | 1572.0000 |                  0.5276 |                9.2316 |                8.7234 |

**min = 0.5276** → **ENTANGLED** — in at least one class, length does not separate the halves, so the length effect is partly carried by sentiment and must be reported as entangled rather than additive
(threshold 0.6).

## Test B — does sentiment separate the halves *within* a length band?

|φ| inside each quartile band of `n_words`. Bands are quartile-derived, not
hand-chosen; edges appear in the table. Reported figure is the **minimum**
across bands.

| length_band   |   n |   abs_phi_cluster_vs_sentiment |   cluster1_share_% |
|:--------------|----:|-------------------------------:|-------------------:|
| (2.999, 6.0]  | 765 |                         0.0857 |            42.3529 |
| (6.0, 8.0]    | 792 |                         0.0828 |            52.3990 |
| (8.0, 10.0]   | 591 |                         0.2172 |            58.5448 |
| (10.0, 84.0]  | 580 |                         0.1519 |            50.8621 |

**min = 0.0828** in band `(6.0, 8.0]` → **not independent**: in `(6.0, 8.0]` sentiment does not separate the halves. Named rather than averaged away
(threshold 0.2).

## Test D — does the lexical-richness inversion survive a length control?

S2e found cluster 1 **33% shorter yet drawing ~18% more word
types** at an equal token budget. Pure length predicts the opposite, which makes
this the strongest available evidence that the halves differ in kind — and also
the claim most likely to be a length artefact. So it is recomputed **inside each
length band**, at a common budget of **1,650 tokens** derived from the
smallest band × cluster cell, so that no cell is compared at a size it cannot
supply.

| length_band   |   budget |   n_reviews_c0 |   types_c0 |   sd_c0 |   n_reviews_c1 |   types_c1 |   sd_c1 | inversion_holds   |
|:--------------|---------:|---------------:|-----------:|--------:|---------------:|-----------:|--------:|:------------------|
| (2.999, 6.0]  |     1650 |            441 |   674.5700 |  8.6623 |            324 |   624.9500 |  2.6585 | False             |
| (6.0, 8.0]    |     1650 |            377 |   679.2950 | 11.8802 |            415 |   645.8000 | 11.2361 | False             |
| (8.0, 10.0]   |     1650 |            245 |   676.8000 |  8.8459 |            346 |   633.7100 | 11.6411 | False             |
| (10.0, 84.0]  |     1650 |            285 |   647.0000 | 12.7024 |            295 |   698.6350 | 13.7139 | True              |

The inversion **holds in some bands and not others**. Under
RQ1-E it is reported band by band and **never aggregated into one sentence**.

## What this step does NOT settle

1. **That the halves are personas.** Eliminating valence and verbosity is not
   the same as establishing an audience distinction. Only G-300 can do that.
2. **That no other cheap variable explains the cut.** Two were tested because
   two were implicated by S2e. A third may exist and would be worth testing if
   named.
3. **Anything with more confidence than a resubstitution bound allows.** Test C
   is a ceiling, not a measurement, and every use of it says so.
