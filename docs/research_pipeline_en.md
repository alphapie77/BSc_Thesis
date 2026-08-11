# Full Research Pipeline — From Raw 5k Dataset to Complete Thesis (v7 — English Edition)
## Title: *A Neuro-Symbolic Multi-Agent Framework for Pre-release Audience Simulation in Bangla Cinema: A Verifier-in-the-Loop Approach*

**Starting assets:** ~5,000 raw Bangla movie reviews (Mendeley) + the locked title. No code, no labels.
**Core claim (one sentence):** An external, cheap, task-trained verifier embedded in a generate–verify–refine loop measurably improves persona-controllability of LLM generation in a low-resource language (Bangla), compared to prompting alone — demonstrated against a matched English reference.

**Timeline:** ~14 weeks | **Compute:** free Colab/Kaggle GPU | **API cost:** ~~৳0 (Groq free tier primary; Gemini free tier secondary)~~ **৳0 — generation local on Kaggle T4 as of 2026-08-12 (§4.4 box); Gemini secondary unchanged**
~~**This file is the English mirror of `research_pipeline_bn.md` (v7). Both are normative; if they ever disagree, fix both.**~~

✅ **STRUCK 2026-08-11 — Sabbir's ruling (decision 18, option b): "bangla ar english to same e. dorkar ki bangla alada kore likhar."** `research_pipeline_bn.md` never existed, and it will not be written. **THIS FILE IS THE ONLY NORMATIVE PIPELINE.** Bangla stays in use for explanation and teaching — per Sabbir's standing request — but no Bangla document is normative, so there is no second file to keep in sync and no second file to go stale.

---

> ## 🔧 MAINTENANCE STATE — corrected 2026-08-11
>
> **This file had not been touched since 2026-08-01 — 55 commits.** Sabbir asked
> why the pipeline was not being maintained, and the answer is that it was not:
> progress was being written to `docs/STATUS.md` only, on the assumption that one
> "where are we" file was enough. It is not. **STATUS says where we are; this file
> says what we are supposed to do, and CLAUDE.md gives *this* file precedence on
> method.** A normative document that is the stalest document in the repo cannot
> perform that job, and anyone opening it cold — a supervisor, a reviewer, a
> future reader — would have seen a plan that died a week earlier.
>
> **Fixed in this pass:** the execution checklist below (8 steps were complete and
> unticked), the §5.1 generation count, and the persona-count arithmetic in the S6
> contract and §4.5.
>
> ---
>
> ### 🔧 SECOND PASS — 2026-08-11, later the same day, at the start of Phase 4
>
> **The first pass missed four live survivals of text it had already struck.**
> Decision 19 struck *"first-pass 60–70%"* and decision 17 struck the uniform
> τ grid, and both strikes were applied **to the §4.5 argument box and nowhere
> else**. Still reading as live instructions afterwards:
>
> | Where | What survived |
> |---|---|
> | checklist step 16 (line ~148) | the struck **`0.6×VerifierA + 0.4×symbolic`** |
> | checklist step 17 (line ~149) | *"first-pass 60–70%"*, **plus** *"blocked by open decision 17"* — closed — **plus its refuted premise** (*"79 of 82 dev items sit at confidence 0.998"*) |
> | S5 stage contract, Gate **G4** (line ~199) | *"if first-attempt pass rate doesn't reach 60–70%, raise τ"* |
> | §4.5 bullet list (line ~473) | *"Pick the operating point where first-attempt pass ≈ 60–70%"* — **four lines below the box that strikes it** |
>
> All four are now struck in place, not deleted, and each points at the section
> of `protocol.md` that replaced it.
>
> 🔑 **The lesson, recorded because it is now three-for-three.** `0.6/0.4`
> survived after its derivation was found not to exist; line 8's Bangla mirror
> survived because nobody followed the reference; and these four survived
> because a strike was written into the prose and not into the instructions.
> **Every one is a case where corrected and uncorrected text lived in the same
> file and only one copy was edited.** Striking a number now means grepping the
> whole file for it, not editing the paragraph where the argument happens to
> live — a reader scanning a checklist or a gate table never reaches the box.
>
> **Deliberately NOT fixed, because it is not Claude's to fix:** every occurrence
> of *persona* / *three personas* as **framing language** (§2.3 heading, §8.1,
> §8.2, the Ch.1 blueprint). That is **open decision 12 — Sabbir's wording call.**
> Each is flagged inline with 🔴 **[D12]** rather than silently rewritten. The
> *constraint* is already fixed and is not optional: K = 2, and the words
> *persona* and *cluster* are both retired in favour of **axis / gradient / the
> cut / level** (STATUS decision 12, 2026-08-10). Only the replacement wording is
> open.
>
> ⛔ **CORRECTION TO THIS BOX, same day, before Sabbir acted on it.** The first
> version said *"`research_pipeline_bn.md` has NOT received this pass"* and called
> the mirrors out of sync. **That was wrong, and wrong in the way this project
> keeps warning about: it was written from line 8 rather than from the disk.**
> `research_pipeline_bn.md` does not exist and never has -- not in `docs/`, not in
> the repo, not in git history. Line 8 asserted a second normative document that
> was never written, and it survived since v7 because **nobody ever tried to
> follow the reference.**
>
> ✅ **RESOLVED the same day. Sabbir's ruling: no Bangla mirror will be written**
> ("bangla ar english to same e"). Line 8 is struck; this file is the sole
> normative pipeline. Bangla remains the language of explanation, not of record.
> STATUS decision 18 is closed.

---

## 📊 S0 — X-ray of the actual data file (ground truth for everything below)

> ## ⛔ CORRECTED 2026-08-01 — read this before the table
>
> **This section was written from claims, not measurements. Three of its numbers
> were wrong and one of its premises was wrong.** Corrections are inline below,
> struck through rather than deleted, so the original can still be audited.
>
> **The premise that failed:** this table treats the 5,000 rows as one corpus.
> **They are two.** Rows 0–1998 and 1999–4999 differ on features that carry no
> sentiment content — দাঁড়ি 38.7% vs 99.2%, first-person pronouns 13.5% vs 0.8%,
> lexical richness 255 vs 128 types per 1,000 tokens — with a step transition at
> one row, not a drift. All 1,670 class-2 rows sit in the second region.
> Evidence: `results/s2c_region_split.md`.
>
> **The consequence, measured:** LaBSE K-Means on the full corpus identifies
> **which of the two corpora a review came from with 93.3% accuracy**
> (ARI(cluster, region) = 0.4813 against ARI(cluster, Sentiment) = 0.1793;
> binary recast ARI 0.7487, φ 0.861). The clusters this pipeline calls "personas"
> are, on the full corpus, **a corpus detector**. See
> `results/s2_pilot_ari_trapcheck.md`.
>
> **What this changes in the design, and it is not cosmetic:**
> - `region` is a **controlled factor** throughout. The split stratifies on
>   `Sentiment × region`, every headline metric is reported full / A / B, and no
>   claim survives that does not survive within-region.
>   (`docs/protocol.md`, "Scope decision".)
> - **Persona discovery happens inside region A**, never on the full corpus.
> - **Gold-300 must be stratified on the region-A clustering.** Stratifying on
>   the full-corpus clustering would stratify 300 annotations on a file seam.
> - Provenance is **unrecoverable**: no venue, thread or timestamp column, no
>   collection log, and the collector does not remember. Closed as unresolvable
>   2026-07-30; both the measurement and his account are recorded, unreconciled.

**File:** `Raw_Bangla_Movie_Review_Comment_Dataset...xlsx` → 1 sheet, **5,000 rows × 2 columns: `Movie Review`, `Sentiment`**

| Finding | Number | Consequence |
|---|---|---|
| Sentiment labels (0/1/2) | 1,665 / 1,664 / 1,670 — ~~perfectly balanced~~ **balanced in the raw file only; 1,513 / 1,599 / 1,618 after cleaning** | 🎁 Free external-validity metadata (§2.4); the balance is curated — disclose in the dataset card. **No prevalence claim may be made: stopping was quota-driven.** |
| **Movie-title column** | **Absent**; in-text name mentions are rare (শাকিব=18, শাবানা=17) | ❌ A held-out-films split is impossible → split map and §5.4 redesigned accordingly |
| Exact/normalized duplicates | 204 / ~~205~~ **206** | Removed in cleaning |
| Reviews with <3 words | 72 | Removed |
| Null rows | ~~1~~ **2** — one missing text, one missing label | Removed |
| **Usable n** | ~~**≈ 4,722**~~ **4,730** after rule-based cleaning; **4,625** after near-duplicate removal at the pre-registered t = 0.95 | All split sizes derive from this. 4,722 came from subtracting the three drop sets as if disjoint, double-counting the 10 rows in SHORT ∩ DUP. Verified in `results/s0_data_xray.md`. |
| **Corpus composition** | **Two corpora, joined at raw row 1999**: 1,999 organic + 3,001 uniform-register | **NOT in the original table.** Region A survives cleaning as 1,910 rows / 2 classes; region B as 2,820 / 3 classes. See the correction box above. |
| Word count | median **8**, mean 9.6, max 84; only 12 reviews ≥50 words | Very short reviews — generated text must match this length distribution (JS-on-length matters); verifier max_len=64 suffices |
| Emoji | **0 rows** | ❌ Emoji features are dead → symbolic scorer is text-only (§3.5); the pre-defence emoji preprocessing tables do not match this file — fix in the thesis |
| URLs/mentions | 0 | The file is partially pre-cleaned despite the "Raw" name — state this honestly in the dataset card |
| Intensifiers present? | খুব=775, অসাধারণ=283, ভালো=643, বাজে=88, ফালতু=65 | ✅ Text-only symbolic features are viable |
| Sentiment × length | positive(1)=11.9 words vs 8.2/8.8 | ✅ First external-validity signal already visible |

