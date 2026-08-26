# Chapter 5 — Proposed Neuro-Symbolic Multi-Agent Framework

Chapters 3 and 4 established what the system is asked to control and what is
permitted to judge it. This chapter specifies the mechanism itself. It is the
construction behind Objective 4, and it is the object under test in RQ2 and RQ3;
contributions C2 and C6 are built here, although the evidence that supports them
is reported in Chapter 6.

The chapter is written as a specification rather than as a description. Two
consequences follow. First, every routing decision, ceiling, threshold and
tie-break appears as an executable rule, and the two central control procedures
are given as algorithm listings (Algorithms 5.1 and 5.2) transcribed from the
implementation rather than paraphrased from it. Second, the cost of the loop is
stated as a model, not as a measurement, because the threshold that governs the
loop was selected against that model before any generation existed. A chapter
that reported only the realized cost would conceal the fact that the operating
point was chosen, and chosen against a criterion that had to be repaired first.

The order of presentation follows the order of control. Sections 5.1 and 5.2
define the roles, the state and the sense in which the word *agent* is being
used. Section 5.3 gives the loop and its cost model. Sections 5.4 to 5.6 specify
the three quantities the loop depends on: the evidence supplied to the writer,
the signal that gates it, and the threshold at which that signal stops it.
Section 5.7 reports what the loop actually did during development, including
where it failed. Sections 5.8 and 5.9 define the ten conditions and the matched-
budget control against which the loop is compared, and Section 5.10 reduces the
execution contract to what a reader needs in order to locate the rest in
Appendix A.

## 5.1 Architecture, roles and state

The framework is a compound system of four functional roles coordinated by an
explicit state graph. The roles are asymmetric by design, and the asymmetry is
the first thing to notice about the architecture:

1. **Researcher.** Retrieves the ten highest-similarity same-level exemplars
   from the frozen R1-only LaBSE index. It makes no model call; it is a
   deterministic tool caller over a fixed vector store.
2. **Writer.** Produces a Bangla cinema response for the requested level from
   the plot, the axis definition and the retrieved exemplars. This is the only
   role that generates text.
3. **Critic.** Applies Verifier-A to obtain the acceptance score and computes
   the symbolic diagnostics. It contains no language model, and it never loads
   Verifier-B.
4. **Reflector.** Converts a score and a set of named failed rules into bounded
   natural-language feedback for the next Writer attempt.

Two of the four roles therefore make no language-model call at all. This is not
an implementation convenience but the point of the design: the component that
decides whether a draft is acceptable is a frozen linear probe over frozen
sentence embeddings, so acceptance is reproducible, auditable, and cannot drift
with a model update. The Critic's determinism is what makes the verifier
isolation of Chapter 4 enforceable in the first place, because a deterministic
Critic can be shown by static analysis never to reach Verifier-B, whereas a
model-based critic could only be argued about.

The Researcher follows the retrieval-augmented generation principle of supplying
external evidence before generation rather than relying on parametric recall
[@b8]. The separation of a learned neural decision from an inspectable symbolic
diagnosis follows recent neuro-symbolic verification work, with one deliberate
departure: here the symbolic output remains diagnostic and is never treated as
ground truth [@b20]. Section 5.5 reports the measurement that forced that
departure.

For a plot $p$, requested level $l$ and attempt $t$, the controller state is

$$
s_t=(p,\;l,\;q_t,\;E_t,\;y_t,\;a_t,\;r_t,\;f_t,\;c_t),
$$

where $q_t$ is the retrieval query, $E_t$ the retrieved exemplars, $y_t$ the
current draft, $a_t$ the Verifier-A score, $r_t$ the symbolic diagnostics, $f_t$
the feedback message and $c_t$ the accumulated logical cost. A transition either
accepts the current draft, revises the query and evidence and requests another
draft, or terminates at the registered retry ceiling. **Verifier-B is not a
state variable**, because no transition is permitted to consult it; its absence
from the state tuple is the formal statement of inviolable rule 6.

Two properties of the state machine are worth stating explicitly because both
were originally implementation defects and both would have been invisible in the
results had they survived. First, every attempt is snapshotted by deep copy
*before* the next attempt begins. A shallow copy shares the retrieved-exemplar
list and the failed-rule list with the live state, so all three trace rows would
have displayed the final attempt's values — which reads as *the loop changed
nothing* rather than as a copying bug, and would have been reported as a null
result about revision. Second, feedback is carried forward in a local variable
rather than read back off the state, because advancing the state clears the
feedback field. Reading it after advancing yielded an empty message, so every
retry prompt would have been identical to the first attempt's except for the
previous draft. The loop would have appeared to retry while in fact re-rolling
the same dice, and the measured effect of revision would have been the effect of
resampling. Both defects are recorded because they define what the reported
dynamics in Section 5.7 are dynamics *of*.

Figure 5.1 shows the resulting routing. The three exits from the Critic —
accept, revise, and terminate at the ceiling — are the only ways a case can
leave the graph, and Verifier-B is drawn outside the graph boundary to indicate
that it observes sealed outputs only.

![Bounded four-role generation state graph](../figures/multi_agent_state_graph.svg)

*Figure 5.1. Bounded routing in the Researcher–Writer–Critic–Reflector graph. A
failed Critic decision can trigger feedback, rewriting, and — when retrieved
evidence overlaps the previous attempt's below the registered threshold — a
revised retrieval query. Thresholds and a ceiling of three Writer attempts bound
the routing. Verifier-B remains outside the graph and scores only sealed
outputs.*

## 5.2 Why this is a bounded workflow, not an autonomous agent

