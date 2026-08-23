# Chapter 1 — Introduction

## 1.1 Background and motivation

Audience response is an important source of evidence for film interpretation,
promotion, and creative decision-making. Most authentic response data, however,
become available only after a film has reached viewers. During pre-release
development, filmmakers can consult small test audiences or domain experts, but
these processes are comparatively slow and cannot easily explore many
alternative response scenarios. Recent language models offer a practical way
to generate provisional comments from a plot synopsis. Such comments could
support early reflection—for example, by revealing how a general reaction may
differ from one that engages with a particular scene, character, or narrative
choice.

Generated comments are not evidence of what a real audience will think. A
system may produce fluent persona-like language while remaining sensitive to
prompt wording, reproducing stereotypes, or inventing unsupported audience
characteristics. A recent systematic review identifies hallucination, bias,
prompt sensitivity, and anthropomorphic overinterpretation as recurring risks
in synthetic-audience research [@b1]. Consequently, this thesis does not attempt
to replace viewers or forecast box-office outcomes. It studies a narrower
question: whether short Bangla cinema responses can be generated so that they
reliably express a requested, human-recognizable level of engagement
specificity.

Bangla is a useful and demanding setting for this question. Although the
BanglaBERT pretrained encoder and Language-Agnostic BERT Sentence Embedding
(LaBSE) multilingual sentence representations are available [@b2; @b3],
resources for controlled Bangla generation and its evaluation
remain limited. The primary resource used here is the 5,000-row *Raw Bangla
Movie Review Comment Dataset for Sentiment Analysis and Natural Language
Processing* [@b4]. It contains short sentiment-labelled comments but no
movie-title field, demographic attributes, or row-level record of the original
collection source. These limitations prevent film-linked audience modelling,
yet the corpus can support a carefully bounded study of recurring textual
response patterns.

## 1.2 Research problem

Controlling a response style requires more than stating the desired style in a
prompt. First, the target distinction must be empirically defensible. A stable
partition of embedding space may reflect source, sentiment, or length rather
than a meaningful audience-related construct. Second, a generator needs a
reliable signal indicating whether its output realizes the requested
distinction. Language models do not consistently correct their own errors when
feedback is generated from the same unsupported reasoning process [@b5; @b6].
Third, repeated optimization against a single evaluator can improve that
evaluator's score while exploiting its blind spots, a form of proxy gaming
[@b7].

This thesis addresses these problems together. It first examines whether a
meaningful distinction can be recovered from unlabeled Bangla reviews without
mistaking a corpus artifact for an audience persona. The surviving distinction
is operationalized as an **engagement-specificity continuum**. At Level 0, a
comment is general, formulaic, or weakly tied to a particular film detail. At
Level 1, it engages with a specific aspect, event, character, or construction
element. The two levels are an operational cut through a continuum; they are
not asserted to be natural clusters or demographic audience groups.

The generation problem is then framed as verifier-guided control. A Writer
produces a candidate response, an in-loop Verifier-A evaluates target-level fit,
and bounded Critic–Reflector feedback may trigger revision. Retrieval supplies
external examples following the general retrieval-augmented generation
principle [@b8]. A second model, Verifier-B, is trained on disjoint data and
kept outside generation. Its role is to reveal whether improvement against the
in-loop proxy transfers to a separately trained outcome scorer.

The central problem investigated in this thesis is therefore:

> Can a bounded neuro-symbolic multi-agent workflow improve control of a
> human-recognizable engagement-specificity level in short Bangla cinema
> responses, relative to prompting, retrieval, self-critique, external judging,
> and resampling controls, while making verifier-induced proxy divergence
> observable?

## 1.3 Research questions

The study is organized around four research questions:

- **RQ1:** Can a meaningful response distinction be recovered from unlabeled
  Bangla reviews and validated as stable and human-recognizable?
- **RQ2:** Does an external trained verifier improve target-level controllability
  over zero-shot, few-shot, retrieval-augmented generation (RAG)-only, and
  self-critique baselines?
- **RQ3:** Does adding symbolic validation improve on neural-only and
  symbolic-only mechanisms?
