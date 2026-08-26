# Chapter 1 — Introduction

## 1.1 Background: pre-release audience response and Bangla cinema

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

This scarcity has a methodological consequence that shapes the whole study. The
literature review in Chapter 2 identified no directly comparable system that
combines Bangla cinema-response generation, a task-trained in-loop verifier,
bounded refinement, and a separately trained outcome verifier isolated from
generation. Nor was an external benchmark found for scoring the specific
property studied here. The experiment therefore uses internally implemented
controls under shared stimuli, paired seeds, and explicit budget accounting.
Where no external reference is available, credibility depends on the
inspectability of the measurement procedure. The framework consequently uses
fixed privileges, explicit stopping rules, and persistent attempt traces, and
its measurement apparatus is developed in a chapter of its own.

## 1.2 Motivation and the limits of synthetic audiences

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

Narrowing the question in this way changes what counts as success. Because
authentic reviews cannot be linked to the plot stimuli, the study cannot
validate film-linked realism or audience representativeness. It can report only
corpus-level distributional diagnostics as sensitivity evidence. Its primary
test is narrower: whether one declared property of the text is realized on
request and can be recovered by a reader who was not told what was requested.
That is a weaker claim than audience simulation, and it is one that the corpus
and evaluation design can support.

## 1.3 Research problem and central question

Controlling a response style requires more than stating the desired style in a
prompt. First, the target distinction must be empirically defensible. A stable
partition of embedding space may reflect source, sentiment, or length rather
than a meaningful audience-related construct. Second, a generator needs a
reliable signal indicating whether its output realizes the requested
distinction. Language models do not consistently correct their own errors when
feedback is generated from the same unsupported reasoning process [@b5; @b6].
Third, repeated optimization against a single evaluator can improve that
evaluator's score while exploiting its blind spots, a form of proxy gaming
observed under evaluator stress tests [@b7].

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
> human-recognizable engagement-specificity level over zero-shot generation in
> short Bangla cinema responses, and how does it compare descriptively with
> registered prompting, retrieval, self-critique, external-judge, and resampling
> controls while making verifier-induced proxy divergence observable?

## 1.4 Research questions

The study is organized around four research questions:

- **RQ1:** Can a meaningful response distinction be recovered from unlabeled
  Bangla reviews and validated as stable and human-recognizable?
- **RQ2:** To what extent do verifier-guided generation and the registered
  prompting, retrieval-augmented generation (RAG), self-critique,
  external-judge, and resampling controls improve target-level controllability
  over zero-shot generation in Bangla?
- **RQ3:** What role does symbolic information play when used for acceptance
  gating and for diagnostic feedback within verifier-guided Bangla response
  generation?
- **RQ4:** Does iteration against Verifier-A create measurable divergence from
  an independent Verifier-B?

Table 1.1 states the evidential status of these questions after the completed
Bangla study. The bounded answers prevent the questions from being read more
broadly than the experiment permits; their supporting analyses appear in later
chapters.

**Table 1.1. Research questions, evidential standing, and bounded answers**

| RQ | Evidence standing | Bounded answer | Main evidence chapter |
|---|---|---|---:|
| RQ1 | Qualified support | A reproducible Region-A continuum cut is human-recognizable as engagement specificity under length-matched comparative judgment, but it is neither a discovered persona nor a naturally separated cluster, and its structural signature does not replicate in Region B. | 3 |
| RQ2 | Supported within Bangla, with attribution limits | All nine registered active conditions improve out-of-loop Verifier-B target probability over zero-shot, and humans can recover the requested level. The result supports controllability but does not identify the verifier as the sole cause, establish active-condition superiority, or support audience prediction. | 6–7 |
| RQ3 | Roles differentiated; incremental value remains exploratory | Symbolic-only gating is weak, whereas symbolic rules remain useful as diagnostic feedback under a neural gate. The combined condition performs strongly against zero-shot, and an exploratory paired comparison shows a small target-probability increment concentrated at Level 0, without establishing a causal level-specific advantage or overall hybrid superiority. | 5–7 |
| RQ4 | Supported as a diagnostic | On continuing cases, revisions in the two neural-gated loops widen the Verifier-A–Verifier-B gap in the direction expected under proxy overoptimization; this is not proof of declining human-perceived quality and does not make Verifier-B an oracle. | 6–7 |

