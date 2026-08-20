#!/usr/bin/env python3
"""Finalize the explicitly single-coded S4.6 failure taxonomy.

This path exists because Sabbir waived the registered independent second coder
after reviewing Coder-A. It records that deviation; it does not synthesize a
second sheet or an agreement statistic.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.common.provenance import write_result  # noqa: E402
from src.common.seed import set_seed  # noqa: E402
from src.eval.score_s4_failure_taxonomy import CATEGORIES, _binary  # noqa: E402


def finalize(rows: list[dict], audit: dict, expected_cases: int) -> dict:
    if len(rows) != expected_cases:
        raise ValueError(f"expected {expected_cases} cases, found {len(rows)}")
    case_ids = [str(row["case_id"]) for row in rows]
    if len(set(case_ids)) != len(case_ids):
        raise ValueError("duplicate case_id in Coder-A sheet")
    if audit.get("independent_coder_b") is not False:
        raise ValueError("single-coder finalizer requires independent_coder_b=false")
    if audit.get("agreement_available") is not False:
        raise ValueError("single-coder finalizer cannot report agreement")

    category_counts = Counter()
    uncategorized = 0
    coded_cases = []
    other_labels = Counter()
    for row in rows:
        labels = {
            category: _binary(row[category], row["case_id"], category)
            for category in CATEGORIES
        }
        category_counts.update({key: value for key, value in labels.items() if value})
        if not any(labels.values()):
            uncategorized += 1
        other_label = str(row.get("other_label", "")).strip()
        if labels["other"] and not other_label:
            raise ValueError(f"{row['case_id']}: other=1 requires other_label")
        if not labels["other"] and other_label:
            raise ValueError(f"{row['case_id']}: other=0 forbids other_label")
        if other_label:
            other_labels[other_label] += 1
        coded_cases.append({
            "case_id": str(row["case_id"]),
            "target_level": int(row["target_level"]),
            "emitted_attempt": int(row["emitted_attempt"]),
            "labels": labels,
            "other_label": other_label or None,
            "coder_notes": str(row.get("coder_notes", "")).strip(),
        })

    return {
        "status": str(audit["finalization_status"]),
        "n_cases": len(rows),
        "coding_unit": "emitted_best_verifier_a_draft_after_three_time_gate_failure",
        "requested_cases_by_normative_spec": 50,
        "observed_complete_case_census": 8,
        "coder_a_identity": str(audit["coder_a_identity"]),
        "user_reviewed_coder_a_before_endorsement": bool(
            audit["user_reviewed_coder_a_before_endorsement"]
        ),
        "independent_coder_b": False,
        "agreement": None,
        "agreement_reason": "not_available_single_coder_protocol_deviation",
        "category_counts": {
            category: category_counts[category] for category in CATEGORIES
        },
        "uncategorized_no_observable_registered_error": uncategorized,
        "other_label_counts_post_hoc": dict(sorted(other_labels.items())),
        "cases": coded_cases,
    }


def main() -> int:
    set_seed()  # inviolable global-seed rule; first action in the entry point
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s4_failure_taxonomy_single.yaml")
    args = ap.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    with Path(cfg["input"]["coder_a_csv"]).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    result = finalize(rows, cfg["audit"], int(cfg["input"]["expected_cases"]))
    write_result(result, cfg["output"]["taxonomy_json"], config_path=args.config)
    print(
        f"status={result['status']}; n={result['n_cases']}; "
        f"uncategorized={result['uncategorized_no_observable_registered_error']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
