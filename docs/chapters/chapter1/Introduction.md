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

The study consequently adopts two design principles. First, it treats generated
responses as controlled textual artefacts rather than predictions of what real
viewers will say. Second, the evaluator used to guide revision is separated from
the evaluator used to score final outcomes. This separation is necessary because
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
multi-agent workflow can improve control of the human-recognizable
engagement-specificity distinction in short Bangla cinema responses and reveal
divergence between the in-loop and independent verifiers.

## 1.4 Research Aim and Objectives

The aim of this thesis is to design and evaluate an auditable framework for
controlled Bangla cinema-response generation.

The specific objectives are to:

1. audit, clean, and partition the Bangla review corpus while testing whether
   apparent structure is explained by corpus region, sentiment, length, or a
   residual textual distinction;
2. determine whether independent native-Bangla annotators can recognize the
   resulting engagement-specificity distinction under a comparative,
   length-matched instrument;
3. develop two verifiers with disjoint data privileges, using Verifier-A for
   generation control and Verifier-B only for outcome scoring;
4. implement a traceable Researcher–Writer–Critic–Reflector workflow with
   R1-only retrieval, neural acceptance, symbolic diagnosis, and bounded
   revision; and
5. evaluate the registered generation strategies against zero-shot generation
   using paired target-level outcomes and computational diagnostics, while
   separately assessing human recoverability and verifier divergence.

## 1.5 Research Questions

This study addresses the following research questions:

- **RQ1:** Can a meaningful and human-recognizable response distinction be
  derived from Bangla reviews without engagement-specificity labels?
- **RQ2:** To what extent do the registered generation strategies improve
  target-level controllability over zero-shot generation in Bangla?
- **RQ3:** How does neural gating with symbolic diagnostic feedback compare
  with neural-only and symbolic-only mechanisms?
- **RQ4:** Does iterative optimization against Verifier-A produce measurable
  divergence from the independent Verifier-B?

These questions concern the controllability and evaluation of generated
responses. They do not address the prediction of real audience reception, the
discovery of demographic audience segments, or commercial forecasting.

## 1.6 Overview of the Proposed Approach

The study uses two Bangla resources for distinct purposes. The review
corpus supports data audit, construct development, retrieval, and verifier
training. A separate set of 120 Bangla Wikipedia film synopses supplies
generation stimuli. The plot and review resources are not merged into
film–review pairs because the review corpus contains no movie-title field.

After cleaning and near-duplicate control, 4,625 reviews form the frozen split
surface. Gold-300 is reserved for human evaluation, R1 supplies retrieval and
Verifier-A, and R2 supplies Verifier-B. Corpus analysis first tests whether an
apparent partition reflects sentiment or corpus-region/style differences.
Construct validation then uses blinded judgments from two independent
native-Bangla annotators to determine whether
the retained distinction is perceptible and whether its direction corresponds
to engagement specificity.

The generation framework follows a bounded
Researcher–Writer–Critic–Reflector sequence. The Researcher retrieves
same-level examples from the R1-only index following the general
retrieval-augmented generation principle [@b8]. The Writer generates a
candidate, the Critic applies Verifier-A and deterministic symbolic diagnostics,
and the Reflector converts detected failures into revision guidance. The
workflow permits at most three Writer attempts and retains an attempt-level
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

This thesis focuses on the controlled generation of short Bangla cinema
responses at two engagement-specificity levels. The generated responses are
treated as research artefacts rather than predictions of real audience
behaviour.

The principal limitations are:

- the source reviews cannot be linked to individual films or audience groups;
- the empirical evaluation covers only Bangla cinema responses;
- the three generation seeds provide paired sensitivity blocks rather than
  independent replications;
- human evaluation measures target-level recoverability, not general quality,
  naturalness, factual support, or audience preference; and
- Verifier-B is an isolated outcome proxy rather than human ground truth, and
  its calibration improvement was not established.

These limitations are examined in detail in Chapter 7.

## 1.8 Contributions

This thesis makes five principal contributions:

1. A human-validated engagement-specificity construct for short Bangla cinema
   responses.
2. A dual-verifier protocol that separates generation control from outcome
   evaluation through disjoint data access.
3. A bounded and auditable neuro-symbolic multi-agent generation framework.
4. A paired comparative evaluation across ten generation conditions, supported
   by blinded human assessment.
5. An empirical analysis of verifier divergence and the diagnostic role of
   symbolic feedback.

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
and verifier-divergence results. Chapter 7 interprets the findings and examines
validity threats, ethical boundaries, and practical implications. Chapter 8
concludes the thesis by summarizing its findings, contributions, limitations,
and directions for future research.