## 1.5 Research aim and objectives

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
5. evaluate nine registered active conditions against zero-shot, compare the
   active conditions descriptively, and report target-level outcomes,
   computational cost, human judgment, diversity, distributional diagnostics,
   and verifier-divergence analysis.

## 1.6 Mapping of objectives, research questions, chapters, and contributions

Table 1.2 records which chapter discharges each objective, which research
question it serves, and which contribution it supports. The mapping is stated
explicitly because the five objectives, the four research questions, and the six
contributions of §1.8 are not in one-to-one correspondence: two objectives
jointly establish the construct that a single research question asks about, and
the final objective supplies evidence for three questions at once.

**Table 1.2. Objectives mapped to research questions, chapters, and contributions**

| Objective (§1.5) | Research question | Principal chapter | Contribution |
|---|---|---:|---|
| 1 — corpus audit, frozen partition, confound testing | RQ1 | 3 | C3 |
| 2 — human recognizability of the distinction | RQ1 | 3 | C3 |
| 3 — two verifiers with disjoint data privileges | instruments for RQ2 and RQ4 | 4 | C1, C4 |
| 4 — traceable Researcher–Writer–Critic–Reflector workflow | RQ2, RQ3 | 5 | C2, C6 |
| 5 — nine registered comparisons against zero-shot, with descriptive active-condition contrasts | RQ2, RQ3, RQ4 | 6 | C1, C2, C5 |

No objective is owned by Chapters 1, 2, 7, or 8. Those chapters respectively
frame the problem, derive the gap from prior work, interpret the findings, and
state the conclusions.

## 1.7 Overview of the research design

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

The generation workflow contains four functional roles, two of which issue no
language-model call. The Researcher retrieves same-level examples from the
frozen R1-only index. The Writer generates a short Bangla response from the
plot, target level, and permitted context. The Critic applies Verifier-A and
deterministic symbolic diagnostics, deciding acceptance without generating text.
The Reflector converts computed failures into bounded revision guidance. This is
a controlled multi-agent workflow rather than an open-ended autonomous system:
roles have fixed privileges, stopping rules, thresholds, and data walls, and the
Critic's determinism is itself part of the measurement apparatus rather than a
simplification of it.

Prompts, thresholds, and retry policies are fixed using 30 development plots.
The main experiment crosses 90 held-out plots with two requested levels, ten
conditions, and three paired generation seeds. The resulting 5,400 responses
are frozen before outcome scoring. Verifier-B then scores every case without
having influenced generation. Paired comparisons evaluate the nine active
conditions against zero-shot, while transition-level analysis examines
divergence between the verifiers. Finally, three adult native-Bangla annotators
evaluate a frozen, balanced 100-item subset under blinded condition labels.

## 1.8 Contributions

The thesis makes six bounded contributions. Each is stated together with the
result that supports it, and each is limited by what that result cannot show.

**C1 — A verifier-isolation protocol, and the proxy divergence it makes
visible.** Verifier-A, a frozen LaBSE logistic probe trained on R1, is the only
scorer permitted to influence generation; Verifier-B, a BanglaBERT model
fine-tuned on the disjoint R2 partition, scores outcomes and never enters the
loop. The separation is enforced mechanically rather than by convention, which
is what makes a retrospective comparison of the two measures meaningful. On
identical continuing cases, a first revision under neural gating raises
Verifier-A by +0.4835 and Verifier-B by +0.3006, widening the gap between them
by +0.1828 over 147 cases; under the proposed loop the same transition widens
the gap by +0.1415. Both scorers agree that the revisions helped, and they
disagree about how much — a disagreement that a single-evaluator design would
have absorbed without trace.

**C2 — A bounded workflow evaluated under accounted compute.** In the frozen
experiment the framework attains the largest registered improvement over
zero-shot, +0.2570 with a 95% paired-bootstrap interval of [+0.2151, +0.2987],
at 1.630–1.889 mean generator calls per case, while both fixed-iteration
self-critique conditions spend exactly 3.000. A resampling condition was given a
per-case token budget matched to the proposed loop's realized generator cost,
registered in configuration before generation rather than selected afterwards.
Because the registered inferential family contains only comparisons against
zero-shot, orderings among active conditions are reported as descriptive.