The term *multi-agent* is used here for functional decomposition with message
passing between roles that hold different information. It does not denote four
independently trained models, and it does not denote autonomy. Writer and
Reflector are the two model-calling roles; the Researcher is a retrieval role
and the Critic a deterministic neural–symbolic evaluation role. Each has a
distinct state contract, a distinct set of permitted inputs and a distinct
transition responsibility, and the persistent trace exposes the messages passing
between them.

What the controller may do is enumerable, and the enumeration is short: it may
retry, it may revise a retrieval query when the evidence it received overlapped
the previous attempt's too heavily, and it may stop. What it may not do is
equally definite. It cannot alter the acceptance threshold, it cannot change the
data walls, it cannot raise the retry ceiling, it cannot select its own tools,
and it cannot modify the registered condition it is executing. The control flow
is fixed in advance and written as a small number of conditional branches. In
the vocabulary of compound language-model systems, this is an
**evaluator–optimizer workflow with a predefined control flow**: a generator
proposes, a separate evaluator scores, and a bounded number of revision rounds
follows. It is not an agent that plans its own trajectory.

The distinction matters for what may be claimed. Naming the system autonomous
would license conclusions about emergent coordination that this experiment
cannot support, and it would misattribute the observed improvement. Whatever
gain Chapter 6 reports is produced by external verification and bounded
revision, not by agency, and the design keeps those two explanations separable
by removing agency from the design.

The conservatism is also empirically motivated. A recent controlled comparison
found that multi-agent RAG decomposition improved structural consistency yet
matched a simpler single-agent pipeline on lexical quality while consuming
substantially more tokens [@b21]. The present ten-condition experiment tests
verification and revision mechanisms; it does not include a matched monolithic
reimplementation of the complete graph, and therefore it cannot establish that
role decomposition is itself beneficial. That absence is a scope limitation, not
an omission to be repaired by a stronger adjective.

## 5.3 Algorithm 5.1 — the bounded generation loop

Algorithm 5.1 states the loop that all four verifier-in-the-loop conditions
execute. It is transcribed from the implemented controller and its state object;
the numbered guarantees below the listing are the properties the test suite
enforces.

```
Algorithm 5.1  Bounded verifier-in-the-loop generation

Input:  plot p, requested level l, threshold tau, arm a
        roles: Researcher R, Writer W, Critic C, Reflector F
Const:  T_max = 3                       (registered retry ceiling)
        theta_overlap = 0.50            (query-revision trigger)
Output: emitted draft y*, trace, gave_up flag, logical call count

 1  t <- 1;  f <- null;  trace <- []
 2  q <- base_query(p, l)
 3  E <- R.retrieve(q, level = l, k = 10)
 4  while true do
 5      y <- W.generate(p, l, E, previous_draft, f)        # one model call
 6      (a_score, r_rules, gate) <- C.evaluate(y, l)       # no model call
 7      if gate >= tau then
 8          return y, trace + snapshot(t), gave_up = false
 9      if t = T_max then                                  # ceiling reached
10          y* <- argmax over candidates of (gate, -attempt)
11          return y*, trace + snapshot(t), gave_up = true
12      f <- F.reflect(a_score, r_rules, l)                # one model call
13      trace <- trace + deepcopy(snapshot(t))             # before mutation
14      if overlap(E, E_previous) < theta_overlap then
15          q <- augment(base_query(p, l), keywords(r_rules))
16      E <- R.retrieve(q, level = l, k = 10)
17      t <- t + 1
```

*Algorithm 5.1. The bounded generation loop. Line 5 is the only text-generating
call and line 12 the only auxiliary one; lines 3, 6 and 16 make no model call.
The plot remains anchored in the query at line 15 — failed-rule keywords augment
the query and never replace it.*

Five guarantees follow from the listing. Each is asserted by at least one named
test rather than left to inspection: twenty tests across three files cover the
controller, its state object and the retrieval anchoring, and the mapping from
guarantee to test is given in Appendix A.

**One Writer call per attempt, and one Reflector call per failure except the
last.** No Reflector call is made when the ceiling is reached, because there is
no subsequent attempt to feed. This is a cost decision, not a tidiness one: a
terminal reflection would inflate expected calls against the model in
Table 5.1 without changing any emitted text. The forced-three variant used as the
expensive endpoint in Section 5.6 is asserted at three Writer calls, two
Reflector calls and five logical calls in total, which is where the five-call
figure in Table 5.4 originates.

**The plot is never displaced from the query.** Line 15 augments the base query
with keywords drawn from the failed rules; it does not substitute them. A loop
permitted to rewrite its query freely could drift onto a different film, and the
retrieved evidence would then be evidence for a different task.

**Query revision is conditional, not automatic.** Re-retrieval is only allowed
to change the query when the new evidence overlaps the previous attempt's below
the registered threshold of 0.50, which is the pre-committed routing-ablation
trigger. When the same exemplars come back, the loop does not pretend to have
found new evidence.

**Snapshots precede mutation.** Line 13 deep-copies before the state advances,
for the reason given in Section 5.1.

**Ties resolve to the earliest attempt.** At the ceiling, line 10 maximizes the
pair (gate score, negative attempt index), so an equal-scoring later draft
loses. Preferring the later draft would flatter the loop in precisely the metric
the threshold objective divides by, namely calls per accepted generation.

The cost of this loop can be written down exactly. Let $q$ be the per-attempt
probability that a draft passes the gate. Charging one Writer call per attempt
and one Reflector call per non-terminal failure, and charging nothing for the
Researcher and Critic because neither calls a model,

$$
\mathbb{E}[\text{calls}] = 1 + 2(1-q) + 2(1-q)^2, \qquad
P(\text{accept}) = 1 - (1-q)^3 .
$$

Table 5.1 evaluates both expressions and reports the ratio, which is the cost of
obtaining one accepted generation.

