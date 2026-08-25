# Chapter 2 — Related Work

This chapter positions the thesis within research on synthetic audiences,
controlled generation, self-correction, retrieval, neuro-symbolic diagnosis,
multi-agent workflows, learned evaluators, Bangla natural language processing,
and human evaluation. It synthesizes the contribution and limitations of each
line of work, identifies their relevance to controlled Bangla response
generation, and concludes by defining the research gap addressed in this
thesis.

## 2.1 Synthetic Audiences and Controlled Response Generation

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

## 2.2 Self-Correction and Feedback

Iterative refinement is often motivated by the intuition that a language model
can inspect a draft, identify its own mistakes, and improve the answer. Evidence
for this intuition is conditional. Huang et al. find that intrinsic
self-correction—revision without reliable external feedback—does not
consistently improve the reasoning tasks they examine and can alter correct
answers [@b5]. Kamoi et al. similarly distinguish intrinsic feedback from
correction supported by an oracle, tool, environment, or separately trained
model, finding stronger evidence when feedback is externally grounded [@b6].
Together, these studies show that generation ability does not guarantee reliable
self-evaluation.

Self-Refine operationalizes an intrinsic generate–feedback–revise cycle using
the same model [@b13]. Reflexion stores verbal feedback in memory and can draw
that feedback from internal or external signals depending on the task [@b14].
These systems demonstrate the usefulness of explicit intermediate critique,
but their success does not establish that self-generated criticism is accurate
or that improvement is caused by reflection rather than by additional model
calls.

External verification provides an alternative. Cobbe et al. train a verifier to
rank sampled completions and report that verifier-based selection improves
performance relative to additional generator fine-tuning [@b58]. This establishes
the value of an independently trained selection signal, but it concerns ranking
a fixed candidate pool rather than guiding iterative revision. The present study
therefore evaluates both verifier-gated revision and blind resampling.

Role placement is also consequential. Recent evidence shows that the effect of
explicit error feedback can change when identical feedback is assigned to
different conversational roles [@b15]. This motivates comparing intrinsic and
external-role critique while holding the critique content constant.

Compute-aware controls are consequently essential. One recent study reports
that repeated sampling can match or exceed Self-Refine and Reflexion under equal
token budgets in its tested settings [@b16]. Other recent reasoning evidence
argues that refinement can outperform resampling under different test-time
conditions [@b17]. The two findings are not inherently contradictory: they use
different tasks, models, correction signals, and budget definitions. Together
they show that refinement should be compared directly with resampling under an
explicit cost contract rather than assumed to be superior.

Revision depth also requires inspection. Feedback-control analysis describes
self-correction as a dynamic process that may improve initially and then cross
a stability boundary where further revision becomes harmful [@b18]. For that
reason, iterative systems should report stopping behaviour, attempt-level
transitions, and realized computational cost rather than treating the loop as a
single opaque operation.

## 2.3 Retrieval-Augmented Generation

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

## 2.4 Neural and Symbolic Validation

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

The relevant design implication is that prediction and diagnosis require
separate evidence. Symbolic information should affect acceptance only if it
improves held-out discrimination beyond the neural score; otherwise, its role
is limited to naming observable failures and guiding revision. The present
study therefore evaluates symbolic gating separately from symbolic diagnostic
feedback rather than treating a neuro-symbolic label as evidence of predictive
benefit.

## 2.5 Multi-Agent Workflows

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
not constitute a direct single-agent-versus-multi-agent architecture ablation.
Accordingly, the experiment does not test whether a multi-agent architecture is
superior to a single-agent alternative.

## 2.6 Verifier Reliability and Proxy Optimization

Learned verifiers can make generation control inexpensive, but they also create
a proxy: the system optimizes what the verifier recognizes rather than the
intended construct itself. Evaluator Stress Tests formalize this concern
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

## 2.7 Bangla Natural Language Processing

### 2.7.1 Classification Backbones

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
naming the construct and compares verifier backbones empirically rather than
assuming that a Bangla-specific or multilingual encoder is inherently superior.

### 2.7.2 Generation and Evaluation Resources

Classification backbones address only half of the low-resource problem. A study
that generates Bangla text also depends on what is known about Bangla generation
quality and on which instruments exist to evaluate it, and that literature is
both thinner and more recent.

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

