#!/usr/bin/env python3
"""Render the registered S5 Bangla Goodhart figure from frozen tables."""
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


LABELS = {
    "rag_neural_loop": "Neural loop",
    "rag_symbolic_loop": "Symbolic loop",
    "rag_neural_symbolic_feedback": "Neural + symbolic feedback",
}
COLORS = {
    "rag_neural_loop": "#3b82f6",
    "rag_symbolic_loop": "#f59e0b",
    "rag_neural_symbolic_feedback": "#10b981",
}


class GoodhartFigureError(RuntimeError):
    pass


def _read_table(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    commits = set(df["_git_commit"].astype(str))
    if len(commits) != 1 or any(x.endswith("-dirty") for x in commits):
        raise GoodhartFigureError(f"input table lacks one clean producing commit: {path}")
    return df


def build_figure(attempts: pd.DataFrame, transitions: pd.DataFrame,
                 output: Path, *, provenance: dict) -> None:
    conditions = list(LABELS)
    if set(attempts["condition"]) != set(conditions) or set(transitions["condition"]) != set(conditions):
        raise GoodhartFigureError("Goodhart tables do not contain the exact three loop conditions")
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8), constrained_layout=True)

    ax = axes[0]
    for condition in conditions:
        part = attempts[attempts["condition"] == condition].sort_values("attempt")
        x = part["attempt"].to_numpy()
        color = COLORS[condition]
        ax.plot(x, part["mean_verifier_a"], marker="o", color=color, linewidth=2,
                label=f"{LABELS[condition]} — A")
        ax.plot(x, part["mean_verifier_b"], marker="s", color=color, linewidth=1.8,
                linestyle="--", label=f"{LABELS[condition]} — B")
        for _, row in part.iterrows():
            ax.annotate(f"n={int(row['n_cases'])}", (row["attempt"], row["mean_verifier_b"]),
                        xytext=(0, -14), textcoords="offset points", ha="center", fontsize=7,
                        color=color)
    ax.set(title="A. Descriptive attempt trajectories (failure-selected)",
           xlabel="Attempt", ylabel="Mean target probability", xticks=[1, 2, 3], ylim=(0, 1))
    ax.grid(alpha=.22)
    ax.legend(fontsize=7, ncol=2, loc="lower left")

    ax = axes[1]
    transitions = transitions.copy()
    transitions["transition"] = transitions["from_attempt"].astype(str) + "→" + transitions["to_attempt"].astype(str)
    x_positions, labels = [], []
    width = .23
    base = list(range(len(conditions)))
    for offset, transition in zip((-width / 1.3, width / 1.3), ("1→2", "2→3")):
        vals, ns = [], []
        for condition in conditions:
            row = transitions[(transitions["condition"] == condition) &
                              (transitions["transition"] == transition)]
            if len(row) != 1:
                raise GoodhartFigureError(f"missing paired transition {condition} {transition}")
            vals.append(float(row.iloc[0]["mean_a_minus_b_delta"]))
            ns.append(int(row.iloc[0]["n_paired_cases"]))
        bars = ax.bar([x + offset for x in base], vals, width=width, label=transition,
                      color="#6366f1" if transition == "1→2" else "#ec4899")
        for bar, n, val in zip(bars, ns, vals):
            ax.annotate(f"n={n}", (bar.get_x() + bar.get_width()/2, val),
                        xytext=(0, 4 if val >= 0 else -10), textcoords="offset points",
                        ha="center", fontsize=7)
    ax.axhline(0, color="black", linewidth=.8)
    ax.set(title="B. Same-case change in A−B gap",
           ylabel="Δ(A−B); positive = widening gap",
           xticks=base, xticklabels=[LABELS[c] for c in conditions])
    ax.tick_params(axis="x", rotation=15)
    ax.grid(axis="y", alpha=.22)
    ax.legend(title="Transition", fontsize=8)
    fig.suptitle("S5 Bangla verifier trajectories and selection-controlled Goodhart test",
                 fontsize=13, fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220, metadata={"Software": "thesis/plot_s5_goodhart_bn.py",
                                           "Title": "S5 Bangla Goodhart figure",
                                           "Description": f"git_commit={provenance['git_commit']}"})
    plt.close(fig)


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s5_goodhart_figure_bn.yaml")
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[2]
    cfg = yaml.safe_load((root / args.config).read_text(encoding="utf-8"))
    attempt_path = root / cfg["inputs"]["attempt_summary_csv"]
    transition_path = root / cfg["inputs"]["paired_transitions_csv"]
    output = root / cfg["outputs"]["figure_png"]
    prov = stamp(args.config, {"stage": "s5_goodhart_figure"})
    build_figure(_read_table(attempt_path), _read_table(transition_path), output,
                 provenance=prov)
    manifest = {
        "status": "S5_BN_GOODHART_FIGURE_PASS",
        "figure": cfg["outputs"]["figure_png"],
        "figure_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "attempt_summary_sha256": hashlib.sha256(attempt_path.read_bytes()).hexdigest(),
        "paired_transitions_sha256": hashlib.sha256(transition_path.read_bytes()).hexdigest(),
        "panels": {
            "A": "descriptive A/B attempt means; later attempts are failure-selected",
            "B": "same-case adjacent transition in A-B gap; positive indicates widening",
        },
    }
    write_result(manifest, root / cfg["outputs"]["manifest_json"], args.config)
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

