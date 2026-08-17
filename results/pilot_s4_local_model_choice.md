# S4 pilot — generator selection

> ⛔ **NOT A RESULT.** This file selects a generator. It measures nothing, and nothing in it may be quoted in the thesis, a paper, or a results table. Decision rule pre-registered in `docs/protocol.md` §S4 decision 3, **before** any generation existed.

| model | prompt arm | n | Latin above baseline | max Latin frac | mean chars | **verbatim corpus copies** | verdict |
|---|---|---|---|---|---|---|---|
| `google/gemma-3-12b-it` | bn | 40 | 2 | 0.0725 | 141 | **0**  | **LANG_CONFUSION** |
| `google/gemma-3-12b-it` | en | 20 | 1 | 0.0336 | 125 | **0**  | **LANG_CONFUSION** |
| `md-nishat-008/TigerLLM-9B-it` | bn | 20 | 1 | 0.0725 | 140 | **0**  | **LANG_CONFUSION** |
| `md-nishat-008/TigerLLM-9B-it` | en | 20 | 1 | 0.0336 | 125 | **0**  | **LANG_CONFUSION** |

Latin-script baseline: **0.0009** of characters (region A `has_latin` = 0.09% / 0.00%, `results/s2e_regionA_k2_profile.md`), so any Latin script in a Bangla generation is signal.

## What may be concluded

- **If exactly one arm is `CLEAN`, it is selected**, and no quality claim is made either way.
- **If both are `CLEAN`, the Bangla arm is retained as incumbent** — not because it won, but because 20 generations cannot separate arms on quality. Registered before the outputs were read.
- **The model tie-break is a declared non-performance rule**: on `TIE`, lower cost and higher rate limit, and the thesis states that the data did not choose.


## ⚠️ Verbatim corpus copies

A generation whose text appears **exactly** in `bn_clean.csv` is a retrieved exemplar echoed back, not a generation. At level 0 this is the cheap path — short formulaic comments are easy to copy and the Critic would pass them — so the count is reported **by level**. Any realism metric computed over copies is measuring retrieval.

🔴 **This is a pilot observation, not a measured rate.** It counts exact matches only; a near-copy with one word changed is not caught and would need an edit-distance check before Phase 5.

Observed rate limits: `none returned`
