# Chapter 4 — Verifier Development

## 4.1 Role of the two verifiers

The framework uses two classifiers with intentionally different privileges.
Verifier-A is the in-loop gate: it scores drafts, determines acceptance at the
frozen threshold, and selects among blind resamples. Verifier-B is an
outcome-only evaluator. It never enters retrieval, prompting, feedback,
selection, or regeneration. Both are evaluated on the same 82-row development
slice, but their training data are disjoint.

The classifiers reproduce the operational K=2 axis label. Their scores are not
independent human-validity estimates. Human validity comes from the comparative
study in Chapter 3 and the generated-output evaluation in Chapter 6.

## 4.2 Backbone ablation

Seven verifier recipes were evaluated on R1 training data (n=804; 481 Level 0,
323 Level 1) and dev-82 (53/29) over five seeds. The registered decision rule was
paired bootstrap with Benjamini–Hochberg correction; seed standard deviations
were descriptive. Mean macro-F1 ranged from 0.9298 for BERT-NLI to 0.9647 for
BanglaBERT, but none of the 21 pairwise comparisons was significant after
correction; the smallest unadjusted p-value was 0.096. The registered verdict is
`TIE`.

BanglaBERT was selected only through the preregistered non-performance tie-break
(smallest parameter count, then BanglaBERT). The study does not claim that
BanglaBERT is empirically superior to the other backbones. A SetFit implementation
defect also made its nominal zero seed variance uninterpretable; that arm is not
used as stability evidence.

## 4.3 Circularity baseline

A necessary baseline changed the interpretation of the ablation. Majority-class
macro-F1 is 0.3926 and a fitted length rule reaches 0.6197. A frozen LaBSE
encoder with default L2 logistic regression reaches 0.9866—one error on 82
items—while the best fine-tuned arm reaches 0.9647. The 0.0219 difference is
about 1.8 development items.

This is `CIRCULARITY_CONFIRMED`: K=2 was created by K-means in LaBSE space, so a
linear probe on the same representation recovers the generating geometry. The
seven-arm experiment demonstrates near-saturated label reproduction, not general
backbone quality. Fine-tuning does not earn its added cost for the in-loop role.

## 4.4 Verifier-A

Verifier-A is frozen `sentence-transformers/LaBSE` plus an L2 logistic head,
trained on 804 R1 rows. It reproduces macro-F1 0.9866 on dev-82. No
hyperparameter is selected from the outcome: C, penalty, and iteration limit are
fixed library defaults in the config.

Temperature scaling on dev-82 yields T=0.1092. Descriptively, ECE falls from
0.1184 to 0.0054, Brier score from 0.0306 to 0.0093, and NLL from 0.1515 to
0.0282. Bootstrap delta-ECE is +0.1130 with 95% CI [+0.0743, +0.1349], giving
`CALIBRATION_IMPROVED`. Because temperature is fitted and described on the same
small slice, this is not a large independent calibration study.

Verifier-A is cheap and accurate at reproducing the label, but this strength is
also its risk: the generator may learn cues that exploit a linear boundary in
the same embedding space. RQ5 is designed to expose that failure.

## 4.5 Verifier-B

Verifier-B is a fine-tuned `csebuetnlp/banglabert` model trained on 888 R2 rows
(531/357). It uses a BanglaBERT/ELECTRA-family representation and tokenizer,
unlike multilingual frozen LaBSE. The persisted seed-42 artifact scores dev
macro-F1 0.9597; the five-seed sensitivity band is 0.9674 ± 0.0158. The artifact
is selected by the global seed, not best-of-five.

Temperature scaling gives T=1.0995. ECE changes from 0.0164 to 0.0100, but the
bootstrap delta-ECE interval is [-0.0066, +0.0070]. The preregistered conclusion
is `CALIBRATION_NOT_ESTABLISHED`. Verifier-B probabilities are therefore fixed
scorer outputs, not claimed perfectly calibrated probabilities.

## 4.6 Isolation wall

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

## 4.7 Chapter summary

Verifier development produces two competent but deliberately unequal tools. A
frozen LaBSE probe is appropriate for cheap in-loop label reproduction; a
fine-tuned BanglaBERT trained on disjoint data supplies a methodologically
separate outcome view. The ablation's most important result is not a winning
backbone but the discovery that the label is nearly linear in its originating
representation. This circularity is disclosed and converted into the central
Goodhart stress test rather than hidden.

