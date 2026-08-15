# protocol.md -- APPEND-ONLY PRE-ANALYSIS RECORD

**Status: SEALED 2026-08-10 for Phases 1-3.** Phases 4-6 (RQ2-RQ5) remain open
and are sealed separately when their first run happens.

**Signed by supervisor: ✅ YES — signature obtained.** Recorded 2026-08-11 on
Sabbir's report ("sir sign dise"). Sabbir's instruction was that the signed copy
does not need to be produced here, and it has not been requested again.

**Recorded exactly as what it is: a statement by the student, not a document in
this repo.** That distinction is kept because it is the same distinction the seal
packet asks the supervisor to rely on — every other claim in this file can be
checked against `git log` and `results/` timestamps, and this one cannot. It is
not weaker for that; it is differently sourced, and saying so costs nothing while
pretending otherwise would undercut the packet's own argument.

Sealed at commit: `d8b1f5d` (HEAD at 2026-08-10, the date the packet was prepared)

> **What this document is, stated precisely, because the earlier wording
> oversold it.** The header used to read *"FROZEN PRE-ANALYSIS PLAN ... freeze
> after the S2 pilot trap-check (Step 5)."* Step 5 ran on 2026-07-30 and the
> document was amended thirty-plus times afterwards, so that description was
> false on its face by August. It is replaced rather than quietly repaired.
>
> **The claim actually being made, and it is checkable:** this is an
> **append-only record**. Every section carries the date it was written; no
> section was edited after the run it governs; superseded text is struck through
> and marked, never deleted; and every departure is logged in the Deviations
> table at the end with a date and a reason. `git log --follow docs/protocol.md`
> against the timestamps in `results/` verifies all four properties
> independently of anyone's word.
>
> That is a narrower claim than "frozen before results existed", and it is the
> true one. A single freeze date would have been easier to sign and impossible
> to defend.

---

## Rule 0 -- three-outcome commitment
For every hypothesis below, the claim made under **win**, **mixed**, and
**negative** outcomes is written in advance. A negative result is a result.

---

## RQ1 -- Persona discovery

> ⚠️ **SECTION SUPERSEDED IN THREE WAYS. Retained verbatim because it is the
> original pre-registration and deleting it would destroy the record.** What
> replaced it, and where: the ARI bands → the four-band scheme immediately below
> (2026-07-28); the human-validation instrument → **RQ1-H**, the intrusion task
> (2026-08-08), after the α-based instrument failed its own reliability gate;
> the word *persona* and the noun *discovery* → the **engagement-specificity
> axis** framing (2026-08-10, deviations log). **Nothing in this section is
> operative.** Its stale quantities are struck through below rather than
> corrected in place, for the same reason.

- **H1:** ~~Audience personas are recoverable from unlabeled Bangla reviews~~
  → **an engagement-specificity axis is recoverable**, and `cluster_k2` is an
  imposed two-way cut through it — and it is
  (a) statistically stable and (b) human-recognizable.
- **Metrics:** bootstrap ARI (80% subsample x 100), prediction strength,
  ~~Krippendorff's alpha (ordinal) on gold-300~~ → **intruder-detection accuracy
  against a 0.25 chance rate (RQ1-H)**; the α instrument returned 0.4970 and is
  reported as an instrument failure, not as a result.
- **n:** R ~ ~~4,422~~ **4,625** for clustering; 300 for human validation;
  ~~3 annotators~~ **2 annotators**, both independent (deviation 2026-08-03).
- **Test:** PS >= 0.8 rule (Tibshirani & Walther); alpha bands 0.667 / 0.80.
  ⚠️ **The PS rule is now known to be passable by a contentless cut** — region B
  cleared it at 0.818 while correlating with nothing measurable (RQ1-G), which
  is the failure mode von Luxburg (2010) describes. PS is reported as necessary
  and **not** sufficient.
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
   Facebook group or YouTube channel rather than any persona. ~~**This is
   untestable in principle here**, because venue was not retained at collection
   (provenance fact (c)). It must be stated as an unresolvable alternative
   explanation, not dismissed.~~
   > ⚠️ **CORRECTED 2026-07-30 — this was wrong, and it was wrong in a way worth
   > keeping visible.** Venue was not retained, but **writing style survives in
   > the text, and style is measurable.** The confound was therefore testable,
   > was tested, and the evidence pointed straight at it: fact (split) in
   > `STATUS.md`, and `results/s2c_region_split.md`. The same correction was
   > applied to `STATUS.md` on 2026-07-30 and — through an oversight recorded
   > here rather than tidied away — **not** to this paragraph until 2026-08-10,
   > so the deviations log has been quoting an error this file was still
   > asserting. *"Untestable in principle"* is a strong claim and deserved a
   > harder look before it was written down.

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

> ⚠️ **RE-SCOPED 2026-08-05 — read the "Scope decision: Verifier-A and the RAG
> index run on region A only" section below before using this table.** The test
> as written here **cannot run**: it needs region-B labels for the axis, and the
> K=2 cut exists only in region A. The cross-region transfer test therefore runs
> on **sentiment classification**, which both regions support with real labels.
> The purpose (*"the register gap, quantified"*) and all three outcome bands
> carry over unchanged. **No claim about axis transfer across regions may be
> made.** The table is retained because the bands below are still the operative
> decision rule; only the task changed.

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

## RQ1-C pre-commitment: Gate G1, the master K-table

> **Written 2026-08-01, before the K-table exists.** No
> `results/s2d_ktable_regionA.md` exists at the commit that introduces this
> section. As with RQ1 and RQ1-A, the commit timestamp is the evidence.

### Where it runs, and why

**Region A only** (n ≈ 1,897 after dedup). The full-corpus clustering was shown
to be a corpus detector (93.3%); running a K-table on it would be selecting the
number of ways to split a file seam.

### The decision rule — taken from pipeline §2.2, not invented here

