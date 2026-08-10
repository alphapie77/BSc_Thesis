# STATUS — single source of truth for "where are we"

**Last updated:** 2026-08-11 (**pipeline cross-check: 10 new deviation rows; RQ3 gaming reframe rejected by search; English arm formally deferred; Verifier-B definition disambiguated**) · **Phase:** 1–2 COMPLETE → **3 (verifier training)**
**Week:** 3 of 14

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
| 4 | **Frozen G/R1/R2 split** | ✅ **FROZEN 2026-08-01.** G=**300** · R1=**2,162** · R2=**2,163** · dev=**200**, over the 4,625 deduped rows. Stratified on `Sentiment × region` (not cluster — the full-corpus clustering is a corpus detector; deviation logged). Every part matches the corpus to within **0.1pp** on both variables; zero overlap. Script refuses to overwrite; `tests/test_split_map.py` pins the invariants. | `data/splits/split_map_v1.json` | 2026-08-01 |
| 5 | S2 pilot: near-dup + ARI trap-check | ✅ **run** 2026-07-30 (Kaggle T4, commit `e3d8e43`) — ARI **0.1793**, Band 1, not degenerate | `results/s2_pilot_ari_trapcheck.md` | 2026-07-30 |
| 5b | S2b register probe (**exploratory**) | ✅ run — class 2 differs structurally from classes 0/1; **RQ1 persona claim suspended** | `results/s2b_register_probe.md` | 2026-07-30 |
| 5c | Provenance query to the data collector | ✅ **CLOSED 2026-07-30 — unresolvable.** Answer: collected from **many different places, all organic; which rows came from where is not remembered, and no metadata was kept.** That is an honest answer, and the pre-committed consequence applies: the measurement stands as the best available evidence, reported as exploratory, with the gap stated in Limitations. **Do not re-ask.** | `docs/provenance_query.md` | 2026-07-30 |
| 5d | S2c region split (**exploratory**) — the corpus is two corpora | ✅ run — **60% of rows carry a uniform, non-organic signature** | `results/s2c_region_split.md` | 2026-07-30 |
| 5e | `ARI(cluster, region)` — the decisive test | ✅ **RUN 2026-07-31. Pre-registered outcome 1 fires.** ARI(region) **0.4813** vs ARI(Sentiment) **0.1793**, at every threshold. Binary recast: ARI 0.7487, φ 0.861, **93.3% accuracy at identifying which corpus a review came from**. The clusters are a corpus detector, not personas. | `results/s2_cluster_assignments.csv` | 2026-07-31 |
| 5f | S2-A: trap-check on region A alone | ✅ **run** — n=1,897, **not degenerate** (29.5/38.9/31.6), ARI **0.1804 → Band 1**. But V=**0.5455** (up from 0.4104) and the clusters are visibly sentiment-ordered; ARI is capped because K=3 meets 2 classes — **pre-registered as weakening this evidence**. G-300 is the arbiter. | `results/s2a_regionA_trapcheck.md` | 2026-07-31 |
| 5g | **Gate G1 — master K-table (region A)** | ✅ **RUN 2026-08-03. SELECTED K = 2** — the only K clearing the pre-registered PS ≥ 0.80 (**0.860**; K=3 = 0.669). Bootstrap ARI 0.940±0.029, shares 39.7/60.3, ARI vs Sentiment **0.152 → Band 1** (so it is *not* the sentiment split). 🔴 **But three indicators say there are no clusters at all**: silhouette peaks at **0.053**, the gap statistic **rises monotonically and selects no K**, and **HDBSCAN calls 100% of points noise**. A reproducible bisection of a continuum, not two discovered groups. | `results/s2d_ktable_regionA.md` | 2026-08-03 |
| 5h | **S2e — what the K=2 cut is made of** | ✅ **RUN 2026-08-03.** `length_auc` **0.6764 → `LENGTH_CONFOUNDED`** (RQ1-D band [0.65, 0.75)): G-300 may proceed, but the guideline must prevent annotators succeeding on length alone, and length is reported beside every persona claim. Strongest surface feature `n_chars` 0.6810 — **below** the 0.80 headline bar, so no regular-expression finding. 🎁 **Unexpected:** cluster 1 is **33% shorter yet ~18% richer** in word types at equal budget — formulaic praise vs short specific complaint. Guard reproduced G1's silhouette and ARI to <1e-6. | `results/s2e_regionA_k2_profile.md` | 2026-08-03 |
| 5i | **S2f — the residual test** (voluntary at Band 1) | ✅ **RUN 2026-08-03.** A: min AUC 0.6115 → length independent of sentiment. B: min \|φ\| 0.3133 → sentiment independent of length in every band. **C: lift +9.80 pp → `RESIDUAL_SURVIVES`** — valence and verbosity do **not** account for the cut — but ⚠️ **0.2 pp from the cutoff, and reported as weak.** D: richness inversion holds in **all 4** bands. Decomposition: sentiment alone +9.28, length alone +5.22, both +9.80 — **length adds only +0.53 pp once sentiment is known.** Test C is a resubstitution upper bound, by deliberate choice. | `results/s2f_regionA_k2_residual.md` | 2026-08-03 |
| 5j | **G-300 — the instrument** (sheets, guideline, scorer) | ✅ **BUILT 2026-08-04, not yet annotated.** Pre-registered as RQ1-F before any item was rated. 0–3 ordinal *engagement specificity*; annotators see **only** `item_id` + review text. Gate 1 = Krippendorff α (ordinal), bands 0.667 / 0.80. Gate 2 = directionless AUC vs `cluster_k2` on the **123** region-A items, decided by a **permutation null** (5,000 shuffles, α = 0.05) and repeated **within each length band**. ⚠️ Gate 2's rule was changed from a bootstrap CI to a permutation test *before any annotation* — the old rule made `NEGATIVE` nearly unreachable (chance's own p95 at n = 123 is ≈ 0.60, not 0.50). 18 tests, incl. one that fails if the null verdict ever becomes unreachable again. | `data/annotation/`, `docs/g300_annotation_guideline.md` | 2026-08-04 |
| 5k | **G-300 round 1 — the human validation** | ⚠️ **RUN 2026-08-05. `UNRELIABLE` → RQ1 INCONCLUSIVE, not negative.** α(ordinal) **0.4970** < 0.667, so Gate 2 was **not computed**, per RQ1-F. **But the raters agreed strongly**: exact **75.5%**, within-1 **98.7%**, **Gwet AC1 0.871** ⚠️ (over-read — see the 2026-08-08 correction: Vach & Gerke 2023 show AC1 rises mechanically with prevalence skew, so it is *not* independent evidence here; the raw 75.5%/98.7% are). α is low because the scale collapsed — **68%/76% of all ratings are the single value "2"**. Kappa paradox, and `gwet2008ac1` was already listed as its guard. **Cause: Claude's calibration advice** (*"names an aspect → at least 2"*) — nearly every review names something, so everything moved to 2 and the 2-vs-3 boundary was never sharpened. Rescue attempted and failed: binary recast (3 vs ≤2) gives κ **0.5285**, still short. **No round 2 — annotator time is exhausted.** | `results/g300_agreement.md`, `results/g300_ratings.csv` | 2026-08-05 |
| 5l | **RQ1-G — region B replication** | ⚠️ **RUN 2026-08-08. NO REPLICATION** (pre-registered outcome 2). K = 2 matched (PS **0.818**, bootstrap ARI **0.962**) but the **signature did not**: `length_auc` 0.550 → `NOT_LENGTH` (A was 0.676 → `LENGTH_CONFOUNDED`), richness inversion holds in **1 of 4** bands (A: 4/4). 🎁 **The more useful finding:** B's cut is a near-perfect 49.4/50.6 bisection correlating with **nothing measurable** — every surface AUC 0.50–0.58, ARI vs Sentiment 0.011, silhouette 0.039, HDBSCAN noise 96.7% — **yet it clears PS ≥ 0.80.** Region B is a **negative control showing the pre-registered stability rule can pass a contentless cut.** | `results/s2d_ktable_regionB.md`, `s2e/s2f_regionB_*` | 2026-08-08 |
| 5m | **RQ1-H — human validation, attempt 2** | ✅ **RUN 2026-08-08. `HUMANLY_PERCEPTIBLE` — RQ1 WINS.** Gate A: **39/50 (0.780)** and **42/50 (0.840)** against a chance rate of **0.25**, p < 1e-15, far above the pre-registered 0.45. Gate B: both **34/40 (0.850)** vs chance 0.50 → **the construct IS specificity**. Obtained with **length matched to within 2 words** — and a length heuristic scores **0.16, below chance**, so the strongest confound is not merely controlled but inverted. Inter-annotator 70%/75%; agreement matches the 0.667 expected under independent errors, so no lockstep. 🎁 **Both annotators reported the items looked alike — then scored 0.78/0.84.** An implicit stylistic distinction: real, perceptible, not articulable. That is also why attempt 1 failed — rating an unnameable property is far harder than spotting the odd one out. | `results/intrusion_agreement.md`, `results/intrusion_responses.csv` | 2026-08-08 |
| 6 | protocol.md seal + supervisor signature | ✅ **SEALED 2026-08-10 for Phases 1–3; signature outstanding.** Reframed from *"FROZEN PRE-ANALYSIS PLAN"* to an **append-only record** — the old header promised a single freeze after Step 5, which ran 2026-07-30 and was followed by 30+ amendments, so the promise was false on its face. The claim now made is narrower and checkable by `git log`: every section dated, **no section edited after the run it governs**, superseded text struck through not deleted, every departure logged. Five body corrections applied (4,422→4,625; 3→2 annotators; "3 personas"→2 axis levels; the *"untestable in principle"* paragraph corrected 11 days after STATUS was; banners on RQ1-B and §S3.2). Four missing deviation rows added — **RQ1-G and RQ1-H had full pre-commitment sections and no log entry**, RQ1-H being the largest departure in the document. RQ2–RQ5 seal separately at their first run. | `docs/protocol.md` | 2026-08-10 |
| 7 | **S3.2 + S3.4 pre-registration** — Phase 3 opened | ✅ **WRITTEN 2026-08-08, before any backbone was downloaded.** Ablation goes **4 → 7 arms** (+IndicBERTv2, +SetFit, +BERT-NLI), **5 seeds not 3**, and the winner is decided by **paired bootstrap**, not by best mean ± SD. 🔴 **The literature contradicted our own protocol from the day before:** Bethard (2022) names "vary the seed to build a score distribution for model comparison" as a *risky* use of seeds — exactly what we had committed to. Calibration demoted from "hidden contribution" to **descriptive** (dev = 82 rows; 10 bins ≈ 8 samples/bin). 🎁 **The ablation's most likely outcome is pre-registered as a tie**, because the 2025–26 Bangla literature reports **three different winners on the same dataset** — so "BanglaBERT because it is Bangla-native" cannot be defended by citation, and a tie is registered as publishable. | `docs/protocol.md` §S3.2, §S3.4 | 2026-08-08 |
| 8 | **S3.2 attempt 1** — the backbone ablation, first real run | ⚠️ **CRASHED 2026-08-09** (Kaggle T4, commit `a2986db`) at **arm 6 of 7**, on `import setfit`: setfit's module chain imports `transformers.training_args.default_logdir`, removed in transformers 5.x, which Kaggle ships. `bert_nli` never ran. ~4 GPU-hours spent. **The five completed numbers are DISCARDED, not carried forward** — all seven re-run under `transformers<5`, because Coakley et al. (2022) measured **>6 pp** of accuracy variation from environment alone and our whole between-arm spread is **2.98 pp**, so a mixed-environment table would measure library version more than backbone. 🎁 **Not wasted:** the discarded run establishes (i) the task is **highly learnable** — 0.94–0.97 across five backbones, expected for a label derived by clustering LaBSE embeddings, i.e. *label reproduction*, exactly what the 2026-08-08 deviation said this measures; and (ii) **the spread is smaller than documented environment noise**, which is itself evidence for the pre-registered `TIE` and is now reported beside the verdict. **Prevention:** `--check-arms` imports every arm's dependencies on CPU in ten seconds, and the runner calls it as Gate 0. | discarded; no file in `results/` | 2026-08-09 |
| 9 | **S3.2 — the backbone ablation, COMPLETE** | ✅ **RUN 2026-08-10** (Kaggle T4 ×1, commit `e3afa71`, transformers 4.57.6). **Verdict `TIE`**, and the pooled-across-learning-rates rule **agrees** — so the winner's-curse question is settled by evidence, not argument, and the ~30% extra compute for inner k-fold is not spent. All **21** pairwise comparisons non-significant after BH; smallest p **0.096**. Tie-break `[smallest_params, banglabert]` → **BanglaBERT** (110M). 🎁 **The tie is a measurement statement, not a shrug:** between-arm spread **0.0348** vs MuRIL's own seed SD **0.0391** — the variation *inside one arm* exceeds the variation *between all seven*, and Coakley et al. (2022) put environment noise alone at >6 pp. ⚠️ **`setfit_labse` contributed ONE configuration, not ten** — its `lr` never reached SetFit and its seed was inert (proved: identical `train_loss` to 18 significant figures across all ten runs, 1 distinct prediction vector out of 10). Its SD of 0.0000 is **not** stability. Code fixed, arm **not** re-run. ⚠️ **No ranking below the top may be quoted** — XLM-R is 6th under one rule and 7th under the other. | `results/s3_backbone_ablation.{md,json}`, `s3_backbone_per_seed.csv`, `env_snapshot_s3_kaggle.json` | 2026-08-10 |
| 10 | **S3.2b — the baselines the ablation lacked** | 🔴 **RUN 2026-08-10. `CIRCULARITY_CONFIRMED`, past its own threshold.** A **frozen LaBSE + logistic regression** scores **0.9866** against the best fine-tuned arm's **0.9647** — the probe is **1.8 dev items AHEAD**, and makes **one error on 82 items**. Majority **0.3926**, length rule **0.6197**. **Cause is structural, not a bug** (verified: train/dev disjoint, error count reconstructs the F1 exactly): `cluster_k2` came from k-means **on LaBSE embeddings**, so the label is near-linear in that space. **Consequences: the seven-arm table may support NO claim about backbones; the `TIE` is re-explained as near-saturation by construction; and fine-tuning cost accuracy rather than adding it.** Not affected: RQ1-H showed humans perceive the distinction (0.78/0.84 vs 0.25), so the label is real — it is simply linear in LaBSE space. | `results/s3b_baselines.{md,json}` | 2026-08-10 |

