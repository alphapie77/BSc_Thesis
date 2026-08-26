# Chapter 4 — Verifier Development, Circularity, and Isolation

## 4.1 Design rationale, verifier roles, and what this chapter contributes

Chapter 3 established that a reproducible two-level cut through an
engagement-specificity continuum exists in region A of the review corpus and
that human annotators can recover it under length-matched comparative judgment.
That result licenses the axis as an object of study. It does not yet provide any
way to measure the axis automatically, and without such a measurement no
generation experiment can be run at all: a system asked to write at Level 1
cannot be scored unless something can decide, cheaply and repeatedly, whether a
piece of text sits at Level 1. This chapter builds that instrument. It builds
two of them, deliberately unequal in what they are allowed to see and allowed to
influence.

Verifier-A is the in-loop gate. It scores each draft the generator produces, it
determines acceptance against the frozen threshold introduced in Chapter 5, and
it selects among the candidates in the blind-resampling condition. Verifier-B is
an outcome-only evaluator. It never enters retrieval, prompting, feedback,
candidate selection, or regeneration; it is applied once, after all generation
has finished, to score what the system produced. The two classifiers are trained
on disjoint halves of the corpus and belong to different pretraining families,
and both are evaluated on the same 82-row development slice.

The reason for building two rather than one is a measurement problem rather than
a performance problem. Generation requires a scorer that can be called thousands
of times on ordinary hardware; evaluation requires a scorer that has not
participated in any of those calls. If a single model performed both roles, a
high final score would be uninterpretable, because a system that improved and a
system that learned the idiosyncratic boundary of its own judge would produce
the same number. Recent work on reward hacking in rubric-based reinforcement
learning treats separation between the optimised judge and the evaluating judge
as the standard defence against exactly this ambiguity [@b69]. The dual-verifier
design does not make either classifier ground truth. It creates a controlled
disagreement that can be inspected after generation has finished, and Chapter 6
inspects it.

It is worth stating plainly what this chapter does and does not answer, because
it is the only chapter of the thesis that resolves no research question of its
own. That is by design. A chapter that both constructed an instrument and
declared the instrument valid would beg the question it appeared to settle. What
this chapter supplies is the instrument itself, on which three research
questions then depend: RQ2's dependent variable is a Verifier-B probability,
RQ3's conditions are distinguished by what the in-loop gate does with
Verifier-A's score, and RQ4's diagnostic is the gap between the two verifiers'
scores on the same generated text. The chapter also produces one finding that
constrains how Chapter 3 may be read, reported in Section 4.4 and its
consequences drawn out in Section 4.5.

Finally, and throughout, the two classifiers reproduce the operational two-level
label defined in Section 3.10. Their scores are not independent estimates of
human validity. Human validity comes from the comparative intrusion study of
Section 3.9 and from the blinded evaluation of generated output in Chapter 6,
neither of which uses either verifier.

![Dual-verifier data and privilege isolation](../figures/dual_verifier_isolation.svg)

*Figure 4.1. Data and privilege isolation for the two verifiers. Gold-300 was
used only by the failed first human-rating instrument (598 of 600 possible
ratings; ordinal Krippendorff α = 0.4970; Gate 2 not computed), never for
fitting, retrieval, or thresholding. R1 supplies retrieval and the in-loop
Verifier-A; disjoint R2 supplies the outcome-only Verifier-B. The dashed wall
marks the privilege Verifier-B does not have: it cannot influence generation,
candidate selection, or retry.*

## 4.2 Training and evaluation protocol

All verifier development uses the labelled region-A rows of the frozen split.
Verifier-A and every arm of the backbone ablation train on the 804 R1 rows that
carry a two-level label, distributed 481 at Level 0 and 323 at Level 1.
Verifier-B trains on the 888 disjoint R2 rows, distributed 531 and 357. Both are
evaluated on the same 82-row development slice, 53 rows at Level 0 and 29 at
Level 1. Gold-300 is not read by any step in this chapter, and the ablation does
not read R2 at all, since R2 belongs to Verifier-B and that boundary is
inviolable rule 6. Each configuration asserts its expected row counts before
training and refuses to run on a mismatch, because a silently different *n*
would make every number reported here incomparable with the pre-registration
that fixed them.

The seven candidate recipes, their training budget, and the reason each was
registered as a candidate are given in Table 4.1. The budget is identical across
the five conventional fine-tuning arms. The two arms with their own published
training procedures, BERT-NLI transfer and SetFit, use those procedures at
matched wall-clock time, and that asymmetry is reported rather than concealed:
their results are not directly budget-comparable with the others. The maximum
sequence length of 128 tokens is generous rather than binding, since Chapter 3
established a median review length of eight words.

