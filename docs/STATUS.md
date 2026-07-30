# STATUS — single source of truth for "where are we"

**Last updated:** 2026-07-30 · **Phase:** 0→1 (setup + Bangla data)
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
| 5 | S2 pilot: near-dup + ARI trap-check | ✅ **run** 2026-07-30 (Kaggle T4, commit `e3d8e43`) — ARI **0.1793**, Band 1, not degenerate | `results/s2_pilot_ari_trapcheck.md` | 2026-07-30 |
| 5b | S2b register probe (**exploratory**) | ✅ run — class 2 differs structurally from classes 0/1; **RQ1 persona claim suspended** | `results/s2b_register_probe.md` | 2026-07-30 |
| 5c | Provenance query to the data collector | 🔴 **OPEN — blocks RQ1** | `docs/provenance_query.md` | 2026-07-30 |
| 6 | protocol.md freeze + supervisor signature | 📝 draft; **cannot freeze while 5c is open** | `docs/protocol.md` | — |

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
| (c) | Collection was a **bulk pull** from Bangla movie-related Facebook groups and YouTube channels — **no keyword or query-seeded search**. Stopping was **quota-driven at ~1,665 per class**. Source venue, thread, and timestamp were **not retained**. | (i) The **natural class prior is destroyed — no prevalence claim may be made from this corpus.** (ii) The disproportionate concentration of duplicates and sub-3-word items in class 0 (152 of 270 drops) is **consistent with quota-filling pressure**. | recall-based (medium) — ⚠️ **contradicted for class 2 by fact (reg) below** |
| (reg) | **Class 2 is not the same kind of text as classes 0 and 1.** 100% carry দাঁড়ি (vs 58% / 66%); **0%** contain a first-person pronoun (expected 149), an exclamation mark (expected 38), or a comma run (expected 33); vocabulary is **1,772 types per 12,000 tokens vs 3,577 / 3,303**. S2 separates it almost perfectly — 12 of 1,572 class-2 items in cluster 0; φ = 0.565 for *cluster 0 vs rest* × *class 2 vs rest*, **above** the 3-way sentiment V of 0.410. | **The RQ1 persona claim is suspended.** The clusters may be tracking how the text was produced rather than who the audience is. Three explanations fit (generated to fill quota / different venue / hand-written) and all three break fact (c). Only the collector can choose between them — `docs/provenance_query.md`. | **verified** (computed, `results/s2b_register_probe.md`) — but **EXPLORATORY**: the hypothesis came from looking at the data |
| (hash) | Source `.xlsx` SHA-256 = `8f972734fc3629427cdf8d01716aa817f7b325410b2fdd0f26cbc2e68506db9f`, 195,186 bytes. | Every `review_id` derives from this file's raw row order. Any future copy can be checked byte-identical before a re-run; a mismatch invalidates all IDs. | **verified** (computed) |
| (env) | S2 will run on **Kaggle's host-native torch/CUDA**, not on the versions pinned in `requirements.lock.txt` (Windows-frozen). Decided 2026-07-30. | **Two environments must be reported in the appendix**, with a statement of which produced which result. S2's numbers are attributable to `results/env_snapshot_s2_kaggle.json` — *not* to `requirements.lock.txt`. Disclosure obligation, not a footnote. | **decided** (2026-07-30) |

---

## Verified facts (supersede the pipeline spec where they disagree)

| Quantity | Pipeline claims | **Verified** |
|---|---|---|
| `null_rows` | 1 | **2** (one missing text, one missing label) |
| `normalized_duplicates` | 205 | **206** |
| `usable_n` after rule-based cleaning | 4,722 | **4,730** |
| Post-clean class balance | "perfectly balanced" | **1,513 / 1,599 / 1,618** |
| Near-duplicate pairs ≥ 0.90 | — | **449** of 11,184,085 off-diagonal pairs (0.004%) |
| Surviving n at t = 0.95 | — | **4,625** (105 rows removed) |
| ARI(cluster, Sentiment) @ 0.95 | — | **0.1793** — Band 1, not degenerate |
| Cosine p99.9 | — | **0.7561** — below every swept threshold, so none cut into the bulk |
| Final `usable_n` for splitting | — | **still unknown** — blocked by 5c, not by the threshold |

> **Correction (2026-07-30).** This file previously recorded the venue/selection
> confound as *"untestable in principle"* because venue was not retained at
> collection. **That was wrong in one specific way.** Venue was not retained, but
> **writing style survives in the text itself**, and style is measurable — see
> fact (reg). The confound is testable, was tested, and the evidence points
> toward it. The lesson is worth keeping: "untestable" is a strong claim and
> deserved a harder look before it was written down.

`docs/research_pipeline_en.md` still carries the old numbers — deliberately not
edited until the final `usable_n` is known (see Open decisions).

---

## Open decisions

| # | Decision | Blocks | Resolved by |
|---|---|---|---|
| **0** | **Where did the 1,670 class-2 rows come from?** | **RQ1, Gold-300, split freeze — everything** | **the data collector** (`docs/provenance_query.md`) |
| 1 | Final `usable_n` after near-dup removal | Step 4 | blocked by 0 |
| 2 | Near-dup threshold: 0.90 gives Band 2, 0.95 and 0.98 give Band 1. Held at the pre-registered **0.95**; audit sheet generated and parked, since 52% of the contested band is class 2 | Step 4 | blocked by 0 |
| 3 | ~~Do personas survive `ARI(cluster, Sentiment)`?~~ **Answered, but superseded**: ARI 0.1793 = Band 1, so the clusters are *not* a sentiment rediscovery — however the crosstab shows they separate class 2 from the rest almost perfectly, so the live question is now decision 0 | RQ1 claim | S2 pilot + 0 |
| 4 | Correct the S0 table in the pipeline spec | — | after 1–2 |
| 5 | Frame the register finding in the **stylometry / authorship** literature or the **machine-generated-text detection** literature? Writing decision, Sabbir's | Ch.2, Ch.4 | Sabbir |
| 6 | Should `s2_pilot.py` persist cluster assignments? Every follow-up question currently needs a full re-run or a reconstruction from the printed crosstab | future analyses | Sabbir |

---

## Immediate next actions

1. 🔴 **Put `docs/provenance_query.md` to the data collector.** Everything
   downstream — RQ1, Gold-300 stratification, the split freeze — waits on it.
   Gold-300 in particular: the annotation scheme was to be stratified on the S2
   clusters, so finding this out *before* 300 items are annotated is the
   cheapest moment it will ever be found out.
2. Read Huang et al. (ICLR 2024) → fill its `related_work.md` entry.
3. Start plot collection: 5/day from bn.wikipedia, log `source_url` for every
   one. **Unblocked by all of the above** — and now the highest-value use of
   waiting time.

## Infrastructure state (2026-07-30)

| Item | State |
|---|---|
| Text artifacts | LF on every host — `provenance.write_text_lf()` + `.gitattributes eol=lf`. The 2026-07-28 phantom diff on three `results/` files was pure CRLF churn, **zero content change**, now resolved. |
| S2 test coverage | `test_s2_verdict.py` 8/8 (verdict bands ↔ pre-registration) + `test_s2_numeric.py` 15/15 (dedup core vs brute force). `cluster_and_ari` is **not** covered locally — needs scikit-learn/scipy, exercised on Kaggle. |
| `env_snapshot.py` | `--out <path>` writes a snapshot without touching `requirements.lock.txt`; refuses `--out requirements.lock.txt`. Mandatory on any non-local host. |
| Git hook | `core.hooksPath = .githooks` — confirmed enabled. |
