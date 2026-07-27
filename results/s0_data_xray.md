# S0 — Data X-ray

Verification of the S0 claims in `docs/research_pipeline_en.md` against the raw
file. **Read-only step:** no data was cleaned, filtered, or written.

- **Config:** `configs/s0_xray.yaml`
- **Input:** `data/raw/Raw Bangla Movie Review Comment Dataset for Sentiment Analysis and Natural Language Processing.xlsx` (sheet `0`)
- **Text column:** `Movie Review` · **Label column:** `Sentiment`
- **Seed:** 42
- **Generated (UTC):** 2026-07-27T14:12:05.930329+00:00
- **Git commit:** `35295e29b378c9aadd2ea2af675e96bd71e29ec1-dirty`
- **Python:** 3.13.3 · **Platform:** Windows-11-10.0.26200-SP0

## Claim verification

| Quantity | Claimed | Observed | Flag |
|---|---|---|---|
| `n_rows` | 5000 | 5000 | MATCH |
| `label_counts` | 0:1665 / 1:1664 / 2:1670 | 0:1665 / 1:1664 / 2:1670 | MATCH |
| `exact_duplicates` | 204 | 204 | MATCH |
| `normalized_duplicates` | 205 | 206 | **MISMATCH** |
| `short_reviews_lt3_words` | 72 | 72 | MATCH |
| `null_rows` | 1 | 2 | **MISMATCH** |
| `usable_n` | 4722 | 4732 | **MISMATCH** |
| `median_words` | 8 | 8 | MATCH |
| `max_words` | 84 | 84 | MATCH |
| `emoji_rows` | 0 | 0 | MATCH |
| `url_or_mention_rows` | 0 | 0 | MATCH |

**Result: 8/11 match.** **3 of 11 claims did not reproduce.** The S0 table in `docs/research_pipeline_en.md` is wrong for those rows and must be corrected to the observed values. The observed column is authoritative; do not adopt the claimed number.

## Union decomposition of the S1 drop set

The three drop sets overlap, so subtracting their sizes independently
double-counts rows. The union is computed once and subtracted once. Set
definitions are in "Measurement definitions" below; `SHORT` excludes the
missing-text row so it stays the reported count of 72.

The claimed `usable_n` of 4722 is reproduced exactly by naive subtraction under the **exact** duplicate definition: 2 + 72 + 204 = 278, and 5000 − 278 = 4722.

Two consequences. First, that subtraction uses **2** null rows — the observed count — while the S0 table's `null_rows` row reports 1. The table is therefore internally inconsistent with its own `usable_n`, and the defect is in how `null_rows` was **reported**, not in the null handling behind the arithmetic. Second, the subtraction still treats the three drop sets as disjoint, so it double-counts the 10 rows in SHORT ∩ DUP. The union is 268, not 278, giving usable_n = **4732**.

**The claim-checked `usable_n` above uses the EXACT duplicate definition**
(DUP = 204), matching the pipeline's own "Removed in
cleaning" wording for the 204 figure. The normalized variant is reported below
so the choice is visible rather than buried; it is a decision for S1, not for
this verification step.

### Duplicates defined as **exact** (DUP = 204)

| Term | Rows |
|---|---|
| \|NULL\| | 2 |
| \|SHORT\| | 72 |
| \|DUP\| | 204 |
| \|NULL ∩ SHORT\| | 0 |
| \|NULL ∩ DUP\| | 0 |
| \|SHORT ∩ DUP\| | 10 |
| \|NULL ∩ SHORT ∩ DUP\| | 0 |
| naive sum (overlaps double-counted) | 278 |
| **\|union\|** | **268** |
| **usable_n = 5000 − union** | **4732** |

### Duplicates defined as **normalized** (DUP = 206)

| Term | Rows |
|---|---|
| \|NULL\| | 2 |
| \|SHORT\| | 72 |
| \|DUP\| | 206 |
| \|NULL ∩ SHORT\| | 0 |
| \|NULL ∩ DUP\| | 0 |
| \|SHORT ∩ DUP\| | 10 |
| \|NULL ∩ SHORT ∩ DUP\| | 0 |
| naive sum (overlaps double-counted) | 280 |
| **\|union\|** | **270** |
| **usable_n = 5000 − union** | **4730** |

| Duplicate definition | union | usable_n |
|---|---|---|
| exact (DUP = 204) | 268 | **4732** |
| normalized (DUP = 206) | 270 | **4730** |

## Measurement definitions

These fix how each observed number was computed, so the table is reproducible:

- **word** — a whitespace-delimited token (`str.split()`). No tokenizer, no
  stemming, no stopword removal.
- **null row** — the review text is missing or whitespace-only, **or** the
  sentiment label is missing.
- **exact duplicate** — a review string identical to an earlier one, counted as
  occurrences beyond the first.
- **normalized duplicate** — same, after Unicode NFC + whitespace collapse +
  strip. Applied for counting only; the data itself is never normalized.
- **usable_n** — rows surviving the three S1 drops (null, exact duplicate,
  <3 words), computed as a single union so rows failing several conditions are
  not double-counted.
- **median/max words** — over rows with non-null text.
- **emoji row** — contains a pictographic character from the Unicode emoji
  blocks (emoticons, pictographs, transport, dingbats, misc symbols, regional
  indicators). A bare `U+FE0F` (VARIATION SELECTOR-16) is a modifier, not an
  emoji, and is **not** counted here — it is reported separately as
  `orphan_vs16_rows` below.
- **url/mention row** — matches `http(s)://`, `www.`, a bare `*.com/.net/.org/.bd`
  token, or an `@handle`.

## Additional observed context (not claim-checked)

| Quantity | Observed |
|---|---|
| `columns` | ['Movie Review', 'Sentiment'] |
| `sheet_shape` | 5000 rows x 2 cols |
| `mean_words` | 9.63 |
| `min_words` | 1 |
| `reviews_ge_50_words` | 12 |
| `mean_words_by_label` | 0:8.19 / 1:11.85 / 2:8.84 |
| `rows_with_missing_text` | 1 |
| `rows_with_missing_label` | 1 |
| `short_rows_that_are_also_duplicates` | 10 |
| `orphan_vs16_rows` | 6 |
