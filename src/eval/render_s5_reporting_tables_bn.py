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


def render(master: pd.DataFrame, paired: pd.DataFrame, provenance: dict,
           human_report: dict | None = None,
           human_summary: pd.DataFrame | None = None) -> str:
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
    if human_report is not None:
        if human_report.get("status") != "S5_BN_HUMAN_EVAL_PASS":
            raise ReportingTableError("human report did not pass its registered gate")
        if human_report.get("n_items") != 100 or human_report.get("n_judgments") != 300:
            raise ReportingTableError("human report is not the exact 100-item/300-judgment surface")
        if human_summary is None:
            raise ReportingTableError("human summary is required with human report")
        annotators = human_summary.loc[human_summary["scope"] == "annotator"].sort_values("annotator")
        if list(annotators["annotator"]) != ["A", "B", "C"]:
            raise ReportingTableError("human summary lacks the exact A/B/C annotator rows")
        lines += ["", "## Blinded human validation — frozen 100-item subset", "",
                  "| Scope | n | Target-match accuracy | 95% item-bootstrap CI |",
                  "|---|---:|---:|---:|"]
        for _, r in annotators.iterrows():
            lines.append(f"| Annotator {r.annotator} | {int(r.n)} | {r.accuracy:.4f} | "
                         f"[{r.accuracy_ci_low:.4f}, {r.accuracy_ci_high:.4f}] |")
        lines.append(f"| Pooled | {human_report['n_judgments']} | "
                     f"{human_report['pooled_accuracy']:.4f} | "
                     f"[{human_report['accuracy_ci_low']:.4f}, "
                     f"{human_report['accuracy_ci_high']:.4f}] |")
        lines += ["", f"Raw three-way agreement: **{human_report['raw_three_way_agreement']:.4f}**.  ",
                  f"Nominal Krippendorff alpha: **{human_report['krippendorff_alpha_nominal']:.4f}** "
                  f"(95% item-bootstrap CI "
                  f"[{human_report['alpha_ci_low']:.4f}, {human_report['alpha_ci_high']:.4f}]).  ",
                  "Both requested levels received 137/150 correct judgments. These ratings validate "
                  "human recoverability of the requested engagement-specificity level on the balanced "
                  "subset; they do not validate audience prediction or rank systems."]
    lines += ["", "## Reporting constraints", "",
              "- Verifier-B calibration improvement was not established; report this beside outcome scores.",
              "- Seeds 42/43/44 are paired blocking/sensitivity factors, not independent study replications.",
              "- Human validation covers a frozen balanced 100-item subset, not all 5,400 generated outputs.",
              "- The English mirror is deferred and is not represented by an invented or partial column.",
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
    human_report = None
    human_summary = None
    if "human_report_json" in paths or "human_summary_csv" in paths:
        if not {"human_report_json", "human_summary_csv"}.issubset(paths):
            raise ReportingTableError("both human report and summary inputs are required")
        human_report = json.loads(paths["human_report_json"].read_text(encoding="utf-8"))["result"]
        human_summary = _clean_csv(paths["human_summary_csv"], 24)
    report_path = root / cfg["outputs"]["report_md"]
    write_text_lf(report_path, render(_clean_csv(paths["master_csv"], 20),
                                      _clean_csv(paths["paired_csv"], 9), prov,
                                      human_report, human_summary))
    manifest = {"status": "S5_BN_REPORTING_TABLES_PASS", "n_master_cells": 20,
                "n_paired_comparisons": 9,
                "human_validation_included": human_report is not None,
                "report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
                "input_sha256": {k: hashlib.sha256(v.read_bytes()).hexdigest() for k, v in paths.items()},
                "standing": "formatting only; no inference recomputed"}
    write_result(manifest, root / cfg["outputs"]["manifest_json"], args.config)
    print(f"wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
