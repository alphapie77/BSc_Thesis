#!/usr/bin/env python3
"""Render Chapter 4 confusion matrices from frozen dev-82 predictions.

The figure deliberately calls dev-82 a held-out development evaluation slice,
not a test set.  Its reference classes are the operational K=2 cluster labels,
not independent human-gold judgements.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.seed import set_seed


def _read_predictions(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {"review_id", "y_true", "y_pred"}
    if not required.issubset(frame.columns) or len(frame) != 82:
        raise RuntimeError(f"{path} must contain 82 frozen predictions")
    if frame["review_id"].duplicated().any():
        raise RuntimeError(f"{path} contains duplicate review identifiers")
    return frame


def main() -> int:
    set_seed()
    parser = argparse.ArgumentParser()
    parser.add_argument("--verifier-a", default="results/s3c_verifier_a_dev_predictions.csv")
    parser.add_argument("--verifier-b", default="results/s3d_verifier_b_dev_predictions.csv")
    parser.add_argument(
        "--output",
        default="docs/chapters/chapter4/figures/verifier_confusion_matrices.png",
    )
    args = parser.parse_args()

    frames = [
        ("Verifier-A: frozen LaBSE probe", _read_predictions(Path(args.verifier_a))),
        ("Verifier-B: BanglaBERT (seed 42)", _read_predictions(Path(args.verifier_b))),
    ]
    if frames[0][1]["review_id"].tolist() != frames[1][1]["review_id"].tolist():
        raise RuntimeError("the two prediction files do not describe the same ordered dev-82 slice")

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.4), constrained_layout=True)
    for ax, (title, frame) in zip(axes, frames):
        matrix = confusion_matrix(frame["y_true"], frame["y_pred"], labels=[0, 1])
        row_share = matrix / matrix.sum(axis=1, keepdims=True)
        image = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=53)
        for i in range(2):
            for j in range(2):
                color = "white" if matrix[i, j] >= 27 else "#17202a"
                ax.text(j, i, f"{matrix[i, j]}\n({row_share[i, j]:.1%})",
                        ha="center", va="center", fontsize=13, color=color)
        ax.set_title(title, fontweight="bold")
        ax.set_xlabel("Predicted operational level")
        ax.set_ylabel("K=2 reference label")
        ax.set_xticks([0, 1], ["Level 0", "Level 1"])
        ax.set_yticks([0, 1], ["Level 0", "Level 1"])
    fig.colorbar(image, ax=axes, shrink=.78, label="Number of development items")
    fig.suptitle("Descriptive Confusion Matrices on the Shared Held-Out dev-82 Slice",
                 fontweight="bold")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output,
        dpi=220,
        metadata={"Title": "Verifier confusion matrices on held-out dev-82"},
    )
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
