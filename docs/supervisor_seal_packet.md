# Pre-analysis record — seal request, Phases 1–3

**Student:** Sabbir Hossain (21701082) · **Date prepared:** 2026-08-10
**Document to sign:** `docs/protocol.md` (1,090 lines, 37 deviation entries)
**Scope of this signature:** Phases 1–3 only. RQ2–RQ5 are unrun and seal later.

---

## 1. What you are being asked to sign

Not "this plan was fixed before any data was seen." That would be false, and the
document says so itself.

What is claimed is narrower and can be checked without trusting anyone:

1. **Every section carries the date it was written.**
2. **No section was edited after the run it governs.**
3. **Superseded text is struck through and marked, never deleted.**
4. **Every departure is in the deviations log with a date and a reason.**

`git log --follow docs/protocol.md`, read against the timestamps inside
`results/`, verifies all four independently.

The header previously read *"FROZEN PRE-ANALYSIS PLAN — freeze after the S2
pilot trap-check (Step 5)."* Step 5 ran on 2026-07-30 and the document was
amended more than thirty times afterwards. That description was false by August
and has been replaced rather than quietly repaired.

---

## 2. The four results that constrain what the thesis may claim

Each is a finding the project would rather not have had. Each is reported.

**(a) The clusters are not groups.** Gate G1 selected K = 2 on a stability rule
(prediction strength 0.860), but three independent indicators say there is no
cluster structure at all: silhouette **0.053**, a gap statistic rising
monotonically and selecting no K, and HDBSCAN calling **100% of points noise**.
The object is a reproducible cut through a continuum, not two discovered groups.

**(b) The stability rule can pass on nothing.** Region B also cleared PS ≥ 0.80
(0.818) with a 49.4/50.6 split correlating with *nothing measurable* — every
surface AUC 0.50–0.58, ARI vs sentiment 0.011. It is now used as a **negative
control**. This matches von Luxburg (2010) and is reproduced in simulation by
Pinto et al. (2026), whose real-data result (k = 2, sizes 50.6/49.4, ARI
0.999 ± 0.001) is numerically almost identical to ours.

**(c) The verifier ablation cannot speak to backbones.** Seven backbones were
compared over five seeds with a paired bootstrap test; the verdict was a **tie**
(21/21 comparisons non-significant). A follow-up baseline then showed a *frozen*
LaBSE probe scoring **0.9866** against the best fine-tuned arm's **0.9647** —
because the label was produced by k-means *on LaBSE embeddings*, so it is
near-linear in that space by construction. The seven-arm table is reported as a
demonstration of that circularity, **not** as evidence about backbones.

**(d) The corpus is two corpora.** The source file changes register abruptly at
row 1999; 60% of it carries a uniform signature no comment thread produces. The
collector kept no log and does not remember which rows came from where. This is
unresolvable and is reported as such, not worked around.

---

## 3. The one result that survives all of it

Human validation, second attempt: an intrusion task (annotators pick which of
four reviews does not belong, with no construct named to them).

- **39/50 and 42/50** against a chance rate of **0.25** — p < 1e-15, against a
  pre-registered bar of 0.45.
- Length matched to within **2 words**, and a length-only heuristic scores
  **0.16 — below chance**. The strongest confound is not merely controlled but
  inverted.
- A secondary block (34/40 and 34/40 vs 0.50) identifies the construct as
  **engagement specificity**.

So: the distinction is geometrically a line drawn through a continuum, and
people can nonetheless perceive it. That is the thesis's RQ1 claim, and it is
deliberately weaker than the "audience personas" the title still implies.

**Both annotators reported the items looked alike to them — then scored
0.78 and 0.84.** That note was written down *during* annotation, before any
answer was scored, so it could not later read as an excuse.

---

## 4. Departures you should look at specifically

