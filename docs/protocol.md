# protocol.md -- FROZEN PRE-ANALYSIS PLAN
**Status: DRAFT -- not yet frozen. Freeze after the S2 pilot trap-check (Step 5).**

Signed by supervisor: ____________________  Date: __________
Frozen at commit: ____________________

> Purpose: this document is written BEFORE results exist. It is the defence
> against "you changed the experiment after seeing the numbers."

---

## Rule 0 -- three-outcome commitment
For every hypothesis below, the claim made under **win**, **mixed**, and
**negative** outcomes is written in advance. A negative result is a result.

---

## RQ1 -- Persona discovery
- **H1:** Audience personas are recoverable from unlabeled Bangla reviews and are
  (a) statistically stable and (b) human-recognizable.
- **Metrics:** bootstrap ARI (80% subsample x 100), prediction strength,
  Krippendorff's alpha (ordinal) on gold-300.
- **n:** R ~ 4,422 for clustering; 300 for human validation; 3 annotators.
- **Test:** PS >= 0.8 rule (Tibshirani & Walther); alpha bands 0.667 / 0.80.
- **Pre-committed trap-check:** ARI(cluster, Sentiment).
  **SUPERSEDED 2026-07-28** by the four-band scheme in "RQ1 pre-commitment:
  interpretation of ARI(cluster, Sentiment)" below, which was written before any
  ARI value was observed. The bands below are retained only to show what
  changed; **they are not operative**. See the deviations log.
  - ~~< 0.4  -> personas are independent of sentiment; proceed as planned.~~
  - ~~0.4-0.6 -> report the overlap explicitly; proceed with caveat.~~
  - ~~> 0.6  -> DO NOT claim independent personas.~~
- **Claims:** win = validated persona scheme; mixed = tentative scheme with
  disclosed overlap; negative = theory-driven scheme with validated learnability.

## RQ1 pre-commitment: interpretation of ARI(cluster, Sentiment)

> **Written 2026-07-28, before any ARI value has been observed.** The S2 pilot
> has never been run: no `results/s2_pilot_ari_trapcheck.md` exists at the commit
> that introduces this section. That is the entire point of writing it now.

The trap-check asks whether the discovered clusters are a rediscovery of the
three sentiment classes. Four bands, each with its claim fixed in advance:

**Band 0 — DEGENERATE flag ON** (any cluster holds <5% or >70% of n)
→ **No claim is permitted, in either direction.** A low ARI here is an artefact
of *non-partition*, not evidence of independence: a solution that fails to split
the data scores low by construction. Re-examine K, the encoder, and the distance
metric. **ARI reporting is suspended** until the partition is non-degenerate.

**Band 1 — ARI < 0.20**
→ Clusters are **not aligned with the sentiment axis**. This is *not* evidence
that the personas are valid — only that they are not a sentiment rediscovery.
The two questions are separate and must stay separate. **G-300 human validation
remains the arbiter** of whether the personas mean anything.

**Band 2 — 0.20 ≤ ARI ≤ 0.60**
→ **Partial overlap.** A **residual test is mandatory**, not discretionary:
conditioning on `Sentiment`, does cluster membership still predict length,
intensifier rate, and specificity? If **yes**, the persona claim survives but
**must be disclosed as sentiment-correlated** wherever it appears. If **no**, the
clusters add nothing beyond sentiment and Band 3 applies.

**Band 3 — ARI > 0.60**
→ **The persona claim fails as stated.** Two candidate explanations, and the
data cannot distinguish them:
1. genuine persona/sentiment overlap; or
2. a **venue/community selection effect** — clusters recovering the source
   Facebook group or YouTube channel rather than any persona. **This is
   untestable in principle here**, because venue was not retained at collection
   (provenance fact (c)). It must be stated as an unresolvable alternative
   explanation, not dismissed.

Response: reframe as **"sentiment-anchored engagement tiers"**, or
re-operationalize personas with engagement features (length / intensity /
specificity). Reported either way.

## REQUIRED falsification test: log-odds probe of the no-keyword-search claim

Provenance fact (c) — bulk pull, **no keyword or query-seeded search** — rests
entirely on the collector's recall. It is testable against the data, and
therefore **must be tested**. This is **REQUIRED, not optional**: a provenance
claim that could have been checked and was not is worth less than no claim.

