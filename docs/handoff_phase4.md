# Handoff prompt — Phase 4 (paste this into the new chat)

---

You are continuing my BSc thesis (targeting a Q1 journal). The repo is the
folder you have open. **Do not start work until you have read, in this order:**

1. `CLAUDE.md` — the inviolable rules and how to behave
2. `docs/STATUS.md` — where we are, verified facts, open decisions
3. `docs/research_pipeline_en.md` §4 (Phase 4) — the normative spec for this task
4. `docs/protocol.md` — the pre-registration; read the last ~10 deviation rows,
   they are all from 2026-08-11 and several change Phase 4

`docs/research_pipeline_en.md` is the **only** normative pipeline — line 8's
reference to a Bangla mirror was struck on 2026-08-11 because that file never
existed. **You must maintain the pipeline file as we go**; it went 10 days and
55 commits stale once already and that is logged as a failure.

## The task

**Pipeline step 16: build the LangGraph loop (§4.1–4.2) + a 20-generation
pilot to choose Llama vs Qwen.**

`src/agents/` and `src/eval/` are empty stubs apart from
`src/eval/tau_objective.py`. Phase 4 has no config yet. This is where the
title's *"Multi-Agent"* and *"Verifier-in-the-Loop"* actually get built.

Four components, contracts in §4.2:

| | Component | LLM? |
|---|---|---|
| 1 | Researcher — ChromaDB, top-10, **R1 index only** | no |
| 2 | Writer — temp 0.8, top_p 0.9, seed logged | **yes** |
| 3 | Critic — `w·VerifierA + (1−w)·symbolic` vs τ | **no, deliberately** |
| 4 | Reflector — names the failed rules, FAIL only | yes (small) |

Loop control: FAIL & attempt<3 → back to Researcher with the original
persona+plot query **anchored** and feedback keywords only *augmenting*;
FAIL & attempt=3 → emit best-of-3 with `gave_up=True`.

## Things settled on 2026-08-11 that you must not re-open

- **`w` has NO value.** The old `0.6/0.4` was struck — the spec called it
  "dev-tuned" and no tuning ever produced it. `w` is fit on the **30
  dev-plots' generations** and reported as a **sensitivity curve, never a
  point**. Do not write a number for it.
- **τ selection is already pre-registered** — `src/eval/tau_objective.py` and
  the decision-19 deviation row. Endpoints α_lo (τ=0, = §5.1 row 1) and α_hi
  (τ=1, all 3 attempts), **both scored by Verifier-B**, headline
  τ\* = argmax[quality(τ) − α_lo]/E[calls](τ). Do not invent a pass-rate target;
  "first-pass 60–70%" was struck.
- **τ is swept at quantiles of the observed scores**, not on a uniform grid.
- **Verifier-B never enters the loop** (inviolable rule 6). It scores S6 and
  the τ sanity-check only. This wall *is* the Goodhart test.
- **Never claim "autonomous multi-agent system"** — §4.0 fixes the wording:
  *compound AI system implementing the evaluator-optimizer workflow*.
  The title keeps "Multi-Agent"; the first Methods paragraph carries the honest
  definition.
- **K = 2, not 3.** The words *persona* and *cluster* are both retired —
  use **axis / gradient / the cut / level**. Replacement wording for the title
  is my call (open decision 12), so flag it, don't rewrite it.
- **`enable_f1` stays false.** The symbolic scorer's IDF family is blocked
  pending a rule-7 amendment my supervisor has not signed
  (`docs/rule7_amendment_packet.md`). The guard is in the code; do not flip it.

## How I need you to work

- **Search the literature BEFORE every design decision**, not after — including
  ones that feel like engineering. Consensus quota is exhausted until
  2026-09-01, so use alphaXiv/scite and **say which index you used**. Report
  what the search changed; if it changed nothing, say that too.
- **Every decision constant must carry a reason.** `python
  src/common/check_constants.py` must pass. When you write
  `configs/s4_*.yaml`, every threshold needs an inline comment, a `# ref:`
  pointer, or a protocol.md pre-registration. A number with a value and no
  criterion is the defect we spent a day removing.
- **Do not invent numbers or reasoning.** If a reason is mine, ask me — do not
  guess and write it down as mine. If something has no reason, say so rather
  than manufacturing one.
- **Negative results are results.** Pre-commit the outcomes before running.
- Small, reviewable scripts. One config = one YAML = one result file.
  Notebooks hold runners only.
- **Definition of Done**: `step_close.py --step S4 ...`, fill the TODOs by hand,
  update `related_work.md` + `references.bib`, update `STATUS.md`, add a
  deviations row if you departed from the spec, and `step_close.py --check`
  must exit 0. Commit code + results + notebook together.
- Teach me the tricky parts in Bangla when it helps.

## Where to start

Read the four documents, then tell me your plan for step 16 **before writing
code** — in particular which LLM provider/models you propose for the pilot and
why, and what you intend to pre-register before the first generation runs.

---
