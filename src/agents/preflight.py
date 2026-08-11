#!/usr/bin/env python3
"""Does the committed Verifier-A behave the same HERE as where it was measured?

WHY THIS EXISTS
---------------
Verifier-A was fitted on Kaggle: Linux, Python 3.12.13 (`results/s3c_verifier_a.json`).
The Phase 4 loop runs on Sabbir's Windows machine, Python 3.13.3, and
`requirements.lock.txt` of 2026-08-11 records **transformers 5.14.1** there --
while S3.2 was deliberately re-run under **transformers < 5** because 5.x broke
an arm, and its numbers are attributed to transformers 4.57.6.

Two things therefore differ between where the Critic's judge was MEASURED and
where it will JUDGE: the operating system and Python minor, and the encoder
stack around LaBSE. Coakley et al. (2022) measured **> 6 pp** of accuracy
variation from environment alone; Verifier-A's reproduction gate is **0.6 pp**
(half a dev item). Those two numbers are an order of magnitude apart, which is
exactly the situation `protocol.md` §S3.3 was worried about when it declined to
run the verifiers on a third host.

So this is run once, before the Critic is trusted, and its answer goes in the
appendix either way. **A null result here is a real result**: "the artifact
reproduces across hosts" is a claim this thesis would otherwise be making
silently.

WHAT IT DOES NOT DO
-------------------
**It never refits and never writes to `artifacts/` or `results/s3c_*`.** Those
are the committed Kaggle-produced files. Re-running `train_verifier_a.py` here
would overwrite them with locally-fitted ones and destroy the very comparison
this script performs -- and it would look like success, because the numbers
would match themselves.

Read-only, by construction: it loads the committed artifact and the committed
per-item predictions, recomputes predictions in THIS environment, and diffs.
Reported in ITEMS, because one dev item = 0.0122 macro-F1 and decimals invite
over-reading at n = 82.

Run:  python src/agents/preflight.py --config configs/s3c_verifier_a.yaml
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.seed import set_seed  # noqa: E402
from src.verifier.split_access import load_training_rows  # noqa: E402

#: The value S3.2b measured and S3.3 reproduced on Kaggle. Not a target to hit
#: -- a reference to diff against. ref: results/s3c_verifier_a.md
KAGGLE_REFERENCE_MACRO_F1 = 0.9866

#: One dev item, in macro-F1, at n = 82. Every gap below is reported as a
#: multiple of this. ref: protocol.md §S3.3, "read every gap in items".
ONE_DEV_ITEM = 0.0122


def macro_f1(y_true: list[int], y_pred: list[int]) -> float:
    from sklearn.metrics import f1_score

    return float(f1_score(y_true, y_pred, average="macro"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    set_seed()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    inp, out = cfg["inputs"], cfg["outputs"]

    _, dev = load_training_rows(
        "A",
        split_map=inp["split_map"],
        k2_assignments=inp["k2_assignments"],
        cleaned_csv=inp["cleaned_csv"],
        hold_out_dev=True,
    )

    committed: dict[str, dict] = {}
    with open(out["dev_predictions_csv"], encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            committed[row["review_id"]] = row

    import joblib
    from sentence_transformers import SentenceTransformer

    clf = joblib.load(out["artifact"])
    encoder = SentenceTransformer(cfg["model"]["labse_model"])
    vecs = encoder.encode(
        list(dev.texts), batch_size=64, show_progress_bar=False,
        normalize_embeddings=True,
    )
    here = [int(p) for p in clf.predict(vecs)]

    y_true = list(dev.labels)
    f1_here = macro_f1(y_true, here)
    f1_committed = macro_f1(
        y_true, [int(committed[i]["y_pred"]) for i in dev.review_ids]
    )

    flips = [
        rid
        for rid, p in zip(dev.review_ids, here)
        if int(committed[rid]["y_pred"]) != p
    ]

    print(f"\ndev rows compared           : {len(dev)}")
    print(f"macro-F1 recorded on Kaggle : {f1_committed:.4f}")
    print(f"macro-F1 recomputed here    : {f1_here:.4f}")
    print(f"reference (S3.2b / S3.3)    : {KAGGLE_REFERENCE_MACRO_F1}")
    gap_items = abs(f1_here - f1_committed) / ONE_DEV_ITEM
    print(f"gap                         : {gap_items:.2f} dev items")
    print(f"per-item prediction flips   : {len(flips)}"
          + (f"  {flips}" if flips else ""))

    if not flips:
        print(
            "\nVERDICT: HOST_INVARIANT — every one of the 82 predictions is\n"
            "identical to the committed Kaggle run. The Critic may use this\n"
            "artifact locally, and the appendix can say so as a measurement\n"
            "rather than an assumption."
        )
    else:
        print(
            f"\nVERDICT: HOST_DEPENDENT — {len(flips)} prediction(s) changed with\n"
            "no change to the model or the data, only to the environment.\n"
            "This is NOT automatically a defect (Coakley et al. put\n"
            "environment-only variation above 6 pp), but it must be reported,\n"
            "and the loop's scores are then attributable to THIS host, not to\n"
            "the one in s3c_verifier_a.json. Do not average the two.\n"
            "Stop and record it before building the Critic."
        )


if __name__ == "__main__":
    main()