**⚠️ New scientific risk:** with 8-word reviews, the easiest thing for LaBSE clustering to capture is sentiment itself — the "3 personas" could be a rediscovery of the 3 sentiment classes. Hence a **mandatory trap-check (§2.4): ARI(cluster labels, Sentiment)**. If >0.6, either re-operationalize personas with engagement features (length/intensity/specificity) or honestly present them as "sentiment-anchored engagement tiers." Hiding it is forbidden; the result is reported either way.

> ✅ **ANSWERED 2026-07-31 (step 10), and the risk was real but not the one feared.**
> ARI(cluster, Sentiment) = **0.1793** on the full corpus — well under 0.6, so the
> clusters are *not* a sentiment rediscovery. **But ARI(cluster, region) = 0.4813**:
> they were detecting which of the two corpora a review came from. The trap-check
> caught a trap the pipeline had not anticipated, which is the argument for running
> checks whose outcome you think you can predict.

---

## 🚀 START HERE — Step-by-step execution order (complete each ☐ before the next)

> **Tick discipline (added 2026-08-11).** ☑ means *the result file exists and its
> lab-notebook entry is written*. ⚠️ means partly done, with the gap named. ✗ means
> **established as not producible** — those are not pending work and must stop
> being read as pending. Every ☑ below names the file that justifies it, so the
> tick can be checked rather than trusted.

**Week 1 — Foundations**
☑ 1. Create the repo (§0.1 layout), requirements.txt, global seed=42 — `src/common/seed.py`, `requirements.lock.txt`
☑ 2. Draft `protocol.md` (§0.2) — written and running; **53 rows in its Deviations log.** ✅ **supervisor sign-off OBTAINED** — Sabbir, 2026-08-11. `docs/supervisor_seal_packet.md` (prepared 2026-08-10, Phases 1–3) was signed; the signed copy is not held in the repo at Sabbir's instruction, so it is recorded as a student report rather than a repo artifact. **Week 1 is now fully closed.** Phases 4–6 seal separately
☑ 3. Core base papers (§0.3) — superseded in practice by `docs/related_work.md` (9 tiers) and the CLAUDE.md search-first rule, which is stricter than "read these first"

**Weeks 2–3 — Data (S1)**
☑ 4. xlsx → clean → `bn_clean.csv` — **n = 4,730**, not 4,722 (see corrected S0) [§1.1] — `results/s0_data_xray.md`, `results/s1_cleaning_log.json`
☑ 5. Freeze the split file — **FROZEN 2026-08-01**, `data/splits/split_map_v1.json`, committed. **G 300 / R1 2,162 / R2 2,163 = 4,625** after near-dup removal at t = 0.95; `dev` = 200 is a **subset of R1**, not a fourth partition. Stratified on `Sentiment × region` as required. Never regenerated
☑ 6. Bangla plots — **120 = 30 dev + 90 eval**, harvested from bn.wikipedia and FROZEN 2026-07-31. Not 130: the source does not hold 130 Bangla films with usable plot sections, and both routes to 130 were refused (deviation logged) [§1.1.7]
☐ 7. English arm: IMDB subsample **matched to the Bangla n actually used** (4,730, or 1,910 if the arm mirrors region A) + MPST plots **30+90** + tokenizer-fertility table [§1.2] — ✅ **SCHEDULED, not cut** (Sabbir 2026-08-11): full §1.2 charter runs after the Bangla machinery exists, since every config takes the corpus as a field. RQ4 stays live in its strong form

**Weeks 3–5 — The engagement-specificity axis (S2–S3)** 🔴 **[D12]** *section title still says "Personas" in the bn mirror*
☑ 8. LaBSE embed → master K-table (7 criteria, K=2..8) [§2.1–2.2] — `results/s2d_ktable_regionA.md`, `s2d_ktable_regionB.md`. 🔴 **Outcome: K = 2, not 3** — K=3's prediction strength was 0.669 against a cutoff of 0.80 fixed two days earlier (decision 7, closed 2026-08-03)
☑ 9. GMM-BIC + HDBSCAN + multi-encoder ARI [§2.2] — 🔴 **Outcome: there is no cluster structure.** Silhouette **0.053**, gap statistic monotone, **HDBSCAN labels 100% noise**. Region B additionally cleared PS at **0.818** on a cut correlating with nothing measurable → kept as a **negative control** (RQ1-G). *Stability is not validity*
☑ 10. **ARI(cluster, Sentiment) trap-check** [§2.4] — DONE. Full corpus 0.1793 but ARI(cluster, **region**) 0.4813 → the clusters are a corpus detector. Region A alone: 0.1804, Band 1, not degenerate. **Also score every future clustering against `region`.**
☑ 11. Gate G1 → profiling [§2.3–2.4] — `results/s2e_*`, `s2f_*`. ⚠️ **G1 FAILED in the informative direction** (see step 9), and 🔴 **all S2e/S2f inferential statistics were DEMOTED to descriptive on 2026-08-10**: φ = 0.3981 and χ² = 300.7 are post-clustering inference on the very rows that defined the partition (Chen & Witten 2023). **No p-value here is evidence that the halves differ**
☑ 12. G-300 → annotation → Gate G2 [§2.5] — ⚠️ **round 1 FAILED** (ordinal α = 0.4970, rating scale). **Attempt 2 used comparative judgement and worked** — this is CLAUDE.md's search-first entry #1 (Kiritchenko & Mohammad, ACL 2017, had already shown rating scales less reliable). 🎁 **RQ1-H is the single non-circular result in the thesis: 0.78 / 0.84 against 0.25 chance, length-matched, length heuristic below chance**

**Weeks 5–7 — Verifiers (S4)**
☑ 13. Backbone ablation (4 models × gold-300) [§3.2] — done, **then repurposed.** 🔴 `results/s3b_baselines.md` verdict = **`CIRCULARITY_CONFIRMED`**: a frozen linear probe on the encoder that *generated* the label matches the best fine-tuned arm to within one dev item (0.9866 vs 0.9647). **The table may support NO claim about backbones**; it is reported as a demonstration that the label is linearly recoverable. "Pick the winner" is void as written
⚠️ 14. Train Verifier-A + B (bn, en) → dual accuracy [§3.1, 3.3] → Gate G3 — **bn pair DONE 2026-08-11** (`results/s3c_verifier_a.json`, `s3d_verifier_b.json`): A 0.986555 (1 error in 82, reproduces S3.2b), B `COMPETENT_EVALUATOR` 0.959666, mean 0.967442 ± 0.015839 over 5 seeds. **en pair not built** (step 7). ✗ **the dual-accuracy table is NOT PRODUCIBLE** — established 2026-08-08. 🔴 **Pre-committed: no claim that either verifier is better may be made from dev-82** (1 item = 0.0122 macro-F1)
☑ 15. Calibration (ECE + temperature scaling) [§3.4] + LR-learned symbolic rules [§3.5] — **both done 2026-08-11.** 🔴 **Verifier-A was miscalibrated: ECE 0.11836 → 0.00537**, and the direction is **UNDER-confidence** (T = 0.10918 < 1), opposite to `guo2017calibration`'s finding. ✅ **Verifier-B's pre-committed null FIRED** (ΔECE CI [−0.00661, +0.00705] straddles zero). ⚠️ Symbolic scorer is weak and gameable: CV **0.5150 ± 0.0713** vs majority 0.3926, features almost all presence-based. 🔴 **F1/IDF disabled pending Sabbir's rule-7 ruling — measured cost ~18 macro-F1 points**