**Table 5.1. Expected cost of the bounded loop as a function of the per-attempt
pass rate**

| Per-attempt pass rate $q$ | $\mathbb{E}[\text{calls}]$ | $P(\text{accept})$ | Calls per accepted generation |
|---:|---:|---:|---:|
| 0.10 | 4.420 | 0.2710 | 16.310 |
| 0.30 | 3.380 | 0.6570 | 5.145 |
| 0.50 | 2.500 | 0.8750 | 2.857 |
| 0.65 | 1.945 | 0.9571 | 2.032 |
| 0.80 | 1.480 | 0.9920 | 1.492 |
| 0.99 | 1.020 | 1.0000 | 1.020 |
| 1.00 | 1.000 | 1.0000 | 1.000 (degenerate) |

The first three columns are evaluations of the two expressions above; the fourth
is as recorded in the registered cost model. The final column is
**monotonically decreasing**, and that is the finding that shaped Section 5.6.
Minimizing cost alone selects $q = 1$, that is $\tau = 0$: the cheapest loop is
the one that never rejects anything and therefore never revises. Cost
minimization is not merely a weak criterion for a verifier threshold; it is a
criterion whose optimum abolishes the verifier. The cascade-routing result from
which this objective was adopted proves threshold policies optimal *subject to*
an accuracy constraint bounded by the measured accuracies of the cheap and
expensive systems [@b88]. An earlier version of the present protocol adopted the
objective and dropped the constraint, and specified instead a target first-pass
rate of 60–70 per cent. A target rate is not an objective, and a threshold
cannot be optimal for an objective that was never stated. Section 5.6 restores
the constraint, and states which verifier is allowed to measure it.

A worked end-to-end trace of one execution of this loop — retrieved identifiers,
both drafts, both scores, the Bangla feedback string and the post-hoc outcome
score — is given in Appendix E.7. That case was selected by a rule stated before
the case was seen (the lexicographically first seed-42 hybrid case requiring more
than one attempt) rather than chosen for how well it reads, which is the only way
a single illustrative example can appear in a thesis without functioning as
advertising.

## 5.4 Retrieval and the shared prompt contract

The retrieval index holds **886 Region-A R1 reviews: 534 at Level 0 and 352 at
Level 1**, encoded with `sentence-transformers/LaBSE` in a cosine space as the
collection `r1_regionA_k2`. Embeddings are L2-normalized at encoding time so
that the store's inner product *is* cosine similarity, rather than being
converted to cosine afterwards. The index is the 804 Verifier-A training rows
plus the 82 development reviews. Including the development rows is admissible
because retrieval is not a fitted classifier and the threshold of Section 5.6 is
tuned on separate development *plots*, not on these reviews; nothing in the
index is used to fit an acceptance decision.

The index contains **zero R2 identifiers and zero Gold-300 identifiers**. Both
counts are checked in the index builder before any vector is written and checked
a second time against the split map directly, and the admitted row set carries
the digest `85fc2d7d7ad3281b9dd99a7a0a01f8221a5e7ab762d1c69a0924bbc4468b45bb`.
The manifest that records these facts is explicit that it certifies membership
and nothing about retrieval quality; no claim in this thesis rests on the
exemplars being good, only on their being admissible.

Retrieval requests the top ten exemplars at the requested level, with the level
filter applied **inside the query** rather than by filtering the results
afterwards. The distinction is not cosmetic. Post-filtering returns fewer than
ten exemplars whenever the unfiltered top ten straddle both levels, so the
Writer's prompt would silently vary in length between calls, and a prompt-length
difference correlated with retrieval difficulty would be indistinguishable from
a treatment effect. Filtering in the query keeps $k$ equal to ten for every
call.

A single prompt renderer supplies every condition. Zero-shot is the same base
prompt with no exemplars and no feedback; retrieval conditions add exemplars;
revision conditions add feedback. Constructing the baselines from the same
renderer prevents the most common way a verification result is inflated, namely
giving the baseline a weaker task definition than the treatment and then
attributing the difference to verification. Bangla characters are preserved
exactly, and the frozen prompt expresses the axis through positive prototypes of
each level rather than a list of forbidden cues, so that a model cannot satisfy
the instruction by avoidance alone.

The prompt imposes a uniform 20-word ceiling at both levels. This was introduced
to suppress the length confound identified in Chapter 3, and it reduced but did
not eliminate it. The confound deserves to be stated plainly here because it
bounds every level-recovery claim in the thesis: a word count alone recovers the
requested level at an AUC of 0.9111 under length control and 0.9894 at free
length. Recent work on decoupling length from specificity in description
evaluation shows why this cannot be dismissed as a nuisance parameter — length
and specificity are entangled in the construct itself, not merely in the
estimator [@b81]. The system therefore reports length diagnostics beside every
control result and never claims length neutrality.

## 5.5 Neural gating and symbolic diagnosis

Verifier-A supplies the acceptance score; the symbolic component names what a
candidate did wrong. That division of labour is C6, and this section reports the
measurement that produced it, because the division was not a preference.

The external diagnostic path exists because intrinsic self-correction is
unreliable when the model is asked to supply its own missing evidence: a model
that could identify the defect would in general have avoided it, and the
literature documents self-correction degrading outputs when no external signal
is available [@b5; @b6]. The Critic supplies exactly such an external signal,
and the Reflector's role is confined to translating it.

Whether the symbolic term should also *decide* was registered as a sensitivity
question rather than assumed either way. A hybrid gate score
$g = w \cdot a + (1-w) \cdot r$ was swept over a 21-point grid of $w$ under both
length-controlled and free-length development conditions, with three outcomes
pre-committed before any generation existed: `SYMBOLIC_INERT` if the curve were
flat, `SYMBOLIC_EARNS_ITS_PLACE` if a grouped held-out test favoured the
mixture, and `SYMBOLIC_HARMS` if neural-only beat the selected mixture.

