# Intrusion sheets — RQ1-H, attempt 2

Generated 2026-08-08T12:08:37.179279+00:00 · commit `68e402f4d79a1ced4bcc2ada25dc4db55dd78610-dirty` · seed 42

## For annotators — the whole instruction

**`intrusion_<you>.csv`** — each row has four reviews (A, B, C, D). Three are
alike and one is the odd one out. Put **A, B, C or D** in the `answer` column.

**`pairwise_<you>.csv`** — each row has two reviews. Put **A** or **B** in
`answer` for whichever goes into **more specific detail about the film**.

That is the entire task. There is no scale, no rubric and no guideline to read.
Work alone; do not discuss any item with the other annotator.

## For the researcher

- `intrusion_key.csv` / `intrusion_key_pairwise.csv` hold the answers.
  **Never send these.**
- 50 sets, 40 pairs. Every set is length-matched to within
  2 words, so **length cannot be the cue** —
  RQ1-D's condition is met by construction, not by measurement.
- Items exclude G-300, which both annotators saw in attempt 1.
- Chance is **0.25** for intrusion and **0.50** for pairwise. Bands are in
  `docs/protocol.md`, RQ1-H.