**Weeks 7–9 — Loop (S5)** — 🔨 **PRE-REGISTERED 2026-08-11 (`protocol.md` §S4), no code yet.** `src/agents/` is an empty stub; `src/eval/` holds `tau_objective.py` only. This is Phase 4, and it is where the title's *"Multi-Agent"* and *"Verifier-in-the-Loop"* live
☐ 16. Build LangGraph (§4.1–4.2) + 20-generation pilot → ~~choose Llama vs Qwen~~ **choose gemma-3-12b-it vs TigerLLM-9B-it, local T4 (corrected 2026-08-12; §4.4 box)** — **unblocked as of 2026-08-11**: §4.2's Critic is `w×VerifierA + (1−w)×symbolic` and both inputs now exist (`artifacts/verifier_a.joblib`, `results/s35_symbolic.*`). ⚠️ ~~`0.6×VerifierA + 0.4×symbolic`~~ **STRUCK** — `w` has no value and is fit on the 30 dev-plots' generations as a sensitivity curve (protocol.md §S4). The pilot's decision rule, with `TIE` pre-committed, is registered in the same section
☐ 17. τ sweep → operating point [§4.5] → Gate G4 — ✅ **unblocked.** ~~first-pass 60–70%~~ **STRUCK** (decision 19): the operating point is **τ\* = argmax [quality(τ) − α_lo] / E[calls](τ)**, derived, with the full Pareto frontier reported regardless. ~~🔴 blocked by open decision 17: after temperature scaling **79 of 82 dev items sit at confidence 0.998**, so a sweep over calibrated Verifier-A scores has almost no resolution.~~ **CLOSED 2026-08-11 and the premise was FALSE** — temperature scaling is accuracy-preserving (`mattei2026welltempered`), so calibrated and raw τ are reparametrisations of the same partition; the defect was the uniform grid, not the scores. τ is swept at **quantiles of the observed score distribution**, and scoped **hierarchically across the two axis levels** (protocol.md §S4, decision 2)
☐ 18. Loop dynamics + failure taxonomy [§4.6]

**Weeks 9–12 — Experiments (S6)**
☐ 19. Main run 8×2×100×3 (overnight batches) [§5.1] — all scoring via Verifier-B
☐ 20. Goodhart figures [§5.3] + plot-level realism test [§5.4] + cross-lingual Δ table [§5.5] + mini-ablations [§5.1b]
☐ 21. Statistics: bootstrap CIs + BH correction + effect sizes, ≥3 seeds [§5.6]
☐ 22. Human eval: 100 generated items × 3 annotators [§5.2]

**Weeks 12–14 — Writing + compliance (Phases 6–7)**
☐ 23. Thesis chapters [§6.1] + Limitations organized by four validity types
☐ 24. Phase-7 checklist — all HARD items first
☐ 25. Demo + defence package [Phase 8]

---

## ⛔ FROZEN EXECUTION CONTRACT — code is merely the translation of this

### A. Data split map — done once on Day 1, seed=42, then untouchable

```
Raw 5,000 ──clean (drop dup 204 + short 72 + null 1)──► usable = 4,730 (4,625 after near-dup removal)
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
          G: gold-300                     R: remaining ≈ 4,422
          (cluster-stratified,            ┌───────┴───────┐
          3 annotators, κ + α)            ▼               ▼
                                    R1 (≈2,211)      R2 (≈2,211)
                                    Verifier-A       Verifier-B
                                    + RAG index      (eval-only)
                                    + dev slice 200
```
**Where H went:** the file has no movie-title column and in-text mentions are rare → reviews cannot be mapped to films, so the "held-out films" split is removed. The held-out element for evaluation is now **120 externally collected plots** (§1.1.7: 30 dev + 90 eval, disjoint; harvested and frozen 2026-07-31) — these never need to map to any review.

**Inviolable rules:**
- **G never enters** training, the RAG index, prompts, or threshold tuning. Eval-only.
- **RAG index = R1 only.** R2 never appears in retrieval — otherwise Verifier-B is contaminated.
- **Verifier-B never enters the loop** — S6 scoring only. This wall *is* the Goodhart test.
- G's 300 need cluster labels for stratification, so G is finalized **after** S2 (placeholder at S1).
- The split file (review-ID lists) is the single most important artifact of the thesis; commit to git, never regenerate.

### B. Stage contracts S1–S6

| Stage | What gets trained | Input → Output | Gate (fail = next stage forbidden) |
|---|---|---|---|
| **S1** Data prep + split | nothing | xlsx 5,000 → clean **4,730** + IMDB subsample (matched n) + **120 bn plots (30/90)** + matched en plots → `bn_clean`, `en_clean`, frozen split file **stratified on `Sentiment × region`** | — |
| **S2** Persona discovery ⚠️ **on region A only** — on the full corpus the clusters are a corpus detector (93.3%) | K-Means (both languages) + GMM + HDBSCAN robustness | R + LaBSE → master K-table (7 criteria), stability, theory grounding, persona definitions | **G1:** prediction strength < 0.8 or bootstrap ARI worse than neighboring K → K=3 may not be forced; most stable K becomes primary, K=3 theory-motivated secondary |
| **S3** Human gold | nothing | **region-A-**stratified 300 → gold labels + Fleiss κ **and** Krippendorff's α (ordinal) | **G2:** α < 0.667 → revise guideline + re-annotate; failing twice → reframe claim ("theory-driven scheme, validated learnability") |
| **S4** Verifier training | **bn-A, bn-B, en-A, en-B** (4 classifiers) + symbolic-weight LR ×2 + temperature scaling ×4 | R1/R2 → dual accuracy (weak-label **and** gold), calibration (ECE before/after) | **G3:** gold accuracy < ~55% (chance=33%) → verifier too weak; increase symbolic weight / inspect data |
| **S5** Loop build + τ sweep | nothing (calibration only) | Verifier-A + R1-RAG → LangGraph loop, τ swept at **quantiles of the observed score distribution** (~~0.30–0.95 uniform~~ struck, decision 17) on dev-plots, operating point | **G4:** ~~if first-attempt pass rate doesn't reach 60–70%, raise τ~~ **STRUCK** (decision 19 — an unreachable target that could not be derived). Replaced: **τ\* = argmax [quality(τ) − α_lo] / E[calls](τ)**, both endpoints scored by **Verifier-B, never A**. The underlying worry survives and is kept: *"everything passes" means the loop is dead* — but it is now read off the frontier, not enforced by a target |
| **S6** Experiments | nothing (all inference) | 8 conditions × 2 languages × **90 eval-plots** (disjoint from dev-30) × ~~3 personas~~ **2 axis levels** (corrected 2026-08-11) → master table, Goodhart figures, plot-level realism JS (§5.4) | All scoring via **Verifier-B + human eval**; A stays inside the loop only. ⚠️ **Verifier-B's calibration improvement is NOT established** (null fired 2026-08-11) — report that beside the Goodhart test, since B is the scorer here |

**Total trained artifacts: 10** (4 verifiers + 2 LR + 4 temperature scalings) — all small, all free-Colab. **No LLM is ever trained** — generation is prompted only.

### C. Finalized stack — all ৳0

| Layer | Tool | Note |
|---|---|---|
| Generator (primary) | ~~**Llama-3.1-8B-Instruct or Qwen2.5-7B @ Groq free tier**~~ ⛔ **CORRECTED 2026-08-12: local T4, `gemma-3-12b-it` vs `TigerLLM-9B-it` — see the §4.4 correction box** | Open-weight = reproducible; choose via a 20-generation Bangla pilot; version-pinned checkpoint goes in the paper |
| Generator (secondary) | Gemini 2.x Flash free tier ⚠️ still scheduled as the robustness subset; unaffected by the 2026-08-12 provider move | "Results hold across a proprietary model" robustness check |
| Orchestration | **LangGraph** (version pinned) | Explicit graph+state; CrewAI/AutoGen forbidden (over-abstraction, hard to log) |
| RAG | ChromaDB + LaBSE | Index = R1 only |
| Verifiers | `csebuetnlp/banglabert` (110M) / `distilroberta-base` (82M) | Deliberately small — the claim *is* "cheap verifier"; a large English model would poison the cross-lingual comparison |
| Eval | `mauve-text`, sklearn, scipy, nltk, statsmodels, `netcal` | MAUVE = comparable with MoP |
| Annotation | **Label Studio** (local, free) | Randomization + progress tracking |
| Tracking / Writing | W&B free / CSV + Overleaf free + public GitHub | Code-availability statements are mandatory at many Q1 journals |

**Three reviewer-proof habits:** (1) pin every version + checkpoint names in the appendix; (2) one config = one YAML = one result file — nothing hand-run in a notebook enters the paper; (3) API sampling is stochastic — the answer is 100 plots per condition × bootstrap CIs, plus one line in Limitations.

---

## PHASE 0 — Setup, Scoping & Protocol Freeze (Week 1)

> 🎯 Goal: immunity against "you changed the experiment after seeing results." A protocol frozen in advance functions as pre-registration.

### 0.1 Repository & environment
```
thesis/
├── data/            # raw/, cleaned/, splits/   (never edit raw/)
├── src/  (preprocess/ cluster/ validator/ agents/ eval/)
├── configs/         # every experiment = one YAML
├── results/         # auto-logged, never hand-edited
└── protocol.md      # frozen BEFORE experiments
```
Python 3.10+, `sentence-transformers`, `transformers`, `scikit-learn`, `langgraph`, `chromadb`, ~~`groq`~~ **`bitsandbytes` (local 4-bit generation, 2026-08-12)**, `google-generativeai` (secondary). Global seed=42; every result carries timestamp + git hash. Tracking: W&B free tier or a CSV logger.

### 0.2 protocol.md — write and freeze now
Contents: (a) every hypothesis, (b) its metric, (c) sample size, (d) statistical test, (e) what will be claimed under each of three outcomes (win / mixed / negative). Get the supervisor's signature — it is your shield at the defence.

