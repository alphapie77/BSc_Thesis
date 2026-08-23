# Chapter 7 — Discussion and Limitations

> **Draft standing.** This discussion is constrained to verified Bangla results.
> It separates empirical findings from interpretation and organizes limitations
> under construct, internal, external, and statistical-conclusion validity.

## 7.1 What the experiment establishes

The central positive finding is not that a language model can reproduce a real
audience. It is that an auditable generation system can make Bangla cinema
comments more consistent with a requested engagement-specificity level than a
zero-shot prompt. All nine registered alternatives improve independent
Verifier-B target probability over zero-shot, and the largest registered effect
is obtained by a neural gate whose correction feedback includes symbolic
diagnostics. On a separately frozen 100-item subset, native-Bangla readers match
the requested level in 91.33% of judgments with 88% unanimous three-way
agreement.

The evidence is strongest when the computational and human results are read
together but not collapsed. Verifier-B covers the complete 5,400-case surface
under a fixed outcome scorer. Human evaluation tests whether the requested
distinction is actually recoverable by readers on a smaller balanced subset.
Neither source alone licenses a broad claim: the automatic scorer is not a human
oracle, and the human sample is not large enough for condition ranking.

The second substantive finding is negative but useful. Repeated optimization
against Verifier-A increases the same-case A–B gap in the neural and
neural-plus-symbolic loops. This demonstrates why a held-out outcome scorer is a
load-bearing design element rather than redundant evaluation. Recent work on
evaluator stress testing reaches the same methodological conclusion: improvement
against a proxy must be separated from improvement in the intended construct,
and invariance or independent checks are needed to expose exploitable sensitivity
[@shihab2025est]. The present study observes divergence; it does not claim to
identify the exact linguistic strategy responsible for every divergence.

## 7.2 Interpretation by research question

### 7.2.1 RQ2: external verification and controllability

The completed Bangla arm supports the proposition that additional control
mechanisms improve target-level matching over zero-shot. Yet “external trained
verification” is not the only successful mechanism: few-shot prompting,
RAG-only generation, self-critique, hosted judging, and blind resampling all
produce positive registered effects. The result should therefore be framed as
comparative evidence about a family of controls, not as proof that only the
proposed architecture can work.

The trained loop offers a favorable quality–compute pattern relative to the
three-call self-critique controls. Neural-plus-symbolic feedback uses roughly
1.63–1.89 generation calls per case while the two self-critique variants use
three. Nevertheless, the thesis does not reduce quality and cost to one
unregistered composite score. Depending on deployment priorities, blind
resampling or a hosted judge may remain attractive alternatives.

### 7.2.2 RQ3: the role of symbolic knowledge

The experiment rejects a strong interpretation in which symbolic gating is
sufficient. The symbolic-only loop fails to improve Level-0 accuracy over
RAG-only and gives up on more than half of Level-1 cases. Symbolic information
is more plausible as a diagnostic language for correction than as the primary
acceptance mechanism. This interpretation matches the system design: the neural
model supplies a learned decision signal, while symbolic rules name observable
failure modes for the Reflector.

However, neural-plus-symbolic and neural-only were not directly contrasted in
the frozen inferential family. Their descriptive difference cannot be upgraded
after inspection into a confirmatory hybrid-superiority claim. The defensible
conclusion is therefore that the combined condition performs strongly and that
symbolic-only gating is inadequate; the incremental causal value of symbolic
feedback remains unresolved.

### 7.2.3 RQ4: cross-lingual generality

RQ4 is not answered. The English mirror is deliberately deferred rather than
shrunk, translated, or replaced with a non-matched convenience experiment.
Consequently, the thesis cannot claim that verifier guidance helps Bangla more
than English, that Bangla is intrinsically harder, or that the architecture is
language-general. The Bangla-only result remains independently defensible, but
cross-lingual comparison belongs to future work unless the complete frozen
mirror is later executed.

### 7.2.4 RQ5: verifier overoptimization

The widening A–B gap is consistent with Goodhart-style overoptimization. It is
not a direct measure of human-quality decline. Verifier-B may have its own blind
spots, its calibration improvement was not established, and later attempts are
selected precisely because earlier drafts failed. The analysis mitigates the
last issue through same-case adjacent transitions, but it cannot make B ground
truth. The correct claim is that optimization changes the relationship between
the in-loop and held-out scorers in a direction expected under proxy gaming.

