# Chapter 2 — Related Work

This chapter positions the thesis within research on synthetic audiences,
controlled generation, self-correction, retrieval, neuro-symbolic diagnosis,
multi-agent workflows, learned evaluators, Bangla natural language processing,
and human evaluation. Rather than listing techniques in isolation, it examines
what each line of work contributes, what its evidence does not establish, and
why their combination still requires a controlled study. Section 2.1 states how
the literature was identified, so that the gap derived in Section 2.10 can be
assessed as a search result rather than as an assertion.

## 2.1 Review methodology

The review is organised by design decision rather than by publication venue. Its
purpose is not exhaustive coverage of every adjacent field but a check, taken
before each methodological commitment, on whether current work supports,
constrains, or contradicts that commitment. Every work retained below is
therefore attached to a specific decision in the study, and the register that
records those attachments is maintained alongside the thesis as an annotated
bibliography.

Searches were run through Consensus as the primary index, following a standing
project requirement adopted on 8 August 2026 that literature be searched before
a method is proposed or defended rather than afterwards. Queries were issued in
several narrower formulations rather than one broad formulation, because an index
matches terminology rather than intent and a single result page is not a search.
The publication window was set to 2025–2026 first and widened only when the
recent window returned too little; where it was widened, the widening is recorded
with the entry, since a method whose only support is an older paper and a method
for which recent work was never sought are different situations that look
identical in a bibliography. Consensus had exhausted its available search quota
by 11 August 2026, with no reset until 1 September 2026. Searches from that date
onward used alphaXiv and Scite together with primary arXiv and publisher records,
and each affected entry records the substitution rather than presenting the
result as though the preferred index had been used.

Inclusion was decided by function. A work was retained when it defended,
constrained, or refuted a named decision in the study; works that a search
returned but that no decision came to depend on remain in the research register
as evidence that the search was run, and are not cited here. Several searches
changed decisions that had already been taken provisionally, and those reversals
are reported in the chapter where the decision lives rather than presented as if
the final design had been the first one considered. Because the review is
organised this way, it is a design-driven narrative review and not a systematic
review: there is no PRISMA-style screening flow, no second independent screener,
and consequently no screening-agreement statistic. That is a limitation of the
review and is stated rather than implied.

Reading depth is recorded per source at three levels — unread record, abstract or
metadata record, and full text — and no source is cited in the thesis without an
entry in the register. Depth is uneven, and the unevenness is material enough to
state plainly. Sources whose methods, estimators, or thresholds this study adopts
were read in full, and in one case a full reading corrected an attribution made
from an abstract, after which the method was not adopted. Sources cited as
convergent evidence for a claim established elsewhere were in several cases
assessed at record level; where such a source carries weight in the argument
below, the text says what the record supports and does not extrapolate beyond it.
Of the six sources on which the central argument leans most heavily, three were
read in full, one partially, and two at record level.

The resulting profile is sixty-seven distinct works cited across the thesis, of
which forty-one appear in this chapter. Thirty-six of the sixty-seven were
published in 2025 or 2026, reflecting the requirement that recency be treated as
a condition rather than a preference. Six predate 2013; each is the original
statement of a statistic the thesis reports, retained for provenance rather than
as current evidence. The chapter-folder submission bibliography therefore
contains the sixty-seven cited works. The 143-record master research bibliography
additionally preserves the audit trail of searches that did not change the
design; uncited records are not included in the chapter-folder file.

## 2.2 Synthetic audiences and controlled response generation

Language models are increasingly used to approximate audiences, users, or
personas before direct human evidence is available. The attraction is clear: a
single system can generate many inexpensive responses under different
conditions. The methodological difficulty is that behavioural plausibility is
not behavioural validity. A fluent response may resemble an intended persona
without predicting how any real person or population would respond. A recent
systematic review identifies hallucination, bias, prompt sensitivity, limited
ecological validity, and anthropomorphic interpretation as recurring problems
in synthetic-audience studies [@b1]. These concerns are especially important
when generated statements are presented as evidence about communities rather
than as hypotheses for subsequent human research.

