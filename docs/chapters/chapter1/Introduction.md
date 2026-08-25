# Chapter 1 — Introduction

## 1.1 Background

Audience commentary can inform how a film is interpreted and discussed, but
authentic commentary is generally unavailable before viewers encounter the
film. Large language models (LLMs) can nevertheless generate plausible
audience-like text from a synopsis; recent work has evaluated this capability
specifically for movie-review generation [@b12]. Generation alone, however,
does not establish that an output consistently expresses a requested property
or provides a credible proxy for real audience reception. Research on synthetic
audiences likewise warns that fluent outputs may reproduce bias, respond
unreliably to prompt wording, hallucinate characteristics, or invite
anthropomorphic interpretations that the evidence does not support [@b1].

This distinction between generation and control motivates the present study.
The task is not merely to ask an LLM for a Bangla cinema comment, but to define
a response property that people can recognize, generate responses at a
requested level of that property, and evaluate the result without allowing the
same scoring mechanism to both steer and certify the output. Classifier-guided
generation provides a relevant precedent for conditioning text on a desired
attribute [@b11], but the present setting additionally requires a
language-specific construct, bounded revision, and an evaluator isolated from
the generation loop.

Bangla provides a useful and demanding context for this problem. BanglaBERT
offers a Bangla-specific pretrained encoder [@b2], while Language-Agnostic BERT
Sentence Embedding (LaBSE) provides multilingual sentence representations
[@b3]. The primary review resource used in this thesis is the 5,000-row *Raw
Bangla Movie Review Comment Dataset for Sentiment Analysis and Natural Language
Processing* [@b4]. The reviews are short and sentiment-labelled, but the dataset
contains no movie-title field, audience demographics, or row-level record of
the original collection source. It can therefore support a bounded study of
textual response patterns, but not film-linked audience modelling or claims
about demographic audience groups.

## 1.2 Motivation

A prompt can request a general or a detailed response, but instruction alone
does not demonstrate that the requested distinction has been realized. The
target may be ill-defined, a model may rely on an unintended cue such as text
length, and repeated revision may optimize a scorer without improving the
underlying property. Intrinsic self-correction is also unreliable when a model
revises its own answer without dependable external feedback [@b5; @b6]. These
problems make evaluation part of the research question rather than a final
reporting step.

The study consequently adopts two restrictions. First, it treats generated
responses as controlled textual artefacts, not predictions of what real viewers
will say. Second, the evaluator used to guide revision is separated from the
evaluator used to score final outcomes. This separation is necessary because
optimization against a visible evaluator can exploit its blind spots, a form
of proxy gaming documented in evaluator stress tests [@b7]. The thesis asks
whether this risk can be made observable in a controlled Bangla generation
setting rather than hidden inside a single score.

## 1.3 Problem Statement

The research problem has three connected parts. First, a meaningful response
construct must be recovered from the review corpus without mistaking sentiment,
length, or a corpus artefact for an audience persona. Second, an LLM must be
guided to express a requested level of that construct under a bounded and
auditable procedure. Third, improvement against the in-loop scorer must be
checked by an outcome evaluator that was trained on disjoint data and was never
available to generation.

The corpus analysis ultimately supports an **engagement-specificity
continuum**, not discrete personas. At Level 0, a response is general,
formulaic, or only weakly connected to a particular film detail. At Level 1, it
engages with a specific event, character, relationship, or narrative element.
The two levels are an operational cut through a continuum and are not claimed
to be natural clusters or demographic audience types.

Therefore, this thesis investigates whether a bounded neuro-symbolic
multi-agent workflow can improve the controllability of human-recognizable
engagement-specificity levels in short Bangla cinema responses and reveal
divergence between the in-loop and independent verifiers.

## 1.4 Research Aim and Objectives

The aim of this thesis is to design and evaluate an auditable framework for
controlled Bangla cinema-response generation.

The specific objectives are to:

1. audit, clean, and partition the Bangla review corpus while testing whether
   apparent structure is explained by corpus region, sentiment, length, or a
   residual textual distinction;
2. determine whether two independent native-Bangla annotators can recognize the resulting
   engagement-specificity distinction under a comparative, length-matched
   instrument;
3. develop two verifiers with disjoint data privileges, using Verifier-A for
   generation control and Verifier-B only for outcome scoring;
4. implement a traceable Researcher--Writer--Critic--Reflector workflow with
   R1-only retrieval, neural acceptance, symbolic diagnosis, and bounded
   revision; and
5. evaluate nine registered alternatives against zero-shot generation using
   target-level outcomes, computational cost, human judgment, diversity,
   distributional diagnostics, and verifier-divergence analysis.

## 1.5 Research Questions

The study addresses four research questions:

- **RQ1:** Can a meaningful response distinction be recovered from unlabeled
  Bangla reviews and validated as stable and human-recognizable?
- **RQ2:** To what extent do verifier-guided generation and the registered
  prompting, retrieval-augmented generation, self-critique, external-judge,
  and resampling conditions improve target-level controllability over
  zero-shot generation in Bangla?
- **RQ3:** Does adding symbolic validation improve on neural-only and
  symbolic-only mechanisms?
- **RQ4:** Does iteration against Verifier-A create measurable divergence from
  an independent Verifier-B?