## Parallel tracks (no step blocks these — but they block later steps)

| Track | Target | Done | Blocks | Risk |
|---|---|---|---|---|
| Bangla plot synopses | ~~130~~ → **120 = 30 dev + 90 eval** (deviation logged 2026-07-31) | ✅ **FROZEN** — 124 harvested, **4 rejected on human review** (BN024 production history, BN042 director's death, BN068 theme commentary, BN113 a 3-sentence fragment). Split assigned once with seed 42; `plots_check` refuses to reassign. Every row carries `revision_id` + licence. | S6 evaluation | 🟢 **done** — BN113 passed every mechanical gate and is unusable, which is the case for human review in one row. ⚠️ **Outstanding: CC BY-SA attribution** (3-item checklist in the dataset card) must be discharged before submission. One kept plot (BN072 দ্য নেমসেক) is an English-language film — Sabbir's scope call, recorded in the notebook |
| Base-paper reading | **6** Tier-1 | **6 briefed** — `docs/base_papers_brief.md`. Depth: Huang 📗, Kamoi 📗, Illusion 📗, MoP 📘 partial, Sands 📙, Cobbe 📙. ⚠️ **All by Claude; Sabbir has read none.** ⬛ Outstanding: MoP §4.1 (datasets / MAUVE / K selection — MathML-blocked), Sands results section, Cobbe numbers. | Ch.1, Ch.2, **§5.1 design** | 🔴 **highest.** Produced 3 open decisions (9, 10, 11) against a pre-registered ablation table, plus 🎁 **Kamoi §5.2 states our gap in a TACL survey's own words**: fine-tuning for self-correction is *"unexplored for small training data"* — and R1 is 2,162 rows |
| Gold-300 annotation | ~~300 × 3 annotators~~ → **300 × 2, both independent** (deviation logged 2026-08-03) | **instrument built 2026-08-04, annotators secured 2026-08-04; 0 items rated.** | RQ1 validation | 🟡 **DECISIVE, and now unblocked.** ✅ **Sabbir does not annotate** — two independent annotators recruited, neither in CSE, neither told what the study is looking for. The author-annotator problem recorded on 2026-08-03 is **closed**, and with it the "partially independent" caveat that would have gone in the abstract. Remaining, and reported not worked around: (i) two annotators means **no majority**, so disagreements are *not* resolved — the gold value is the mean and the disagreement rate is a result; (ii) only **123 of the 300** are in region A (the split was stratified before G1 chose K), so Gate 2 runs on the 123 with its power stated as a number and the frozen split untouched. G1 found a reproducible 2-way split in a space with *no* cluster structure (silhouette 0.053, monotone gap, 100% HDBSCAN noise). Whether that split is an audience distinction or an artefact of cutting a continuum **cannot be settled by any statistic** — only by whether three annotators can reliably tell the halves apart. If they cannot, RQ1 is a negative result, which RQ1-C already recorded as publishable. Must be stratified on the **region-A** clustering, never the full-corpus one — that one is a corpus detector. G-300 is what decides whether cluster 1 (the 54/46 mixed cluster) is an audience persona or just the ambivalent reviews; nothing else can. |
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
| Selected K, region A | 3 (design) | **2** — the only K clearing PS ≥ 0.80 (0.860 vs 0.669 at K=3) |
| `length_auc` of the K=2 cut | — | **0.6764** → `LENGTH_CONFOUNDED`; strongest surface feature `n_chars` 0.6810, below the 0.80 headline bar |
| φ(cluster_k2, Sentiment) | — | **0.3981** (χ² 300.7, accuracy 69.5% vs 50.2%) — **while ARI is 0.1522**. Both are correct; ARI is the weaker instrument here |
| Sentiment + length explain (upper bound) | — | **+9.80 pp** over a 60.25% baseline → `RESIDUAL_SURVIVES`, **0.2 pp from the cutoff** — weak, and reported as weak |
| Length's contribution once sentiment is known | — | **+0.53 pp** (sentiment alone +9.28, both +9.80) — length is largely redundant with sentiment at the level of prediction |
| Lexical richness inversion | — | cluster 1 is **33% shorter yet ~18% richer** at equal budget, and this **holds in all 4 length bands** — the strongest pre-G-300 evidence of a difference in kind |
| R1 rows carrying a persona label | — | **804 of 1,962 (41.0%)** — the other 1,158 are region B, which has no K=2 label. Same for R2: **888 of 2,163**. Phase 3 and the RAG index both need labelled rows, so this is a hard input constraint, not a detail |
| `dev` vs `R1` | "zero overlap between any two parts" | **`dev` ⊂ `R1` by design** (200 rows), stated in the split map's own `_contract`. The parts sum to 4,825 and the union is 4,625; nothing is wrong, but the "zero overlap" phrasing above was imprecise and is corrected here |
| Verifier-A training n | — | **804** labelled region-A rows (481 / 323), dev held out |
| Verifier-B training n | — | **888** (531 / 357) — R2, disjoint by the frozen split's contract |
| Dev slice for the symbolic scorer | 200 | **82** labelled (53 / 29) — §3.5 assumes 200; it has 82 |
| Gold-300 usable for Phase 3 validity | 300 | **0** — G-300 gave specificity ratings, not cluster labels, and they failed reliability |
| S3.2b: frozen LaBSE probe | — | **0.9866** — **1 error on 82 items**, and **1.8 dev items ABOVE** the best fine-tuned arm. The label is near-linear in its generating embedding space |
| S3.2 trivial baselines | — | majority **0.3926**, best length rule (fitted on train, n_words ≤ 7) **0.6197** — the arms are not the class prior or the length confound |
| What the S3.2 ablation may claim | "which backbone is best" | **nothing about backbones.** It demonstrates the label is linearly recoverable from LaBSE |
| S3.2 verdict | — | **`TIE`** under both aggregation rules (headline and LR-pooled), 21/21 pairs non-significant, min p **0.096** |
| S3.2 between-arm spread | — | **0.0348** (banglabert 0.9647 → bert_nli 0.9298) — **smaller than MuRIL's own seed SD of 0.0391** |
| Verifier-A backbone | BanglaBERT (assumed) | **BanglaBERT**, but by the pre-registered **tie-break**, not by performance. The data did not choose. |
| `setfit_labse` effective runs | 10 | **1** — `lr` never reached SetFit and the seed was inert; SD 0.0000 is an artefact, not stability |
| Tokens in a two-encoding Unicode group | — | **10.44%** of 46,758 (267 collapsing groups). φ(region, encoding form) = **−0.3245** — an independent corroboration of fact (split) from orthography |
| Inferential status of S2e / S2f statistics | treated as tests | 🔴 **DEMOTED to descriptive profiling 2026-08-10.** φ = 0.3981, χ² = 300.7 and every surface AUC are **post-clustering inference on the rows that defined the partition**. Chen & Witten (2023) show this inflates Type I error and produces large between-group differences *even when no population categories exist*. **No p-value from S2e/S2f is evidence that the halves differ.** S2f Test C already self-flagged as a resubstitution bound; the flag simply was never generalised. **RQ1-H does not inherit this** — held-out items, annotators blind to the partition — which is why the human validation, not the profiling, carries RQ1 |
| What PS ≥ 0.80 establishes | "the K is stable, therefore real" | **necessary, not sufficient.** Region B cleared it at **0.818** on a cut correlating with nothing measurable (RQ1-G) — the exact failure mode von Luxburg (2010) describes and Pinto et al. (2026) reproduce in simulation at ARI 1.00, SD 0.00 |
| Verifier-B's definition | "the fine-tuned BanglaBERT **from S3.2**" | 🔴 **the S3.2 BanglaBERT *recipe*, RETRAINED on R2 (888 rows).** `configs/s3_backbone.yaml` sets `role: A` → every S3.2 arm trained on **R1**. The literal reading would have put A and B on the same data and voided inviolable rule 6. No result affected; corrected before any training |
| §5.1 generation count | 90 × 3 personas × 8 = **2,160** per language | **1,440** (90 × **2** × 8). Stale since K=2 was selected on 2026-08-03 — a one-third reduction in experiment size, cost, and CI width |
| Does symbolic scoring resist gaming? | assumed yes (proposed 2026-08-11) | **NO — refuted before it was written.** Mahmoud et al. (2026): rule-based rewards *are* hacked; **presence-based criteria are the worst case**, and §3.5's features are almost all presence/count-based. Our Reflector also *names the failing rule to the Writer*. Symbolic is plausibly the **most** gameable component here |
| Does cross-family separation establish verifier independence? | assumed yes (decision 16) | **necessary, not sufficient.** Kuai et al. (2026): entanglement is widespread intra- *and* cross-family; **plain correlation cannot detect it.** A dev-slice failure-manifold audit (BEI/CIG) is now pre-registered before any RQ5 gap is interpreted |

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
| ~~**1**~~ | ~~Final `usable_n` after near-dup removal~~ ✅ **CLOSED 2026-08-08 — answered, and the answer has been in the file since 2026-08-01.** `usable_n` = **4,625** at the pre-registered t = 0.95 (105 rows removed), which is what the frozen split map partitions. The row said "blocked by 0", but decision 0 closed on 2026-07-30 and the split froze on 2026-08-01; nobody came back to close this. **Housekeeping failure, recorded rather than tidied away** — an open-decision table that lists settled questions is a table people stop reading. | — | ✅ closed |
| ~~**2**~~ | ~~Near-dup threshold: 0.90 gives Band 2, 0.95 and 0.98 give Band 1~~ ✅ **CLOSED 2026-08-08 — held at the pre-registered 0.95, and never revisited.** The audit sheet (`s2_threshold_audit_sheet.csv`, 38 items) was generated and **deliberately never annotated**: 52% of the contested band is class 2, i.e. region B, and the region split (fact (split)) made the threshold question downstream of a larger one. The threshold was not tuned, and no result depends on the choice between 0.95 and 0.98. Same "blocked by 0" staleness as decision 1. | — | ✅ closed |
| 3 | ~~Do personas survive the trap-check?~~ **ANSWERED 2026-07-31.** On the full corpus the clusters are a **corpus detector** (93.3% accuracy) — no persona claim stands there. In region A they are non-degenerate, Band 1, but sentiment-ordered with V=0.5455. **Persona discovery moves inside region A; G-300 decides whether the mixed middle cluster is a persona.** | RQ1 claim | closed |
| 4 | Correct the S0 table in the pipeline spec | — | after 1–2 |
| 5 | Frame the register finding in the **stylometry / authorship** literature or the **machine-generated-text detection** literature? Writing decision, Sabbir's | Ch.2, Ch.4 | Sabbir |
| ~~7~~ | ~~Three personas or two?~~ | — | ✅ **CLOSED 2026-08-03: TWO.** K=3's prediction strength is 0.669 against a cutoff of 0.80 fixed two days earlier. The design gave way; K=3 is retained as the theory-motivated secondary. |
| ~~**12**~~ | ✅ **CLOSED 2026-08-10 — the engagement-specificity AXIS. Both *persona* and *cluster* are retired.** Sabbir delegated ("you can make the best decision"); the choice and reasoning are Claude's, recorded as such in `protocol.md`'s deviations log. **The literature moved the answer past both options that were on the table.** Pinto et al. (2026) obtain k=2, silhouette ≈0.31, ARI 0.999±0.001, sizes **50.6/49.4** on 8,360 psychometric respondents — numerically almost our region B (49.4/50.6) — and read it as *"geometric stratifications of a latent continuum rather than evidence for discrete subtypes"*, with the line **"Stability, therefore, is not equivalent to validity."** Cornelissen et al. (2026) publish a negative clusterability result and show a prior four-type typology was an artefact of k-means placing centroids on principal axes. So *persona* was already banned; ***cluster* does not survive either**, because the literature reserves it for structure we do not have (silhouette 0.053, monotone gap, HDBSCAN 100% noise). Permitted: **axis, gradient, the cut, level**; `cluster_k2` survives as a frozen *variable name* only. 🎁 **Our position is stronger than either paper's, and must be stated in these words: neither had human validation.** RQ1-H did — 0.78/0.84 vs 0.25 chance, length-matched, length heuristic below chance. The claim is therefore sharper than "the cut is arbitrary": **geometrically a line through a continuum, and people can nonetheless see it.** ⚠️ **Title wording remains Sabbir's; the constraint is not.** ⬛ superseded text: ~~**Title and framing — REOPENED 2026-08-08.**~~ It was closed by force on 2026-08-05 because human validation was inconclusive. **It no longer is** (RQ1-H: 0.81 against 0.25 chance, and the construct is specificity). What the evidence now supports is *a humanly recognisable two-way distinction in engagement specificity* — **not** "two audience types", because G1 showed no cluster structure. Whether the word *persona* is permitted again is **Sabbir's wording call**; the bound is that the object is a **cut through a continuum that people can see**, not two discovered groups. ⬛ superseded text: ~~CLOSED BY FORCE 2026-08-05.~~ G-300 round 1 returned α = 0.4970 → inconclusive, and no annotator time remains for a round 2. **The word *persona* may no longer describe the K = 2 halves anywhere** — not in the title, not in Ch.1, not in the conference draft. They are **clusters**; generation is **cluster-controlled**. What the thesis may claim: *"a stable two-way partition whose correspondence to a human-perceived distinction is undetermined."* ⚠️ **The title still says "Audience Simulation" and the pipeline still says "three personas" throughout** — both need a pass. Sabbir's wording, but the constraint is no longer optional. | Ch.1, title, all framing | 🔴 **Sabbir — wording only; the constraint is fixed** |
| ~~**12-old**~~ | ~~**Title and framing**~~ — "three personas" appears throughout the pipeline, the pre-defence report and the conference draft. All of it now needs revisiting for two. **And the persona language itself needs qualifying**: what G1 found is a stable 2-way partition of a space with no cluster structure, which is not the same as discovering two audience types. | Ch.1, title, all framing | 🔴 **Sabbir** |
| **13** | **Unicode encoding variants.** 10.44% of tokens sit in a group where the same word exists in two encodings (অভিনয় as `U+09DF` 188× vs `U+09AF U+09BC` 152×; নায়ক and নায়িকা each appear **twice** in S2e's log-odds table for this reason). The inviolable rule forbids normalising the corpus, and **nothing has been changed**. Two open questions, both Sabbir's: (a) should the *vocabulary tables* additionally be shown NFC-collapsed, as a reporting variant only? (b) LaBSE's tokenizer sees the two forms as different, so the variation is **inside the embedding** — does that go in Limitations, or does it become a measurement (φ(region, encoding) = −0.3245 is already an independent corroboration of the split)? | Ch.4, Limitations | 🔴 **Sabbir** |
| ~~**14**~~ | ~~Phase 3 + RAG scope~~ ✅ **CLOSED 2026-08-05 — option (a): region A only, n = 804.** Sabbir delegated the choice; the reasoning is Claude's and is recorded as such in `protocol.md` §"Scope decision: Verifier-A and the RAG index run on region A only". Option (b) survives as a **pre-registered robustness check** with all three outcomes pre-committed. ⚠️ **Cost, stated not buried: RQ1-B as written cannot run** — it needs region-B persona labels, which do not exist. It is **re-scoped to sentiment classification**, a task both regions support with real labels; its purpose (*"the register gap, quantified"*) and its three outcome bands carry over unchanged. **No claim about persona transfer across regions may be made.** | Phase 3, Phase 4, RQ2 | ✅ closed |
| ~~**14-old**~~ | ~~**Phase 3 + RAG scope: only 41% of R1 has a persona label.**~~ Verifier-A trains on persona labels and the RAG index retrieves *within the same persona label* (pipeline §4.2), but the K=2 partition exists **only in region A** — 804 of 1,962 R1 rows. Three options, and it is a scope call, not a statistic's: **(a)** run Verifier-A and the RAG index on **region A only** (n=804) — clean, consistent with "persona discovery moved inside region A", costs sample size; **(b)** propagate labels to region B by nearest region-A centroid → n=1,962, but every B label is an extrapolation and the register confound re-enters the training set; **(c)** cluster region B separately → different personas, comparability gone. **Recommended: (a), with (b) as a pre-registered robustness check.** Whichever is chosen must be registered *before* Verifier-A is trained. | Phase 3, Phase 4, **RQ2** | 🔴 **Sabbir** |
| ~~**16**~~ | ✅ **CLOSED 2026-08-10 — Verifier-A = frozen LaBSE probe, Verifier-B = fine-tuned BanglaBERT (cross-family).** Claude's recommendation, delegated and endorsed by Sabbir; the reasoning is Claude's and is recorded as such in `protocol.md` §S3.2c. The wall is now methodological as well as data-level (ELECTRA vs BERT, Bangla-specific vs multilingual, fine-tuned vs frozen) where before it was only a split. Mahmoud et al. (2026) make cross-family evaluation the standard; Wang et al. (2026) name evaluator–policy co-adaptation as the failure two probes would have been; Baker et al. (2025) kill the objection that a weaker evaluator is a flaw. 🎁 **The S3.2 table is repurposed rather than discarded** — it cannot speak to backbones, but it is the evidence BanglaBERT is a viable independent evaluator. ⚠️ **RQ5 also gains a second signal**: Zhou (2026) shows judge errors transfer across families and ensembles still accept 55%, so an invariance/perturbation check (Shihab et al. 2025) is added alongside the A-vs-B gap. ⬛ superseded text: ~~🔴 Verifier-A / Verifier-B design, REOPENED by S3.2b.~~ The frozen LaBSE probe is now the strongest, cheapest and best-calibrated candidate for Verifier-A — but **if B is also a probe, A and B agree by construction and RQ5's Goodhart test dies**, which inviolable rule 6 exists to prevent. Three options in `protocol.md` §S3.2c: **(a)** A = probe, B = fine-tuned BanglaBERT (different families — arguably a *stronger* wall than the original, where A and B differed only by split); **(b)** both probes on disjoint splits (cheapest, but abandons RQ5 and must say so); **(c)** A = fine-tuned BanglaBERT anyway, paying ~2 pp to keep the in-loop verifier independent of the label's own geometry — **which S3.2b makes genuinely interesting, since a verifier that is a linear function of LaBSE may be trivially gameable by a generator scored in that same space, and that is precisely the failure RQ5 hunts.** Must be registered **before** Verifier-A is trained. | Phase 3, Phase 4, **RQ5** | ✅ closed |
| 15 | Should `s2_pilot.py` also persist **UMAP coordinates** for the Ch.4 figure? Cheap to add, and re-running the embedding later just to draw a picture is wasteful. ⚠️ Inviolable rule 9 stands regardless: **UMAP is visualisation-only, never a clustering space.** *(Migrated 2026-08-05 from a duplicate table in `lab_notebook.md`, which was the only place it lived and had already gone stale.)* | Ch.4 figures | 🔵 open |
| ~~**8**~~ | ~~If open decision 0 returns "region B was generated", does the thesis exclude it, keep it as a labelled condition, or make the contrast the contribution?~~ ✅ **CLOSED 2026-08-08 — the antecedent can never be satisfied.** Decision 0 closed on 2026-07-30 as *unresolvable*: the collector does not remember which rows came from where, no metadata was kept, and the file has no venue, thread or timestamp column. **"Region B was generated" is a question the evidence cannot answer, so a decision conditioned on that answer cannot be taken.** What actually happened is recorded and is stronger than the conditional: region B is **kept as a labelled condition** (decision 0b, full corpus, region as a controlled factor), and RQ1-G then made the contrast genuinely useful — region B is a **negative control** showing the pre-registered stability rule can pass a contentless cut. The provenance question stays in Limitations, unresolved and labelled as such. | Ch.1 framing | ✅ closed |
| ~~6~~ | ~~Should `s2_pilot.py` persist cluster assignments?~~ | — | ✅ done 2026-07-31 |
| **9** | **Add an inference-cost-matched baseline to §5.1?** Huang et al. §6 require self-correction to be compared against baselines *of comparable inference cost*. Our rows 1–3 are single-call while 4–8 loop, so "row 6 beats row 1" may be partly a call-count effect. They also name **self-consistency / best-of-N at matched calls** as the strong baseline — our table has none. | §5.1 ablation, **the RQ2 headline** | 🔴 **Sabbir** — changes a pre-registered design |
| **11** | **Add row 7b — self-critique under an EXTERNAL role label?** The Self-Correction Illusion (arXiv 2606.05976) reports that relabelling a byte-identical claim from the model's own `<thought>` to a `user`/`tool`/`<memory>` role lifts correction rates by **23–93 pp**, and builds a training-free intervention on it. If 7b ≈ row 6, our trained verifier is not earning its cost — *a publishable negative result we would rather find ourselves*. If 6 > 7b, the contribution survives the cheapest known alternative. | §5.1, **the RQ2 claim** | 🔴 **Sabbir** |
| **10** | **Prompt parity between row 1 and the loop.** Huang et al. §5 document a reported "self-correction gain" that was really a more informative second prompt (81.8 standard vs 75.1 self-corrected, once the requirement was stated up front). Row 1's zero-shot persona prompt must specify the persona requirement as fully as the verifier feedback does. | §5.1 internal validity | 🔴 **Sabbir** |

---

## 🔴 Phase 3 real state (added 2026-08-11, after the pipeline cross-check)

Pipeline §3 asks for **five** deliverables. **One exists.** This was not visible
anywhere before today, because progress was being tracked against `protocol.md`
(which is Bangla-only and silent on §3.5) rather than against the normative spec.

| Pipeline §3 deliverable | State |
|---|---|
| **4 trained verifiers (A/B × bn/en)** | 🔴 **0 trained.** A and B are *designed* (decision 16), not built |
| Backbone-ablation table | ✅ done — then repurposed; may support no backbone claim (S3.2b) |
| Dual-accuracy table | ✗ **not producible** — logged 2026-08-08 |
| Calibration figure | ✗ not started |
| Rule table / symbolic scorer (§3.5) | 🔴 **not started — no code.** `grep -rl symbolic src/ configs/` returns nothing |

**The binding constraint is §3.5, not the verifiers.** §4.2's Critic is
`0.6×VerifierA + 0.4×symbolic`; with no symbolic component there is no Critic,
and with no Critic there is no loop. **Phase 4 cannot start.** `src/agents/` and
`src/eval/` are empty stubs.

⚠️ **English arm deferred** under the charter's own cut rule (deviation
2026-08-11). Cost: **RQ4 cannot be answered in its strong form** — the
cross-lingual claim reduces to the fertility covariate plus a zero-shot
reference.

## Immediate next actions

**Phase 3 is open and pre-registered (2026-08-08).** Order of work:

1. ✅ **S3.2 / S3.4 pre-registration written** — 7 arms, 5 seeds, paired
   bootstrap, calibration descriptive. Nothing in those two sections may be
   edited once the first run happens.
2. ⬛ **Citations** — the 16 method references behind the amendments go into
   `related_work.md` and `references.bib`, each verified through Consensus.
3. ✅ **Code, config, tests, runner notebook written** (2026-08-08). 24 tests
   pass. Dry run is byte-identical on the local sandbox and the Kaggle host.
4. ⚠️ **Attempt 1 crashed at arm 6** (2026-08-09) — see step 8. Environment now
   pinned; `--check-arms` added as Gate 0.
5. 🔬 **Re-run all seven arms** under `transformers<5`, via
   `notebooks/s3_backbone_kaggle.ipynb`. **Use Save & Run All (Commit), not an
   interactive session** — the checkpoint file lives in `/kaggle/working` and a
   fresh commit run re-clones, so checkpoints do *not* survive across sessions.
   `env_snapshot_s3_kaggle.json` is mandatory (fact (env)), and it must now
   record transformers 4.x, not the 5.0.0 of the crashed attempt.
6. 🟡 **`protocol.md` freeze + supervisor signature** (step 6) is now the oldest
   outstanding item and nothing blocks it.

⚠️ **Still Sabbir's, and none of it blocks Phase 3:** decision 12 (title and
whether *persona* is permitted again, reopened by RQ1-H), decision 13 (Unicode),
decision 5 (stylometry vs MGT framing), decisions 9/10/11 (they block **Phase 5**,
not Phase 3), the CC BY-SA attribution checklist, and — the highest-risk item in
this file — **reading the six base papers, none of which Sabbir has read.**