The observed result matched none of them. Every one of five held-out folds,
grouped by plot, selected $w = 1.0$, with a mean $\Delta$AUC against neural-only
of exactly $+0.0000$ and a record of zero wins, five ties and zero losses. So
the mixture does not earn its place, and it also does not harm. Yet the curve is
demonstrably not flat: **50.8 per cent of generations under length control and
39.2 per cent at free length change PASS/FAIL somewhere across the range of
$w$.** A component that flips the verdict on between two and five of every ten
outputs is not inert. The registered rule does not resolve this combination, and
the audit state is recorded as `PRECOMMITMENT_UNRESOLVED`.

The phrasing matters, so it is worth being precise about what is and is not
being said. `PRECOMMITMENT_UNRESOLVED` is **not a fourth scientific outcome
invented after the fact**; it is the statement that the pre-registered decision
rule was incomplete and did not cover the observed data. The honest reading is
that the symbolic term is *consequential but not predictive*: it moves
acceptance decisions without improving the accuracy of those decisions. Those
two facts are jointly coherent, and together they are an argument for exactly the
placement the framework adopts. A signal that changes verdicts without improving
them must not be allowed to adjudicate; a signal that localizes a defect can
still be useful for saying *what* to fix. Consequently no single $w$ is selected,
no hybrid-accuracy claim is made anywhere in this thesis, and the symbolic module
is retained solely for failed-rule naming and feedback localization.

Table 5.2 explains why the symbolic scorer behaves this way, and the explanation
is more damaging to the adjudication reading than the held-out ties are. The
scorer is a logistic model over 11 features fitted on 82 development rows — 7.45
rows per feature — reaching 0.6570 macro-F1 by resubstitution but only
$0.5150 \pm 0.0713$ under stratified five-fold cross-validation, against a
majority baseline of 0.3926. Removing whole feature families and re-running
cross-validation localizes what little signal exists.

**Table 5.2. Symbolic feature families and their leave-one-family-out
contribution**

| Feature family | Cross-validated macro-F1 without it | $\Delta$ | Registered as gameable |
|---|---:|---:|---|
| F2_length | 0.6232 | −0.1082 | yes |
| F4_connective | 0.5339 | −0.0189 | yes |
| F5_sentiment | 0.5338 | −0.0188 | yes |
| F6_richness | 0.4764 | +0.0386 | no |
| F3_ortho | 0.4503 | +0.0647 | yes |

A negative $\Delta$ means performance *improved* when the family was removed, so
the family was contributing noise; a positive $\Delta$ means the family carried
signal. Read that way, the two families that carry signal are orthographic form
and lexical richness, and orthographic form — the larger of the two — was
pre-registered as **gameable**. It is exactly the property a generator can
satisfy superficially once the Reflector names it. The pre-commitment recorded
in advance that a contribution concentrated in gameable families would be read
as a negative result about the hybrid design, and it is read that way here. The
striking entry is F2_length: removing length features improves cross-validated
performance by 0.1082, which means the symbolic scorer's length features were
actively harmful on held-out folds while length alone predicts the requested
level at above 0.91 AUC. The symbolic scorer is not failing to use length; it is
using it badly.

**Table 5.3. Neural–symbolic weight sensitivity and registered interpretation**

| Development condition | n | Symbolic-only AUC ($w=0$) | Neural-only / best AUC ($w=1$) | Length-only AUC (Bangla) | Outputs changing verdict somewhere on the curve | Held-out mixture $\Delta$ vs neural | Standing |
|---|---:|---:|---:|---:|---:|---:|---|
| Length-controlled | 120 | 0.3417 | 0.8333 | 0.9111 | 50.8% | +0.0000; 0 wins, 5 ties, 0 losses | `PRECOMMITMENT_UNRESOLVED` |
| Free-length | 120 | 0.0656 | 0.8658 | 0.9894 | 39.2% | +0.0000; 0 wins, 5 ties, 0 losses | `PRECOMMITMENT_UNRESOLVED` |

Two features of Table 5.3 should be read together. Symbolic-only AUC is not
merely weak but **below chance** — 0.3417 and 0.0656 — which means the symbolic
score is anti-correlated with the requested level rather than uninformative
about it; an inverted symbolic scorer would outperform the honest one. And the
reference point for the neural column is not 0.5 but the length-only probe in
the adjacent column, which exceeds it in both conditions. Neither the symbolic
score nor the hybrid is the interesting comparison for this framework; the
length probe is, and Chapter 6 reports against it.

Where the symbolic component *is* permitted to gate — the registered
symbolic-loop condition of Section 5.8 — it uses its own threshold of
$\tau_{\text{sym}} = 0.1816651$, which accepts 39 of the 60 development cases.
That condition exists as a control on the neural loop, not as a competing
proposal, and its inclusion is what allows Chapter 6 to distinguish the effect of
*having* a gate from the effect of having a *good* gate.

## 5.6 Threshold and stopping-policy selection

The acceptance threshold is selected on 60 held-out development plot-level cases
by a constrained cost objective adopted from calibrated cascade routing [@b88].
Following that formulation, the constraint is not free-floating but bounded by
the measured quality of the cheap and the expensive system, and the selected
operating point maximizes quality gained per unit of cost:

$$
\tau^{*} \;=\; \arg\max_{\tau}\;
\frac{Q_B(\tau)-\alpha_{\text{lo}}}{\mathbb{E}[\text{calls}\mid\tau]},
$$

where

- $Q_B(\tau)$ is outcome quality at threshold $\tau$, measured **by Verifier-B
  after the fact**;
