# Notebooks are RUNNERS, not code.

A Kaggle/Colab notebook in this project clones, installs, and calls a script.
Nothing else. If logic lives in a cell instead of `src/`, it cannot enter the
paper — a reviewer cannot read a cell that only ever existed in a browser tab.

## Current runners

| Notebook | Runs | Needs |
|---|---|---|
| `s2_pilot_kaggle.ipynb` | `src/cluster/s2_pilot.py` (S2 pilot: near-dup + ARI trap-check) | GPU, internet ON, `bn_clean.csv` as a Kaggle Dataset |
| `s4_fit_w_kaggle.ipynb` | `src/eval/preflight_w.py`, then `src/eval/fit_w.py` (S4.5a sensitivity curve) | Internet ON; GPU recommended; no external data/model input |

## Why a Kaggle Dataset for the input

`data/cleaned/bn_clean.csv` is **gitignored** (derived data), so cloning the repo
does not bring it. It has to be uploaded to Kaggle separately as a private
Dataset and copied into the clone. The runner asserts the row count is 4,730
before doing anything expensive — a mismatch means the CSV was regenerated, and
`review_id`s are referenced by the split map, so that must be investigated
rather than accepted.

## Bringing results back

Download the produced files and commit them **from your laptop**, together with
the lab-notebook entry:

- `results/s2_pilot_ari_trapcheck.md`
- `data/cleaned/near_dup_pairs.csv` (gitignored — keep locally for auditing)
- the environment snapshot the runner writes for the host that produced the run

A commit that touches `results/` without touching `docs/lab_notebook.md` is
blocked by `.githooks/pre-commit`, by design.

> **Do not run `src/common/env_snapshot.py` with no arguments on Kaggle.**
> With no `--out` it overwrites the committed `requirements.lock.txt` with a
> Linux freeze, silently replacing the record of the environment the rest of the
> pipeline ran in. Pass `--out` (see the runner) so the Kaggle environment is
> recorded *alongside* the lock file instead of on top of it.
