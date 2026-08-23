# Dataset Card — Bangla review and plot resources

Follows Gebru et al. (2021) Datasheets for Datasets + Bender & Friedman (2018)
Data Statement.

- **Language (Bender Rule):** Bangla (Bengali), Bangladeshi variety, Bengali script.
- **Source:** Hossain et al. (2026), Mendeley Data, version 3,
  DOI `10.17632/vwp7gnj3d6.3`.
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
| Published resource | Version 3; DOI `10.17632/vwp7gnj3d6.3` |
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
- **To add:** annotator demographics, gold-300 release.

---

## The review corpus is two corpora — read this before using n = 4,730

Rows 0–1998 and 1999–4999 of the source `.xlsx` differ on features that carry no
sentiment content: **38.7% vs 99.2%** of rows carry a দাঁড়ি, **13.5% vs 0.8%**
contain a first-person pronoun, and lexical richness is **255 vs 128** word types
per 1,000 tokens. The change is a step at one row, not a drift. All 1,670
class-2 rows sit in the second region. See `results/s2c_region_split.md`.

**Collector's account (2026-07-30, recall-based, no written log):** gathered
from many different places, all organic user comments, none written or
generated, and no memory of which rows came from where.

**These two records are not reconciled, and the thesis reports both.** The
consequence is fixed regardless of cause: `region` is a controlled factor, the
split is stratified on `Sentiment × region`, and every headline metric is
reported full / A / B (`docs/protocol.md`, "Scope decision").

**Do not describe this corpus as organic Bangla audience opinion.** ~60% of it
has an unrecoverable provenance.

---

## Plot synopses (secondary corpus, n = 120) — FROZEN 2026-07-31

| | |
|---|---|
| Source | **bn.wikipedia.org**, MediaWiki API |
| Method | `src/preprocess/plots_scrape.py` — harvest 3,135 candidates → 124 passing the gate → **4 removed on human review** → 120 |
| **Split** | **30 dev / 90 eval**, assigned once with seed 42, frozen |
| Per-row provenance | `source_url`, **`revision_id`**, `revision_timestamp` — complete for all 120 |
| Length | 3–12 sentences (median 9) |
| **Licence** | **CC BY-SA 4.0** |

**Not 130.** The pipeline spec asks for 130 = 30 dev + 100 eval; bn.wikipedia
does not contain 130 Bangla-film articles with a usable plot section. Two routes
to 130 existed and both were refused — relaxing the quality gate (thin,
two-sentence plots) and adding the language-neutral by-year categories (which
would have admitted Tamil and Hindi films described in Bangla, passing every
check while making the corpus stop being Bangla cinema). Deviation logged in
`docs/protocol.md`, 2026-07-31.

**Removed on human review**, after passing every mechanical gate:

| id | film | why |
|---|---|---|
| BN024 | আদম সুরত | production history, and a documentary |
| BN042 | কাগজের ফুল | the director's fatal accident; the film was never finished |
| BN068 | দহন (১৯৮৫) | commentary *about* the story, never what happens |
| BN113 | শঙ্খবেলা | a 3-sentence fragment that sets up and stops |

Logged in `data/plots/rejected_by_review.csv`. BN113 is the case for human
review in one row: Bangla, exactly 3 sentences, over 120 characters, no
biography section — passes everything, and nothing happens in it.

**One caveat to state if this corpus is described as Bangla cinema:** BN072
(দ্য নেমসেক) is Mira Nair's **English-language** film, in bn.wikipedia because
its subject is a Bengali immigrant family. Kept as a scope decision (2026-07-31).

### Attribution obligation — discharged in the thesis package

bn.wikipedia text is **CC BY-SA 4.0**: reuse requires **attribution** and
**share-alike**. This is a licence condition, not a courtesy.

The thesis package now supplies the required record in
`docs/appendices/appendix_d_plot_attribution.md`:

1. bn.wikipedia and its contributors are attributed through all 120 article
   titles and exact **revision ids**.
2. The CC BY-SA 4.0 licence and share-alike requirement are stated.
3. The 2026-07-31 harvest date is stated.

Appendix D must ship with the thesis and with any distributed derivative of the
plot set. Removing it would reopen the licence obligation.

Unlike the review corpus, this one has **complete, checkable provenance**: any
reader can fetch the exact revision used. That contrast is deliberate and is
worth stating in the thesis — it is the difference between a corpus assembled
with a record and one assembled without.
