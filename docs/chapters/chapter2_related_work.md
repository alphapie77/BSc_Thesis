# Chapter 2 — Related Work

## 2.1 Synthetic audiences and controllable response generation

LLM-based persona and audience simulation is often motivated as a fast proxy for
human research. Its central methodological problem is validity: a fluent response
can resemble a persona without predicting any real person's behavior. Recent
reviews emphasize prompt sensitivity, bias, hallucination, weak ecological
validity, and anthropomorphic overinterpretation [@lappas2026syntheticaudiences].
This thesis therefore avoids treating generated comments as synthetic viewers.
Its controlled variable is a textual engagement-specificity level whose
recognizability is tested directly with Bangla readers.

The closest generation literature supplies useful baselines but not the whole
design. Persona prompting and mixture-of-personas approaches motivate explicit
conditioning [@mop2025], while classifier-guided generation shows
that an external signal can steer output without fine-tuning the generator. The
present work differs by placing a lightweight classifier inside a bounded
revision loop, measuring it against prompting, RAG, self-critique, a hosted
judge, and resampling, and reserving a second classifier for outcomes.

## 2.2 Intrinsic and extrinsic self-correction

Intrinsic self-correction asks a model to inspect and revise its own answer
without new external evidence. Huang et al. show that apparent gains can vanish
under prompt-parity controls and that intrinsic revision may degrade correct
answers [@huang2024selfcorrect]. Kamoi et al. distinguish settings in which
feedback supplies genuinely new information from those in which a model merely
reconsiders the same state [@kamoi2024when]. Self-Refine and Reflexion demonstrate
the engineering value of iterative feedback, but do not imply that every
self-generated critique is reliable.

This thesis treats the distinction between intrinsic and extrinsic feedback as
an experimental factor. Intrinsic self-critique and an external-role relabeling
control share the self-generated critique pathway, while the proposed loop uses
a trained external verifier. Prompt parity is enforced through one renderer so
that the baseline does not lose information merely because it appears before a
revision instruction.

## 2.3 Retrieval-augmented generation

Retrieval-augmented generation can ground style and content in examples, but it
also introduces leakage and copying risks. The present design restricts the
index to R1, retrieves only examples with the requested level, and never exposes
R2 or Gold-300. Static few-shot examples are instance-randomized independently
of plot similarity, separating the value of examples from the value of
retrieval. Exact and near-copy diagnostics are retained because a real retrieved
review is likely to score well under a verifier trained on the same label space,
even if the model has merely reproduced an exemplar.

## 2.4 Neural and symbolic validation

Neural classifiers provide flexible decision boundaries but often return an
opaque score. Symbolic rules provide interpretable failure names but may be weak
predictors. The system therefore separates **gating** from **diagnosis**: the
neural verifier determines whether a draft passes, while symbolic checks can
tell the Reflector what observable property needs attention. This design is
supported conditionally rather than ideologically. The registered weight sweep
found no held-out predictive gain from combining symbolic and neural scores, so
the thesis does not claim that the symbolic component improves classifier
accuracy. Its defended role is interpretable feedback.

## 2.5 Verifiers, reward models, and Goodhart effects

Verifier-guided generation descends from work in which a learned evaluator
selects or rewards candidate solutions. The methodological risk is that the
generator optimizes the proxy rather than the intended construct. Evaluator
stress testing formalizes this distinction through controlled perturbations and
proxy–true divergence [@shihab2025est]. LLM judges introduce additional
self-preference and rubric sensitivity, particularly when judge and generator
share a model family.

The A/B wall in this thesis is designed around that risk. Verifier-A is cheap and
available to the loop. Verifier-B uses disjoint data, a different pretrained
family, a different tokenizer, and end-to-end fine-tuning; it never gates,
selects, critiques, or regenerates an output. A widening A–B gap is reported as
a Goodhart diagnostic, not as proof that B is ground truth.

## 2.6 Bangla NLP and low-resource evaluation

Bangla models differ in pretraining data, script coverage, tokenizer fertility,
and register behavior. These differences make memory-based backbone selection
unreliable. The seven-arm verifier ablation in this study was therefore decided
by paired prediction comparisons rather than the narrative that a
Bangla-specific backbone must win. The outcome was a tie, and a frozen LaBSE
probe outperformed the best fine-tuned arm on the constructed label. This result
demonstrates that benchmark geometry can dominate backbone choice.

Short Bangla reviews create further risks. Average texts contain only about
eight words, sentiment is an obvious dominant signal, and source-specific
punctuation or register can overwhelm engagement structure. The study therefore
tests sentiment ARI, corpus source, clusterability, length, and residual
structure before naming the axis.

## 2.7 Human evaluation

Human evaluation is used twice for different purposes. The first study asks
whether the corpus distinction is perceptible. An ordinal scale failed its
reliability gate, while a length-matched comparative intrusion task succeeded;
this is consistent with evidence that comparative judgments can be more reliable
than ratings and that the two forms can complement each other
[@axiv2602_08033_comparisonsandratings]. The second study asks whether generated outputs
match a requested level. It uses a forced binary decision, three blinded native
speakers, case-bootstrap uncertainty, raw agreement, and nominal Krippendorff
alpha. HEDS 3.0 structures the reporting of recruitment, interface, allocation,
and analysis choices [@belz2025heds3].

Agreement is not treated as construct validity by itself. High agreement can
coexist with a collapsed scale, as the failed ordinal round demonstrated.
Validity requires that the instrument, task, labels, and intended claim align.

## 2.8 Research gap

The literature contains persona prompting, retrieval, classifier guidance,
self-correction, LLM judging, neuro-symbolic diagnostics, and reward-hacking
analysis as mostly separate lines. This thesis joins them in a Bangla
generation experiment with four properties rarely tested together: a
human-recognizable low-resource construct, matched strong baselines, a strict
in-loop/outcome evaluator wall, and complete cost and revision traces. Its
novelty is not the invention of each component but the falsifiable integration
of them under explicit leakage and claim boundaries.
