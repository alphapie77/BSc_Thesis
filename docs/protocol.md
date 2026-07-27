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
  - < 0.4  -> personas are independent of sentiment; proceed as planned.
  - 0.4-0.6 -> report the overlap explicitly; proceed with caveat.
  - > 0.6  -> DO NOT claim independent personas. Either re-operationalize with
    engagement features (length / intensity / specificity) or reframe as
    "sentiment-anchored engagement tiers." Reported either way.
- **Claims:** win = validated persona scheme; mixed = tentative scheme with
  disclosed overlap; negative = theory-driven scheme with validated learnability.

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