Mixture-of-Personas illustrates one approach to population-conditioned
generation: latent or synthesized persona representations are used to steer a
common language model toward diverse response distributions [@b9]. SimAB
extends the synthetic-audience idea to persona-conditioned agents for rapid web
A/B-test evaluation and compares simulated decisions with historical outcomes
[@b10]. Both studies demonstrate how explicit conditioning can broaden the
range of generated responses. Their aims, however, differ from the present
work. They concern population simulation or behavioural prediction, whereas
this thesis controls a textual engagement-specificity level and validates only
whether that level is recognizable in Bangla comments.

Controlled generation provides a second relevant tradition. FUDGE modifies
token probabilities using a learned future discriminator while leaving the
base generator unchanged [@b11]. This establishes that an external classifier
can steer generation without fine-tuning the generator itself. The mechanism is
nevertheless different from a revision workflow: discrimination occurs during
decoding, and a separately trained outcome evaluator is not used to test
whether repeated optimization has exploited the steering model. The present
study therefore treats classifier-guided control as a methodological precursor,
not as an equivalent architecture.

Movie-review generation is a particularly close application domain. Sands et
al. evaluate LLM-generated movie reviews and expose the gap between fluent
persona-conditioned text and evidence that the output represents authentic
audience response [@b12]. That distinction supports using generated comments as
controlled pre-writing hypotheses rather than predicted reviews of a film.

## 2.3 Self-correction and feedback

Iterative refinement is often motivated by the intuition that a language model
can inspect a draft, identify its own mistakes, and improve the answer. Evidence
for this intuition is conditional. Huang et al. show that intrinsic
self-correction—revision without reliable external feedback—does not
consistently improve the reasoning tasks they study and can change correct
answers into incorrect ones [@b5]. Their result is bounded to reasoning
benchmarks, but it reveals a general evaluation problem: generation ability
does not guarantee the ability to judge one's own output. Kamoi et al.'s survey
similarly distinguishes intrinsic feedback from settings in which an oracle,
tool, environment, or separately trained model supplies new information, and
finds stronger support for correction when feedback is externally grounded
[@b6]. The same survey observes that fine-tuning enables self-correction when
large training data is available but remains unexplored for small training data,
which is precisely the regime a verifier trained on a few hundred low-resource
examples occupies.

Self-Refine operationalizes an intrinsic generate–feedback–revise cycle using
the same model [@b13]. Reflexion stores verbal feedback in memory and can draw
that feedback from internal or external signals depending on the task [@b14].
These systems demonstrate the usefulness of explicit intermediate critique,
but their success does not establish that self-generated criticism is accurate
or that improvement is caused by reflection rather than by additional model
calls.

The established alternative to intrinsic revision is a separately trained
verifier. Cobbe et al. introduced this line by training a verifier to judge the
correctness of sampled model completions and returning the candidate the verifier
ranks highest, reporting both that verification improves performance and that it
scales more effectively with additional data than a fine-tuning baseline [@b58].
Huang et al. point to that work as the practical alternative to intrinsic
correction [@b5]. The present study inherits the trained-verifier idea and
departs from it in mechanism: Cobbe et al.'s verifier ranks a fixed pool of
completions, whereas Verifier-A additionally gates a bounded revision loop. The
ranking procedure is not discarded but reconstructed separately as the
blind-resampling control of Chapter 5, so that the ancestor of the method and one
of the baselines it must beat are the same work.

Role placement is itself a treatment variable. Recent evidence on the
self-correction illusion reports that explicit error flagging can change when
the same feedback is relabelled across conversational roles [@b15]. This
motivates the present intrinsic-versus-external-role control, where critique
text is held constant and only its role placement changes.

Compute-matched controls are consequently essential. One recent study reports
that repeated sampling can match or exceed Self-Refine and Reflexion under equal
token budgets in its tested settings [@b16]. Other recent reasoning evidence
argues that refinement can outperform resampling under different test-time
conditions [@b17]. The two findings are not inherently contradictory: they use
different tasks, models, correction signals, and budget definitions. Together
they show that refinement should be compared directly with resampling under an
explicit cost contract rather than assumed to be superior. This motivates the
blind-resampling condition in the present experiment and the reporting of
realized rather than nominal model calls.

