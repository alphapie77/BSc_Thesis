# Chapter 7 — Discussion and Limitations

This chapter interprets the completed Bangla study without extending its claims
beyond the registered evidence. Automatic scores, human judgments, cost, and
distributional diagnostics are treated as complementary rather than collapsed
into a single notion of quality. The discussion first answers the four research
questions and then examines construct, internal, external, statistical,
measurement, ethical, and practical limitations. Contributions, future work,
and the final synthesis are reserved for Chapter 8.

## 7.1 What the experiment establishes

The central positive finding is not that a language model can reproduce a real
audience. It is that an auditable generation system can make Bangla cinema
comments more consistent with a requested engagement-specificity level than a
zero-shot prompt. All nine registered alternatives improve target probability
under the sealed Verifier-B outcome measure, and the largest observed
condition-versus-zero-shot difference belongs to a neural gate whose correction
feedback includes symbolic diagnostics. This does not constitute a registered
ranking among active conditions. On a separately frozen 100-item subset,
native-Bangla readers match the requested level in 91.33% of judgments, with
88% unanimous three-way
agreement.

The evidence is strongest when the computational and human results are read
together but not collapsed. Verifier-B covers the complete 5,400-case surface
under a fixed outcome scorer. Human evaluation tests whether the requested
distinction is actually recoverable by readers on a smaller balanced subset.
Neither source alone licenses a broad claim: the automatic scorer is not a human
oracle, and the human sample is not large enough for condition ranking.

The second substantive finding is negative but useful. Repeated optimization
against Verifier-A increases the same-case A–B gap in the neural and
neural-plus-symbolic loops. This illustrates why a held-out outcome scorer is a
load-bearing design element rather than redundant evaluation. Recent work on
evaluator stress testing reaches the same methodological conclusion: improvement
against a proxy must be separated from improvement in the intended construct,
and invariance or independent checks are needed to expose exploitable sensitivity
[@b7]. The present study observes divergence; it does not claim to
identify the exact linguistic strategy responsible for every divergence.

## 7.2 Interpretation by research question

### 7.2.1 RQ1: construct recovery and human recognizability

RQ1 receives qualified support. The Region-A K=2 solution is reproducible and
people can identify both its contrast and its engagement-specificity direction
under length-matched comparative judgment. That positive human evidence does
not overturn the negative geometric evidence: silhouette is 0.053, the gap
statistic selects no K, HDBSCAN returns 100% noise, and the Region-A signature
does not replicate in Region B. The contribution is therefore a validated
operational cut through a continuum, not discovery of audience personas or
natural clusters.

### 7.2.2 RQ2: external verification and controllability

The completed Bangla arm supports the proposition that additional control
mechanisms improve target-level matching over zero-shot. Yet “external trained
verification” is not the only successful mechanism: few-shot prompting,
RAG-only generation, self-critique, hosted judging, and blind resampling all
produce positive registered effects. The result should therefore be framed as
comparative evidence about a family of controls, not as proof that only the
proposed architecture can work.

Descriptively, the trained loop offers a favorable outcome-score–compute pattern
relative to the three-call self-critique controls. Neural-plus-symbolic feedback
uses roughly 1.63–1.89 logical model calls per case, while the two self-critique
variants use three. Nevertheless, the thesis does not reduce outcome score and
cost to one unregistered composite measure. Depending on deployment priorities, blind
resampling or a hosted judge may remain attractive alternatives.

The hosted-judge result must also retain its measurement boundary. Judge
replacement can change scores on fixed responses [@b22], same-family
self-preference has been observed in rubric-based evaluation [@b23], and
multilingual and low-resource studies report uneven agreement with humans
[@b24; @b25]. The Gemma-4 arm is therefore a treatment comparison, not an
independent outcome authority.

### 7.2.3 RQ3: symbolic gating and diagnostic feedback

The experiment rejects a strong interpretation in which symbolic gating is
sufficient. The symbolic-only loop fails to improve Level-0 accuracy over
RAG-only and gives up on more than half of Level-1 cases. Symbolic information
is more plausible as a diagnostic language for correction than as the primary
acceptance mechanism. This interpretation matches the system design: the neural
model supplies a learned decision signal, while symbolic rules name observable
failure modes for the Reflector.

An exploratory paired comparison of the 540 frozen hybrid and neural-only pairs
finds a +0.02159 target-probability difference, but only a +0.02037 binary
accuracy difference (exact McNemar p=0.11728). The observed probability
difference is concentrated at Level 0, while the Level-1 estimate is
approximately zero. The defensible conclusion is that the combined condition
performs strongly and exhibits a possible level-specific pattern, while
symbolic-only gating is inadequate and neither a level-specific causal advantage
nor overall hybrid superiority is established.

### 7.2.4 RQ4: verifier overoptimization

The widening A–B gap is consistent with Goodhart-style overoptimization. It is
not a direct measure of human-quality decline. Verifier-B may have its own blind
spots, its calibration improvement was not established, and later attempts are
selected precisely because earlier drafts failed. The analysis mitigates the
last issue through same-case adjacent transitions, but it cannot make B ground
truth. The correct claim is that optimization changes the relationship between
the in-loop and held-out scorers in a direction expected under proxy gaming.