**Table 4.1. The seven registered backbone arms and their training budget**

| # | Arm key | Model | Kind | Why it was registered as a candidate |
|---|---|---|---|---|
| 1 | `banglabert` | `csebuetnlp/banglabert` | fine-tune | Bangla-native ELECTRA; the pipeline's default, and therefore the arm whose victory the design tacitly expected |
| 2 | `xlmr` | `xlm-roberta-base` | fine-tune | Without beating it, the claim that a Bangla-specific model is needed collapses |
| 3 | `muril` | `google/muril-base-cased` | fine-tune | Indic-specialised; reported as beating both BanglaBERT and XLM-R on Bangla emotion detection [@b26] |
| 4 | `mbert` | `bert-base-multilingual-cased` | fine-tune | Historical multilingual baseline |
| 5 | `indicbertv2` | `ai4bharat/IndicBERTv2-MLM-only` | fine-tune | Top scorer on a Bangla formal/colloquial style task close in kind to this one [@b28] |
| 6 | `setfit_labse` | `sentence-transformers/LaBSE` | SetFit | Contrastive few-shot learning designed for this sample size, on an encoder already present in the pipeline; registered with a pre-stated expectation of losing |
| 7 | `bert_nli` | `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` | NLI transfer | Reported gains of 10.7 to 18.3 points over classical models at 100 to 2,500 training texts, particularly on imbalanced data; this task has 804 rows at roughly 40 per cent minority [@b51] |

Shared budget for arms 1–5: learning rate in {2 × 10⁻⁵, 3 × 10⁻⁵}, four epochs,
batch size 16, maximum sequence length 128, seeds 42 through 46. Arm 6 uses 20
pair-sampling iterations, the published default. Arms 6 and 7 follow their own
published procedures at matched wall-clock.

Macro-F1 is the principal metric because the two levels are imbalanced at
roughly 65 to 35 in both the training and development slices, and accuracy on
such a split rewards a classifier for ignoring the minority level. Arms are run
over five seeds rather than three, and the variation across those seeds is
reported as a sensitivity measurement and never as a decision rule. This
distinction is not stylistic. There is direct evidence that small absolute
effect sizes combined with few repetitions readily produce wrong conclusions in
model comparison [@b46], that only a minority of transformer papers report
multiple runs at all and that robustness to seed and hyperparameter choice is
low [@b47], and there is a theoretical stability bound behind the phenomenon
[@b48]. Treating a mean over five seeds as though it settled a comparison would
be an instance of precisely the practice these papers document.

The registered decision rule is therefore a paired bootstrap significance test
over the development predictions, with 10,000 resamples, α = 0.05, and
Benjamini–Hochberg correction across all 21 pairwise comparisons [@b49; @b50].
The rule was fixed, together with the arm set and the tie-break, before any
backbone had been downloaded. Four outcomes were pre-committed: one arm
significantly best, in which case it becomes the verifier and the choice is
empirically justified; a set of arms statistically indistinguishable, in which
case the tie is reported as the result and broken on openly declared
non-performance grounds; BanglaBERT significantly beaten, in which case the
winner is used and the monolingual-versus-multilingual comparison becomes a
small finding in its own right; and every arm near chance, in which case the
two-level label is not learnable at this sample size from text of this length
and RQ2 cannot proceed as specified. No arm could be added after seeing a
result, none could be dropped for performing badly, and no hyperparameter search
beyond the two learning rates was permitted.

One property of the development slice must be disclosed before any number from
it is read. Dev-82 carries three roles: it is the surface on which each arm's
learning rate was selected, the surface on which both temperature scalings were
fitted, and the surface on which all results in this chapter are reported. The
consequence is quantifiable rather than vague. At 82 rows a single item is
0.0122 macro-F1, so any difference this chapter reports should be read in items
first and decimals second, and the arm means below are descriptive levels rather
than clean held-out estimates. The pre-registration states this in advance of
the numbers, which is the only order in which such a limitation can be recorded
without appearing to be an excuse.

## 4.3 Backbone ablation and the registered `TIE`

