#!/usr/bin/env python3
"""Registered S5 Bangla length-matched sensitivity analysis.

Pairs are same plot x condition x replicate and differ only in requested level.
The strict criterion was frozen in S4: |l0-l1| < .15 * max(l0,l1). Matching is
based only on emitted word counts, never on Verifier-B or success. Because this
conditions on generated (post-treatment) length, it is explicitly a sensitivity
slice and not a replacement for the full-surface primary estimate.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import write_csv_result, write_result  # noqa: E402
from src.common.seed import set_seed  # noqa: E402
from src.eval.s5_contract import CONDITIONS, REPLICATE_SEEDS  # noqa: E402


class LengthMatchedError(RuntimeError):
    pass


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def emitted_text(row: dict) -> str:
    emitted = row["result"]["emitted"]
    text = emitted.get("text")
    if text is None:
        text = emitted.get("generation", {}).get("text")
    if not isinstance(text, str) or not text.strip():
        raise LengthMatchedError(f"empty text for {row.get('key')}")
    return text


def summarize(cases: list[dict], scores: list[dict], tolerance: float) -> list[dict]:
    expected = 90 * 2 * len(CONDITIONS) * len(REPLICATE_SEEDS)
    if len(cases) != expected or len(scores) != expected:
        raise LengthMatchedError(f"requires complete 5,400/5,400 archives; got {len(cases)}/{len(scores)}")
    score_by_key = {r["key"]: r for r in scores}
    if len(score_by_key) != expected or {r["key"] for r in cases} != set(score_by_key):
        raise LengthMatchedError("case/score key sets differ or contain duplicates")
    groups = defaultdict(dict)
    for row in cases:
        groups[(row["condition"], row["plot_id"], int(row["replicate_seed"]))][
            int(row["target_level"])] = row
    out = []
    for condition in CONDITIONS:
        pairs = [v for (c, _, _), v in groups.items() if c == condition]
        if len(pairs) != 90 * len(REPLICATE_SEEDS) or any(set(p) != {0, 1} for p in pairs):
            raise LengthMatchedError(f"incomplete L0/L1 pairs for {condition}")
        matched, all_auc_rows = [], []
        for pair in pairs:
            n0, n1 = len(emitted_text(pair[0]).split()), len(emitted_text(pair[1]).split())
            ok = abs(n0 - n1) < tolerance * max(n0, n1)
            if ok:
                matched.append((pair[0], pair[1], n0, n1))
            all_auc_rows.append((n0, 0)); all_auc_rows.append((n1, 1))
        selected_scores = [score_by_key[r["key"]] for p in matched for r in p[:2]]
        by_level = {level: [score_by_key[p[level]["key"]] for p in matched] for level in (0, 1)}
        out.append({
            "condition": condition, "n_total_pairs": len(pairs),
            "n_matched_pairs": len(matched), "matched_pair_fraction": len(matched) / len(pairs),
            "n_matched_cases": 2 * len(matched),
            "mean_abs_word_gap_matched": (float(np.mean([abs(p[2] - p[3]) for p in matched])) if matched else None),
            "verifier_b_accuracy_matched_all": (float(np.mean([r["verifier_b_binary_success"] for r in selected_scores])) if matched else None),
            "verifier_b_accuracy_matched_l0": (float(np.mean([r["verifier_b_binary_success"] for r in by_level[0]])) if matched else None),
            "verifier_b_accuracy_matched_l1": (float(np.mean([r["verifier_b_binary_success"] for r in by_level[1]])) if matched else None),
            "verifier_b_probability_matched_all": (float(np.mean([r["verifier_b_target_probability"] for r in selected_scores])) if matched else None),
        })
    return out


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s5_length_matched_bn.yaml")
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[2]
    cfg = yaml.safe_load((root / args.config).read_text(encoding="utf-8"))
    rows = summarize(read_jsonl(root / cfg["inputs"]["cases_jsonl"]),
                     read_jsonl(root / cfg["inputs"]["b_scores_jsonl"]),
                     float(cfg["matching"]["relative_tolerance"]))
    write_csv_result(rows, root / cfg["outputs"]["summary_csv"], list(rows[0]), args.config)
    write_result({"status": "S5_BN_LENGTH_MATCHED_SENSITIVITY_PASS",
                  "relative_tolerance": cfg["matching"]["relative_tolerance"],
                  "total_matched_pairs": sum(r["n_matched_pairs"] for r in rows),
                  "standing": "post-treatment sensitivity slice; full-surface analysis remains primary"},
                 root / cfg["outputs"]["report_json"], args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

