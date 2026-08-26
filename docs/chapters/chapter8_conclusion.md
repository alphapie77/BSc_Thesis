# Chapter 8 — Conclusion and Future Work

## 8.1 Chapter Overview

This chapter consolidates the thesis contributions, gives the final answer to
each research question, identifies the next empirical steps, and closes the
study within the limits established in Chapter 7. It introduces no new analysis.
The conclusions refer to the completed Bangla experiment and preserve the
distinction between registered findings, exploratory evidence, negative
results, and questions that remain unanswered.

## 8.2 Contributions of the Study

**C1 — Verifier isolation and observable proxy divergence.** The first
contribution is a verifier-isolation protocol that makes proxy
divergence observable. Verifier-A can influence generation, whereas Verifier-B
is trained on a disjoint partition and remains outside retrieval, prompting,
threshold selection, and retry routing. This separation permits improvement
against the in-loop verifier and divergence from the sealed outcome verifier to
be measured as different quantities rather than absorbed into a single score.

**C2 — A bounded workflow under accounted compute.** The second contribution
is a bounded and auditable neuro-symbolic multi-agent
workflow evaluated under accounted compute. The Researcher, Writer, Critic,
and Reflector are functional roles connected by fixed transitions rather than
an autonomous planning system. Retrieval evidence, drafts, feedback, scores,
logical cost, and stopping decisions remain traceable. The paired evaluation
covers ten conditions over a frozen 5,400-case Bangla surface, with the nine
registered alternatives compared with zero-shot on identical plot–level–seed
keys.

**C3 — Construct validation that rejected its initial interpretation.** The
third contribution is a construct-validation process that rejected its own
initial audience-persona interpretation. Although the corpus analysis produced
a reproducible Region-A partition, the silhouette, gap-statistic, HDBSCAN, and
Region-B replication evidence did not support natural clusters or audience
personas. The thesis therefore retained a human-recognizable
engagement-specificity continuum cut instead of converting algorithmic
stability into an unsupported claim about discrete audiences.

**C4 — Explicit treatment of construction circularity.** The fourth
contribution is the explicit identification of circularity in the
Verifier-A result. Its near-perfect development performance is reported as a
consequence of predicting a geometric label derived in the same LaBSE feature
space, not as evidence that one language-model backbone is superior. This
interpretive constraint prevents an instrument-construction artifact from being
presented as substantive model performance.

**C5 — Blinded human validation of requested-level recovery.** The fifth
contribution is blinded human validation of requested-level
recovery. Three native-Bangla readers produced 300 judgments on a frozen,
balanced 100-item subset and achieved 0.9133 pooled target-match accuracy. This
supports human recoverability of the requested distinction, but does not
establish overall quality, naturalness, plot fidelity, or correspondence with a
real film audience.

**C6 — Separation of symbolic diagnosis from symbolic adjudication.** The sixth
contribution is this functional separation. Every held-out fold selected the
neural-only gate, and the mixture produced no mean AUC improvement over it,
although verdict sensitivity across the weight grid was not flat. The observed
case therefore remained outside the preregistered outcome partition. Symbolic
rules are consequently used to identify observable failure modes and formulate
revision guidance rather than to decide acceptance.

## 8.3 Final Answers to the Research Questions

**Table 8.1. Final research-question verdicts and claim boundaries**

| Research question | Final verdict | Evidence-bearing conclusion | Boundary that remains |
|---|---|---|---|
| RQ1 | Qualified support | A reproducible Region-A continuum cut is human-recognizable as engagement specificity under length-matched comparative judgment. | It is not a discovered persona or natural cluster, and its structural signature does not replicate in Region B. |
| RQ2 | Supported within the completed Bangla arm, with attribution limits | All nine registered alternatives improve sealed Verifier-B target probability relative to zero-shot, and the requested level is human-recoverable on the balanced subset. | The evidence does not rank active conditions, isolate the verifier as the sole cause, or establish audience prediction. |
| RQ3 | Roles differentiated; incremental value remains exploratory | Symbolic-only acceptance gating is weak, whereas symbolic rules provide diagnostic revision guidance under a neural gate. The combined condition performs strongly relative to zero-shot, and the post-hoc hybrid-minus-neural estimate is +0.02159 in target probability, concentrated at Level 0. | The exploratory binary contrast is not statistically significant under the exact McNemar test ($p=0.11728$); neither a level-specific causal advantage nor overall hybrid superiority is established. |
| RQ4 | Supported as a diagnostic | Same-case Verifier-A–Verifier-B gaps widen across revisions in the two neural-gated loops, in the direction expected under proxy overoptimization. | The result does not prove declining human-perceived quality and does not make Verifier-B an oracle. |