- $\alpha_{\text{lo}} = 0.640501$ is the cheap endpoint: $\tau \to 0$, where the
  Critic never rejects, so every case emits its first retrieval-conditioned draft
  at exactly 1.000 calls and a first-pass rate of 1.000;
- $\alpha_{\text{hi}} = 0.866272$ is the expensive endpoint: forced three
  attempts on every case, with best-of-three selected by Verifier-A.

Both endpoints are defined beside the equation rather than in surrounding prose
because they are the objective's constraint, not context for it. Both are
measured on the same 60 cases, and — this is the load-bearing restriction, and it
is the present framework's addition to the cascade formulation rather than
something inherited from it — **both are measured by Verifier-B, never by
Verifier-A**. Constraining a loop by the quality judgement of the verifier
sitting inside that loop is precisely the Goodhart collapse that inviolable
rule 6 exists to prevent: the loop would be tuned to satisfy its own examiner,
and the resulting threshold would be optimal with respect to a quantity the loop
can inflate directly. Verifier-B can measure the constraint because it never
influences generation.

Candidate thresholds are the observed gate scores rather than a uniform grid.
This too was a repair rather than a choice. On the development score
distribution, the originally specified uniform grid from 0.30 to 0.95 in steps
of 0.05 reaches pass rates spanning only 0.06 to 0.38 and sits flat at the same
pass set across eight consecutive grid points, whereas thresholds placed at
observed score values recover 81 distinct operating points. The specified grid
could not have reached the specified target rate on this distribution, and that
mismatch was discovered by checking the grid against the target rather than by
reasoning about either. Scores are reported on the temperature-calibrated scale,
which is admissible because temperature scaling is a monotone single-parameter
rescaling: every threshold on the calibrated scale has an exact twin on the raw
scale producing an identical PASS/FAIL partition, so the choice of scale affects
interpretability and nothing else [@b87].

**Table 5.4. The three registered operating points on the development frontier
($n=60$ cases)**

| Quantity | Cheap endpoint $\tau\to 0$ | **Selected $\tau^{*}=0.4384071$** | Expensive endpoint, forced three |
|---|---:|---:|---:|
| Verifier-B outcome quality | 0.640501 | **0.802219** | 0.866272 |
| Mean logical model calls | 1.000 | **2.000** | 5.000 |
| First-pass acceptance | 1.000 | **0.650** | 0.000 |
| Final acceptance | 1.000 | **0.867** | 0.000 |
| Cases reaching the ceiling without acceptance | 0 | **8 of 60 (0.133)** | not applicable |
| Mean emitted attempt | 1.000 | **1.367** | 1.867 |
| Objective value | — | **0.080859** | — |

Three readings of Table 5.4 are needed, and the third is a correction to how the
frontier was previously described.

First, the expensive endpoint costs **five** logical calls, not three. Forcing
three Writer attempts also forces two Reflector calls, and the cost model of
Table 5.1 charges both. At $q = 0$ the model gives $1 + 2 + 2 = 5$, which is
exactly the measured figure; the agreement is a consistency check on the
accounting, not a coincidence. Stating the endpoint as "three attempts" while
budgeting five calls is the kind of slippage that makes a cost comparison
unfalsifiable, so the call count is reported rather than the attempt count.

Second, the selected point's cost of 2.000 calls reconciles exactly with the
stopping distribution of Section 5.7. Thirty-nine cases accept at attempt one
for one call each, twelve accept at attempt two for three calls, one accepts at
attempt three for five, and the eight cases that reach the ceiling spend five
each: $39 + 36 + 5 + 40 = 120$ calls over 60 cases, or 2.000. The constant-rate
model in Table 5.1 evaluated at the observed first-pass rate of 0.65 predicts
1.945, and the small discrepancy is informative rather than an error — the
per-attempt pass rate is not constant across attempts, as Section 5.7 shows.

Third, **two different denominators can be used to express how much of the
available gain the selected point captures, and the thesis reports both rather
than choosing the flattering one.** Measured against the frontier's own
endpoints, the selected point captures
$(0.802219 - 0.640501)/(0.866272 - 0.640501) = 71.63$ per cent of the achievable
gain. Measured against a post-hoc Verifier-B oracle that picks the best of the
three attempts with full knowledge of the outcome score — a ceiling no
deployable policy can reach, since Verifier-B is forbidden from the loop — the
same point captures 69.74 per cent, and the forced-three policy captures 97.36
per cent. These are different quantities with different denominators, and
earlier drafts of this chapter used the phrase "achievable gain" for the first
without distinguishing it from the second. Both are reported here, each with its
denominator named, because the gap between them is itself the measure of how much
the isolation wall costs.

Finally, one descriptive check on the threshold's behaviour across levels. A
permutation test on attempt-one mean gate score, Level 1 minus Level 0, gives an
observed difference of $+0.082894$ with 30 cases per level and 5,000 shuffles,
$p = 0.4687$ two-sided. This is registered as descriptive and **not** as a gate:
$p = 0.4687$ means the difference was not detected at this sample size, which is
not the same as the levels being equally easy. A single threshold is applied
globally to both levels, with per-level performance reported separately
throughout Chapter 6.

## 5.7 Development loop dynamics

This section reports what the loop did on the 60 development cases at the
selected threshold, and then what its failures looked like. Everything here is
descriptive and none of it is part of the frozen 5,400-case result surface.

**Table 5.5. Attempt-level scores and transition dynamics, 60 development cases
at $\tau^{*}=0.4384071$**

