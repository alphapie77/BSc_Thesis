# Appendix A — Reproducibility and execution contract

## A.1 Repository-wide invariants

This appendix records the execution conditions required to reproduce or audit
the reported computational results. It complements the methodological account
in Chapters 3–6 by binding each stage to its frozen inputs, configuration and
canonical evidence.

- Global seed: 42 through `src/common/seed.py`.
- Frozen review split: Gold-300=300, R1=2,162, R2=2,163. The 200-row
  development subset is contained within R1 rather than forming a fourth
  disjoint partition.
- Gold-300 is evaluation-only; RAG uses R1 only; Verifier-B never enters
  generation.
- Main generation replicates: 42, 43 and 44 as paired sensitivity blocks.
- Every canonical result is config-addressed and carries runtime provenance.
- The frozen 5,400-generation surface is not regenerated for reporting.

## A.2 Data and artifact lineage

**Table A.1. Frozen data and artifact lineage**

| Stage | Input | Canonical output/evidence |
|---|---|---|
| Raw audit | immutable 5,000-row workbook | `results/s0_data_xray.md` |
| Cleaning | raw workbook | `data/cleaned/bn_clean.csv`; `s1_cleaning_log.json` |
| Split freeze | 4,625 near-duplicate-controlled rows | `data/splits/split_map_v1.json` |
| Axis study | Region-A/R1 geometry and human instruments | S2 reports; G-300 and intrusion reports |
| Verifier-A | 804 R1 rows | frozen LaBSE + L2 logistic artifact; S3c report |
| Verifier-B | 888 R2 rows | fine-tuned BanglaBERT artifact; S3d report |
| RAG index | 886 Region-A R1 rows: 804 Verifier-A training rows plus 82 development rows | R1-only index manifest, 534/352 by level |
| Main generation | 90 eval plots × 2 levels × 10 conditions × 3 seeds | 5,400-case sealed archive |
| Outcome scoring | sealed cases + Verifier-B | 5,400 score rows and score manifest |
| Post-run analysis | sealed cases/scores | master, paired, Goodhart, length and realism artifacts |
| Human evaluation | frozen 100-item balanced subset | 300 judgments and registered report |

## A.3 Runtime environments

**Table A.2. Runtime evidence associated with each computational stage**

| Work | Environment evidence | Principal hardware/standing |
|---|---|---|
| Local preprocessing and document scoring | `results/env_snapshot.json` | Windows local environment |
| S2 clustering | `results/env_snapshot_s2_kaggle.json` | Kaggle Tesla T4; host-native scientific stack |
| S3 verifier training | `results/env_snapshot_s3_kaggle.json` | Kaggle Tesla T4 |
| S4 development generation/scoring | `env_snapshot_s4*` files | Kaggle Tesla T4; producing snapshot selected per result |
| S5 final generation | `results/env_snapshot_s5_bn_kaggle.json` | Kaggle Tesla T4; transformers 5.15.0, scikit-learn 1.9.0 |
| S5 human scoring | provenance inside human report | Windows local environment |

Environment snapshots must be cited by the result they produced; the local
lock file is not retroactively treated as the Kaggle environment.

## A.4 Main generation configuration

- Writer: `google/gemma-3-12b-it`, NF4.
- Sampling: `max_new_tokens=80`, temperature 0.8, top-p 0.9.
- Uniform output instruction: at most 20 words at either requested level.
- Verifier-A threshold: 0.4384071; maximum three Writer attempts.
- Symbolic threshold: 0.18166513482099075; maximum three attempts.
- Hosted judge: `gemma-4-26b-a4b-it`, structured PASS/FAIL, seed 42,
  high thinking, maximum 512 output tokens and maximum three judgments.
- Blind resampling: maximum five candidates; Verifier-A selects the best prefix
  inside the realized neural-plus-symbolic token budget.

## A.5 Statistical contract

- Primary outcome: Verifier-B target probability.
- Primary family: nine paired condition-versus-zero-shot comparisons.
- Pairing key: plot × target level × replicate seed.
- Uncertainty: 10,000-resample paired bootstrap, 95% interval.
- Multiplicity: Benjamini–Hochberg across the frozen family.
- Binary paired check: McNemar test.
- The registered inferential family contains only the nine
  condition-versus-zero-shot comparisons. The later neural-plus-symbolic versus
  neural-only comparison is reported separately as exploratory and is not added
  to that confirmatory family.

## A.6 Compute-reporting boundary

Exact consolidated GPU wall-clock hours were not registered as a canonical
result and are therefore not reported. The available compute record consists of
hardware identity, logical model-call counts, token counts, runtime snapshots
and producing commits. These quantities permit cost comparison within the
experiment but do not constitute a retrospective estimate of energy use or
total GPU hours.

## A.7 Control guarantees of the generation loop and the tests that enforce them

Each guarantee stated beneath Algorithm 5.1 is asserted by at least one named
test. Twenty tests across the three files below cover the controller, its state
object and retrieval anchoring.

**Table A.3. Executable tests enforcing the generation-loop control guarantees**

| Guarantee (Chapter 5, §5.3) | Enforcing test | File |
|---|---|---|
| One Writer call per attempt; no Reflector call at the ceiling | `test_pass_on_first_attempt_costs_one_call_and_no_reflection`; `test_three_failures_give_up_and_make_exactly_two_reflector_calls` | `tests/test_s4_graph.py` |
| Forced-three costs three Writer, two Reflector, five logical calls | `test_forced_three_continues_after_pass_without_calling_it_gave_up` | `tests/test_s4_graph.py` |
| The plot is never displaced from the retrieval query | `test_retry_query_keeps_the_original_as_a_prefix`; `test_feedback_augments_rather_than_replaces` | `tests/test_s4_researcher.py` |
| Query revision fires only below the registered overlap trigger | `test_the_routing_trigger_is_the_spec_value_not_a_new_constant`; `test_overlap_arithmetic`; `test_overlap_is_none_on_the_first_attempt` | `tests/test_s4_researcher.py` |
| Snapshots are independent and precede mutation | `test_trace_entries_are_independent_snapshots`; `test_advance_clears_scores_so_a_stale_pass_cannot_survive`; `test_trace_holds_every_earlier_attempt` | `tests/test_s4_state.py`; `tests/test_s4_graph.py` |
| Ties resolve to the earliest attempt | `test_ties_break_toward_the_earliest_attempt`; `test_best_of_three_picks_the_highest_gate_score` | `tests/test_s4_state.py` |
| Retry prompts differ from the first attempt | `test_the_retry_prompt_contains_the_previous_draft_and_the_feedback` | `tests/test_s4_graph.py` |
| The attempt cap cannot be exceeded | `test_advance_refuses_past_the_cap` | `tests/test_s4_state.py` |
| The loop state carries no `w` and no `τ` default | `test_state_carries_no_w_and_no_tau` | `tests/test_s4_state.py` |

The last row is a design constraint rather than a behavioural one: the state
object deliberately holds neither a hybrid weight nor a default threshold, so
neither can be silently supplied by the controller instead of by a registered
configuration. Verifier-B's exclusion from the loop is enforced separately by the
package-wide static scan reported in Chapter 4, §4.8.
