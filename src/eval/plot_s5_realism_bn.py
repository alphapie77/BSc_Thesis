#!/usr/bin/env python3
"""Render the S5 Bangla corpus-level realism diagnostics from frozen tables."""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import stamp, write_result  # noqa: E402
from src.common.seed import set_seed  # noqa: E402


CONDITIONS = [
    "zero_shot", "static_few_shot", "rag_only", "blind_resampling",
    "intrinsic_self_critique", "external_role_self_critique", "rag_symbolic_loop",
    "rag_neural_loop", "rag_neural_symbolic_feedback", "gemma4_26b_a4b_judge_loop",
]
LABELS = {
    "zero_shot": "Zero-shot", "rag_only": "RAG only",
    "static_few_shot": "Static few-shot", "blind_resampling": "Blind resampling",
    "intrinsic_self_critique": "Intrinsic critique",
    "external_role_self_critique": "External-role critique",
    "rag_symbolic_loop": "Symbolic loop", "rag_neural_loop": "Neural loop",
    "rag_neural_symbolic_feedback": "Neural + symbolic",
    "gemma4_26b_a4b_judge_loop": "Hosted judge loop",
}


class RealismFigureError(RuntimeError):
    pass


def _read_table(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    commits = set(df["_git_commit"].astype(str))
    if len(commits) != 1 or any(x.endswith("-dirty") for x in commits):
        raise RealismFigureError(f"input table lacks one clean producing commit: {path}")
    return df


def _validate(df: pd.DataFrame, name: str) -> None:
    keys = list(zip(df["condition"], df["target_level"]))
    expected = {(c, level) for c in CONDITIONS for level in (0, 1)}
    if len(keys) != 20 or set(keys) != expected or len(keys) != len(set(keys)):
        raise RealismFigureError(f"{name} does not contain the exact 20 condition-level cells")


def build_figure(lengths: pd.DataFrame, diversity: pd.DataFrame, mauve: pd.DataFrame,
                 output: Path, *, provenance: dict) -> None:
    for frame, name in ((lengths, "length JS"), (diversity, "diversity"), (mauve, "MAUVE")):
        _validate(frame, name)
    frames = [
        (lengths, "js_length_exact_word_count", "A. Exact word-count JS ↓", (0, None)),
        (diversity, "rate_texts_under_4_words", "B. Generated texts under 4 words", (0, 1)),
        (mauve, "labse_feature_mauve", "C. LaBSE-feature MAUVE ↑ (sensitivity)", (0, None)),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(14, 6.8), sharey=True)
    y = list(range(len(CONDITIONS)))
    for ax, (frame, metric, title, limits) in zip(axes, frames):
        indexed = frame.set_index(["condition", "target_level"])
        for level, color, marker in ((0, "#2563eb", "o"), (1, "#db2777", "s")):
            values = [float(indexed.loc[(condition, level), metric]) for condition in CONDITIONS]
            ax.scatter(values, y, label=f"Level {level}", color=color, marker=marker, s=38)
        ax.set_title(title, fontsize=10)
        ax.grid(axis="x", alpha=.22)
        ax.set_ylim(len(CONDITIONS)-.5, -.5)
        if limits[1] is not None:
            ax.set_xlim(*limits)
    axes[0].set_yticks(y, [LABELS[c] for c in CONDITIONS], fontsize=8)
    axes[0].legend(loc="lower right", fontsize=8)
    fig.suptitle("S5 Bangla corpus-level realism diagnostics (n=270 generated per cell)",
                 fontsize=13, fontweight="bold")
    fig.subplots_adjust(left=.15, right=.985, top=.87, bottom=.16, wspace=.08)
    fig.text(.5, .055,
             "No sentiment-JS panel: no independent registered generated-text sentiment scorer.\n"
             "MAUVE uses LaBSE features and is not default-GPT2/MoP comparable.",
             ha="center", va="center", fontsize=8, color="#374151")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220, metadata={"Software": "thesis/plot_s5_realism_bn.py",
                                           "Title": "S5 Bangla realism figure",
                                           "Description": f"git_commit={provenance['git_commit']}"})
    plt.close(fig)


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s5_realism_figure_bn.yaml")
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[2]
    cfg = yaml.safe_load((root / args.config).read_text(encoding="utf-8"))
    paths = {key: root / value for key, value in cfg["inputs"].items()}
    output = root / cfg["outputs"]["figure_png"]
    prov = stamp(args.config, {"stage": "s5_realism_figure"})
    build_figure(_read_table(paths["length_js_csv"]),
                 _read_table(paths["diversity_csv"]),
                 _read_table(paths["labse_mauve_csv"]), output, provenance=prov)
    manifest = {
        "status": "S5_BN_REALISM_FIGURE_PASS",
        "figure": cfg["outputs"]["figure_png"],
        "figure_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "input_sha256": {key: hashlib.sha256(path.read_bytes()).hexdigest()
                         for key, path in paths.items()},
        "n_cells": 20,
        "n_generated_per_cell": 270,
        "sentiment_js_status": "NOT_MEASURED_NO_INDEPENDENT_REGISTERED_SCORER",
        "mauve_standing": "LaBSE-feature small-sample sensitivity; not default-GPT2/MoP comparable",
    }
    write_result(manifest, root / cfg["outputs"]["manifest_json"], args.config)
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
