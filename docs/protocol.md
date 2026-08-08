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

## RQ2 -- Verifier-in-the-loop
- **H2:** An external trained verifier in a generate-verify-refine loop improves
  persona-controllability over zero-shot, few-shot, RAG-only, and self-critique.
- **Metrics:** persona accuracy under **Verifier-B** (never in the loop), MAUVE,
  length-JS divergence.
- **n:** 8 conditions x 2 languages x **90** eval-plots x 3 personas, >= 3 seeds.
  (90, not 100 — the plot corpus froze at 120 = 30 dev + 90 eval on 2026-07-31;
  see the Deviations entry of that date.)
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
| 2026-08-01 | Split map — **stratified on `Sentiment × region`, not on cluster** | Pipeline §A specifies a *cluster*-stratified gold set. `data/splits/split_map_v1.json` is stratified on `Sentiment × region` (5 non-empty cells; region A holds no class-2 rows). G=300, R1=2,162, R2=2,163, dev=200, over the 4,625 rows surviving near-duplicate removal at the pre-registered t = 0.95. | The cluster instruction predates two findings. **(1)** The corpus is two corpora (`s2c_region_split.md`). **(2)** The full-corpus clustering is a **corpus detector** — 93.3% accuracy at identifying which of the two a review came from (`s2_pilot_ari_trapcheck.md`). Stratifying the gold set on that clustering would stratify it on a file seam. Additionally, **Gate G1 has not run**: the master K-table is outstanding, so any cluster-stratification now goes stale the moment K changes. `region` and `Sentiment` are both known, both stable, and both matter — region because it is the confound the design now controls for, Sentiment because it is the label. Verified: every part matches the corpus on both variables to within 0.1pp, zero overlap between any two parts, union covers the input exactly. Pinned permanently by `tests/test_split_map.py`. **The persona-stratification question moves to the annotation stage, where the scheme will actually be settled.** |
| 2026-07-31 | Plot corpus — **target reduced from 130 to whatever the source yields.** ⟶ **FINAL: 120 = 30 dev + 90 eval**, frozen the same day. (The estimate below said ~124/94; human review then removed 4 more — BN024 production history, BN042 the director's fatal accident, BN068 commentary about a story rather than the story, BN113 a 3-sentence fragment that sets up and stops. All four had passed every mechanical gate.) | The pipeline's §1.1.7 asks for 130 = 30 dev + 100 eval. bn.wikipedia does not contain 130 Bangla-film articles with a usable plot section. Four harvests: 67 → 110 → 132 → **124**, the last figure lower because a person-article veto removed 8 rows that had been counted as usable — actors' and directors' biographies swept in by the film categories. `N_DEV` stays at **30** (the dev slice tunes the loop threshold and 30 is the smallest defensible size); **eval takes the remainder**, with a hard floor of 80 below which the tool refuses to split. | **Two ways to reach 130 existed and both were refused.** (1) Relax the quality gate to admit two-sentence plots — but it was rejecting only ~20 of 3,135, so it is not the constraint, and thin plots are poor generation inputs. (2) Add the by-year categories, the largest available (২০১৯-এর = 268, ২০২২-এর = 220, ...) — but they are **language-neutral**: Tamil, Hindi, British and Japanese films sit in them, their bn.wikipedia articles are in Bangla, and they would therefore pass every gate in the harvester while quietly making the plot corpus stop being *Bangla cinema*. No check in the pipeline would have caught it. **Losing six eval plots costs a little power in a bootstrap CI; padding the set costs validity, which no n buys back.** 130 was a design choice in the spec, not a statistical requirement, and this is recorded before the number is used rather than after it is convenient. |
| 2026-08-03 | RQ1-D — **K=2 profile registered as EXPLORATORY IN ORIGIN, pre-registered in interpretation** | New analysis added after G1's table was seen: `src/cluster/s2e_profile.py`, `configs/s2e_profile.yaml` → `results/s2e_regionA_k2_profile.md` (+ assignments, features and log-odds CSVs). Section "RQ1-D pre-commitment" added above, **before the script existed**. | Two gaps in G1, both closed here. **(1)** G1 selected K = 2 and never persisted the labels; G-300 stratification needs them, and they cannot be recovered from `s2d_ktable_regionA.csv`. **(2)** G1 never asked what separates the halves. That question is decisive *before* annotation, not after: G1 reports PS 0.860 and bootstrap ARI 0.940 (a reproducible cut) alongside silhouette 0.053, a monotonically rising gap statistic satisfied at no K, and **HDBSCAN calling 100% of points noise** (no separated groups). A reproducible bisection of a continuum is what K-Means yields when it cuts along the dominant direction of variation — and with ~8-word reviews on L2-normalised LaBSE, **length** is the obvious candidate. If a word count reproduces the encoder's cut, spending 300 annotations on it would buy an expensive confirmation of a ruler. The **decision to profile is post-hoc and is labelled as such in the report itself**; what was fixed in advance is what each `length_auc` band would be taken to mean, including the pre-committed refusal to run G-300 on a `LENGTH_DOMINATED` partition. Guarded in code: `s2e_profile.py` re-derives G1's silhouette and ARI and **aborts** if they differ by more than 1e-6, so it cannot profile a K = 2 solution other than the one G1 selected; `tests/test_s2e_profile.py` (11 tests) additionally fails if the two configs' embedding or K-Means blocks ever diverge. Nothing is trained (AUC and Cliff's delta are rank statistics, the Dirichlet prior is fixed) — rule 10 untouched; whitespace tokens only, no stemming, stopword removal or TF-IDF — rule 7 untouched. New method citation: `monroe2008fightinwords`. |
| 2026-08-03 | RQ1-E — **residual test run VOLUNTARILY at Band 1** | New analysis: `src/cluster/s2f_residual.py`, `configs/s2f_residual.yaml` → `results/s2f_regionA_k2_residual.md` + `_cells.csv`. Section "RQ1-E pre-commitment" added above, before the script existed. **No band assignment is revised**: ARI(cluster, Sentiment) = 0.1522 remains Band 1 and the corpus does not move into Band 2. | Band 2 makes a residual test mandatory at ARI ≥ 0.20 and we are below it, so nothing was owed. Run anyway because **ARI is the wrong instrument for this association and this project has already been misled by that gap once** — `s2b_register_probe.md` recorded φ 0.565 against V 0.410. The same 2×2 that yields ARI 0.1522 yields **φ = 0.3981**, χ² = 300.7, and cluster→sentiment accuracy 69.5% against a 50.2% baseline; all 12 reviews nearest cluster 0's centre are positive and all 12 nearest cluster 1's are negative. Skipping on a technicality would leave a question a reviewer will certainly ask, answerable from data already on disk. **Results:** A min AUC 0.6115 (length independent of sentiment), B min \|φ\| 0.3133 (sentiment independent of length in every band), **C lift +9.80 pp → `RESIDUAL_SURVIVES`** — but **0.2 pp from the 10.0 cutoff**, and the script emits an automatic boundary-warning box at ≤2 pp so the weakness cannot depend on anyone remembering it. D: the richness inversion holds in **all four** length bands. Decomposition (added after the first run, before any interpretation was written): Sentiment alone +9.28 pp, length alone +5.22 pp, both +9.80 — so **length adds only 0.53 pp once sentiment is known**, and S2e's `LENGTH_CONFOUNDED` overstates length's independent contribution. Test C is a **resubstitution** estimate and therefore an upper bound; the bias direction was chosen deliberately, since it makes the persona-killing verdict easier to reach. Nothing trained (rule 10); whitespace tokens only (rule 7). Pinned by `tests/test_s2f_residual.py` (9 tests), including one that fails if the 10.0 cutoff or the quartile count moves, because either would flip the published verdict. |
| 2026-08-03 | RQ1-F — **G-300 registered; 3 annotators → 2; author-as-annotator flagged** | New: `configs/g300.yaml`, `src/annotate/g300_build.py`, `g300_score.py`, `docs/g300_annotation_guideline.md`, `tests/test_g300.py` (18). Section "RQ1-F pre-commitment" added **before any item was annotated**. | Three departures from RQ1 as written, all forced and all recorded rather than absorbed. **(1) n = 2 annotators, not 3.** With two there is no majority, so the adjudication rule is fixed in advance: **disagreements are not resolved** — the gold value is the mean and the disagreement rate is reported, because adjudicating after seeing the data is how an IAA figure gets laundered. **(2) One available annotator is the author.** Recommendation on record: *Sabbir should not annotate* — he designed the study and has read the log-odds lists and the cluster-representative reviews. If he does anyway, no claim of *independent* human validation may be made, only *partially independent*, and it goes in the abstract's limitations and the dataset card, not a footnote. **(3) Only 123 of the frozen G-300 are in region A** and carry a K=2 label, because the split was stratified on `Sentiment × region` in August, before G1 chose K. The split map is **frozen (rule 3) and was not regenerated**; all 300 are annotated and Gate 2 runs on the 123, with its reduced power reported as a number. Task design: annotators rate **engagement specificity** on a 0–3 ordinal scale and **never see cluster, K, region, Sentiment, word count or `review_id`** — `review_id` is ordered by position in the source file, and position *is* the region variable. They are not asked "which persona is this?", which would make their agreement a measure of how well we wrote the cluster descriptions. RQ1-D's binding condition is enforced twice: worked counter-examples in the guideline (`bn_0360`, 12 words → 1; `bn_0252`, 4 words → 2, both from `dev`) **and** a per-length-band AUC in the scorer, because instruction is not enforcement. |
| 2026-08-03 | RQ1-F Gate 2 — **decision rule changed from a bootstrap CI to a permutation test, before any annotation** | Gate 2 previously fired `NEGATIVE` when the bootstrap 95% CI included 0.50. It now uses a permutation null (5,000 shuffles of cluster membership, α = 0.05); the CI is still reported, for precision only. | **The old rule was broken in the direction that matters most.** `directionless_auc` is `max(a, 1−a)`, so every bootstrap resample is bounded below by 0.50 and the lower bound essentially never reaches it — the `NEGATIVE` verdict was close to unreachable, making the single number that decides RQ1 biased toward finding an effect. Demonstrated rather than asserted: under chance at n = 123 the null's own 95th percentile sits at ≈ **0.60**, not 0.50, so any rule treating 0.50 as the null value is wrong. Found by the scorer's own smoke test. **Nothing had been observed when this changed** — no sheet filled, no α, no AUC — so this is a pre-registration refinement of the same kind as the 2026-07-28 band revision, not a post-hoc adjustment. `tests/test_g300.py::test_the_negative_verdict_is_actually_reachable` now fails if the null verdict ever becomes unreachable again, and `::test_permutation_null_sits_well_above_half_at_this_n` pins the reason. |
| 2026-08-05 | RQ1-F outcome — **G-300 round 1 returns `UNRELIABLE`; recorded as INCONCLUSIVE (instrument failure), NOT as a negative result** | α(ordinal) = **0.4970** < 0.667, so the pre-registered rule fires and **Gate 2 was not computed**. That verdict stands and is not revised. What is added here is the diagnosis, because "α < 0.667" and "humans cannot make this distinction" are different claims and only the first is established. | **The annotators agreed strongly**: exact agreement **75.5%**, within-1 **98.7%**, **Gwet's AC1 = 0.871**. α is low because the *scale* collapsed, not because the raters diverged — **68% of A's and 76% of B's ratings are the single value "2"**, so there is almost no variance for agreement to be measured against. This is the kappa/κ paradox, and `related_work.md` had already listed `gwet2008ac1` as the guard for exactly it. **Cause, and it is mine to own: the calibration advice was bad.** Round 1 calibration showed annotator A compressed onto "1" (12 of 20), and Claude's fix was *"if the review names an aspect, at least 2"* — but nearly every review names something, so both annotators moved almost everything to 2, and the **2-vs-3 boundary was never given equal attention**. One problem was traded for a worse one. **A rescue was attempted and failed, and is reported rather than omitted:** recast as binary at the only boundary with real spread (3 vs ≤2) gives κ = **0.5285**, still below 0.667. No post-hoc recoding saves it. **Consequence:** RQ1 is reported as **inconclusive on human validation**, with the failure attributed to the instrument and its cause named. Writing "negative result" would assert that people do not make this distinction, which this data does not show. **No second round:** annotator time is exhausted and none is available, so the repaired-rubric option was closed by circumstance rather than chosen — recorded so nobody reads the absence of round 2 as a judgement that round 1 sufficed. |
| 2026-08-05 | RQ2–RQ5 — **decoupled from RQ1's outcome** | The generation and verifier experiments condition on `cluster_k2` as a **controlled label**, and no longer depend on that label having been validated as a persona. | RQ2 asks whether an external trained verifier improves adherence to a **target label**. That question needs the label to be well-defined and reproducible, not to be a validated audience type — and K = 2 is well-defined and reproducible (PS 0.860, bootstrap ARI 0.940 ± 0.029). Making this explicit costs nothing and prevents an inconclusive RQ1 from being read as invalidating the thesis's actual contribution. **The price is terminological and is paid in full:** the word *persona* may no longer describe the K = 2 halves anywhere. They are **clusters**, and generation is **cluster-controlled**, not persona-controlled. This closes STATUS decision 12 by force — including for the title. |
| 2026-07-30 | Provenance — `git_hash()` semantics | `-dirty` now reflects **tracked** modifications only (`git status --porcelain -uno`); untracked files are counted separately in `stamp()` as `untracked_files` | The suffix previously came from bare `--porcelain`, which also lists untracked files. Every run creates untracked artifacts — its own outputs, caches, a copied input — so every stamp came out `-dirty` and the flag stopped distinguishing anything; the one case it exists to catch (a result produced from edited but uncommitted source) had become invisible. This is why `results/s2_pilot_ari_trapcheck.md` carries `e3d8e434…-dirty` despite being produced from a **fresh `--depth 1` clone**, in which no tracked file *can* have been modified. The S2 result is therefore attributable to a pristine `e3d8e43`. Untracked files are reported, not ignored — a source file that was never committed is a real provenance gap. |
| 2026-07-27 | S1 class balance | Post-cleaning class balance is no longer uniform; the R1/R2 split will be sentiment-stratified | Raw 1665/1664/1670 becomes 1513/1599/1618 after S1. Drops concentrate in class 0 (152 of 270 total; 152 of the 269 labelled drops), because duplicates and sub-3-word reviews are over-represented in the negative class. Stratifying the R1/R2 split on `Sentiment` keeps the shifted distribution identical across partitions instead of letting it drift further. Counts in `results/s1_cleaning_log.json` and `docs/dataset_card.md`. |