---

### Superseded note (pre-2026-08-08)

**Nothing is blocked any more.** The provenance question is closed as
unresolvable, the scope decision is made (full corpus), and the code for the
next run is written and pre-registered.

0. ✅ **S2e and S2f are done** (2026-08-03). `length_auc` 0.6764 →
   `LENGTH_CONFOUNDED`; the residual test returns `RESIDUAL_SURVIVES` at
   +9.80 pp, **0.2 pp from its cutoff**. Valence and verbosity do not account
   for the K=2 cut, and the richness inversion survives a length control in all
   four bands. **G-300 is now the decisive step**, not a confirmatory one: no
   cheaper instrument remains that could pre-empt the annotators.
1. 🟡 **Hand the sheets to the two annotators.** ✅ Secured 2026-08-04, both independent, Sabbir out. Give each: `docs/g300_annotation_guideline.md` + `data/annotation/g300_calibration_<A|B>.csv` (20 practice items, then **one** discussion), then `g300_sheet_<A|B>.csv` with **no further communication**. ⛔ Never `g300_key.csv` — it holds the answers. Then `python -m src.annotate.g300_score`.
   **Neither annotator is told what the study is looking for** — no clusters,
   no K, no hypothesis. A rater who knows the expected answer drifts toward it,
   and the agreement then stops being evidence.