| Quantity | Attempt 1 | Attempt 2 | Attempt 3 |
|---|---:|---:|---:|
| Mean Verifier-A score | 0.646845 | 0.734036 | 0.671316 |
| Mean symbolic diagnostic score | 0.475833 | 0.489569 | 0.465913 |
| Mean Verifier-B outcome score | 0.640501 | 0.729517 | 0.711472 |
| Pass rate if the attempt is reached | 0.650 | 0.750 | 0.683 |
| | **Transition 1 → 2** | **Transition 2 → 3** | |
| Mean change in gate score | +0.087190 (35 up, 25 down) | −0.062719 (25 up, 35 down) | |
| Mean change in Verifier-B score | +0.089016 (31 up, 29 down) | −0.018045 (23 up, **37 down**) | |
| Mean change in symbolic score | +0.013737 (31 up, 29 down) | −0.023656 (28 up, 32 down) | |
| A and B disagree on direction | 18 of 60 | 18 of 60 | |
| Mean normalized character edit distance | 0.665138 | 0.633043 | |
| Mean change in word count | +0.033 words | +0.283 words | |

The shape of Table 5.5 is the empirical case for a ceiling of three rather than a
larger number, and it is a case that could have come out the other way. The first
revision helps by both measures and by similar amounts: gate score rises 0.0872
and the independent outcome score rises 0.0890. The second revision does not.
Gate score falls by 0.0627, outcome score falls by 0.0180, and Verifier-B
declines on **37 of 60 cases** — the majority. A third attempt is not merely of
diminishing value on these data; it is on balance harmful, and the retry ceiling
is therefore doing work rather than expressing caution. The edit distances above
0.63 in both transitions confirm that the Writer is genuinely rewriting rather
than lightly editing, so the second revision's regression is not an artifact of
the model refusing to change anything.

The pattern is consistent with treating self-correction as a feedback-control
process that has a stability threshold rather than a monotone improvement
schedule: additional correction rounds are beneficial only while the correction
signal carries more information than the perturbation it introduces, and beyond
that point further iterations degrade the output [@b18]. What the present data
add is a case where the crossover is observed directly, and observed by a scorer
that had no influence on the corrections being applied.

The disagreement counts deserve emphasis because they are the in-chapter
foreshadowing of the Goodhart analysis in Chapter 6. In each transition, the
in-loop scorer and the out-of-loop scorer disagree about whether the revision
improved the text on 18 of 60 cases. In the second transition the modal cell is
the one where both decline (27 cases), but the cell where the gate rises while
the outcome score falls holds 10 — cases in which the loop was, by its own
measure, succeeding and by an independent measure making things worse. That
divergence is measurable here only because Verifier-B was kept out of the loop.

The stopping distribution is as follows. Accepted stops occur at attempts one,
two and three for 39, 12 and 1 cases respectively, and 8 cases reach the ceiling
without acceptance, giving 52 accepted of 60. The distribution of *emitted* best
attempts is 41, 16 and 3, which differs from the accepted-stop distribution
because a case that reached the ceiling still emits its highest-scoring draft,
and that draft need not be the last one.

The eight ceiling cases are not a random sample of the corpus, and their outcome
scores make that concrete: cases that reached the ceiling emit text with a mean
Verifier-B score of **0.503921**, against **0.848111** for accepted cases, while
the pooled mean over all 60 is 0.802219. The loop's failures are genuinely
harder cases rather than arbitrary ones, and a mean computed only over accepted
cases would overstate the system's quality by more than a third of the range
between the two endpoints. This is also the reason Chapter 6 reports coverage
beside every conditional mean. Six of the eight are Level-1 requests
(BN046, BN048, BN066, BN105, BN110, BN115) against two Level-0 requests
(BN043, BN063). Level 1 is the sparser side of the retrieval index at 352 rows
against 534, so the direction is at least consistent with an evidence-supply
explanation; with eight cases no test is warranted and none is performed, and
the permutation result in Section 5.6 did not detect a level difference in
attempt-one scores.

A second, larger-sample descriptive quantity points the same way. Against the
post-hoc outcome oracle of Section 5.6, the selected threshold captures 82.00
per cent of the available gain on Level-0 requests but only 39.07 per cent on
Level-1 requests. Both figures are registered as post-hoc descriptive and
neither is a selection rule, but the gap between them is more than twofold and
rests on 30 cases per level rather than on eight. Taken together with the
ceiling-failure split, the development evidence suggests that the loop's
difficulty is concentrated on the specific end of the axis. Chapter 6 reports
every result per level for this reason, and Chapter 7 returns to whether sparser
retrieval evidence is the explanation.

The registered protocol called for a coded failure taxonomy over a sample of
**fifty** cases. The complete census of ceiling failures at the selected
threshold contains **eight**, so the planned sample does not exist and the
taxonomy was coded over the census instead. Of the eight, one is coded
`off_topic` — a draft asserting that a film was Ritwik Ghatak's last work, which
is false — and two fall into a post-hoc `other` category covering a medium
misidentification (a film described as a serial, *সিরিয়াল*) and a
specificity-level mismatch. The remaining **five exhibit no observable
registered error at all**. Coding was performed by a single coder with the
researcher's explicit authorization and reviewed by the researcher; no
independent second coder was used, so no inter-coder agreement statistic exists.

What this costs the analysis should be stated rather than left for a reader to
infer, since the deviation is disclosed in the result file but its consequences
are not. Three distinct limitations follow. First, with eight cases the smallest
resolvable proportion is one in eight, so any failure mode whose true prevalence
is below roughly twelve per cent is expected to be absent from this census
altogether; the four categories recording zero counts are uninformative rather
than falsified. Second, because agreement was never estimated, the category
assignments have no reliability, and a taxonomy without a reliability estimate
cannot support a claim that two failures are of the same kind. Third and most
substantively, five of the eight failures — a clear majority — could not be
described by any registered category. That is a finding about the instrument, not
only about the sample: the registered taxonomy failed to describe most of its own
census. The correct conclusion is therefore narrow. These eight are a complete
description of ceiling failures at this threshold on these development cases; no
population-level claim about failure prevalence, and no claim that the taxonomy
is adequate, is made from them. The deviation is logged in the protocol, and the
per-case census appears in Appendix E.6.

