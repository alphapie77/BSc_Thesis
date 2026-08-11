# Handoff — Phase 4, second session (paste this into the new chat)

---

You are continuing my BSc thesis (targeting a Q1 journal). The repo is the
folder you have open. **Do not start work until you have read, in this order:**

1. `CLAUDE.md` — the inviolable rules and how to behave
2. `docs/STATUS.md` — where we are, verified facts, open decisions
3. `docs/research_pipeline_en.md` §4 — the normative spec
4. `docs/protocol.md` — read the **2026-08-11 and 2026-08-12** deviation rows.
   There are ~25 of them and several overturn things stated earlier the same day.
5. `src/agents/README.md` — one page, the whole Phase 4 system

⚠️ **Check `results/` and `artifacts/` on disk before believing STATUS.** STATUS
contradicted itself once on 2026-08-11 and told a fresh session Phase 4 was
blocked when it was not. Disk cannot go stale.

## Where things actually are

**Phase 4 is BUILT.** All four §4.2 components exist with 79 passing tests:
`state.py`, `researcher.py`, `writer.py` (API), `local_writer.py` (own GPU),
`critic.py`, `reflector.py`, `graph.py`, one prompt renderer in `prompts.py`.
The R1-only RAG index is built (886 rows, digest `85fc2d7d…`). Both verifiers
are trained and committed.

**Nothing has been generated yet that counts.** 27 Groq generations exist
(`results/pilot_s4_generations.jsonl`) — they are on a **different provider and
different models** from the current plan and may not be merged with anything new.
They are kept because they are what measured Llama's Bangla tokenizer fertility.

## The task

**Run the pilot on Kaggle, then §4.5's τ sweep.**

`notebooks/s4_pilot_kaggle.ipynb` is the runner. `configs/s4_pilot_local.yaml`
is the config. Sabbir will run it; you read the output and record it.

## Settled on 2026-08-12 — do not re-open

- **Generation runs on our own GPU (Kaggle T4), not a hosted API.** The cause was
  budget and is recorded as budget. But it also *narrows* the reproducibility
  concession `2601.17768` forced on us: locally we choose the batch and set the
  seed. **Batch size is provenance, not a knob.**
- **Arms: `google/gemma-3-12b-it` (general) vs `md-nishat-008/TigerLLM-9B-it`
  (Bangla-adapted).** Same base, same size — **one variable**. The struck pair
  (`llama-3.3-70b` vs `gpt-oss-20b`) differed in three ways at once.
- **1B was tried and failed** — 1 of 3 usable, one degenerate. 9B: 3 of 3.
  Hand-read, n=3, **NOT A RESULT**, but it is why the size moved.
- **arXiv 2503.10995 (TigerLLM) does not describe these weights.** It says
  LLaMA-3.2 / Gemma-2; the uploads are Gemma-3, and the "9B" is 12.19B. No claim
  may rest on its benchmark table.
- **Tokenizer fertility is per-tokenizer**: 0.93 chars/token on Llama, **3.71 on
  Gemma-3**. Every budget number computed on 2026-08-11 was Llama-specific.
- **`w` and τ still have no values.** `w` is fitted on the 30 dev-plots'
  generations as a sensitivity curve; τ\* is decision 19's argmax. No defaults
  anywhere, and the Critic refuses to run without both.
- **Multi-accounting to evade free-tier limits was declined twice** (Groq,
  Kaggle). Not to be revisited: the appendix must state how generations were
  produced.
- **`enable_f1` stays false** pending the rule-7 amendment.

## Two things recorded before they can become convenient

- The 9B's comments read **more literary than the corpus** — the naturalness gap
  `2410.15956` names; §5.4 is the instrument.
- Three samples **all opened with the same phrase** — low diversity at temp 0.8.

Both are observations, not measurements. Do not quietly drop either.

## How I need you to work

- **Search the literature BEFORE every design decision**, not after. Consensus
  quota is exhausted until 2026-09-01, so use alphaXiv and **say which index**.
  Report what the search changed; if it changed nothing, say that too.
- **One search call is not "the search."** Re-wording found a full field where
  one call had reported "thin" — that error is logged.
- 🔴 **Do not trust blog posts about free tiers or model availability.** Three
  separate claims failed against vendor documentation on 2026-08-11/12. Read the
  primary source. Model IDs come from the live catalogue, never from memory and
  **never from a search summary**.
- **Read the rendered artifact, not just the tests.** Three bugs were caught by
  printing a prompt and reading it, after the tests were already green.
- **Every decision constant must carry a reason.** `python
  src/common/check_constants.py` must pass.
- **Do not invent numbers or reasoning.** If a reason is mine, ask me.
- **Negative results are results.** Pre-commit outcomes before running.
- **Definition of Done**: `step_close.py --step … `, fill the TODOs by hand,
  update `related_work.md` + `references.bib` + `STATUS.md`, add a deviations row,
  and `step_close.py --check` must exit 0. Commit code + results + notebook
  together.
- Teach me the tricky parts in Bangla when it helps.

## Open, and mine

| # | Decision |
|---|---|
| 12 | Title wording / whether the levels get names |
| 13 | Unicode encoding variants |
| 20 | Who double-codes the §4.6 failure taxonomy |
| 21 | Compute budget for Phase 5 |
| — | Rule-7 amendment signature |
| — | **Six base papers, none of which I have read — STATUS calls this the highest risk in the file** |
