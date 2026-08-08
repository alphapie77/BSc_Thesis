# RQ1-H — Human validation, attempt 2: the intrusion task

> **Both gates were pre-registered in `docs/protocol.md` (RQ1-H) before a single
> item was answered.** So was the note recorded *during* annotation, that both
> annotators independently reported the items looking alike — together with the
> pre-commitment for how a failure would be worded. Read that section first.
>
> **Attempt 1 (step 5k) is not superseded.** It is reported in full: its rating
> scale collapsed, α = 0.4970, and RQ1 was inconclusive. This is a second
> attempt with a different instrument, and it is labelled that way throughout.

- **Config:** `configs/intrusion.yaml` · **Generated (UTC):** 2026-08-08T14:45:31.869492+00:00
- **Commit:** `75688957a9197a18f40982a619151f299cdf13e3` · **Seed:** 42
- **50 intrusion sets**, each 4 reviews (3 alike + 1 intruder),
  **length-matched to within 2 words**, drawn from region A
  **excluding G-300** — text neither annotator had seen.
- **Nothing is trained.** These are counts, and the significance test is an
  exact binomial tail computed in-repo so it can be checked by hand.

## Gate A — is the split perceptible at all?

**HUMANLY_PERCEPTIBLE.** Pooled accuracy **0.810**
against a chance rate of 0.25, exact one-sided binomial
**p = 1.037e-31**, and at or above the pre-registered
0.45 threshold.

The K = 2 partition corresponds to a distinction people can see **without being
told what it is** — and, because every set was length-matched to within
2 words, **without length as a cue**. This is stronger than
RQ1 required.

| annotator   |   correct |   n |   accuracy |   p_exact |
|:------------|----------:|----:|-----------:|----------:|
| A           |        39 |  50 |     0.7800 |    0.0000 |
| B           |        42 |  50 |     0.8400 |    0.0000 |
| **pooled**  |        81 | 100 |     0.8100 |    0.0000 |

The two annotators chose the **same option** on
**70.0%** of sets. That is a separate quantity
from accuracy: it measures whether they were seeing the same thing as each
other, whether or not it was the intruder.

⚠️ **The pooled row is not 100 independent trials.** Both
annotators judged the same 50 sets, so the pooled p-value is
optimistic. The per-annotator rows are the honest tests; pooled is reported for
completeness.

## Gate B — is the distinction *specificity*?

| annotator   |   correct |   n |   accuracy |   p_exact |
|:------------|----------:|----:|-----------:|----------:|
| A           |        34 |  40 |     0.8500 |    0.0000 |
| B           |        34 |  40 |     0.8500 |    0.0000 |
| **pooled**  |        68 |  80 |     0.8500 |    0.0000 |

Chance is 0.50. The two annotators agreed with each other on
**75.0%** of pairs.

## What this settles

- **This is RQ1's arbiter.** S2f eliminated valence and verbosity; nothing
  cheaper than annotators remained.
- **It says nothing about region B**, whose own K = 2 split correlates with no
  measurable feature at all (`s2d_ktable_regionB.md`).
- **It cannot show there is cluster structure.** G1 established there is none
  (silhouette 0.053, HDBSCAN 100% noise). At best this concerns a **cut through
  a continuum** that humans can or cannot see.
