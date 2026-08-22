#!/usr/bin/env python3
"""Render thesis-ready S5 Bangla tables without recomputing inference."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.common.provenance import stamp, write_result, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402


class ReportingTableError(RuntimeError):
    pass


def _clean_csv(path: Path, expected_rows: int) -> pd.DataFrame:
    frame = pd.read_csv(path)
    if len(frame) != expected_rows:
        raise ReportingTableError(f"{path} requires {expected_rows} rows, got {len(frame)}")
    commits = set(frame["_git_commit"].astype(str))
    if len(commits) != 1 or any(x.endswith("-dirty") for x in commits):
        raise ReportingTableError(f"{path} lacks one clean producing commit")
    return frame


def render(master: pd.DataFrame, paired: pd.DataFrame, provenance: dict) -> str:
    if master[["condition", "target_level"]].duplicated().any():
        raise ReportingTableError("duplicate master condition-level cell")
    if set(master["target_level"]) != {0, 1} or master["condition"].nunique() != 10:
        raise ReportingTableError("master table is not exact 10 conditions x 2 levels")
    if set(paired["baseline"]) != {"zero_shot"} or paired["condition"].nunique() != 9:
        raise ReportingTableError("paired table is not the planned 9-vs-zero-shot family")
    lines = [
        "# S5 Bangla thesis-ready reporting tables", "",
        f"**UTC:** `{provenance['timestamp_utc']}`  ",
        f"**Producing commit:** `{provenance['git_commit']}`  ",
        "**Standing:** formatting-only view of audited tables; no inference recomputed.", "",
        "## Main table — Verifier-B outcome scoring", "",
        "| Condition | Level | n | Mean target p | Binary accuracy | Mean calls | Mean tokens | Gave-up |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in master.sort_values(["condition", "target_level"]).iterrows():
        lines.append(f"| {r.condition} | {int(r.target_level)} | {int(r.n)} | "
                     f"{r.verifier_b_mean_target_probability:.4f} | {r.verifier_b_binary_accuracy:.4f} | "
                     f"{r.mean_generator_calls:.3f} | {r.mean_generator_tokens:.1f} | {r.gave_up_rate:.4f} |")
    lines += ["", "## Planned paired statistics — each condition vs zero-shot", "",
              "| Condition | Pairs | Delta target p | 95% CI | Bootstrap p | BH q | McNemar p |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for _, r in paired.sort_values("b_probability_delta", ascending=False).iterrows():
        lines.append(f"| {r.condition} | {int(r.n_pairs)} | {r.b_probability_delta:+.4f} | "
                     f"[{r.ci_low:+.4f}, {r.ci_high:+.4f}] | {r.bootstrap_p:.6g} | "
                     f"{r.bh_q_bootstrap_p:.6g} | {r.mcnemar_p:.6g} |")
    lines += ["", "## Reporting constraints", "",
              "- Verifier-B calibration improvement was not established; report this beside outcome scores.",
              "- Seeds 42/43/44 are paired blocking/sensitivity factors, not independent study replications.",
              "- Human accuracy is pending and must be added only after all three blinded response files pass ingestion.",
              "- The registered dev-plot mini-ablations are not represented by this main-run table and are not inferred post hoc.", ""]
    return "\n".join(lines)


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s5_reporting_tables_bn.yaml")
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[2]
    cfg = yaml.safe_load((root / args.config).read_text(encoding="utf-8"))
    paths = {k: root / v for k, v in cfg["inputs"].items()}
    analysis = json.loads(paths["analysis_json"].read_text(encoding="utf-8"))["result"]
    if analysis.get("status") != "S5_BN_ANALYSIS_PASS" or analysis.get("n_scored_cases") != 5400:
        raise ReportingTableError("analysis manifest is not the complete S5 Bangla result")
    prov = stamp(args.config, {"stage": "s5_reporting_tables"})
    report_path = root / cfg["outputs"]["report_md"]
    write_text_lf(report_path, render(_clean_csv(paths["master_csv"], 20),
                                      _clean_csv(paths["paired_csv"], 9), prov))
    manifest = {"status": "S5_BN_REPORTING_TABLES_PASS", "n_master_cells": 20,
                "n_paired_comparisons": 9,
                "report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
                "input_sha256": {k: hashlib.sha256(v.read_bytes()).hexdigest() for k, v in paths.items()},
                "standing": "formatting only; no inference recomputed"}
    write_result(manifest, root / cfg["outputs"]["manifest_json"], args.config)
    print(f"wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

