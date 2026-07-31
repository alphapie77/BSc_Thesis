# STATUS — single source of truth for "where are we"

**Last updated:** 2026-08-01 · **Phase:** 0→1 (setup + Bangla data)
**Week:** 2 of 14

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
| 4 | Frozen R1/R2 split | 🟢 **unblocked** — cluster assignments now exist; stratify on `Sentiment × region` | `data/splits/split_map_v1.json` | — |
| 5 | S2 pilot: near-dup + ARI trap-check | ✅ **run** 2026-07-30 (Kaggle T4, commit `e3d8e43`) — ARI **0.1793**, Band 1, not degenerate | `results/s2_pilot_ari_trapcheck.md` | 2026-07-30 |
| 5b | S2b register probe (**exploratory**) | ✅ run — class 2 differs structurally from classes 0/1; **RQ1 persona claim suspended** | `results/s2b_register_probe.md` | 2026-07-30 |
| 5c | Provenance query to the data collector | ✅ **CLOSED 2026-07-30 — unresolvable.** Answer: collected from **many different places, all organic; which rows came from where is not remembered, and no metadata was kept.** That is an honest answer, and the pre-committed consequence applies: the measurement stands as the best available evidence, reported as exploratory, with the gap stated in Limitations. **Do not re-ask.** | `docs/provenance_query.md` | 2026-07-30 |
| 5d | S2c region split (**exploratory**) — the corpus is two corpora | ✅ run — **60% of rows carry a uniform, non-organic signature** | `results/s2c_region_split.md` | 2026-07-30 |
| 5e | `ARI(cluster, region)` — the decisive test | ✅ **RUN 2026-07-31. Pre-registered outcome 1 fires.** ARI(region) **0.4813** vs ARI(Sentiment) **0.1793**, at every threshold. Binary recast: ARI 0.7487, φ 0.861, **93.3% accuracy at identifying which corpus a review came from**. The clusters are a corpus detector, not personas. | `results/s2_cluster_assignments.csv` | 2026-07-31 |
| 5f | S2-A: trap-check on region A alone | ✅ **run** — n=1,897, **not degenerate** (29.5/38.9/31.6), ARI **0.1804 → Band 1**. But V=**0.5455** (up from 0.4104) and the clusters are visibly sentiment-ordered; ARI is capped because K=3 meets 2 classes — **pre-registered as weakening this evidence**. G-300 is the arbiter. | `results/s2a_regionA_trapcheck.md` | 2026-07-31 |
| 6 | protocol.md freeze + supervisor signature | 📝 draft; 5c closed, so this can now freeze | `docs/protocol.md` | — |

## Parallel tracks (no step blocks these — but they block later steps)

