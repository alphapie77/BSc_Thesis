#!/usr/bin/env python3
"""Plot the registered K-selection diagnostics for Chapter 3."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.seed import set_seed


REQUIRED = {
    "K",
    "prediction_strength",
    "bootstrap_ari_mean",
    "bootstrap_ari_sd",
    "silhouette",
    "gap",
    "gap_se",
}


def _read(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise RuntimeError(f"{path} is missing columns: {sorted(missing)}")
    if frame["K"].tolist() != list(range(2, 9)):
        raise RuntimeError(f"{path} must contain the frozen K=2..8 sweep")
    return frame


def main() -> int:
    set_seed()
    parser = argparse.ArgumentParser()
    parser.add_argument("--region-a", default="results/s2d_ktable_regionA.csv")
    parser.add_argument("--region-b", default="results/s2d_ktable_regionB.csv")
    parser.add_argument(
        "--output",
        default="docs/chapters/chapter3/figures/k_selection_diagnostics.png",
    )
    args = parser.parse_args()

    series = [
        ("Region A", _read(Path(args.region_a)), "#1769aa", "o"),
        ("Region B (negative control)", _read(Path(args.region_b)), "#d95f02", "s"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 7.5), sharex=True)

    panels = [
        ("prediction_strength", "Prediction strength", (0.25, 0.92)),
        ("bootstrap_ari_mean", "Bootstrap ARI", (0.25, 1.03)),
        ("silhouette", "Silhouette score", (0.0, 0.06)),
        ("gap", "Gap statistic", (0.86, 1.05)),
    ]
    for ax, (column, title, ylim) in zip(axes.flat, panels):
        for label, frame, colour, marker in series:
            error = None
            if column == "bootstrap_ari_mean":
                error = frame["bootstrap_ari_sd"]
            elif column == "gap":
                error = frame["gap_se"]
            ax.errorbar(
                frame["K"], frame[column], yerr=error, label=label,
                color=colour, marker=marker, linewidth=2.0, markersize=5.5,
                capsize=3,
            )
        ax.axvline(2, color="#2b2b2b", linestyle=":", linewidth=1.2)
        ax.set_title(title, fontweight="bold")
        ax.set_ylim(*ylim)
        ax.set_xticks(range(2, 9))
        ax.grid(axis="y", alpha=0.22)
        ax.spines[["top", "right"]].set_visible(False)

    axes[0, 0].axhline(0.80, color="#4d4d4d", linestyle="--", linewidth=1.3)
    axes[0, 0].text(8.0, 0.807, "registered threshold = 0.80",
                    ha="right", va="bottom", fontsize=9)
    axes[0, 0].annotate("only K=2 clears threshold",
                        xy=(2, series[0][1].loc[0, "prediction_strength"]),
                        xytext=(3.15, 0.875), fontsize=9,
                        arrowprops={"arrowstyle": "->", "lw": 1.0})
    axes[1, 0].annotate("negligible separation",
                        xy=(2, series[0][1].loc[0, "silhouette"]),
                        xytext=(3.0, 0.051), fontsize=9,
                        arrowprops={"arrowstyle": "->", "lw": 1.0})
    axes[1, 1].text(7.95, 0.875, "registered rule selects no K",
                    ha="right", va="bottom", fontsize=9)

    for ax in axes[1, :]:
        ax.set_xlabel("Number of K-means clusters (K)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Diagnostic value")

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.945),
               ncol=2, frameon=False)
    fig.suptitle("K-selection diagnostics across the two corpus regions",
                 fontweight="bold", y=0.985)
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.08, top=0.85,
                        hspace=0.18, wspace=0.13)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output,
        dpi=220,
        bbox_inches="tight",
        metadata={"Title": "Chapter 3 K-selection diagnostics"},
    )
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
