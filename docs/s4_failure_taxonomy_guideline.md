# S4.6 failure-taxonomy coding guideline

## Purpose and coding unit

Code the **emitted draft** for each of the eight cases that failed Verifier-A
on all three attempts at the selected tau. The system emits the highest-A draft
after giving up, which is not necessarily attempt 3; auditing attempt 3 alone
would classify text the system never ships.

Use the synopsis and target specificity level as context. The three attempts
are included only to explain the trajectory. Do not use model scores, feedback,
or another coder's sheet. Each category is binary (`1` present, `0` absent),
and multiple categories may apply.

## Registered categories

- `wrong_sentiment`: mark `1` only for a clear sentiment error in the comment
  itself (for example, internally contradictory valence). The S4 task has no
  target sentiment, so disagreement with an imagined desired polarity is not
  an error.
- `too_short`: mark `1` when the emitted text is not a semantically complete,
  usable audience comment. There is no word-count cutoff; short but complete is
  not an error.
- `off_topic`: mark `1` when a material claim is unrelated to or unsupported by
  the supplied synopsis. A general reaction can still be on-topic.
- `template_repeat`: mark `1` when the draft substantially repeats boilerplate
  found in another emitted draft in this eight-case packet. Shared ordinary
  words are not enough.
- `register_or_honorific`: mark `1` for clearly unsuitable Bangla register or
  an honorific/address-form error. Do not turn personal style preference into
  an error.
- `other`: mark `1` for any material failure not captured above, fill
  `other_label`, and explain it briefly in `coder_notes`. The label is reported
  as post hoc; do not squeeze an observed error into a registered category.

## Independent coding and reconciliation

1. Generate the blank packet with
   `python src/eval/build_s4_failure_sheet.py`.
2. Make two copies, one per independently chosen coder. Coders must not discuss
   cases or inspect each other's labels before both sheets are frozen.
3. Save the frozen sheets at the two paths in
   `configs/s4_failure_taxonomy.yaml`, then run
   `python src/eval/score_s4_failure_taxonomy.py`. This produces category-wise
   and micro agreement plus a disagreement sheet.
4. Reconcile only the listed disagreements, recording the resolution and a
   short reason. Agreement is always reported **before** reconciliation.

The normative request was 50 cases, but only eight three-time gate failures
exist. All eight are coded; no case is duplicated, no threshold is changed, and
no non-failure is substituted.