The ablation is load-bearing rather than decorative, and the reason is that the
Bangla classification literature does not settle the question the ablation asks.
A search of the 2023–2026 work on comparable tasks at comparable data sizes,
recorded before the run rather than discovered after it, returns three different
winners. MuRIL is reported as beating both BanglaBERT and XLM-R on Bangla
emotion detection [@b26]. XLM-R is reported above BanglaBERT, 94.0 against 93.4
per cent, on formal-versus-colloquial style classification over the BanglaBlend
dataset [@b27]. IndicBERTv2 is reported at 95.44 per cent above both XLM-R and
BanglaBERT on the *same* BanglaBlend data [@b28]. The last two are the sharpest
pair: one dataset yielding two different winners in two papers, with the first
margin at six-tenths of a point, removes any possibility of settling the matter
by citation. The
proposition that BanglaBERT is Bangla-native and therefore the correct verifier
backbone cannot be defended from the literature, which is what made a
pre-registered ablation the only available justification and made its outcome
genuinely unpredictable in advance.

**Table 4.2. Backbone ablation on dev-82: mean macro-F1 over five seeds**

| Arm | Mean macro-F1 | SD across five seeds | Selected learning rate | Standing after correction |
|---|---:|---:|---|---|
| `banglabert` | 0.9647 | 0.0209 | 3 × 10⁻⁵ | Tied; selected by non-performance tie-break |
| `setfit_labse` | 0.9590 | 0.0000 | 2 × 10⁻⁵ | Tied; SD is an implementation defect, not stability evidence |
| `indicbertv2` | 0.9560 | 0.0156 | 3 × 10⁻⁵ | Tied |
| `muril` | 0.9421 | 0.0391 | 3 × 10⁻⁵ | Tied |
| `mbert` | 0.9402 | 0.0125 | 2 × 10⁻⁵ | Tied |
| `xlmr` | 0.9360 | 0.0219 | 3 × 10⁻⁵ | Tied |
| `bert_nli` | 0.9298 | 0.0165 | 3 × 10⁻⁵ | Tied |

The SD is computed over the five seeds at the selected learning rate, not over
all ten runs per arm. Because that learning rate was selected by best mean on
this same development slice, the levels are not clean held-out estimates.

None of the 21 pairwise comparisons is significant after Benjamini–Hochberg
correction. The smallest unadjusted *p*-value in the entire family is 0.0960,
for BanglaBERT against XLM-R and for BanglaBERT against BERT-NLI; BanglaBERT
against mBERT follows at 0.0966. A robustness check that pooled across both
learning rates instead of selecting one returned the same verdict. The
registered outcome is therefore `TIE`, and it was the outcome the literature's
own disagreement made most likely.

BanglaBERT was selected by the pre-registered tie-break, which is smallest
parameter count first and the pipeline's default second, and which is applied on
non-performance grounds. Stated in the words the protocol requires: *the
backbone choice was not determined by the data.* No claim is made anywhere in
this thesis that BanglaBERT is empirically superior to the other six candidates
for this task.

Two consequences follow that matter more than the ranking. The first is
practical. If seven recipes spanning Bangla-native, Indic-specialised,
multilingual, contrastive few-shot, and NLI-transfer designs cannot be
distinguished on this task, then fine-tuning has bought nothing that a cheaper
mechanism could not buy, and the burden shifts to justifying its cost rather
than assuming its benefit. Section 4.4 collects that cost, and Section 4.6 acts
on it. The second is a matter of scale. The entire seven-arm spread, from 0.9298
to 0.9647, is 0.0349 macro-F1, which at this sample size is fewer than three
development items. A table whose full range is under three reviews is not a
table from which a backbone recommendation can be extracted, whatever its
significance tests had returned.

One arm requires a separate warning. The SetFit implementation reported a seed
standard deviation of exactly zero, which is not a plausible measurement of
stability but the signature of a defect in how seeds were handled in that arm.
Its mean is retained in Table 4.2 for completeness, since removing an arm after
seeing its result is precisely what the pre-registration forbids, but its
apparent perfect stability is not used as evidence of anything. BERT-NLI is
retained on its own registered grounds, that transfer-based classification can
reduce annotation requirements in small-data settings [@b51]; and the broader
finding that fine-tuned smaller models still outperform zero-shot generative
classifiers on text classification [@b52] is the reason trained discriminative
baselines were evaluated at all rather than assuming a prompted large language
model would serve as the verifier.

## 4.4 The circularity baseline

The ablation was accompanied by a set of reference points registered before the
frozen-probe number existed. Those reference points changed the interpretation
of the entire seven-arm experiment, and they are the most consequential result
in this chapter.

