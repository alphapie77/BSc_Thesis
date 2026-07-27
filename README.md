# A Neuro-Symbolic Multi-Agent Framework for Pre-release Audience Simulation in Bangla Cinema
### A Verifier-in-the-Loop Approach

**Status:** Phase 0 — setup. No experimental results yet.

## Reproducibility contract
- **Global seed = 42** (`src/common/seed.py`, used everywhere).
- **One config = one YAML = one result file.** Nothing hand-run in a notebook enters the paper.
- Every file in `results/` carries a timestamp and the git commit hash it was produced from.
- `data/raw/` is **read-only**. No script may write to it.
- `data/splits/split_map_v1.json` is frozen after creation and never regenerated.
- **The source `.xlsx` is pinned by checksum.** Every `review_id` derives from its
  raw row order, so a different copy silently invalidates every ID with no error.
  Verify byte-identity before any re-run:
  ```
  SHA-256  8f972734fc3629427cdf8d01716aa817f7b325410b2fdd0f26cbc2e68506db9f
  size     195,186 bytes
  ```
  The file is re-downloadable from Mendeley, so the control is **verification,
  not backup**. `bn_clean.csv` needs neither — it is deterministically
  regenerable by `s1_clean.py`, which asserts n = 4,730.

## Layout
```
data/      raw/ (immutable)  cleaned/  splits/ (frozen)  plots/
src/       common/ preprocess/ cluster/ verifier/ agents/ eval/
configs/   one YAML per experiment
results/   auto-logged, never hand-edited
docs/      protocol.md, dataset card, model card
notebooks/ Kaggle/Colab runners ONLY (clone + install + call a script)
```

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.in        # resolves to latest
python src/common/env_snapshot.py     # writes requirements.lock.txt + results/env_*.json
```
Commit `requirements.lock.txt`. From then on, reruns use:
```bash
pip install -r requirements.lock.txt
```

### Enable the pre-commit hook (once per clone)
```bash
git config core.hooksPath .githooks
```
Git does not track hook configuration, so this is **not** inherited when you
clone — every working copy must run it once, or the check silently never runs.

`.githooks/pre-commit` runs `python src/common/step_close.py --check` and blocks
the commit on a non-zero exit. It enforces the Definition of Done in
`CLAUDE.md`: no unfilled TODOs in `docs/lab_notebook.md`, and no commit that
touches `results/` without touching the lab notebook alongside it.

To bypass deliberately — for example while `docs/protocol.md` is legitimately
still unfrozen before S2:
```bash
git commit --no-verify
```
`--no-verify` is the intended override. Weakening the check itself to make a
commit pass is not.

**The hook must be mode `100755` in the index.** This checkout has
`core.fileMode=false`, so a plain `git add .githooks/pre-commit` can silently
drop the executable bit back to `100644`. Git then **skips the hook without any
warning** — the check looks enabled while never running. Verify and repair:
```bash
git ls-files -s .githooks/pre-commit      # must start with 100755
git update-index --chmod=+x .githooks/pre-commit   # fix if it reads 100644
```
`.gitattributes` pins `.githooks/**` to LF endings for the same reason: with
`core.autocrlf=true`, CRLF in a `#!/bin/sh` script breaks the hook on
Linux/macOS.

## Data availability
Base corpus: Raw Bangla Movie Review Comment Dataset (Mendeley), 5,000 rows.
See `docs/dataset_card.md` for provenance and the honest note on pre-cleaning.
