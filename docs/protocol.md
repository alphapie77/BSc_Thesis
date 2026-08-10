# protocol.md -- APPEND-ONLY PRE-ANALYSIS RECORD

**Status: SEALED 2026-08-10 for Phases 1-3.** Phases 4-6 (RQ2-RQ5) remain open
and are sealed separately when their first run happens.

Signed by supervisor: ____________________  Date: __________
Sealed at commit: ____________________

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