1. **Prediction strength:** the **largest K with PS ≥ 0.80** (Tibshirani &
   Walther's own cutoff).
2. **Bootstrap ARI:** 80% subsample × 100 runs, mean ± SD per K. **Stability
   beats compactness** where they disagree.
3. **Cross-checks:** GMM + BIC (soft membership — the honest model if personas
   overlap) and HDBSCAN (finds its own K, reports noise fraction). If HDBSCAN
   independently lands near the chosen K, that is strong evidence.
4. **If criteria disagree:** report the **full table**, no cherry-picking;
   stability > compactness; human validation and theory are the stated tie-break;
   the disagreement goes in Limitations.

### What each outcome means — fixed now

| Outcome | Claim |
|---|---|
| **Selected K = 3, PS ≥ 0.80, bootstrap ARI stable** | The three-persona design is **empirically supported**, not just posited. Proceed to S3 with K=3. This is the best case and it is *not* the expected one. |
| **Selected K = 2** | **The three-persona design gives way.** Region A has two sentiment classes, so a K of 2 raises the obvious worry that the clusters are the sentiment split — the ARI trap-check at K=2 settles that, and it is reported either way. If K=2 wins on stability, the thesis runs **two personas**, and the title's framing is adjusted rather than the data. K=3 is reported as the theory-motivated secondary, per pipeline §2.2. |
| **Selected K ≥ 4** | Report it. A K larger than the design posited is a *finding about the audience*, not a failure — but with n ≈ 1,897 and 8-word reviews, check the degeneracy band (5–70%) before believing it. |
| **No K reaches PS ≥ 0.80** | **`NO_STABLE_K`.** The honest reading is that this corpus does not support a stable partition at any K in 2–8. Then the persona scheme cannot be data-derived, and the thesis must either (a) use a **theory-driven** scheme validated by G-300, exactly as the pipeline's Gate G2 fallback already anticipates, or (b) reframe RQ1 as a negative result. **Both are publishable; neither is a reason to lower the cutoff.** |
| **HDBSCAN disagrees sharply** (e.g. finds 2 where PS picks 5, or >40% noise) | Reported as a robustness failure in Limitations. A high noise fraction is itself informative: it would mean much of the corpus belongs to no persona. |

### What is forbidden

- **Lowering the PS cutoff after seeing the table.** 0.80 is Tibshirani &
  Walther's, adopted before running.
- **Choosing K to match the three-persona design.** The design is the hypothesis;
  the table is the test.
- **Reporting only the criteria that agree.** The full table goes in the thesis.

### The trap-check runs at every K

`ARI(cluster, Sentiment)` is computed for **each** K in 2–8, with the same
pre-registered bands as RQ1. A K whose clusters merely reproduce the sentiment
split is disclosed as such regardless of how stable it is — stability and
validity are different properties.

## RQ1-D pre-commitment: what the K=2 partition is made of

> **Written 2026-08-03, before `src/cluster/s2e_profile.py` exists.** G1 has run
> and selected K = 2 (PS 0.860, ARI vs Sentiment 0.152 → Band 1). What has *not*
> been observed is anything about **what distinguishes the two halves**. No
> `results/s2e_regionA_k2_profile.md` exists at the commit that introduces this
> section, and the assignments themselves were never persisted by G1.
>
> **Honest framing, as in RQ1-A:** the decision to profile was made after seeing
> G1, so the *analysis* is exploratory in origin. What is pre-registered is the
> **interpretation** — fixed before the numbers are known, because the temptation
> here is specific and strong: with a stable K in hand, any difference found
> between the halves will look like a persona if nobody wrote down in advance
> what would *not* count as one.

### Why this step exists

G1 established that the cut is reproducible (PS 0.860, bootstrap ARI 0.940) and
that it is **not** the sentiment split (ARI 0.152). Three other indicators —
silhouette 0.053, a gap statistic rising monotonically and satisfying its rule at
no K, and **HDBSCAN calling 100% of points noise** — say there are no separated
groups to find. The recorded synthesis is that region A contains *a highly
reproducible bisection of a space with no separated groups*.

A reproducible bisection of a continuum is exactly what K-Means produces when it
cuts along the single dominant direction of variation. **The question this step
asks is what that direction is.** It is answered before G-300, because if the
direction turns out to be a surface property, annotating 300 items against it
would be spending the study's scarcest resource on a ruler.

### The decisive diagnostic — fixed now

**`length_auc`** = AUC of raw word count as a predictor of cluster membership,
taken as `max(auc, 1 - auc)` so direction does not matter. Reviews here average
~8 words; on L2-normalised LaBSE embeddings of very short text, length is a
plausible dominant axis, and it is measurable without a model.

| Outcome | Claim |
|---|---|
| `length_auc` ≥ 0.75 → **LENGTH_DOMINATED** | The partition is **substantially a length split**. It may not be called a persona structure. Two responses are permitted and both are pre-committed: (a) report RQ1 as a **negative result on data-derived personas**, which RQ1-C already established as publishable; or (b) re-operationalise personas on engagement features with length **explicitly controlled**, reported as a separate, clearly-labelled analysis. **Not permitted:** proceeding to G-300 on this partition as though it were a persona scheme. |
| 0.65 ≤ `length_auc` < 0.75 → **LENGTH_CONFOUNDED** | Length is a **major but not sole** component. G-300 may proceed, but the annotation guideline must be written so annotators cannot simply be reading length, and **length is reported alongside every persona claim in the thesis**, not in a footnote. |
| `length_auc` < 0.65 → **NOT_LENGTH** | The cut is not primarily about how much people wrote. This does **not** make it a persona — it only removes the cheapest alternative explanation. G-300 remains the arbiter, exactly as in RQ1 Band 1. |

### The secondary diagnostic

**`max_surface_auc`** = the largest `max(auc, 1-auc)` over *all* measured surface
features (word count, character count, দাঁড়ি termination, `?`, `!`, ellipsis,
first-person pronouns, Latin-script characters, digits, type-token ratio).

If **`max_surface_auc` ≥ 0.80 on any single feature**, then a property
computable with a regular expression separates the halves nearly as well as a
768-dimensional multilingual encoder. That is reported as a **headline finding
about the corpus**, whichever feature it is, and it carries the same consequence
as `LENGTH_DOMINATED` for the feature concerned.

### What may NOT be concluded from this step, in either direction

1. **That the two halves are personas.** No statistic in this file can establish
   that; only G-300 can. A clean `NOT_LENGTH` result removes an alternative
   explanation and does nothing more.
2. **That the halves are *not* personas, because a surface feature separates
   them.** Real personas plausibly *do* differ in length and punctuation. What
   `LENGTH_DOMINATED` establishes is that **the persona claim is unsupported**,
   not that it is false. The distinction is stated wherever this result appears.
3. **Anything from the distinctive-vocabulary list on its own.** Ranked terms
   are a **reading aid for a human**, not evidence. They are reported so Sabbir
   and the examiners can look at the halves directly; no claim in the thesis
   rests on them.

### Method note — inviolable rule 7

Distinctive terms use the **log-odds ratio with an informative Dirichlet prior**
(Monroe, Colaresi & Quinn 2008) over whitespace tokens: **no stemming, no
stopword removal, no TF-IDF.** Monroe's prior exists precisely so that stopword
removal is unnecessary. Nothing here is trained, nothing enters the RAG index or
any model, and no feature computed in this step is used as a model input — it is
a descriptive diagnostic and a reading aid. Rules 7 and 10 are intact.

## RQ1-E pre-commitment: the residual test, run voluntarily

> **Written 2026-08-03, after S2e's table was read but before
> `src/cluster/s2f_residual.py` exists and before any number in it is known.**
> No `results/s2f_regionA_k2_residual.md` exists at the commit that introduces
> this section.

### Why this is being run when the pre-registration does not require it

RQ1 Band 2 makes a residual test **mandatory** only at ARI ≥ 0.20. S2e reports
ARI(cluster, Sentiment) = **0.1522**, which is Band 1, so mechanically no
residual test is owed.

**Running it anyway, because ARI is the wrong instrument here and this project
has already been misled by it once.** The same 2×2 that yields ARI 0.1522 yields
**φ = 0.3981**, χ² = 300.7, and a cluster→sentiment accuracy of **69.5%** against
a 50.2% majority baseline — a 19.3-point lift. Every one of the twelve reviews
nearest cluster 0's centre is labelled positive; every one of the twelve nearest
cluster 1's centre is labelled negative; and the log-odds lists separate praise
terms (সুন্দর, অসাধারণ, সেরা) from complaint terms (না, নাই, বাজে, ফালতু).
`s2b_register_probe.md` recorded exactly this gap before (φ 0.565 against
V 0.410). A test that a reviewer will certainly demand, and that costs one
script over data already on disk, should not be skipped on a technicality.

**Recorded plainly: this is Band 1 by the pre-registered rule. The residual test
is voluntary and additional; it does not retroactively move the corpus into
Band 2, and no band assignment is being revised.**

### The four tests, and what each outcome will mean

Nothing is trained anywhere in this step. AUC and φ are rank/contingency
statistics; the richness comparison is sampling at a fixed token budget. Rule 10
untouched.

**Test A — does length separate the clusters *within* a sentiment class?**
Directionless AUC of `n_words` against cluster, computed separately for
Sentiment 0 and Sentiment 1; the reported figure is the **minimum** of the two.

| Outcome | Claim |
|---|---|
| min ≥ 0.60 | Length contributes **independently of sentiment**. The `LENGTH_CONFOUNDED` verdict stands on its own and is not an artefact of longer reviews being more positive. |
| min < 0.60 | In at least one sentiment class, length does not separate the halves. The length effect is then partly carried by sentiment and must be reported as entangled, not additive. |

**Test B — does sentiment separate the clusters *within* a length band?**
`|φ(cluster, Sentiment)|` inside each quartile band of `n_words`; the reported
figure is the **minimum** across bands.

| Outcome | Claim |
|---|---|
| min ≥ 0.20 | Sentiment contributes **independently of length**, in every band. |
| min < 0.20 | There is at least one length band in which sentiment does not separate the halves. Named, with its band, rather than averaged away. |

**Test C — the decisive one: how much is left over?**
Cross-classify Sentiment × `n_words` quartile (8 cells) and predict cluster by
each cell's own majority. Report accuracy against the marginal baseline (60.3%,
the larger cluster's share). **This is a resubstitution estimate fitted and
scored on the same rows, so it is an optimistic UPPER BOUND** on how much
sentiment and length together account for — and it is reported with that
sentence attached, every time.

| Outcome | Claim |
|---|---|
| lift ≥ 25 points | Sentiment and length **largely account for the partition**. The cut is then a valence × verbosity grid, and **the persona claim is unsupported**: G-300 would be paying three annotators to rediscover two variables already in the CSV. RQ1 is reported as a negative result on data-derived personas, exactly as RQ1-C permits. |
| lift 10–25 points | Substantial but partial. G-300 proceeds; **both** variables are reported as controls beside every persona claim, and the residual is stated as the part being annotated. |
| lift < 10 points | Most of the partition is explained by **neither**. Whatever LaBSE is cutting on, it is not valence and not verbosity — and G-300 becomes the right place to spend, because no cheaper instrument has explained the cut. |

**Test D — does the lexical-richness inversion survive a length control?**
S2e found cluster 1 is **33% shorter yet draws 18% more word types** at an equal
token budget (1,913 vs 1,623 per 4,000 tokens). Pure length would predict the
opposite, which is why this is currently the strongest evidence that the halves
differ in **kind** rather than in **size**. It is also the claim most likely to
be a length artefact, so it gets its own control: types at a fixed budget,
computed **within each length band**.

| Outcome | Claim |
|---|---|
| Inversion holds in **every** band | The difference in kind survives its most obvious control. Reported as the strongest pre-G-300 evidence for the persona reading — still not proof, and still subordinate to G-300. |
| Inversion holds in **some** bands | Reported band by band, never aggregated into a single sentence. |
| Inversion vanishes or reverses | It was a length artefact. **Withdrawn**, and the withdrawal is stated in the same place the claim was made. |

### What may not be concluded

A clean Test C (lift < 10) does **not** show the halves are personas. It shows
the two cheapest explanations have been eliminated. That is a stronger position
than S2e left us in and a weaker one than a persona claim requires, and the
thesis must say so in those words.

## RQ1-F pre-commitment: the G-300 human validation

> **Written 2026-08-03, before a single item has been annotated and before
> `src/annotate/` exists.** G-300 is now the decisive step for RQ1: S2f
> eliminated valence and verbosity as explanations of the K=2 cut, so no
> cheaper instrument remains that could pre-empt the annotators.

### Two constraints discovered before designing, and neither is negotiable away

**(1) Only 123 of the frozen G-300 are in region A.** The split was stratified on
`Sentiment × region` in August, before G1 chose K, so 177 of the 300 are region-B
rows that carry **no K=2 label** — G1 and S2e ran on region A only. Composition
of the usable 123: cluster 0 = 78 (26 neg / 52 pos), cluster 1 = 45 (35 neg /
10 pos).

**`data/splits/split_map_v1.json` is frozen (inviolable rule 3) and is not being
regenerated.** All 300 are annotated; the **cluster-validation analysis runs on
the 123**, and its reduced power is reported as a number, not as a hedge. The
alternative — drawing a fresh region-A gold set — was rejected because it breaks
the frozen split, which is the single artifact the whole design rests on.

**(2) Two annotators, not three — but both independent.** This is a **protocol
deviation from RQ1's stated `n = 3 annotators`** and is logged as one.

**Resolved 2026-08-04: Sabbir does not annotate.** Two independent annotators
were recruited, and the author is out of the loop entirely. The version of this
section written on 2026-08-03 carried a branch for "if Sabbir annotates anyway",
under which no claim of *independent* human validation would have been
permitted — only *partially independent*. **That branch is now dead and is
recorded here rather than deleted**, because the reason it existed is the same
reason the outcome matters: an author-annotator's agreement with an independent
one is partly evidence about the author's memory of the log-odds lists and the
cluster-representative reviews, not about the construct. G-300 now measures the
construct.

Neither annotator is in CSE or knows what the study is looking for. **They are
not told about clusters, K, the two halves, or any hypothesis** — only the
guideline. A rater who knows the expected answer drifts toward it, and the
agreement then stops being evidence.

- **Remaining consequence — with two annotators there is no majority**, so the
  adjudication rule is
  fixed now: **disagreements are not resolved.** No third-party tie-break, no
  discussion-to-consensus after the fact. The gold label for a tied item is
  **the mean of the two ordinal ratings**, and the disagreement rate is
  reported. Adjudicating after seeing the data is how an IAA figure gets
  laundered.

### The task: an ordinal rating, never a cluster assignment

Annotators **never see cluster labels, cluster names, K, or any statistic from
this repository.** They are not asked "which persona is this?" — that would
require handing them descriptions derived from the clusters, and their agreement
would then measure how well we wrote the descriptions.

Instead each review is rated on a **4-point ordinal scale of engagement
specificity**: how far the reviewer goes beyond a global verdict toward naming
what specifically they are reacting to. This construct was chosen because it is
what the data suggested — S2e/S2f found formulaic praise on one side and short
but *specific* complaint on the other, with the richness inversion surviving a
length control in all four bands — and because it is ordinal, which is what
RQ1 already pre-registered (Krippendorff's α, ordinal).

### The binding condition from RQ1-D, and how it is enforced

RQ1-D fixed that **annotators must not be able to succeed by reading length
alone.** Two enforcement mechanisms, because instruction alone is not
enforcement:

1. The guideline states explicitly that length is not the criterion, and
   includes **worked counter-examples in both directions**: a long unspecific
   review and a short highly specific one.
2. **Measured, not assumed:** the scoring script reports the rating→cluster AUC
   **within each length band**, the same control S2f used. If the rating's
   ability to recover the cluster disappears once length is held fixed, the
   annotators were reading length whatever the guideline said.

### Procedure

- **Calibration first:** 20 items, both annotators, then one discussion. After
  that, **no communication until all 300 are done.** Calibration items are drawn
  from `dev`, never from G, and are excluded from every reported figure.
- Items are **shuffled once with seed 42** and presented in identical order to
  both annotators, with region, sentiment, cluster and length hidden.
- **Sentiment is not part of the task.** If an annotator asks, the answer is
  that a scathing review can be highly specific and a rave can be formulaic.

### What each outcome means — fixed now

**Gate 1 — can humans agree at all?** Krippendorff's α (ordinal) on all 300.

| α | Claim |
|---|---|
| ≥ 0.80 | The construct is reliably annotatable. Proceed to Gate 2. |
| 0.667 – 0.80 | Tentative. Gate 2 proceeds, and every persona claim carries the α with it. |
| < 0.667 | **The construct is not reliably annotatable by humans.** Gate 2 is not run, because a rating nobody agrees on cannot validate anything. RQ1 is reported as a negative result — publishable under RQ1-C — and the failure is attributed to the construct, not to the annotators. |

**Gate 2 — does the human rating recover the machine's split?** Directionless
AUC of the mean rating against `cluster_k2`, on the 123 region-A items, tested
against a **permutation null**, and repeated within each length band.

> **⚠️ Amended 2026-08-03, before any item was annotated.** The first version of
> this section decided Gate 2 on whether a bootstrap 95% CI excluded 0.50. **That
> was wrong.** `directionless_auc` is `max(a, 1−a)`, so every bootstrap resample
> is bounded below by 0.50 and the lower bound essentially never reaches it —
> the `NEGATIVE` verdict was close to unreachable, and the test was biased
> toward finding an effect. On the single number that decides RQ1, that is the
> worst direction to be wrong in. Caught by the scorer's own smoke test.
> **Nothing had been observed when this changed** — no sheet was filled, no α
> and no AUC existed — so this is a pre-registration *refinement*, not a
> post-hoc adjustment, and it is logged in the deviations table with the same
> standing as the 2026-07-28 band revision. The bootstrap CI is still reported,
> for the **precision** of the estimate; it no longer decides anything.

The permutation null shuffles cluster membership, preserving class balance and
the statistic's floor, so it measures where a directionless AUC actually sits
under chance at n = 123 — which is well above 0.50. `p` is the share of 5,000
permutations reaching the observed AUC, with the customary +1 correction so a
permutation p-value is never reported as 0. Cutoff **α = 0.05**.

| Outcome | Claim |
|---|---|
| p < 0.05 **and** AUC ≥ 0.70 **and** it survives within every length band | **RQ1 wins.** The K=2 partition corresponds to a distinction humans perceive and agree on, and is not a length artefact. The halves may be called personas — with the qualifications already on record (no cluster structure, silhouette 0.053). |
| p < 0.05 but AUC < 0.70, **or** it fails within one or more length bands | **Mixed.** Reported band by band; the persona claim is disclosed as length-entangled and the failing band is named. |
| p ≥ 0.05 and AUC ≤ 0.65 | **RQ1 is a negative result.** Humans agree with each other but not with the machine: the K=2 cut is reproducible, not sentiment, not verbosity — and **not a distinction people make.** This is the most informative negative outcome available and is reported as a finding, not a failure. |
| p ≥ 0.05 but AUC > 0.65 | **Under-powered is not the same as negative.** Reported as **inconclusive at this n**, with the CI width and the null's own 95th percentile stated, and **not** written up as a refutation. n = 123 is a power limit, not a result. |

### What may not be done

- **No re-annotation of items after seeing Gate 2.** 
- **No dropping of "hard" items.** The disagreement rate is a result.
- **No revision of the scale or the bands after calibration.** Calibration
  aligns annotators to a fixed rubric; it does not rewrite the rubric.

## Scope decision: Verifier-A and the RAG index run on region A only (2026-08-05)

> **Delegated.** Sabbir asked for the best option rather than choosing; the
> choice and the reasoning below are Claude's, recorded as such so that nobody
> later reads it as the author's own judgement. **It is reversible** — nothing
> has been trained — and the alternative is pre-registered below rather than
> discarded.

Only **804 of 1,962** R1 rows carry a persona label, because the K = 2 partition
exists only in region A. Three options were open (STATUS decision 14). **Option
(a) is taken: Verifier-A trains on the 804 labelled region-A rows, and the RAG
index is built from those rows only.**

### Why, in order of weight

1. **Option (b) re-imports the confound the whole design controls for.**
   Assigning region-B rows to their nearest region-A centroid would manufacture
   labels for a corpus that the encoder can already separate from region A with
   **93.3% accuracy**. Those labels would encode register, not persona, and they
   would be indistinguishable from real ones inside the training set.
2. **Option (b) makes RQ1-B circular.** RQ1-B measures the cross-region transfer
   gap. If region-B labels are *defined* by region-A centroids, then testing
   A → B measures how well a model reproduces the rule that generated its own
   test labels. The test would pass for the wrong reason.
3. **Region B may be machine-written** (open decision 0, closed as
   unresolvable). Training a persona verifier on it and then reporting realism
   is the "machine imitating machine" problem this document already flags as
   unfixable. Option (a) confines that exposure to the evaluation, where it is
   disclosed, instead of putting it in the training set.
4. **n = 804 is small, and that is on-message rather than embarrassing.** Kamoi
   et al. §5.2 name fine-tuning for self-correction with **small training data**
   as unexplored. A verifier trained on 804 rows is an instance of the gap the
   thesis claims to address, provided the n is reported plainly and the
   confidence intervals are honest.

### The cost, stated rather than buried

**RQ1-B as written cannot run.** It trains Verifier-A on one region and tests on
the other; with no region-B persona labels, both directions are impossible.

**RQ1-B is therefore re-scoped, and its purpose is preserved.** Its actual
object was never persona transfer — it was *"the register gap, quantified"*. So
the cross-region transfer test now runs on **sentiment classification**, a task
both regions support with real labels, and is reported as a measurement of the
register gap between the two corpora. The three outcome bands (drop > 15 points
/ 5–15 / < 5) carry over unchanged, and the claim attached to each is unchanged.
**What may no longer be claimed is anything about persona transfer across
regions**, and that is stated wherever RQ1-B appears.

### Option (b) survives as a pre-registered robustness check

Nearest-centroid label propagation to region B, Verifier-A retrained on the full
1,962, **reported beside the primary result and never in place of it.**
Pre-committed now, before either is run:

| Outcome | Claim |
|---|---|
| Propagated-label verifier performs **similarly** | The region restriction costs little; reported as evidence that the primary result is not an artefact of n = 804. |
| Propagated-label verifier performs **better** | Expected, and **not** evidence of a better verifier — the extra labels come from the same geometry the verifier is being scored against. Reported as a **circularity demonstration**, which is the more interesting finding. |
| Propagated-label verifier performs **worse** | The register gap is large enough that region-B rows are actively harmful as persona training data. Strengthens the primary choice. |

## RQ1-G pre-commitment: independent replication of the K = 2 split in region B

> **Written 2026-08-05, before `configs/*_regionB.yaml` were run.** No region-B
> K-table, profile or residual test exists at the commit that introduces this
> section.

### Why this supersedes the reasoning in the scope decision above

The scope decision treats the two-corpus split purely as a liability to be
contained. **That was the wrong frame, and this section corrects it while the
correction is still free** — nothing has been trained.

Region B is not only a contaminant. It is a **second, independent corpus in a
different register**, and the single strongest thing that could be said about a
discovered structure is that it appears **in both**. So the same instrument —
identical seed, encoder, K range, thresholds and bands — is pointed at region B
and asked the same question. Three outcomes, all informative, all pre-committed.

**This does not change the primary line.** Verifier-A and the RAG index still
train on region A's 804 labelled rows, exactly as decided above. Replication is
additional evidence, not a substitute.

### What runs

`s2_pilot_regionB.yaml` → `s2d_ktable_regionB.yaml` → `s2e_profile_regionB.yaml`
→ `s2f_residual_regionB.yaml`. **No script changes**: every one of these already
takes the region as a config field. Same instrument, different subset.

### Matching rule — fixed now, because this is where the cheating would happen

If region B also selects K = 2, its two clusters must be matched to region A's
before anything can be compared. **The matching is done on the linguistic
profile, never on whichever pairing maximises agreement:**

> **Region B's cluster with the higher type count at an equal token budget is
> matched to region A's cluster 1.** That is S2e's own richness statistic, and
> it is the signature that survived the length control in all four bands.

The matching is computed and written down **before** any cross-region agreement
number is looked at. A rule chosen after seeing ARI is not a rule.

### What each outcome means

| Outcome | Claim |
|---|---|
| **B selects K = 2, and the matched clusters carry the same specificity signature** (richness inversion holds, length AUC in the same band) | **Independent replication.** The structure appears in two corpora that differ in register, provenance and possibly authorship. This is a far stronger basis for RQ1 than region A alone, and it is the outcome that would most improve the thesis. It also **gives region B its own labels, derived independently** — so RQ1-B recovers its original form and *can* test persona transfer without circularity, and the scope decision's re-scoping to sentiment becomes a fallback rather than the plan. |
| **B selects K = 2, but the signature does not match** | Two corpora, two different two-way splits. **No replication**, and the persona claim stays confined to region A. Reported as a negative replication, which is more informative than not having looked. |
| **B selects a different K, or `NO_STABLE_K`** | The region-A structure does not generalise. Reported plainly. **This does not retract anything about region A** — it bounds the claim to the corpus it was found in, which is where the claim already lives. |
| **B replicates, but region B is later shown to be machine-written** | Then the split is a property of **how film reviews get written**, not of an audience. Still a finding, and a sharper one than silence — but the persona framing would have to give way to something like "a reproducible register axis in Bangla film commentary". Pre-committed here so it cannot be quietly dropped if it happens. |

### What may not be concluded

Replication in region B would **not** show there is cluster structure. G1 already
established there is none in region A (silhouette 0.053, HDBSCAN 100% noise), and
the same diagnostics run in B. Replication of a *cut through a continuum* is
still a cut through a continuum — it would show the cut lands in the same place
twice, which is a claim about reproducibility across corpora, not about groups.

**G-300 remains the arbiter of whether either split is an audience distinction.**
No amount of replication substitutes for a human saying the halves differ.

## RQ1-H pre-commitment: human validation, attempt 2 — the intrusion task

> **Written 2026-08-08, before `src/annotate/intrusion_build.py` exists and
> before any item has been judged.** Attempt 1 (RQ1-F / step 5k) is reported in
> full and is not superseded, withdrawn or reframed. **This is a second attempt
> with a different instrument, and it is labelled that way everywhere.**

### What went wrong the first time — both causes, not one

1. **The rating scale collapsed.** 68–76% of ratings landed on the single value
   "2", so α fell to 0.4970 despite 75.5% exact agreement.
2. **The construct had to be named in advance, and Claude named it.** The task
   asked for "engagement specificity". *If that name was wrong, the test fails
   even when the clusters are real* — and nothing in attempt 1 could tell those
   two failures apart.

Cause 1 was diagnosed at the time. **Cause 2 was not, and it is the more
dangerous of the two.**

### Why an intrusion task, and what the literature says

**Chang et al. (NIPS 2009)** established the intrusion task as the way to test
whether unsupervised structure corresponds to *"natural groupings for humans"*.
It names no construct: the annotator is asked only which item does not belong.

**Kiritchenko & Mohammad (ACL 2017)** showed empirically that, at equal
annotation cost, comparative judgements are more reliable than rating scales,
and attributed rating-scale failure to exactly the inconsistency we hit. **Had
this been read before attempt 1, attempt 1 would not have used a rating scale.**

**Eklund et al. (2025), CIPHE** criticise intrusion — but specifically
*keyword* intrusion, showing that keyword abstraction skews cluster
interpretation in nearly half of instances. Their own method has participants
**read sample texts**. This design is document-level for that reason, and lands
on the supported side of that critique rather than the criticised side.

### Design

- **50 sets.** Each is 4 reviews: 3 from one cluster, 1 intruder from the other.
  25 sets with a cluster-0 majority, 25 with cluster-1.
- **Length-matched within every set** (max−min ≤ 2 words). RQ1-D's binding
  condition is thereby satisfied **by construction rather than by measurement** —
  there is no length signal left to read.
- **Items drawn from region A but NOT from G-300.** The clustering ran on all
  1,897 region-A rows, so G was never held out from it and confers no advantage
  here; drawing outside G means **both annotators see text they have never
  seen**, which attempt 1's items no longer can offer.
- Both annotators receive identical sets in identical (seed-42 shuffled) order.
- **Secondary block: 40 pairwise items**, one review from each cluster,
  length-matched, asking which goes into more specific detail.

### Gate A — is the split perceptible at all? (primary)

Accuracy at picking the intruder, against a chance rate of **0.25**, one-sided
exact binomial.

| Outcome | Claim |
|---|---|
| accuracy ≥ 0.45 and p < 0.05 | **`HUMANLY_PERCEPTIBLE`.** The K=2 partition corresponds to a distinction people can see without being told what it is. This is the outcome RQ1 needed and attempt 1 could not deliver. |
| p < 0.05 but accuracy < 0.45 | **`WEAKLY_PERCEPTIBLE`.** Above chance but slight; reported with the interval, and every persona-adjacent claim carries it. |
| p ≥ 0.05 | **`NOT_PERCEPTIBLE` — and this time it is a real negative.** The instrument cannot collapse and names no construct, so failure here means the split is not one people make. RQ1 is then reported as a **negative result** under RQ1-C, not as inconclusive. |

**Power, computed before running:** at n = 50, detecting 0.45 against 0.25 has
≈ 97% power (α = 0.05, one-sided); 32 sets would suffice for 80%. The margin is
deliberate — a second failed attempt on a power technicality would be the worst
outcome available.

### Gate B — is the distinction *specificity*? (secondary)

Only interpreted if Gate A passes. Accuracy against **0.50**, exact binomial,
n = 40 (≈ 85% power to detect 0.70).

| Gate A | Gate B | Claim |
|---|---|---|
| pass | pass | The split is perceptible **and** the construct is specificity. Strongest available outcome; the S2e/S2f profile is corroborated by humans. |
| pass | fail | **The split is real and our name for it is wrong.** A genuinely useful result, and one attempt 1 was structurally incapable of producing. The thesis then reports a perceptible distinction whose character is undetermined. |
| fail | — | Gate B is not interpreted. |

### LLM supplement — large n, and three caveats that are not optional

Following **Miller et al. (2024, Royal Society Open Science)**, who use a
generative LLM alongside human reviewers to bridge the *validation gap* for
short-text clusters, the same sets (plus a larger auto-generated pool) are also
judged by LLMs, multiple models × multiple runs.

**It is a supplement and may never be reported as the validation.** Three
reasons, all pre-committed:

1. **Nasution et al. (2024, IEEE Access)** find human annotation consistently
   beats LLMs on complex tasks in **low-resource languages** — and Bangla is
   one. This cuts directly against us.
2. **HUME (2025)** benchmarks nine LLMs as annotators on clustering-type tasks
   and finds them below humans (76.1% vs 81.2%).
3. **Encoder circularity, which we raise ourselves and did not find in the
   literature:** the clusters were produced by LaBSE, a neural text encoder, and
   an LLM is another. Agreement between them may reflect shared training-data
   statistics rather than a real distinction. **This is why no LLM result can
   substitute for a human one here**, and it is stated wherever the supplement
   appears.

**Human–LLM divergence is itself reported as a finding**, per Miller et al., who
observe intrinsic biases in both and challenge treating human coding as the
definitive standard.

### ⚠️ Recorded 2026-08-08, DURING annotation and BEFORE any answer was scored

Both annotators independently reported that **the items look alike to them** and
that they are struggling to tell the options apart. **No guidance was given in
response** beyond "answer anyway, guess if unsure, do not skip" — telling them
what to look for would destroy the test, and this note exists so that the
instruction actually given is on record.

This is written now, before the numbers, because afterwards it would read as an
excuse. **Two readings are possible and the data will not distinguish them:**

1. **The split is not humanly perceptible.** That is the `NOT_PERCEPTIBLE`
   outcome, it is a real negative, and it is what the instrument was built to be
   able to say.
2. **Length matching made the task strictly harder than RQ1 asks.** In region A,
   `length_auc` is **0.676** — length is a *genuine component* of the cut, not
   only a confound. By matching every set to within 2 words, this design removes
   that component entirely and asks whether the **residual, non-length**
   difference is perceptible. RQ1-D required only that annotators not succeed on
   length *alone*; matching enforces something stronger. **That was my design
   choice and it may have over-corrected.**

**Pre-committed reporting, whichever way Gate A lands:**

- If Gate A **passes**, reading 2 is moot and the result is stronger than
  required, because it was obtained with the length signal removed.
- If Gate A **fails**, it is reported as `NOT_PERCEPTIBLE` **with reading 2
  stated beside it in the same paragraph**, in these terms: *the K = 2 split was
  not recoverable by human annotators once length was held constant, and because
  length carries part of the split (AUC 0.676), this is a test of the residual
  distinction rather than of the whole one.* The claim is bounded to what was
  tested; it is **not** written as "humans cannot perceive the K = 2 split".
- **A length-unmatched re-run is NOT permitted**, even though it would be easier
  to pass. That is the third attempt this section forbids, and running it after
  seeing a failure is the exact move `protocol.md` exists to prevent. It may be
  proposed in Future Work, where it belongs.

### What may not be done

- **No third attempt.** If Gate A fails, RQ1 is a negative result and is
  written up as one. Iterating instruments until one produces a significant
  number is the failure mode this whole document exists to prevent.
- **No re-use of attempt-1 items**, which both annotators have seen.
- **No interpretation of Gate B when Gate A fails.**

## S3.2 pre-commitment: the verifier backbone ablation

> **Written 2026-08-08, before any verifier has been trained and before any
> backbone has been downloaded.** Nothing in this section may be edited after the
> first run. Pipeline §3.2 specifies this ablation; this section fixes its arms,
> its decision rule, and what each outcome licenses us to say.
>
> 🔴 **POINTER ADDED 2026-08-10 — the section body is unedited and stays that
> way; this note is navigation, not revision.** S3.2b returned
> `CIRCULARITY_CONFIRMED`: a frozen LaBSE probe scores **0.9866** against the
> best fine-tuned arm's **0.9647**. **The premise below — that this ablation is
> "the only available justification" for the backbone choice — did not survive
> its own result. The table may support NO claim about backbones.** See the
> three deviation rows of 2026-08-10 (S3.2 `TIE`, S3.2b, S3.2c) for what it may
> support instead. Read this section as the reasoning that was fixed in advance,
> not as a conclusion the thesis holds.

### Why the ablation is load-bearing, not decorative

Pipeline §3.2 frames the ablation as "the empirical answer to *why only
BanglaBERT?*", with an implied expectation that BanglaBERT wins and the choice
is thereby justified. **A Consensus search of the 2023–2026 Bangla
classification literature does not support that expectation, and this is
recorded before the run rather than discovered after it.** The field disagrees,
on comparable tasks and comparable data sizes:

| Reported winner | Where |
|---|---|
| BanglaBERT | Bangla emotion, 7,200 sentences, 0.83 macro-F1 (Hasan et al. 2025); Bangla sentiment, 10,861 comments (Hasan et al. 2023) |
| **MuRIL** | Bangla emotion, 92% — beating **both** BanglaBERT and XLM-R (Mitra et al. 2025) |
| **XLM-R** | BanglaBlend style classification, 94% vs BanglaBERT 93.4% (Hassin et al. 2026); BLP-2023 sentiment shared task (Mukherjee et al. 2023) |
| **IndicBERTv2** | 95.44% on the *same* BanglaBlend data, above XLM-R and BanglaBERT (Mazumder et al. 2025) |

The last two rows are the sharpest: **the same dataset yields three different
winners across three papers.** So "BanglaBERT is Bangla-native, therefore it is
the right verifier backbone" cannot be defended by citation. The ablation is the
only available justification, and its result is not predictable in advance —
which is the condition under which pre-registration is worth doing.

### Arms (7, fixed here)

| # | Arm | Why it is a candidate |
|---|---|---|
| 1 | `csebuetnlp/banglabert` | Bangla-native ELECTRA; the pipeline's default |
| 2 | `xlm-roberta-base` | Without beating it, "a Bangla-specific model is needed" collapses |
| 3 | `google/muril-base-cased` | Indic-specialised; beat both 1 and 2 in Mitra et al. 2025 |
| 4 | `bert-base-multilingual-cased` | Historical baseline |
| 5 | **`ai4bharat/IndicBERTv2-MLM-only`** 🆕 | Top scorer in Mazumder et al. 2025 on a Bangla style task, which is close in kind to ours |
| 6 | **SetFit, LaBSE body** 🆕 | Contrastive few-shot, designed for exactly our n; LaBSE is already in the pipeline (Tunstall et al. 2022) |
| 7 | **BERT-NLI transfer** 🆕 | Laurer et al. 2023 report +10.7–18.3 pp over classical models at 100–2,500 training texts, and note it works *particularly well on imbalanced data*. We have 804 rows at ~40% minority |

Arms 5–7 are additions to pipeline §3.2 and are logged as a deviation.
**Arm 6 is registered with a stated expectation of losing:** Beliveau et al.
(2024), the closest study to our setting (non-English, small, imbalanced,
domain-specific), found BERT-like models > SetFit > prompted LLMs. It is
included because it is cheap and because a pre-registered expected loser that
loses is evidence, while one that wins is a finding.

### Training protocol

- Data: the **804** labelled region-A rows of R1 (481 / 323), per the 2026-08-05
  scope decision. Dev = the 82 labelled dev rows. **G-300 is not touched.**
  **R2 is not touched** — it belongs to Verifier-B, and the wall is inviolable
  rule 6.
- Identical budget across arms: lr ∈ {2e-5, 3e-5} × 4 epochs, batch 16.
  Arms 6 and 7 use their own published training procedures at matched wall-clock,
  and that asymmetry is reported rather than hidden.
- **5 seeds per arm** (42, 43, 44, 45, 46). Not 3 — see the decision rule below.

### Decision rule — and why it is not "highest mean macro-F1"

Seed variance is reported as a **sensitivity measurement**, which Bethard (2022)
lists as a safe use of random seeds. It is **not** the decision rule. Bethard's
survey of 85 ACL Anthology papers names *"varying only the random seed to create
score distributions for performance comparison"* as a **risky** use, and finds
more than half of recent papers commit it. Gundersen et al. (2023) show that
small absolute effect sizes plus few repetitions readily produce wrong
conclusions; Casola et al. (2022) find only 20% of transformer papers report
multiple runs at all, and document low robustness to seed and hyperparameters;
Fu et al. (2023) give the theoretical stability bound behind the phenomenon.

**The winner is therefore decided by a paired bootstrap significance test**
(10,000 resamples of the dev set, paired across arms, α = 0.05,
Benjamini–Hochberg across the 21 pairwise comparisons). Precedent: Hasan et al.
(2025) settle exactly this comparison in exactly this language with a paired
bootstrap test.

Pre-committed outcomes:

| Outcome | What we may claim |
|---|---|
| One arm is significantly best | It becomes the Verifier. The choice is empirically justified and reported with its test statistic. |
| **A set of arms is statistically indistinguishable** | **Report the tie as the result.** The tie-break is then declared openly and on non-performance grounds — smallest parameter count first, then the pipeline's default (BanglaBERT) — and the thesis says in those words that *the backbone choice was not determined by the data*. This is the outcome the literature's disagreement makes most likely, and it is registered as publishable. |
| BanglaBERT is significantly beaten | Use the winner. "Monolingual vs multilingual verifier in low-resource" becomes a small finding in its own right, consistent with Mitra et al. 2025 and Mazumder et al. 2025. |
| Every arm is near chance | The K=2 label is not learnable at n=804 from ~8-word text. **RQ2 cannot proceed as specified**, and that is reported rather than rescued by adding data or relaxing the label. |

### What may not be done

- **The winner is selected on weak-label macro-F1 — label *reproduction*, not
  validity.** No human-validated accuracy exists for any verifier (deviation of
  2026-08-08). Every defence of the backbone choice states this.
- **No arm may be added after seeing a result**, and no arm may be dropped
  because it performed badly. Arms 5–7 are registered above precisely so that
  their inclusion cannot later look like a search for a better number.
- **No hyperparameter search beyond the two learning rates fixed above.**
- G-300 and R2 are not read by any part of this step.

## S3.4 pre-commitment: calibration is descriptive, not a contribution

> **Written 2026-08-08, before any verifier exists.**

Pipeline §3.4 calls calibration "the hidden contribution": reliability diagram
(10 bins), ECE, Brier, temperature scaling, ECE before/after. **At our n that
framing cannot be sustained, and saying so now is cheaper than defending it at
viva.** The dev slice is **82 rows**. A 10-bin reliability diagram puts ~8
samples in a bin; the resulting ECE is dominated by binning noise, and a
before/after ECE improvement computed on 82 rows is not a measurement anyone can
rely on.

What stands, and why:

- **Temperature scaling is kept, and deliberately not upgraded.** Balanya et al.
  (2022) show that expressive calibrators outperform simple ones when data is
  plentiful and **fail when it is scarce**, while simple scaling stays robust.
  Guo et al. (2025) make the same point from the variance side: methods
  operating on full logit distributions suffer high variance under insufficient
  validation data. The single-parameter method is the correct choice here *because*
  n is small, not despite it.
- **ECE is reported with fewer bins (5) and a bootstrap CI**, never as a bare
  scalar, and the bin count is fixed here rather than chosen after seeing which
  count flatters the result.
- **The calibration figure is labelled descriptive** in the thesis and in any
  paper. It illustrates the verifier's confidence behaviour; it does not
  establish that the verifier is calibrated.
- τ in §4.5 stands on this confidence. Since the calibration behind it is weak,
  **τ's sensitivity is reported as a curve, not a point**, and the pipeline's
  existing requirement to sanity-check the final τ against Verifier-B scores
  becomes mandatory rather than advisory.

**Pre-committed:** if post-scaling ECE improvement is smaller than its own
bootstrap CI, the honest statement is *"calibration could not be established at
this sample size"*, and it is written in those words. That is not a failed step;
it is the step returning what it can support.

## RQ2 -- Verifier-in-the-loop
- **H2:** An external trained verifier in a generate-verify-refine loop improves
  ~~persona-controllability~~ **label-controllability** over zero-shot, few-shot,
  RAG-only, and self-critique.
- **Metrics:** ~~persona accuracy~~ **`cluster_k2` label accuracy** under
  **Verifier-B** (never in the loop), MAUVE, length-JS divergence.
- **n:** 8 conditions x 2 languages x **90** eval-plots x ~~3 personas~~
  **2 axis levels**, >= 3 seeds.
  (90, not 100 — the plot corpus froze at 120 = 30 dev + 90 eval on 2026-07-31;
  see the Deviations entry of that date. **"3 personas" was stale from
  2026-08-03**, when Gate G1 selected K = 2; corrected 2026-08-10.)
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

## S3.5 pre-commitment: the symbolic scorer's feature pool

> **Written 2026-08-11, before `src/symbolic/` exists and before any feature has
> been computed on any row.** Pipeline §3.5 specifies this component; this
> section fixes its **feature families**, why each is there, what is deliberately
> excluded, and where its weights are fit. **The search that produced it ran
> before the design, per the standing instruction — and it changed the design.**

### Why the pipeline's list, as written, is the wrong list

§3.5's pool is: intensifier count, positive/negative lexemes, length bucket,
exclamation, negation, name mentions, specificity terms. **Almost every item is
"does the text contain X".** `mahmoud2026rubric` shows that **presence-based
criteria are the category that gets hacked**: under a *strong* verifier, gains
concentrated in presence-based criteria (+1.07 completeness) while conciseness
(−2.91), relevance (−1.10) and factual correctness (−0.85) all degraded.

**Our loop makes this worse than theirs**, and the mechanism is in §4.2: the
Reflector *tells the Writer which rule failed* ("no intensifiers [R1 failed]").
Their policies had to discover the rubric. Ours is handed it. **A pool of
presence rules under a loop that names the failing rule is a gaming instruction,
not a scorer.**

### The construct has prior art, and a validated feature set

**This was not known to the project before 2026-08-11 and it changes the
framing:** our construct is **sentence specificity**, an established task
(Louis & Nenkova 2011; Li & Nenkova 2015; `ko2019specificity`), *"the level of
detail in a sentence."* `ko2019specificity` evaluates on **movie reviews** —
our domain — reaching Spearman **0.702**, against a **length baseline of 0.581**.

**Length is a strong but incomplete predictor of specificity.** That is their
result and ours: `length_auc` = **0.6764**. It is registered as expected, not
as a defect.

### Feature families — fixed here

| # | Family | Members | Gameable? |
|---|---|---|---|
| **F1** | **IDF statistics** 🆕 | min / max / mean IDF over whitespace tokens, IDF computed on **R1 only** | 🟢 **Hard.** Raising it requires using genuinely rarer words — which *is* the construct. This is the one family that cannot be satisfied vacuously |
| F2 | Length & shape | token count, mean characters per word | 🟡 trivially gameable, retained because it is genuinely predictive (0.581 baseline) and its contribution is *reported*, never hidden |
| F3 | Normalised orthography | punctuation, digits, Latin-script chars, দাঁড়ি termination — each **divided by length** | 🟡 |
| F4 | Discourse connectives | কিন্তু, তাই, কারণ, যদিও, তবে | 🔴 highly gameable |
| F5 | Sentiment-bearing fraction | fraction of tokens in a polarity list (ভালো/বাজে/ফালতু), **as a fraction, not a count** | 🔴 highly gameable |
| F6 | Lexical richness | **length-corrected** richness (Guiraud-type V/√N), never raw type-token ratio | 🟢 harder — S2e's richness inversion survived a length control in **all 4** bands |

**F1 and F6 are the load-bearing pair, and both are distributional.** F2–F5 are
retained because §3.5 mandates them and because the Reflector needs
human-readable rules to name — **but every one of them is registered as
gameable, in advance, and their weights are reported individually.**

### Deliberately EXCLUDED, with reasons

- **Word familiarity / imageability norms** — used by `ko2019specificity`, and
  **no Bangla norms exist** that we could verify. Not silently dropped: stated.
- **Stop-word fraction** — would require building a Bangla stop-word list. Rule 7
  forbids stop-word *removal*; a fraction is not removal, but no resource exists
  and inventing one is unjustified.
- **Emoji** — zero in the corpus (S0 verified).
- **Name mentions** as a standalone rule — §3.5 lists it; retained only inside F1,
  since names are naturally high-IDF and a separate presence rule adds a gameable
  surface without adding signal.

### Where the weights are fit — and this is a change

- **Feature weights: logistic regression, never hand-set** (§3.5's own rule),
  on the **82 labelled dev rows**, reported with that n.
- 🔴 **The hybrid weight (§3.5's 0.6/0.4) moves OFF the 82 rows onto the 30
  dev-plots' generations.** At Verifier-A = **0.9866** (1 error in 82) the sweep
  is degenerate: every weight in §5.1b's 0.5–0.8 grid returns the same answer,
  and the "<2 points" rule would need to resolve **1.6 dev items**. The weight is
  a **generation-time** parameter and is fit where the Critic operates.
  ⚠️ Reinforced by `kapur2026length`: in *human* text longer means more specific,
  but in **machine-generated text that relation is flat or reversed** — so a
  weight calibrated on real reviews is not transferable to generated ones.
- Reported as a **sensitivity curve, never a point** (as for τ).

### Pre-committed outcomes

| Outcome | Claim |
|---|---|
| Symbolic adds **≥ 2 points** over neural-only on dev-plots | The hybrid claim (RQ3) stands, and the **per-family weights are reported** so the reader sees whether the gain came from F1/F6 or from the gameable families |
| Symbolic adds **< 2 points** | **RQ3's own pre-commitment fires: the hybrid claim is softened.** Registered as the expected outcome given Verifier-A's ceiling. The scorer is still built and still used, because §4.2's Reflector cannot name a failing rule without it — *interpretability is a stated purpose, not a consolation* |
| Gain comes **only** from F2–F5 (the gameable families) | 🔴 Reported as a **negative result about the hybrid design**: the symbolic contribution is exactly the part a generator could fake. Stated in those words |

### Registered gaming diagnostic (feeds RQ5, not RQ3)

Per-family symbolic scores are logged **per attempt**. **Presence-family (F2–F5)
scores rising across attempts while Verifier-B stays flat is Mahmoud et al.'s
signature**, and is reported alongside the A−B gap and the invariance check.
**Symbolic is registered as an instrument for detecting gaming, never as a shield
against it** — the shield framing was proposed on 2026-08-11 and rejected by the
same search that produced this section.

## S3.3 pre-commitment: training and evaluating Verifier-A and Verifier-B

> **Written 2026-08-11, before either verifier exists.** No checkpoint has been
> fitted, no dev number computed. Decision 16 (2026-08-10) fixed *what* A and B
> are; the 2026-08-11 disambiguation fixed *which data* B trains on. **Three
> things were still unregistered, and are fixed here: B's learning rate, B's
> evaluation slice, and whether Verifier-A needs calibrating at all.** The
> search that produced this section ran before the design, per the standing
> instruction. **Index used: alphaXiv** — Consensus's quota is exhausted until
> 1 September 2026, and that is recorded rather than worked around, because
> "searched a different index" and "did not search" must not look alike.

### The two artifacts, restated so no config has to infer them

| | Verifier-A | Verifier-B |
|---|---|---|
| Role | In-loop gate (§4.2 Critic) | S6 evaluation only — **never in the loop** (inviolable rule 6) |
| Model | **Frozen LaBSE + L2 logistic head.** Nothing is fine-tuned | **The S3.2 BanglaBERT *recipe*** — same backbone, budget, seeds — **retrained** |
| Training data | **R1**, region-A labelled, dev held out: **n = 804** (481/323) | **R2**, region-A labelled: **n = 888** (531/357) |
| Checkpoint reuse | — | 🔴 **None.** The S3.2 checkpoints are `role: A`, i.e. trained on R1. Loading one as Verifier-B would put A and B on the same data and void rule 6 |
| Evaluation | dev-82 | dev-82 |

### Registered decision 1 — Verifier-B's learning rate is **fixed at 2e-5**, not selected

S3.2's recipe sweeps `lr ∈ {2e-5, 3e-5}` × 5 seeds. **Verifier-B runs 5 seeds at
lr = 2e-5 only**, the value pipeline §3.1 specifies as the default. No
hyperparameter is chosen by looking at a score.

**Why, and the search that decided it.** `schneider2025overtuning` (AutoML 2025)
re-analyse seven large HPO benchmark suites and define *overtuning*: selecting the
validation-optimal configuration and thereby generalising **worse than the
default**. It happens in **~10% of runs** ("severe", relative overtuning > 1.0),
and their mixed-model analysis names the conditions that make it worse — **small
datasets, holdout rather than cross-validation, and binary classification under
an accuracy-type metric**. *All four describe this exact run:* 888 training rows,
an 82-row holdout, two classes, macro-F1. Their own recommendation is to prefer
(repeated) CV over holdout at small n. **We take the stronger option available to
us: do not tune at all.** The claim the thesis may then make is checkable —
*"Verifier-B's learning rate was taken from the pipeline specification and never
selected against a score"* — which no amount of CV would buy.

**Cost, named:** Verifier-B may be slightly worse than a tuned Verifier-B would
be. That is accepted deliberately. **A verifier that is 2 pp weaker is a
reportable fact; a verifier whose 82-row holdout was reused for selection and
then for reporting is an unreportable one**, and RQ5 rests on B's number being
independent of everything A's number touched.

**Sabbir's call, taken 2026-08-11**, from the three options above.

### Registered decision 2 — both verifiers are evaluated on the **same dev-82**

`data/splits/split_map_v1.json`'s `_contract` says `dev` is *"Subset of R1.
Threshold sweep only."* **That wording is extended here, deliberately and with a
deviation row**: dev-82 is also the evaluation slice for both verifiers.

**It is leakage-free, and the reason is structural rather than a promise.**
`dev` ⊂ R1 and is held out of Verifier-A's 804. `dev` ∩ R2 = ∅ by the frozen
split's own contract, so it is untouched by Verifier-B's 888. **Neither verifier
has seen any of the 82 rows.** S3.2 and S3.2b already used dev-82 as their
evaluation set, so this is a continuation, not a new use.

**Why the same slice rather than one each.** RQ5 measures the **gap between
A-scores and B-scores** as the loop optimises against A. If A and B are measured
on different items, that gap confounds *model difference* with *item difference*,
and no amount of care afterwards separates them. Head-to-head on identical items
is the only configuration in which the Goodhart gap means what RQ5 says it means.

**What dev-82 may NOT be used for**, restated because this section widens its
use: no hyperparameter selection, no threshold tuning that feeds back into
training, no arm selection. It is a reporting surface. τ's sweep (§4.5) is the
one tuning use the contract already allowed and it stands.

**Power, stated in advance so a null is readable.** At n = 82 one item is
**0.0122** macro-F1. Verifier-A is expected near 0.9866 (1 error) from S3.2b and
Verifier-B near 0.9647 from S3.2's BanglaBERT arm — **a difference of ~1.8
items**. 🔴 **Pre-committed: no claim that either verifier is better than the
other may be made from dev-82.** The A−B comparison this slice supports is
*"both are competent on the same items"*, which is all the cross-family wall
requires. RQ5's gap is measured on **generations**, not here.

### Registered decision 3 — 🔴 the "natively calibrated" claim in decision 16 is **withdrawn**

Decision 16 (2026-08-10) justified Verifier-A partly as *"best measured, seconds
to fit, **natively calibrated**, no GPU in the Phase 4 loop."* **The
"natively calibrated" clause was written from memory and is wrong.**

`zhang2026tabpfn` evaluate nine classification heads on frozen image, text and
audio encoders across **22,820 episodes**, 14 datasets and 11 encoders. Logistic
regression takes the **best mean rank on accuracy** (3.20) — and ranks **below**
kNN and every in-context head on **both** calibration metrics. At their canonical
setting its **Top-1 ECE is 0.069**, against kNN 0.037 and TabPFN 0.031, and its
NLL (0.581) is the second worst of ten heads. Their own summary: *"strong
accuracy does not inherently guarantee well-calibrated probabilities."*

**What this changes and what it does not.**

- ❌ **Withdrawn:** the assertion that Verifier-A needs no calibration. It has no
  support, and §3.4's temperature-scaling stage is therefore **mandatory for
  Verifier-A**, not optional.
- ✅ **Unchanged:** the choice of Verifier-A itself. The same paper's practical
  guidance is that *"logistic regression or SVM remains appropriate for extremely
  low shot counts, high dimensions, or near-ceiling tasks"* — and this task is
  **high-dimensional (768-d LaBSE) and near-ceiling (0.9866)**, i.e. all three.
  The literature supports the artifact and refutes one sentence of its defence.
- ⚠️ **Bounded:** their canonical grid is 10-class; ours is binary, and they note
  the calibration advantage over classical heads **narrows at C = 2**. The
  correction is therefore recorded as *"the claim had no support"*, not as
  *"Verifier-A is definitely miscalibrated"* — a distinction the ECE figure will
  settle on our own data.

**This is the fourth entry in CLAUDE.md's table of decisions made without
searching first**, and it is the cheapest one to have caught: the sentence had
been in `protocol.md` for one day and no code depended on it yet.

### Calibration protocol (inherits the 2026-08-08 S3.4 amendment unchanged)

**5 bins, not 10.** ECE and Brier before and after temperature scaling, each with
a **bootstrap CI over the 82 rows**, and the figure labelled **descriptive**.
Pre-committed null statement, unchanged: *"calibration could not be established
at this sample size"* fires if the ECE improvement is smaller than its own CI.
The temperature is fitted **on dev-82 and reported as fitted there** — at n = 82
there is no second slice, and an in-sample temperature reported as in-sample is
honest where a held-out one would be fictional.

### Three-outcome commitment (Rule 0)

| Outcome | What is claimed |
|---|---|
| Both verifiers ≥ ~0.90 macro-F1 on dev-82 | The cross-family wall is built from two competent evaluators; Phase 4 proceeds. **No claim that either is better.** |
| Verifier-B clearly below A (> 5 items) | Reported as-is. `baker2025monitoring` already establishes that a weaker monitor of a stronger system is documented practice, so this **bounds** RQ5's interpretation rather than voiding it — and the bound is stated in Ch.5 |
| Verifier-B at or below the S3.2b surface baselines (length rule 0.6197) | 🔴 **Stop.** R2's labels or the retraining are broken, and this is checked for a bug before it is believed — the same rule S3.2b's `NOT_CIRCULAR` band carries |

### Scope of Phase 3 as delivered

Pipeline §3.1 asks for **four** verifiers (A/B × bn/en). **This step delivers
two.** The English pair is scheduled, not cut (STATUS, 2026-08-11), and runs after
the Bangla machinery exists. **Phase 3 is therefore closed as "Bangla-complete",
and the English half is named as outstanding rather than counted as done.**
§3.3's dual-accuracy table remains **not producible** (logged 2026-08-08): G-300
returned specificity ratings, not cluster labels, and they failed reliability.

## S4 pre-commitment: the Phase 4 loop, the hybrid weight, τ scoping, and the generator pilot

> **Written 2026-08-11, before `src/agents/` contains a single line and before
> any generation exists anywhere in this project.** Phase 4 has produced no text,
> no score and no trace. Everything below is a procedure fixed in advance of the
> numbers it will govern, which is the only order in which a procedure can be
> registered at all.
>
> **Index used: alphaXiv.** Consensus's quota is exhausted until 1 September
> 2026. Recorded rather than worked around, for the reason §S3.3 gives:
> *"searched a different index"* and *"did not search"* must not look alike.
>
> **Prerequisite state, verified on disk rather than read from STATUS.**
> `artifacts/verifier_a.joblib` and `artifacts/verifier_b/` both exist, committed
> in `0d2578d`; `results/s3c_verifier_a.md` reports dev macro-F1 **0.9866** with
> T = **0.1092** (`CALIBRATION_IMPROVED`), `results/s3d_verifier_b.md` reports
> **0.9597** at seed 42 (`COMPETENT_EVALUATOR`, `CALIBRATION_NOT_ESTABLISHED`).
> The symbolic scorer is fitted (`results/s35_symbolic.*`). **So the Critic has
> both of its terms and Phase 4 is unblocked.** ⚠️ `docs/STATUS.md` said the
> opposite in two places when this section was written — see the deviations row.

### The four components, restated so that no config has to infer them

Contracts are §4.2's and are **not** re-specified here; what follows is only what
§4.2 leaves open. Naming is §4.0's, verbatim and non-negotiable: **a compound AI
system implementing the evaluator–optimizer workflow.** The phrase *autonomous
multi-agent system* may not appear in any file this phase produces.

| | Component | LLM call | Registered here |
|---|---|---|---|
| 1 | Researcher | no | retry-query contract, exemplar-overlap logging |
| 2 | Writer | **yes** | generator identity (decision 3) |
| 3 | Critic | **no, deliberately** | `w` (decision 1), τ scoping (decision 2) |
| 4 | Reflector | yes, small | FAIL-only firing, failed-rule naming |

🔴 **Rule 6, restated as a code-level constraint rather than an intention:**
Verifier-B may not be imported, loaded or referenced anywhere under
`src/agents/`. It scores S6 and the τ endpoints only. A test must fail if the
Phase 4 package acquires a path to it. **This wall *is* the Goodhart test**, and
the one previous near-miss (2026-08-11, Verifier-B's data definition) shows the
wall collapses through ambiguity, not through disagreement.

### Registered decision 1 — `w` has **no value**, and may not acquire one before the dev-plot generations exist

The pipeline's ~~`0.6 × VerifierA + 0.4 × symbolic`~~ is struck (2026-08-11).
`w` is **fit on the 30 dev-plots' generated outputs** and **reported as a
sensitivity curve, never as a point**. Inclusion of the symbolic term must
additionally survive a **held-out marginal-value test** — not a standalone score.

**Pre-committed outcomes, fixed before any curve is drawn:**

1. **`SYMBOLIC_EARNS_ITS_PLACE`** — the verdict is sensitive to `w` and the
   held-out marginal-value test favours including the symbolic term. RQ3's
   original hypothesis is supported and the curve is the evidence.
2. **`SYMBOLIC_INERT`** — the verdict is flat in `w` across the reported range.
   **This is a publishable negative result and is reported as one.** The
   symbolic term is still retained, for the reason already registered in §S3.5:
   the Reflector *requires* a component that can name which rule failed, and the
   LaBSE probe cannot. Retained for interpretability, not for accuracy.
3. **`SYMBOLIC_HARMS`** — the held-out test rejects the symbolic term, as
   `barata2026hybrid` rejected a cheap component in 50 of 50 folds. Reported,
   and the consequence for RQ3 stated plainly rather than softened.

⚠️ **Outcome 2 is the one to expect**, and saying so now is the point of saying
it here: Verifier-A scores **1 error on 82 items**, so on *human* text every
weight returns the same verdict. Whether generated text behaves the same way is
exactly what is unknown — `kapur2026length` show the length/specificity relation
is flat or reversed in machine text — and it is why the fit moved off dev-82 in
the first place.

### Registered decision 2 — τ is fitted **hierarchically across the two axis levels**, not pooled and not split

**The question.** §4.2 says *"a τ per axis level"*. Under K = 2 (decision 7) that
is two τ values fitted on 30 dev-plots each, while decision 19's τ\* argmax is
written for a single frontier. The two readings were put to Sabbir, who
delegated: *"research kore dekho konta vlo hoy."*

**⚠️ Provenance: the choice and reasoning below are Claude's, endorsed not
authored — as for decisions 12, 14, 16 and 19.**

**What the search returned, and it moved the answer off both options.** The
2026 literature on group-conditional thresholds is close to one-directional:
`2605.14260` (*On the Burden of Achieving Fairness in Conformal Prediction*)
states that a single pooled threshold *"can hide cross-group heterogeneity in
score distributions and distort group-wise coverage"* — our exact configuration,
two levels whose generated-score distributions we have no basis to assume match.
`2605.05562` makes the same point in its title: *marginal validity is not enough
for subgroup reliability*. `2606.29403` and `2606.20115` independently reproduce
pooled calibration masking subgroup undercoverage. **So a single global τ is not
the conservative choice it appears to be.** But `2605.14260`'s own title names
the counterweight — group-conditional thresholds cost calibration sample — and at
30 dev-plots per level we have very little to spend.

**The registered procedure**, following `2607.24562` (*Hierarchical
Group-Conditional Conformal Risk Control*): τ is estimated by **partial pooling
across the two levels**, with the shrinkage **estimated from the ratio of
within-level to between-level score variance, not chosen**. This matters for the
standing rule — a hand-picked pooling weight would be exactly the constant
`check_constants.py` exists to catch, whereas an estimated one has a criterion.
The estimator degrades to the global τ when the levels are indistinguishable and
to per-level τ when they are strongly separated, which is precisely the
behaviour we cannot predict in advance and therefore should not hard-code.

**Reported alongside, always, and not as an afterthought:** the **global τ** and
the **two per-level τ** as the limiting cases the estimator interpolates between,
plus a **two-sample permutation test** on the per-level generated-score
distributions (**5,000 shuffles, α = 0.05** — the same instrument and the same
constants already pre-registered in §RQ1-F Gate 2, adopted rather than reinvented).

🔑 **The permutation test is DESCRIPTIVE and is not a gate.** At 30 generations
per level it is underpowered, and a gate whose null verdict is the likely one
regardless of the truth is the failure RQ1-F's Gate 2 had to be rewritten
mid-protocol to escape. **A non-significant result means *not detected*, never
*equal*, and must be written that way.** This is why the hierarchical estimator
is the default rather than the consequence of a test: it needs no gate to be
correct.

**Decision 19 is unaffected.** τ\* = argmax [quality(τ) − α_lo] / E[calls](τ)
still names one point on one frontier; the hierarchical fit determines *which* τ
each level is held to, not how the operating point is chosen. `quality(τ)`,
α_lo and α_hi remain measured by **Verifier-B, never Verifier-A**.

### Registered decision 3 — the 20-generation generator pilot, with `TIE` as the pre-committed default

§4.4 specifies a **20-generation pilot** on Groq to choose between Llama and
Qwen. **As written it is a budget with no decision rule**, which is the same
defect class as the struck `0.6/0.4` and the struck *"first-pass 60–70%"*.
The rule is fixed here, before the first generation.

- **Design:** 20 generations = **10 dev-plots × 2 axis levels**, one draft each,
  seed logged; temp **0.8**, top_p **0.9** (§4.2, not chosen here). Both models
  see byte-identical prompts.
- **Scored by:** *not* Verifier-A. Verifier-A is the in-loop judge, and
  pre-selecting the generator against it is a soft form of the co-adaptation
  `wang2026hacking` name and rule 6 exists to prevent.
- **Pre-committed default outcome: `TIE`.** The tie-break is fixed in advance
  and is a **declared non-performance rule**, exactly as S3.2's was: on tie,
  take the model with the lower cost and higher rate limit, and **state in the
  thesis that the data did not choose**.
- **Banner: `NOT A RESULT`**, in the style of `results/pilot_s35_idf.*`. No
  Llama-vs-Qwen claim may be quoted from this file.

**Why `TIE` is registered as the expected outcome rather than discovered as a
disappointment.** `2605.10405` (*Valid Best-Model Identification for LLM
Evaluation*) treats best-model selection under a small evaluation budget as a
statistical problem with a known failure mode, not a matter of inspection; and
our own S3.2 returned `TIE` across **seven arms × five seeds**, with a
between-arm spread smaller than one arm's own seed SD. **Expecting 20
generations to separate two models, when 70 runs could not separate seven, is
not defensible.** Registering the tie-break now is what stops the pilot
collapsing into "read 20 outputs and pick the nicer ones", which is a preference,
not a reason.

⚠️ **Model identity is deliberately left blank here.** The exact Groq model IDs
are written into `configs/s4_pilot.yaml` with a retrieval date, from the live
catalogue — **not from memory.** A model string recalled from training data is a
constant with no source, and catalogues churn.

**Bangla generation quality is a live risk and gets its own citation trail
rather than an assumption:** `2605.31483` (BenHalluEval) is the first systematic
Bengali hallucination evaluation of LLMs, and `2605.22487` documents honorific
failures in multilingual Bangla generation — register and honorifics being part
of the very construct the axis measures. Neither is briefed to
`base_papers_brief.md` depth; **abstracts only, and that is stated.**

### Registered decision 4 — the Researcher's retry contract

§4.2's anchoring rule is adopted unchanged and made checkable: on retry the
original persona+plot query **stays anchored**; feedback keywords **augment,
never replace**. A test must fail if the retry query does not contain the
original query as a subsequence.

**Exemplar overlap per attempt is logged**, and §4.2's own trigger is
pre-committed rather than left to judgement: **overlap < 50% with no pass-rate
gain → re-retrieval is disabled and retries route straight to the Writer**, which
becomes the §5.1b routing ablation. The 50% is §4.2's, not a new constant.

### Loop control and `gave_up`

FAIL & attempt < 3 → Researcher (anchored + augmented). FAIL & attempt = 3 →
emit **best-of-3 by hybrid** with `gave_up = True`. **Every metric in Phases 4–5
is reported split by `gave_up` status** (§4.2). The three-attempt cap is §4.2's
and is itself a claim to be earned in §4.6 by the per-iteration curves, not
assumed — `madaan2023selfrefine` report diminishing returns by iteration 3.

### Registered decision 5 — prompt parity is enforced **by construction**, not by inspection (open decision 10, closed)

**The threat.** §5.1 row 1 (zero-shot, 1 call) *is* α_lo, the lower endpoint of
decision 19's τ objective. If row 1's prompt states the axis-level requirement
less fully than the loop's does, then the loop's measured "gain" is partly the
difference between two prompts, and **every number in RQ2 inherits the
artefact** — including τ\*, because α_lo sits inside it.

**⚠️ Provenance: Sabbir delegated — *"research kore dekho konta valo hoy erpor
koro."* The choice and reasoning are Claude's, endorsed not authored.**

**Registered:** row 1's prompt and the loop's attempt-1 Writer prompt are
**emitted by the same template function**, with row 1 being
`render_prompt(exemplars=[], feedback=None)`. They therefore differ in exactly
two things — retrieved exemplars and Reflector feedback — and **cannot** differ
in how fully the axis-level requirement is stated, because that text has one
source. A test asserts that removing exemplars and feedback from the loop's
attempt-1 prompt yields row 1's prompt **byte-for-byte**.

🔑 **Why by construction rather than by audit.** Huang et al. §5 document a
reported self-correction gain that was really a more informative second prompt
(81.8 standard vs 75.1 self-corrected once the requirement was stated up front).
An audit catches that if someone remembers to look; a shared template makes the
divergence unrepresentable. **The literature says the artefact is the normal
case, not the exceptional one**, so the defence should not depend on vigilance.

**What the search returned, and it also narrows what the loop may claim.**
`2606.23196` (*When Does Intrinsic Self-Correction Help?*) and `2606.13156`
(*the Self-Correction Mirage*) both report that the reliability of
self-correction gains is contested. 🎁 **Both are scoped to *intrinsic*
self-correction — a model revisiting its own answer *without external
feedback*.** Ours is extrinsic by construction: a **trained external verifier**
plus a role-separated Critic that is not the Writer's model. **So the bulk of
the "self-correction does not work" literature does not refute this design; it
describes the design this one was built to avoid, and the thesis should say so
in exactly those terms rather than ignoring the literature or over-claiming
against it.** ⚠️ **The prompt-parity threat, however, is *not* scoped to
intrinsic SC** — it is a measurement artefact that applies to any loop compared
against a single-call baseline, which is why it is closed structurally here.
`2604.22273` (*Self-Correction as Feedback Control*) additionally frames repeated
refinement as having **stability thresholds** past which it degrades — relevant
to §4.6's claim that max-retry = 3 must be *earned* by the per-iteration curves
rather than assumed.

### Registered decision 6 — the §4.6 failure taxonomy is **seeded, extensible, and honest about which categories were post hoc**

§4.6 fixes four categories for the hand-coded taxonomy of 50 three-time
failures: *wrong sentiment / too short / off-topic / template repeat*. **There
is no register or honorific category**, and `axiv2605_22487_banglahonorific`
documents exactly that failure mode in multilingual Bangla generation — on a
dimension the engagement-specificity axis partly *is* (S2b's register probe
separated the corpora on first-person pronouns, exclamation and comma-runs).

**⚠️ Provenance: as decision 5 — delegated, Claude's reasoning.**

**Registered:**

1. **Seed categories** = §4.6's four, **plus `register_or_honorific`**, plus an
   explicit **`other`** bucket.
2. **The `other` rate is reported as a number**, always. No threshold is
   attached to it — a cutoff here would be a constant with no criterion, which
   is the defect this project spent 2026-08-11 removing. The number is
   evidence about the taxonomy's adequacy and is left to speak.
3. **Any category added after seeing the failures is labelled `post hoc` in the
   paper**, by name. Adding categories is legitimate and expected; doing it
   silently is what turns a taxonomy into a story.
4. **Double-coding and an agreement figure are required** — a single coder's
   taxonomy is one person's reading. 🔴 **Who codes is Sabbir's to decide and is
   NOT assumed here**: G-300's annotator time is recorded as exhausted, and
   Claude must not be the sole coder of failures produced by a system Claude
   built. This is flagged as an open resource question, not silently resolved.

**What the search supports.** `2604.18490` (*LQM*) argues that MQM and other
established schemes are **language-agnostic and therefore miss language-specific
phenomena** — which is the general form of our missing register category, and
the citation for adding one rather than inheriting a generic list.
`2606.10765` (*ArabiGEE*) is precedent for a **language-specific hierarchical
error taxonomy** in a non-English language. `2608.03966` notes that existing
resources in a comparable setting *"often assign a binary label"*, supporting a
fine-grained scheme over a pass/fail one. ⚠️ **All three are abstracts only.**

### What is NOT registered here, and is left open on purpose

- **`w`, τ and τ\* have no values.** They cannot until generations exist.
- **`enable_f1` stays `false`.** The rule-7 amendment packet is unsigned
  (`docs/rule7_amendment_packet.md`); the structural guard in `s35_scorer.py`
  stays in place. Flipping it is not a Phase 4 act.
- **Title wording** (open decision 12) is Sabbir's. Phase 4 code and configs use
  *axis / level / the cut* throughout and never *persona* or bare *cluster*.
- **Decisions 9, 10 and 11** (cost-matched baseline, prompt parity, external-role
  self-critique row 7b) block **Phase 5**, not Phase 4 — but decision 10 in
  particular constrains the §5.1 row-1 prompt that becomes α_lo, so it is flagged
  here as due before the τ sweep is interpreted, not before the loop is built.

## Deviations log
Any departure from this document is recorded here with date, reason, and commit.

| Date | Section | Change | Reason |
|---|---|---|---|
| 2026-08-11 | S3.3 — **Verifier-B's learning rate is fixed at 2e-5 and never selected** | S3.2's recipe sweeps `lr ∈ {2e-5, 3e-5}`. Verifier-B runs **5 seeds at 2e-5 only**, the pipeline §3.1 default. Half the compute, and no hyperparameter is chosen by looking at a score. | **Searched before deciding** (alphaXiv; Consensus quota exhausted until 1 Sep). `schneider2025overtuning` re-analyse seven HPO benchmark suites and find **~10% of runs select a configuration that generalises worse than the default** — and their mixed models name the aggravating conditions as **small data, holdout rather than CV, binary classification, accuracy-type metric**. Verifier-B is all four: 888 rows, an 82-row holdout, two classes, macro-F1. Their recommendation is repeated CV; **not tuning at all is strictly stronger and was available**, so it was taken. Cost accepted and named: B may be a little weaker than a tuned B. **Sabbir's call, 2026-08-11**, from three options presented with their costs. |
| 2026-08-11 | S3.3 — **the `dev` contract is widened from "threshold sweep only" to "threshold sweep and verifier evaluation"** | `split_map_v1.json`'s `_contract` restricts `dev` to the threshold sweep. Both verifiers are now evaluated on it. `src/verifier/split_access.py` previously returned `dev = None` for role B, so **Verifier-B had no registered evaluation slice at all** — the gap this row closes. | **Leakage-free by construction, not by promise:** `dev` ⊂ R1 and is held out of A's 804; `dev` ∩ R2 = ∅ by the frozen split's contract, so it is untouched by B's 888. Neither verifier has seen any of the 82 rows, and S3.2/S3.2b already used dev-82 as their evaluation set. **The reason it must be the *same* slice is RQ5:** the Goodhart test measures the A−B gap, and measuring A and B on different items confounds model difference with item difference irrecoverably. ⚠️ **Pre-committed limit:** at 1 item = 0.0122 macro-F1 and an expected A−B gap of ~1.8 items, **no claim that either verifier is better may be made from dev-82.** Sabbir's call, 2026-08-11. |
| 2026-08-11 | 🔴 S3.2c / decision 16 — **the "natively calibrated" justification for Verifier-A is WITHDRAWN; §3.4 temperature scaling becomes mandatory for A** | Decision 16 defended the frozen LaBSE probe as *"best measured, seconds to fit, **natively calibrated**, no GPU in the loop."* The calibration clause is struck. The **choice of Verifier-A is unchanged**; one sentence of its defence is not. | **Written from memory one day earlier, and refuted by the first search that looked.** `zhang2026tabpfn` evaluate nine heads on frozen encoders across **22,820 episodes**: logistic regression takes the **best mean rank on accuracy** and ranks **below kNN and every in-context head on both ECE and NLL** — Top-1 ECE **0.069** vs kNN 0.037 and TabPFN 0.031, NLL 0.581, second worst of ten. Their words: *"strong accuracy does not inherently guarantee well-calibrated probabilities."* **What survives:** the same paper's guidance keeps LR appropriate at *"extremely low shot counts, high dimensions, or near-ceiling tasks"* — ours is 768-d and 0.9866, i.e. two of three. ⚠️ **Bounded honestly:** their grid is 10-class and they note the gap narrows at C = 2, so the correction recorded is *"the claim had no support"*, **not** *"Verifier-A is miscalibrated"*; our own ECE settles that. **This is the fourth entry in CLAUDE.md's search-first table**, and the cheapest — no code depended on the sentence yet. |
| 2026-07-27 | S0 arithmetic | `null_rows` 1 → 2; `usable_n` 4722 → `n_after_rule_based_cleaning` = 4730 | Two distinct null rows exist (one missing review text, one missing sentiment label), not one. 4722 was produced by treating the three drop sets as disjoint (2+72+204=278 subtracted from 5000), which double-counts the 10 rows in SHORT ∩ DUP. True union under normalized duplicates = 270, giving 4730. **Final `usable_n` pending near-duplicate removal** (cosine ≥ 0.95, deferred to S2). Verified in `results/s0_data_xray.md`. |
| 2026-07-28 | RQ1 trap-check bands | ARI bands changed from 0.4 / 0.4–0.6 / >0.6 to **DEGENERATE / <0.20 / 0.20–0.60 / >0.60**; old bullet struck through and marked superseded | Written **before any ARI value existed** (S2 has never been run), so this is a pre-registration refinement, not a post-hoc adjustment. Three substantive additions: a degeneracy band (a non-partition scores low ARI by construction and must not be read as independence); a mandatory residual test in the middle band; and the venue/community selection effect named as an untestable alternative explanation in the top band, following provenance fact (c). ⚠️ `configs/s2_pilot.yaml` and `src/cluster/s2_pilot.py` still implement the OLD 0.4/0.6 bands — they must be updated before the pilot is run or its printed verdict will contradict this pre-registration. |
| 2026-07-28 | RQ1 code/protocol alignment | Code-vs-protocol mismatch **found and closed before the first run**: `configs/s2_pilot.yaml` and `verdict()` in `src/cluster/s2_pilot.py` still implemented the superseded 0.4/0.6 bands and derived the verdict from ARI alone | **No ARI value was ever produced under the old scheme** — the S2 pilot had not been run at any point while the mismatch existed, so nothing was observed, reported, or interpreted under the retired bands. Closure: config now carries the four-band scheme; `verdict()` evaluates **degeneracy as the first gate**, returning `NO_CLAIM` and emitting no PASS/CAVEAT/FAIL when the partition is degenerate, so ARI can no longer be read as independence when K-Means simply failed to partition; Band 2 emits a `RESIDUAL_TEST_REQUIRED` marker; verdict strings map one-to-one onto the protocol band names. Pinned by `tests/test_s2_verdict.py` (8 tests), including one asserting a degenerate partition with near-zero ARI returns `NO_CLAIM` and never a claim verdict. |
| 2026-07-28 | RQ1 / provenance | Log-odds probe registered as a **REQUIRED** falsification test of provenance fact (c) | Fact (c) ("no keyword or query-seeded search") is recall-based with no written collection log. It is testable against the corpus, so leaving it untested would be a choice to prefer an uncheckable claim. Both outcomes pre-committed. |
| 2026-07-30 | RQ1 / provenance — **register probe registered as EXPLORATORY** | New analysis added after the S2 result was seen: `src/preprocess/s2b_register_probe.py`, `configs/s2b_register_probe.yaml` → `results/s2b_register_probe.md`. It measures whether `Sentiment == 2` differs from classes 0 and 1 on **orthographic and structural features only** (punctuation, length, pronouns) — features that cannot encode an opinion about a film. | **The hypothesis came from reading the data, so this is exploratory and is labelled as such everywhere it appears. It is not, and may not be reported as, a confirmatory test.** It was run because S2's own crosstab pointed at it: refolded as *cluster 0 vs rest* × *class 2 vs rest*, φ = 0.565, **stronger than the clustering's association with sentiment overall** (V = 0.410), with only 12 of 1,572 class-2 items in cluster 0. Findings: class 2 is **100%** দাঁড়ি-terminated (others 58%/66%), **0%** first-person pronouns (expected 149), **0%** exclamation marks (expected 38), **0%** comma runs (expected 33), and draws **1,772** word types per 12,000 tokens against 3,577 / 3,303. This is the confound named in RQ1 Band 3 — clusters recovering the source rather than a persona — which `STATUS.md` had recorded as *untestable in principle* because venue was not retained. **That record was wrong in one specific way: venue was not retained, but writing style survives in the text and is measurable.** Nothing is trained (AUC is a rank statistic), so inviolable rule 10 is untouched. Consequence: the RQ1 persona claim is **suspended** pending `docs/provenance_query.md`. |
| 2026-07-30 | Provenance — **region split found; supersedes the s2b framing** | `src/preprocess/s2c_region_split.py` → `results/s2c_region_split.md`. The grouping variable is `raw_row`, not `Sentiment`. | The collector answered the s2b question with "collected the same way", so the raw `.xlsx` row order was examined directly (read-only; rule 1 intact). The label sequence has **10 runs in 5,000 rows** — the file was assembled in blocks — and the register signature tracks **position in the file, not label**: rows 3665–4330 are labelled 0 and sit at 99.8% দাঁড়ি / 0% first-person, while rows 499–896, also labelled 0, sit at 32% / 9%. Aggregated, rows 0–1998 (38.7% দাঁড়ি, 13.5% first-person, 255 types/1k) versus rows 1999–4999 (**99.2%, 0.8%, 128**), with a step transition over ~50 rows. **60% of the corpus is in the second region, across all three labels.** Consequences: (i) fact (reg) is superseded by fact (split) in STATUS — class 2 only looked special because all 1,670 neutral rows are nested inside region B; (ii) **every result over the full corpus is confounded, including the S2 trap-check**; (iii) provenance fact (c) cannot describe region B, and this document's pre-commitment that a computed test supersedes the recall-based provenance table is now operative; (iv) region A remains usable at 1,910 cleaned rows, organic, two classes. **Outstanding:** `ARI(cluster, region)` is the decisive number and cannot be computed until `s2_pilot.py` persists cluster assignments. Exploratory throughout. |
| 2026-08-01 | Split map — **stratified on `Sentiment × region`, not on cluster** | Pipeline §A specifies a *cluster*-stratified gold set. `data/splits/split_map_v1.json` is stratified on `Sentiment × region` (5 non-empty cells; region A holds no class-2 rows). G=300, R1=2,162, R2=2,163, dev=200, over the 4,625 rows surviving near-duplicate removal at the pre-registered t = 0.95. | The cluster instruction predates two findings. **(1)** The corpus is two corpora (`s2c_region_split.md`). **(2)** The full-corpus clustering is a **corpus detector** — 93.3% accuracy at identifying which of the two a review came from (`s2_pilot_ari_trapcheck.md`). Stratifying the gold set on that clustering would stratify it on a file seam. Additionally, **Gate G1 has not run**: the master K-table is outstanding, so any cluster-stratification now goes stale the moment K changes. `region` and `Sentiment` are both known, both stable, and both matter — region because it is the confound the design now controls for, Sentiment because it is the label. Verified: every part matches the corpus on both variables to within 0.1pp, zero overlap between any two parts, union covers the input exactly. Pinned permanently by `tests/test_split_map.py`. **The persona-stratification question moves to the annotation stage, where the scheme will actually be settled.** |
| 2026-07-31 | Plot corpus — **target reduced from 130 to whatever the source yields.** ⟶ **FINAL: 120 = 30 dev + 90 eval**, frozen the same day. (The estimate below said ~124/94; human review then removed 4 more — BN024 production history, BN042 the director's fatal accident, BN068 commentary about a story rather than the story, BN113 a 3-sentence fragment that sets up and stops. All four had passed every mechanical gate.) | The pipeline's §1.1.7 asks for 130 = 30 dev + 100 eval. bn.wikipedia does not contain 130 Bangla-film articles with a usable plot section. Four harvests: 67 → 110 → 132 → **124**, the last figure lower because a person-article veto removed 8 rows that had been counted as usable — actors' and directors' biographies swept in by the film categories. `N_DEV` stays at **30** (the dev slice tunes the loop threshold and 30 is the smallest defensible size); **eval takes the remainder**, with a hard floor of 80 below which the tool refuses to split. | **Two ways to reach 130 existed and both were refused.** (1) Relax the quality gate to admit two-sentence plots — but it was rejecting only ~20 of 3,135, so it is not the constraint, and thin plots are poor generation inputs. (2) Add the by-year categories, the largest available (২০১৯-এর = 268, ২০২২-এর = 220, ...) — but they are **language-neutral**: Tamil, Hindi, British and Japanese films sit in them, their bn.wikipedia articles are in Bangla, and they would therefore pass every gate in the harvester while quietly making the plot corpus stop being *Bangla cinema*. No check in the pipeline would have caught it. **Losing six eval plots costs a little power in a bootstrap CI; padding the set costs validity, which no n buys back.** 130 was a design choice in the spec, not a statistical requirement, and this is recorded before the number is used rather than after it is convenient. |
| 2026-08-03 | RQ1-D — **K=2 profile registered as EXPLORATORY IN ORIGIN, pre-registered in interpretation** | New analysis added after G1's table was seen: `src/cluster/s2e_profile.py`, `configs/s2e_profile.yaml` → `results/s2e_regionA_k2_profile.md` (+ assignments, features and log-odds CSVs). Section "RQ1-D pre-commitment" added above, **before the script existed**. | Two gaps in G1, both closed here. **(1)** G1 selected K = 2 and never persisted the labels; G-300 stratification needs them, and they cannot be recovered from `s2d_ktable_regionA.csv`. **(2)** G1 never asked what separates the halves. That question is decisive *before* annotation, not after: G1 reports PS 0.860 and bootstrap ARI 0.940 (a reproducible cut) alongside silhouette 0.053, a monotonically rising gap statistic satisfied at no K, and **HDBSCAN calling 100% of points noise** (no separated groups). A reproducible bisection of a continuum is what K-Means yields when it cuts along the dominant direction of variation — and with ~8-word reviews on L2-normalised LaBSE, **length** is the obvious candidate. If a word count reproduces the encoder's cut, spending 300 annotations on it would buy an expensive confirmation of a ruler. The **decision to profile is post-hoc and is labelled as such in the report itself**; what was fixed in advance is what each `length_auc` band would be taken to mean, including the pre-committed refusal to run G-300 on a `LENGTH_DOMINATED` partition. Guarded in code: `s2e_profile.py` re-derives G1's silhouette and ARI and **aborts** if they differ by more than 1e-6, so it cannot profile a K = 2 solution other than the one G1 selected; `tests/test_s2e_profile.py` (11 tests) additionally fails if the two configs' embedding or K-Means blocks ever diverge. Nothing is trained (AUC and Cliff's delta are rank statistics, the Dirichlet prior is fixed) — rule 10 untouched; whitespace tokens only, no stemming, stopword removal or TF-IDF — rule 7 untouched. New method citation: `monroe2008fightinwords`. |
| 2026-08-03 | RQ1-E — **residual test run VOLUNTARILY at Band 1** | New analysis: `src/cluster/s2f_residual.py`, `configs/s2f_residual.yaml` → `results/s2f_regionA_k2_residual.md` + `_cells.csv`. Section "RQ1-E pre-commitment" added above, before the script existed. **No band assignment is revised**: ARI(cluster, Sentiment) = 0.1522 remains Band 1 and the corpus does not move into Band 2. | Band 2 makes a residual test mandatory at ARI ≥ 0.20 and we are below it, so nothing was owed. Run anyway because **ARI is the wrong instrument for this association and this project has already been misled by that gap once** — `s2b_register_probe.md` recorded φ 0.565 against V 0.410. The same 2×2 that yields ARI 0.1522 yields **φ = 0.3981**, χ² = 300.7, and cluster→sentiment accuracy 69.5% against a 50.2% baseline; all 12 reviews nearest cluster 0's centre are positive and all 12 nearest cluster 1's are negative. Skipping on a technicality would leave a question a reviewer will certainly ask, answerable from data already on disk. **Results:** A min AUC 0.6115 (length independent of sentiment), B min \|φ\| 0.3133 (sentiment independent of length in every band), **C lift +9.80 pp → `RESIDUAL_SURVIVES`** — but **0.2 pp from the 10.0 cutoff**, and the script emits an automatic boundary-warning box at ≤2 pp so the weakness cannot depend on anyone remembering it. D: the richness inversion holds in **all four** length bands. Decomposition (added after the first run, before any interpretation was written): Sentiment alone +9.28 pp, length alone +5.22 pp, both +9.80 — so **length adds only 0.53 pp once sentiment is known**, and S2e's `LENGTH_CONFOUNDED` overstates length's independent contribution. Test C is a **resubstitution** estimate and therefore an upper bound; the bias direction was chosen deliberately, since it makes the persona-killing verdict easier to reach. Nothing trained (rule 10); whitespace tokens only (rule 7). Pinned by `tests/test_s2f_residual.py` (9 tests), including one that fails if the 10.0 cutoff or the quartile count moves, because either would flip the published verdict. |
| 2026-08-03 | RQ1-F — **G-300 registered; 3 annotators → 2; author-as-annotator flagged** | New: `configs/g300.yaml`, `src/annotate/g300_build.py`, `g300_score.py`, `docs/g300_annotation_guideline.md`, `tests/test_g300.py` (18). Section "RQ1-F pre-commitment" added **before any item was annotated**. | Three departures from RQ1 as written, all forced and all recorded rather than absorbed. **(1) n = 2 annotators, not 3.** With two there is no majority, so the adjudication rule is fixed in advance: **disagreements are not resolved** — the gold value is the mean and the disagreement rate is reported, because adjudicating after seeing the data is how an IAA figure gets laundered. **(2) One available annotator is the author.** Recommendation on record: *Sabbir should not annotate* — he designed the study and has read the log-odds lists and the cluster-representative reviews. If he does anyway, no claim of *independent* human validation may be made, only *partially independent*, and it goes in the abstract's limitations and the dataset card, not a footnote. **(3) Only 123 of the frozen G-300 are in region A** and carry a K=2 label, because the split was stratified on `Sentiment × region` in August, before G1 chose K. The split map is **frozen (rule 3) and was not regenerated**; all 300 are annotated and Gate 2 runs on the 123, with its reduced power reported as a number. Task design: annotators rate **engagement specificity** on a 0–3 ordinal scale and **never see cluster, K, region, Sentiment, word count or `review_id`** — `review_id` is ordered by position in the source file, and position *is* the region variable. They are not asked "which persona is this?", which would make their agreement a measure of how well we wrote the cluster descriptions. RQ1-D's binding condition is enforced twice: worked counter-examples in the guideline (`bn_0360`, 12 words → 1; `bn_0252`, 4 words → 2, both from `dev`) **and** a per-length-band AUC in the scorer, because instruction is not enforcement. |
| 2026-08-03 | RQ1-F Gate 2 — **decision rule changed from a bootstrap CI to a permutation test, before any annotation** | Gate 2 previously fired `NEGATIVE` when the bootstrap 95% CI included 0.50. It now uses a permutation null (5,000 shuffles of cluster membership, α = 0.05); the CI is still reported, for precision only. | **The old rule was broken in the direction that matters most.** `directionless_auc` is `max(a, 1−a)`, so every bootstrap resample is bounded below by 0.50 and the lower bound essentially never reaches it — the `NEGATIVE` verdict was close to unreachable, making the single number that decides RQ1 biased toward finding an effect. Demonstrated rather than asserted: under chance at n = 123 the null's own 95th percentile sits at ≈ **0.60**, not 0.50, so any rule treating 0.50 as the null value is wrong. Found by the scorer's own smoke test. **Nothing had been observed when this changed** — no sheet filled, no α, no AUC — so this is a pre-registration refinement of the same kind as the 2026-07-28 band revision, not a post-hoc adjustment. `tests/test_g300.py::test_the_negative_verdict_is_actually_reachable` now fails if the null verdict ever becomes unreachable again, and `::test_permutation_null_sits_well_above_half_at_this_n` pins the reason. |
| 2026-08-05 | RQ1-F outcome — **G-300 round 1 returns `UNRELIABLE`; recorded as INCONCLUSIVE (instrument failure), NOT as a negative result** | α(ordinal) = **0.4970** < 0.667, so the pre-registered rule fires and **Gate 2 was not computed**. That verdict stands and is not revised. What is added here is the diagnosis, because "α < 0.667" and "humans cannot make this distinction" are different claims and only the first is established. | **The annotators agreed strongly**: exact agreement **75.5%**, within-1 **98.7%**, **Gwet's AC1 = 0.871**. α is low because the *scale* collapsed, not because the raters diverged — **68% of A's and 76% of B's ratings are the single value "2"**, so there is almost no variance for agreement to be measured against. This is the kappa/κ paradox, and `related_work.md` had already listed `gwet2008ac1` as the guard for exactly it. **Cause, and it is mine to own: the calibration advice was bad.** Round 1 calibration showed annotator A compressed onto "1" (12 of 20), and Claude's fix was *"if the review names an aspect, at least 2"* — but nearly every review names something, so both annotators moved almost everything to 2, and the **2-vs-3 boundary was never given equal attention**. One problem was traded for a worse one. **A rescue was attempted and failed, and is reported rather than omitted:** recast as binary at the only boundary with real spread (3 vs ≤2) gives κ = **0.5285**, still below 0.667. No post-hoc recoding saves it. **Consequence:** RQ1 is reported as **inconclusive on human validation**, with the failure attributed to the instrument and its cause named. Writing "negative result" would assert that people do not make this distinction, which this data does not show. **No second round:** annotator time is exhausted and none is available, so the repaired-rubric option was closed by circumstance rather than chosen — recorded so nobody reads the absence of round 2 as a judgement that round 1 sufficed. |
| 2026-08-05 | RQ2–RQ5 — **decoupled from RQ1's outcome** | The generation and verifier experiments condition on `cluster_k2` as a **controlled label**, and no longer depend on that label having been validated as a persona. | RQ2 asks whether an external trained verifier improves adherence to a **target label**. That question needs the label to be well-defined and reproducible, not to be a validated audience type — and K = 2 is well-defined and reproducible (PS 0.860, bootstrap ARI 0.940 ± 0.029). Making this explicit costs nothing and prevents an inconclusive RQ1 from being read as invalidating the thesis's actual contribution. **The price is terminological and is paid in full:** the word *persona* may no longer describe the K = 2 halves anywhere. They are **clusters**, and generation is **cluster-controlled**, not persona-controlled. This closes STATUS decision 12 by force — including for the title. |
| 2026-08-08 | Phase 3 — **the dual-accuracy table is not producible; Phase 3 measures label reproduction only** | Pipeline §3.3 requires two numbers per verifier: weak-label accuracy (~87% expected) and **"true persona detection accuracy" on the human gold-300** (65–75% expected), calling the gap between them "an honest, citable contribution". **The second number cannot be computed.** §3.2's backbone-ablation criterion depends on the same number and is affected identically. | Three independent reasons, any one of which is sufficient. **(1)** G-300 produced **0–3 specificity ratings, not cluster labels** — there is nothing to compute an accuracy *against*. **(2)** Those ratings came back **unreliable** (α 0.4970; step 5k), and Gate 2 was not computed, so even a derived binary would rest on an instrument that failed its own reliability gate. **(3)** Only **123 of the 300** gold items are region A and carry a `cluster_k2` label at all. **Consequence, stated rather than absorbed:** Phase 3 reports **label-reproduction accuracy only**, and the thesis says in those words that **no human-validated accuracy exists for the verifier**. The backbone winner in §3.2 is therefore selected on weak-label macro-F1 alone — *reproduction*, not validity — and that selection is disclosed as such wherever the backbone choice is defended. This is consistent with the RQ2–RQ5 decoupling logged above: RQ2 needs a verifier that enforces a **well-defined reproducible label**, and label-reproduction accuracy is exactly the right measurement for that claim. It is **not** the measurement §3.3 wanted, and the difference is not papered over. |
| 2026-08-08 | Phase 3 — **§3.1's "2-fold swap" superseded by the frozen split; n stated in advance** | §3.1 asks for Verifier-A and Verifier-B to be separated by "different seeds + disjoint train splits (2-fold swap)". Replaced by the frozen split map, which already guarantees disjointness by contract: **Verifier-A ← R1, Verifier-B ← R2**, and G is eval-only. | The split map postdates §3.1 and is the stronger mechanism — disjointness is committed to git and pinned by `tests/test_split_map.py`, rather than depending on a swap being performed correctly at training time. **The usable n is smaller than §3.1 assumed and is recorded now, before any result exists, so a weak number later cannot be blamed on the method:** Verifier-A trains on **804** labelled rows (R1 minus the 82 labelled dev rows; 481/323 across the two clusters), Verifier-B on **888** (531/357), dev tuning has **82** (53/29), and G-300 has **123**. All are region A only, per the scope decision. Binary task, ~40% minority. **Two obligations follow.** Fine-tuning BanglaBERT on 804 rows of ~8-word text is high-variance, so every verifier number is reported as **mean ± SD over ≥3 seeds**, never as a single run. And §3.5's symbolic scorer learns its weights on the dev slice, which is **82 rows, not the 200 the spec assumes** — logistic regression over ~7 features at n=82 is fitted, reported with its n, and treated as the fragile component it is. |
| 2026-07-30 | Provenance — `git_hash()` semantics | `-dirty` now reflects **tracked** modifications only (`git status --porcelain -uno`); untracked files are counted separately in `stamp()` as `untracked_files` | The suffix previously came from bare `--porcelain`, which also lists untracked files. Every run creates untracked artifacts — its own outputs, caches, a copied input — so every stamp came out `-dirty` and the flag stopped distinguishing anything; the one case it exists to catch (a result produced from edited but uncommitted source) had become invisible. This is why `results/s2_pilot_ari_trapcheck.md` carries `e3d8e434…-dirty` despite being produced from a **fresh `--depth 1` clone**, in which no tracked file *can* have been modified. The S2 result is therefore attributable to a pristine `e3d8e43`. Untracked files are reported, not ignored — a source file that was never committed is a real provenance gap. |
| 2026-07-27 | S1 class balance | Post-cleaning class balance is no longer uniform; the R1/R2 split will be sentiment-stratified | Raw 1665/1664/1670 becomes 1513/1599/1618 after S1. Drops concentrate in class 0 (152 of 270 total; 152 of the 269 labelled drops), because duplicates and sub-3-word reviews are over-represented in the negative class. Stratifying the R1/R2 split on `Sentiment` keeps the shifted distribution identical across partitions instead of letting it drift further. Counts in `results/s1_cleaning_log.json` and `docs/dataset_card.md`. |
| 2026-08-08 | S3.2 — **seed count 3 → 5, and seed variance is no longer the decision rule** | The 2026-08-08 Phase 3 entry above committed to "mean ± SD over ≥ 3 seeds". Both halves are amended: **5 seeds**, and the backbone winner is decided by a **paired bootstrap significance test** (10,000 resamples, BH-corrected over 21 pairs), with seed variance reported as sensitivity only. | **The literature contradicted our own protocol, and it was found by searching rather than by a reviewer.** Bethard (2022) surveys 85 ACL Anthology papers and names *"varying only the random seed to create score distributions for performance comparison"* as a **risky** use of seeds — which is precisely what "pick the arm with the best mean ± SD" is — while listing sensitivity measurement as a **safe** use. Gundersen et al. (2023) show small effect sizes plus few repetitions readily yield wrong conclusions; Casola et al. (2022) find only 20% of transformer papers report multiple runs and document low seed robustness; Fu et al. (2023) supply the stability bound. Precedent for the replacement rule exists in-language: Hasan et al. (2025) settle BanglaBERT vs mBERT vs XLM-R on Bangla with a paired bootstrap test. ⬛ **Considered and rejected:** Xue et al. (2023) recommend blocked 3×2 cross-validation over repeated standard splits on SNR grounds. Rejected by Sabbir on 2026-08-08: it re-draws the train/dev boundary inside R1, and **the frozen split map is the thesis's strongest reproducibility claim** -- committed to git, pinned by `tests/test_split_map.py`, never regenerated -- which is not worth disturbing for a statistical improvement. (Wording drafted by Claude and confirmed by Sabbir; endorsed, not authored -- see the lab-notebook entry of the same date.) Recorded here so the rejection is visible rather than absent. |
| 2026-08-08 | S3.2 — **three arms added to the backbone ablation (4 → 7)** | Added `IndicBERTv2`, **SetFit** (LaBSE body), and **BERT-NLI** transfer to pipeline §3.2's four backbones. Registered in §"S3.2 pre-commitment" before any download or run. | Two independent reasons. **(1) The four specified arms do not span the candidate space the recent literature identifies.** Mazumder et al. (2025) report IndicBERTv2 above both XLM-R and BanglaBERT on a Bangla style-classification task close in kind to ours. **(2) The specified arms are all full fine-tuning, which is the weakest regime at our n.** Laurer et al. (2023, *Political Analysis*) report BERT-NLI beating classical models by 10.7–18.3 pp at 100–2,500 training texts and performing *particularly well on imbalanced data* — 804 rows at ~40% minority is that case exactly. SetFit (Tunstall et al. 2022) is the cheap contrastive alternative built for this n. **SetFit is registered with a pre-stated expectation of losing**: Beliveau et al. (2024), the closest published setting (non-English, small, imbalanced, domain-specific), found BERT-like > SetFit > LLM. Registering the expected loser in advance is what makes either outcome informative. Cost: three extra arms at matched budget, no extra annotation. |
| 2026-08-08 | S3.4 — **calibration demoted from "hidden contribution" to descriptive** | Pipeline §3.4's reliability diagram keeps 10 bins and treats before/after ECE as a contribution. Amended: **5 bins, bootstrap CI, figure labelled descriptive**, and the pre-committed null statement *"calibration could not be established at this sample size"* if the ECE improvement is smaller than its own CI. Temperature scaling is kept and explicitly **not** upgraded to an adaptive method. | The dev slice is **82 rows** (recorded 2026-08-08, before any result). Ten bins gives ~8 samples per bin, so the ECE estimate is dominated by binning noise and a before/after delta on 82 rows cannot carry a claim. Keeping the *simple* calibrator is the literature's own recommendation at this n, not a concession: Balanya et al. (2022) show expressive calibrators fail under data scarcity while simple scaling stays robust, and Guo et al. (2025) attribute that failure to variance from insufficient validation data. **Consequence carried forward:** τ in §4.5 rests on this confidence, so τ is reported as a sensitivity curve rather than a point, and the existing Verifier-B sanity-check on the final τ becomes mandatory. |
| 2026-08-08 | S3.2 — **`transformers` pinned below 5 for the whole run; the five completed arms discarded and all seven re-run** | The first real run (Kaggle, T4, commit `a2986db`) completed five arms and died at arm 6 on `import setfit`: setfit's module chain imports `transformers.training_args.default_logdir`, removed in transformers 5.x, which is what Kaggle ships. `bert_nli` never ran. The environment is now pinned to `transformers<5` and **all seven arms are re-run under it**; the five completed numbers (banglabert 0.9700, xlmr 0.9508, muril 0.9616, mbert 0.9402, indicbertv2 0.9617) are **discarded, not carried forward**. | **The cheap fix — run the two remaining arms in a second environment and put all seven in one table — was considered and rejected on quantitative grounds.** Coakley et al. (2022) ran three experiments five times each across 13 hardware and 4 software environments (780 results) and measured **>6 pp of accuracy variation on identical deterministic examples from environment alone**; Shahriari et al. (2022) show framework major-version changes alter performance and that versions can be bug-polluted. **Our entire observed between-arm spread is 2.98 pp** (0.9402–0.9700) — smaller than the known environment effect. A mixed-environment table would therefore be measuring library version as much as backbone, and the comparison would be void. **Re-implementing SetFit locally to dodge the dependency was also rejected:** Liu et al. (2020, 2022) separate *reproducibility* (original artifacts) from *replicability* (re-implemented artifacts) and find re-implementations frequently fail to reproduce; a hand-written SetFit would license no claim about *SetFit*, which is the arm this protocol pre-registered. **Carried forward as a finding, not just a cost:** the between-arm spread being smaller than documented environment noise is itself evidence for the pre-registered `TIE`, and is reported beside the verdict. **Prevention:** `--check-arms` now imports every arm's dependencies on CPU in preflight, and the Kaggle runner calls it as Gate 0. Every dependency that failed was knowable in ten seconds; instead it was discovered after roughly four GPU-hours. |
| 2026-08-09 | S3.2 — **the learning rate stays selected on dev, and the selection question is settled empirically instead of by design** | The LR is chosen per arm by best mean on the 82-row dev set, and the arms are then compared on that same dev set — selection and evaluation share data. Rather than removing the sharing, the run now reports the verdict under **two aggregation rules from the same 70 runs**: (i) **headline** — each arm at its own best LR; (ii) **pooled** — element-wise majority vote over all 10 runs per arm, with no selection at all. **Pre-registered trigger: if the two verdicts disagree, S3.2 is re-run with inner k-fold tuning on the 804 training rows (dev untouched), and neither verdict may be reported until that is done.** | **Four alternatives were considered; the literature killed two of them and costed the third.** *(a) Fix one LR for all arms* — rejected: Wen et al. (2025) show blind hyperparameter transfer across methods is **unfair**, and Shehzad et al. (2023) demonstrate that untuned baselines let any method be reported as winning. *(b) Split dev in two* — rejected: 41 + 41 rows, and Grewe et al. (2026) show single small hold-outs are unstable enough that a rank-1 model drops to rank 7 under CV. *(c) Inner k-fold CV on the 804 training rows* — methodologically the best answer (Zhang et al. 2025 find 10-fold stable across all strategies at n = 595–5946, which brackets our 804; Dwarampudi et al. 2026 and Chen et al. 2025 both confirm that reusing folds for selection and evaluation inflates estimates). **Costed and deferred, not dismissed: ~91 run-equivalents against the current 70, i.e. ~30% MORE GPU, not less** — an earlier estimate in this project claimed it would be cheaper and that was wrong. It also imports a new caveat, since Teodorescu et al. (2025) find k-fold selection unreliable *across model classes*, and our seven arms span three. *(d) What is adopted.* The bias from shared selection pushes **every** arm in the same direction, so it distorts the **levels** far more than the **comparison** — and the levels only mattered for the "all arms near chance" outcome band, which the discarded 2026-08-09 run put out of reach at 0.94–0.97. The one risk that could genuinely manufacture a winner is **winner's-curse**: an arm whose two LRs are noisier gets a higher maximum for free. That risk is measurable from the runs we already have, at **zero extra GPU**, which is what the pooled rule does. **Agreement between the two rules settles the question with evidence rather than argument; disagreement buys the expensive design at the point where it is known to matter.** Limitation carried to Ch.5 regardless: the cross-model-class caveat (Teodorescu et al. 2025) applies to any comparison spanning fine-tuning, SetFit and NLI transfer. |
| 2026-08-09 | S3.2 — **every arm is pinned to ONE GPU; the 2026-08-09 run's hardware budget was not matched across arms** | `CUDA_VISIBLE_DEVICES=0` is now set at the top of the script, before any torch import, and the visible device count is recorded in the result file so a reader can confirm it. | **Found by reading the stalled run's log, not by design.** Kaggle's "GPU T4 x2" exposes two devices. The five fine-tuning arms use a plain `model.to(device)` loop and take one; SetFit detects two and silently switches itself to **DataParallel** (the log emits `sentence_transformers.base.training_args: Currently using DataParallel (DP)... DDP is recommended`). **The ablation was therefore comparing five arms on one GPU against one arm on two** — a compute budget that varies by arm, which is the same unequal-budget failure Wen et al. (2025) describe for hyperparameters, relocated to hardware. An ablation that silently varies compute is partly measuring compute. Pinning to one device also removes DataParallel itself, which HuggingFace's own documentation describes as leaving GPU 0 doing most of the work while the others idle, and against which sentence-transformers carries open hang reports (UKPLab/sentence-transformers#2844). **No result is affected**, because no S3.2 result exists yet — both attempts were discarded. |
| 2026-08-09 | S3.2 — **W&B disabled inside the script; the second run stalled on its account prompt** | `WANDB_DISABLED`, `WANDB_MODE=disabled` and `report_to="none"` are set in `setfit_predict`, not in the notebook, so the script is safe however it is invoked. | The 2026-08-09 re-run completed five arms in 71 minutes, then printed W&B's `(1) Create a W&B account / (2) Use an existing / (3) Don't visualize` menu at the start of arm 6 and produced no further output for over two hours. This is a documented Kaggle failure mode rather than a local mistake: **W&B ships as a default package in the Kaggle image and its prompt cannot be answered in a saved/committed run**, so the hang is "impossible to avoid by default" (ultralytics/yolov5#1372). Kaggle also runs the kernel behind a pseudo-TTY (`forkpty` appears in the log), which is why W&B believed a human was present. **Two further pieces of insurance were added at the same time:** the arm order now puts SetFit **last**, so a failure inside the slowest and most fragile arm costs only itself rather than the six after it (arm order carries no scientific meaning; the arm set, budget and decision rule are unchanged); and the runner packages the checkpoint even when the script exits non-zero, printing `INCOMPLETE` rather than a results table that does not exist. |
| 2026-08-09 | S3.2 — **runs may RESUME across Kaggle sessions, gated on an environment fingerprint** | The per-arm checkpoint now stores an environment fingerprint (python, torch, transformers, GPU name, device count) and the runner restores a checkpoint attached as a Kaggle input, skipping arms already complete. Resuming across a **changed** environment is refused outright; resuming from a pre-2026-08-09 checkpoint that has no fingerprint requires `--allow-unverified-resume` and stamps `resumed_from_unverified_checkpoint: true` into the result file. | **This corrects a waste, not a scientific error.** The checkpoint was written into `/kaggle/working`, and every Kaggle commit run starts from a fresh clone, so it never survived a session. Three attempts therefore re-trained the **same five arms for ~70 minutes each** before reaching the arm that was actually broken (transformers 5.x → W&B hang → 3-class NLI head). The failures were all different; the 70 minutes in front of them was not. **Resuming is sound rather than merely convenient, and the evidence is ours:** arms train independently, seeds are fixed, and the five completed arms returned **identical** macro-F1 in two separate sessions on different GPU allocations — 0.9647 / 0.9360 / 0.9421 / 0.9402 / 0.9560. **The environment gate is not optional decoration:** Coakley et al. (2022) measured >6 pp of accuracy variation from environment alone across 780 runs on deterministic examples, and our whole between-arm spread is under 3 pp, so arms from two environments in one table would be reporting the environment. That is the same reasoning that discarded the five arms of the first attempt, applied as a mechanism instead of a judgement call. |
| 2026-08-10 | S3.2 — **RUN COMPLETE, verdict `TIE`. The setfit arm contributed ONE configuration, not ten, and is reported as such** | The seven-arm ablation ran to completion (commit `e3afa71`, Kaggle T4 ×1, transformers 4.57.6). Verdict **`TIE`** under both aggregation rules. **But the `setfit_labse` arm's `lr` was never passed to SetFit**, so its two learning-rate settings were the same computation, and its seed had no effect either. Its ten runs are one run repeated. Its mean (0.9590) stands as a **single-configuration point estimate**; its SD of 0.0000 is **not** evidence of stability and may not be reported as such; its "selected lr = 2e-05" is meaningless and is withdrawn. | **Proved from the log, not inferred.** Across all ten setfit runs the schedule peaked at the same 1.98e-5 under both nominal learning rates, `grad_norm` matched to sixteen decimals (2.8027944564819336), and `train_loss` was 0.016336093562370195 every time. Identical gradients cannot arise from different initialisations, so the seed was inert too. The checkpoint confirms it independently: setfit stored **1 distinct prediction vector out of 10**, against 8/10 for MuRIL and IndicBERTv2. **The code is fixed (`body_learning_rate`/`head_learning_rate` now passed, plus a test that reads the source) but the arm is NOT re-run**, because re-running costs ~2h15m of GPU for a measurement that cannot change a verdict already agreed by both aggregation rules — and the honest report of a single configuration is available for free. **What may be claimed about SetFit is correspondingly narrowed**: it was evaluated once, at SetFit's own default learning rate, and no seed-sensitivity figure exists for it. Its pre-registered status as an expected loser (Beliveau et al. 2024) is **not** discharged: it placed second of seven, but in a TIE, and on one configuration. |
| 2026-08-10 | S3.2 — **`TIE` fires; the tie-break is applied and the thesis must say the data did not choose** | Pre-registered outcome 2 fires: no arm significantly beats every other. All **21** pairwise paired-bootstrap comparisons are non-significant after Benjamini–Hochberg; the smallest p is **0.096**. The tie-break `[smallest_params, banglabert]` selects **BanglaBERT** (110M, smallest of the seven), which is also the pipeline default. | This is the outcome §S3.2 named as most likely, for the reason it gave: the 2025–26 Bangla literature reports different winners on the same data, so no result was predictable. **Two independent facts make the tie a measurement statement rather than a shrug.** (i) The **between-arm spread is 0.0348** (0.9298–0.9647) while **MuRIL's seed-to-seed SD alone is 0.0391** — the variation inside one arm exceeds the variation between all seven. (ii) Coakley et al. (2022) measured **>6 pp** of accuracy variation from hardware/software environment alone; our whole spread is under 3.5 pp. **The differences we are trying to resolve are below the resolution of the instrument, and the thesis says so.** Consequently: **BanglaBERT is used, and every defence of that choice states that the data did not determine it** — the tie-break is a declared non-performance rule, not a finding. ⚠️ Also carried: the winner is selected on weak-label **reproduction**, not validity (deviation of 2026-08-08); and the arm ORDER differs between the two aggregation rules (XLM-R is 6th under the headline rule and 7th under pooling), so **no ranking below the top may be quoted at all** — only the tie. |
| 2026-08-10 | S3.2b — **three reference points added; the ablation had none** (pre-registered BEFORE the numbers) | S3.2 compared seven arms only with each other. S3.2b adds **majority class**, a **single length threshold fitted on TRAIN**, and — the one that matters — **frozen LaBSE embeddings with an L2 logistic head**. Bands are fixed here, before the probe has been run, in units of **one dev item = 1/82 = 0.0122 macro-F1**, because that is the resolution the dev set has. | **The ablation cannot answer "0.96 against what?", and that is a reviewer's first question.** Two of the three references were computable in seconds and simply were not computed: majority = **0.3926**, best length rule tuned even *on dev* = **0.6322**. Those already establish that the arms are not the class prior or the length confound wearing a transformer, and they belong in the artifact rather than in someone's memory. **The third is a threat, not a courtesy.** `cluster_k2` was produced by k-means **on LaBSE embeddings**, so a linear probe on those same embeddings is the label's own generating geometry asked to reproduce itself. Buckmann et al. (2024) independently report that penalised logistic regression on a small model's embeddings matches much larger models in the tens-of-shot regime. **Pre-committed bands:** (i) probe within **one dev item** of the best arm → `CIRCULARITY_CONFIRMED` — the seven-arm table may then support **no claim about backbones**, the `TIE` is re-explained as near-saturation by construction rather than backbone interchangeability, and **Verifier-A's choice is reopened**, since a frozen probe matching a fine-tuned BanglaBERT means the fine-tuning is not earning its cost in the Phase 4 loop; (ii) probe clearly above the surface baselines but below the arms → `PARTIAL`, and **the gap, not the raw 0.96, is what may be quoted as the verifier's contribution**; (iii) probe at surface-baseline level → `NOT_CIRCULAR`, which strengthens S3.2 and **must be checked for a bug before it is believed**. **This is run now rather than at write-up because outcome (i) would change what Phase 3 is allowed to claim, and finding that at viva is not a recoverable position.** |
| 2026-08-10 | S3.2b — **`CIRCULARITY_CONFIRMED`. The frozen probe BEATS every fine-tuned arm, and the seven-arm ablation may support no claim about backbones** | Pre-registered band (i) fires, and beyond its own threshold: **frozen LaBSE + L2 logistic regression scores 0.9866 against the best fine-tuned arm's 0.9647** — the probe is **1.8 dev items *ahead*, not behind**. It makes **one error on 82 items**. Reference points: majority **0.3926**, best length rule fitted on train **0.6197** (threshold: n_words ≤ 7). | **Verified before being believed**: train and dev are disjoint (no leakage into the logistic fit), the error count reconstructs the reported macro-F1 exactly at 1/82, and the artifact carries a real provenance stamp (commit `1a37be1`). **The mechanism is not mysterious and was foreseeable**: `cluster_k2` was produced by k-means **on LaBSE embeddings**, so the label is close to a linear boundary in that space, and a linear probe recovers it almost perfectly. **Three consequences, all binding.** (1) **The seven-arm table may support no claim about backbones.** It is reported as a demonstration that the label is linearly recoverable from its generating encoder. (2) **The `TIE` verdict stands but its explanation changes**: the arms are indistinguishable because the task is near-saturated by construction, not because backbones are interchangeable in general — and the 2026-08-10 tie-break note must be read with this attached. (3) **Fine-tuning did not merely fail to help; it cost accuracy.** Every arm sits below a probe that trains in seconds, which is what Buckmann et al. (2024) predict for the tens-of-shot regime and what Beliveau et al. (2024) imply for small non-English data. **Not affected:** RQ2 needs a well-defined reproducible label, and RQ1-H established that humans perceive the distinction at 0.78/0.84 against 0.25 chance — the label is not an artefact, it is simply *linear in LaBSE space*. **What this does affect is Verifier-A, and that is opened as a decision rather than settled here** (see the next row). |
| 2026-08-10 | S3.2c — **OPEN DECISION: Verifier-A and Verifier-B can no longer both be the obvious choice, because RQ5 needs them to disagree** | S3.2b makes the frozen LaBSE probe the strongest, cheapest and best-calibrated candidate for Verifier-A. **But if Verifier-B is also a LaBSE probe, A and B become near-identical functions on the same embedding space, and RQ5's Goodhart test — which measures the gap between A-scores and B-scores as the loop optimises against A — is destroyed by construction.** Inviolable rule 6 makes that wall the point of the design, so this cannot be decided on convenience. | **Not settled here, because it is a design call with a real trade-off and it belongs to Sabbir.** Sketch of the options, with what each costs: **(a) A = LaBSE probe, B = fine-tuned BanglaBERT.** Deliberately different model families, so the wall is methodological as well as data-level — arguably *stronger* than the original design, in which A and B differed only by training split. Costs: B is then the weaker model, and "the evaluator is worse than the thing it evaluates" needs defending. **(b) A = B = probes on disjoint splits.** Cheapest and most consistent, but the two verifiers agree by construction and RQ5 becomes unmeasurable; this would have to be declared as abandoning RQ5, not as a detail. **(c) A = fine-tuned BanglaBERT anyway**, on the argument that the in-loop verifier should not be the same object as the label's generating geometry — i.e. accept 2 pp less accuracy to buy independence from LaBSE. This is the option the S3.2b result makes *interesting* rather than obviously wrong: a verifier that is a linear function of LaBSE may be trivially gameable by a generator whose text is scored in that same space, which is exactly the failure RQ5 is looking for. **Whichever is chosen must be registered before Verifier-A is trained**, and the reasoning recorded as Sabbir's or as delegated. |
| 2026-08-10 | **S3.2c RESOLVED — Verifier-A = frozen LaBSE probe, Verifier-B = fine-tuned BanglaBERT (cross-family)** | Decision 16 is closed. **Verifier-A** (in-loop gate) is the frozen LaBSE + L2 logistic probe: best measured, seconds to fit, natively calibrated, no GPU in the Phase 4 loop. **Verifier-B** (S6 evaluation only, never in the loop) is the fine-tuned BanglaBERT from S3.2. The wall between them is now **methodological as well as data-level**: ELECTRA vs BERT pretraining objective, Bangla-specific vs multilingual corpus, different tokenizer, fine-tuned vs frozen — where the original design separated A and B only by training split. | **⚠️ Provenance, stated so it is not mistaken for Sabbir's own argument: the recommendation and the reasoning below are Claude's; Sabbir delegated the call and endorsed it ("তোমার মতামতই ঠিক আছে"). Endorsed, not authored.** **The literature moved this from a preference to a standard.** Mahmoud et al. (2026) optimise against a training verifier and evaluate against a **cross-family panel**, explicitly to reduce dependence on any single evaluator, and find that weak verifiers produce proxy gains that do not transfer to reference verifiers. Wang et al. (2026) name **evaluator–policy co-adaptation** as one of three mechanisms of reward hacking — which is precisely what two LaBSE probes would have been. **The obvious objection to this configuration is dead:** Baker et al. (2025) show a *weaker* model (GPT-4o) monitoring a stronger one (o3-mini) effectively, so "the evaluator is weaker than what it evaluates" is documented practice rather than a flaw. **A use is also restored for the S3.2 table**: it may support no claim about backbones, but it is the evidence that BanglaBERT is a viable independent evaluator (0.9647, strongest of the fine-tuned family) — the ablation is repurposed honestly rather than discarded. **Cost accepted and named:** Verifier-B is ~2 pp weaker than Verifier-A, and B is the arm whose `lr`/seed handling was correct, so its numbers stand. |
| 2026-08-05 | RQ1-G — **region-B replication added; not in RQ1 as written, and logged late** | A complete second pass of the instrument (`s2_pilot_regionB` → `s2d` → `s2e` → `s2f`, no script changes) pointed at region B, with a matching rule fixed in advance. Section "RQ1-G pre-commitment" was written 2026-08-05 before any region-B config ran. **This row is added 2026-08-10; the section had no deviations entry for five days, which is a process failure and is recorded as one rather than backdated.** | RQ1 as written analyses one corpus. Replication in a second corpus differing in register and provenance is the strongest available evidence for a discovered structure, and it was free — every script already took the region as a config field. **The outcome justified the addition, though not in the hoped-for direction:** pre-registered outcome 2 fired. B selected K = 2 (PS **0.818**, bootstrap ARI **0.962**) but the signature did **not** match — `length_auc` 0.550 → `NOT_LENGTH` against A's 0.676, richness inversion in **1 of 4** bands against A's 4/4. 🎁 **The useful finding is the negative one:** B's cut is a 49.4/50.6 bisection correlating with *nothing measurable* (every surface AUC 0.50–0.58, ARI vs Sentiment 0.011, silhouette 0.039, HDBSCAN noise 96.7%) **yet it clears PS ≥ 0.80.** Region B is therefore a **negative control demonstrating that the pre-registered stability rule can pass a contentless cut** — which is exactly the failure von Luxburg (2010) describes for stability-based K selection, and which Pinto et al. (2026) reproduce in simulation. The rule is not withdrawn; it is demoted to necessary-but-not-sufficient, and the demotion is reported. |
| 2026-08-08 | RQ1-H — **human validation attempt 2, a DIFFERENT INSTRUMENT after attempt 1 failed. The single largest departure in this document, and it was not logged until 2026-08-10** | RQ1 pre-registered Krippendorff's α (ordinal) on a 0–3 rating scale over gold-300. Attempt 1 (RQ1-F) returned α = **0.4970** and Gate 2 was not computed. **Attempt 2 replaces the instrument entirely**: a 50-set **intrusion task** (Chang et al. 2009) plus a 40-item pairwise block, length-matched to within 2 words, no construct named to the annotator. Section "RQ1-H pre-commitment" was written before `intrusion_build.py` existed and before any item was judged. **Attempt 1 is reported in full and is not withdrawn, superseded or reframed.** | **This is the departure a reviewer will attack hardest — "they kept running instruments until one worked" — so the defence is stated here, in the log, and not left in the section body where nobody checks.** Four things make it a second *measurement* rather than a second *try*. **(1) The failure was diagnosed before the replacement was designed**, and diagnosed as an instrument failure with a named cause: the scale collapsed (68%/76% of ratings on the single value "2") because Claude's calibration advice — *"names an aspect → at least 2"* — moved everything to 2. Raw agreement was **75.5% exact / 98.7% within-1**; the raters agreed, the scale did not discriminate. That is the kappa paradox, and `gwet2008ac1` was already listed as its guard. **(2) The literature predicted the failure and was read too late.** Kiritchenko & Mohammad (ACL 2017) had already shown comparative judgements more reliable than rating scales at equal cost. Had it been read first, attempt 1 would not have used a rating scale — this is the founding entry of the "search before the decision" standing instruction. **(3) The new instrument can fail.** It names no construct, so it cannot fail merely because *our name* for the construct was wrong — the flaw attempt 1 could not distinguish from a real negative — and `NOT_PERCEPTIBLE` was pre-registered as a genuine negative result. **(4) A third attempt is forbidden in advance**, including the easier length-unmatched re-run, which is confined to Future Work. **Outcome:** Gate A **39/50 and 42/50** against 0.25 chance (p < 1e-15, pre-registered bar 0.45); Gate B **34/40 and 34/40** against 0.50 → the construct **is** specificity. Obtained with length matched to ±2 words and a length heuristic scoring **0.16, below chance**. |
| 2026-08-10 | **TERMINOLOGY — `persona` and `cluster` are BOTH retired; the object is an engagement-specificity AXIS and `cluster_k2` is an imposed cut through it** | STATUS decision 12 is closed. The K = 2 halves are levels of a **continuous engagement-specificity axis**, not two groups. Permitted: *axis*, *gradient*, *the cut*, *level*, *`cluster_k2` as an operational discretisation*. Forbidden: *persona*, *audience type*, *subgroup*, *typology*, and — new, and the part that changes most — **bare *cluster* as a claim about structure**, though `cluster_k2` stays as the frozen variable name in code and data, where renaming would break the split map. Generation is **axis-level-controlled**. | **⚠️ Provenance: Sabbir delegated the call ("you can make the best decision"); the choice and the reasoning are Claude's. Endorsed, not authored.** **The literature settled this, and it moved the answer past both options that were on the table.** Pinto et al. (2026) run k-means on data with no latent groups and on 8,360 real psychometric respondents, obtaining **k = 2, silhouette ≈ 0.31, ARI 0.999 ± 0.001, cluster sizes 50.6/49.4** — numerically almost our region B (49.4/50.6, silhouette 0.039, bootstrap ARI 0.962). Their verdict on their own result: *"better interpreted as **geometric stratifications of a latent psychological continuum** rather than as evidence for discrete subtypes"*, and, decisively for us, **"Stability, therefore, is not equivalent to validity."** On correlated Gaussian data they obtain ARI = 1.00, SD 0.00 and call it *"an artificial partition of a continuous, anisotropic distribution."* Cornelissen et al. (2026) publish a negative clusterability result across three musical traditions, show that a previously published four-type typology was an artefact — with no clustering present, k-means places centroids near the leading principal axes *"for entirely mathematical, not musical reasons"* — and conclude the character is **continuous**. **Consequence: *persona* was already banned on 2026-08-05, and *cluster* does not survive either**, because the literature reserves it for structure our geometry does not have (silhouette 0.053, monotone gap, HDBSCAN 100% noise). **What makes our position stronger than either paper's, and it must be said in these words: neither of them had human validation.** RQ1-H did — 0.78/0.84 against 0.25 chance, length-matched, length heuristic below chance. So the claim is sharper than "the cut is arbitrary": **geometrically it is a line drawn through a continuum, and people can nonetheless see it.** ⬛ Considered and rejected: keeping *persona* on RQ1-H's warrant — rejected because perceptibility of a distinction is not evidence of discrete groups, and the two claims are exactly what this literature separates. Title and Ch.1 framing follow this constraint; the wording is Sabbir's, the constraint is not. |
| 2026-08-10 | **Ch.5 LIMITATION registered: S2e and S2f are post-clustering inference on the rows that defined the clusters** | The φ = 0.3981 / χ² = 300.7 association, the surface AUCs, and the distinctive-vocabulary tables in S2e/S2f are all computed on the **same region-A rows that k-means used to form the partition**. No number is withdrawn; the inferential status of all of them is downgraded and stated wherever they appear. | **Found by literature search on 2026-08-10, not by a reviewer, and not by us at the time.** Chen & Witten (2023), *Selective inference for k-means clustering*, show that classical post-hoc tests on cluster-derived groups produce **inflated Type I error**, because the same data both defines and tests the groups — and that substantial between-group differences appear **even when no population categories exist**. S2f's Test C already carried the right instinct, self-flagging as a resubstitution upper bound; the flag simply was not generalised to the other statistics in the same two files. **Consequence: S2e and S2f are descriptive profiling, not hypothesis tests, and no p-value from them may be quoted as evidence that the halves differ.** What survives untouched is RQ1-H, which is computed on **held-out items outside G-300, judged by annotators blind to the partition** — it is not post-clustering inference and does not inherit this limitation. That asymmetry is the reason the human validation, not the profiling, carries the RQ1 claim. |
| 2026-08-10 | RQ5 — **an invariance test is added; the A-vs-B gap alone is documented to under-detect** | RQ5 keeps its A-score-vs-B-score gap across attempts, and **adds a pre-registered invariance check** in the style of Shihab et al.'s (2025) Evaluator Stress Test: controlled perturbations that leave meaning intact are applied to accepted drafts, and a verifier whose score moves on those perturbations is responding to surface artefacts rather than content. Both signals are reported; **neither alone decides RQ5**. | **Because cross-family separation is necessary but not sufficient, and we now have the number.** Zhou (2026) shows judge errors **transfer across families** (Qwen, Llama, Gemma) and that a strict three-judge ensemble still accepts **55%** of them — so an A-vs-B gap can stay small while gaming is happening. Shihab et al. (2025) report 74.2% precision / 78.6% recall for perturbation-based detection in the LLM-alignment domain, with **early warning that precedes quality decline**, which is the property RQ5 needs. 🎁 **One structural advantage we already have, recorded because it is easy to lose:** Zhou's decisive fix is a judge that **commits to its own answer before seeing the candidate** (false positives 0.719 → 0.012). Our verifiers predict the cluster label **independently** and are never shown a target to agree with — so the S3.x design is **already de-anchored in Zhou's sense**, by accident rather than by foresight, and the thesis should say so in those words. |
| 2026-08-11 | ⚠️ **PROCESS DEFECT, recorded not tidied: the seal of 2026-08-10 was granted without cross-checking `research_pipeline_en.md`** | The Phases 1–3 seal claimed *"every departure is logged."* Departures are measured against the **normative spec** (`docs/research_pipeline_en.md`, per `CLAUDE.md`), and that file was never opened during the audit. The audit compared `protocol.md` against `STATUS.md` (numbers) and against itself. **The seal is not withdrawn — the four append-only properties still hold and are still checkable — but the completeness claim was not verified the way it should have been, and the rows below are what the missing check found.** Found because Sabbir asked whether the pipeline had been read. | **The claim was stronger than the work behind it, and that is exactly the failure mode this document exists to catch — so it is logged against ourselves.** Consequence carried forward: the pipeline cross-check is now a required step of any future seal, not an optional one. |
| 2026-08-11 | 🔴 **Pipeline §2.1's "honesty clause" instructs writing a sentence our own results falsify. It is WITHDRAWN and must not appear in the thesis** | §2.1 directs: *"low silhouette reflects known pathologies of high-dimensional embedding spaces, **not absence of structure**; hence we rely on **stability** + human validation."* **That sentence may not be written.** The pipeline text is deliberately not edited (same policy as its stale S0 numbers); the withdrawal lives here. | **Stability is precisely what region B destroyed.** RQ1-G: region B cleared PS ≥ 0.80 at **0.818** on a 49.4/50.6 cut correlating with nothing measurable (all surface AUCs 0.50–0.58, ARI vs Sentiment 0.011, silhouette 0.039, HDBSCAN noise 96.7%). `vonluxburg2010stability` describes this failure mode for stability-based K selection; `pinto2026drawinglines` reproduces it in simulation at ARI 1.00, SD 0.00 and states plainly that **"Stability is not equivalent to validity."** The clause would have had the thesis assert, in its own Methods, the exact inference its Results disprove. **What replaces it:** low silhouette is reported as evidence *consistent with* absence of separated groups, the three converging indicators are reported together, and the claim rests on **RQ1-H's human validation alone** — which is the one instrument that does not depend on the geometry. |
| 2026-08-11 | **Pipeline §2.5's prescribed failure path was NOT followed, and the substitution is only now logged as a departure from it** | §2.5 fixes the remedy for low agreement: *"α < 0.667 → **revise guideline + re-annotate**. Still < 0.667 after **two** revisions → reframe as a theory-driven scheme."* Observed α = **0.4970**. **Zero re-annotations were run**, and instead of the prescribed reframe, a **different instrument** (RQ1-H, intrusion task) was introduced. | The RQ1-H row of 2026-08-08 defends the instrument switch on its merits; **what it never said is which rule the switch broke**, and that is the form a reviewer checks. Stated now: §2.5 offers two exits from low α — re-annotate, or reframe — and **we took a third that the spec does not contain.** The reason is recorded and is not a methodological argument: **annotator time was exhausted and none was available**, so the re-annotation path was closed by circumstance rather than rejected on merit. Whether the third exit is *better* than §2.5's reframe is arguable and is argued in the RQ1-H row (an instrument that names no construct can return a real negative; a rating scale that collapsed cannot). Whether it is a **departure** is not arguable, and it is now on the record as one. |
| 2026-08-11 | **Pipeline §5.1's generation count is arithmetically stale: 2,160 → 1,440 per language** | §5.1 specifies *"90 eval-plots × **3 personas** × 8 conditions = **2,160** generations per language."* K = 2 since 2026-08-03, so the correct figure is **90 × 2 × 8 = 1,440**. Same correction applies to §4.5's τ-sweep (30 dev-plots × 3 → × 2) and §4.6's per-level retry-rate report. | Consequence of decision 7 (K = 3 → 2) that nobody propagated for eight days, including in yesterday's audit, which corrected RQ2's *design line* to "2 axis levels" and left the *count* untouched. **Not cosmetic: it is a one-third reduction in the experiment's size**, and therefore in its cost, its runtime, and the width of every bootstrap CI in §5.6. Recorded before Phase 5 is planned rather than discovered while running it. ⚠️ §4.6 additionally names a persona — *"Enthusiastic Casual expected highest — prior recall 0.5674"* — from the retired three-tier scheme; that name and that number refer to an object that no longer exists and may not be quoted. |
| 2026-08-11 | **Pipeline §2.3's theory grounding and §5.4's mandatory Limitations sentence both need rewording under the axis framing** | §2.3 grounds *"three personas"* in audience typologies (`abercrombie1998`, `funk2001pcm`, `cuadrado1999`, `hunt1999`); `cuadrado1999` is described as a **3-cluster** cinema segmentation, *"almost a mirror of our scheme."* It is no longer a mirror of anything claimed. §5.4's mandatory sentence reads *"'Simulation' should be read as **persona-conditioned** response generation"* — using the word retired on 2026-08-10. | **The §5.4 sentence is the one that matters, because it is the thesis's own defence of the word "Simulation" in the title, and I broke it yesterday while fixing the terminology.** Corrected wording, fixed here: *"Our data lacks review-to-film mapping; hence we validate distributional realism at corpus level, not per-film audience prediction. **'Simulation' should be read as axis-level-conditioned response generation, not validated predictive audience modelling.**"* On §2.3: the sources may still ground a **graded engagement construct**, which is what RQ1-H's Gate B measured; they may **not** ground discrete audience types. Each entry needs a re-read against the axis framing (`related_work.md` Tier 3 carries the same flag). |
| ~~2026-08-11~~ | ~~**English arm formally DEFERRED, not dropped — invoking the charter's own cut rule**~~ ⛔ **THIS ROW WAS WRONG AND IS SUPERSEDED BY THE ROW BELOW (2026-08-11, later same day).** It is struck rather than deleted because the error is instructive: **Claude invoked a scope-reducing escape clause that belongs to Sabbir, on the basis of Sabbir saying "pore kori" (do it later).** "Later" is a statement about *order*; the cut rule is a statement about *scope*. They were treated as the same thing and they are not. | Retained as a record of the misreading, not as an operative deviation. |
| 2026-08-11 | **English arm is SCHEDULED, not reduced — full scope retained, RQ4 intact** (supersedes the struck row above) | Pipeline §1.2's English Arm Charter runs **in full**: IMDB subsample to n = |bn_clean| = **4,625** with identical cleaning and split construction, LaBSE clustering under the identical K-selection protocol, **en-A / en-B verifiers + backbone check** (§3.2), MPST v2 **30 dev + 90 eval** plots, the full **8-condition ablation** (§5.1) at **1,440** generations, and the tokenizer-fertility covariate. **Sequenced after the Bangla Phase 3/4 machinery exists**, because every config already takes the corpus as a field, so building it twice would be wasted work. **RQ4 (Δ_bn vs Δ_en) remains live in its strong form.** | **Sabbir's call, stated directly: *"english thakbe. cross lingual hobe. pore kori"* — and separately, as a standing instruction: *"amader lokkho research pipeline onujayi kaj kora."*** The charter's *"exceeding one week → cut to fertility + zero-shot reference only"* clause is **not** invoked and remains available **to Sabbir**, unexercised. ⚠️ **Risk recorded now rather than discovered later, because it is real:** IMDB reviews are long and detailed while the Bangla corpus averages ~8 words, so the English side may yield **no stable K** — the engagement-specificity axis may simply not exist there. **The charter already survives this**, and the reason is worth stating: its core comparison is **Δ, the improvement over zero-shot per condition**, not label correspondence. Each language derives its own label from its own clustering; what is compared is how much the verifier loop *helps*. So a different English structure — or a `NO_STABLE_K` outcome there — bounds the comparison without invalidating it, and would itself be a reportable cross-lingual finding. **Mirror-never-merge (inviolable rule 8) binds throughout.** |
| 2026-08-11 | 🔴 **Verifier-B's definition disambiguated — as written it could have voided inviolable rule 6** | Decision 16 (2026-08-10) says Verifier-B is *"the fine-tuned BanglaBERT **from S3.2**."* But `configs/s3_backbone.yaml` sets `role: A`, i.e. **S3.2 trained every arm on R1 — Verifier-A's data.** Read literally, Verifier-B would share training data with Verifier-A. **Binding definition, fixed here: Verifier-B is the BanglaBERT *recipe* from S3.2 — same backbone, same budget, same seeds — RETRAINED on R2's 888 labelled rows (531/357). The S3.2 checkpoints are never used as Verifier-B.** | **No result is affected — no verifier has been trained — but the sentence was one training run away from silently collapsing the wall that RQ5 measures.** Rule 6 exists to keep A and B independent; sharing R1 would have made the Goodhart gap unmeasurable *and* left an artifact that looked correct. The intent was never in doubt (STATUS records Verifier-B's n as 888; the config comments `"B" would draw R2`), which is exactly why it survived review — **an ambiguity that everyone reads correctly is still an ambiguity, and code does not read intent.** Prevention: the Verifier-B training config must assert `role: B` and a test must fail if its training ids intersect R1. |
| 2026-08-11 | ⚠️ **Decision 16 AMENDED: "cross-family" is registered as necessary but NOT sufficient, and independence becomes measurable rather than asserted** | Decision 16 justified the A/B wall on family separation (ELECTRA vs BERT, Bangla-specific vs multilingual, fine-tuned vs frozen). **That argument is weakened by evidence found on 2026-08-11 and the weakening is recorded rather than absorbed.** Added: a pre-registered **entanglement audit** on the dev slice before any Goodhart number is interpreted, following `kuai2026entanglement` — co-failure structure on the failure manifold (BEI / CIG), not score correlation. | `kuai2026entanglement` audits 18 LLMs across 6 families and finds **widespread intra- *and* cross-family behavioural entanglement, including cross-generation**, concluding that *"apparent agreement may reflect a consensus of correlated errors rather than independent verification."* Entanglement tracks judge over-endorsement bias (Spearman **0.64**, p < 0.001; **0.71**, p < 0.01), and — the operationally important part — **plain correlation fails to detect it**; the signal lives in *how models fail together*, weighted toward co-failures on easy items. **This cuts at us harder than at their setting:** our A and B are not two independently-developed frontier models. They are trained on **the same label, derived from the same k-means over the same corpus**, so shared-label entanglement is guaranteed and only its magnitude is unknown. **Pre-committed:** if the audit shows high A/B entanglement, a small A−B gap in RQ5 **may not be read as absence of gaming**, and that is stated wherever the gap appears. |
| 2026-08-11 | 🔴 **RQ3 — the "symbolic resists gaming" reframing was proposed, searched, and REJECTED BEFORE being written. RQ3 stands unchanged** | S3.2b left RQ3 ("hybrid beats neural-only") nearly unanswerable: Verifier-A now scores **0.9866 = 1 error on 82 dev rows**, so the §5.1b rule *"if symbolic adds < ~2 points, soften the claim"* would need to resolve ~1.6 dev items. Claude proposed reframing RQ3 around gaming-resistance instead. **The search killed it.** RQ3 keeps its original hypothesis and its original pre-commitment. | **This is the standing search-first instruction working as designed, and it is logged as a near-miss rather than quietly dropped.** `mahmoud2026rubric` — already cited here for decision 16, but only from its abstract — studies exactly this claim and refutes it. Rubric/rule-based rewards **are** hacked: under a *strong* verifier, rubric-based judges preferred the RL checkpoint on **85.8%** of prompts while rubric-free judges preferred the **base** model on **78.4%**, with gains concentrated in **presence-based** criteria (completeness **+1.07**) and losses everywhere else (conciseness **−2.91**, relevance **−1.10**, factual correctness **−0.85**, overall **−1.02**). They name the mechanism *"hacking the rubric, not the verifier."* 🔴 **Our §3.5 feature pool is almost entirely presence/count-based** — intensifier count, positive/negative lexemes, exclamation, negation, name mentions, specificity terms — i.e. the exact category that was hacked. **And our design is strictly worse than theirs:** §4.2's Reflector *tells the Writer which symbolic rule failed* ("no intensifiers [R1 failed]"). Their policies had to discover the rubric; ours is handed it. **Conclusion: symbolic is plausibly the MOST gameable component in this system, not a shield against gaming.** Had the reframing been written from memory, it would have been refuted by a paper already in our own bibliography. **What symbolic is retained for, honestly:** (i) §3.5 mandates it and §4.2's Critic cannot exist without it; (ii) **interpretability** — it can say *which* rule failed, which the LaBSE probe cannot, and the Reflector requires exactly that; (iii) a new, testable use registered here — **symbolic as an instrument for detecting gaming rather than preventing it**: presence-based symbolic scores rising across attempts while Verifier-B stays flat is Mahmoud et al.'s signature, and it is added to RQ5's evidence alongside the A−B gap and the invariance check. **Weights are not hand-set** (§3.5 already forbids it) and, per the 82-row resolution limit, the hybrid weight is fit on the **30 dev-plots' generations** — where the Critic actually operates — and reported as a sensitivity curve, never a point. |
| 2026-08-11 | ⚠️ **Dev-slice reuse counted and disclosed: 82 rows now carry five decisions** | The 82-row labelled dev slice is used for: (1) learning-rate selection in S3.2, (2) temperature scaling / calibration (§3.4), (3) the symbolic scorer's logistic weights (§3.5), (4) the hybrid weight (§3.5, §5.1b), and (5) τ selection (§4.5, via dev-plots). | Recorded as a count rather than a caveat because the number is the argument. §3.4 already demoted calibration to descriptive at this n; the same n is silently carrying four further decisions. Decisions (4) and (5) are moved to the **30 dev-plots** by the RQ3 row above, which removes them from the 82; the remaining three are disclosed together in Ch.5 as a single multiple-use limitation rather than three separate footnotes. |
| 2026-08-11 | **S3.5 — the symbolic feature pool is REPLACED before a line of it was written; IDF added, presence rules demoted** | Pipeline §3.5's pool (intensifier count, positive/negative lexemes, length bucket, exclamation, negation, name mentions, specificity terms) is **almost entirely presence-based**. Replaced by six families registered in §"S3.5 pre-commitment" above, built on `ko2019specificity`'s validated set: **F1 IDF statistics (min/max/mean)** and **F6 length-corrected lexical richness** as the load-bearing pair, with the pipeline's presence rules retained as F2–F5 and **individually labelled gameable**. Excluded with reasons: imageability/familiarity norms (**none exist for Bangla**), stop-word fraction (no resource, and rule 7 territory), emoji (zero in corpus). | **The search ran before the design and changed it — twice over.** (1) `mahmoud2026rubric` shows presence-based criteria are the category that gets hacked, and §4.2's Reflector *names the failing rule to the Writer*, so a pool of presence rules under this loop is closer to a gaming instruction than a scorer. (2) `ko2019specificity` then supplied the replacement: our construct is **sentence specificity**, a named task with prior art back to Louis & Nenkova (2011), evaluated by them **on movie reviews** at Spearman **0.702** against a **length baseline of 0.581** — which independently reproduces our own `length_auc` 0.6764 and registers length as expected rather than embarrassing. 🔑 **Why IDF is the one that matters: raising it requires using genuinely rarer, more specific words, which *is* the construct.** It cannot be satisfied vacuously, which is exactly the property Mahmoud et al. find presence criteria lack. 🎁 **A framing gain beyond S3.5: the construct is adopted, not invented** — Ch.2 may now cite a literature for it instead of defending a coinage, and RQ1-H's Gate B result becomes corroboration of an existing construct rather than the definition of a new one. ⚠️ **And an uncomfortable correction to the G-300 post-mortem:** `ko2019specificity` reached Cronbach α 0.68–0.70 on this construct with **nine** raters and an exclusion rule for raters below 0.3. Attempt 1 had **two** and no exclusion rule. The 2026-08-05 diagnosis blamed scale collapse and Claude's calibration advice; **both stand, but they were not the whole cause — specificity rating is known to need many raters, and we ran it with the minimum possible.** |
| 2026-08-11 | **S3.5 — the hybrid weight is fit on dev-plot GENERATIONS, not on the 82 dev rows** | §3.5 and §5.1b tune the 0.6/0.4 neural/symbolic weight on the dev slice (grid 0.5–0.8). Moved to the **30 dev-plots' generated outputs**, and reported as a **sensitivity curve, never a point**. | Two independent reasons. **(1) Resolution.** Verifier-A is now the frozen LaBSE probe at **0.9866 — one error in 82**. Every weight in the 0.5–0.8 grid returns the same answer, and §5.1b's "<2 points" rule would need to resolve **1.6 dev items**. The sweep as specified is degenerate, not informative. **(2) Transfer, which is the deeper reason.** `kapur2026length` show that in **human** text longer means more specific, while in **machine-generated** text the relation is **flat or reversed** — so a weight calibrated on real reviews is calibrated on the wrong distribution. The Critic scores *generated* text; the weight belongs where the Critic operates. This also removes two of the five decisions the 82-row slice was carrying (deviation of 2026-08-11), leaving three. |
| 2026-08-11 | **S3.5 / INVIOLABLE RULE 7 — F1 (IDF) is NOT enabled; it is run once as an explicitly-labelled PILOT, and the cost of the rule is now measured at ~18 macro-F1 points** | F1 stays **off** in `results/s35_symbolic.*`. A single pilot run under `configs/s35_symbolic_pilot_idf.yaml` writes to `results/pilot_s35_idf.*`, banner-marked **NOT A RESULT** and unquotable. **The constraint is enforced structurally, not remembered:** `s35_scorer.py` refuses to run with `enable_f1: true` unless the config sets `pilot: true` *and* the output filename contains `pilot`. ⚠️ **This row records a measured cost and requests a ruling. It does not take one.** | **⚠️ Provenance: Sabbir delegated ("jeta valo hoy koro"); the choice and reasoning are Claude's, endorsed not authored.** Rule 7 forbids TF-IDF "in the main pipeline ... **never in a result**", and permits it "**only as an explicitly-labelled cheap proxy in a pilot**". F1 is IDF alone — three scalar summaries of a review's own tokens, no document-term matrix, no encoder replaced, no text altered before LaBSE or BanglaBERT — so a reading exists under which it falls outside the rule. **That reading was not adopted, for two reasons.** (i) The rule's text governs *results*, not our interpretation of it, and it supplies its own legitimate route: the pilot. (ii) **Reinterpreting an inviolable rule is not a delegated-decision-sized act** — "breaking any of these invalidates the thesis" — so it belongs to Sabbir *and* the supervisor, dated and signed, not to a config flag. 🔴 **What the pilot found, and it contradicts the prediction that justified running it cautiously:** F1 raises stratified 5-fold CV from **0.5150 ± 0.0713 → 0.6949 ± 0.0532**. Leave-one-out delta **+0.1798**, i.e. **2.5× the CV SD** and an order of magnitude above every other family. **Mean rises and variance falls together**, which is not the signature of overfitting. Claude predicted the opposite — that 14 features on 82 rows (5.86 rows/feature) would likely *lower* CV — and that prediction was wrong, recorded here rather than quietly dropped. 🎁 **A second effect nobody anticipated: F1 repairs F2.** Without IDF, removing length *improves* CV by 0.1082 — length is actively harmful. With IDF present, length's delta moves to **+0.0033**. Length was a poor proxy for the signal IDF measures directly, and was injecting noise in its absence. 🔑 **The design consequence is the one that matters for RQ3 and RQ5:** with F1 the two **non-gameable** families (F1 +0.1798, F6 +0.0213) are the top contributors, while the gameable presence families remain **negative** (F4 −0.0191, F5 −0.0350). **Rule 7 as applied does not merely cost accuracy — it pushes the symbolic scorer toward exactly the gameable families that `mahmoud2026rubric` identifies as the hacked category.** That is the substantive argument for an amendment, and it is put here as evidence for a decision, not as a decision. **Until a ruling is recorded in this file, `enable_f1` stays false and the guard stays in place.** |
| 2026-08-11 | 🔧 **MAINTENANCE FAILURE, self-reported: `research_pipeline_en.md` went 10 days and 55 commits without an update, while remaining the normative spec** | The pipeline's execution checklist showed **3 ticks when 8 further steps were complete**; §5.1 still specified **2,160 generations** when K=2 (2026-08-03) had made it **1,440**; §4.5 and the S6 stage contract still multiplied by **3 personas**; and the Ch.1 blueprint still asserted the three-persona scheme was *"data-confirmed"*, which G1 had refuted. All corrected in one pass on 2026-08-11, with a MAINTENANCE STATE box at the top of the file recording what was fixed and what was deliberately left. Framing language (*persona*, *three personas*) was **flagged inline as 🔴 [D12] rather than rewritten**, because the replacement wording is open decision 12 and belongs to Sabbir. | **Sabbir asked directly why the pipeline was not being maintained, and it was not.** His standing instruction is explicit — *"the research pipeline is the step-by-step process of this project. You have to maintain it."* Progress was being written to `docs/STATUS.md` alone, on the assumption that a single "where are we" file sufficed. **It does not: CLAUDE.md gives `research_pipeline_en.md` precedence on questions of method, so the document that wins arguments had become the stalest document in the repo.** Anyone opening it cold — supervisor, reviewer, future reader — would have read a plan that died a week earlier and a generation budget one third too large. 🔴 **Two further findings surfaced only because the file was finally read end-to-end:** (i) **open decision 4 had been satisfied on 2026-08-01 and left open for ten days** — the third instance of the same housekeeping failure after decisions 1 and 2, and the pattern is now named in STATUS rather than fixed a third time and forgotten; (ii) **Week-1 step 2's supervisor sign-off on `protocol.md` is recorded nowhere** and is now flagged for Sabbir. ⚠️ **`research_pipeline_bn.md` did NOT receive this pass**, so the two mirrors are out of sync — which line 8 of the English file forbids. Recorded here rather than left to be discovered. |
| 2026-08-11 | ⛔ **`research_pipeline_bn.md` is cited as a normative document and does not exist — plus a same-day self-correction of Claude's own claim about it** | Line 8 of `research_pipeline_en.md` has read, since v7: *"This file is the English mirror of `research_pipeline_bn.md` (v7). Both are normative; if they ever disagree, fix both."* The file is **absent from `docs/`, from the repo, and from git history**. Line 8 is struck and marked FALSE; the English file is declared the only normative pipeline pending **open decision 18** (write the mirror, or drop the bilingual-normative claim). | **Two failures, and the second is Claude's.** (1) The spec has been pointing at a second authority that cannot be opened, since v7, and it survived because *nobody ever tried to follow the reference.* A citation to a non-existent normative document is the same defect class as `guo2017calibration` being cited with no `.bib` entry, found hours earlier the same day — **both are references that were trusted rather than resolved.** (2) 🔴 **Claude's maintenance banner asserted the Bangla mirror existed and was merely "out of sync", from reading line 8 instead of the disk** — the exact failure CLAUDE.md's "do not invent" rule names, committed while writing a box about maintenance discipline. Caught within the hour, corrected in place with the wrong text struck rather than deleted, and **before Sabbir acted on it**. Recorded because a self-correction that leaves no trace is indistinguishable from never having erred, and this project's argument rests on that distinction. ⚠️ Recommendation on decision 18 is **(b) single normative file**: writing a 579-line Bangla mirror creates a second document to keep current, doubling the staleness surface this pass existed to reduce. The bilingual charter is Sabbir's, so the recommendation is offered, not taken. |
| 2026-08-11 | ✅ **Two Sabbir rulings recorded: (i) supervisor seal obtained; (ii) no Bangla normative mirror — decision 18 closed as option (b)** | (i) `protocol.md`'s signature line is filled: signed for Phases 1–3, sealed at commit `d8b1f5d`, on Sabbir's report *"sir sign dise"*, with his instruction that the signed copy need not be produced here. (ii) Line 8 of `research_pipeline_en.md` is struck; that file becomes the **sole normative pipeline** and `research_pipeline_bn.md` will not be written. | (i) **Recorded as a student report, explicitly labelled as such.** Every other claim in this document is verifiable against `git log --follow` and `results/` timestamps; this one is not, and the seal packet's entire argument is that its claims can be checked *without trusting anyone*. Logging the signature as though it were an auditable repo artifact would quietly undercut that argument, so the provenance is stated instead. It is not a weaker fact — it is a differently sourced one. (ii) Sabbir: *"bangla ar english to same e. dorkar ki bangla alada kore likhar."* 🎁 **The ruling is also the better engineering, which is why it is recorded as agreement rather than as concession:** one current file beats two where one is fictional, and writing a 579-line mirror would have doubled the very staleness surface the same day's maintenance pass existed to reduce. **Bangla remains the language of explanation** — Sabbir's standing request that methods sometimes be taught in Bangla is unaffected; what changes is only that no Bangla document is normative. **Week 1 of the execution checklist is now fully closed**, the last open item having been the sign-off in (i). |
| 2026-08-11 | ✅ **STANDING RULE from Sabbir: a hand-written constant is not acceptable — every decision number must carry a reason. Enforced by `src/common/check_constants.py`, not by memory** | Sabbir: *"hate likha thakle hbe na. karon thakte hobe."* Prompted by §4.2's Critic weight `0.6xVerifierA + 0.4xsymbolic`, which appears in the pipeline spec with **no derivation anywhere**. New checker tiers every numeric config constant and enforces only the first tier: **DECISION** (changes a verdict — must have a reason), **KNOB** (engineering default — warned, never enforced), **ASSERTION** (`expected_n`, `train_n`, the S0 claimed counts — the *opposite* of hand-set, they exist to fail loudly if the data moves, and are skipped). A reason counts as an inline comment, a comment block above, an explicit `# ref:` pointer, or the key appearing in `protocol.md` **outside the deviations log**. Final state: **114 constants carry a reason, 0 DECISION-tier are silently unjustified, 1 is openly flagged as unresolved.** | ⛔ **This row REPLACES an earlier version of itself, which overstated the finding, and the correction is the more useful record.** The first run reported **29 constants with "no reason anywhere"**. That was wrong for 28 of them. `strong_at_or_above: 0.45` is pre-registered in the RQ1-H section **with power computed before the run** (*"at n = 50, detecting 0.45 against 0.25"*); `dominated_at_or_above: 0.75` and `confounded_at_or_above: 0.65` are the boundaries of a three-outcome pre-committed table; `explained_at_or_above` / `partial_at_or_above` are RQ1-E Test C, already pinned by a test that fails if 10.0 moves. **The reasons existed and were good. The key names simply did not appear in the prose, so a key-name search could not see them.** 🔑 **The defect was LINKAGE, not absence — but linkage is a real defect**: a reader holding the config could not get from the number to the argument, and neither could the checker. Fixed by adding `# ref:` pointers naming the exact protocol section. 🔴 **Two loopholes were found in the checker itself, both within the hour, both the same shape.** (i) The audit note written into this deviations log **named the offending keys in order to report them as unjustified** — so on the next run the checker found those names in `protocol.md` and passed them. **Writing about the gap closed the check.** Fixed by cutting the deviations log out of the searched text. (ii) An inline `# NO RECORDED REASON` marker then counted as a reason for the same substring reason. Fixed with a separate **OPEN** tier, so that flagging a gap can never be the thing that hides it. **A checker that cannot distinguish prose *about* a reason from a reason certifies the exact defect it exists to catch.** ✅ **One genuine gap survives, and only one: `r1_fraction: 0.5` in `configs/s3_split.yaml`** — the sole decision constant in the repo with no source in `protocol.md` or the pipeline. An equal R1/R2 split is the obvious default and yields 2,162/2,163, but *obvious* is not a reason. ⚠️ **The split map is FROZEN (inviolable rule 3), so this cannot be revised — only explained.** Left for Sabbir and deliberately not back-filled by Claude. |
| 2026-08-11 | ✅ **Open decision 17 CLOSED — and the question itself was malformed, which is the finding** | §4.5's τ sweep moves from a **uniform 0.30→0.95 step-0.05 grid** to **quantiles of the observed score distribution**, reported on the **calibrated** scale. The calibrated-vs-uncalibrated question that decision 17 posed is **withdrawn as ill-posed**, not answered. Opens decision 19 (τ has no objective). | 🔴 **Claude wrote decision 17 and its premise was false.** It asserted that temperature scaling makes Verifier-A's output *"near-binary, so a τ sweep has almost no resolution"*, and offered (a) uncalibrated / (b) calibrated as alternatives. **They are the same alternative.** `mattei2026welltempered`: β>0 ⇒ βz is ordered exactly as z, so temperature scaling is **accuracy-preserving**; their Thm 5.1 / Cor 1 strengthen this into a characterisation — it is the **only** accuracy-preserving linear scaler, which is precisely why matrix scaling and Dirichlet calibration can move hard predictions and it cannot. A monotone map cannot move an item across a threshold, so every τ on the calibrated scale has an exact twin on the raw scale producing an identical PASS/FAIL set. ✅ **Checked against our own data rather than taken on the paper's word:** applying T = 0.10918 to `s3c_verifier_a_dev_predictions.csv` gives **0 rank inversions, 1 new tie, and 2 of 82 items saturated to exactly 1.0** — the theorem holds, with float saturation as the only leakage. 🔑 **The real defect was the GRID, and it is worse than decision 17 described.** On the spec's uniform grid the calibrated scores yield **5 distinct pass-set sizes against raw's 12**, and sit **flat at 28 items for τ = 0.30 through 0.65 — eight consecutive dead grid points**. Thresholds placed at the observed score values recover **81 operating points on either scale**. So the fix is arithmetic, not a choice of score. **Reported on the calibrated scale** because `kotte2026ucci` (Thm 1) show threshold policies on calibrated error probability are cost-optimal under stated assumptions, and because a τ that reads as a probability is interpretable in Ch.4. ⚠️ **Two warnings carried forward rather than absorbed.** (i) `kotte2026ucci` selected **isotonic regression over temperature scaling** precisely because temperature is *"constrained to a single-parameter monotone rescaling, which is too rigid"* (ECE 0.03 vs 0.08) — and our T = 0.109 is one parameter fitted in-sample on 82 rows. (ii) Their τ minimises an **explicit cost objective**; §4.5 names only *"first-pass 60–70%"*, a target rate. **A threshold cannot be optimal for an unstated objective**, so that becomes open decision 19 — the same defect class as the struck `0.6/0.4`: a number with a value and no criterion. |
| 2026-08-11 | 🔴 **Decision 19 quantified: the τ cost objective is DEGENERATE without a quality constraint, and §4.5's own grid may not reach §4.5's own target** | Sabbir: *"dekho paper e kivabe deya oita hishab kore koro"* — take `kotte2026ucci`'s formulation and compute it rather than describe it. `src/eval/tau_objective.py` does so against §4.2's actual loop. | **The loop's cost, written out:** Writer call per attempt, Reflector per FAIL except after the last (nothing left to feed), Researcher free because §4.2 makes it a deterministic tool-caller. With `q` = per-attempt pass rate and 3 attempts: **E[calls] = 1 + 2(1−q) + 2(1−q)²**, **P(accept) = 1 − (1−q)³**. Calls per accepted generation: **q=0.10 → 16.310, 0.30 → 5.145, 0.50 → 2.857, 0.65 → 2.032, 0.80 → 1.492, 0.99 → 1.020.** 🔑 **Monotonically decreasing, so the unconstrained minimum is q = 1, τ = 0 — the cheapest loop never rejects.** UCCI's Thm 1 proves threshold policies optimal *subject to* an accuracy constraint; **we adopted the objective and dropped the constraint**, which is why §4.5's *"first-pass 60–70%"* reads like an operating point but cannot be derived as one. It is a stand-in for a quality floor that was never stated. **The fix is not a number:** the floor must be measured by **Verifier-B, never Verifier-A** — A is inside the loop, and constraining the loop by its own judge is precisely the Goodhart collapse inviolable rule 6 exists to prevent. ⚠️ **Second finding, not looked for.** On the only score distribution in the repo (dev-82; labelled NOT A RESULT in the script, since `kapur2026length` show human text does not stand in for generated), the uniform 0.30–0.95 grid reaches pass-rates spanning only **0.06–0.38**, while quantile spacing spans **0.01–1.00**. **The spec's grid cannot reach the spec's 60–70% target on this distribution.** Whether that survives on generated text is unmeasured — but the grid and the target were plainly never checked against each other, and that check cost one script. |
| 2026-08-11 | ✅ **Decision 19 CLOSED: τ selection adopts `kotte2026ucci`'s procedure wholesale. §4.5's "first-pass 60–70%" is STRUCK** | τ is selected by constrained cost minimisation with the constraint bounded by two measured endpoints — **α_lo** (τ=0, Critic never rejects; = §5.1 row 1, zero-shot, 1 call) and **α_hi** (τ=1, all 3 attempts, best-of-3) — **both scored by Verifier-B, never Verifier-A**. Headline operating point τ\* = **argmax [quality(τ) − α_lo] / E[calls](τ)**. Full Pareto frontier reported regardless. Cost model and selection rule: `src/eval/tau_objective.py`. | ⚠️ **Provenance: Sabbir delegated — *"abar amar shiddhanto ki vai. tmk paper dekhte bolsi emnei nki. paper er moto kora lagbe."* The choice and reasoning are Claude's, endorsed not authored, as for decisions 12, 14 and 16.** He is also correcting a real failure: the previous pass computed the cost curve and then handed him a three-option menu, which is the opposite of "do it like the paper". **The forcing result, computed rather than asserted:** under §4.2's loop (**E[calls] = 1 + 2(1−q) + 2(1−q)²**, Researcher free because it makes no LLM call), calls-per-accepted is **monotonically decreasing** — 16.310 at q=0.10, 5.145 at 0.30, 2.857 at 0.50, 2.032 at 0.65, 1.020 at 0.99. **Minimising cost alone therefore selects q=1, τ=0: the cheapest loop is the one that never rejects anything.** UCCI's Thm 1 proves threshold policies optimal *subject to* an accuracy constraint; we had adopted the objective and dropped the constraint, which is exactly why "first-pass 60–70%" reads like an operating point and cannot be derived as one. 🔑 **The paper's constraint is not free-floating either** — *"a target accuracy τ in [α_s, α_ℓ]"*, bounded by the cheap and expensive systems' measured accuracies. Our two ends of τ **are** two ends of a cost/quality range we were already going to measure, so no new experiment is created. **The Verifier-B restriction is ours, not theirs:** UCCI has no in-loop/out-of-loop wall, and using Verifier-A to constrain a loop Verifier-A judges would be the Goodhart collapse rule 6 exists to prevent. ✅ **Why an argmax and not a fraction:** UCCI's 0.91 sits 74.1% up their achievable range — a deployment choice they were entitled to make. Adopting a fraction of our own would reintroduce precisely the hand-written constant this day was spent eliminating (see the `0.6/0.4` and `r1_fraction` rows above), so the headline point is defined by an argmax with nothing to choose. Synthetic check in the script: the rule selects an interior point at **67.1% of achievable gain**, close to UCCI's own 74.1% — the rule is not degenerate at either end. ⚠️ **`quality(τ)` cannot be computed yet** — it needs generations and Phase 4 has produced none. What is registered here is the **procedure, fixed before any number exists**, which is the only order in which it can be registered at all. |
| 2026-08-11 | ✅ **S4 pre-commitment written — Phase 4 is registered before `src/agents/` contains a line of code** | New section §"S4 pre-commitment" registers: `w` has no value and three pre-committed outcomes for its sensitivity curve; τ scoping (below); the 20-generation generator pilot's decision rule; the Researcher's retry contract; and `gave_up` reporting. **Rule 6 is restated as a code-level constraint** — Verifier-B may not be imported anywhere under `src/agents/`, enforced by a test rather than by intention. | **Written in the only order that makes a pre-registration mean anything: Phase 4 has produced no text, no score and no trace.** Index used: **alphaXiv** (Consensus quota exhausted to 1 Sep 2026), stated because *"searched a different index"* and *"did not search"* must not look alike. ⚠️ **The rule-6 restatement is not ceremonial.** The 2026-08-11 Verifier-B data-definition row records a wall that came one training run from collapsing through **ambiguity, not disagreement** — everyone read the sentence correctly and the code would not have. A constraint that lives only in prose has already failed once here. |
| 2026-08-11 | **§4.2's "a τ per axis level" is REPLACED by a hierarchical fit across the two levels — neither pooled nor split** | τ is estimated by **partial pooling** over the two axis levels, with the shrinkage **estimated from the within/between-level score-variance ratio, not chosen**. Global τ and the two per-level τ are reported as the limiting cases it interpolates. A two-sample permutation test on the per-level generated scores (5,000 shuffles, α = 0.05 — §RQ1-F's existing instrument and constants, adopted not reinvented) is reported **descriptively and is not a gate**. Decision 19's τ\* argmax is unaffected. | ⚠️ **Provenance: Sabbir delegated — *"research kore dekho konta vlo hoy"*. The choice and reasoning are Claude's, endorsed not authored, as for decisions 12, 14, 16 and 19.** 🔑 **The search moved the answer off BOTH options that were offered him, and that is the finding.** Claude had recommended a single global τ. `2605.14260` states a single pooled threshold *"can hide cross-group heterogeneity in score distributions and distort group-wise coverage"*; `2605.05562` — *marginal validity is not enough for subgroup reliability*; `2606.29403` and `2606.20115` independently reproduce pooled calibration masking subgroup undercoverage. **So the "conservative" option was not conservative.** The counterweight is in `2605.14260`'s own title — group-conditional thresholds cost calibration sample, and we have 30 dev-plots per level. `2607.24562` supplies the resolution: hierarchical partial pooling **degrades to global when the levels are indistinguishable and to per-level when they separate**, i.e. it is correct under the condition we cannot know in advance. 🔑 **Why the permutation test is deliberately not a gate:** at n = 30 per level it is underpowered, and a gate whose null verdict fires regardless of the truth is exactly the failure that forced RQ1-F's Gate 2 to be rewritten mid-protocol. **A non-significant result means *not detected*, never *equal*.** The hierarchical estimator needs no gate to be right, which is the whole argument for it. ⚠️ Estimating the shrinkage rather than picking it is what keeps this compliant with the 2026-08-11 standing rule; a hand-set pooling weight would be the same defect as `0.6/0.4`. |
| 2026-08-11 | **§4.4's 20-generation pilot gains a DECISION RULE; `TIE` is pre-committed as the expected outcome** | §4.4 specifies *"20-generation pilot → Llama vs Qwen"* — a budget with no rule for reading it. Registered: 10 dev-plots × 2 levels, byte-identical prompts, **not scored by Verifier-A**, **`TIE` as the pre-committed default**, a declared non-performance tie-break (lower cost / higher rate limit), and a **`NOT A RESULT`** banner in the style of `results/pilot_s35_idf.*`. Groq model IDs are read from the live catalogue with a retrieval date, never from memory. | **The same defect class as the struck `0.6/0.4` and the struck *"first-pass 60–70%"*: a procedure with a number and no criterion.** `2605.10405` treats best-model identification under a small evaluation budget as a statistical problem with a known failure mode rather than a matter of inspection. 🔑 **The forcing argument is our own data, not the citation:** S3.2 returned `TIE` across **seven arms × five seeds**, with the between-arm spread (0.0348) *smaller than one arm's own seed SD* (0.0391). **Expecting 20 generations to separate two models, when 70 runs could not separate seven, is not defensible** — so the tie-break is registered now rather than improvised at the point of looking at 20 outputs, which would be a preference wearing a result's clothes. **Not scored by Verifier-A** because pre-selecting the generator against the in-loop judge is a soft form of the evaluator–policy co-adaptation `wang2026hacking` name and rule 6 exists to prevent. ⚠️ **Bangla generation quality is registered as a live risk with citations rather than an assumption** — `2605.31483` (BenHalluEval, first systematic Bengali hallucination evaluation) and `2605.22487` (honorific failures in multilingual Bangla generation, where register is part of the construct the axis measures). **Abstracts only; neither is briefed to `base_papers_brief.md` depth, and that is stated rather than implied.** |
| 2026-08-11 | 🔧 **PROCESS DEFECT, self-reported: `docs/STATUS.md` contradicted itself about whether Phase 3 had run, and the stale half was the one a fresh session read first** | STATUS line 128 recorded the completed S3.3 run (Verifier-A 0.986555, Verifier-B `COMPETENT_EVALUATOR` 0.959666). The **step-11 row** and the **"Phase 3 real state" box** in the same file still read *"0 trained, 2 built"*, *"zero files in `results/`"* and **"Phase 4 cannot start."** Both artifacts and all four result files were committed in `0d2578d`. Corrected in this commit. | **Found because a fresh Phase 4 session read STATUS top-to-bottom, believed it, and reported Phase 4 as blocked — and Sabbir corrected it from memory: *"verifier A to ache maybe. artifacts e. check koro to."*** 🔴 **This is the fourth instance of the pattern STATUS itself already names** (open decisions 1, 2 and 4 were each satisfied and left open for days): *a row here is not closed by the work being done, only by someone closing it.* **What makes this instance worse than those three:** the contradiction was **inside the single file `CLAUDE.md` designates as the source of truth for "where are we"**, and the two halves disagreed on whether the next phase could begin at all. Decisions 1/2/4 were stale rows in a table people had stopped reading; this one actively instructed a new session to stop working. ⚠️ **The general lesson, recorded rather than fixed a fourth time and forgotten: a "verified facts" row and a "pipeline steps" row can be updated independently, so the file's own structure permits this failure.** Checking `results/` and `artifacts/` on disk is now the first action of any session that reads STATUS, because disk cannot go stale. |
| 2026-08-11 | 🔧 **`research_pipeline_en.md` §4.5 still carried the struck *"first-pass 60–70%"* as a live bullet, directly beneath the box that strikes it** | Decision 19 (earlier the same day) struck the target and recorded it in the §4.5 prose box. **The bullet *"Pick the operating point where first-attempt pass ≈ 60–70%"* survived four lines below it**, unmarked. Struck in place, not deleted, per the append-only convention, and noted in the file's MAINTENANCE STATE box. | **The strike was applied to the argument and not to the instruction.** A reader — supervisor, reviewer, or a fresh session — scanning §4.5's bullet list for the operating rule would have found the withdrawn target and no indication it was dead, and the box above it is long enough that skipping to the bullets is the likely reading path. 🔑 **Same shape as the two defects logged hours earlier**: `0.6/0.4` survived in the spec after its derivation was found not to exist, and line 8's Bangla mirror survived because nobody followed the reference. **All three are cases where the corrected text and the uncorrected text lived in the same file and only one was edited.** Recorded as a maintenance failure rather than a typo, because the pattern is now three-for-three and the cost of the next one lands on whoever trusts the spec. |
| 2026-08-11 | ✅ **Open decision 10 CLOSED — prompt parity is enforced BY CONSTRUCTION (shared template), not by audit** | §5.1 row 1's prompt and the loop's attempt-1 Writer prompt are emitted by **one template function**; row 1 is `render_prompt(exemplars=[], feedback=None)`. A test asserts byte-for-byte equality after stripping exemplars and feedback. Registered as §S4 decision 5. | ⚠️ **Provenance: Sabbir delegated — *"research kore dekho konta valo hoy erpor koro"*. Choice and reasoning are Claude's, endorsed not authored, as for decisions 12, 14, 16, 19 and the τ ruling.** 🔑 **Why this could not wait for Phase 5, where the row had been filed:** §5.1 row 1 **is α_lo**, the lower endpoint of decision 19's τ objective, so an under-specified row-1 prompt propagates into **τ\* itself** — not merely into the RQ2 headline. Huang et al. §5 document the artefact concretely (81.8 standard vs 75.1 self-corrected, once the requirement was stated up front). **An audit catches this only if someone remembers to look; a shared template makes the divergence unrepresentable**, and the literature says the artefact is the normal case rather than the exceptional one, so the defence should not rest on vigilance. 🎁 **Second finding, which changes what Ch.2 may claim rather than what the code does:** the recent sceptical literature — `2606.23196` (*When Does Intrinsic Self-Correction Help?*), `2606.13156` (*the Self-Correction Mirage*) — is scoped to **intrinsic** self-correction, a model revisiting its own answer *without external feedback*. **Ours is extrinsic by construction** (trained external verifier; Critic is not the Writer's model). So that body of work does not refute this design — **it describes the design this one was built to avoid**, and the thesis should say exactly that rather than either ignoring it or over-claiming against it. ⚠️ **The prompt-parity threat is NOT so scoped** — it applies to any loop compared against a single-call baseline, which is why it is closed structurally. `2604.22273` additionally frames refinement as having **stability thresholds** past which it degrades, which bears on §4.6's requirement that max-retry = 3 be *earned* by the per-iteration curves rather than assumed. **Abstracts only, all three.** |
| 2026-08-11 | **§4.6's failure taxonomy is EXTENDED before coding starts: a `register_or_honorific` category is added, plus an `other` bucket whose rate is reported** | §4.6 fixes four categories (*wrong sentiment / too short / off-topic / template repeat*). Registered as §S4 decision 6: those four **plus `register_or_honorific` plus `other`**; the `other` rate is reported as a number with **no threshold attached**; **any category added after seeing the failures is labelled `post hoc` by name in the paper**; and **double-coding with an agreement figure is required**. | ⚠️ **Provenance: delegated as above; Claude's reasoning.** **The gap was found by the Phase 4 literature pass, not by reading §4.6.** `axiv2605_22487_banglahonorific` documents honorific failures in multilingual Bangla generation — and register is not incidental to this thesis, it is **partly the construct itself**: S2b's register probe separated the two corpora on first-person pronouns, exclamation marks and comma-runs, and that probe is why the corpus is known to be two corpora at all. **A taxonomy that cannot name a register failure cannot describe our most likely failure mode.** `2604.18490` (*LQM*) supplies the general argument — MQM and comparable schemes are **language-agnostic and miss language-specific phenomena** — and `2606.10765` (*ArabiGEE*) is precedent for a language-specific error taxonomy in a non-English language; `2608.03966` notes comparable resources *"often assign a binary label"*, favouring a fine-grained scheme. 🔑 **Why no threshold on the `other` rate:** a cutoff would be a constant with no criterion, the exact defect removed on 2026-08-11. The number is evidence about the taxonomy's adequacy and is left to speak for itself. 🔴 **Who does the double-coding is Sabbir's and is deliberately NOT assumed here** — G-300's annotator time is on record as exhausted, and **Claude must not be the sole coder of failures produced by a system Claude built.** Flagged as an open resource question rather than quietly resolved by whoever is available. **Abstracts only, all three citations.** |
| 2026-08-11 | 🔴 **The RAG index SS4.2 assumes did not exist, in any form. Step 16's real prerequisite, found only when the component was about to be written** | `src/agents/build_index.py` + `configs/s4_index.yaml` + `tests/test_s4_index.py` are added. SS4.2 specifies a Researcher that "queries ChromaDB, top-10, within same persona label, **R1 index only**" — and there was **no index, no config for one, and no script**. The component contract was written as though the index were a given. **Dry-run resolves 886 R1 region-A rows (levels 534/352), digest `85fc2d7d7ad3281b...`, zero R2 ids, zero Gold-300 ids.** | **Nobody had noticed because the contract reads like a description of an existing system.** Recorded as a spec gap rather than a task, because the same shape could hide elsewhere in SS4: a contract that names a resource does not create it. 🔑 **Rules 4 and 5 are implemented as REFUSALS, checked twice.** `split_access` is asked for a **role**, never a partition — so a copy-pasted config cannot name R2 — and `assert_rag_contract` then re-checks the resolved ids against the split map **independently**, before a single vector is written. Two checks of one wall cost nothing and fail differently: the frozen split (inviolable rule 3) is a *promise*, and the second check is a *mechanism*. Precedent for insisting on the difference: the 2026-08-11 Verifier-B row, where a wall came one training run from collapsing through ambiguity that every human reader resolved correctly. ⚠️ **REGISTERED CHOICE, stated because it is a judgement call and not an obvious one: the 82 dev rows ARE in the index** (`hold_out_dev=False`, 886 = 804 + 82). The index is not a fitted object — nothing is estimated from those rows here — and the objects the τ sweep operates on are **dev-PLOTS** (Bangla film synopses), not dev reviews, so no threshold is tuned on anything the index supplies. **The residue, named rather than buried:** dev reviews may appear as Writer exemplars while also being the slice Verifier-A's temperature was fitted on. That is disclosed as a sixth use of the 82-row slice under the 2026-08-11 dev-reuse row. Reverting to `hold_out_dev=True` costs 82 of 886 exemplars and is available if the disclosure is judged insufficient. 🔑 **The manifest, not the index, is the reviewable artifact** — an index is a binary blob whose contents cannot be read off a diff, so `id_digest` (SHA-256 over sorted ids, order-independent, membership-sensitive, and **tested to be both**) is what a rebuild's identity claim is checked against. |
| 2026-08-11 | ✅ **Inviolable rule 6 becomes machine-checkable: `tests/test_s4_index.py` AST-scans `src/agents/` for any path to Verifier-B** | Rule 6 was enforced by everyone remembering it. A test now walks every import node in the loop package — **including imports inside function bodies**, where a late `from src.verifier...` would hide from a top-of-file reading — and fails if `verifier_b` or `train_verifier_b` is reachable. **A companion test proves the scanner can actually detect such an import**, so the passing verdict means something. | **Rule 6 is the load-bearing wall: "Verifier-B never enters the loop. This wall *is* the Goodhart test — collapsing it makes RQ5 meaningless."** A wall enforced by memory has already nearly failed once here (2026-08-11, Verifier-B's data definition). 🔑 **Why AST and not a grep:** a substring search passes a file containing `# never import verifier_b` and fails a file that mentions it in a docstring — **wrong in both directions**. The recorded precedent is `check_constants.py`'s two loopholes from earlier the same day, where a checker could not distinguish prose *about* a rule from the rule, and **writing about the gap closed the check**. 🔑 **Why the reachability test has a twin:** RQ1-F's Gate 2 had to be rewritten mid-protocol when its null verdict turned out unreachable by construction. **A guard whose failure branch cannot fire certifies nothing**, so the failure branch is exercised on a synthetic import. That pattern is now standard in this repo rather than a response to one incident. |
| 2026-08-11 | 🔴 **The axis definition's "what it is NOT" section is REMOVED before any generation — negative constraints are a documented hazard, and ours named the two confounds we most need absent** | `docs/axis_definition.md` §3's third block listed three negative constraints (*not sentiment direction, not length, not good Bangla*). All three are struck and **rewritten positively**: *"both praise and criticism are normal at either level"*, *"short and long comments both occur"*. No guardrail is dropped; each is restated in a form the literature says a model can act on. | ⚠️ **Provenance: Sabbir delegated — *"tmi research kore dekho ki valo hoy"*. Reading is Claude's, endorsed not authored.** Index: **alphaXiv**. `2601.08070` (*Semantic Gravity Wells: Why Negative Constraints Backfire*) studies instructions of literally the form *"do not use word X"* and reports they misfire; `2605.03052` and `2606.18922` report negation as a known weak point, so the constraint may not land even where it does not backfire. 🔑 **The removed lines named `length` and `sentiment` — precisely the two confounds this design must keep out of generated text** (`length_auc` **0.6764 → LENGTH_CONFOUNDED`; level 0 is 66% positive against level 1's 74% negative). A prompt that names a confound in order to forbid it may make it *more* available, which would have manufactured the exact artefact RQ1-H's length-matched design was built to exclude. 🔴 **The assumption that broke was Claude's own, written in the same file two hours earlier:** §3 justified reusing the G-300 wording on the ground that RQ1-H validated that instrument. **RQ1-H validated it on humans.** Negative framing is unremarkable for an annotator reading a guideline and is a documented hazard for a model reading a prompt — **the validation transfers to the construct, not to the prompt format**, and the two were treated as one. Sixth entry in CLAUDE.md's search-first table, and the first where the search corrected a document written by the same search-first process. |
| 2026-08-11 | **Pre-registered diagnostic: did the Writer learn specificity, or did it learn length?** | Registered in `docs/axis_definition.md` §3c before any generation exists. **Mean generated length by target level is reported beside every axis-level result.** If level-1 generations are shorter than level-0 by an amount comparable to the corpus gap (**13.12 → 8.85** mean words), the loop's axis control **may not be claimed as specificity control** without a length-matched check. If the gap is absent or reversed while Verifier-B still separates the levels, that is **positive evidence the construct transferred rather than the confound**. | **A risk no component owns, surfaced by `2605.20382` (*Instruction-Induction Conflict*): instruction-following and pattern-completion can conflict.** §4.2's Writer prompt carries **both** the definition (instruction) **and 10 retrieved exemplars from the target level** (pattern) — and the level-1 exemplars *are* systematically shorter, as a fact about the corpus rather than a choice. **So the model can satisfy the exemplars by copying length while ignoring the construct, and the Critic would partly reward it, because `length_auc` is 0.6764.** Neither the Researcher (which retrieves correctly), the Writer (which follows its prompt), nor the Critic (which scores as specified) is at fault — which is exactly why it needed registering as a diagnostic rather than assigning as a bug. 🎁 **Both outcomes are informative and both are pre-committed**, so this cannot become a post-hoc explanation of whichever result appears. |
| 2026-08-11 | **Axis-definition language pass — register anchored positively, a swap test added, and one question recorded as NOT settled** | `docs/axis_definition.md` §3's Bangla block is rewritten: register anchored as *"সাধারণ দর্শকের চলিত বাংলা — যেভাবে ফেসবুক বা ইউটিউবের মন্তব্যে মানুষ লেখেন"*; each level ends with a **swap test** (level 0 *"can be pasted under almost any film and nothing changes"*, level 1 *"stops working under a different film"*); prose moved to চলিত throughout. | ⚠️ **Provenance: Sabbir delegated — *"vasha aro valo koro research kore"*. Reading is Claude's.** Index: alphaXiv. 🔴 **The honest negative first, because it is the part most easily buried: the question I had silently assumed away — whether the definition should be in Bangla or English at all — came back THIN.** The cross-lingual searches returned alignment, steering and transfer work, and nothing settling whether native-language or English instructions produce better *generation* in a low-resource target language. **The definition stays in Bangla on the weaker, inferential ground that a Bangla instruction is less likely to induce translationese — that is an inference, not a finding, and is labelled so.** *"Nothing recent exists"* and *"nothing recent was looked for"* are different facts that look identical in a bibliography. **What the search did establish is about the output:** `2410.15956` (*Do LLMs Have an English Accent?*) reports English-centric bias in the *naturalness* of non-English output; `2503.04369` (*Lost in Literalism*) documents translationese as trained-in; and `2603.15949` (**BanglaSocialBench**) is our setting rather than an analogy — sociopragmatic alignment in **Bangladeshi social interaction**, finding that *"fluency alone does not guarantee socially appropriate language use"* in high-context languages. 🔑 **The swap test is the substantive improvement: a concrete operation a model can apply, replacing a property it has to interpret — and it states the construct without naming length or sentiment**, which is what the gravity-wells row forbids. ⚠️ **The venue naming rests on the collector's recall-based account** (STATUS, medium confidence; no venue column exists) and is used as a **register anchor, never as a provenance claim**. 🎁 **A design strength stated rather than assumed: the register is carried mostly by the 10 retrieved real exemplars, not by this text.** Where the §3c row warns that pattern-completion may *fight* the instruction on length, here it *helps* — same mechanism, opposite sign, both now on the record. |
| 2026-08-11 | ✅ **Prompt language becomes a PRE-REGISTERED PILOT FACTOR, not a decision — and the criterion is a failure rate, not a quality score** | Sabbir: *"english prompt hole valo bujhbe maybe LLM. lagle bangla add korba okhane akri."* Registered in `docs/axis_definition.md` §3e: the axis definition is rendered in **two arms from one source** — Bangla (incumbent) and English-instructions/Bangla-content. **Invariant in both:** the 10 retrieved exemplars are real Bangla comments, the plot is Bangla, the output must be Bangla. Decision rule: **`LANG_CONFUSION`** fires if an arm emits non-Bangla or Bangla–English code-mixed output beyond the corpus's own baseline (`has_latin` = **0.09% / 0.00%** in region A, i.e. effectively zero — any Latin script is signal). Clean arm wins; **if neither confuses, the Bangla arm is retained as incumbent and NO quality claim is made.** | 🔴 **First, a methodological correction against myself: §3d recorded this question as "thin" after ONE call with ONE phrasing.** Re-worded, the field is not thin at all. **The "thin" verdict was a property of my query, not of the literature** — and CLAUDE.md's mechanics section says exactly this ("do not treat one call as the search"), which I quoted and then violated. A thin result is precisely what silently closes a question. **Sabbir is largely right:** `2502.15603` (DeepMind/Oxford) — LLMs *"make key decisions in a representation space closest to English"*; `2402.10588` (EPFL) — English as internal **pivot**, and our generator arm is **Llama**; `2504.11833` — *"often perform better when tasks are presented in English"*; `2605.27649` studies our exact configuration (instruction, content and response languages not coinciding). **And three findings stop it being a free swap.** (i) `2606.08994`: **language confusion** when generating non-English — an English instruction block raises the chance the Writer answers in English or a mix, which for us is **not a quality dip but a void generation**. (ii) `2606.19668` + `2506.14012`: mixing languages *"frequently degrades performance relative to source- or target-language monolingual"* — **so the *"lagle bangla add korba"* half of the suggestion is the option with the LEAST support**; if the prompt goes English the split must be clean and structural, instructions English / content Bangla. (iii) `2603.25015` (*Imperative Interference*) is decisive against deciding: *"instructions that cooperate in English **compete** in Spanish, with the same semantic content, but opposite interaction topology."* §4.2's Writer prompt carries **four** instruction sources — definition, exemplars, plot, and on retry the feedback — so switching language may change **how they interact**, not merely how well each is understood, and nothing in the literature says which way for Bangla. `2604.16937` adds that effectiveness *varies* across ten languages, so there is no universal answer to import. 🔑 **Why this is decidable at n = 20 when model choice is not:** a quality difference between prompt languages needs hundreds of generations — the same power problem that makes `TIE` the registered default for Llama-vs-Qwen. **Language confusion is a binary with a near-zero corpus baseline and a large expected gap, so it is visible immediately.** The retain-the-incumbent rule is registered **now** so it cannot be reasoned to after the outputs are read. |
| 2026-08-11 | ⛔ **FORCED DEVIATION: the Researcher does NOT extract plot key-phrases. It embeds the whole synopsis** | §4.2 specifies *"ChromaDB query from plot **key-phrases**"*. `src/agents/researcher.py` instead queries with the LaBSE embedding of the full plot text. | **Both routes to key-phrases are closed, and neither closure is a preference.** (i) TF-IDF / IDF-based keyphrase extraction is **inviolable rule 7** territory, and the amendment packet is unsigned. (ii) An LLM call would make the Researcher generative — breaking its own contract, breaking §4.0's identity sentence (*"2 of 4 components make no LLM calls"*), and **adding an uncounted call to E[calls]**, which silently invalidates decision 19's τ\* since the cost model charges this component zero. Dense retrieval over the whole synopsis is the only route consistent with both, and it is what LaBSE exists for. ⚠️ **Known risk recorded rather than hidden — a GRANULARITY MISMATCH:** the plots are multi-sentence synopses, the indexed reviews average **~8 words**. Embedding a long document to retrieve very short ones is not what either length is ideal for, and retrieval may be weak. **§4.2 already requires exemplar overlap logged per attempt, and that log is the instrument that will show it** — so this is measurable, not merely acknowledged, and the §5.1b routing ablation is where it surfaces. |
| 2026-08-11 | **The axis-level filter is applied INSIDE the Chroma query, not by post-filtering** | `collection.query(..., where={"axis_level": level})` rather than fetching top-k and dropping the wrong level afterwards. | Post-filtering would return **fewer than 10 exemplars** whenever the unfiltered top-10 straddled both levels, so the Writer's prompt would vary in length between calls **for reasons unrelated to the plot or the level**. §4.2 fixes top-10; a prompt that is sometimes top-6 is a different prompt, and the variation would land inside the generations without appearing in any config. Small choice, recorded because it is invisible in the output and would be untraceable later. |
| 2026-08-11 | 🔴 **§4.4's pilot pair "Llama vs Qwen" is NOT instantiable as written: Qwen on Groq is a PREVIEW model. The pair is re-registered as Llama vs GPT-OSS, both Production** | §4.4 fixes a *"20-generation pilot → Llama vs Qwen"*. Read from the live catalogue (`console.groq.com/docs/models.md`, retrieved 2026-08-11): **`qwen/qwen3.6-27b` is listed under Preview Models**, which Groq's own note defines as *"intended for evaluation purposes only and should not be used in production environments as they may be discontinued at short notice."* Re-registered pair: **`llama-3.3-70b-versatile` vs `openai/gpt-oss-20b`**, both **Production**. `llama-3.1-8b-instant` is retained as the cheap fallback if throughput binds. | **A thesis experiment is exactly the case Groq's warning excludes.** §5.1 is 1,440 generations per language and Phase 5 runs over weeks; a model withdrawn *"at short notice"* mid-experiment would leave a partially-completed condition that **cannot be finished and cannot be reproduced** — and reproducibility is the one property this repo is organised around. Preview status is also a **provenance** problem: the appendix must name the generator, and naming a model a reader cannot access is the same defect class as `research_pipeline_bn.md` being cited and not existing. ⚠️ **A search-result discrepancy, recorded because it is the reason the rule exists.** A web search asserted that `llama-3.1-8b-instant` and `llama-3.3-70b-versatile` were **deprecated on 2026-06-17**. **The authoritative Groq docs list both as current Production models.** The secondary source was wrong, or stale, and had it been trusted the pilot would have been rebuilt around a false premise. §S4 decision 3 already required model IDs to be *"read from the live catalogue with a retrieval date, never from memory"* — this extends to *never from a search summary either*. 🔑 **What does NOT change:** the pilot's decision rule, its pre-committed `TIE` default, the declared non-performance tie-break, and the `NOT A RESULT` banner. Only the identity of the two arms moves, and it moves for a reproducibility reason rather than a quality one — **no claim is made that GPT-OSS is better than Qwen at Bangla, and none can be, since nothing was measured.** |
| 2026-08-11 | ✅ **§4.4's "Groq primary, Gemini secondary on a subset" is CONFIRMED by measured rate limits rather than left as an assumption** | Free-tier throughput, retrieved 2026-08-11: **Groq** 30 RPM / **6,000 TPM** / 14,400 RPD; **Gemini** 2.5 Flash-Lite 15 RPM / **1,000 RPD**, Flash 10 RPM / 250 RPD, Pro 5 RPM / 100 RPD, 250K TPM shared. Against our measured prompt size (**~2,416 chars** = ~600–1,200 tokens; synopsis 695 + ten exemplars 640 + definition 1,079), Groq is **token-bound at ~5 calls/min ≈ 7,200/day** and Gemini Flash-Lite is **request-bound at 1,000/day**. | **Groq is ~7× the free-tier throughput for this workload, and Gemini's per-day caps make it unusable for volume and perfectly suited to a subset cross-check — which is what §4.4 already specified.** The spec is confirmed rather than changed, and that is worth logging: a check that changes nothing is still evidence, and silently discarding it hides the check. ⚠️ **The token estimate is a RANGE, not a number, and the reason is our own gap:** Bangla tokenizer fertility is an *unmeasured covariate* in this very pipeline (§1.2 lists it as a deliverable). 2 chars/token gives ~1,200 tokens, 4 gives ~600. **The fertility measurement would convert this estimate into a figure**, and it is now flagged as blocking any firm runtime plan. 🔴 **Two consequences that bind on the code, not on the plan.** (i) At ~5 calls/min the full Phase 5 (~8–10k calls including retries and Reflector calls) is **~30 hours of wall clock** on the free tier, so the Writer **must** implement 429 backoff and **append each generation to JSONL as it completes** — a run that cannot resume will lose hours, which is precisely how S3.2 attempt 1 lost ~4 GPU-hours at arm 6 of 7. (ii) The Developer plan raises Groq to **250K TPM / 1K RPM** (~40×) at zero minimum spend; **that is Sabbir's call and is offered, not taken.** |
| 2026-08-11 | 🔴 **PHASE 4 GENERATIONS ARE NOT REPRODUCIBLE BY RE-RUNNING, whatever seed is logged. The archived generations become the reproducibility artifact, and Ch.5 must say so** | §4.2 says *"temp 0.8, top_p 0.9, seed logged"*, which reads as though logging the seed makes a run repeatable. It does not, for a hosted API. **Registered here:** the seed is still logged, but **the JSONL trace of every generation is the reproducibility guarantee**, not the seed; the Writer appends each generation as it completes; and the appendix states that Phase 4 results are **replicable in distribution, not reproducible bit-for-bit.** | **Searched before writing the Writer, per the standing instruction, and it changed the artifact's status rather than a parameter.** `2601.17768` (LLM-42, UW/Microsoft): *"the same prompt may yield different outputs across different runs… this non-determinism arises from floating-point non-associativity combined with **dynamic batching**."* 🔑 **Dynamic batching means the batch composition depends on OTHER TENANTS' TRAFFIC on Groq's servers — a variable we do not control, cannot record, and cannot hold fixed.** `2604.22411` closes the obvious escape: *"even when decoding with temperature T = 0, LLMs can produce divergent outputs for identical inputs"* — so dropping to greedy buys nothing. `2605.19537` names the inference **backend** as a silent hyperparameter affecting reproducibility, which is **the exact parallel of `coakley2022environment`** (>6 pp from environment alone) that this project already relies on for the *training* side; the same argument now applies to inference, on hardware we do not own. `2602.14349` supplies the empirical companion across six models, four temperatures and ten runs — this is not a corner case. ⚠️ **Why this matters more here than in most projects:** inviolable rule 2 fixes a global seed, the splits are frozen, every result carries a provenance stamp, and the repo's whole argument is that its numbers can be re-derived. **Phase 4 is the first step where that guarantee genuinely cannot be extended**, and the honest move is to say which weaker guarantee replaces it rather than to let rule 2's presence imply the stronger one. 🎁 **The design consequence is free, because we were already doing it for another reason:** §4.4's JSONL trace was specified as the substrate for the failure taxonomy and dynamics report. It is now *also* the reproducibility artifact — a reviewer re-runs nothing and inspects the archived generations instead. **A trace that cannot be regenerated must never be deleted**, which upgrades it from an analysis convenience to a primary artifact. |
| 2026-08-11 | **§4.2's temp 0.8 / top_p 0.9 is RETAINED unchanged — and recorded as conventional-but-unTUNED, with the field having moved past it** | No change to the values. What changes is what may be claimed about them: they were **fixed by the protocol and never optimised**, and the thesis says so rather than implying a choice was made. §5.1b's retry schedule 0.8→0.9→1.0 likewise stays an ablation and is not baked in. | **A search that changed nothing is still evidence, and discarding it silently would hide the check.** `2408.13586` (Mannheim/MPI-INF/CISPA) is the standard reference for selecting a sampling method and parameter for open-ended generation — our pair is conventional against it. 🔴 **But `2407.01082` (min-p, Apart Research) criticises top-p directly** and proposes min-p for creative-yet-coherent output, i.e. the field has moved past the setting §4.2 fixes. **Recorded as a limitation, not adopted, for two independent reasons: min-p is not exposed by the Groq chat-completions API, so it is not a free choice; and changing the decoder would change a pre-registered condition after the fact.** `2602.18292` supplies the framing for Ch.5 — decoding is still *"treated as a heuristic knob-tuning exercise"* — which places our unTUNED decoder as the field's normal practice rather than as our idiosyncrasy, while still being a real limitation. ⚠️ **Related and already registered:** `2606.12234`'s effectiveness–fluency trade-off means pushing axis control harder may cost fluency, and the §3c length diagnostic is where that would first show. |
| 2026-08-11 | **Axis definition softened from an ABSOLUTE criterion to a prototype + comparative test, after the rendered prompt was read against real retrieved exemplars** | §3's level-0 text read *"ছবির কোনো একটা জিনিসের নাম **ওঠে না**"* / *"it never names any particular thing"*. Replaced by *"নাম উঠতেও পারে — কিন্তু নাম করেই থেমে যায়"* / *"it may even name something, but it stops at the naming and goes no further"*. The swap test is unchanged. | ⚠️ **Provenance: Sabbir delegated — *"dekho research kore jeta vlo hoy koro"*. Reasoning is Claude's.** 🔴 **Found by reading the dry-run's real retrieved exemplars, not by any test.** Among the ten level-0 exemplars retrieved for BN001: *"এই সিনেমা তে দুজন অভিনয় করলেন, **রূপা গঙ্গোপাধ্যায়** আর **সুমন্ত মুখোপাধ্যায়**"* and *"শ্রদ্ধেয় **সৌমিত্র চট্টোপাধ্যায়ের** অপরূপ অভিনয়"* — both name people, which the definition said level 0 does not do. **The model was being given an absolute rule and then shown ten examples, several of which break it** — instruction-versus-pattern conflict (`2605.20382`) in its sharpest form. 🔑 **The defect was in the definition's wording, not in the cut.** `cluster_k2` is a line through a continuum (silhouette 0.053, HDBSCAN 100% noise), so mixed membership is expected and is already the registered reading. **And RQ1-H validated the construct COMPARATIVELY** — Gate B is length-matched pairs asking which *"goes into more specific detail about the film"*, 34/40 against 0.50 chance. **An absolute rule was therefore never what was validated.** ✅ `2602.08033` supplies the shape: combining comparative and rating-style judgements beats either alone — so the fix is prototype description **plus** the swap test, not one replacing the other. This also sits beside `kiritchenko2017`, whose same lesson already cost this project a failed G-300 round. ⛔ **A false start, recorded because it nearly became a finding:** Claude first computed a keyword proxy (*does the review contain অভিনয়/গান/গল্প…?*) and got **21.6% vs 22.5% — 0.9 pp**, and read it as the exemplars contradicting the definition. **That inference was wrong.** The proxy is an *absolute* test of a construct validated *comparatively*; *"অভিনয় ভালো"* contains the word and is not specific. **The proxy is uninformative, not contradictory**, and the 0.9 pp may not be quoted as evidence about the cut. |
| 2026-08-11 | ✅ **Retrieval is level-conditioned exemplar sampling, NOT plot-relevant retrieval — and it cannot be otherwise. §5.1b's routing ablation is pre-registered to find no effect** | The dry-run's retrieval for BN001 (*অংশুমান এমবিএ*, two MBA students) returned comments about শাকিব খান, উত্তম কুমার and ময়নামতির সংসার. **Not a bug.** `CLAUDE.md` states the corpus has **no movie-title column**, so the reviews concern other, unknown films; **no plot-relevant exemplar exists to be found.** Registered: the exemplars supply **register and level**, not content. **Pre-committed prediction: §5.1b's routing ablation (disable re-retrieval on retry) will find no meaningful difference**, and if it does, that difference needs explaining rather than celebrating. | **This was foreseeable from a fact already written in `CLAUDE.md` and was not foreseen** — the Researcher was built, its granularity mismatch was logged as a *risk*, and only reading ten actual retrieved comments made it concrete. 🔑 **What the retrieval can and cannot contribute is now stated rather than assumed:** it filters to the target level and supplies ten real Bangla comments in the corpus's own register — which `2410.15956` (English accent) and `2603.15949` (BanglaSocialBench) make a real contribution — and it cannot supply anything about *this film*. ✅ **The exemplar block survives the impurity finding, and the reason is cited rather than hoped:** `2202.12837` finds ground-truth labels in demonstrations matter far less than the label space, input distribution and format. ⚠️ **With one boundary stated explicitly because a reader will notice the surface match:** `2605.08295` reports HOMOGENEOUS demonstration labels collapse accuracy to ≤12%, and our block is homogeneous by design (§4.2 retrieves within the target level). **That finding is about classification, where homogeneity destroys the decision; ours is generation with no labels attached, where homogeneity IS the conditioning signal.** ⚠️ `2303.03846` adds a live consideration for the pilot rather than a preference: larger models override in-context semantic priors and smaller ones do not, and our two arms differ ~3.5× in parameters — **so the two may respond differently to impure exemplars, which is a reason the pilot exists.** |
| 2026-08-11 | 🔴 **NEW REGISTERED CHECK: verbatim and near-verbatim copying of retrieved exemplars. `src/eval/copy_check.py`** | The pilot's first run emitted *"বাংলা সিনেমার মধ্যে ভালো একটা সিনেমা।"* for BN016 at level 0 — **`bn_0230`, exactly**, and one of the ten exemplars in that very prompt. Registered: copy statistics are reported **beside** every Phase 4/5 quality number, split by **level** and by **whether the match is to the exemplars shown or to unrelated corpus reviews**. **No threshold is applied** — the distribution is the report. | 🔑 **A copied exemplar passes the Critic BY CONSTRUCTION.** Verifier-A was trained on exactly these reviews, so **a real corpus review is the highest-scoring thing the loop can emit.** The system could therefore report an excellent first-attempt pass rate, a healthy τ frontier and strong §5.4 realism **while doing retrieval — every one of those numbers measuring the corpus against itself.** ⚠️ **Close to RQ5's Goodhart test and NOT the same thing, so they are reported separately:** gaming exploits the verifier's blind spots; **copying bypasses generation entirely.** Both inflate the same metrics, and merging them would let either explain the other. 🔑 **Why exact matching is not enough, stated before it fails rather than after:** a model has no reason to copy exactly rather than approximately, so the check is **token Jaccard against the exemplars actually shown in that prompt** — resembling one of the ten it was just given is the failure mode, while resembling some unrelated review is a property of a small formulaic domain and is reported for contrast. **No cutoff is set**, because a cutoff here would be a decision constant with no criterion. ⛔ **Predicted before Phase 5 rather than discovered in it: copying should concentrate at LEVEL 0**, where short formulaic comments are easiest to echo. If it does not, that is informative and needs explaining. |
| 2026-08-11 | 🔴 **BANGLA TOKENIZER FERTILITY MEASURED — 0.93 chars/token — and it changes the Phase 5 budget by an order of magnitude** | §1.2 lists tokenizer fertility as a covariate to be measured and it had never been. Measured from the pilot's first **27** generations: **3,434 prompt chars → 3,710 prompt tokens = 0.93 chars per token**, i.e. **roughly one token per Bangla character**. Mean **3,882 total tokens per call**. The Writer's pacer assumed 2.5 chars/token and therefore **under-estimated spend by 2.7×**, which is why it could not keep the run inside the budget. `CHARS_PER_TOKEN` is now the measured value and the per-minute limit is **read from `x-ratelimit-limit-tokens`** rather than hard-coded. | **The covariate was on the deliverables list, is cheap to measure, and blocked a plan nobody could cost until it was measured.** 🔴 **The consequence is not a tuning detail.** At ~3,900 tokens per generation: the **80-call pilot is ~312,000 tokens**, and the Groq free tier stopped this account at **~104,800** — hence the 2,759-second (46-minute) `Retry-After`, which the per-minute headers show was *not* a per-minute limit (`limit-tokens` **12,000**, `remaining-tokens` **12,000**, `remaining-requests` **999/1000** — the minute budget was untouched). **So the pilot alone needs about three days of free-tier daily allowance.** Extrapolated to §5.1's **1,440 generations per language**, Phase 5 is **~5.6M tokens for Bangla alone** — on the order of **two months** of free-tier daily budget, before the English arm, before retries, and before the Reflector's calls. **Free tier is not a viable substrate for this experiment, and that is now a measured statement rather than an impression.** 🎁 **An unanticipated finding that bears on a live pre-registered decision:** the two prompt-language arms have very different costs — **arm `bn` averages 4,010 prompt tokens against arm `en`'s 2,852, i.e. the English-instruction arm is ~29% cheaper**, because English instructions tokenise efficiently and Bangla does not. ⚠️ **This may NOT be used to choose the arm.** `axis_definition.md` §3e registers the criterion as `LANG_CONFUSION`, a failure rate, and cost is not a quality argument — but it is a real operational difference, it was not anticipated by anyone, and it is recorded here so that it is on the record *before* the arms are compared rather than discovered as a convenient reason afterwards. |
| 2026-08-12 | 🔴 **Generation moves OFF the hosted API onto our own GPU, and the pilot arms are re-registered as `gemma-3-1b-it` vs `TigerLLM-1B-it`** | `src/agents/local_writer.py`, `configs/s4_pilot_local.yaml`, `notebooks/s4_pilot_kaggle.ipynb`. Arms: **A = `google/gemma-3-1b-it`** (general multilingual), **B = `md-nishat-008/TigerLLM-1B-it`** (Bangla-adapted). Batch size **8**, fixed and recorded as provenance. | **The immediate cause is budget** — Bangla costs ~0.93 chars/token, Phase 5 is ~10M tokens, and no free API supplies that (eight checked). **That is recorded as the cause, because a scope change driven by cost must not be presented as a methodological insight.** 🎁 **But the change improves the methodology, and that is not a rationalisation.** `writer.py` had to concede *"replicable in distribution, not reproducible bit-for-bit"* because `2601.17768` traces API non-determinism to floating-point non-associativity **combined with dynamic batching over other tenants' traffic** — a variable we cannot control, record, or hold fixed. **Locally we choose the batch, set the seed and own the stack**, so the concession narrows to GPU reduction order alone, and the recorded environment makes even that checkable. For a repo whose whole argument is that its numbers can be re-derived, this returns Phase 4 inside that argument. ⚠️ **Batch size is therefore PROVENANCE, not a knob**: it fixes the order of floating-point reductions and may not vary within a comparison. 🔑 **The arms are a strictly better comparison than the ones they replace.** Verified from each model's own `config.json` — **not from the paper, not from memory** — both are `Gemma3ForCausalLM`, hidden 1152, 26 layers, vocab 262144: **identical architecture and size, so Bangla adaptation is the only variable.** The struck pair (`llama-3.3-70b` vs `gpt-oss-20b`) differed in architecture, size and training data simultaneously and **could not have attributed any difference it found.** The new contrast also sits on the thesis's own question — is external verification needed in a low-resource language, or does a language-adapted model suffice? — instead of being a model beauty contest. ⛔ **A provenance defect in the source, recorded because it changes what may be cited:** arXiv 2503.10995 (TigerLLM) states its 1B is built on **LLaMA-3.2** and its 9B on **Gemma-2**; the uploaded weights are **Gemma-3** for both, and the "9B" is **12.19B parameters**. **The paper's benchmark table does not describe the weights we would download**, so the arm choice rests on our own pilot and on architecture equivalence, **never on that table**. ⚠️ This is the same defect the TigerLLM paper criticises in others (*"results are not reproducible"*, *"absence of technical documentation"*). ⚠️ Two further cautions on that table if it is ever cited: LLaMA-3.2-11B scores **0.22 on MMLU-bn against a ~0.25 chance rate**, and `shehzad2023` — already in our bibliography — shows untuned baselines let any method be reported as winning; and every benchmark there is understanding/QA/reasoning, **not short colloquial generation**, which is our task. |
| 2026-08-12 | ⚠️ **Multi-accounting to evade free-tier limits was proposed twice and declined both times** | Sabbir asked whether a second Groq account, and later a second Kaggle account, would supply more free capacity. Declined in both cases; no such account is used. | **Consistency matters more than the two decisions separately: having refused the first, refusing the second is what makes the first a principle rather than a mood.** Two reasons, and the second is the operative one. (i) It breaches the providers' terms. (ii) 🔑 **The appendix must state how generations were produced, and *"we opened multiple accounts to evade rate limits"* is not a sentence that can be written down — so it is not a thing that can be done.** This repo's entire architecture is the ability to defend every number: provenance stamps, frozen splits, `NOT A RESULT` banners, this log. **A provenance trail that cannot be disclosed is precisely what that architecture exists to prevent.** Recorded rather than left implicit, because a reader of the appendix should be able to see that the question was asked and how it was resolved. Also verified on the vendors' own authority: Groq's limits are *"at the organization level"* and Google's are *"per project, not per API key"*, so a second key would not have helped in any case. |
| 2026-08-12 | 🎁 **Bangla tokenizer fertility MEASURED AGAIN on Gemma-3 — 3.71 chars/token, four times better than Llama's 0.93 — and the budget crisis largely dissolves** | On Groq/Llama the measured fertility was **0.93 chars per token** (~1 token per Bangla character), which made a ~3,434-char prompt cost ~3,710 tokens and put Phase 5 at ~10M tokens. On `TigerLLM-1B-it` (Gemma-3, vocab **262,144**): **891 chars → 240 tokens = 3.71 chars/token.** The same prompt costs **~925 tokens**, not 3,710. | **The covariate §1.2 asked for is not one number — it is per-tokenizer, and nobody had said so.** Llama-3's vocab is 128k and Gemma-3's is 262k, and for Bangla that is a **4× difference in cost for identical text**. 🔑 **Two consequences.** (i) Every budget figure computed on 2026-08-11 was Llama-specific and is superseded for any Gemma-family run. (ii) **Tokenizer fertility is not just a covariate to report in Ch.4 — it is a first-order determinant of whether the experiment is affordable at all**, and that belongs in the write-up as a finding about low-resource NLP practice rather than as a footnote. ⚠️ Recorded with the measurement method, since it was taken from a real rendered prompt rather than a synthetic string. |
| 2026-08-12 | 🔴 **TigerLLM-1B FAILS the generation task; TigerLLM-9B (12.19B, 4-bit) passes. The pilot's model size is re-registered** | Hand-read smoke test on the real prompt structure, 3 samples each, T4, temp 0.8 / top_p 0.9. **1B: 1 of 3 usable** — one rambling and truncated at the cap, one **degenerate** (the plot sentence repeated seven times under ক./খ./গ. bullets), one acceptable. **9B (4-bit nf4, ~7 GB, 6–8 s/generation): 3 of 3** plausible, specific, correctly-lengthed viewer comments, no degeneration. | ⛔ **NOT A RESULT: n = 3 per model, hand-read by Claude, no annotation, no sampling.** It is a smoke test — does the machine work — and it may not be quoted as a model comparison. 🔑 **But it settles the thing that mattered, and it settles it against the literature we were relying on.** arXiv 2503.10995 reports TigerLLM-1B at **MMLU-bn 0.61**, beating Gemma-2-27B's 0.35 — and that model **cannot reliably write a two-sentence film comment.** The caution registered on 2026-08-12 before running was exactly this: *"every benchmark there is understanding/QA/reasoning, not short colloquial generation, which is our task."* **A multiple-choice benchmark did not transfer to open-ended generation, and this is the concrete instance.** ⚠️ **Two caveats on the 9B output, recorded now so they cannot later be discovered as convenient:** (i) the comments read as **more literary than the corpus** — *"কষ্টগুলো সুরের মধ্যে বেঁধেছে"* against real comments like *"সিনেমা দেখে ঘুম চলে আসে"* — which is the naturalness gap `2410.15956` names and which §5.4's distributional realism check is the instrument for; (ii) **all three samples opened with the same phrase** (*ছেলেটা/ছেলেটার গান*), i.e. low diversity at temp 0.8 across only three draws, which bears on §5.4 and on the §5.1b temperature-schedule ablation. Both are observations, not measurements. ⚠️ **Consequence for the arms:** the controlled pairing must move with the size, so arm A becomes **`google/gemma-3-12b-it`** — which is **gated**, so the licence must now be accepted. |
| 2026-08-12 | 🔴 **Runner notebook: the save-back cell copied the RETIRED Groq filenames with errors suppressed — the local pilot's JSONL would have been silently lost** | `notebooks/s4_pilot_kaggle.ipynb` cell 4 copied `results/pilot_s4_generations.jsonl` / `pilot_s4_model_choice.*` (the Groq run's names) under `2>/dev/null`, while `configs/s4_pilot_local.yaml` writes `pilot_s4_local_*`. Kaggle wipes disk between sessions and `2601.17768` makes the JSONL the sole reproducibility artifact, so the failure mode was: pilot runs, copy fails silently, session ends, generations unrecoverable — or worse, the stale 27-row Groq file copied out looking like output. Fixed before any run: filenames now come from the config's `outputs:` block and the error suppression is removed, with a comment stating why a failed copy must be seen. Same session: the dry-run cell called `run_pilot.py --dry-run` with no `--config`, defaulting to the retired `configs/s4_pilot.yaml`, so the printed prompt would not have been the run's prompt; `--config configs/s4_pilot_local.yaml` added. | **Fourth and fifth bugs of the read-the-artifact class** — both found by reading the notebook against the config's `outputs:` block, after the code was believed ready. No generation existed, so nothing was lost; the row exists because the failure would have been invisible until it was unrecoverable. |
| 2026-08-12 | 🔧 **Pipeline maintenance: the 2026-08-12 provider/arm re-registrations had not reached `research_pipeline_en.md`** | §4.4 still read *"Generator: Groq primary (20-generation pilot → Llama vs Qwen); Gemini secondary"* — struck 2026-08-12 with a correction box; the same pass greped the whole file and struck six further live mentions (header API-cost line, execution-checklist step 16, tool-stack table, dependency list, budget table, risk table). Gemini's secondary role is explicitly unaffected. | The 2026-08-11 maintenance-failure row records the cost of letting the normative spec lag; this pass applies its remedy on the day of the change rather than 10 days later. Struck in place, not deleted; every strike carries the date and points to this log. |
| 2026-08-12 | 🔴 **`run_pilot.py` IGNORED the config's `provider:` field — the "local" pilot would have run on the Groq API** | The generation loop constructed the API `Writer` unconditionally; `provider: local`, `batch_size`, `quantization` and `max_new_tokens` in `configs/s4_pilot_local.yaml` were read by nobody. `LocalWriter` existed, was tested, and was never wired in. Fixed: the loop now selects `LocalWriter` when `provider: local`, passing the config's batch/quantization/token cap; a `--model-path ARM=PATH` override separates WHERE weights load from (a Kaggle Models mount, session-local) from WHAT the model IS (the config id, which keys every generation). All 242 tests pass. | **STATUS step 17 said "READY, NOT RUN" and the ready half was false** — the components were each built and tested, and the wiring between config and loop was never exercised because no generation had run. Caught by reading `run_pilot.py` against the config before Sabbir launched, i.e. the read-the-artifact class again, sixth instance. |
| 2026-08-12 | 🔴 **The weights-caching plan in the runner notebook FAILED on disk (`ENOSPC`) and could never have worked; replaced by Kaggle Models mount + plain cache** | `snapshot_download(local_dir=/kaggle/working/models/...)` keeps a second copy in the HF cache (~2× disk) and `/kaggle/working` caps at ~19.5 GB against ~24 GB of weights — the plan failed at 6/18 files on Sabbir's first attempt and would have failed at any point. Replaced: arm A (`gemma-3-12b-it`) attaches from **Kaggle Models** (read-only mount, zero disk); arm B (`TigerLLM-9B-it`) downloads to the default HF cache only, accepted as a per-session re-download of a few minutes. | The plan was written without checking `/kaggle/working`'s quota against the weight sizes — a number that was knowable in advance and was not looked up, same shape as the free-tier claims that failed against vendor docs on 2026-08-11. The smoke-test cell now exercises **both** arms (the failed plan's cell tested only TigerLLM, so a gemma load failure would have surfaced mid-pilot). |
| 2026-08-12 | 🔴 **Commit `0abdd6a` (2026-08-11 constants-linkage pass) BROKE four S2 configs — three would not parse, one parsed with a band constant silently OUTSIDE `trap_check.bands`** | Inserting `# ref:` comment blocks dedented `not_sentiment_aligned_below` out of `bands:` in `s2_pilot_regionA.yaml`, `s2_pilot_regionB.yaml`, `s2d_ktable_regionB.yaml` (YAML `ScannerError` — 3 tests failing since that commit) and dedented `persona_claim_fails_above` in `s2d_ktable.yaml`, which **still parsed** but moved the Band-3 boundary out of the instrument. All four restored to the exact pre-`0abdd6a` structure; values never changed; 242/242 tests pass, `check_constants.py` still reports 120/0. | **No result is affected**: every S2 run predates `0abdd6a` and ran from the intact configs. The parse failures were loud; the `s2d_ktable.yaml` one was not — a config that parses wrong is worse than one that does not parse, and only the cross-region identity test caught it. The linkage pass edited configs the day's session never re-ran the suite against; the pre-commit hook checks `step_close`, not pytest. |
| 2026-08-12 | 🔴 **Pilot run 1 crashed at generation 21/80: one LocalWriter per (model × prompt-arm) double-loaded the model onto a 16 GB T4** | The generation loop constructed a fresh `LocalWriter` for each prompt arm without freeing the previous one; the second 4-bit 12B load spilled to CPU and bitsandbytes aborted. Fixed: one load per model role, shared across prompt arms (the arm changes the prompt text, not the weights), model freed before the next role loads, and a role whose generations are all on disk is skipped without loading at all. | **The resume design did its job**: the 20 completed arm_a/bn generations were on disk in the JSONL and the re-run skips them — nothing lost, nothing regenerated. The 20 completed generations show varied openings (unlike the 3-sample smoke test), consistent with the exemplars supplying register; the smoke test's four observations (Malayalam script leak, Latin "actors", literary length, identical openings) remain open until the full 80 are read. |
| 2026-08-12 | 🔴 **THE PILOT'S COMPARISON DOES NOT EXIST: `md-nishat-008/TigerLLM-9B-it`'s uploaded weights are `google/gemma-3-12b-it`, byte-for-byte** | All 40 arm_b generations came out character-identical to arm_a's, token counts included — impossible for two different sampled models. Verified at the weights, not inferred from output: SHA-256 of `model-00001-of-00005.safetensors` is `4847447e9259…` for **both** the TigerLLM HF snapshot (`133d78aa…`) and the Kaggle `gemma-3/transformers/gemma-3-12b-it/1` mount; the HF blob store deduplicated them to one object. **Third independent defect for this model**: (1) arXiv 2503.10995 describes LLaMA-3.2/Gemma-2 weights that are not these; (2) "9B" is 12.19B; (3) the "Bangla-adapted" upload contains no adaptation. The pilot is **VOID as a model comparison** — one variable was planned and zero were delivered. The 100 generations are retained (`results/pilot_s4_local_generations.jsonl`) as a single-model measurement and are NOT a result. 🎁 **Salvage, registered before anyone wants it to be true:** the double-run is a **determinism check that passed** — identical seed → identical 40 generations across two loads — establishing that the local path is bit-reproducible, which the hosted API could not be (`2601.17768`). The model-choice verdict (`LANG_CONFUSION` in all four cells) is re-read as a **single-model** property of gemma-3-12b-it under both prompt languages. **Arm B is unfilled; candidate selection reopens, with the standing rule now upgraded by this event: no model enters an arm until its weights are verified against its claim (config.json + shard checksums), never from its model card.** | Sabbir's morning decision: replacement candidate for the Bangla-adapted arm. |
| 2026-08-12 | 🔴 **Resume did not resume: the archive check computed keys with `provider="groq"` while `LocalWriter` writes `provider="local"` — 20 duplicate-key rows now sit in the pilot JSONL** | `run_pilot.py` called `generation_key()` without its `provider` argument, whose default is `"groq"`; every stored local key is `…|local:model`, so nothing matched, `resuming: 20` was printed from the count and all 20 arm_a/bn generations were regenerated (identically — see the determinism note above) and appended under keys already present. Fixed: both call sites pass `provider=provider`. The archive is left as-is (append-only; the duplicates are self-identifying by key) and every consumer of this file must deduplicate by key on read. | The provider field was added to the key precisely so two backends could not be conflated — and the check then defaulted the field. A default becomes a value by use: the same failure shape as the `w=0.6` constant, in a different place. |
| 2026-08-12 | ✅ **The pilot is NOT re-run now: the generator is fixed at `google/gemma-3-12b-it` (single-arm), and the Bangla-adapted comparison becomes a PRE-REGISTERED ROBUSTNESS CHECK** | §4.4's pilot exists to *select* a generator between two arms. Arm B collapsed (weights = base, see the void row above), so there is nothing left to select between, and the pre-registered `TIE` default already said the pilot would not establish a quality difference at n=20. Registered: generation proceeds on `gemma-3-12b-it` with the 80 valid generations from run 1 retained as its dry-run evidence; the second-generator comparison is **scheduled, not dropped**, with candidates and the weight-verification gate held in open decision 22. ⚠️ **Provenance: Sabbir delegated (*"dekho jeta vlo hoy"*); the choice and reasoning are Claude's, endorsed not authored.** | **Searched before deciding** (alphaXiv; Consensus quota exhausted to 1 Sep). The search **changed the framing, not the decision**: `2604.04532` (4,950 judge runs, six backbones, five languages) finds backbone rankings **invert** across languages and recommends non-English evaluation be validated on **at least two backbones** — so a single-generator result is a *bounded* claim, not a safe default, and that bound now goes in Ch.5 Limitations with this citation rather than being discovered by a reviewer. What makes the bound tolerable here is design, not luck: §5.1's comparison is **Δ over zero-shot within a condition**, so a generator-specific level shifts every row together. Also relevant and recorded: their ablation shows **instruction-language localisation can be decisive** (Hindi 42.8% → 23.2% under partial localisation), which is independent support for §3e treating prompt language as a factor — and run 1's own leak counts point the same way (bn-prompt 1/20 vs en-prompt 4/20). |
| 2026-08-15 | ⚠️ **Runner notebooks passed an EMPTY `--model-path` because IPython expands `$VAR` only on the first line of a `!` cell** | Both Kaggle runners wrote `!python … \` then `--model-path arm_a=$GEMMA_PATH` on a continuation line; the variable was not expanded and the argument arrived empty. `run_devplots.py` refused and stopped at the grid line — **no generation ran, nothing was written**. Fixed in both notebooks by exporting to `os.environ` and keeping the command on one line. | 🔑 **The refusal is why this cost nothing.** `--model-path` validates its argument and exits; had it accepted the empty value and fallen back to the hub id, the run would have silently loaded a *different copy* of the weights than the mounted one, and the archive would say `arm_a` either way. The same pattern in the pilot notebook is fixed here too, where it had merely dropped the argument unnoticed. |