## 7.3 Theoretical interpretation and construct validity

The original language of “audience personas” is stronger than the evidence.
Earlier phases found no separated cluster structure: silhouette was 0.053, the
gap statistic did not select a K, and HDBSCAN assigned all points to noise. The
operational object is therefore a two-level cut through an
engagement-specificity continuum, supported by comparative human recognition,
not two naturally occurring audience types.

Phase-5 human evaluation strengthens only the output-side construct: readers can
usually identify which level the generator was asked to produce. It does not
show that generated comments represent stable demographic, psychological, or
behavioral groups. A 2026 systematic review of synthetic audiences highlights
hallucination, bias, prompt sensitivity, and anthropomorphic overgeneralization
as recurring threats [@b1]. Accordingly,
the thesis claims **axis-level-conditioned response generation**, not audience
simulation. This does not imply substitution for real viewers, prediction of
individual opinions, box-office forecasting, or estimation of a film's audience
mix.

Generated length is a further construct threat. Although a uniform length clause
reduced the original gap, level remained recoverable from length in development,
and the main-run matched slice retained only 486/2,700 pairs with sharply unequal
condition coverage. This means the system controls a package of textual cues in
which specificity and length remain entangled. No result should be described as
length-neutral control.

Human target match also differs from overall response quality. Annotators were
asked only whether the output matched Level 0 or Level 1. They did not rate
fluency, helpfulness, naturalness, sentiment appropriateness, plot faithfulness,
or likely audience acceptance. The 91.33% result must always retain the label
“target-level match,” never simply “human accuracy” or “human quality.”

## 7.4 Internal validity

The strongest internal-validity safeguard is the enforced separation between
Verifier-A and Verifier-B. A is allowed to gate and select; B never enters
generation. The final archive and source-code checks make that separation
auditable. The same plot, level, and replicate keys support paired comparisons,
and shared initial RAG drafts reduce irrelevant sampling differences across the
loop conditions.

Several threats remain. First, both verifiers learn labels originating from the
same broader operational construct, so cross-family architecture does not make
their errors independent. Second, the hosted Gemma-4 judge is in the same model
family as the generation stack and may exhibit self-preference. It is therefore
a treatment condition, never the final scorer. Third, later attempts are
failure-selected; raw attempt-wise means cannot be interpreted as a trajectory
for the original 540 cases. Fourth, the live demonstration uses a hosted
Gemma-4 Writer rather than the frozen Gemma-3 Writer and is diagnostic software,
not Phase-5 evidence.

The length-matched analysis introduces post-treatment selection. Because each
condition affects emitted length, filtering on length changes the evaluated
population differently across conditions. Its small, unequal cells are useful
as a stress test but cannot repair the confound or replace the full-surface
analysis.

## 7.5 External validity

The study concerns short Bangla cinema comments drawn from one corpus and plots
used as generation stimuli. The source data contain no review-to-film mapping.
It is therefore impossible to test whether generated responses match the real
distribution of reactions to the same film. Corpus-level length, diversity, and
LaBSE-feature diagnostics are not substitutes for film-level predictive
validation.

The 90 evaluation plots are held out from development, but they do not establish
generalization to other Bangla registers, longer reviews, social-media
conversations, other cultural communities, or non-cinema domains. The three
human evaluators are adult native-Bangla university batchmates known to the
researcher. Their consistency is useful for this instrument, but the convenience
sample cannot represent the full Bangla-speaking audience.

## 7.6 Statistical-conclusion validity

The primary automated comparisons use 540 paired cases per condition and
10,000-resample paired bootstrap intervals, with Benjamini–Hochberg correction
across the nine frozen comparisons [@b49; @b50]. This is substantially more informative than
reporting unpaired mean differences or choosing the best replicate. Still, the
three seeds are sensitivity blocks rather than a population of independent model
runs, so conventional mean±SD claims across three seeds would overstate the
replication base.

The human study contains 100 items and 300 judgments, which supports an overall
target-match estimate and agreement analysis. It does not support confirmatory
20-cell condition ranking: each cell has five items and 15 judgments. Similarly,
the length-matched sensitivity cells vary from 9 to 80 pairs, making their
accuracies unstable and selection-dependent.

The registered inferential family omits direct comparisons among active systems.
The exploratory hybrid-versus-neural-only contrast is therefore interpreted
separately from that family and reported with its level heterogeneity. A
preregistered replication is required before claiming the incremental
superiority of symbolic feedback.

## 7.7 Measurement limitations

Verifier-B calibration improvement was not established, so its probabilities
should be read as fixed scorer outputs rather than perfectly calibrated empirical
probabilities. The realism analysis also remains incomplete: sentiment
Jensen–Shannon divergence was not computed because no independent registered
generated-text sentiment scorer existed. Reusing the target-level verifier for
sentiment would have mixed constructs.