### 0.3 Core base papers (read this week)
| Paper | Why now |
|---|---|
| Huang et al., ICLR 2024 — "LLMs Cannot Self-Correct Reasoning Yet" | Theoretical anchor of the entire thesis |
| Kamoi et al., TACL 2024 — "When Can LLMs Actually Correct Their Own Mistakes?" | Intrinsic-vs-extrinsic taxonomy — your framing |
| "The Self-Correction Illusion" (arXiv 2606.05976, 2026) | Why external-role feedback works — Critic's justification |
| Mixture-of-Personas (Findings of ACL 2025, arXiv 2504.05019) | Closest competitor; borrow their formalism (population P, K groups, persona g_k); uses IMDB/SST-2 |
| Sands et al., NCAA 2026 (doi 10.1007/s00521-026-12247-0) | English persona-prompted movie reviews — their gaps are your motivation |
| Cobbe et al. 2021 — "Training Verifiers to Solve Math Word Problems" | Origin of the trained-verifier line |

**Deliverable:** repo + frozen protocol.md + supervisor sign-off.

---

## PHASE 1 — Data Engineering: Bangla + English Mirror (Weeks 2–3)

### 1.1 Bangla side (primary)
1. **Start from the raw 5k. Do not use the augmented 9,998** for clustering/training — augmentation creates semantic duplicates that artificially harden cluster structure. If used at all: as a separate disclosed robustness check.
2. Cleaning (regex): strip URL/HTML/mentions/hashtag symbols; normalize whitespace.
3. **⚠️ Old pipeline's mistake, corrected: no stemming, no stopword removal.** LaBSE/BanglaBERT are contextual encoders and need natural text; stemming/stopwords belong to the TF-IDF era. Also delete the TF-IDF/Count-Vectorization sections from the thesis — unused anywhere.
4. Filter (**measured**, superseding the estimates): exact dup **204**, <3-word **72**, null **2** → **4,730** (the union is 270, not the 278 you get by subtracting the drop sets as if disjoint); near-duplicate removal at LaBSE cosine ≥ 0.95 removes a further **105** → **4,625**.
5. ~~Movie-title tagging~~ **(cancelled)** — no title column, rare in-text names → film mapping impossible. Replaced by the redesigned §5.4. State this limitation in the dataset card.
6. Emoji **(zero in the file)** — nothing to extract; symbolic scorer is text-only (§3.5). The file is partially pre-cleaned despite "Raw" — state honestly; fix the inconsistent pre-defence emoji tables.
7. **Plot collection (DONE 2026-07-31):** **120** Bangla plot synopses (3–12 sentences, median 9) — **30 dev-plots** (τ-sweep + pilot, §4.5) + **90 eval-plots** (S6 main run only), **disjoint**, else the threshold is tuned on eval data (leakage). Sources: Wikipedia (bn), bmdb.com.bd, self-written; log the source per plot. **Plot text never comes from the review corpus.**

### 1.2 English Arm Charter

> One-line constitution: **Mirror, never merge. One table, one paragraph, one week — cut anything beyond.**

**⛔ Mirror-not-merge (inviolable):** English data never enters Bangla training/clustering/RAG — no translate-train, no joint multilingual training, no cross-lingual augmentation. Doing so changes the research question ("does the verifier help in low-resource?" → "does transfer help?") — exactly the supervisor's scope complaint. Two fully independent, matched pipelines.

**Datasets:**
1. **Reviews (clustering + verifier training): IMDB Large Movie Review (Maas et al. 2011)** — HuggingFace `imdb`. Deliberate: **MoP also uses IMDB/SST-2**, so our English numbers are directly comparable with theirs — say so in the paper.
2. **Plots (generation input): MPST v2** (Kar et al., LREC 2018; ritual.uh.edu/mpst-2018) — sample **30 dev + 90 eval** synopses, matched to the Bangla side. IMDB has no plots; review corpus and plot corpus are from different sources — disclose (symmetric with Bangla).
3. Random subsample to n = |bn_clean| (seed=42), same cleaning, same split construction.

**Scope table (what the English arm does / does not do):**
| Does | Does NOT (Bangla-only) |
|---|---|
| LaBSE clustering + identical K-selection protocol | Plot-level realism test (§5.4 — bn primary; en optional if time allows) |
| Verifier en-A/en-B training + backbone check (§3.2) | Multi-encoder robustness check |
| Full 8-condition ablation (§5.1) | 300-item human gold (a 100-sample check, or an honest limitation — §2.5) |
| Tokenizer-fertility covariate | Separate theory grounding (same citations apply) |

**Framing rules (how the paper words it):**
- English = **reference ceiling**, not strict apples-to-apples. Never attribute the score gap purely to "language difficulty" — encoder/generator/tokenizer artifacts contribute (Petrov et al., NeurIPS 2023: identical text can tokenize up to 15× longer across languages; Rust et al. 2021). Report the fertility table beside every cross-lingual comparison.
- The core comparison is **Δ (improvement over zero-shot)** per condition, en-column vs bn-column (§5.5). Three outcomes → three honest claims: Δ_bn > Δ_en → "the verifier matters more in low-resource" (strongest); Δ_bn ≈ Δ_en → "the verifier helps generally; demonstrated in low-resource Bangla" (still publishable); English arm exceeding one week → cut to fertility + zero-shot reference only.
- Matched controls: n, domain, K, encoder (LaBSE both sides — zero encoder confound), generator LLM, hybrid weights, τ-selection procedure. Verifier backbones differ (BanglaBERT vs DistilRoBERTa) — an unavoidable confound; mitigate via the size-matched pairing of §3.2 and state in Limitations.

**English-side comparator papers (position against these):** MoP (formalism + IMDB/SST-2 + MAUVE/FID — the main baseline family); Sands et al. NCAA 2026 (their "emotional richness gap" is your motivation); WWW 2026 Companion (persona prompting can *degrade* survey alignment); "LLM Generated Persona is a Promise with a Catch" (NeurIPS 2025 Position).

**Fertility measurement (during S1):** tokens/word in both languages under the generator's tokenizer — one small table, reported as a covariate.

### 1.3 Dataset cards (both corpora)
Source, collection dates, per-step attrition, length distributions, license, the partial-pre-cleaning disclosure. *Base: Gebru et al., Datasheets for Datasets.*

**Deliverables:** `bn_clean.csv`, `en_clean.csv` (matched n), **120 bn + 120 en** plots, dataset cards, fertility table.

---

## PHASE 2 — Persona Discovery + Human Ground Truth (Weeks 3–5)

> 🎯 Goal: prove "personas are real, not clustering artifacts." This is where circularity is broken.
> ⚠️ **Core principle:** "why K=3?" is never answered by one elbow plot. The answer is a **four-layer convergence**: (1) multiple internal indices, (2) stability, (3) human validation, (4) theory. The paper sentence: *"K=3 was selected by convergence of multiple internal indices, confirmed by stability analysis (bootstrap ARI, prediction strength ≥ 0.8), corroborated across encoders (ARI/AMI), validated by human annotators (Krippendorff's α), and grounded in established audience-engagement typologies; GMM/BIC and HDBSCAN are reported as robustness checks."*

### 2.1 Embedding + clustering (same encoder both languages)
- **LaBSE**, 768-dim. Cluster in the **original space (or PCA-95% space)**, cosine distance.
- **UMAP is visualization-only** — never cluster in UMAP space (non-linear + stochastic; poisons validity claims). Caption: "visualization only."
- **K = 2…8 sweep.** One master table, 7 columns per K: Silhouette, Calinski–Harabasz, Davies–Bouldin, **Gap statistic** (Tibshirani et al. 2001, B=100), **bootstrap ARI (mean±SD)**, **Prediction strength** (Tibshirani & Walther 2005), **GMM-BIC**. This table *is* the primary answer to "why 3."
- Honesty clause: silhouette 0.05–0.15 is normal in high-dim transformer spaces (hubness, anisotropy, distance concentration). Write: "low silhouette reflects known pathologies of high-dimensional embedding spaces, not absence of structure; hence we rely on stability + human validation."