Two consequences follow for this study. First, apparent Bangla fluency cannot
replace evaluation by a separately trained outcome verifier and native readers.
Second, register and honorific handling remain possible failure dimensions that
are not fully represented by the study's bounded symbolic taxonomy; this is
retained as a limitation rather than interpreted as evidence of linguistic
adequacy.

## 2.8 Human Evaluation

Human evaluation serves two distinct purposes in this thesis: validating the
corpus-derived construct and assessing whether generated outputs express the
requested level. These purposes require different instruments. Comparative
judgments can be more reliable than rating scales for subjective intensity
annotation [@b29], while recent work shows that ratings and comparisons may
provide complementary information rather than interchangeable measurements
[@b30]. This evidence motivates matching the elicitation format to the construct
and validating the instrument empirically rather than assuming that an ordinal
rating scale is sufficient.

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

Taken together, Sections 2.1 to 2.8 supply the components of the present design
and the constraints under which each may be used. What they do not supply is a
study in which those constraints hold simultaneously. Section 2.9 makes that
comparison explicit.

## 2.9 Research Gap

Table 2.1 positions the present study against selected adjacent work. The table
compares reported design components rather than ranking study quality; “None
reported” indicates only that the component is not part of the reported design.

**Table 2.1. Comparison with selected adjacent studies**

| Study | Setting | Retrieval | Feedback or control | Symbolic diagnosis | Isolated outcome evaluator | Reported evaluation |
|---|---|---|---|---|---|---|
| Mixture-of-Personas [@b9] | Population-conditioned generation | None reported | Persona conditioning | None reported | None reported | Study-specific task evaluation |
| SimAB [@b10] | Persona-conditioned web A/B prediction | Context documents | Agent interaction | None reported | None reported | Historical outcomes and practitioner study |
| FUDGE [@b11] | Controlled text generation | None reported | Discriminator-guided decoding | None reported | None reported | Task-specific automatic metrics |
| Self-Refine [@b13] | Multi-task refinement | None reported | Same-model self-feedback | None reported | None reported | Task-dependent human and automatic evaluation |
| Reflexion [@b14] | Reasoning, coding, and decision tasks | Task-dependent | Verbal feedback and memory | None reported | None reported | Benchmark outcomes |
| HybridRAG-BN [@b19] | Bangla knowledge-base question answering | BM25 and BGE-M3 | Fine-tuned verifier and refiner | None reported | None reported | Token-F1 |
| SymDiag [@b20] | Multi-step reasoning | None reported | Symbolic diagnosis and repair | Constraint-based diagnosis | None reported | Manual diagnosis audit |
| Saleh et al. [@b21] | Repository documentation | Repository retrieval | Reviewer-mediated rewriting | None reported | None reported | Automatic metrics and manual structural assessment |
| Present study | Bangla cinema-response generation | R1 level-specific exemplars | Verifier-A and bounded feedback | Deterministic diagnostic rules | Loop-isolated Verifier-B | Blinded construct and output judgments |

*Note.* The table is selective rather than exhaustive. Evaluation approaches
differ across tasks and should not be interpreted as equivalent instruments.

Prior work establishes the individual foundations for controlled generation,
retrieval augmentation, iterative feedback, trained verification, symbolic
diagnosis, role-based decomposition, and human evaluation. Among the studies
reviewed here, none jointly evaluates these components for short Bangla cinema
responses under four simultaneous constraints: a human-validated response
construct, disjoint privileges for the in-loop and outcome verifiers,
compute-aware generation controls, and blinded native-speaker assessment.

The research gap is therefore an evaluation gap rather than the absence of any
single technical component. What is missing is an auditable study that combines
these mechanisms while exposing their data access, computational cost, negative
results, and susceptibility to proxy optimization. This framing bounds the
thesis contribution to controlled integration and evidence; it does not claim
that retrieval, verification, symbolic diagnosis, or multi-agent roles are
individually novel.

## 2.10 Chapter Summary

The literature supports controlled generation, retrieval, external feedback,
and symbolic diagnosis, but also identifies risks from unsupported
self-correction, evaluator dependence, retrieval leakage, and unnecessary
architectural complexity. These findings motivate an auditable design with
declared data privileges, compute-aware controls, and independent human and
model-based evaluation. Chapter 3 therefore begins by establishing the data
provenance and validating the response construct on which the generation study
depends.