- **RQ4:** Does iteration against Verifier-A create measurable divergence from
  an independent Verifier-B?

Table 1.1 states the evidential status of these questions after the completed
Bangla study. The bounded answers prevent the questions from being read more
broadly than the experiment permits; their supporting analyses appear in later
chapters.

**Table 1.1. Research questions, evidential standing, and bounded answers**

| RQ | Evidence standing | Bounded answer | Main evidence chapter |
|---|---|---|---:|
| RQ1 | Qualified support | A reproducible Region-A continuum cut is human-recognizable as engagement specificity, but it is neither a discovered persona nor a naturally separated cluster, and its structural signature does not replicate in Region B. | 3 |
| RQ2 | Supported within Bangla, with attribution limits | All nine registered active conditions improve held-out Verifier-B target probability over zero-shot, and humans can recover the requested level. This supports controllability, not audience prediction or exclusive superiority of the proposed loop. | 6–7 |
| RQ3 | Mixed; incremental value unresolved | Symbolic-only gating is weak and neural gating with symbolic feedback performs strongly against zero-shot, but no registered hybrid-versus-neural contrast establishes the incremental contribution of symbolic feedback. | 5–7 |
| RQ4 | Supported as a diagnostic | On continuing cases, neural-loop revisions widen the Verifier-A–Verifier-B gap in the direction expected under proxy overoptimization; this is not proof of declining human-perceived quality. | 6–7 |

## 1.4 Research aim and objectives

The overall objective is to design and evaluate an auditable framework for
controlled Bangla cinema-response generation. It is divided into five goals:

1. audit, clean, and partition the Bangla review corpus while preserving its
   script and testing whether apparent structure is explained by source,
   sentiment, length, or a stable residual distinction;
2. test whether native-Bangla annotators can recognize the resulting
   engagement-specificity distinction under a comparative, length-matched
   instrument;
3. develop two lightweight verifiers with disjoint data privileges, using
   Verifier-A for generation control and Verifier-B only for outcome scoring;
4. implement a traceable Researcher–Writer–Critic–Reflector workflow with
   R1-only retrieval, neural gating, symbolic diagnosis, and bounded revision;
5. compare the proposed mechanism with nine registered alternatives using
   target-level outcomes, computational cost, human judgment, diversity,
   distributional diagnostics, and verifier-divergence analysis.

## 1.5 Overview of the research design

The research uses two Bangla resources for separate purposes. The Mendeley Data
V3 review workbook provides observations for corpus audit, construct
development, retrieval examples, and verifier training. A second resource
comprises 120 plot synopses harvested from exact revisions of Bangla Wikipedia
film articles. These synopses serve only as generation stimuli. Plot text is
never inserted into review clustering or verifier training, and the two
resources are not merged into a synthetic film–review dataset.

After cleaning, near-duplicate control produces a frozen 4,625-review surface,
divided into Gold-300, R1, and R2. Gold-300 is evaluation-only; R1 supplies the
retrieval index and Verifier-A; R2 supplies Verifier-B. Full-corpus clustering
is rejected because it recovers corpus source more strongly than the intended
construct. Analysis proceeds within Region A, where a reproducible but weakly
separated two-way cut is studied. An initial ordinal human instrument fails its
preregistered reliability gate. A second comparative instrument, using fresh
R1 items and length matching, establishes that the distinction is recognizable
and supports its interpretation as engagement specificity.

The generation workflow contains four functional roles. The Researcher obtains
same-level examples from the frozen R1-only index. The Writer generates a short
Bangla response from the plot, target level, and permitted context. The Critic
applies Verifier-A and symbolic diagnostics, and the Reflector converts failures
into bounded revision guidance. This is a controlled multi-agent workflow
rather than an open-ended autonomous system: roles have fixed privileges,
stopping rules, thresholds, and data walls.