LaBSE-feature MAUVE is reported only as sensitivity evidence. With 270 texts per
distribution and a non-default feature representation, its absolute values are
not comparable to default GPT-2-feature MAUVE reported in prior benchmarks
[@b55].
Distinct-n, Self-BLEU, word-count JS, and short-output rates capture different
properties and are intentionally not collapsed into a single realism ranking.

The interface's plot-support check is also not a thesis metric. It is a live,
source-bounded triage call that can help a user inspect a response, but it has
not undergone the registered human faithfulness audit. Its verdict cannot be
used to state a hallucination rate for the frozen 5,400 outputs.

## 7.8 Ethical and practical limitations

All three evaluators were adults, native Bangla speakers, and provided informed
consent. Public files contain only codes A, B, and C; identity and consent
evidence remain private. No monetary honorarium was paid, and refreshments were
provided. Participation through an existing batchmate/friend network creates a
possibility of perceived social pressure despite the consent language stating
that participation and withdrawal carry no academic or personal consequence.

No institutional approval or exemption is claimed. Completion times and
substantive evaluator feedback were not present in the returned CSVs and have
not been inferred. The
final Human Evaluation Data Sheet (HEDS) 3.0 package [@b32] should preserve these
fields as unknown unless the
participants voluntarily report them.

Generated cinema comments may reproduce stereotypes, offensive language, or
incorrect plot claims. The system should therefore be treated as a research and
pre-writing aid, not as evidence about real communities and not as an autonomous
decision-maker for casting, marketing, or audience targeting.

**Table 7.1. Validity threats, mitigations and residual risks**

| Validity domain | Principal threat | Implemented mitigation | Residual risk |
|---|---|---|---|
| Construct | Axis labels originate from a geometric cut; specificity remains entangled with length | Comparative human validation; persona/cluster terminology retired; length diagnostics reported | Human target match is not overall quality or real-audience validity |
| Internal | Optimization may exploit Verifier-A; both verifiers reproduce the same operational label | Disjoint R1/R2 training, cross-family models, executable B-outside-loop guard, paired keys | Verifier errors are not independent; later attempts are failure-selected |
| External | One short-comment Bangla corpus, 90 plots, no review-to-film mapping | Claims restricted to corpus-level Bangla response generation | No film-level audience prediction or other-register/domain generalization |
| Statistical conclusion | Three seeds can be mistaken for independent replications; the direct hybrid contrast is exploratory | Paired 540-case comparisons, 10,000 bootstrap resamples, frozen BH family | Overall hybrid superiority remains unestablished; small human per-cell n |
| Measurement | Verifier-B calibration improvement not established; realism metrics measure different properties | Calibration null retained; length/diversity/MAUVE reported separately | B is not ground truth; LaBSE-feature MAUVE is small-sample sensitivity only |
| Human evaluation | Three known university batchmates form a convenience sample | Adults, native Bangla, blinded sheets, consent, coded identities | Social-pressure and population-representativeness risks remain |
| Ethics/governance | Generated claims may be stereotyped, offensive or plot-unsupported | Research/pre-writing use only; diagnostic support check separated from results; adult consent and coded responses documented | No institutional approval/exemption claim; convenience-sample pressure risk remains |

## 7.9 Practical implications

The framework is most defensible as a transparent pre-writing and hypothesis-
generation tool. A user can request both engagement levels, inspect retrieved
examples and correction traces, and compare alternative responses before
deciding what deserves human investigation. The output may help formulate
questions for a test screening or identify film details that invite more
specific discussion. It should not be presented as a forecast of audience
sentiment, market demand, or the response distribution of a demographic group.

The experiment also shows that system choice should depend on the intended
trade-off. Static examples and RAG provide inexpensive improvement; blind
resampling is a strong control; self-critique consumes a fixed three calls; the
symbolic-only loop is inefficient at Level 1; and the neural-plus-symbolic
condition has the largest observed registered difference against zero-shot and
a small, Level-0-specific exploratory increment over neural-only. A practical
deployment should therefore expose cost, stopping status, and verifier
disagreement rather than display one unqualified quality score.

The local interface demonstrates this inspectable workflow but is not the
frozen experimental system. Its hosted Writer and source-support triage are
useful for exploration, yet their outputs cannot be added to the Phase-5 result
surface or used to estimate a hallucination rate. Any consequential audience or
marketing decision still requires direct human evidence.

## 7.10 Chapter Summary

The results support controllable generation of a human-recognizable
engagement-specificity level within the completed Bangla experiment, while
rejecting stronger interpretations involving natural audience segments or
audience prediction. The principal methodological lesson is equally bounded:
verifier-guided revision can improve the registered outcome measure, but the
widening relationship between the in-loop and sealed outcome verifiers makes
proxy divergence observable rather than eliminating it.

These findings remain constrained by length entanglement, a corpus without
film-linked responses, one generation model family, a convenience sample of
three human evaluators, an outcome verifier whose calibration improvement was
not established, and exploratory rather than confirmatory evidence for the
incremental value of symbolic feedback. Chapter 8 consolidates the resulting
contributions, future research priorities, and final thesis conclusion.