**C3 — A construct validation that rejected its own first result.**
Full-corpus structure recovered the collection source of a review with 93.3%
accuracy rather than anything audience-related, so the discrete-persona reading
was abandoned rather than retained; analysis moved to a reproducible two-level
cut within Region A, with Region B held as a negative control. The first human
instrument, an ordinal rating task, failed its preregistered reliability gate
and is reported rather than discarded. A second comparative instrument, on fresh
length-matched R1 items, established recognizability at 0.78 and 0.84 against a
0.25 chance rate.

**C4 — A circularity result published together with the number it disarms.**
Verifier-A reaches 0.9866 macro-F1 with a single error on 82 development items,
and the thesis reports this as a structural consequence rather than a modelling
achievement: the two-level label was obtained by clustering the same LaBSE
embeddings the probe reads, so the label is close to linearly separable in that
space by construction. The registered consequence is that the seven-arm backbone
comparison supports no claim about backbones.

**C5 — Blinded human validation of requested-level recovery.** Three adult
native-Bangla annotators produced 300 judgments on a frozen, balanced 100-item
subset while blinded to condition, model, requested level, replicate, and
automatic scores. Pooled recovery of the requested level was 0.9133 with a
bootstrap interval of [0.8667, 0.9567], raw three-way agreement was 0.88, and
nominal Krippendorff α was 0.8405. This establishes that the requested level is
humanly recoverable; it does not rate quality, naturalness, or plot fidelity.

**C6 — Separation of symbolic diagnosis from symbolic adjudication.** The
symbolic component names which rule a candidate failed and localizes revision
guidance; it is not permitted to decide acceptance. That placement follows a
measurement rather than a preference. Every grouped held-out fold selected a
mixture weight of 1.0 on the neural score, with mean change in area under the
curve of 0.0000 in both the length-controlled and free-length conditions, while
verdict sensitivity across the weight grid was not flat. The registered outcome
is therefore that no predictive-value claim for the symbolic component is
licensed in either direction, and the component is retained only for the
diagnostic role the revision step requires.

These contributions concern controllability, evaluation, and auditability. None
of them establishes that generated responses represent the distribution of a
real film audience. None establishes that a multi-agent arrangement outperforms
a single model at this task either: no active-versus-active contrast was
registered, and the strongest single-model control improved on zero-shot by
+0.2147.

## 1.9 Scope and delimitations

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

## 1.10 Organization of the thesis

Chapter 2 states the methodology under which prior work was selected and then
reviews synthetic-audience research, controllable generation, self-correction,
retrieval-augmented generation, neuro-symbolic validation, verifier gaming,
Bangla NLP, and human evaluation, closing with the research gap. Chapter 3
describes the review and plot resources, the read-only corpus audit, the frozen
partition, the clusterability analysis, and the human validation of the
engagement-specificity construct. Chapter 4 develops Verifier-A and Verifier-B
and documents their performance, calibration, circularity, and isolation wall.
Chapter 5 specifies the bounded workflow as an executable procedure, together
with the ten experimental conditions, threshold selection, and development-loop
dynamics. Chapter 6 reports the frozen Bangla experiment, the planned paired
comparisons, the blinded human evaluation, diversity and realism diagnostics,
and verifier divergence. Chapter 7 interprets the findings, relates them to the
reviewed literature, and states the validity threats and ethical boundaries.
Chapter 8 states each contribution against its supporting result, summarizes the
limitations, and sets out the future work the design leaves open.

## 1.11 Chapter summary

This chapter has framed the thesis as a controlled-generation study rather than
an attempt to simulate or replace real audiences. It identified three linked
challenges—construct validity, reliable correction, and proxy optimization—and
translated them into four research questions and five operational objectives,
mapped in Table 1.2 onto the chapters that discharge them and the six
contributions they support. The study addresses these questions through a frozen
Bangla data design, disjoint in-loop and outcome verifiers, a bounded
neuro-symbolic workflow, matched controls, and blinded human evaluation. The
next chapter examines the evidence from which this design and its research gap
arise.