## 7.3 Construct validity

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
as recurring threats [@lappas2026syntheticaudiences]. Accordingly,
“simulation” in this thesis means **axis-level-conditioned response generation**.
It does not mean substitution for real viewers, prediction of individual
opinions, box-office forecasting, or estimation of a film's audience mix.

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

The English arm is absent, so no multilingual robustness claim is available.
Tokenizer fertility, model availability, and register behavior differ across
languages; transferring the Bangla effect without executing the matched mirror
would conflate these factors.

## 7.6 Statistical-conclusion validity

The primary automated comparisons use 540 paired cases per condition and
10,000-resample paired bootstrap intervals, with Benjamini–Hochberg correction
across the nine frozen comparisons. This is substantially more informative than
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
In particular, neural-plus-symbolic feedback cannot be declared significantly
better than neural-only from their two zero-shot contrasts. Adding that test now
would be post-hoc. The thesis reports the descriptive ordering and leaves the
incremental comparison to a future preregistered study.

## 7.7 Measurement limitations

Verifier-B calibration improvement was not established, so its probabilities
should be read as fixed scorer outputs rather than perfectly calibrated empirical
probabilities. The realism analysis also remains incomplete: sentiment
Jensen–Shannon divergence was not computed because no independent registered
generated-text sentiment scorer existed. Reusing the target-level verifier for
sentiment would have mixed constructs.

LaBSE-feature MAUVE is reported only as sensitivity evidence. With 270 texts per
distribution and a non-default feature representation, its absolute values are
not comparable to default GPT-2-feature MAUVE reported in English benchmarks.
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

The institutional ethics determination remains pending and must be stated
accurately before submission. Completion times and substantive evaluator
feedback were not present in the returned CSVs and have not been inferred. The
final HEDS 3.0 package should preserve these fields as unknown unless the
participants voluntarily report them.

Generated cinema comments may reproduce stereotypes, offensive language, or
incorrect plot claims. The system should therefore be treated as a research and
pre-writing aid, not as evidence about real communities and not as an autonomous
decision-maker for casting, marketing, or audience targeting.

## 7.9 Contributions under the bounded claim

Within these limitations, the thesis makes four defensible contributions:

1. It reports a negative clusterability result rather than converting a stable
   geometric cut into unsupported discrete personas.
2. It implements an auditable Bangla multi-agent generation loop with a strict
   in-loop/outcome-verifier wall and ten matched conditions.
3. It demonstrates both improved requested-level controllability and measurable
   verifier divergence, showing the benefit and risk of verifier-guided revision
   in the same experiment.
4. It releases a reproducible analysis trail that joins complete computational
   evidence with blinded native-speaker validation while retaining negative and
   missing results.

## 7.10 Future work

The first priority is the complete matched English mirror, executed only if time
permits and without merging English data into Bangla training, retrieval, or
clustering. That experiment would answer RQ4 and quantify cross-lingual effects
alongside tokenizer fertility rather than attributing raw gaps to language.

A second study should preregister direct active-system contrasts, especially
neural-plus-symbolic versus neural-only, with adequate power for the incremental
effect. A larger human sample should allocate enough unique items per condition
to evaluate system-specific target match, overall quality, and source-grounded
plot faithfulness as separate criteria. Evaluator-stress perturbations could
also test whether the observed A–B divergence follows length, register,
formatting, or other exploitable cues.

Finally, film-linked human response data would be required for any move from
corpus-level controlled generation to genuine pre-release audience prediction.
Until such data exist, the appropriate application is transparent hypothesis
generation and interface-assisted exploration, with authentic audience research
remaining the validation standard.

## 7.11 Chapter summary

The results support a bounded claim: the proposed framework improves control of
a human-recognizable engagement-specificity axis in Bangla cinema comments, and
its held-out verifier reveals divergence that a single in-loop score would hide.
They do not support discrete audience personas, length-neutral control,
cross-lingual superiority, film-level realism, or replacement of human audiences.
Preserving those boundaries is not merely cautious wording; it is the difference
between the experiment that was actually run and a stronger experiment that
remains future work.

