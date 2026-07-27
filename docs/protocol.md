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
| 2026-07-27 | S1 class balance | Post-cleaning class balance is no longer uniform; the R1/R2 split will be sentiment-stratified | Raw 1665/1664/1670 becomes 1513/1599/1618 after S1. Drops concentrate in class 0 (152 of 270 total; 152 of the 269 labelled drops), because duplicates and sub-3-word reviews are over-represented in the negative class. Stratifying the R1/R2 split on `Sentiment` keeps the shifted distribution identical across partitions instead of letting it drift further. Counts in `results/s1_cleaning_log.json` and `docs/dataset_card.md`. |