Figure 5.2 shows the frontier and the attempt-level dynamics together.

![Development threshold frontier and retry dynamics](../figures/s4_loop_dynamics.svg)

*Figure 5.2. Development quality–cost frontier and retry dynamics. The selected
threshold ($\tau^{*}=0.438$) is an interior operating point between the one-call
retrieval endpoint and forced-three revision, not the maximum-quality endpoint.
The attempt-level panel shows that the second revision is not monotonically
beneficial. These 60 development cases are not part of the frozen 5,400-case
result surface.*

## 5.8 The ten experimental conditions

The main experiment instantiates ten conditions through the same prompt renderer
and the same data contracts: zero-shot, instance-randomized static few-shot,
retrieval-only, the neural loop, the symbolic loop, the neural loop with
symbolic feedback, intrinsic self-critique, external-role self-critique, a
large-model judge loop, and blind resampling. The two self-critique arms
instantiate the established iterative-refinement and verbal-feedback
formulations [@b13; @b14], and they are controls rather than proposals: they test
whether the improvement attributed to the framework requires an external verifier
at all, or whether a model criticizing its own draft suffices.

**Table 5.6. Frozen ten-condition intervention matrix**

| Condition | Example source | Acceptance/selection signal | Revision feedback | Max Writer calls | Max auxiliary calls | Verifier-B in loop |
|---|---|---|---|---:|---:|---|
| Zero-shot | None | None; emit first draft | None | 1 | 0 | No |
| Static few-shot | 10+10 instance-randomized R1 examples | None; emit first draft | None | 1 | 0 | No |
| RAG-only | Top-10 same-level R1 retrieval | None; emit first draft | None | 1 | 0 | No |
| RAG + neural loop | Top-10 R1 retrieval | Verifier-A, $\tau=0.4384071$ | Neural score-derived bounded feedback | 3 | Up to 2 Reflector | No |
| RAG + symbolic loop | Top-10 R1 retrieval | Symbolic score, $\tau=0.1816651$ | Named failed symbolic rules | 3 | Up to 2 Reflector | No |
| RAG + neural + symbolic feedback | Top-10 R1 retrieval, query augmented by failed-rule keywords | Verifier-A, $\tau=0.4384071$ | Neural result plus named symbolic failures | 3 | Up to 2 Reflector | No |
| Intrinsic self-critique | Top-10 R1 retrieval | Model self-critique | Critique placed in assistant role | 2 | 1 critique | No |
| External-role self-critique | Top-10 R1 retrieval | Same byte-identical critique | Critique placed in user role | 2 | 1 critique | No |
| Large-model judge loop | Top-10 R1 retrieval | Judge PASS/FAIL and target-fit score | Bounded judge feedback | 3 | Up to 3 judge | No |
| Blind resampling | Top-10 R1 retrieval | Verifier-A selects best candidate prefix | None; fresh samples | Up to 5 | 0 | No |

Three design points in Table 5.6 carry more weight than their single table rows
suggest.

**The two self-critique arms differ only in message role.** Both receive a
byte-identical critique string; one places it in the assistant role and the
other in the user role. Identity is enforced by comparing SHA-256 digests of the
UTF-8 encoded critique before the pair is admitted, so the contrast isolates
message placement and nothing else. This is a deliberately narrow manipulation
whose purpose is to detect whether an apparent self-correction effect is in fact
a prompt-formatting effect.

**The judge condition uses a specific model, and it is named.** The judge is
`gemma-4-26b-a4b-it`, accessed over the provider's interactions interface with
seed 42, high reasoning effort, and a 512-token output ceiling, under a
registered enumerated feedback contract. It sees the plot, the requested level,
the draft and the rubric, and it never sees a Verifier-A or Verifier-B score.
Transport-level retries — three are permitted — are not logical model calls and
are not charged as such, since a retried request produces one verdict. Naming
the judge matters because a judge condition is not reproducible against an
unnamed model, and because the judge is substantially larger than the Writer,
which makes this the thesis's strongest control: it asks whether a small frozen
probe inside the loop can match a large model reasoning about the same draft.

**Blind resampling is a matched-compute control with a specific ancestry.** It
draws up to five independent retrieval-conditioned samples and lets Verifier-A
select among them, reconstructing verifier-ranked candidate selection as
introduced by Cobbe and colleagues, in which a trained verifier scores many
sampled completions and the highest-ranked is returned [@b58]. The difference
from the loop conditions is precisely one thing: here the verifier only *ranks*
and never triggers a revision. Recent matched-compute studies report conflicting
refinement-versus-resampling outcomes across tasks, which is why this control is
necessary rather than decorative — without it, any advantage of the loop could be
an advantage of spending more compute [@b16; @b17]. Section 5.9 states the
selection rule that keeps the comparison matched.

Conditions three through nine share a byte-identical initial retrieval-
conditioned draft at each plot–level–replicate key, while still being charged
their own logical cost. This paired schedule removes irrelevant sampling
variation from every comparison among them without concealing any of their cost.
Table 6.1 counts both text generations and auxiliary calls, so a verifier loop
can exceed three logical calls without exceeding three Writer drafts; the
ceilings in Table 5.6 describe the treatment contracts, and realized costs are
reported in Chapter 6. Verifier-B appears only after generation, for outcome
scoring.

## 5.9 Algorithm 5.2 — blind-resampling selection under a matched budget

