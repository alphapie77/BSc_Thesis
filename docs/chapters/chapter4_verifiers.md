# Chapter 4 — Verifier Development and Validation

## 4.1 Design rationale and verifier roles

The framework uses two classifiers with intentionally different privileges.
Verifier-A is the in-loop gate: it scores drafts, determines acceptance at the
frozen threshold, and selects among blind resamples. Verifier-B is an
outcome-only evaluator. It never enters retrieval, prompting, feedback,
selection, or regeneration. Both are evaluated on the same 82-row development
slice, but their training data are disjoint.

The classifiers reproduce the operational K=2 axis label. Their scores are not
independent human-validity estimates. Human validity comes from the comparative
study in Chapter 3 and the generated-output evaluation in Chapter 6.

The separation addresses two different needs. Generation requires a cheap
scorer that can be called repeatedly and locally; evaluation requires a scorer
that has not participated in those calls. If one model performed both roles, a
higher final score would be ambiguous because the generator could learn that
same model's idiosyncratic boundary. The dual-verifier design does not make
either classifier ground truth. It creates a controlled disagreement that can
be inspected after generation.

![Dual-verifier data and privilege isolation](../figures/dual_verifier_isolation.svg)

*Figure 4.1. Data and privilege isolation for the two verifiers. Gold-300 was
used only by the failed first human-rating instrument (598/600 ratings;
ordinal alpha=0.497; Gate 2 not run), never for fitting or retrieval. R1
supplies retrieval and the in-loop Verifier-A; disjoint R2 supplies outcome-only
Verifier-B. The dashed wall emphasizes that Verifier-B cannot influence
generation, selection or retry.*

## 4.2 Training and evaluation protocol

Verifier development uses only Region-A reviews carrying the frozen two-level
label. Verifier-A candidates train on 804 R1 rows, while Verifier-B trains on
888 disjoint R2 rows. Both are measured on the same labelled 82-row development
slice (53 Level 0 and 29 Level 1). This common slice makes development scores
comparable, but it is not a fresh test set: it also supports model-development
decisions and temperature scaling. The reported development metrics are
therefore descriptive evidence rather than population-level generalization
estimates.

Macro-F1 is the principal label-reproduction metric because the levels are
imbalanced. Fine-tuned candidates are run over seeds 42–46; variation over
these seeds is sensitivity evidence, not five independent experiments. This
guard is consistent with evidence that few repetitions and random variation can
distort neural-model comparisons [@b46; @b47] and with theoretical analysis of
fine-tuning stability [@b48]. The
backbone decision uses paired predictions and a 10,000-resample paired
bootstrap, with Benjamini–Hochberg correction over the 21 registered pairwise
comparisons [@b49; @b50]. If no model significantly beats every alternative,
the preregistered non-performance tie-break applies. Gold-300 is excluded from
training, selection, calibration, and the backbone comparison.

## 4.3 Backbone ablation

Seven verifier recipes were evaluated on R1 training data (n=804; 481 Level 0,
323 Level 1) and dev-82 (53/29) over five seeds. The registered decision rule was
paired bootstrap significance testing in NLP [@b49] with Benjamini–Hochberg
correction [@b50]; seed standard deviations
were descriptive. Mean macro-F1 ranged from 0.9298 for BERT-NLI to 0.9647 for
BanglaBERT, but none of the 21 pairwise comparisons was significant after
correction; the smallest unadjusted p-value was 0.096. The registered verdict is
`TIE`.

BanglaBERT was selected only through the preregistered non-performance tie-break
(smallest parameter count, then BanglaBERT). The study does not claim that
BanglaBERT is empirically superior to the other backbones. A SetFit implementation
defect also made its nominal zero seed variance uninterpretable; that arm is not
used as stability evidence.

BERT-NLI is retained because transfer-based classification can reduce annotation
requirements in small-data settings [@b51]. The wider literature also reports
that fine-tuned smaller models can outperform zero-shot generative classifiers
[@b52]; neither result determines the winner here, but both justify evaluating
trained discriminative baselines rather than assuming an LLM judge is enough.

**Table 4.1. Verifier-label reproduction and circularity baselines on dev-82**

| Recipe/reference point | Mean macro-F1 | SD across five seeds | Standing |
|---|---:|---:|---|
| BanglaBERT | 0.9647 | 0.0209 | Tied; selected only by non-performance tie-break |
| SetFit–LaBSE | 0.9590 | 0.0000 | Defective seed handling; SD is not stability evidence |
| IndicBERTv2 | 0.9560 | 0.0156 | No significant difference after BH correction |
| MuRIL | 0.9421 | 0.0391 | No significant difference after BH correction |
| mBERT | 0.9402 | 0.0125 | No significant difference after BH correction |
| XLM-R | 0.9360 | 0.0219 | No significant difference after BH correction |
| BERT-NLI | 0.9298 | 0.0165 | No significant difference after BH correction |
| Majority-class baseline | 0.3926 | — | Cheap reference |
| Length rule fitted on train | 0.6197 | — | Content-blind confound reference |
| Frozen LaBSE + L2 logistic regression | **0.9866** | — | One dev error; reveals construction circularity |

