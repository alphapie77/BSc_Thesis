# Chapter 5 — The Neuro-Symbolic Multi-Agent System

## 5.1 Architecture

The compound system contains four functional agents coordinated by an explicit
state graph:

1. **Researcher:** retrieves the top ten same-level examples from the frozen
   R1-only LaBSE/Chroma index.
2. **Writer:** produces a Bangla cinema response for the requested level using
   the plot, axis definition, and retrieved examples.
3. **Critic:** applies Verifier-A and computes symbolic diagnostics; it never
   loads Verifier-B.
4. **Reflector:** converts the score and named failed rules into bounded feedback
   for the next Writer attempt.

The graph records every attempt, score, diagnostic, feedback string, token count,
latency, and stopping reason. State snapshots are deep-copied before mutation,
and ties select the earliest attempt because an equal later draft has not earned
its extra cost. At most three logical Writer attempts are permitted in the
primary loop.

## 5.2 Retrieval and prompt contract

The RAG index contains 886 region-A R1 reviews: 534 at Level 0 and 352 at Level
1. It includes the 804 Verifier-A training rows plus 82 development reviews,
because retrieval is not a fitted classifier and threshold tuning occurs on
separate development plots. It contains zero R2 and zero Gold-300 identifiers.

One prompt renderer supplies every condition. Zero-shot is the same base prompt
with no exemplars or feedback; RAG conditions add retrieved examples; revision
conditions add feedback. This construction prevents a baseline from receiving a
weaker task definition than a loop condition. Bangla characters are preserved,
and negative constraints were rewritten as positive prototypes because negation
can itself foreground the forbidden cue.

The prompt uses a uniform 20-word ceiling at both levels. This reduced but did
not eliminate the generated-length confound. The system therefore reports
length diagnostics beside control results and never claims length neutrality.

## 5.3 Neural gating and symbolic diagnosis

Verifier-A supplies the acceptance score. Symbolic checks describe observable
features such as insufficient specificity or problematic form, but are not
combined into a claimed predictive hybrid score. A 21-point `w` sensitivity
curve was evaluated under length-controlled and free-length conditions. Every
grouped held-out fold selected w=1.0, and the mean delta AUC relative to
neural-only was 0.0000. Symbolic-only AUC was 0.3417 under length control and
0.0656 at free length, both below neural-only (0.8333 and 0.8658).

The curve was nevertheless verdict-sensitive: 50.8% and 39.2% of generations
changed PASS/FAIL somewhere across w. This observed combination was missing from
the three preregistered outcomes, so the correct audit state is
`PRECOMMITMENT_UNRESOLVED`. No fourth outcome is invented, no single hybrid
weight is selected, and symbolic information is retained only for failed-rule
naming.

## 5.4 Threshold selection

The neural threshold is selected on 60 held-out development plot-level cases by
the preregistered frontier objective

\[
\tau^* = \arg\max_\tau
\frac{Q_B(\tau)-\alpha_{lo}}{E[\mathrm{calls}\mid\tau]},
\]

where outcome quality is measured by Verifier-B after the fact and Verifier-B
never enters the loop. The lower endpoint is one-call RAG-only, not zero-shot;
the upper endpoint is forced-three revision.

The selected threshold is \(\tau^*=0.4384071\). At this point Verifier-B quality
is 0.802219, expected calls equal 2.000, first-pass acceptance is 0.6500, final
acceptance is 0.8667, and 8/60 cases give up. The one-call endpoint is 0.640501
and the forced-three endpoint 0.866272; the chosen operating point captures
71.63% of the achievable gain. A descriptive level-score permutation gives
delta +0.08289, p=0.4687; this means “not detected,” not “equal.”

## 5.5 Loop dynamics

At the selected threshold, accepted stops occur at attempts 1/2/3 for 39, 12,
and 1 cases; eight give up. The emitted-best attempts are 41/16/3 because a
gave-up case can emit an earlier higher-scoring draft. Attempt 1→2 improves mean
Verifier-A by +0.08719 and Verifier-B by +0.08902. Attempt 2→3 regresses by
-0.06272 and -0.01805 respectively, with Verifier-B declining in 37/60 cases.
A and B disagree on revision direction for 18/60 cases in each transition.

The post-hoc Verifier-B oracle reaches 0.872402, while A-selected forced-three
reaches 0.866272, or 97.36% of the available oracle gain. This is diagnostic
only; it is not a deployable selector because B is forbidden from the loop.
These dynamics justify the bounded retry budget and show why more iterations
cannot be assumed beneficial [@axiv2604_22273_scfeedbackcontrol].

## 5.6 Failure taxonomy

The final failure set contains eight cases, not the planned fifty. One is coded
off-topic, two are post-hoc `other`, and five have no observable registered
error. The researcher authorized Codex as Coder-A, reviewed the labels, and
waived independent Coder-B. Inter-coder agreement is therefore null and is not
fabricated. This component is a complete census of the eight observed failures
but a protocol deviation in both sample size and coder independence.

## 5.7 Ten-condition experimental interface

The main experiment instantiates ten conditions through the same underlying
prompt and data contracts: zero-shot, randomized static few-shot, RAG-only,
neural loop, symbolic loop, neural loop with symbolic feedback, intrinsic
self-critique, external-role self-critique, hosted Gemma-4 judging, and blind
resampling. Conditions 3–9 share a byte-identical initial RAG draft for each
plot/level/replicate while retaining logical cost. This paired schedule reduces
irrelevant sampling variation.

The hosted Gemma-4 judge sees the plot, requested level, draft, and rubric but no
Verifier-A/B score. Blind resampling draws up to five independent RAG samples and
lets Verifier-A select the best prefix under a matched compute budget. Both are
strong controls: one tests a large external judge and the other tests whether
fresh sampling can match refinement.

## 5.8 Reproducibility and safety boundaries

Global seed 42 initializes every script; main generation replicates are fixed at
42, 43, and 44. Every config maps to named outputs with git commit and runtime
provenance. Checkpoints must parse fully, have unique registered keys, and match
an allowed clean producing commit. Raw provider payloads and superseded calls are
archived separately and cannot occupy active resume paths.

The live local interface is not the frozen experiment. It uses a hosted Gemma-4
Writer and an additional operational plot-support check, whereas the main run
uses frozen Gemma-3 generation and outcome-only Verifier-B. The demo neither
persists prompts nor changes Phase-5 results and must be presented as diagnostic
software.

## 5.9 Chapter summary

The system operationalizes external verification as an inspectable state machine
rather than an opaque “agent” label. Neural gating decides, symbolic rules
explain, the Reflector translates diagnosis into feedback, and a separate
Verifier-B makes overoptimization visible. Development results establish a
useful two-attempt region, diminishing third-attempt returns, no predictive case
for a hybrid score, and the necessity of strict data and evaluator walls. The
next chapter evaluates this architecture against nine matched alternatives.