Revision depth also requires inspection. Feedback-control analysis describes
self-correction as a dynamic process that may improve initially and then cross
a stability boundary where further revision becomes harmful [@b18]. For that
reason, this thesis reports attempt-level transitions, stopping behaviour, and
realized calls rather than treating a multi-step loop as a single opaque
generation operation.

## 2.4 Retrieval-augmented generation

Retrieval-augmented generation combines a parametric generator with external
non-parametric memory [@b8]. Retrieved material can provide facts, examples, or
domain-specific language that is absent from a prompt. It can also create
leakage, copying, and evaluation circularity when retrieved examples overlap
with training or assessment material. The scientific value of RAG therefore
depends as much on index construction and data privileges as on retrieval
quality.

In the present setting, reviews are useful as examples of register and target
level, not as factual evidence for a plot. This distinction matters because the
source corpus contains no review-to-film mapping. Retrieval cannot establish
that a generated statement is true of the input film; it can only condition the
style and specificity of the response. The experimental design accordingly
restricts retrieval to R1, excludes R2 and Gold-300, retrieves within the
requested level, and retains copy diagnostics. A randomized static few-shot
condition separates the effect of receiving examples from the effect of
semantic retrieval.

HybridRAG-BN is a close recent Bangla-language adjacency. It addresses
knowledge-base question answering (KBQA) by combining BM25 lexical retrieval
with BGE-M3 dense retrieval, Gemma generation, and a verifier and refiner
obtained by low-rank adaptation (LoRA) fine-tuning of Gemma [@b19]. Its
retrieved knowledge base can provide query-relevant facts, and its verifier
participates in answer repair. By contrast, the present index provides response
exemplars rather than plot facts, no language model is fine-tuned, and the
independent outcome verifier is prohibited from revision. HybridRAG-BN therefore
supports the feasibility of retrieval and verification in Bangla, but not the
particular data-isolation or audience-response claims examined here.

## 2.5 Neural and symbolic validation

Neural and symbolic evaluators offer complementary properties. Neural
classifiers can learn flexible boundaries from contextual representations, but
their scores rarely identify an actionable reason for failure. Hand-specified
symbolic rules can name observable defects, yet such rules may be incomplete,
brittle, or weakly predictive. A neuro-symbolic design must therefore state
whether symbolic information changes the decision boundary, explains a neural
decision, or guides a subsequent repair; these are different claims and they
carry different evidentiary burdens.

SymDiag provides a recent example in which symbolic verification supports
explainable diagnosis and repair of multi-step reasoning [@b20]. Its
satisfiability-based setting differs from short Bangla comments, for which no
complete formal theory of an acceptable response exists. The relevant transfer
is architectural: outcome assessment can be separated from a diagnosis that
names the failed constraint.

This thesis adopts that separation and, because the separation is the substance
of the neuro-symbolic claim, states in advance what would count as evidence on
each side of it. Two bars were registered before the measurement was made. The
predictive bar concerns the decision boundary: symbolic information earns a place
in the acceptance decision only if a neural–symbolic mixture improves held-out
discrimination over the neural score alone under cross-validation grouped by film
plot, so that the two requested levels of one plot — which share a synopsis and a
retrieved exemplar set — cannot be split across a fitting and an evaluation fold.
Three outcomes were pre-specified — that symbolic scores are inert
and change nothing, that they earn their place by improving held-out
discrimination, or that they harm it and are rejected — with the consequence for
the architecture fixed in advance for each. The diagnostic bar is separate and
weaker by design: naming a failed constraint in feedback needs only to change
what the reviser is told, and is assessed through the behaviour of the loop and
through attempt traces, not through classification gain. Keeping the two bars
apart is what allows the symbolic component to be retained for one role after
being refused the other.

