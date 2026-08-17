# S4.dev — attempt-1 generations on the 30 dev-plots (LENGTH-CONTROLLED)

> ⛔ **NOT A RESULT.** These generations are the substrate `w` (`protocol.md` §S4 decision 1) and τ (decisions 2, 19) are fitted on. No Critic ran — it requires both, and both are unknown until this file exists. Attempt 1 only; no loop, no Reflector.

| prompt arm | level | n | mean words | median | truncated | foreign script | Latin > baseline | verbatim copies |
|---|---|---|---|---|---|---|---|---|
| bn | L0 | 30 | 11.5 | 11.5 | 0 | 1 | 0 | **0** |
| bn | L1 | 30 | 16.2 | 16.0 | 0 | 2 | 1 | **0** |
| en | L0 | 30 | 10.0 | 10.0 | 0 | 1 | 0 | **0** |
| en | L1 | 30 | 19.2 | 18.5 | 0 | 3 | 2 | **0** |

## The pre-registered length diagnostic

Registered in `docs/axis_definition.md` §3c **before any generation existed**: if level-1 generations are shorter than level-0 by an amount comparable to the corpus gap (**4.27** mean words, 13.12 → 8.85), then axis control **may not be claimed as specificity** — it may be length.

| prompt arm | L0 − L1 mean words | verdict |
|---|---|---|
| bn | -4.77 | `GAP_BELOW_CORPUS` |
| en | -9.23 | `GAP_BELOW_CORPUS` |

⚠️ A verdict of `GAP_BELOW_CORPUS` does **not** establish that the distinction is specificity. It establishes only that the length explanation is not as strong here as in the human corpus. The construct claim rests on RQ1-H's human validation, not on this table.

🔴 **And on 2026-08-16 that verdict was UNINFORMATIVE.** The rule above fixes a *direction* — it asks whether level 1 came out shorter — and the free-length run produced the opposite: level 1 was 25–34 words *longer*. The test passed while the confound it exists to catch was at its strongest. The table below replaces it for any axis-control claim, because it has no direction in it.

## The length confound, measured without a direction

**Content-blind probe** (`2607.18508` §4.1): P(a level-1 generation is longer than a level-0 one). **0.5 = length says nothing about the level; 1.0 = the level is fully recoverable from a word count.** **Matched pairs**: same-plot L0/L1 pairs within 15% of the longer — the slice any length-neutral claim would have to be made on. **Zero means no such claim can be made at all.**

Prompt length control: **ON** (≤ 20 words, identical at both levels)

| prompt arm | length-only AUC | verdict | matched pairs (of 30) |
|---|---|---|---|
| bn | 0.9111 | 🔴 `LENGTH_RECOVERS_LEVEL` | **8** |
| en | 0.9928 | 🔴 `LENGTH_RECOVERS_LEVEL` | **2** |

Reference — the **free-length** run of 2026-08-16: AUC **0.9894** (bn) and **1.0000** (en), **0** matched pairs in either arm. In the en arm the ranges did not overlap at all (longest L0 = 15 words, shortest L1 = 25), so no length-matched evaluation existed to be run.

⚠️ `2601.01768` finds LLMs track their own output length poorly, so a length clause is expected to shift the distribution rather than enforce a bound. **If the AUC stays ≥ 0.90 and the matched slice stays empty, the control FAILED** — and that is reported as a failure, not softened.

## Non-Bangla script

The danda (`U+0964`) is **excluded** from the foreign-script count: Bangla shares it and the corpus uses it. Counting it was the first version's bug, and it inflated the pilot's apparent leak rate from 1-in-20 to 18-in-20.
