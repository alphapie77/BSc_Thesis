# STATUS — single source of truth for "where are we"

**Last updated:** 2026-07-28 · **Phase:** 0→1 (setup + Bangla data)
**Week:** 1 of 14

> Update this at the same time as the lab notebook entry, at the end of every
> step. `CLAUDE.md` points here rather than duplicating it, so this file is the
> only place progress is recorded.

---

## Pipeline steps

| # | Step | Status | Artifact | Notebook entry |
|---|---|---|---|---|
| 1 | Repo skeleton + reproducibility contract | ✅ done | repo, `seed.py`, `provenance.py` | 2026-07-27 |
| 2 | S0 verification (read-only) | ✅ done | `results/s0_data_xray.md` | 2026-07-27 |
| 3 | S1 cleaning → `bn_clean.csv` (n=4,730) | ✅ done | `data/cleaned/bn_clean.csv`, `results/s1_cleaning_log.json` | 2026-07-27 |
| 4 | Frozen R1/R2 split | ⏸ **deferred** — must run after near-dup removal (leakage) | `data/splits/split_map_v1.json` | — |
| 5 | S2 pilot: near-dup + ARI trap-check | 🔨 code written + unit-tested, **never run** | `results/s2_pilot_ari_trapcheck.md` | — |
| 6 | protocol.md freeze + supervisor signature | 📝 draft; freezes after step 5 | `docs/protocol.md` | — |

## Parallel tracks (no step blocks these — but they block later steps)

| Track | Target | Done | Blocks | Risk |
|---|---|---|---|---|
| Bangla plot synopses | 130 (30 dev + 100 eval) | **0** | S6 evaluation | 🔴 highest — manual, slow, no shortcut |
| Base-paper reading | 5 Tier-1 | **0** | Ch.1, Ch.2 | 🔴 high |
| Gold-300 annotation | 300 × 3 annotators | 0 | RQ1 validation | 🟡 needs S2 clusters first (stratified) |
| **Retrospective base-label reliability study** | 200 items from R (disjoint from G-300), 2 native annotators, sentiment only, **blind to the original labels**; run in a session **separate** from persona annotation, order randomized | **0** | Ch.4 §Data Quality; Ch.5 §Threats | 🟡 converts "no IAA exists" (fact (a)) into an **estimated** base-label reliability figure. Report annotator-vs-annotator κ/α **and** their majority vs the original single-coder label. |

---

## Provenance facts (dataset collection)

> **Source and standing.** Everything in this table marked `recall-based` was
> reported **verbally by the data collector on 2026-07-28**. **There is no
> written collection log.** These are recollections, not records: they cannot be
> re-checked against an artifact, and they must never be described as
> "verified" anywhere in the thesis, the dataset card, or a paper. Where a
> statement can be tested against the data instead of recall, that test is
> registered in `protocol.md` and its outcome supersedes this table.
>
> (b) — merged into (c) on 2026-07-28; retained as a numbering placeholder so
> earlier references resolve.

| # | Fact | Consequence | Confidence |
|---|---|---|---|
| (a) | `Sentiment` labels are **per-item human judgments, but single-coded**: one annotator, no overlapping items. | **No inter-annotator agreement is computable for the base labels**, and single-annotator systematic bias is unmeasurable. Label validity is adequate in kind but unquantified. | recall-based (medium) |
| (c) | Collection was a **bulk pull** from Bangla movie-related Facebook groups and YouTube channels — **no keyword or query-seeded search**. Stopping was **quota-driven at ~1,665 per class**. Source venue, thread, and timestamp were **not retained**. | (i) The **natural class prior is destroyed — no prevalence claim may be made from this corpus.** (ii) The disproportionate concentration of duplicates and sub-3-word items in class 0 (152 of 270 drops) is **consistent with quota-filling pressure**. | recall-based (medium) |
| (hash) | Source `.xlsx` SHA-256 = `8f972734fc3629427cdf8d01716aa817f7b325410b2fdd0f26cbc2e68506db9f`, 195,186 bytes. | Every `review_id` derives from this file's raw row order. Any future copy can be checked byte-identical before a re-run; a mismatch invalidates all IDs. | **verified** (computed) |

---

## Verified facts (supersede the pipeline spec where they disagree)

| Quantity | Pipeline claims | **Verified** |
|---|---|---|
| `null_rows` | 1 | **2** (one missing text, one missing label) |
| `normalized_duplicates` | 205 | **206** |
| `usable_n` after rule-based cleaning | 4,722 | **4,730** |
| Post-clean class balance | "perfectly balanced" | **1,513 / 1,599 / 1,618** |
| Final `usable_n` for splitting | — | **unknown** until near-dup removal |

`docs/research_pipeline_en.md` still carries the old numbers — deliberately not
edited until the final `usable_n` is known (see Open decisions).

---

## Open decisions

| # | Decision | Blocks | Resolved by |
|---|---|---|---|
| 1 | Final `usable_n` after near-dup removal | Step 4 | S2 pilot |
| 2 | Near-dup threshold (0.90 / 0.95 / 0.98) from the sensitivity curve | Step 4 | S2 pilot |
| 3 | Do personas survive `ARI(cluster, Sentiment)`, or reframe as engagement tiers? | RQ1 claim | S2 pilot |
| 4 | Correct the S0 table in the pipeline spec | — | after 1–2 |

---

## Immediate next actions

1. Run S2 pilot on Kaggle (internet ON, GPU on, upload `bn_clean.csv` as a Kaggle Dataset — it is gitignored).
2. Read Huang et al. (ICLR 2024) → fill its `related_work.md` entry.
3. Start plot collection: 5/day from bn.wikipedia, log `source_url` for every one.