**Table 4.3. Circularity reference points on dev-82**

| Reference point | Macro-F1 | In development items | What it establishes |
|---|---:|---:|---|
| Majority-class prediction | 0.3926 | — | The floor for a metric that punishes ignoring the minority level |
| Length rule fitted on the training split | 0.6197 | — | A content-blind confound reference: predict Level 0 when a review has seven words or fewer, fitted at training macro-F1 0.6634 |
| **Frozen LaBSE encoder + L2 logistic head** | **0.9866** | 1 error on 82 | The generating representation asked to reproduce its own partition |
| Best fine-tuned arm (`banglabert`) | 0.9647 | 3 errors on 82 | The ceiling of the seven-arm ablation |
| Difference, best arm − frozen probe | −0.0219 | −1.79 items | The entire benefit of fine-tuning, in reviews |

The frozen probe is not a better model. It is the same geometry the label came
from. Section 3.6 established that the two-level partition was produced by
K-means on LaBSE sentence embeddings, so a linear classifier trained on those
same embeddings is the label's own generating geometry being asked to reproduce
itself, and it does so to within one development item of the best of seven
fine-tuned transformers. The registered verdict is `CIRCULARITY_CONFIRMED`.

Three consequences were fixed in the pre-registration and are honoured here. The
seven-arm table may support no claim about backbone quality; it is reported as a
demonstration that the label is linearly recoverable from the representation
that produced it. The `TIE` verdict stands but is re-explained: the arms are
indistinguishable because the task is near-saturated by construction, not
because these seven backbones are interchangeable in general or on any other
task. And Verifier-A is reconsidered from first principles, since a logistic
regression on frozen embeddings that matches a fine-tuned transformer makes the
fine-tuning's cost inside a generation loop indefensible.

The length rule deserves a second look, because it is the one reference point
that carries information beyond the circularity finding. A rule that consults
nothing but word count reaches 0.6197 against a majority floor of 0.3926, which
is consistent with the `LENGTH_CONFOUNDED` verdict recorded for the same cut in
Section 3.6. Length is a substantial component of the axis, and Chapter 3's
residual analysis is what establishes that it is not the whole of it. No verifier
in this chapter is credited with having separated the two.

## 4.5 What the circularity finding implies for the rest of the thesis

A finding that undermines the experiment that produced it is easy to state and
easy to leave unconnected. Its consequences run through four later parts of the
thesis, and setting them out here is what allows those parts to be read
correctly.

The first consequence bounds what any verifier score in this thesis can mean. A
Verifier-A or Verifier-B probability is an estimate of whether a piece of text
falls on the Level 1 side of a boundary that K-means drew in LaBSE space. It is
not a measure of audience response, not a detection of a persona, and not a
prediction of how viewers will react to a film. Every number in Chapter 6
inherits this limit, and the language of Chapter 6 is chosen to respect it.

The second consequence makes Verifier-A's design defensible rather than merely
convenient. At near-saturation there is nothing left for fine-tuning to buy, as
Table 4.3 quantifies at 1.79 development items; and a frozen encoder with a
linear head requires no gradient computation, no GPU inside the generation loop,
and seconds rather than minutes to fit. The cheap option was chosen because the
expensive one demonstrably purchased nothing, which is a different and stronger
argument than choosing it because it was cheap.

The third consequence is the one that turns a weakness into the thesis's central
experiment. If the in-loop gate is a linear function of a fixed embedding space,
then a generator optimised against that gate has an obvious and *cheap* route to
higher scores that does not involve writing better text: move the draft toward
whatever region of LaBSE space the boundary favours. Under this construction,
proxy divergence is the expected failure mode rather than a remote theoretical
worry, which is why Verifier-B is a different pretraining family trained on
different rows, and why the Goodhart diagnostic in Chapter 6 is a necessary
component of the design rather than a prudent extra. The circularity finding is
the reason inviolable rule 6 exists in the form it does.

The fourth consequence bounds Chapter 3 rather than Chapter 6. The stability
evidence reported there — prediction strength 0.8605 and bootstrap ARI 0.9399 ±
0.0290 at K = 2 — describes how reproducibly an algorithm redraws the same cut,
and Section 4.4 shows that the same cut is almost perfectly recoverable by a
linear probe on its originating embeddings. Both are statements about geometry.
Neither is evidence that the cut corresponds to natural categories, and the
thesis does not use them that way.

