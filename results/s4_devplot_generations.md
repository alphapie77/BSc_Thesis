# S4.dev — attempt-1 generations on the 30 dev-plots

> ⛔ **NOT A RESULT.** These generations are the substrate `w` (`protocol.md` §S4 decision 1) and τ (decisions 2, 19) are fitted on. No Critic ran — it requires both, and both are unknown until this file exists. Attempt 1 only; no loop, no Reflector.

| prompt arm | level | n | mean words | median | truncated | foreign script | Latin > baseline | verbatim copies |
|---|---|---|---|---|---|---|---|---|
| bn | L0 | 30 | 13.5 | 12.5 | 0 | 0 | 0 | **0** |
| bn | L1 | 30 | 38.3 | 37.0 | 2 | 3 | 3 | **0** |
| en | L0 | 30 | 6.3 | 6.0 | 0 | 1 | 0 | **0** |
| en | L1 | 30 | 40.3 | 40.0 | 3 | 6 | 6 | **0** |

## The pre-registered length diagnostic

Registered in `docs/axis_definition.md` §3c **before any generation existed**: if level-1 generations are shorter than level-0 by an amount comparable to the corpus gap (**4.27** mean words, 13.12 → 8.85), then axis control **may not be claimed as specificity** — it may be length.

| prompt arm | L0 − L1 mean words | verdict |
|---|---|---|
| bn | -24.77 | `GAP_BELOW_CORPUS` |
| en | -33.97 | `GAP_BELOW_CORPUS` |

⚠️ A verdict of `GAP_BELOW_CORPUS` does **not** establish that the distinction is specificity. It establishes only that the length explanation is not as strong here as in the human corpus. The construct claim rests on RQ1-H's human validation, not on this table.

## Non-Bangla script

The danda (`U+0964`) is **excluded** from the foreign-script count: Bangla shares it and the corpus uses it. Counting it was the first version's bug, and it inflated the pilot's apparent leak rate from 1-in-20 to 18-in-20.