2. 🔬 **Re-run the Kaggle notebook** — now three runs: both S2 configs **plus Gate G1** (one notebook, two runs). Produces
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
| `s2d_ktable_regionA.md` / `.csv` | **Gate G1** — K = 2..8 × seven criteria, PS, bootstrap ARI, gap, GMM-BIC, HDBSCAN, trap band at every K | ✅ current — **selected K = 2**; the only K clearing PS ≥ 0.80 |
| `s2e_regionA_k2_profile.md` | **what the K = 2 partition is made of** — `length_auc` 0.6764 → `LENGTH_CONFOUNDED`, surface AUCs, distinctive vocabulary, the reviews themselves | ✅ current — but **read with `s2f`**: its length verdict measures correlation, and s2f shows length adds only +0.53 pp once sentiment is known |
| `s2e_regionA_k2_assignments.csv` | per-review K=2 label + centroid distance + margin + n_words (n=1,897) | ✅ current — **G-300 stratification comes from HERE**; G1 never persisted its labels |
| `s2e_regionA_k2_features.csv` / `_logodds.csv` | per-row surface features; Monroe log-odds table | ✅ current — supporting data. **No claim rests on the log-odds list**, and note নায়ক/নায়িকা appear twice in it (open decision 13) |
| `s2f_regionA_k2_residual.md` / `_cells.csv` | **the residual test** — is the cut just valence × verbosity? Tests A–D, the decomposition, the 8 cells | ✅ current — **`RESIDUAL_SURVIVES`, but 0.2 pp from its cutoff.** Voluntary at Band 1; pre-registered as RQ1-E |
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