What the circularity finding does *not* imply is that the label is empty. That
question is settled elsewhere and settled independently: the comparative
intrusion study of Section 3.9 had human annotators recover the distinction at
0.780 and 0.840 against a chance rate of 0.25, on length-matched items, using no
verifier and no embedding. The axis is linear in LaBSE space and also
perceptible to people. The first fact constrains what the verifiers measure; the
second is why measuring it is worth doing.

## 4.6 Verifier-A: the in-loop scorer

Verifier-A is a frozen `sentence-transformers/LaBSE` encoder [@b3] with an
L2-regularised logistic head, trained on the 804 R1 rows. Nothing is fine-tuned,
which keeps the artifact inside inviolable rule 10's allowance of exactly two
logistic regressions. The head's hyperparameters are library defaults fixed in
the configuration file — inverse regularisation strength 1.0, L2 penalty, a
2,000-iteration limit, and L2-normalised embeddings — and none of them was
selected by looking at a development score. The encoder string is required by
configuration to match the one used to produce the partition, because if it did
not, this verifier would not be the artifact whose circularity Section 4.4
measured and that verdict would not transfer to it.

On dev-82 the artifact reaches macro-F1 0.9866, which is one error on 82 items.
That figure reproduces the frozen-probe reference point of Table 4.3 exactly,
for the same model on the same rows, and reproducing it is the purpose of
running the check rather than an incidental coincidence.

The single error is the classifier's least confident prediction. Before
temperature scaling, five development items fall in the 0.4-to-0.6 confidence
band and their empirical accuracy is 0.8, while every item above 0.6 confidence
is classified correctly. The one mistake Verifier-A makes on this slice is
therefore a case it was already unsure about, which is the benign form of an
error for a gate that will later be applied with a threshold.

What the number is not bears repeating in this specific place, because 0.9866 is
the kind of figure a reader will carry forward. It is label reproduction. The
literature that motivated the choice of a logistic head over a more expressive
one supports the artifact on exactly these grounds: logistic regression remains
appropriate for extremely low shot counts, high-dimensional representations, and
near-ceiling tasks [@b83], and this task is high-dimensional at 768 LaBSE
dimensions and near-ceiling at one error in 82.

The strength is also the risk, and the risk is specific rather than
philosophical. A verifier that is a linear function of LaBSE may be gameable by
a generator whose output is scored in that same space, without that generator
producing better writing in any sense a reader would recognise. That is the
failure RQ4 exists to detect, Verifier-B is the instrument that detects it, and
Section 4.9 is the wall that keeps the detection honest.

## 4.7 Verifier-B: the outcome scorer

Verifier-B is the BanglaBERT *recipe* — the same backbone [@b2], budget, and
seeds as the winning ablation arm — retrained from scratch on the 888 R2 rows.
The distinction between the recipe and the checkpoint is not pedantic. Every
checkpoint produced by the ablation was trained with role A, that is, on R1,
which is Verifier-A's data. Loading one of them as Verifier-B would have placed
both verifiers on the same rows, voided inviolable rule 6, and taken RQ4 with
it, since "the loop improved the text" and "the loop learned the shared
training distribution" would have become indistinguishable. The configuration
therefore declares its role explicitly and a test fails if that declaration ever
changes.

Verifier-B trains at a single learning rate of 2 × 10⁻⁵, the value the pipeline
specification names as the default, and it is never selected against a score.
The reason is a specific and recent finding about hyperparameter selection:
re-analysis of seven large HPO benchmark suites shows that selecting the
validation-optimal configuration generalises *worse* than the default in roughly
ten per cent of runs, and the conditions that aggravate this are small datasets,
holdout rather than cross-validation, binary classification, and accuracy-type
metrics [@b82]. All four describe this run exactly: 888 training rows, an 82-row
holdout, two classes, macro-F1. The recommendation in that work is repeated
cross-validation; not tuning at all is strictly stronger and was available, so it
was taken. The cost is named rather than hidden — Verifier-B may be slightly
weaker than a tuned Verifier-B would be — and it is accepted because a verifier
that is two points weaker is a reportable fact, whereas a verifier whose 82-row
holdout was reused for selection and then for reporting is not reportable at all,
and RQ4 depends on B's number being independent of everything A's number touched.

The persisted artifact is the seed-42 model, declared in the configuration before
any score existed, and explicitly not the best of five. An ensemble of all five
seeds was considered and rejected, because Verifier-A is a single model and an
ensembled B would make the RQ4 gap partly a gap between one model and five,
which no later analysis could separate out. Symmetry with A was judged worth more
than the ensemble's calibration benefit.