**Test.** Log-odds ratio with an informative Dirichlet prior (Monroe et al.)
over the corpus vocabulary, per sentiment class and overall, looking for terms
whose over-representation is too extreme to arise from unseeded collection —
the signature of a query-seeded harvest.

**Both outcomes are pre-committed:**

- **Clean probe** (no dominant seed-like terms) → the collector's account is
  **corroborated by data rather than by recall alone**. The confidence on fact
  (c) is upgraded accordingly, and the basis of the upgrade is stated.
- **Dominant-term probe** (one or few terms dominate beyond plausible chance)
  → **the data overrides recall.** Fact (c) is wrong, the corpus is a
  keyword-seeded sample, and this is **logged as a protocol deviation** with the
  offending terms named. Any claim depending on unseeded collection is withdrawn.

Neither outcome is a failure of the study. Only *not running the probe* would be.

## RQ1-A pre-commitment: the trap-check re-run on region A alone

> **Written 2026-07-30, before the region-A run exists.** No
> `results/s2a_regionA_trapcheck.md` and no
> `results/s2_cluster_assignments.csv` exist at the commit that introduces this
> section. As with the original RQ1 pre-commitment, the commit timestamp is the
> evidence.
>
> **Honest framing:** the *decision* to analyse a subset was made after seeing
> S2c, so its origin is exploratory. What is pre-registered is the
> **interpretation** — what each outcome will be taken to mean — fixed before
> the number is known.

### Test 1 — is the full-corpus clustering recovering provenance?

`configs/s2_pilot.yaml` now scores the same clustering against `region` as well
as `Sentiment`. Pre-committed reading, on the **primary threshold 0.95**:

| Outcome | Claim |
|---|---|
| `ARI(cluster, region)` > `ARI(cluster, Sentiment)` | The encoder recovers **which file a review came from** more strongly than what it says. **No persona claim may rest on the full-corpus clustering.** The S2 trap-check is reported as confounded, and region A becomes the only defensible corpus. |
| `ARI(cluster, region)` ≈ `ARI(cluster, Sentiment)` (within ±0.05) | Both are weak axes; neither dominates. The split is disclosed as a confound and region A is still preferred, but the strong version of the objection is not established. |
| `ARI(cluster, region)` < `ARI(cluster, Sentiment)` | The two-corpus split is **not** the dominant recovered axis. This does not clear the corpus — the register difference is measured and real — but the full corpus remains usable with the split disclosed. |

### Test 2 — does any structure survive inside the organic corpus?

`configs/s2_pilot_regionA.yaml`: identical seed, encoder, K, thresholds and
bands; the only change is the subset (1,910 cleaned rows, 2 classes).

**Stated in advance, because it weakens the result and must not be discovered
afterwards:** region A has **two** sentiment classes while K = 3, so ARI between
a 3-way partition and a 2-class labelling is **structurally capped below 1**. A
low ARI here is therefore *weaker* evidence of persona-independence than the
same number was on the full corpus. A K = 2 run is registered as a **secondary**
comparison for exactly this reason; the K = 3 run is primary because three
personas is what the design posits.

The four bands from RQ1 apply unchanged, with the degeneracy gate first. In
addition:

| Outcome | Claim |
|---|---|
| Non-degenerate, ARI < 0.20 | Clusters in the organic corpus are not a sentiment rediscovery. **Still not evidence that personas are valid** — G-300 remains the arbiter — but the persona programme may proceed on region A. |
| Non-degenerate, 0.20–0.60 | Proceed with the residual test, disclosed as sentiment-correlated. |
| Non-degenerate, ARI > 0.60 | With only two classes and K = 3 this would be a strong result: the clusters reproduce sentiment despite the structural cap. Persona claim fails on the organic corpus too. |
| Degenerate | `NO_CLAIM`. At n ≈ 1,897 a degenerate partition may simply mean the corpus is too small for K = 3 — report that, do not tune K to escape it. |

### What is NOT pre-registered here

Whether the thesis ultimately runs on region A, on the full corpus with
disclosure, or takes the split itself as its object. That is a scope decision
(STATUS open decision 0b) and it is Sabbir's, not a number's.

## Scope decision: the thesis runs on the FULL corpus (Sabbir, 2026-07-30)

Region A alone was the conservative option and was declined. The full corpus is
used. **This is defensible only under the conditions below, and they are
conditions, not suggestions.**

### The one rule that makes it defensible

