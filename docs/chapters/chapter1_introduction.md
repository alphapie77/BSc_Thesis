# Chapter 1 — Introduction

> **Draft standing.** The exact thesis title remains a researcher decision. This
> chapter uses “axis-level-conditioned response generation” as the scientific
> object and does not assume that the words “Audience Simulation” remain in the
> final title.

## 1.1 Background

Film producers commonly receive extensive audience commentary only after a film
has been released. A controllable text-generation system could provide cheap,
early hypotheses about the kinds of comments that different response styles may
produce. Large language models make such pre-release exploration technically
possible, but an unconstrained prompt does not establish that generated text
follows a meaningful human-recognizable distinction. The problem is sharper for
Bangla, where task-specific generators, evaluation resources, and reproducible
benchmarks are comparatively limited.

This thesis studies a narrow and testable version of that problem. Instead of
claiming to reproduce demographic or psychological audience groups, it controls
an **engagement-specificity axis** in short Bangla cinema comments. Level 0 is a
general or formulaic reaction; Level 1 engages with a particular film aspect,
event, or construction element. The distinction originated from corpus geometry
but is treated as a continuum cut, not as evidence of two naturally separated
personas.

Prompting alone is an incomplete solution. Intrinsic self-correction often fails
when a model lacks reliable external feedback [@huang2024selfcorrect;
@kamoi2024when], while optimizing repeatedly against one evaluator may exploit
that evaluator's blind spots [@shihab2025est]. This motivates a verifier-in-the-
loop design: a Writer generates, a cheap trained Verifier-A gates the draft, a
Critic and Reflector convert failures into correction guidance, and a separately
trained Verifier-B scores outcomes without entering generation.

## 1.2 Problem statement

The study asks whether a cheap external verifier embedded in a
generate–verify–reflect loop improves control of a human-recognizable textual
axis in Bangla cinema responses relative to prompting, retrieval, self-critique,
LLM judging, and matched-compute resampling baselines, while making
verifier-induced overoptimization observable through an independent scorer.

## 1.3 Research questions

- **RQ1:** Can a meaningful response distinction be recovered from unlabeled
  Bangla reviews and validated as stable and human-recognizable?
- **RQ2:** Does an external trained verifier improve target-level controllability
  over zero-shot, few-shot, RAG-only, and self-critique baselines?
- **RQ3:** Does adding symbolic validation improve on neural-only and
  symbolic-only mechanisms?
- **RQ4:** Is the verifier-in-the-loop benefit different under matched Bangla
  and English conditions?
- **RQ5:** Does iteration against Verifier-A create measurable divergence from
  an independent Verifier-B?

RQ4 remains unanswered in the present Bangla-only thesis draft. The English arm
is preserved as future work rather than replaced with an unmatched shortcut.

## 1.4 Objectives

The research has five operational objectives. First, it audits and cleans the
Bangla corpus without altering its script, then tests whether apparent clusters
reflect sentiment, source, length, or a stable latent structure. Second, it
validates the surviving distinction with human comparative judgments. Third, it
trains two methodologically and data-separated lightweight verifiers. Fourth, it
constructs an instrumented multi-agent generation loop and compares ten matched
conditions. Fifth, it evaluates target match, human recoverability, cost,
diversity, realism, and A–B verifier divergence without allowing the outcome
scorer into the loop.

## 1.5 Contributions

This thesis makes the following bounded contributions:

1. A reproducible audit showing that stable K-means partitions can be corpus
   detectors or geometric cuts without constituting discrete audience personas.
2. A human-validated, two-level engagement-specificity construct: comparative
   judgments achieve 0.78 and 0.84 accuracy against 0.25 chance, with length
   matched within two words.
3. A dual-verifier design in which Verifier-A is a frozen LaBSE probe trained on
   R1 and Verifier-B is a fine-tuned BanglaBERT trained on disjoint R2.
4. An auditable Researcher–Writer–Critic–Reflector loop with R1-only retrieval,
   neural gating, symbolic diagnostic feedback, bounded retries, and complete
   traces.
5. A 5,400-case Bangla experiment covering ten conditions, two axis levels, 90
   held-out plots, and three paired generation replicates.
6. A held-out-verifier Goodhart diagnostic showing that the A–B gap can widen
   during neural-gated revision.
7. Blinded native-speaker validation on a frozen 100-item subset, yielding
   0.9133 pooled target match and 0.88 raw three-way agreement.

## 1.6 Scope

“Simulation” in this work means controlled generation of candidate responses at
a requested engagement-specificity level. The source corpus has no movie-title
column and no review-to-film mapping. The study therefore does not validate
individual opinions, real audience distributions for a film, box-office
outcomes, or demographic personas. Recent synthetic-audience research warns
against hallucination, prompt sensitivity, bias, and anthropomorphic
overgeneralization [@lappas2026syntheticaudiences]; those risks define the scope
boundary rather than appearing only as after-the-fact caveats.

## 1.7 Thesis organization

Chapter 2 reviews controllable generation, self-correction, retrieval,
neuro-symbolic feedback, verifier gaming, Bangla NLP, and human evaluation.
Chapter 3 describes the corpus audit, split, clusterability tests, and human
validation of the axis. Chapter 4 develops the two verifiers and their
calibration evidence. Chapter 5 presents the multi-agent system, threshold
selection, and loop dynamics. Chapter 6 reports the main Bangla experiment and
human evaluation. Chapter 7 discusses implications, validity threats, ethics,
and future work.