These questions concern controllability and evaluation. They do not ask whether
the system predicts audience reception, discovers audience segments, or
forecasts commercial performance.

RQ3 receives a bounded answer. Symbolic-only gating is evaluated within the
registered design, and an exploratory paired comparison directly contrasts the
hybrid and neural-only conditions. The comparison suggests a level-specific
advantage but does not establish overall hybrid superiority.

## 1.6 Overview of the Proposed Approach

The research uses two Bangla resources for different purposes. The review
corpus supports data audit, construct development, retrieval, and verifier
training. A separate set of 120 Bangla Wikipedia film synopses supplies
generation stimuli. The plot and review resources are not merged into
film--review pairs because the review corpus contains no movie-title field.

After cleaning and near-duplicate control, 4,625 reviews form the frozen split
surface. Gold-300 is reserved for human evaluation, R1 supplies retrieval and
Verifier-A, and R2 supplies Verifier-B. Corpus analysis first tests whether an
apparent partition reflects sentiment or corpus-region/style differences.
Construct validation then uses blinded judgments from two independent
native-Bangla annotators to determine whether
the retained distinction is perceptible and whether its direction corresponds
to engagement specificity.

The generation framework follows a bounded
Researcher--Writer--Critic--Reflector sequence. It retrieves same-level examples
from the R1-only index following the general retrieval-augmented generation
principle [@b8], generates a candidate, applies Verifier-A and deterministic
symbolic diagnostics, and converts computed failures into revision guidance.
The workflow permits at most three Writer attempts and retains the attempt-level
trace.

Thirty development plots are used for prompt, threshold, and retry-policy work.
The main experiment uses 90 held-out plots, two requested levels, ten
conditions, and three paired generation seeds, producing 5,400 frozen outputs.
Verifier-B scores the outputs only after generation. The experiment compares
each of the nine registered alternatives with zero-shot generation and reports
active-condition orderings descriptively. A separate output study uses three
adult native-Bangla annotators, blinded to condition, model, and requested
level, to test whether readers can recover the requested level from generated
responses. This three-annotator output study is distinct from the earlier
two-annotator construct-validation study.

## 1.7 Scope and Limitations

The thesis concerns short Bangla cinema responses generated at a requested
engagement-specificity level. It does not model named individuals,
demographics, psychological profiles, or naturally occurring audience
segments. Because authentic reviews cannot be linked to the plot stimuli, the
study cannot validate film-specific audience realism or individual preference.
Generated responses are therefore research artefacts for controlled
exploration, not substitutes for audience research.

The submitted experiment addresses the Bangla arm of the registered design.
Its three generation seeds are paired sensitivity blocks rather than
independent replications. Human evaluation establishes recovery of the
requested level on a balanced subset; it does not establish general quality,
naturalness, factual support, or audience preference. Verifier-B is an isolated
outcome proxy, not human ground truth, and improvement in its calibration was
not established on the available development sample.

## 1.8 Contributions

The thesis makes six bounded contributions:

1. **A human-validated Bangla response construct.** It replaces the rejected
   persona interpretation with two operational levels on an
   engagement-specificity continuum while retaining the negative
   clusterability evidence and the failed first human instrument.
2. **A dual-verifier isolation protocol.** Verifier-A controls generation from
   R1, whereas the cross-family Verifier-B is trained on disjoint R2 data and is
   prohibited from entering the loop.
3. **A bounded and auditable generation workflow.** The
   Researcher--Writer--Critic--Reflector design combines R1-only retrieval,
   neural acceptance, deterministic symbolic diagnosis, explicit stopping
   rules, and persistent attempt traces.
4. **A controlled evaluation protocol.** Ten conditions are evaluated on the
   same plots and paired seeds with explicit computational accounting,
   including prompting, retrieval, self-critique, external judging, and
   compute-matched resampling controls.
5. **An observable proxy-divergence diagnostic.** Same-case transitions compare
   the in-loop and outcome verifiers, revealing when both scores improve but
   the visible scorer improves more.
6. **A measured separation of symbolic diagnosis from adjudication.** The
   symbolic component identifies failed rules and supports revision, but the
   held-out weight study does not establish independent predictive value, so it
   is not used to decide acceptance.

Together, these contributions concern controllability, evaluator isolation,
and auditability. They do not establish that the framework predicts real
audience reception or that a multi-agent arrangement is superior to every
single-model alternative.

## 1.9 Organization of the Thesis

Chapter 2 reviews synthetic audiences, controllable generation,
self-correction, retrieval, neuro-symbolic diagnosis, evaluator gaming, Bangla
NLP, and human evaluation, and then states the research gap. Chapter 3 describes
the review and plot resources, corpus audit, frozen data split, construct
analysis, and human validation. Chapter 4 develops and evaluates Verifier-A and
Verifier-B and documents their isolation. Chapter 5 presents the proposed
workflow, experimental conditions, and development-stage threshold analysis.
Chapter 6 reports the main experiment, paired comparisons, human evaluation,
and verifier-divergence results. Chapter 7 interprets the findings and discusses
validity threats and ethical boundaries. The planned Chapter 8 will summarize
the conclusions, contributions, limitations, and directions for future work.