A resampling control is only a control if it is not permitted to spend more than
the loop it is being compared against. The naive implementation — draw five
samples and keep the best — is not matched, because the loop rarely spends its
full budget: at the selected threshold it averages 2.000 calls against a ceiling
of five. Comparing a five-sample selector against a two-call loop and reporting
the selector's quality would measure the budget, not the mechanism.

Algorithm 5.2 states the rule that prevents this. The budget is the compute the
loop actually realized on the same case, and the selector may consider only the
largest *nested prefix* of its candidate pool whose cumulative realized cost fits
inside that budget.

```
Algorithm 5.2  Largest nested prefix within a matched budget

Input:  candidate costs c[1..n] in generation order   (realized, not nominal)
        budget B                                      (realized loop compute
                                                        on the same case)
Output: m, the number of candidates the selector may consider

 1  if B <= 0 or n = 0 then
 2      raise ContractError("budget and candidate pool must be positive")
 3  total <- 0;  m <- 0
 4  for i <- 1 to n do
 5      if c[i] is not finite or c[i] <= 0 then
 6          raise ContractError("each candidate cost must be positive")
 7      total <- total + c[i]
 8      if total <= B then
 9          m <- i
10  if m = 0 then
11      raise ContractError("loop budget cannot fund even one sample")
12  return m
```

*Algorithm 5.2. Matched-budget prefix selection. The selector then applies
Verifier-A to candidates 1 through m and emits the highest-scoring one.
Candidates are consumed in generation order, so the admitted set is a prefix and
never a subset chosen with knowledge of the scores.*

Three properties of Algorithm 5.2 are what make the control honest, and each
closes a specific way the comparison could have been rigged.

The admitted set is a **prefix in generation order**, not an arbitrary subset.
Choosing which five candidates to price would allow the cheapest ones to be
selected after their scores were known, which is selection on the outcome
wearing a budget's clothing.

The budget is **realized loop compute on the same case**, not the loop's nominal
ceiling. A case on which the loop accepted immediately funds fewer resamples than
one on which the loop revised twice, which is the correct behaviour: the control
is allowed exactly what the treatment spent, case by case.

**Insufficient funding raises rather than degrades.** If the loop's realized
budget cannot fund even one sample, the contract raises an error instead of
silently emitting a zero-candidate or unpriced result. A control that quietly
falls back when its budget is exhausted produces a comparison whose matching
holds only on the cases where matching was easy.

## 5.10 Main-run execution contract

The frozen Writer is `google/gemma-3-12b-it`, loaded locally with 4-bit
NormalFloat quantization, generating at `max_new_tokens=80`, temperature 0.8 and
top-p 0.9 under the 20-word prompt ceiling described in Section 5.4. Replicate
seeds 42, 43 and 44 are crossed with every evaluation plot, level and condition,
yielding the frozen surface of 5,400 cases: 90 plots by 2 levels by 10
conditions by 3 replicates. The replicates are paired sensitivity blocks and are
**not** independent experimental replications, and Chapter 6's inferential family
treats them accordingly.

Ingestion is gated before any model loads: a checkpoint must present the exact
registered key set, parse as valid and unique JSON records, and carry an allowed
clean producing commit. The judge condition additionally archives its structured
verdict, target-fit score, feedback, token usage and model version. Every
completed case records the plot identifier, target level, condition, replicate
seed, prompt arm, attempt count, emitted draft, logical calls and tokens, and
stopping status. Outcome scoring runs as a separate process after generation and
joins on the frozen case key.

The remaining execution detail — the complete configuration-to-output map, the
runtime environments, the artifact lineage and the statistical contract — is
specified in Appendix A and is not restated here. Two boundaries, however, are
substantive enough to belong in the chapter that defines the framework. Global
seed 42 initializes every script as its first action, so the loop's routing is
reproducible rather than merely recorded. And the live local demonstration
interface **is not the frozen experiment**: it sends the supplied plot to a
hosted judge-family Writer and an additional operational plot-support check,
whereas the main run uses frozen local Gemma-3 generation with outcome-only
Verifier-B. The application does not persist user plots or live-call records in
the repository. Its outputs contribute no evidence to any result in this thesis,
and its model, processing and persistence boundaries are documented in Appendix
H.

## 5.11 Chapter summary

The framework specified here operationalizes external verification as an
inspectable state machine rather than as an opaque *agent*. Four roles are
defined, two of which make no model call; acceptance is decided by a frozen
linear probe whose determinism is what makes the Chapter 4 isolation wall
enforceable; the symbolic component explains failures without adjudicating them;
and an outcome verifier that never touches the loop makes overoptimization
measurable.

Four results from the development phase shaped the design rather than merely
accompanying it. The cost model showed that minimizing cost alone drives the
threshold to zero and abolishes the verifier, which is why the selected operating
point is a constrained argmax with both endpoints measured by the out-of-loop
verifier. The weight sweep showed the symbolic term to be consequential but not
predictive, which is why it names failures instead of gating them. The attempt
dynamics showed the second revision to be, on balance, harmful by an independent
measure, which is why the retry ceiling is three and is enforced. And the failure
census showed that most of the loop's residual failures fall outside the
registered taxonomy, which is why no prevalence claim is made from it.

Three quantities in this chapter should be carried into the next. The selected
threshold buys 71.63 per cent of the frontier's achievable gain at 2.000 of a
possible 5.000 logical calls; cases that reach the ceiling emit markedly weaker
text (mean outcome score 0.503921 against 0.848111), so coverage must be read
beside every conditional mean; and the in-loop and out-of-loop verifiers already
disagree about the direction of revision on 18 of 60 development cases before the
main experiment begins. Chapter 6 evaluates this architecture against nine
matched alternatives on the frozen 5,400-case surface, and reports what that
disagreement becomes at scale.