**`region` becomes a controlled factor, reported everywhere — not a footnote.**
The corpus is two corpora (fact (split)); pretending otherwise would be the
failure. Carrying region explicitly through the design turns a hidden confound
into a measured variable, and makes the split a *result* rather than a
liability.

Concretely, and all of it pre-committed here:

1. **The frozen split stratifies on `Sentiment × region`** (6 strata), not on
   `Sentiment` alone. G-300, R1 and R2 therefore each carry a proportional share
   of both corpora, and every downstream metric can be decomposed by region. A
   split stratified only on sentiment would make region-wise reporting a matter
   of luck.
2. **Every headline metric is reported three ways: full, region A, region B.**
   Not an appendix table — the main results table.
3. **G-300 is stratified on region as well as cluster**, and inter-annotator
   agreement is computed **per region**. If annotators agree less on one corpus
   than the other, that is itself evidence about what region B is.
4. **No claim survives that does not survive within-region.** A persona
   structure visible only across the full corpus, and absent inside both A and
   B separately, is a structure made of the seam.

### RQ1-B pre-commitment: the cross-region generalisation test

> **Written 2026-07-30, before any verifier exists.** This test does not appear
> in the original pipeline. It exists because the corpus turned out to be two
> corpora, and it converts that problem into a measurement.

Verifier-A is trained on R1 restricted to one region and evaluated on the other,
both directions, alongside the within-region baselines:

| Train → Test | Purpose |
|---|---|
| A → A, B → B | within-register baselines |
| **A → B**, **B → A** | the register gap, quantified |

| Outcome | Claim |
|---|---|
| Cross-region accuracy drops **> 15 points** below the within-region baseline in either direction | The two corpora are **not interchangeable for modelling**. Any full-corpus verifier number is an average over two populations and must always be presented decomposed. Reported as a primary finding, not a caveat. |
| Drop of **5–15 points** | Meaningful register gap; full-corpus numbers stay but every table carries the decomposition. |
| Drop **< 5 points** | The register difference does not impede transfer. The split is still disclosed — it is measured and real — but it does not threaten the modelling claims. |

**Any of the three is publishable, and the first is the most interesting.**

### What may NOT be claimed, whatever the numbers say

These follow from what is already established and are not contingent on any
future result:

1. **That the corpus represents organic Bangla audience opinion.** 60% of it has
   **unknown provenance** and a register no comment thread produces. Any framing
   of the corpus as "real audience reviews" is false as stated.
2. **Any prevalence or distribution claim.** Already excluded by fact (c);
   fact (split) makes it worse, not better.
3. **That agreement between generated text and region-B references measures
   realism.** If region B is machine-written — which is unresolved (open
   decision 0) — then a system that generates audience reviews, trained and
   scored against it, is partly **machine imitating machine**. This must appear
   in Limitations regardless of how open decision 0 resolves, because the
   thesis cannot currently rule it out.

Point 3 is the sharp one and it does not go away by choosing the full corpus.
It is the price of the larger n, and it is payable — provided it is paid in the
open.

## RQ2 -- Verifier-in-the-loop
- **H2:** An external trained verifier in a generate-verify-refine loop improves
  persona-controllability over zero-shot, few-shot, RAG-only, and self-critique.
- **Metrics:** persona accuracy under **Verifier-B** (never in the loop), MAUVE,
  length-JS divergence.
- **n:** 8 conditions x 2 languages x 100 eval-plots x 3 personas, >= 3 seeds.
- **Test:** bootstrap CIs, Benjamini-Hochberg correction, effect sizes.
- **Claims:** win = external verification helps; mixed = helps on some personas
  only -> report per-persona; negative = prompting suffices, report honestly.

## RQ3 -- Hybrid neural + symbolic
- **H3:** Hybrid gating beats neural-only and symbolic-only.
- **Pre-commitment:** if hybrid gains < 2 points over neural-only, the hybrid
  claim is softened; the sensitivity curve is reported regardless.

## RQ4 -- Cross-lingual
- **H4:** Delta_bn > Delta_en (verification matters more in low-resource).
- **Constraint:** mirror, never merge. English data never enters Bangla
  training / clustering / RAG.

## RQ5 -- Goodhart
- **H5:** Iterating against fixed Verifier-A induces overoptimization detectable
  as a gap between A-scores and B-scores across attempts.
- **Claims:** if detected, the headline is reframed to "verifier gaming in
  low-resource generation" -- pre-committed here so it is not post-hoc.

---