| Track | Target | Done | Blocks | Risk |
|---|---|---|---|---|
| Bangla plot synopses | ~~130~~ → **120 = 30 dev + 90 eval** (deviation logged 2026-07-31) | ✅ **FROZEN** — 124 harvested, **4 rejected on human review** (BN024 production history, BN042 director's death, BN068 theme commentary, BN113 a 3-sentence fragment). Split assigned once with seed 42; `plots_check` refuses to reassign. Every row carries `revision_id` + licence. | S6 evaluation | 🟢 **done** — BN113 passed every mechanical gate and is unusable, which is the case for human review in one row. ⚠️ **Outstanding: CC BY-SA attribution** (3-item checklist in the dataset card) must be discharged before submission. One kept plot (BN072 দ্য নেমসেক) is an English-language film — Sabbir's scope call, recorded in the notebook |
| Base-paper reading | 5 Tier-1 | **0** | Ch.1, Ch.2 | 🔴 **highest now** — plots are frozen and S2 is done, so nothing else is competing for the time |
| Gold-300 annotation | 300 × 3 annotators | **0** | RQ1 validation | 🔴 **now the arbiter.** Must be stratified on the **region-A** clustering, never the full-corpus one — that one is a corpus detector. G-300 is what decides whether cluster 1 (the 54/46 mixed cluster) is an audience persona or just the ambivalent reviews; nothing else can. |
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
| (collector-2) | **Collector's account, 2026-07-30, on the region split:** the data was gathered from **many different places**, all of it **organic user comments**; **none of it was written or machine-generated**; and **which rows came from which source is not remembered — no metadata was kept.** | Recorded as stated, in his words. It **does not reconcile with fact (split)**: many mixed sources would interleave registers throughout the file, whereas the observed change is a step at one row. The likeliest reconciliation — **collection in two separate sittings, months apart, with no log** — is consistent with both, but is inference, not testimony, and is labelled as such wherever it appears. | recall-based (low — the same recollection previously stated "same way" for a block the file shows was assembled separately) |
| (split) | **The corpus is two corpora concatenated at raw row 1999.** Rows 0–1998 (n=1,999): দাঁড়ি **38.7%**, first-person **13.5%**, exclamation 3.4%, comma-runs 3.3%, **255** types/1k tokens, labels **999 / 999 / 0**. Rows 1999–4999 (n=3,001): দাঁড়ি **99.2%**, first-person **0.8%**, exclamation 0.3%, comma-runs **0.0%**, **128** types/1k, labels 666 / 665 / **1,670**. The seam is a step over ~50 rows, not a drift. **60% of the corpus is region B.** | **Supersedes fact (reg) below, which mis-framed this as a class-2 property.** Class 2 is perfectly nested inside region B, which is why it looked that way — but rows 3665–4330 are labelled **0** and carry the same signature. **Every result over the full corpus is confounded.** Region A survives cleaning as 1,910 rows, organic, two classes — a smaller but usable corpus. | **verified** (computed, `results/s2c_region_split.md`) — **EXPLORATORY** framing |
| (reg) | ~~Superseded by (split).~~ **Class 2 is not the same kind of text as classes 0 and 1.** 100% carry দাঁড়ি (vs 58% / 66%); **0%** contain a first-person pronoun (expected 149), an exclamation mark (expected 38), or a comma run (expected 33); vocabulary is **1,772 types per 12,000 tokens vs 3,577 / 3,303**. S2 separates it almost perfectly — 12 of 1,572 class-2 items in cluster 0; φ = 0.565 for *cluster 0 vs rest* × *class 2 vs rest*, **above** the 3-way sentiment V of 0.410. | **The RQ1 persona claim is suspended.** The clusters may be tracking how the text was produced rather than who the audience is. Three explanations fit (generated to fill quota / different venue / hand-written) and all three break fact (c). Only the collector can choose between them — `docs/provenance_query.md`. | **verified** (computed, `results/s2b_register_probe.md`) — but **EXPLORATORY**: the hypothesis came from looking at the data |
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
| ~~**0**~~ | ~~Where did rows 1999–4999 come from?~~ **CLOSED 2026-07-30 — unresolvable, and correctly so.** Collector's account: many different sources, all organic user comments, **no memory of which rows came from where and no metadata retained**. Nothing further can be recovered; the file has no venue, thread or timestamp column (fact (c)) and no collection log exists (fact (a)). **The measurement (fact (split)) and the collector's account are both recorded and they are not reconciled** — that is the honest end state, not a failure. Nothing downstream stays blocked on it. | — | closed |
| ~~**0b**~~ | ~~region A only, full corpus, or the split as the object of study?~~ **CLOSED 2026-07-30 — Sabbir: full corpus.** Conditions are pre-registered in `protocol.md` §"Scope decision": region becomes a **controlled factor**, the split stratifies on `Sentiment × region`, every headline metric is reported full / A / B, and no claim survives that does not survive within-region. Region A is retained as a robustness check, not the main line. | — | closed |
| 1 | Final `usable_n` after near-dup removal | Step 4 | blocked by 0 |
| 2 | Near-dup threshold: 0.90 gives Band 2, 0.95 and 0.98 give Band 1. Held at the pre-registered **0.95**; audit sheet generated and parked, since 52% of the contested band is class 2 | Step 4 | blocked by 0 |
| 3 | ~~Do personas survive the trap-check?~~ **ANSWERED 2026-07-31.** On the full corpus the clusters are a **corpus detector** (93.3% accuracy) — no persona claim stands there. In region A they are non-degenerate, Band 1, but sentiment-ordered with V=0.5455. **Persona discovery moves inside region A; G-300 decides whether the mixed middle cluster is a persona.** | RQ1 claim | closed |
| 4 | Correct the S0 table in the pipeline spec | — | after 1–2 |
| 5 | Frame the register finding in the **stylometry / authorship** literature or the **machine-generated-text detection** literature? Writing decision, Sabbir's | Ch.2, Ch.4 | Sabbir |
| 7 | **Three personas or two?** The design posits three; region A has two sentiment classes and region B three. K is settled by the S2 master K-table (pipeline gate G1), not by the label count — but the mismatch must be resolved before S3 | S2 → S3 | after the re-run |
| 8 | If open decision 0 returns "region B was generated", does the thesis **exclude** it, **keep** it as a labelled condition, or **make the contrast the contribution**? Different from 0b, which only settled the corpus | Ch.1 framing | after 0 |
| 6 | Should `s2_pilot.py` persist cluster assignments? Every follow-up question currently needs a full re-run or a reconstruction from the printed crosstab | future analyses | Sabbir |

---

## Immediate next actions

**Nothing is blocked any more.** The provenance question is closed as
unresolvable, the scope decision is made (full corpus), and the code for the
next run is written and pre-registered.

1. 🔬 **Re-run both S2 configs on Kaggle** (one notebook, two runs). Produces
   `ARI(cluster, region)` and the region-A robustness check, and persists
   cluster assignments. Interpretations are pre-registered in `protocol.md`
   (RQ1-A) **before the run** — re-read that table before reading the numbers.
2. **Freeze the split** on `Sentiment × region` (6 strata) once cluster
   assignments exist. This closes open decisions 1 and 2.
3. **Run the plot harvest** — `plots_scrape.py`, then `--sample 130`, then
   **read the 130**. The quality gate counts characters and sentences; it cannot
   tell a plot from a production-history paragraph. Anything that is not a plot
   gets deleted from the harvest and the sample **redrawn**, never patched.
4. Read Huang et al. (ICLR 2024) → fill its `related_work.md` entry.

## Artifact index — every file in `results/`, and what it is for

Added 2026-08-01 after three files were found orphaned: present on disk,
referenced nowhere. A result nobody can find is a result nobody can check.

| File | What it holds | Standing |
|---|---|---|
| `s0_data_xray.md` | S0 verification against the raw file | ✅ current |
| `s1_cleaning_log.json` | cleaning counts → n = 4,730 | ✅ current |
| `s2_pilot_ari_trapcheck.md` | full-corpus trap-check **+ the region table** | ✅ current — **the decisive result** |
| `s2_cluster_assignments.csv` | per-review cluster, sentiment, region (n=4,625) | ✅ current — input to the split freeze and G-300 |
| `s2a_regionA_trapcheck.md` | trap-check on the organic corpus alone | ✅ current |
| `s2a_regionA_cluster_assignments.csv` | per-review cluster for region A (n=1,897) | ✅ current — **G-300 stratification comes from HERE**, not the full-corpus file |
| `s2b_register_probe.md` | register measurements by class | ⛔ **framing superseded** by `s2c` — the file now carries a banner saying so |
| `s2b_register_features.csv` | per-row orthographic features (n=4,730) | supporting data for `s2b`; measurements stand, framing does not |
| `s2c_region_split.md` | the two-corpora finding | ✅ current — supersedes `s2b`'s framing |
| `s2_threshold_audit_sheet.csv` | blinded 0.90-vs-0.95 review sheet, 38 items | ⏸ **generated, never annotated.** Parked: the threshold question turned out to be downstream of the region split |
| `s2_threshold_audit_key.csv` | the blinding key for the above | ⏸ do not open until the sheet is filled |
| `plots_harvest_report.md` | harvest yield, reject reasons, heading tally | ✅ current (4th harvest) |
| `env_snapshot.json` | local Windows environment | ✅ current |
| `env_snapshot_s2_kaggle.json` | **the environment S2's numbers came from** — Kaggle T4, scikit-learn 1.6.1 | ✅ current — cite this, not `requirements.lock.txt`, for S2 |

## Infrastructure state (2026-07-30)

| Item | State |
|---|---|
| Text artifacts | LF on every host — `provenance.write_text_lf()` + `.gitattributes eol=lf`. The 2026-07-28 phantom diff on three `results/` files was pure CRLF churn, **zero content change**, now resolved. |
| S2 test coverage | `test_s2_verdict.py` 8/8 (verdict bands ↔ pre-registration) + `test_s2_numeric.py` 15/15 (dedup core vs brute force). `cluster_and_ari` is **not** covered locally — needs scikit-learn/scipy, exercised on Kaggle. |
| `env_snapshot.py` | `--out <path>` writes a snapshot without touching `requirements.lock.txt`; refuses `--out requirements.lock.txt`. Mandatory on any non-local host. |
| Git hook | `core.hooksPath = .githooks` — confirmed enabled. |