That artifact reaches dev macro-F1 0.9597, three errors on 82 items. Across the
five seeds the same recipe yields 0.9674 ± 0.0158, with individual runs spanning
0.9448 to 0.9866 — that is, one error to four errors on the same 82 rows. This
band is reported as sensitivity, never as a score distribution for model
comparison, and it is also the clearest available caution against reading any
small difference on this slice as a difference between models: an identical
recipe moves by three items across seeds.

The distribution of Verifier-B's errors differs from Verifier-A's in a way that
matters for the next section. Of its three errors, one is a low-confidence case
and two are made among the 81 items it scores above 0.8 confidence, where its
empirical accuracy is 0.9753 against a mean confidence of 0.9840. Verifier-A's
single error was its least confident prediction; Verifier-B's errors are mostly
confident ones. Its registered verdict is `COMPETENT_EVALUATOR`, and the
pre-committed reading of two verifiers both above roughly 0.90 macro-F1 is that
the cross-family wall is built from two competent evaluators — with no claim that
either is better than the other.

The ablation's BanglaBERT arm scored 0.9647, and that figure appears nowhere in
this thesis as a before-and-after pair with 0.9597. It is a different model
trained on different rows and is quoted only as context.

**Table 4.4. The two verifiers side by side**

| Property | Verifier-A | Verifier-B |
|---|---|---|
| Role | In-loop gate: scoring, acceptance, candidate selection | Outcome scoring only; never in the loop |
| Training partition | R1, *n* = 804 (481 / 323) | R2, *n* = 888 (531 / 357) |
| Pretraining family | LaBSE, multilingual sentence encoder | BanglaBERT, Bangla-native ELECTRA |
| Adaptation | Frozen encoder, L2 logistic head | Fine-tuned end to end |
| Tokenizer | LaBSE | BanglaBERT |
| Hyperparameters selected on a score | None; library defaults fixed in config | None; one learning rate taken from the specification |
| Evaluation slice | dev-82 (53 / 29) | dev-82 (53 / 29) |
| Dev macro-F1 | 0.9866 (1 error) | 0.9597 (3 errors), persisted seed-42 artifact |
| Five-seed sensitivity band | Not applicable; deterministic fit | 0.9674 ± 0.0158, range 0.9448–0.9866 |
| Registered verdict | `CALIBRATION_IMPROVED` (Section 4.8) | `COMPETENT_EVALUATOR`; `CALIBRATION_NOT_ESTABLISHED` |

## 4.8 Calibration of both verifiers

Calibration was registered as descriptive, and it was registered that way before
either verifier existed. The pipeline had described calibration as a hidden
contribution, with a ten-bin reliability diagram and before-and-after expected
calibration error. At 82 development rows a ten-bin diagram places roughly eight
items in a bin, the resulting error estimate is dominated by binning noise, and a
before-and-after improvement computed on 82 rows is not a measurement anyone can
rely on. Saying so in advance was judged cheaper than defending it later. What
survives is five bins rather than ten, with the bin count fixed before any
number was seen rather than chosen after seeing which count flattered the
result; expected calibration error reported with a bootstrap confidence interval
and never as a bare scalar; and the analysis labelled descriptive wherever it
appears.

Temperature scaling [@b53] is kept and deliberately not upgraded. More
expressive calibrators outperform simple ones when validation data is plentiful
and fail when it is scarce, while single-parameter scaling remains robust
[@b54]. The single-parameter method is the correct choice here *because* n is
small, not despite it.

Calibrating Verifier-A at all became mandatory through a correction that is worth
recording, since the chapter would otherwise present a calibration stage with no
stated motive. The original design defended Verifier-A partly as natively
calibrated, and that clause was withdrawn. An evaluation of nine classification
heads on frozen image, text, and audio encoders across 22,820 episodes finds
that logistic regression takes the best mean rank on accuracy while ranking
below k-nearest-neighbours and every in-context head on both calibration
metrics, with a top-1 expected calibration error of 0.069 against 0.037 and
0.031 for the two best-calibrated heads [@b83]. The correction is bounded rather
than sweeping: that evaluation's canonical grid is ten-class, this task is
binary, and the calibration gap narrows as the number of classes falls. What was
withdrawn is therefore the claim that Verifier-A needed no calibration, not a
new claim that it is miscalibrated. Which of the two holds is a question this
project's own data can answer, and Table 4.5 answers it.