### 2.2 Stability + robustness (the real tribunal for K)
- **Bootstrap ARI:** 80% subsample × 100 runs → ARI vs full-data labels, mean±SD per K. The most stable K is the prime candidate.
- **Prediction strength:** rule — **the largest K with PS ≥ 0.8** (Tibshirani & Walther's own cutoff).
- **Alternative-method robustness:** **GMM+BIC** (soft membership — the honest model if personas overlap; report BIC-minimum K) and **HDBSCAN** (discovers K itself + allows noise; report its K and noise fraction; if it also finds ~3 groups, that is strong independent evidence).
- **Multi-encoder check (bn only):** LaBSE vs BanglaBERT mean-pooled vs multilingual-E5 → pairwise ARI/AMI.
- **If criteria disagree** (e.g., silhouette→2, gap→4): (1) report the full table — no cherry-picking; (2) **stability > compactness**; (3) human validation + theory are the tie-break, stated explicitly; (4) acknowledge the disagreement in Limitations.

### 2.3 Theory grounding — ~~"three personas"~~ did not fall from the sky

> 🔴 **[D12] WORDING IS SABBIR'S — 2026-08-11.** K = 2, not 3 (decision 7), and the
> words *persona* and *cluster* are both retired (decision 12): the literature
> reserves *cluster* for structure we do not have (silhouette 0.053, monotone gap,
> HDBSCAN 100% noise). Permitted: **axis, gradient, the cut, level**. The theory
> grounding below still matters — but it now grounds **a two-level engagement-
> specificity axis**, and the section must be rewritten to say so. Claude has not
> rewritten it, because the replacement wording is Sabbir's call.
The three tiers are a collapse of established engagement continua. Cite:
- **Abercrombie & Longhurst (1998), *Audiences*** — consumer → fan → cultist → enthusiast
- **Hunt, Bristol & Bashaw (1999), *J. Services Marketing* 13(6)** — five fan types (⚠️ often mis-attributed — verify authorship before citing)
- **Funk & James (2001), Psychological Continuum Model** — awareness → attraction → attachment → allegiance
- **Cuadrado & Frasquet (1999), *J. Cultural Economics* 23(4)** — empirical 3-cluster cinema segmentation: social 36.1% / apathetic 28.2% / cinema-buff 35.7% (p=0.000) — almost a mirror of our scheme
- Honesty: some studies find four segments — write "3 vs 4 is a modeling choice; theory-motivated, data-confirmed, human-validated."

### 2.4 Persona interpretation (linguistic profiling)
Per cluster: mean length, intensifier frequency (খুব/দারুণ/অসাধারণ), negation, actor/director mentions, top-20 distinctive terms (log-odds). This table yields each persona's **operational definition** (behavioral criteria, not just a name).
**External validity (strengthened — we have Sentiment):** cluster × Sentiment cross-tab + χ², and cluster × length. First signal already visible: positive reviews are longer (11.9 vs 8.2 words).
**⚠️ Mandatory trap-check:** **ARI(cluster labels, Sentiment)**. If >0.6, personas ≈ sentiment rediscovery → either engagement-feature re-operationalization, or the honest "sentiment-anchored engagement tiers" framing. Reported regardless.

### 2.5 ⭐ Human validation (the single most important task of the thesis)
1. Stratified sample: 100 per cluster = **300 Bangla reviews**.
2. **3 native annotators**, blind to cluster labels, given operational definitions + 10 practice examples + a written guideline (released later).
3. **Report both:** **Fleiss' κ** and **Krippendorff's α (ordinal)** — personas are ordinal (engagement levels), so ordinal α credits near-misses. Under class imbalance also report **Gwet's AC1** (kappa-paradox guard).
4. Majority vote = **gold set**. K-Means vs gold → κ + confusion matrix.
5. English side: a 100-sample check if annotators exist, else an honest limitation.

**Decision rule:** α ≥ 0.80 reliable; **0.667–0.80 tentative-acceptable (Krippendorff's own bands)**; α < 0.667 → revise guideline + re-annotate. Still < 0.667 after two revisions → reframe: *"we impose a theory-driven three-tier scheme and validate its learnability"* — weaker but honest and publishable.

**Base papers:** Rousseeuw 1987; Tibshirani et al. 2001; Tibshirani & Walther 2005; Hubert & Arabie 1985; Fraley & Raftery 2002 (GMM/BIC); Campello et al. 2013 + McInnes et al. 2017 (HDBSCAN); Krippendorff 2019; Artstein & Poesio 2008; Miller & Alexander 2025 (arXiv 2502.17020 — multi-resolution alternative to "single optimal K"); MoP; BluePrint/SIMPACT.
**Deliverables:** master K-table, GMM/HDBSCAN robustness note, multi-encoder ARI/AMI, theory paragraph, persona definitions + profiles + external-validity cross-tab, 300-review gold set, κ+α report.

---

## PHASE 3 — Verifier Training: A/B + Calibration (Weeks 5–7)

> 🎯 Goal: Claim 2 — "the verifier is a valid, calibrated instrument," plus the Goodhart-test prerequisite.

### 3.1 Two separate verifiers (both languages)
| | Role | Ever sees |
|---|---|---|
| **Verifier-A** | The in-loop gate | Generation-time scores |
| **Verifier-B** | Evaluation only | Never enters the loop |

Different seeds + disjoint train splits (2-fold swap). **Without this, every result is circular.**
- Bangla: fine-tune `csebuetnlp/banglabert` (batch 16, lr 2e-5, 4–6 epochs, early stop) — ~30–40 min on free Colab.
- English: `distilroberta-base` (small, fair — a large English model would poison the comparison).

### 3.2 Verifier backbone ablation — the empirical answer to "why only BanglaBERT?"
| Backbone | Params | Why a candidate |
|---|---|---|
| `csebuetnlp/banglabert` | 110M | Bangla-native ELECTRA; Bhattacharjee et al. (Findings of NAACL 2022) — SOTA on multiple Bangla NLU tasks |
| `xlm-roberta-base` | 270M | Strong multilingual baseline — without beating it, the "Bangla-specific model is needed" claim collapses |
| `google/muril-base-cased` | 236M | Indic-specialized (17 languages incl. Bangla) |
| `bert-base-multilingual-cased` | 178M | Historical baseline |
- Protocol: identical R1 training / identical budget (lr {2e-5, 3e-5} × 4 epochs, seed 42) → macro-F1 on the same weak-label test **and the same gold-300**. One table; the winner becomes the Verifier.
- Either outcome wins: BanglaBERT wins → the choice is empirically proven; XLM-R wins → use it, and "monolingual vs multilingual verifier in low-resource" is itself a small finding.
- English side matched: quick `distilroberta-base` vs `roberta-base` check → pick a size-matched pair to avoid capacity confounds.
- Cost: 4 backbones × ~30 min Colab = half a day. One table + two sentences in the paper.

### 3.3 Evaluation — report both numbers
1. **Weak-label test set:** ~87% expected → "label reproduction accuracy."
2. **300-item human gold:** likely 65–75% → **"true persona detection accuracy"** — the real number; the gap between the two is itself an honest, citable contribution.

### 3.4 Calibration (hidden contribution)
Reliability diagram (10 bins), **ECE**, Brier score → **temperature scaling** → ECE before/after. The threshold gate stands on confidence; miscalibrated confidence makes τ meaningless. *Base: Guo et al., ICML 2017.*

### 3.5 Symbolic scorer — full specification (text-only features)
- Feature pool (no emoji — absent from data): intensifier count, positive/negative lexemes (ভালো/বাজে/ফালতু), length bucket, exclamation, negation, name mentions (where present), specificity terms (গান/অভিনয়/গল্প).
- Rule table in the appendix: rule ID, persona, feature, weight, provenance.
- **Never hand-set weights** — learn via logistic regression on the 200-item dev slice. Tune the 0.6/0.4 hybrid weight on dev too (grid 0.5–0.8) and report it.

**Deliverables:** 4 trained verifiers (A/B × bn/en), backbone-ablation table, dual-accuracy table, calibration figure, rule table.

---

## PHASE 4 — The Compound AI System: Building the Loop and Bringing It Alive (Weeks 7–9)

> 🎯 Goal: Claim 3 — earn the loop empirically. The old "100% / 1.0-attempt" meant the loop was dead.

### 4.0 Naming — what we call it, and what we refuse to call it (final)
The paper's identity sentence: **"a compound AI system (Zaharia et al., BAIR 2024) implementing the evaluator-optimizer workflow (Anthropic, *Building Effective Agents*, Dec 2024) — generator + external trained verifier + reflection loop, with role-separated deterministic and generative components."**
- **Never claim "autonomous multi-agent system"** — control flow is predefined and 2 of 4 components make no LLM calls; on Anthropic's workflow-vs-agent distinction, this is a workflow. This honest naming fully answers the "this is just a pipeline" attack.
- The title keeps "Multi-Agent Framework" (pre-defence-locked); the first Methods paragraph carries the definition above — an honesty bridge between title and content.

### 4.1 System state — the heart of the LangGraph
```python
State = {
  plot: str, target_persona: str,          # immutable input
  retrieved: list[review_id],              # written by Researcher
  draft: str,                              # written/updated by Writer
  neural_score: float, symbolic_score: float, hybrid: float,
  verdict: PASS | FAIL,                    # written by Critic
  feedback: str | None,                    # written by Reflector
  attempt: int (max 3),
  trace: list[full snapshot of every previous attempt]   # nothing is lost
}
```

### 4.2 The four component contracts (input → work → output → design justification)

**1 — Researcher** (deterministic tool-caller, no LLM call)
- In: `plot, target_persona` → ChromaDB query from plot key-phrases + persona filter (**R1 index only**, cosine, top-10, within same persona label) → Out: `retrieved`.
- On retry (query-drift fix): the original persona+plot query **always stays anchored**; feedback keywords only **augment**, never replace. Log exemplar overlap per attempt — if overlap <50% with no pass-rate gain, disable re-retrieval and route retries straight to the Writer (this is the §5.1b routing ablation).
- Justification: a non-parametric form of MoP's exemplar conditioning.

**2 — Writer** (the only generative component)
- In: `plot, persona, retrieved, feedback?` → prompt order: [persona operational definition — verbatim from Phase 2] + [10 retrieved exemplars] + [plot] + on retry [previous draft + Reflector feedback + "fix exactly these issues"].
- Params: temp 0.8, top_p 0.9, seed logged. Out: `draft` (Bangla). Prompt templates go verbatim in the appendix.

**3 — Critic** (deterministic judge — explicitly not an LLM; this is the thesis's central claim)
- In: `draft, target_persona` → `hybrid = ~~0.6~~w×VerifierA(draft) + ~~0.4~~(1−w)×symbolic(draft)`, compared with a τ per axis level → Out: `verdict + both scores`.

> 🔴 **`0.6 / 0.4` IS STRUCK — 2026-08-11, Sabbir's rule: *"hate likha thakle hbe na. karon thakte hobe."*** The spec called these *"dev-tuned weights, §3.5"*, but **no tuning ever produced them** — they are the number this whole audit started from, and tracing them found no derivation anywhere in the repo.
>
> ⚠️ **They are also not *tunable* as written.** Verifier-A scores **0.9866 — one error in 82** — so every weight in §5.1b's 0.5–0.8 grid returns the same verdict, and the *"symbolic adds <2 points"* rule would have to resolve **1.6 dev items**. The sweep as specified is degenerate.
>
> **What replaces it** (registered in `protocol.md`, 2026-08-11): `w` is fit on the **30 dev-plots' generated outputs** — where the Critic actually operates, and where `kapur2026length` says the length/specificity relation *differs* from human text — and reported as a **sensitivity curve, never a point**. Inclusion of the symbolic term must survive a **held-out marginal-value test**, not a standalone score: `barata2026hybrid` rejected a cheap component in **50 of 50 folds** while it looked fine standalone.
>
> **Until that runs, `w` has no value and §4.2 may not be implemented with one.**
- Justification: **Self-Correction Illusion (2606.05976)** — external-role feedback is what works; **CRITIC (ICLR 2024)** — the judge is a tool, not the model itself. The Critic is never the Writer's model — that separation is the architecture's soul.
- ⚠️ τ chosen to hit a pass-rate is itself a proxy — so τ is set **on dev-plots**, and the final τ is sanity-checked against Verifier-B scores, not only A.

**4 — Reflector** (small generative call, FAIL only)
- In: `draft, scores, failed-rule list` → structured feedback — not random critique but **which symbolic rules failed + which persona the neural confidence leaned toward**, rendered in natural language (e.g., "no intensifiers [R1 failed]; reads Indifferent-cold — raise emotion, name the lead actor") → Out: `feedback`.
- Justification: Reflexion (NeurIPS 2023) — verbal feedback memory; ours is verifier-grounded, not self-generated. Error-localized feedback beats generic (Self-Refine ablation; Tyen et al. 2024).

**Loop control:** FAIL & attempt<3 → back to Researcher (anchored+augmented query). FAIL & attempt=3 → emit best-of-3 by hybrid with `gave_up=True` — the raw material of the failure taxonomy; report all metrics split by `gave_up` status.

### 4.3 ⚠️ Pre-empting "is this really multi-agent?"
Be honest: two of four components are deterministic. Three defences, written explicitly in the paper:
1. Use the §4.0 naming verbatim — compound AI system + evaluator-optimizer (BAIR 2024; Anthropic 2024); with no autonomy claim there is nothing to attack.
2. Role-separation *is* the scientific point: generator and judge are distinct entities — the direct application of the Self-Correction Illusion role-label finding.
3. The ablation table proves each component earns its place (rows 3 vs 4 vs 6 vs 7) — none is decorative.

### 4.4 Instrumentation
Full state snapshot per attempt in `trace`; JSONL dump per run — the substrate of dynamics analysis + failure taxonomy. RAG index = R1 only; G never (leakage). ~~Generator: Groq primary (20-generation pilot → Llama vs Qwen); Gemini secondary on a subset.~~

> ⛔ **CORRECTED 2026-08-12 (protocol.md, four rows dated 2026-08-12).** Generation runs on **our own GPU (Kaggle T4), not a hosted API** — no free API supplies ~10M tokens of Bangla (eight checked); the cause is budget and is logged as budget, and it narrows the `2601.17768` reproducibility concession: locally the batch is chosen and the seed set (**batch size 8 = provenance, not a knob**). Pilot arms re-registered: **`google/gemma-3-12b-it` vs `md-nishat-008/TigerLLM-9B-it`** — same base (both Gemma3ForCausalLM, verified from each `config.json`), one variable: Bangla adaptation. The 1B pair was tried and failed (1 of 3 usable; hand-read, n=3, NOT A RESULT). "Llama vs Qwen" was already dead on 2026-08-11 (Qwen is a Groq Preview model); its replacement "Llama vs GPT-OSS" differed in three ways at once and is superseded. arXiv 2503.10995 does **not** describe the TigerLLM uploads (paper says LLaMA-3.2/Gemma-2; weights are Gemma-3, "9B" = 12.19B) — no claim may rest on its benchmark table. The 27 Groq generations (`results/pilot_s4_generations.jsonl`) are retained for the Llama fertility measurement (0.93 chars/token; Gemma-3: 3.71) and may never be merged with local generations. Runner: `notebooks/s4_pilot_kaggle.ipynb` + `configs/s4_pilot_local.yaml`.

### 4.5 Threshold sweep — the central task
- ~~τ = 0.30 → 0.95 (step 0.05)~~ **τ swept at QUANTILES of the observed score distribution** (corrected 2026-08-11, decision 17), each τ on the **30 dev-plots** × **2 axis levels**; the 20-generation model pilot uses this dev set too.

> 🔑 **Why the uniform grid was replaced, and why the calibrated/uncalibrated question was dropped.** Temperature scaling is **accuracy-preserving** — `mattei2026welltempered` prove it is the *only* accuracy-preserving linear scaler — so it cannot move an item across a threshold, and calibrated vs raw τ are **reparametrisations of the same partition**. Confirmed on dev-82: **0 rank inversions**. The defect was never the scores; it was the grid. On the old uniform grid, calibrated scores gave **5 distinct pass-sets against raw's 12**, and were **flat for 8 consecutive grid points**. Thresholds placed at observed score values give **81 operating points on either scale**. **Report on the calibrated scale** so τ reads as a probability (`kotte2026ucci`, Thm 1). ✅ **Decision 19 CLOSED 2026-08-11 — τ is now derived, and ~~"first-pass 60–70%"~~ is struck.**
>
> The cost objective **alone is degenerate**: calls-per-accepted falls monotonically in the pass rate (16.310 at q=0.10 → 1.020 at q=0.99), so minimising it selects **τ = 0**. The 60–70% target was a constraint wearing an optimum's clothes.
>
> **Following `kotte2026ucci` §3, the constraint is bounded by two measured endpoints, and ours are already §5.1 rows:**
> - **α_lo** — τ=0, the Critic never rejects: **row 1, zero-shot, 1 call**
> - **α_hi** — τ=1, every plot runs all 3 attempts, best-of-3 emitted
>
> 🔑 **Both measured by Verifier-B, never Verifier-A** (rule 6 — A is inside the loop). This is stricter than UCCI, which has no such wall.
>
> **Headline point, no free constant:** τ\* = **argmax [quality(τ) − α_lo] / E[calls](τ)**. UCCI picked 74.1% of the achievable range; choosing our own fraction would reintroduce a hand-written constant, so the argmax replaces it. **The full frontier is the deliverable** (their Fig. 2); τ\* names a point on it.
>
> Procedure and cost model: `src/eval/tau_objective.py`, pre-registered before any generation exists.
- Plot: first-attempt pass rate, avg attempts, final acceptance, and **Verifier-B score** (independent quality).
- ~~**Pick the operating point where first-attempt pass ≈ 60–70%** → the Reflector fires on 30–40% of cases → the loop's behavior becomes measurable.~~ ⛔ **STRUCK 2026-08-11 (decision 19).** This bullet survived four lines below the box that strikes it — logged as a maintenance failure in `protocol.md`. **Replaced by the derived τ\* above.** The *motivation* is retained and is still right — a loop that passes everything is dead — but it is now observed on the frontier rather than imposed as a target, because a target that cannot be derived is a constraint wearing an optimum's clothes.
- **Temperature schedule (ablation only):** retry temps 0.8→0.9→1.0 — a published diversity mechanism for escaping mode-collapsed drafts; measure in §5.1b, do not bake in.

### 4.6 Loop dynamics report
Attempt distribution (1/2/3), hybrid-score growth per attempt, persona-wise retry rates (Enthusiastic Casual expected highest — prior recall 0.5674 says so), and a hand-coded **failure taxonomy** of 50 three-time failures (wrong sentiment / too short / off-topic / template repeat).

**Base papers:** Madaan et al. NeurIPS 2023 (Self-Refine — diminishing returns by iteration 3); Shinn et al. NeurIPS 2023 (Reflexion); Gou et al. ICLR 2024 (CRITIC); Anthropic 2024; Zaharia et al. (BAIR) 2024.
**Deliverables:** working instrumented system, threshold-sweep figure, chosen τ per persona, **per-iteration pass-rate/score curves per persona (the empirical justification for max-retry=3)**, dynamics report.

---

## PHASE 5 — The Experiment: Ablations × 2 Languages (Weeks 9–12)

### 5.1 Main ablation table (identical in both languages)
| # | Condition | Tests |
|---|---|---|
| 1 | Zero-shot persona prompt | Is prompting enough? |
| 2 | Few-shot (static examples) | Do examples alone suffice? |
| 3 | RAG only (no verifier) | Retrieval's contribution |
| 4 | RAG + neural-only verifier + loop | Is symbolic needed? |
| 5 | RAG + symbolic-only + loop | Is neural needed? |
| 6 | **Full hybrid (proposed)** | — |
| 7 | ⭐ Self-critique (same LLM critiques itself) | **Intrinsic vs extrinsic — the headline baseline** |
| 8 | LLM-as-judge critic (Gemini judges) | Cheap trained verifier vs large LLM judge |

- **Scale:** **90** eval-plots (never dev-plots) × ~~3 personas~~ **2 axis levels** × 8 conditions = ~~2,160~~ **1,440 generations per language** (~~৳0 on Groq~~ ৳0, local T4 — 2026-08-12; overnight batches). 🔴 **Corrected 2026-08-11.** Stale since K = 2 was selected on 2026-08-03 — **a one-third reduction in experiment size, cost and CI width** that sat unrecorded in the normative spec for eight days.
- Row 7 < Row 6 → external verification is necessary in low-resource — **the headline, a direct extension of Huang et al.**
- Row 8 ≈ Row 6 at 1/40th the cost → the efficiency claim. (Note LLM-judge biases to discuss: position, verbosity, self-preference; degraded reliability in lower-resource languages — further motivation for a *trained* critic.)

### 5.1b Mini-ablations (small, on dev-plots, bn only)
| Ablation | Measures |
|---|---|
| Retry → Researcher vs Retry → Writer | Does re-retrieval help, or drift? |
| Hybrid weight sweep (neural 0.5–0.8) | 0.6/0.4 is not arbitrary — sensitivity curve; if symbolic adds <~2 points over neural-only, soften the hybrid claim |
| k ∈ {3, 5, 10} exemplars | Optimal k for style imitation |
| Temperature schedule on/off | Is retry-diversity worth it? |

### 5.2 Metrics (per condition, per language)
| Metric | Measures | Tool |
|---|---|---|
| Persona accuracy (**via Verifier-B**, never A) | Controllability | — |
| Human persona match (100 samples × 3 annotators) | True controllability | Phase-2 team |
| distinct-1/2, Self-BLEU | Diversity / template repetition | nltk |
| MAUVE (+ FID optional) | Real-vs-generated alignment — **MoP-comparable** | `mauve-text` |
| JS divergence (length, sentiment dist.) | Realism | scipy |
| Cost + latency (**per-attempt marginal cost vs marginal gain** — ~60% of agentic cost sits in refinement; this table prices each retry) | Practicality | logs |

### 5.3 ⚠️ The Goodhart test (this opens the Q1 door)
Verifier-A and Verifier-B scores side by side per condition:
- A↑ and B↑ → genuine improvement ✅
- A↑ but B flat → verifier gaming — also publishable, possibly the most interesting finding.
- **Formal metric:** plot the **(A−B) gap as a function of attempt number** — a widening gap means overoptimization is occurring (direct descendant of Gao et al. 2022 reward-model overoptimization; a held-out verifier is the literature's standard mitigation — **this design is our strongest novelty hook; foreground it**).

### 5.4 Plot-level realism test (redesigned — film mapping is impossible)
- **Corpus-level distributional realism:** all generated reviews per persona vs that persona's real reviews → **MAUVE + JS(length) + JS(sentiment-classifier output)**.
- **Persona-mix sanity:** unconditional generation on the 90 eval-plots → Verifier-B label distribution vs the corpus's observed persona proportions (whatever S2 yields) → JS.
- **Mandatory Limitations sentence:** *"Our data lacks review-to-film mapping; hence we validate distributional realism at corpus level, not per-film audience prediction. 'Simulation' should be read as persona-conditioned response generation, not validated predictive audience modeling."*

### 5.5 Cross-lingual comparison
The key table: Δ (improvement over zero-shot) per condition — English column vs Bangla column, with the fertility covariate alongside. Claims per outcome as specified in §1.2. Never present the raw gap as pure "language difficulty."

### 5.6 Statistics
- **Paired bootstrap** (10,000 resamples, 95% CI) for the main metrics; **McNemar** for paired binary outcomes.
- **Multiple-comparison correction: Benjamini–Hochberg (FDR)** across the 8 conditions (or Holm — state which). Never "p<0.05" alone — always effect sizes (Cohen's d or absolute Δ + CI).
- **≥3 seeds/runs per arm** (API sampling is stochastic) → mean±SD; all comparisons paired.
- **N=300 justification:** show the bootstrap-CI width at 300 and the minimum detectable effect; cite Card et al. 2020 (EMNLP, "With Little Power Comes Great Responsibility").
- *Framework: Dror et al. 2018 (ACL), "The Hitchhiker's Guide to Testing Statistical Significance in NLP."*

**Deliverables:** master results table (8 × 2 languages), Goodhart figures (incl. A−B vs attempt), realism figure, cross-lingual Δ table, mini-ablation table, stats appendix.

---

## PHASE 6 — Analysis, Writing & Packaging (Weeks 12–14)

### 6.1 Thesis chapter mapping
| Chapter | Content | Feeds from |
|---|---|---|
| 1 Introduction | Per the Introduction Blueprint below | — |
| 2 Related Work | Rebuilt: self-correction (Huang, Kamoi, Illusion), verifiers (Cobbe, Gao), persona simulation (MoP, Sands, WWW'26, Promise-with-a-Catch), controllable generation (FUDGE line, classifier-gated rewriting), Bangla NLP; halve the neuro-symbolic surveys | 0 |
| 3 Data & Personas | Phases 1–2, human validation front and center | 1–2 |
| 4 Verifier | Backbone ablation + dual accuracy + calibration | 3 |
| 5 The Compound System | §4.0 naming, architecture, live-loop dynamics | 4 |
| 6 Experiments | Ablation, Goodhart, realism, cross-lingual | 5 |
| 7 Discussion & Limitations | Organized by the four validity types: construct (personas real or artifacts), internal (verifier vs extra-compute confound), external (beyond Bangla movie reviews), statistical conclusion (power) | — |

### 6.2 Packaging
Code + configs on GitHub; model on HuggingFace; gold-300 release (with annotator consent) — itself a small resource contribution. Venues: first **BLP Workshop (ACL) / LREC-COLING**, then with strong results **Computer Speech & Language / Natural Language Engineering / Information Processing & Management / IEEE TASLP**.

---

## PHASE 7 — Q1 COMPLIANCE CHECKLIST (none of this existed at pre-defence)

### 7.1 HARD — no review without these
- [ ] **Limitations section** — mandatory at ACL/ARR (desk-reject without it since Dec 2023); after the conclusion; excluded from page limits; organized by the four validity types.
- [ ] **Responsible NLP checklist** filed correctly (since Dec 2024 ARR desk-rejects incorrect/incomplete filing): artifact licenses, intended use, PII acknowledgment, **compute budget (GPU-hours, hardware)**, **all hyperparameters + search ranges**, number of runs + variance, annotation/ethics details — each with section pointers.
- [ ] **Generative-AI declaration** — the LLM as research object (Methods) and any writing assistance (Elsevier: a statement immediately above the references). AI cannot be an author.
- [ ] **Journal-specific (if IPM/Elsevier):** CRediT author-contribution statement + Data Availability statement — verify against the live Guide for Authors at submission.
- [ ] **Ethics status statement:** if CU has an ethics committee, obtain a determination letter; if not, state so explicitly + safeguards (annotator informed consent, fair compensation, anonymization).

### 7.2 NORM — reviewers cut without these
- [ ] **Human-eval documentation:** annotator count/recruitment/compensation/native-speaker status, released guidelines, rating instrument, randomization+blinding, κ+α, CIs. Complete a **HEDS (Human Evaluation Datasheet; HEDS 3.0, 2024)**.
- [ ] **Datasheets for Datasets** (Gebru et al. 2021) + **Data Statement for NLP** (Bender & Friedman 2018) — name the variety: Bangladeshi Bangla, Bengali script.
- [ ] **Model Card** (Mitchell et al. 2019) for the verifier.
- [ ] **Agent Card + state-machine diagram + sample traces** — the emerging documentation standard for agent systems (MICAI 2025); LangGraph figure + shared-state schema + released `trace[]` samples.
- [ ] **Data licensing/privacy (scraped FB/YouTube):** follow the Bangla precedent — SentiGOLD (arXiv 2306.06147): public-API collection + anonymization + non-commercial academic license; ToxLex_bn (Data in Brief 2022): dedupe + anonymize → Mendeley. Rules: strip usernames/PII, release **text+labels only**; if ToS blocks redistribution → gated/on-request or ID+rehydration release. One-line academic fair-use rationale for review copyright.
- [ ] **Bender Rule:** name the language explicitly from the abstract onward — "Bangla (Bengali), Bangladeshi variety, Bengali script." Native-speaker involvement statement.
- [ ] **English gloss for every Bangla example** (ideal: original script + transliteration + translation).

### 7.3 NICE — visibly above the bar
- [ ] Multi-resolution K analysis Sankey (Miller & Alexander 2025 style)
- [ ] Gwet's AC1 robustness agreement
- [ ] Publicly timestamped protocol.md — proof that the story was not written after the results

---

## PHASE 8 — Demo, Defence & Dissemination (after S6, ~1 week total)

> ⚠️ Wrappers, not contributions — not one day here before S6 is done.

### 8.1 Streamlit "Audience Simulator" v2 (2–3 days)
Rebuild the existing app (movie-review-agent.streamlit.app) on the new LangGraph backend: plot in → ~~3 persona reviews~~ **2 axis-level reviews** 🔴 **[D12 wording]** + hybrid scores + attempt counts + **the Reflector's feedback trace made visible** — self-correction you can watch; the defence show-piece. Hosting: Streamlit Community Cloud or HF Spaces (both free); if the 110M verifier is heavy, call it via HF Inference API. In the paper, one line: "A publicly accessible demonstration is available at <URL>."

### 8.2 Defence package (2 days)
Slide order = problem → the writer-examiner metaphor → split-map figure → master K-table → ablation table → Goodhart figure → live demo. Memorize the 2-minute summary; prepare the four expected questions: ~~"why 3 personas"~~ 🔴 **[D12]** **"why 2 levels, and why not clusters"** — the honest answer is §2.1–2.3 *plus* the negative results in steps 9 and 11, which is a stronger answer than the original question expected (§2.1–2.3), "why only BanglaBERT" (§3.2), "is this really multi-agent" (§4.0/4.3), "did you validate simulation?" (§5.4 + Limitations).

### 8.3 Dissemination (2 days)
Public GitHub (code + configs + timestamped protocol.md), updated HF model card, new Mendeley dataset version (gold-300 labels + guideline, under §7.2 licensing rules).

---

## 🗂 LEGACY ASSETS — carried over from the pre-defence report & conference paper

| Asset | Status | Role in v7 |
|---|---|---|
| HF model `shksabbir7/bengali-movie-review-classifier` | Published (cited in the paper) | Kept as the v1 artifact; **the new verifier is retrained** (v1 was trained on a leaked split) — document v1→v2 differences in the model card |
| Streamlit app movie-review-agent.streamlit.app | Live (single/batch/history UI) | Rebuilt on the new backend in Phase 8; UI structure reusable |
| Old hyperparameters: lr 2e-5/2.5e-5, 4–6 epochs, batch 16 | Tested | Starting grid for §3.1 — keeps the new search small |
| Old thresholds 0.7 / 0.45 / 0.6 | Used | **Superseded** — reported only as the comparison point for the new τ-sweep |
| Per-class table: Enthusiastic Casual recall **0.5674** | Paper Table I | Evidence of the middle persona's weakness — source of the §4.6 retry-rate hypothesis |
| Gemini 2.5 Flash (old Writer) | Used | Now the **secondary** robustness generator |
| LangGraph + ChromaDB + LaBSE stack | Used | Unchanged — proven to work |

**To correct in the thesis text:** unify the "9,998→6,114" vs "5,000 raw" story (S0 is the truth); delete the meaningless "6,114 representing 612 of 9,998" sentence; the 97.5% CV (LaBSE+LogReg) and 87.49% (BanglaBERT) are different experiments — un-conflate them in the abstract; remove the TF-IDF/Count-Vectorization and stemming/stopword sections (unused/harmful); resolve the emoji-tables-vs-emoji-free-data inconsistency; and never present "100% accuracy, 1.0 attempts" as success — discuss it as evidence of a dead loop.

---

## 📝 THESIS INTRODUCTION BLUEPRINT (write Chapter 1 to this structure)

**1.1 Background (3 paragraphs):** ① The Bangladeshi film industry's absence of pre-release audience feedback, and the rise of LLM persona simulation as a proposed remedy; ② but 2025–26 evidence shows prompt-only persona control is unreliable (Sands et al., NCAA 2026; WWW 2026 Companion) and intrinsic self-correction fails (Huang et al., ICLR 2024; The Self-Correction Illusion, 2026); ③ both problems sharpen in low-resource languages — Bangla as the testbed.

**1.2 Motivation:** the solution's pieces exist in separate literatures — persona generation (MoP), classifier gating (FUDGE/detox line), refinement loops (math/code) — **no one has joined them in a low-resource language**; a cheap trained verifier makes the approach practical for a real industry.

**1.3 Problem statement (one sentence):** *Whether an external, cheap, task-trained verifier embedded in a generate–verify–refine loop measurably improves persona-controllability of LLM text generation in a low-resource language, relative to prompting-alone and self-critique baselines.*

**1.4 Research questions:**
- **RQ1:** Can audience personas be discovered from unlabeled Bangla reviews via weak supervision, and validated as stable (bootstrap ARI, prediction strength) and human-recognizable (Krippendorff's α)?
- **RQ2:** Does an external trained verifier in an evaluator-optimizer loop measurably improve persona-controllability over zero-shot, few-shot, RAG-only, and LLM-self-critique baselines?
- **RQ3:** Does hybrid neural+symbolic validation outperform neural-only and symbolic-only gates?
- **RQ4:** Is the verifier-in-the-loop benefit larger in low-resource Bangla than under matched English (IMDB) conditions?
- **RQ5:** Does iterating against a fixed verifier induce measurable overoptimization (Goodhart), detectable via an independent held-out verifier?

**1.5 Objectives:** one operational line per RQ (from protocol.md).

**1.6 Contributions (seven):** ① a human-validated, persona-labeled Bangla review dataset with a 300-item gold set and released guidelines; ② a convergence-validated persona-discovery protocol (7 criteria + stability + theory); ③ a calibrated, cheap persona verifier with dual-accuracy reporting (weak-label vs gold); ④ a compound AI system implementing the evaluator-optimizer workflow with a trained-classifier gate — *to our knowledge* the first for persona control in a low-resource language; ⑤ an A/B held-out-verifier evaluation design for detecting Goodhart effects in refinement loops; ⑥ cross-lingual evidence (Δ_bn vs Δ_en) on where verification matters most; ⑦ full open release: code, model, traces, demo.

**1.7 Scope & limitations preview:** "simulation" = persona-conditioned generation (per-film prediction is not validated — the data lacks review-to-film mapping); ~~the three-persona scheme is theory-motivated and data-confirmed, with 3-vs-4 acknowledged as a modeling choice.~~ 🔴 **[D12] REPLACE — this sentence is now false in two ways.** K = 2, and the scheme is **not** "data-confirmed": G1 found no cluster structure. What the data supports is *a two-level cut through a continuum that human annotators can nonetheless recognise* (RQ1-H: 0.78/0.84 vs 0.25 chance). 🎁 State the advantage plainly — **Pinto et al. (2026) and Cornelissen et al. (2026) report the same geometric finding and neither ran human validation.**

**1.8 Thesis organization:** per the §6.1 chapter map.

---

## Master checklist — everything required
| Item | Source | Cost |
|---|---|---|
| GPU | Colab/Kaggle free | ৳0 |
| ~~Groq API (primary)~~ **Local generation on Kaggle T4 (2026-08-12)** + Gemini (secondary) | free | ৳0 |
| 3 Bangla annotators × ~300+100 items | Batchmates | honorarium optional |
| IMDB dataset | HuggingFace `imdb` | free |
| MPST v2 (English plot synopses — generation input, required) | ritual.uh.edu/mpst-2018 | free |
| LaBSE, BanglaBERT, DistilRoBERTa (+XLM-R, MuRIL, mBERT for §3.2) | HuggingFace | free |
| Storage | ~5 GB | — |

## Risk register
| Risk | Fallback |
|---|---|
| α < 0.667 (personas not human-recognizable) | Revise guideline + re-annotate; failing twice → reframe: "theory-driven scheme, validated learnability" |
| Loop activation drops accuracy | That is the real number — report it; the old one was an artifact |
| Goodhart detected (B flat) | Reframe headline: "verifier gaming in low-resource" — a high-citation finding |
| English arm exceeds one week | Cut to fertility + zero-shot reference |
| ~~Groq/Gemini rate limits~~ **Kaggle session caps (12 h, weekly GPU quota)** | ~~Batch + sleep + retry; fallback local Ollama (8B 4-bit) on Colab~~ **resumable JSONL: re-run skips completed keys (2026-08-12). Multi-accounting declined twice — appendix states how generations were produced** |
| ARI(cluster, sentiment) > 0.6 — personas ≈ sentiment | Engagement-feature re-operationalization, or honest "sentiment-anchored engagement tiers" reframe — both publishable |
| Symbolic adds <~2 points over neural-only (§5.1b) | Soften the hybrid claim; report the sensitivity curve regardless |