Chapter 5 reports the outcome, and it is worth noting here that the observed
combination of measurements fell outside the registered three-way partition
rather than landing on one of its branches: held-out folds did not favour any
mixture over the neural score, yet the verdict curve was not flat. The registered
consequence is that no claim of symbolic predictive value is made and no mixture
weight is selected, while the separately registered diagnostic role remains
available. The result is recorded as an unresolved pre-commitment, not as a
demonstrated null, and Chapter 5 states why the difference matters. Setting both
bars here is what makes that outcome legible as a coverage defect in the
pre-registration rather than as a disappointing number.

## 2.6 Multi-agent workflows and architectural complexity

Multi-agent language-model systems divide a task among roles such as planner,
retriever, writer, critic, or reviewer. Role separation can make intermediate
decisions inspectable and can restrict which component may access a particular
tool or dataset. It does not, by itself, guarantee better output. Additional
roles can duplicate work, amplify an early error, or consume more tokens without
adding independent evidence.

A recent controlled comparison of single-agent and multi-agent RAG systems for
repository documentation illustrates this trade-off [@b21]. The multi-agent
workflow achieved strong structural consistency, but a simpler single-agent
pipeline obtained comparable lexical quality with substantially lower token
cost. Developer-guided planning performed best in that study, suggesting that
the value of decomposition depended on where reliable structure entered the
workflow rather than on the number of agents alone. Its software-documentation
task is not directly comparable with Bangla cinema responses, but the result
rules out a generic claim that agentic complexity is inherently beneficial.

The present architecture is therefore described as a **bounded multi-agent
workflow** with a predefined control flow, and not as an autonomous system.
Writer and Reflector are model-calling roles; Researcher is a retrieval and tool
role that makes no model call; Critic is a deterministic neural–symbolic
evaluation role that also makes no model call. Their privileges and transitions
are fixed rather than negotiated at run time. The ten-condition experiment tests
retrieval, verification, feedback, judging, and resampling mechanisms; it does
not constitute a direct single-agent-versus-multi-agent architecture ablation,
and no claim of that form is made anywhere in this thesis.

## 2.7 Verifiers, judges, and proxy optimization

Learned verifiers are widely used to score, rank, or select candidate outputs,
a practice established by Cobbe et al.'s demonstration that a trained verifier
can select among sampled completions more effectively than further fine-tuning
of the generator [@b58]. Verifiers make generation control inexpensive, but they
also create a proxy: the system optimizes what the verifier recognizes rather
than the intended construct itself. Evaluator Stress Tests formalize this concern
through perturbations that separate proxy improvement from performance under an
independent criterion [@b7]. Large language model (LLM) judges introduce related
risks, including rubric sensitivity, position effects, and self-preference when
evaluator and generator share model families. Fixed responses can receive
different measurements after a judge change [@b22], and rubric-based judges can
prefer outputs from their own model family [@b23]. Multilingual evidence also
finds uneven judge reliability across languages [@b24], while a low-resource
Basque study reports weak agreement both with humans and across judges [@b25].
These findings prevent the hosted same-family Gemma judge from serving as the
final Bangla outcome evaluator.

An outcome evaluator must therefore be insulated from the procedure it assesses.
In this thesis, Verifier-A is deliberately available to generation, whereas
Verifier-B is trained on disjoint data with a different pretrained model and
tokenizer and is never allowed to gate, select, critique, or rewrite an output.
A widening A–B gap is interpreted as evidence consistent with proxy
overoptimization. It is not proof that Verifier-B represents human truth or
that human-perceived quality has declined.

## 2.8 Bangla natural language processing

### 2.8.1 Classification backbones

Bangla NLP systems vary in pretraining corpus, tokenizer, script coverage, and
register. BanglaBERT provides a Bangla-specific pretrained language model and
evaluation benchmarks [@b2], while LaBSE provides language-agnostic sentence
embeddings suitable for multilingual semantic comparison [@b3]. These
resources enable controlled studies in Bangla, but model identity alone does
not determine which representation will best reproduce a constructed label.

