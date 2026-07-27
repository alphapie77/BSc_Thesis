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

## Source file identity (fixes what every `review_id` points at)

| Property | Value |
|---|---|
| Filename | `Raw Bangla Movie Review Comment Dataset for Sentiment Analysis and Natural Language Processing.xlsx` |
| **SHA-256** | `8f972734fc3629427cdf8d01716aa817f7b325410b2fdd0f26cbc2e68506db9f` |
| Size | 195,186 bytes |
| Sheet / shape | `Sheet1`, 5,000 rows × 2 cols (`Movie Review`, `Sentiment`) |
| Download date | **UNCONFIRMED — to be filled by hand.** Filesystem mtime is 2026-07-27 19:51:35 +06:00, but that records when the file landed on this disk (possibly a copy), not when it was downloaded from Mendeley. |

**Why the hash matters.** `review_id` is derived from the **row order of this
exact file** (`bn_0042` = raw row 42, assigned before any row is dropped). The
split map references those IDs. If Mendeley silently publishes an updated
version — a row inserted, reordered, or corrected — then re-running S1 against
it produces IDs that look identical but point at different reviews. **Nothing in
the pipeline would raise an error**; the split would simply be wrong, and every
downstream result with it. Verify before any re-run:

```bash
sha256sum "data/raw/Raw Bangla Movie Review Comment Dataset for Sentiment Analysis and Natural Language Processing.xlsx"
```

A mismatch means the IDs are invalid — stop and reconcile, do not regenerate.

**⚠️ The `.xlsx` is gitignored by design and has no backup in this repo.**
`data/raw/` is excluded from version control (size + licensing), so cloning the
repo does **not** restore it — a clone yields only `.gitkeep` and a README. The
repo therefore protects the code, the results, and the IDs, but **not the one
file they all resolve against**. Keep an independent off-repo copy (Drive or
equivalent) and record its location here. Re-downloading from Mendeley is not a
substitute: it is exactly the path that risks silently fetching a different
version, which is what the hash above exists to detect.

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
