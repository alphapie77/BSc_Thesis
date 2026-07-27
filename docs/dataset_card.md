# Dataset Card -- STUB (complete during Phase 1)

Follows Gebru et al. (2021) Datasheets for Datasets + Bender & Friedman (2018)
Data Statement.

- **Language (Bender Rule):** Bangla (Bengali), Bangladeshi variety, Bengali script.
- **Source:** Mendeley Data, "Raw Bangla Movie Review Comment Dataset..."
- **Size:** 5,000 rows x 2 columns (Movie Review, Sentiment).
- **HONEST NOTE (to verify in S0):** despite "Raw" in the title, the file appears
  partially pre-cleaned -- zero emoji, zero URLs/mentions. State this explicitly;
  it means the pre-defence report's emoji preprocessing tables do not describe
  this file.
- **Known absence:** no movie-title column -> reviews cannot be mapped to films
  -> a held-out-films split is impossible.

## Class balance before and after cleaning

The raw file is curated to near-uniform balance. **Rule-based cleaning (S1)
breaks that balance** -- this must be stated whenever the balance is mentioned,
because the uniform figure describes only the raw file.

| Sentiment | Raw | Post-clean (S1) | Dropped |
|---|---|---|---|
| 0 | 1,665 | 1,513 | 152 |
| 1 | 1,664 | 1,599 | 65 |
| 2 | 1,670 | 1,618 | 52 |
| **Total labelled** | **4,999** | **4,730** | **269** |
| Unlabelled | 1 | 0 | 1 |
| **All rows** | **5,000** | **4,730** | **270** |

**The per-class drops sum to 269, not 270.** The 270th dropped row has a missing
`Sentiment` value, so it belongs to no class and cannot appear in any per-class
count: 269 + 1 = 270.

Duplicates and sub-3-word reviews are concentrated in class 0 (152 of the 269
labelled drops, ~56%). Consequence: **no downstream step may assume a balanced
set after S1**, and the R1/R2 split is sentiment-stratified for this reason.

Source of these numbers: `results/s1_cleaning_log.json` (`class_balance`);
drop-set arithmetic verified in `results/s0_data_xray.md`.

- **Note on n:** 4,730 is `n_after_rule_based_cleaning`. Near-duplicate removal
  (cosine >= 0.95) is deferred to S2, so the final `usable_n` is not yet fixed.
- **To add:** collection method, annotator demographics, licensing, gold-300 release.
