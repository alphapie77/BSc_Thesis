# G-300 annotation sheets — do not edit by hand

Generated 2026-08-03T17:53:32.395152+00:00 from commit `b566f59ba713862d750a54441b7d94c7c4fd0251-dirty`, seed
42.

## For annotators

Read **`docs/g300_annotation_guideline.md`** first, all of it. Then:

1. `g300_calibration_<you>.csv` — 20 practice items. Both annotators do these
   **separately**, then discuss **once**. These do not count.
2. `g300_sheet_<you>.csv` — the 300 real items. **No discussion from here on**
   until both of you have finished.

Fill only the `rating` column (0–3) and optionally `note`. Do not reorder,
delete or add rows.

## For the researcher

- `g300_key.csv` maps `item_id` → `review_id`, `Sentiment`,
  `cluster_k2`, `region`, `n_words`. **It is not shipped to annotators.**
- Of the 300 items, **123 are in region A** and therefore carry a K=2 label;
  Gate 2 runs on those. Composition (cluster, sentiment): {(0.0, 0): 26, (0.0, 1): 52, (1.0, 0): 35, (1.0, 1): 10}
- Calibration drew from `dev` after excluding 10 id(s) quoted as worked
  examples in the guideline — an annotator who has just read the rubric would be
  recalling those, not judging them.
- Sheets are written in `utf-8-sig` so Excel on Windows renders Bangla instead
  of mojibake.