Recent Bangla classification studies reinforce that caution. MuRIL performs
strongly on Bangla emotion detection [@b26], whereas studies on BanglaBlend and
Bangla form classification report advantages for XLM-R or IndicBERTv2 over
BanglaBERT in their respective settings [@b27; @b28]. Their tasks and datasets
do not settle the present verifier choice; collectively they show why a
Bangla-specific backbone should not be declared superior from model identity.

This is especially relevant for short reviews. Sentiment, length, punctuation,
and source register may dominate a representation that is later interpreted as
engagement or persona. The present study therefore audits those factors before
naming the construct and compares verifier backbones through paired prediction
evidence. The observed tie across fine-tuned backbones and the strong frozen
LaBSE probe are interpreted as evidence that label geometry can outweigh a
simple language-specific-versus-multilingual model narrative.

### 2.8.2 Generation and evaluation resources

Classification backbones address only half of the low-resource problem. A study
that generates Bangla text also depends on what is known about Bangla generation
quality and on which instruments exist to evaluate it, and that literature is
both thinner and more recent. The sources in this subsection were assessed at
record level rather than read in full, so they are used here to establish that a
documented risk exists and not to import any specific finding.

Three 2026 resources are directly relevant. A multi-task hallucination
evaluation framework for Bengali reports that no prior work had systematically
evaluated hallucination in large language models for the language, despite its
speaker population [@b98]. A curated dataset on honorific failures in
multilingual Bangla generation targets a failure mode in which output is
superficially polite but pragmatically wrong [@b99]. A benchmark for
sociopragmatic and cultural alignment in Bangladeshi social interaction reports
that fluency alone does not guarantee socially appropriate language use in a
high-context language [@b110]. Alongside these, work on informal Bangla machine
translation documents that informal Bangla is under-resourced relative to formal
Bangla [@b111], which matters because the present corpus is entirely informal
comment text.

Two consequences follow for this study. First, Bangla generation quality is
treated as a documented risk rather than as an assumption, which is part of the
reason a separately trained outcome verifier and a blinded human study are both
retained instead of relying on the generator's apparent fluency. Second, register
and honorific handling are recognized as dimensions on which a Bangla generator
can fail while remaining fluent, and the pre-specified failure taxonomy used for
symbolic diagnosis in Chapter 5 does not contain a register or honorific
category. That omission is a limitation of the taxonomy rather than a property of
the language, and it is not repaired retrospectively: the taxonomy was frozen
before generation and changing it afterwards would replace a registered
instrument with a post-hoc one.

## 2.9 Human evaluation

Human evaluation serves two distinct purposes in this thesis: validating the
corpus-derived construct and assessing whether generated outputs express the
requested level. These purposes require different instruments. Comparative
judgments can be more reliable than rating scales for subjective intensity
annotation [@b29], while recent work shows that ratings and comparisons may
provide complementary information rather than interchangeable measurements
[@b30]. This literature is consistent with the study's empirical sequence: an
ordinal instrument failed its reliability gate, whereas a length-matched
comparative intrusion task succeeded.

The generated-output study uses a forced binary target-level judgment rather
than a general quality rating. Agreement is reported through raw three-way
agreement and nominal Krippendorff alpha [@b31], with item-level bootstrap
uncertainty. HEDS 3.0 guides transparent reporting of recruitment, evaluated
systems, allocation, criteria, ethics, and analysis decisions [@b32]. Agreement
is not treated as validity on its own, and the human study is not used to rank
conditions whose per-cell sample is too small.

Evaluation-set construction is also consequential. Outcome-blind balanced
selection avoids conditioning the human sample on either verifier, a risk noted
for metric-guided NLG evaluation sampling [@b33]. Replicable evaluation depends
jointly on item allocation and ratings per item [@b34], and persistent rater
identifiers are needed to represent annotator variation [@b35]. Recent work on
global versus pairwise scoring supports matching the elicitation form to the
estimand rather than treating one format as universally best [@b36]. For three
nominal raters, metric-selection guidance further supports reporting
Krippendorff alpha with uncertainty and disagreement patterns rather than a
universal agreement cutoff [@b37].

Taken together, Sections 2.2 to 2.9 supply the components of the present design
and the constraints under which each may be used. What they do not supply is a
study in which those constraints hold simultaneously. Section 2.10 makes that
comparison explicit.

