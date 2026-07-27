# STATUS — single source of truth for "where are we"

**Last updated:** 2026-07-28 · **Phase:** 0→1 (setup + Bangla data)
**Week:** 1 of 14

> Update this at the same time as the lab notebook entry, at the end of every
> step. `CLAUDE.md` points here rather than duplicating it, so this file is the
> only place progress is recorded.

---

## Pipeline steps

| # | Step | Status | Artifact | Notebook entry |
|---|---|---|---|---|
| 1 | Repo skeleton + reproducibility contract | ✅ done | repo, `seed.py`, `provenance.py` | 2026-07-27 |
| 2 | S0 verification (read-only) | ✅ done | `results/s0_data_xray.md` | 2026-07-27 |
| 3 | S1 cleaning → `bn_clean.csv` (n=4,730) | ✅ done | `data/cleaned/bn_clean.csv`, `results/s1_cleaning_log.json` | 2026-07-27 |
| 4 | Frozen R1/R2 split | ⏸ **deferred** — must run after near-dup removal (leakage) | `data/splits/split_map_v1.json` | — |
| 5 | S2 pilot: near-dup + ARI trap-check | 🔨 code written + unit-tested, **never run** | `results/s2_pilot_ari_trapcheck.md` | — |
| 6 | protocol.md freeze + supervisor signature | 📝 draft; freezes after step 5 | `docs/protocol.md` | — |

## Parallel tracks (no step blocks these — but they block later steps)

| Track | Target | Done | Blocks | Risk |
|---|---|---|---|---|
| Bangla plot synopses | 130 (30 dev + 100 eval) | **0** | S6 evaluation | 🔴 highest — manual, slow, no shortcut |
| Base-paper reading | 5 Tier-1 | **0** | Ch.1, Ch.2 | 🔴 high |
| Gold-300 annotation | 300 × 3 annotators | 0 | RQ1 validation | 🟡 needs S2 clusters first (stratified) |

---

## Verified facts (supersede the pipeline spec where they disagree)

| Quantity | Pipeline claims | **Verified** |
|---|---|---|
| `null_rows` | 1 | **2** (one missing text, one missing label) |
| `normalized_duplicates` | 205 | **206** |
| `usable_n` after rule-based cleaning | 4,722 | **4,730** |
| Post-clean class balance | "perfectly balanced" | **1,513 / 1,599 / 1,618** |
| Final `usable_n` for splitting | — | **unknown** until near-dup removal |

`docs/research_pipeline_en.md` still carries the old numbers — deliberately not
edited until the final `usable_n` is known (see Open decisions).

---

## Open decisions

| # | Decision | Blocks | Resolved by |
|---|---|---|---|
| 1 | Final `usable_n` after near-dup removal | Step 4 | S2 pilot |
| 2 | Near-dup threshold (0.90 / 0.95 / 0.98) from the sensitivity curve | Step 4 | S2 pilot |
| 3 | Do personas survive `ARI(cluster, Sentiment)`, or reframe as engagement tiers? | RQ1 claim | S2 pilot |
| 4 | Correct the S0 table in the pipeline spec | — | after 1–2 |

---

## Immediate next actions

1. Run S2 pilot on Kaggle (internet ON, GPU on, upload `bn_clean.csv` as a Kaggle Dataset — it is gitignored).
2. Read Huang et al. (ICLR 2024) → fill its `related_work.md` entry.
3. Start plot collection: 5/day from bn.wikipedia, log `source_url` for every one.
