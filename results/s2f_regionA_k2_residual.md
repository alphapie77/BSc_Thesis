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

- **Config:** `configs/s2f_residual.yaml` · **n:** 1897 (region A, post-dedup, K = 2)
- **Generated (UTC):** 2026-08-03T16:44:32.870633+00:00 · **Commit:** `730de20136ae8e572f8340701c405477258a64e9-dirty`
- **Seed:** 42 · Marginal cluster-1 share: **39.7%**
- **No embedding required.** This runs off S2e's assignments and the cleaned
  text. **Nothing is trained** — AUC and φ are rank/contingency statistics and
  richness is sampling at a fixed budget. Rules 7 and 10 intact.

## Verdict — Test C, the decisive one

**RESIDUAL_SURVIVES** — lift **+9.8 pp** <
10.0.

Most of the partition is explained by **neither** variable. Whatever LaBSE is
cutting on, it is not valence and not verbosity — and under RQ1-E that makes
G-300 the right place to spend, because no cheaper instrument has explained the
cut.

**This does not show the halves are personas.** It shows the two cheapest
explanations have been eliminated: a stronger position than S2e left us in, and
a weaker one than a persona claim requires.

> ### ⚠️ This verdict sits **0.2 pp** from its threshold
>
> The lift is **9.8 pp** against a cutoff of
> **10.0**. A different quartile binning, a
> different corpus draw, or a handful of reviews moving cells could return
> **PARTIALLY_EXPLAINED** instead. The threshold was fixed in advance and is applied as
> written — but a verdict this close to its own boundary is **weak evidence, and
> is to be reported as weak** wherever it appears. It is not rounded, softened,
> or restated as a comfortable margin.

### Which variable is actually doing the work?

"Sentiment and length together" is not a useful summary when one of them may be
doing all the work, and the joint number cannot tell you which. Same estimator,
three cell definitions:

| conditioning_on             |   accuracy_% |   lift_pp |
|:----------------------------|-------------:|----------:|
| nothing (marginal baseline) |         60.3 |       0.0 |
| Sentiment only              |         69.5 |       9.3 |
| length band only            |         65.5 |       5.2 |
| both (the 8 cells)          |         70.1 |       9.8 |

**Read the gap between the last two rows.** That is what length adds *once
sentiment is already known* — and it is the honest measure of the length
confound at the level of prediction, as opposed to the level of correlation that
S2e's `length_auc` reports.

### The number, with the caveat that must always travel with it

Cell-majority accuracy **70.1%** against a marginal baseline of
**60.3%** → lift **+9.8 pp**.

⚠️ **This is a resubstitution estimate.** Each cell's majority is read from the
same rows it is scored on, so it **overstates** how much sentiment and length
explain. That is the useful direction of error: it makes the "cheap variables
explain everything" verdict *easier* to reach, so a **low** lift is strong
evidence, while a high one is a ceiling rather than a measurement.

### The eight cells

| cell            |   n |   cluster1_share_% |   cell_majority |   deviation_from_marginal_pp |
|:----------------|----:|-------------------:|----------------:|-----------------------------:|
| S0|(15.0, 69.0] | 129 |               48.8 |               0 |                          9.1 |
| S0|(2.999, 6.0] | 391 |               69.3 |               1 |                         29.6 |
| S0|(6.0, 9.0]   | 239 |               57.3 |               1 |                         17.6 |
| S0|(9.0, 15.0]  | 185 |               48.1 |               0 |                          8.4 |
| S1|(15.0, 69.0] | 311 |               11.3 |               0 |                         28.5 |
| S1|(2.999, 6.0] | 192 |               36.5 |               0 |                          3.3 |
| S1|(6.0, 9.0]   | 177 |               23.7 |               0 |                         16.0 |
| S1|(9.0, 15.0]  | 273 |               17.2 |               0 |                         22.5 |

A cell share near the marginal 39.7% means that knowing a review's
sentiment and length tells you nothing about which half it landed in. Shares
near 0 or 100 mean the opposite.

## Test A — does length separate the halves *within* a sentiment class?

Directionless AUC of `n_words` against cluster, computed separately per
sentiment class. Reported figure is the **minimum**: length is only
"independent" if it works in *both* classes.

|   Sentiment |        n |   auc_length_vs_cluster |   mean_words_cluster0 |   mean_words_cluster1 |
|------------:|---------:|------------------------:|----------------------:|----------------------:|
|      0.0000 | 944.0000 |                  0.6115 |               10.3620 |                8.3214 |
|      1.0000 | 953.0000 |                  0.6567 |               14.5138 |               10.3866 |

**min = 0.6115** → **independent of sentiment**
(threshold 0.6).

## Test B — does sentiment separate the halves *within* a length band?

|φ| inside each quartile band of `n_words`. Bands are quartile-derived, not
hand-chosen; edges appear in the table. Reported figure is the **minimum**
across bands.

| length_band   |   n |   abs_phi_cluster_vs_sentiment |   cluster1_share_% |
|:--------------|----:|-------------------------------:|-------------------:|
| (2.999, 6.0]  | 583 |                         0.3133 |            58.4906 |
| (6.0, 9.0]    | 416 |                         0.3355 |            43.0288 |
| (9.0, 15.0]   | 458 |                         0.3318 |            29.6943 |
| (15.0, 69.0]  | 440 |                         0.4112 |            22.2727 |

**min = 0.3133** in band `(2.999, 6.0]` → **independent of length**, in every band
(threshold 0.2).

## Test D — does the lexical-richness inversion survive a length control?

S2e found cluster 1 **33% shorter yet drawing ~18% more word
types** at an equal token budget. Pure length predicts the opposite, which makes
this the strongest available evidence that the halves differ in kind — and also
the claim most likely to be a length artefact. So it is recomputed **inside each
length band**, at a common budget of **1,100 tokens** derived from the
smallest band × cluster cell, so that no cell is compared at a size it cannot
supply.

| length_band   |   budget |   n_reviews_c0 |   types_c0 |   sd_c0 |   n_reviews_c1 |   types_c1 |   sd_c1 | inversion_holds   |
|:--------------|---------:|---------------:|-----------:|--------:|---------------:|-----------:|--------:|:------------------|
| (2.999, 6.0]  |     1100 |            242 |   503.3450 |  2.6107 |            341 |   649.1250 |  8.1129 | True              |
| (6.0, 9.0]    |     1100 |            237 |   572.4500 |  9.6009 |            179 |   665.4400 |  7.4092 | True              |
| (9.0, 15.0]   |     1100 |            322 |   611.8050 | 12.3506 |            136 |   715.5850 |  9.2235 | True              |
| (15.0, 69.0]  |     1100 |            342 |   652.2100 | 15.1458 |             98 |   751.5200 | 10.5707 | True              |

The inversion **holds in every length band**. It survives its
most obvious control, so the halves differ in **kind** and not only in **size**.
Under RQ1-E this is the strongest pre-G-300 evidence for the persona reading —
still not proof, and still subordinate to G-300.

## What this step does NOT settle

1. **That the halves are personas.** Eliminating valence and verbosity is not
   the same as establishing an audience distinction. Only G-300 can do that.
2. **That no other cheap variable explains the cut.** Two were tested because
   two were implicated by S2e. A third may exist and would be worth testing if
   named.
3. **Anything with more confidence than a resubstitution bound allows.** Test C
   is a ceiling, not a measurement, and every use of it says so.
