#!/usr/bin/env python3
"""Compare two independent S4.6 failure-taxonomy coding sheets."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.common.provenance import write_result, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402


CATEGORIES = (
    "wrong_sentiment", "too_short", "off_topic", "template_repeat",
    "register_or_honorific", "other",
)


def _binary(value: str, case_id: str, category: str) -> int:
    token = str(value).strip().lower()
    mapping = {"0": 0, "no": 0, "n": 0, "false": 0,
               "1": 1, "yes": 1, "y": 1, "true": 1}
    if token not in mapping:
        raise ValueError(f"{case_id} {category}: expected binary 0/1, got {value!r}")
    return mapping[token]


def _kappa(left: list[int], right: list[int]) -> float | None:
    observed = sum(a == b for a, b in zip(left, right)) / len(left)
    p_left = sum(left) / len(left)
    p_right = sum(right) / len(right)
    expected = p_left * p_right + (1 - p_left) * (1 - p_right)
    return None if expected == 1.0 else (observed - expected) / (1 - expected)


def compare(coder_a: list[dict], coder_b: list[dict]) -> tuple[dict, list[dict]]:
    by_a = {row["case_id"]: row for row in coder_a}
    by_b = {row["case_id"]: row for row in coder_b}
    if len(by_a) != len(coder_a) or len(by_b) != len(coder_b):
        raise ValueError("duplicate case_id in a coder sheet")
    if set(by_a) != set(by_b):
        raise ValueError("coder sheets do not contain the same case_ids")
    cases = sorted(by_a)
    category_stats = {}
    disagreements = []
    flat_a, flat_b = [], []
    for category in CATEGORIES:
        left = [_binary(by_a[key][category], key, category) for key in cases]
        right = [_binary(by_b[key][category], key, category) for key in cases]
        flat_a.extend(left)
        flat_b.extend(right)
        category_stats[category] = {
            "n": len(cases),
            "coder_a_positive": sum(left),
            "coder_b_positive": sum(right),
            "agreement": sum(a == b for a, b in zip(left, right)) / len(cases),
            "cohen_kappa": _kappa(left, right),
        }
        for key, a, b in zip(cases, left, right):
            if a != b:
                disagreements.append({
                    "case_id": key,
                    "category": category,
                    "coder_a": a,
                    "coder_b": b,
                    "resolution": "",
                    "resolution_notes": "",
                })
    return ({
        "status": "agreement_before_reconciliation",
        "n_cases": len(cases),
        "categories": list(CATEGORIES),
        "category_stats": category_stats,
        "micro_binary_agreement": sum(a == b for a, b in zip(flat_a, flat_b)) / len(flat_a),
        "micro_binary_cohen_kappa": _kappa(flat_a, flat_b),
        "n_disagreements": len(disagreements),
        "reconciliation_required": bool(disagreements),
    }, disagreements)


def _read(path: str) -> list[dict]:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    set_seed()  # inviolable global-seed rule; first action in the entry point
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s4_failure_taxonomy.yaml")
    args = ap.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    result, disagreements = compare(
        _read(cfg["input"]["coder_a_csv"]),
        _read(cfg["input"]["coder_b_csv"]),
    )
    expected = int(cfg["input"]["expected_cases"])
    if result["n_cases"] != expected:
        raise ValueError(f"expected {expected} cases, found {result['n_cases']}")
    write_result(result, cfg["output"]["agreement_json"], config_path=args.config)
    if disagreements:
        from io import StringIO
        buffer = StringIO(newline="")
        fields = list(disagreements[0])
        writer = csv.DictWriter(buffer, fieldnames=fields)
        writer.writeheader()
        writer.writerows(disagreements)
        write_text_lf(cfg["output"]["disagreements_csv"], buffer.getvalue())
    print(
        f"agreement={result['micro_binary_agreement']:.3f}; "
        f"disagreements={len(disagreements)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