**Table 4.5. Calibration before and after temperature scaling, five bins, fitted
on dev-82 in sample**

| Quantity | Verifier-A before | Verifier-A after | Verifier-B before | Verifier-B after |
|---|---:|---:|---:|---:|
| Fitted temperature | — | 0.1092 | — | 1.0995 |
| Expected calibration error | 0.1184 | 0.0054 | 0.0164 | 0.0100 |
| Brier score | 0.0306 | 0.0093 | 0.0278 | 0.0273 |
| Negative log-likelihood | 0.1515 | 0.0282 | 0.1101 | 0.1088 |
| ΔECE with bootstrap 95% CI | +0.1130 [+0.0743, +0.1349] | | +0.0065 [−0.0066, +0.0070] | |
| Registered verdict | `CALIBRATION_IMPROVED` | | `CALIBRATION_NOT_ESTABLISHED` | |

The two temperatures move in opposite directions, and the direction is
informative. Verifier-A's fitted temperature of 0.1092 is far below one, which
sharpens its probabilities, and the reliability bins in Table 4.6 explain why
that is the correction it needed: before scaling, the 70 items it scored above
0.8 confidence had a mean confidence of 0.9076 against an empirical accuracy of
1.0. Verifier-A was *under*confident rather than overconfident, which is the
opposite of the failure the word "miscalibrated" usually evokes, and sharpening
is the appropriate remedy. Verifier-B's temperature of 1.0995 is slightly above
one, a mild softening, and its effect on every metric is smaller than the
bootstrap interval around it.

**Table 4.6. Reliability bins on dev-82, five bins. Empty bins are omitted**

| Verifier | Stage | Confidence band | *n* | Mean confidence | Empirical accuracy |
|---|---|---|---:|---:|---:|
| A | before | [0.4, 0.6) | 5 | 0.5435 | 0.800 |
| A | before | [0.6, 0.8) | 7 | 0.7206 | 1.000 |
| A | before | [0.8, 1.0) | 70 | 0.9076 | 1.000 |
| A | after | [0.6, 0.8) | 3 | 0.7500 | 0.667 |
| A | after | [0.8, 1.0) | 79 | 0.9976 | 1.000 |
| B | before | [0.6, 0.8) | 1 | 0.6430 | 0.000 |
| B | before | [0.8, 1.0) | 81 | 0.9840 | 0.975 |
| B | after | [0.6, 0.8) | 1 | 0.6307 | 0.000 |
| B | after | [0.8, 1.0) | 81 | 0.9776 | 0.975 |

For Verifier-B the pre-committed null statement fires, and it fires in the words
that were registered for it: calibration could not be established at this sample
size. That is not a failed step. It is the step returning what its sample can
support, and it is why Verifier-B's outputs are treated throughout Chapter 6 as
fixed scorer outputs rather than as probabilities claimed to be well calibrated.

Both temperatures were fitted on dev-82 and are reported as fitted there. At 82
rows there is no second slice to hold out, and an in-sample temperature reported
as in-sample is honest where a nominally held-out one would be fictional.

Figure 4.2, a reliability diagram showing both verifiers before and after
scaling, was planned and is **deferred**. Tables 4.5 and 4.6 carry its content —
the bin populations, mean confidences, and empirical accuracies it would have
plotted are given numerically above — so no claim in this chapter depends on a
figure that does not yet exist.

One forward consequence follows for Chapter 5. The acceptance threshold τ stands
on Verifier-A's confidence, and since the calibration behind that confidence is
descriptive and fitted in sample, τ's sensitivity is reported there as a curve
rather than as a point, and the sanity check of the final τ against Verifier-B
scores is treated as mandatory rather than advisory.

## 4.9 The executable isolation wall

The separation between the two verifiers is the load-bearing structure of RQ4,
and a separation that depends on the researcher remembering it is not a
separation. This section states what the wall is made of and how each part of it
is enforced.

At the data level, the two training sets are disjoint by construction: R1 and R2
are halves of the frozen split, neither contains any Gold-300 row, and a test
asserts that no Verifier-B training identifier intersects R1. The shared
development slice does not breach this. Dev-82 is a subset of R1 that is held out
of Verifier-A's 804 rows, and it is disjoint from R2 by the split's own contract,
so neither verifier has been trained on any of the 82 rows either verifier is
scored on.

