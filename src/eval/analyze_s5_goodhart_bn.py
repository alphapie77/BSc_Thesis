#!/usr/bin/env python3
"""Selection-aware Goodhart analysis for S5 Bangla retry trajectories.

Attempt 2/3 exist only after an earlier attempt fails.  This runner therefore
reports the descriptive attempt curve *and* same-case adjacent transitions;
the latter is the only valid evidence for a widening A−B gap across retries.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import write_csv_result, write_result
from src.common.seed import set_seed


class S5GoodhartError(RuntimeError):
    pass


def _load(path: Path) -> list[dict]:
    rows, keys = [], set()
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        key = row.get("key")
        if not isinstance(key, str) or key in keys:
            raise S5GoodhartError(f"duplicate/invalid score key at {lineno}")
        keys.add(key)
        rows.append(row)
    return rows


def _mean(rows: list[dict], field: str) -> float:
    return sum(float(x[field]) for x in rows) / len(rows)


def summaries(scores: list[dict]) -> tuple[list[dict], list[dict]]:
    """Return descriptive curves and selection-controlled paired transitions."""
    attempts_by_condition: dict[tuple[str, int], list[dict]] = defaultdict(list)
    transitions: dict[tuple[str, int, int], list[dict]] = defaultdict(list)
    for case in scores:
        condition = case.get("condition")
        attempts = [a for a in case.get("attempt_scores", [])
                    if a.get("verifier_a_target_probability") is not None]
        by_attempt = {}
        for a in attempts:
            attempt = int(a["attempt"])
            record = {
                "condition": condition, "attempt": attempt,
                "verifier_a": float(a["verifier_a_target_probability"]),
                "verifier_b": float(a["verifier_b_target_probability"]),
            }
            record["a_minus_b"] = record["verifier_a"] - record["verifier_b"]
            attempts_by_condition[(condition, attempt)].append(record)
            by_attempt[attempt] = record
        for start in (1, 2):
            if start in by_attempt and start + 1 in by_attempt:
                left, right = by_attempt[start], by_attempt[start + 1]
                transitions[(condition, start, start + 1)].append({
                    "a_delta": right["verifier_a"] - left["verifier_a"],
                    "b_delta": right["verifier_b"] - left["verifier_b"],
                    "gap_delta": right["a_minus_b"] - left["a_minus_b"],
                })
    if not attempts_by_condition:
        raise S5GoodhartError("no A/B attempt trajectories found")
    curve = []
    for (condition, attempt), rows in sorted(attempts_by_condition.items()):
        curve.append({
            "condition": condition, "attempt": attempt, "n_cases": len(rows),
            "mean_verifier_a": _mean(rows, "verifier_a"),
            "mean_verifier_b": _mean(rows, "verifier_b"),
            "mean_a_minus_b": _mean(rows, "a_minus_b"),
            "interpretation": "descriptive; later attempts are failure-selected",
        })
    paired = []
    for (condition, start, end), rows in sorted(transitions.items()):
        paired.append({
            "condition": condition, "from_attempt": start, "to_attempt": end,
            "n_paired_cases": len(rows),
            "mean_a_delta": _mean(rows, "a_delta"),
            "mean_b_delta": _mean(rows, "b_delta"),
            "mean_a_minus_b_delta": _mean(rows, "gap_delta"),
            "interpretation": "same cases only; positive gap delta indicates widening A−B gap",
        })
    return curve, paired


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s5_goodhart_bn.yaml")
    args = ap.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parents[2]
    resolve = lambda x: Path(x) if Path(x).is_absolute() else root / x
    scores = _load(resolve(cfg["inputs"]["b_scores_jsonl"]))
    if len(scores) != 5400:
        raise S5GoodhartError(f"need the sealed 5,400-case score archive, got {len(scores)}")
    curve, paired = summaries(scores)
    write_csv_result(curve, resolve(cfg["outputs"]["attempt_summary_csv"]), list(curve[0]), args.config)
    write_csv_result(paired, resolve(cfg["outputs"]["paired_transitions_csv"]), list(paired[0]), args.config)
    report = {
        "status": "S5_BN_GOODHART_ANALYSIS_PASS",
        "n_scored_cases": len(scores),
        "n_descriptive_attempt_rows": len(curve),
        "n_selection_controlled_transitions": len(paired),
        "warning": "Attempt 2/3 descriptive rows are failure-selected; use paired transitions for Goodhart direction.",
    }
    write_result(report, resolve(cfg["outputs"]["report_json"]), args.config)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