Prompts, thresholds, and retry policies are fixed using 30 development plots.
The main experiment crosses 90 held-out plots with two requested levels, ten
conditions, and three paired generation seeds. The resulting 5,400 responses
are frozen before outcome scoring. Verifier-B then scores every case without
having influenced generation. Paired comparisons evaluate the nine active
conditions against zero-shot, while transition-level analysis examines
divergence between the verifiers. Finally, three adult native-Bangla annotators
evaluate a frozen, balanced 100-item subset under blinded condition labels.

## 1.6 Contributions

The thesis makes seven bounded contributions:

1. **A source-aware corpus audit** showing that a stable embedding partition can
   primarily recover corpus provenance and that algorithmic stability alone is
   insufficient evidence of audience personas.
2. **A human-recognizable response construct** defining a two-level
   engagement-specificity continuum while retaining both the failed ordinal
   instrument and the successful comparative validation.
3. **A dual-verifier isolation design** in which Verifier-A is a frozen LaBSE
   logistic probe trained from R1, whereas Verifier-B is a BanglaBERT model
   trained on disjoint R2 data and prohibited from generation.
4. **An auditable neuro-symbolic workflow** combining R1-only retrieval, neural
   acceptance, symbolic failure descriptions, bounded feedback, and persistent
   attempt traces.
5. **A matched ten-condition experiment** containing 5,400 cases across 90
   held-out plots, two target levels, ten conditions, and three paired seeds.
6. **A held-out-verifier proxy diagnostic** showing that improvement against
   Verifier-A can coincide with a widening gap from Verifier-B during same-case
   neural-loop transitions.
7. **Blinded human evaluation of generated outputs** in which three
   native-Bangla annotators provide 300 judgments on a balanced 100-item subset,
   yielding 0.9133 pooled target-level match and 0.88 raw three-way agreement.

These contributions concern controllability, evaluation, and auditability. They
do not establish that generated responses represent the distribution of a real
film audience.

## 1.7 Scope and delimitations

This thesis addresses short Bangla cinema-response generation at a requested
engagement-specificity level. It does not model named individuals,
demographics, psychological profiles, or naturally occurring audience segments.
Because the review corpus contains no movie-title field, generated responses
cannot be compared with authentic reviews of the same film. The study therefore
makes no claim about film-level realism, audience composition, box-office
performance, or individual preference.

The submitted study contains four Bangla research questions. The three
generation seeds are paired sensitivity blocks, not independent replications.
Human evaluation establishes recovery of the requested level on a
balanced subset; it does not rate general quality, naturalness, factual plot
support, or audience preference. Likewise, Verifier-B is a held-out proxy with
unestablished calibration improvement, not human ground truth.

Here, *pre-release* refers to using plot synopses before authentic post-release
comments are available. Generated responses are intended for transparent
research and pre-writing exploration. They should not substitute for audience
research or be presented as evidence about real Bangla-speaking communities.

## 1.8 Organization of the thesis

Chapter 2 reviews synthetic-audience research, controllable generation,
self-correction, retrieval-augmented generation, neuro-symbolic validation,
verifier gaming, Bangla NLP, and human evaluation. Chapter 3 describes the
review and plot resources, corpus audit, frozen partition, clusterability
analysis, and human validation of the engagement-specificity construct. Chapter
4 develops Verifier-A and Verifier-B and documents their performance,
calibration, and isolation wall. Chapter 5 presents the bounded multi-agent
workflow, ten experimental conditions, threshold selection, and development
loop dynamics. Chapter 6 reports the frozen Bangla experiment, paired analyses,
human evaluation, diversity, realism diagnostics, and verifier divergence.
Chapter 7 interprets the findings, answers the research questions, and discusses
validity threats, ethical boundaries, practical implications, future work, and
the final conclusion.

## 1.9 Chapter summary

This chapter has framed the thesis as a controlled-generation study rather than
an attempt to simulate or replace real audiences. It identified three linked
challenges—construct validity, reliable correction, and proxy optimization—and
translated them into four research questions and five operational objectives.
The study addresses these questions through a frozen Bangla data design,
disjoint in-loop and outcome verifiers, a bounded neuro-symbolic workflow,
matched controls, and human evaluation. The next chapter examines the evidence
from which this design and its research gap arise.