That the slice is *shared* is deliberate, and the reason is specific to RQ4.
The Goodhart diagnostic measures the gap between A-scores and B-scores. If A and
B were measured on different items, that gap would confound a difference between
models with a difference between items, and no subsequent analysis could
separate the two. Head-to-head measurement on identical items is the only
configuration in which the gap means what RQ4 says it means. The widening of the
development slice's registered use, from threshold sweeping alone to threshold
sweeping and verifier evaluation, is logged as a deviation rather than absorbed
silently.

At the code level the wall is executable. An abstract-syntax-tree scan walks
every Python file in the agent package and inspects every import statement,
including imports inside function bodies, where a late import would hide from
anyone reading only the top of a file; it fails if any name matching Verifier-B's
artifact or training module is reachable. A companion test proves that scanner
can actually see such an import, on the principle that a guard whose failure
branch is unreachable certifies nothing — a lesson taken from an earlier gate in
this project whose null verdict turned out to be unreachable by construction.
Around those two sit further checks: source-level assertions that the Critic
module, the development-plot runner, and the hybrid-weight fitting module never
reference Verifier-B; an import scan of the main generation runner; a preflight
assertion that the generation configuration reports Verifier-B as not loaded; a
checkpoint audit that rejects any generation record carrying a Verifier-B score;
an identifier-intersection test over Verifier-B's training rows and R1; a test
that its configuration still declares role B; and two exclusion checks on the
demonstration configuration and its startup path. Seventeen tests across ten
files in the suite name Verifier-B explicitly, and the ones listed here are
what hold inviolable rule 6 in place.

**Table 4.7. The isolation wall and its enforcement**

| What is separated | How it is guaranteed | Where it is enforced |
|---|---|---|
| Training rows | R1 and R2 are disjoint halves of the frozen split | Identifier-intersection test over Verifier-B's training set and R1 |
| Evaluation rows | dev-82 ⊂ R1, held out of A's 804, disjoint from R2 by contract | Split contract; asserted row counts in both verifier configs |
| Gold-300 | Excluded from both verifiers, from selection, and from calibration | Split contract; per-step assertions that no Gold row is read |
| Model family | Frozen LaBSE against fine-tuned BanglaBERT | Config strings tested against the registered recipe |
| Checkpoints | Verifier-B is retrained, never loaded from an ablation checkpoint | Role declaration test; the ablation runs role A only |
| Loop privilege | No Verifier-B import reachable from the agent package | AST scan of every import in the package, plus a failure-branch proof |
| Generation records | No generation checkpoint may carry a Verifier-B score | Checkpoint audit test |

No claim is made that either verifier is better than the other, and the reason is
arithmetic rather than modesty. One development item is 0.0122 macro-F1, the
expected gap between the two was around 1.8 items, and the prohibition was
pre-committed before either model was trained. The comparison this slice
supports is that both are competent on the same items, which is all the
cross-family wall requires. RQ4's gap is measured on generated text in Chapter
6, not here.

## 4.10 Chapter summary

Verifier development produced two competent and deliberately unequal
instruments. A frozen LaBSE encoder with a logistic head serves as the in-loop
gate, reaching 0.9866 macro-F1 on the shared development slice at one error in
82, with no hyperparameter selected against a score and no gradient computation
inside the generation loop. A BanglaBERT recipe retrained on the disjoint R2
half serves as the outcome scorer, reaching 0.9597 with the pre-declared seed-42
artifact, and it is walled out of the loop by an executable set of tests rather
than by convention.

The chapter's most consequential result is not a winning backbone but the
demonstration that no backbone wins. A seven-arm ablation spanning
Bangla-native, Indic, multilingual, contrastive, and NLI-transfer designs
returned `TIE` across all 21 corrected comparisons, and a frozen linear probe on
the encoder that generated the label matched the best of those seven to within
1.79 development items. The label is very nearly linear in its originating
representation. This chapter reports that as `CIRCULARITY_CONFIRMED`, declines
to extract a backbone recommendation from a table whose full range is under three
reviews, and converts the finding into the argument for the Goodhart stress test
rather than leaving it as a caveat.

Two limits are carried forward explicitly. Calibration is descriptive
throughout: Verifier-A's improvement is real on its own slice but fitted in
sample, and Verifier-B's registered verdict is that calibration could not be
established at this sample size. And the specification asked for four verifiers,
one pair per language; two were delivered. The English pair is named as
outstanding rather than counted as complete, and Chapter 8 places it in future
work.

Chapter 5 takes these two instruments and builds the generation system around
them: what the in-loop gate is allowed to do with a score, how the threshold it
compares against was chosen, and which parts of the system make no model call
at all.