Together, these answers support a bounded claim: short Bangla cinema responses
can be generated with improved control over a requested, human-recognizable
engagement-specificity level, and a verifier-in-the-loop design can expose its
own proxy divergence when outcome scoring is kept outside the loop. They do not
support discrete audience segmentation, film-specific response prediction,
box-office forecasting, or replacement of authentic audience research.

## 8.4 Directions for Future Research

The most immediate next step is a preregistered direct comparison between the
neural-only loop and neural gating with symbolic diagnostic feedback. The design
should be powered for the smaller incremental effect observed here, specify
level-wise contrasts in advance, and preserve the same paired cases and sealed
outcome-verifier wall. This would test the contribution of symbolic feedback
without selecting the contrast after inspecting condition-versus-zero-shot
results.

A larger human study should allocate enough unique items to each condition and
requested level to estimate system-specific target match. Target-level
recoverability, general writing quality, naturalness, and plot faithfulness
should be evaluated as separate constructs rather than combined into one rating.
Recruitment should extend beyond a convenience sample of three university
batchmates, with the sampling frame, compensation, rater variation, and ethics
determination documented prospectively.

Future evaluator work should test both verifiers with controlled perturbations
of length, register, punctuation, sentiment markers, and lexical specificity.
Such stress tests could identify which cues widen the A–B gap and whether human
judgments follow either automatic instrument. Calibration should be reassessed
on a substantially larger held-out set before verifier probabilities are given
an empirical-confidence interpretation.

The symbolic component also requires redevelopment on more labelled data and
features that are less directly gameable. Any revised symbolic scorer should be
evaluated out of sample before it is permitted to gate generation. Until then,
its defensible function remains the localization of observable features for
feedback rather than independent adjudication.

External validity requires both broader Bangla data and a cross-domain test.
Longer reviews, other social registers, additional model families, and the
deferred English mirror would clarify which findings are specific to this
corpus, language, and Writer. Most importantly, film-linked human-response data
would be required for any transition from corpus-level controlled generation to
genuine pre-release audience prediction. Without such data, a generated
response cannot be validated against the audience reaction to the film whose
plot prompted it.

## 8.5 Final Conclusion

This thesis investigated whether a bounded neuro-symbolic multi-agent workflow
could improve control of a human-recognizable response distinction in short
Bangla cinema comments while making verifier-induced proxy divergence
observable. The completed experiment provides a qualified affirmative answer.
The neural-gate condition with symbolic diagnostic feedback produces a positive
registered difference relative to zero-shot under the sealed Verifier-B outcome
measure, and the broader set of registered controls shows that several prompting,
retrieval, critique, judging, and resampling strategies can also improve that
measure. Human evaluation shows that readers can usually recover the
requested engagement-specificity level on the balanced subset.

The same evidence prevents a stronger conclusion. The controlled distinction is
a cut through a continuum rather than a discovered audience segment; generated
length remains entangled with the requested level; Verifier-B is an outcome
proxy rather than ground truth; the incremental contribution of symbolic
feedback is supported only by an explicitly post-hoc contrast; and the review
corpus contains no film identifiers with which to validate predicted audience
responses. Revisions can also widen the disagreement between the in-loop and
outcome verifiers, showing that optimization and validity can move apart.

The defensible outcome is therefore not synthetic audience prediction. It is an
auditable framework for generating alternative Bangla response styles under
explicit control, accompanied by evidence about where that control succeeds,
what it costs, and how its verifier can diverge from a sealed evaluator. Any use
beyond transparent pre-writing, hypothesis generation, or research exploration
requires direct evidence from real audiences.