## 2.10 Comparative position and research gap

Table 2.1 compares the present study with the closest verified lines of work.
The entries describe evaluated components rather than assigning quality. A
negative cell means only that the component lies outside that paper's reported
design. No row is entered for a source assessed only at record level, since a
negative cell is a claim about what a paper does not report and an abstract
cannot support it; the two such sources in this chapter, Sands et al. [@b12] and
Cobbe et al. [@b58], are therefore discussed in the text and omitted from the
table.

**Table 2.1. Position relative to verified adjacent work**

| Work | Task/language | Retrieval | Revision signal | Symbolic diagnosis | Outcome scorer isolated from generation | Human validation |
|---|---|---:|---|---:|---:|---:|
| Mixture-of-Personas [@b9] | population-conditioned text generation | No | persona conditioning | No | No | study-specific evaluation |
| SimAB [@b10] | persona-conditioned web A/B prediction | context documents | agent interaction | No | No | historical outcomes and practitioner study |
| FUDGE [@b11] | controlled text generation | No | learned discriminator during decoding | No | No | task metrics |
| Self-Refine [@b13] | multi-task refinement | No | same-model self-feedback | No | No | task-dependent human/automatic evaluation |
| Reflexion [@b14] | reasoning, coding, and decision tasks | task-dependent | verbal feedback or memory | verbal/heuristic | No | benchmark outcomes |
| HybridRAG-BN [@b19] | Bangla KBQA | BM25 + BGE-M3 | LoRA-tuned Gemma verifier/refiner | No | No | competition token F1 |
| SymDiag [@b20] | multi-step reasoning | No | symbolic diagnosis supports repair | Yes | No A/B wall | manually audited diagnosis |
| Saleh et al. [@b21] | repository documentation | repository RAG | reviewer-mediated rewriting | No | No | manual structure analysis + automatic metrics |
| Present study | Bangla cinema-response generation | R1 level exemplars | trained Verifier-A + bounded feedback | diagnostic rules | Verifier-B outside the loop | construct study + blinded output study |

The literature provides the individual foundations for persona conditioning,
classifier-guided generation, retrieval augmentation, self-refinement, trained
verifiers, symbolic diagnosis, multi-agent role decomposition, and human
evaluation. What remains insufficiently tested is their combination under the
constraints of a short-text, low-resource-language setting. In particular, the
verified adjacent work does not jointly examine: (i) a corpus-derived distinction
whose clusterability and human recognizability are tested before generation;
(ii) an R1-only retrieval and in-loop verifier contract; (iii) symbolic feedback
separated from predictive gating; (iv) an outcome verifier trained on disjoint R2
data and sealed from the loop; (v) compute-aware self-critique, external-judge,
and resampling controls; and (vi) blinded native-speaker validation of generated
target-level match.

The research gap is therefore not the invention of any one component. It is the
absence of an auditable evaluation that brings these components together while
making their data privileges, costs, negative results, and proxy failures
visible. That formulation also fixes the kind of contribution this thesis can
claim. Prior work establishes the feasibility of persona conditioning,
classifier-guided control, retrieval, iterative feedback, symbolic diagnosis, and
role-based workflows; it equally explains why none of these mechanisms should be
accepted without strong controls, since synthetic audiences carry unresolved
validity risks, intrinsic correction can fail, refinement competes with
resampling under equal budgets, retrieval can leak or copy, and additional agents
can add cost without improving quality. The gap that follows is an evaluation
gap, not a claim that the individual components are novel.

## 2.11 Chapter summary

The review establishes the constraints under which the remainder of the thesis
must operate: an external rather than intrinsic correction signal, a retrieval
index with declared privileges, a symbolic component held to two separate
evidentiary bars, an outcome evaluator sealed from the procedure it scores, and
controls matched on realized compute. Chapter 3 begins by establishing the data
provenance and the human-recognizable construct that any generation result
depends on, because a controlled generation study cannot be interpreted before
the thing being controlled is shown to exist.
