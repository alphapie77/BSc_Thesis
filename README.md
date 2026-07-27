# A Neuro-Symbolic Multi-Agent Framework for Pre-release Audience Simulation in Bangla Cinema
### A Verifier-in-the-Loop Approach

**Status:** Phase 0 — setup. No experimental results yet.

## Reproducibility contract
- **Global seed = 42** (`src/common/seed.py`, used everywhere).
- **One config = one YAML = one result file.** Nothing hand-run in a notebook enters the paper.
- Every file in `results/` carries a timestamp and the git commit hash it was produced from.
- `data/raw/` is **read-only**. No script may write to it.
- `data/splits/split_map_v1.json` is frozen after creation and never regenerated.

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

## Data availability
Base corpus: Raw Bangla Movie Review Comment Dataset (Mendeley), 5,000 rows.
See `docs/dataset_card.md` for provenance and the honest note on pre-cleaning.