The learning rate of each fine-tuned arm was selected on the same development
set, so its mean is descriptive rather than a clean held-out estimate. None of
the 21 registered pairwise comparisons was significant after correction; the
smallest unadjusted p-value was 0.096. The table supports label recoverability
and `CIRCULARITY_CONFIRMED`, not backbone superiority.

## 4.4 Circularity baseline and revised interpretation

A necessary baseline changed the interpretation of the ablation. Majority-class
macro-F1 is 0.3926 and a fitted length rule reaches 0.6197. A frozen LaBSE [@b3]
encoder with default L2 logistic regression reaches 0.9866—one error on 82
items—while the best fine-tuned arm reaches 0.9647. The 0.0219 difference is
about 1.8 development items.

This is `CIRCULARITY_CONFIRMED`: K=2 was created by K-means in LaBSE space, so a
linear probe on the same representation recovers the generating geometry. The
seven-arm experiment demonstrates near-saturated label reproduction, not general
backbone quality. Fine-tuning does not earn its added cost for the in-loop role.

## 4.5 Verifier-A: the in-loop scorer

Verifier-A is frozen `sentence-transformers/LaBSE` plus an L2 logistic head,
trained on 804 R1 rows. It reproduces macro-F1 0.9866 on dev-82. No
hyperparameter is selected from the outcome: C, penalty, and iteration limit are
fixed library defaults in the config.

Temperature scaling [@b53] on dev-82 yields T=0.1092. Descriptively, expected
calibration error (ECE) falls from
0.1184 to 0.0054, Brier score from 0.0306 to 0.0093, and negative log-likelihood
(NLL) from 0.1515 to
0.0282. Bootstrap delta-ECE is +0.1130 with a 95% confidence interval (CI) of
[+0.0743, +0.1349], giving
`CALIBRATION_IMPROVED`. Because temperature is fitted and described on the same
small slice, this is not a large independent calibration study. More expressive
calibrators can be unstable under data scarcity, which supports retaining the
simple registered temperature-scaling analysis rather than adding a post-hoc
calibrator [@b54].

Verifier-A is cheap and accurate at reproducing the label, but this strength is
also its risk: the generator may learn cues that exploit a linear boundary in
the same embedding space. RQ4 is designed to expose that failure.

## 4.6 Verifier-B: the outcome scorer

Verifier-B is a fine-tuned `csebuetnlp/banglabert` model [@b2] trained on 888 R2 rows
(531/357). It uses a BanglaBERT/ELECTRA-family representation and tokenizer,
unlike multilingual frozen LaBSE. The persisted seed-42 artifact scores dev
macro-F1 0.9597; the five-seed sensitivity band is 0.9674 ± 0.0158. The artifact
is selected by the global seed, not best-of-five.

Temperature scaling gives T=1.0995. ECE changes from 0.0164 to 0.0100, but the
bootstrap delta-ECE interval is [-0.0066, +0.0070]. The preregistered conclusion
is `CALIBRATION_NOT_ESTABLISHED`. Verifier-B probabilities are therefore fixed
scorer outputs, not claimed perfectly calibrated probabilities.

## 4.7 Executable isolation wall

| Property | Verifier-A | Verifier-B |
|---|---|---|
| Training source | R1, n=804 | R2, n=888 |
| Encoder | frozen LaBSE | fine-tuned BanglaBERT |
| Adaptation | logistic head | end-to-end |
| Function | gating/selection | outcome scoring only |

The training sets do not overlap, neither contains Gold-300, and both use the
same dev-82 only for evaluation/calibration. An AST-based test scans the agent
package and fails if any Verifier-B import becomes reachable. A companion test
proves the guard's failure branch. The wall is therefore executable rather than
dependent on researcher memory.

No claim is made that A is better than B. One dev item corresponds to roughly
0.0122 macro-F1, so the observed gap is too small for that interpretation and
was preregistered as such.

## 4.8 Chapter summary

Verifier development produces two competent but deliberately unequal tools. A
frozen LaBSE probe is appropriate for cheap in-loop label reproduction; a
fine-tuned BanglaBERT trained on disjoint data supplies a methodologically
separate outcome view. The ablation's most important result is not a winning
backbone but the discovery that the label is nearly linear in its originating
representation. This circularity is disclosed and converted into the central
Goodhart stress test rather than hidden.