| # | Departure | Where |
|---|---|---|
| 1 | **Human validation was attempted twice with different instruments.** Attempt 1 (rating scale) returned α = 0.4970 and is reported in full as an instrument failure, not withdrawn. Attempt 2 is the intrusion task above. A third attempt is forbidden in writing. | Deviations, 2026-08-08 |
| 2 | **Three personas → two.** The design posited three; the data cleared the pre-registered cutoff only at K = 2. The design gave way, not the cutoff. | Deviations, 2026-08-03 |
| 3 | **Two annotators, not three**, both independent, neither in CSE, neither told what the study sought. With two there is no majority, so disagreements are *not* resolved — the disagreement rate is itself reported. | Deviations, 2026-08-03 |
| 4 | **S2e/S2f demoted from tests to descriptive profiling**, because they are post-clustering inference on the rows that defined the clusters (Chen & Witten 2023). | Deviations, 2026-08-10 |
| 5 | **Terminology: *persona* and *cluster* both retired** in favour of an engagement-specificity axis. | Deviations, 2026-08-10 |

---

## 5. Known weaknesses, stated rather than buried

- **No human-validated verifier accuracy exists.** Phase 3 measures label
  *reproduction* only. The gold set produced specificity ratings, not cluster
  labels, and those ratings failed their reliability gate.
- **Small n throughout.** Verifier-A trains on **804** rows; the dev slice used
  for calibration and thresholds is **82**. Calibration is therefore labelled
  *descriptive* and cannot be claimed as a contribution.
- **Two unread load-bearing citations** (Chen & Witten 2023; von Luxburg 2010)
  are flagged as debts in `related_work.md`, not presented as read.
- **The title still says "Audience Simulation"** and has not yet been revised to
  match §4's constraint. This is outstanding.

---

## 6. One ruling requested — inviolable rule 7 vs the symbolic scorer

**This is the only thing in this packet that asks you to decide rather than
to check.**

Rule 7 of the project's inviolable rules reads: *"No stemming, no stopword
removal, no TF-IDF in the main pipeline... (TF-IDF is allowed only as an
explicitly-labelled cheap proxy in a pilot, **never in a result**.)"* Its stated
reason is that LaBSE and BanglaBERT are contextual encoders and need natural
text.

The symbolic scorer (§3.5) would benefit from an **IDF** feature family: the
minimum, maximum and mean inverse document frequency of a review's own words.
This is **not** TF-IDF vectorisation — it builds no document-term matrix,
replaces no encoder, and alters no text fed to any model. But IDF is half of
TF-IDF, and "never in a result" is unambiguous.

**The feature was therefore left disabled, and run once as a labelled pilot,
which the rule itself permits.** Measured cost:

| | stratified 5-fold CV macro-F1 |
|---|---|
| Rule 7 applied literally (IDF off) — **the committed result** | **0.5150 ± 0.0713** |
| IDF enabled (pilot only, unquotable) | 0.6949 ± 0.0532 |

The gap is **≈ 18 points**, about 2.5× the cross-validation standard deviation,
with variance *falling* as the mean rises.

**The methodological cost is larger than the accuracy cost.** Without IDF, the
scorer's contribution comes from surface families — punctuation, cue words,
sentiment terms — which the 2026 literature on reward hacking identifies as
precisely the category a generator learns to fake, and which our own refinement
loop names aloud to the generator. With IDF, the two families that carry the
signal are the two that cannot be faked vacuously, because raising IDF requires
using genuinely rarer, more specific words — which is the construct itself.

**What is being asked:** whether IDF-as-a-scalar-feature falls inside or outside
rule 7. Either answer is workable and both are already implemented; the code
refuses to enable IDF except under a pilot-labelled config, so the current state
is the conservative one. **No result in this thesis currently uses IDF.**

Ruling: ☐ IDF is outside rule 7 — enable it  ☐ IDF is inside rule 7 — keep it disabled

Signed: ____________________  Date: __________

---

## Signature

I have read the pre-analysis record and the deviations log, and I understand
that Phases 1–3 are sealed on the four properties in §1.

Supervisor: ____________________  Date: __________

Sealed at commit: ____________________