## Deviations log
Any departure from this document is recorded here with date, reason, and commit.

| Date | Section | Change | Reason |
|---|---|---|---|
| 2026-07-27 | S0 arithmetic | `null_rows` 1 → 2; `usable_n` 4722 → `n_after_rule_based_cleaning` = 4730 | Two distinct null rows exist (one missing review text, one missing sentiment label), not one. 4722 was produced by treating the three drop sets as disjoint (2+72+204=278 subtracted from 5000), which double-counts the 10 rows in SHORT ∩ DUP. True union under normalized duplicates = 270, giving 4730. **Final `usable_n` pending near-duplicate removal** (cosine ≥ 0.95, deferred to S2). Verified in `results/s0_data_xray.md`. |
| 2026-07-28 | RQ1 trap-check bands | ARI bands changed from 0.4 / 0.4–0.6 / >0.6 to **DEGENERATE / <0.20 / 0.20–0.60 / >0.60**; old bullet struck through and marked superseded | Written **before any ARI value existed** (S2 has never been run), so this is a pre-registration refinement, not a post-hoc adjustment. Three substantive additions: a degeneracy band (a non-partition scores low ARI by construction and must not be read as independence); a mandatory residual test in the middle band; and the venue/community selection effect named as an untestable alternative explanation in the top band, following provenance fact (c). ⚠️ `configs/s2_pilot.yaml` and `src/cluster/s2_pilot.py` still implement the OLD 0.4/0.6 bands — they must be updated before the pilot is run or its printed verdict will contradict this pre-registration. |
| 2026-07-28 | RQ1 code/protocol alignment | Code-vs-protocol mismatch **found and closed before the first run**: `configs/s2_pilot.yaml` and `verdict()` in `src/cluster/s2_pilot.py` still implemented the superseded 0.4/0.6 bands and derived the verdict from ARI alone | **No ARI value was ever produced under the old scheme** — the S2 pilot had not been run at any point while the mismatch existed, so nothing was observed, reported, or interpreted under the retired bands. Closure: config now carries the four-band scheme; `verdict()` evaluates **degeneracy as the first gate**, returning `NO_CLAIM` and emitting no PASS/CAVEAT/FAIL when the partition is degenerate, so ARI can no longer be read as independence when K-Means simply failed to partition; Band 2 emits a `RESIDUAL_TEST_REQUIRED` marker; verdict strings map one-to-one onto the protocol band names. Pinned by `tests/test_s2_verdict.py` (8 tests), including one asserting a degenerate partition with near-zero ARI returns `NO_CLAIM` and never a claim verdict. |
| 2026-07-28 | RQ1 / provenance | Log-odds probe registered as a **REQUIRED** falsification test of provenance fact (c) | Fact (c) ("no keyword or query-seeded search") is recall-based with no written collection log. It is testable against the corpus, so leaving it untested would be a choice to prefer an uncheckable claim. Both outcomes pre-committed. |
| 2026-07-30 | RQ1 / provenance — **register probe registered as EXPLORATORY** | New analysis added after the S2 result was seen: `src/preprocess/s2b_register_probe.py`, `configs/s2b_register_probe.yaml` → `results/s2b_register_probe.md`. It measures whether `Sentiment == 2` differs from classes 0 and 1 on **orthographic and structural features only** (punctuation, length, pronouns) — features that cannot encode an opinion about a film. | **The hypothesis came from reading the data, so this is exploratory and is labelled as such everywhere it appears. It is not, and may not be reported as, a confirmatory test.** It was run because S2's own crosstab pointed at it: refolded as *cluster 0 vs rest* × *class 2 vs rest*, φ = 0.565, **stronger than the clustering's association with sentiment overall** (V = 0.410), with only 12 of 1,572 class-2 items in cluster 0. Findings: class 2 is **100%** দাঁড়ি-terminated (others 58%/66%), **0%** first-person pronouns (expected 149), **0%** exclamation marks (expected 38), **0%** comma runs (expected 33), and draws **1,772** word types per 12,000 tokens against 3,577 / 3,303. This is the confound named in RQ1 Band 3 — clusters recovering the source rather than a persona — which `STATUS.md` had recorded as *untestable in principle* because venue was not retained. **That record was wrong in one specific way: venue was not retained, but writing style survives in the text and is measurable.** Nothing is trained (AUC is a rank statistic), so inviolable rule 10 is untouched. Consequence: the RQ1 persona claim is **suspended** pending `docs/provenance_query.md`. |
| 2026-07-30 | Provenance — **region split found; supersedes the s2b framing** | `src/preprocess/s2c_region_split.py` → `results/s2c_region_split.md`. The grouping variable is `raw_row`, not `Sentiment`. | The collector answered the s2b question with "collected the same way", so the raw `.xlsx` row order was examined directly (read-only; rule 1 intact). The label sequence has **10 runs in 5,000 rows** — the file was assembled in blocks — and the register signature tracks **position in the file, not label**: rows 3665–4330 are labelled 0 and sit at 99.8% দাঁড়ি / 0% first-person, while rows 499–896, also labelled 0, sit at 32% / 9%. Aggregated, rows 0–1998 (38.7% দাঁড়ি, 13.5% first-person, 255 types/1k) versus rows 1999–4999 (**99.2%, 0.8%, 128**), with a step transition over ~50 rows. **60% of the corpus is in the second region, across all three labels.** Consequences: (i) fact (reg) is superseded by fact (split) in STATUS — class 2 only looked special because all 1,670 neutral rows are nested inside region B; (ii) **every result over the full corpus is confounded, including the S2 trap-check**; (iii) provenance fact (c) cannot describe region B, and this document's pre-commitment that a computed test supersedes the recall-based provenance table is now operative; (iv) region A remains usable at 1,910 cleaned rows, organic, two classes. **Outstanding:** `ARI(cluster, region)` is the decisive number and cannot be computed until `s2_pilot.py` persists cluster assignments. Exploratory throughout. |
| 2026-07-31 | Plot corpus — **target reduced from 130 to whatever the source yields** (~124: 30 dev + ~94 eval) | The pipeline's §1.1.7 asks for 130 = 30 dev + 100 eval. bn.wikipedia does not contain 130 Bangla-film articles with a usable plot section. Four harvests: 67 → 110 → 132 → **124**, the last figure lower because a person-article veto removed 8 rows that had been counted as usable — actors' and directors' biographies swept in by the film categories. `N_DEV` stays at **30** (the dev slice tunes the loop threshold and 30 is the smallest defensible size); **eval takes the remainder**, with a hard floor of 80 below which the tool refuses to split. | **Two ways to reach 130 existed and both were refused.** (1) Relax the quality gate to admit two-sentence plots — but it was rejecting only ~20 of 3,135, so it is not the constraint, and thin plots are poor generation inputs. (2) Add the by-year categories, the largest available (২০১৯-এর = 268, ২০২২-এর = 220, ...) — but they are **language-neutral**: Tamil, Hindi, British and Japanese films sit in them, their bn.wikipedia articles are in Bangla, and they would therefore pass every gate in the harvester while quietly making the plot corpus stop being *Bangla cinema*. No check in the pipeline would have caught it. **Losing six eval plots costs a little power in a bootstrap CI; padding the set costs validity, which no n buys back.** 130 was a design choice in the spec, not a statistical requirement, and this is recorded before the number is used rather than after it is convenient. |
| 2026-07-30 | Provenance — `git_hash()` semantics | `-dirty` now reflects **tracked** modifications only (`git status --porcelain -uno`); untracked files are counted separately in `stamp()` as `untracked_files` | The suffix previously came from bare `--porcelain`, which also lists untracked files. Every run creates untracked artifacts — its own outputs, caches, a copied input — so every stamp came out `-dirty` and the flag stopped distinguishing anything; the one case it exists to catch (a result produced from edited but uncommitted source) had become invisible. This is why `results/s2_pilot_ari_trapcheck.md` carries `e3d8e434…-dirty` despite being produced from a **fresh `--depth 1` clone**, in which no tracked file *can* have been modified. The S2 result is therefore attributable to a pristine `e3d8e43`. Untracked files are reported, not ignored — a source file that was never committed is a real provenance gap. |
| 2026-07-27 | S1 class balance | Post-cleaning class balance is no longer uniform; the R1/R2 split will be sentiment-stratified | Raw 1665/1664/1670 becomes 1513/1599/1618 after S1. Drops concentrate in class 0 (152 of 270 total; 152 of the 269 labelled drops), because duplicates and sub-3-word reviews are over-represented in the negative class. Stratifying the R1/R2 split on `Sentiment` keeps the shifted distribution identical across partitions instead of letting it drift further. Counts in `results/s1_cleaning_log.json` and `docs/dataset_card.md`. |
