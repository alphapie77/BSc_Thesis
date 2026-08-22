#!/usr/bin/env python3
"""Validate and score the frozen S5 Bangla human evaluation."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import write_csv_result, write_result  # noqa: E402
from src.common.seed import set_seed  # noqa: E402


class HumanEvalScoreError(RuntimeError):
    pass


def validate_responses(key: pd.DataFrame, responses: pd.DataFrame,
                       annotators: tuple[str, ...]) -> pd.DataFrame:
    required_key = {"item_id", "case_key", "plot_id", "condition",
                    "replicate_seed", "target_level"}
    required_response = {"annotator", "item_id", "response"}
    if not required_key.issubset(key.columns):
        raise HumanEvalScoreError(f"key missing columns: {sorted(required_key - set(key.columns))}")
    if set(responses.columns) != required_response:
        raise HumanEvalScoreError("responses must contain exactly annotator,item_id,response")
    if len(key) != 100 or key["item_id"].duplicated().any():
        raise HumanEvalScoreError("researcher key must contain exactly 100 unique items")
    expected = {(a, item) for a in annotators for item in key["item_id"]}
    observed = set(zip(responses["annotator"].astype(str), responses["item_id"].astype(str)))
    if len(responses) != len(expected) or observed != expected:
        missing, extra = expected - observed, observed - expected
        raise HumanEvalScoreError(f"response surface mismatch: missing={len(missing)}, extra={len(extra)}")
    if responses.duplicated(["annotator", "item_id"]).any():
        raise HumanEvalScoreError("duplicate annotator/item response")
    parsed = pd.to_numeric(responses["response"], errors="coerce")
    if parsed.isna().any() or not parsed.isin([0, 1]).all():
        raise HumanEvalScoreError("every response must be forced binary 0 or 1")
    out = responses.copy()
    out["response"] = parsed.astype(int)
    out = out.merge(key, on="item_id", how="left", validate="many_to_one")
    out["correct"] = (out["response"] == out["target_level"].astype(int)).astype(int)
    return out


def nominal_krippendorff_alpha(matrix: np.ndarray) -> float:
    """Nominal alpha for items x raters with complete binary ratings."""
    if matrix.ndim != 2 or matrix.shape[1] < 2 or not np.isin(matrix, [0, 1]).all():
        raise HumanEvalScoreError("alpha requires complete binary item x rater matrix")
    n_raters = matrix.shape[1]
    disagree_pairs = sum(np.sum(row[:, None] != row[None, :]) for row in matrix)
    do = disagree_pairs / (matrix.shape[0] * n_raters * (n_raters - 1))
    values = matrix.ravel()
    n0, n1 = int(np.sum(values == 0)), int(np.sum(values == 1))
    total = len(values)
    de = (2 * n0 * n1) / (total * (total - 1)) if total > 1 else 0.0
    return 1.0 - do / de if de else (1.0 if do == 0 else float("nan"))


def bootstrap_items(joined: pd.DataFrame, *, n: int, confidence: float,
                    rng: np.random.Generator) -> dict:
    items = sorted(joined["item_id"].unique())
    by_item = {item: joined.loc[joined["item_id"] == item, "correct"].to_numpy(float)
               for item in items}
    ratings = joined.pivot(index="item_id", columns="annotator", values="response").loc[items].to_numpy(int)
    acc, alpha = np.empty(n), np.empty(n)
    for i in range(n):
        idx = rng.integers(0, len(items), len(items))
        acc[i] = np.concatenate([by_item[items[j]] for j in idx]).mean()
        alpha[i] = nominal_krippendorff_alpha(ratings[idx])
    q = [(1 - confidence) / 2, 1 - (1 - confidence) / 2]
    return {"accuracy_ci_low": float(np.quantile(acc, q[0])),
            "accuracy_ci_high": float(np.quantile(acc, q[1])),
            "alpha_ci_low": float(np.nanquantile(alpha, q[0])),
            "alpha_ci_high": float(np.nanquantile(alpha, q[1]))}


def summarize(joined: pd.DataFrame, *, n_boot: int, confidence: float) -> tuple[list[dict], dict]:
    rng = np.random.default_rng(42)
    alpha_q = [(1 - confidence) / 2, 1 - (1 - confidence) / 2]

    def accuracy_ci(group: pd.DataFrame) -> tuple[float, float]:
        # Resample items, retaining every rating attached to each sampled item.
        item_values = [g["correct"].to_numpy(float) for _, g in group.groupby("item_id")]
        estimates = np.empty(n_boot)
        for i in range(n_boot):
            draw = rng.integers(0, len(item_values), len(item_values))
            estimates[i] = np.concatenate([item_values[j] for j in draw]).mean()
        return tuple(float(x) for x in np.quantile(estimates, alpha_q))

    rows = []
    for annotator, group in joined.groupby("annotator", sort=True):
        lo, hi = accuracy_ci(group)
        rows.append({"scope": "annotator", "annotator": annotator,
                     "condition": "ALL", "target_level": "ALL", "n": len(group),
                     "accuracy": float(group["correct"].mean()),
                     "accuracy_ci_low": lo, "accuracy_ci_high": hi})
    for (condition, level), group in joined.groupby(["condition", "target_level"], sort=True):
        rows.append({"scope": "cell_pooled", "annotator": "ALL",
                     "condition": condition, "target_level": int(level), "n": len(group),
                     "accuracy": float(group["correct"].mean()),
                     "accuracy_ci_low": None, "accuracy_ci_high": None})
    overall_lo, overall_hi = accuracy_ci(joined)
    rows.append({"scope": "overall_pooled", "annotator": "ALL", "condition": "ALL",
                 "target_level": "ALL", "n": len(joined),
                 "accuracy": float(joined["correct"].mean()),
                 "accuracy_ci_low": overall_lo, "accuracy_ci_high": overall_hi})
    pivot = joined.pivot(index="item_id", columns="annotator", values="response")
    matrix = pivot.to_numpy(int)
    unanimous = float(np.mean(np.all(matrix == matrix[:, [0]], axis=1)))
    alpha = nominal_krippendorff_alpha(matrix)
    ci = bootstrap_items(joined, n=n_boot, confidence=confidence,
                         rng=np.random.default_rng(42))
    confusion = {}
    disagreement = {}
    for level, group in joined.groupby("target_level", sort=True):
        confusion[f"target_level_{int(level)}"] = {
            "n_judgments": len(group),
            "responses_level_0": int((group["response"] == 0).sum()),
            "responses_level_1": int((group["response"] == 1).sum()),
            "accuracy": float(group["correct"].mean()),
        }
        item_matrix = group.pivot(index="item_id", columns="annotator", values="response").to_numpy(int)
        disagreement[f"target_level_{int(level)}"] = {
            "n_items": len(item_matrix),
            "unanimous_items": int(np.sum(np.all(item_matrix == item_matrix[:, [0]], axis=1))),
            "split_2_to_1_items": int(np.sum(~np.all(item_matrix == item_matrix[:, [0]], axis=1))),
        }
    report = {"status": "S5_BN_HUMAN_EVAL_PASS", "n_items": len(pivot),
              "n_judgments": len(joined), "pooled_accuracy": float(joined["correct"].mean()),
              "raw_three_way_agreement": unanimous, "krippendorff_alpha_nominal": alpha,
              **ci, "bootstrap_resamples": n_boot, "confidence_level": confidence,
              "confusion_by_target_level": confusion,
              "disagreement_by_target_level": disagreement,
              "standing": "human target-level match on the frozen balanced 100-case subset"}
    return rows, report


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s5_human_eval_bn.yaml")
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[2]
    cfg = yaml.safe_load((root / args.config).read_text(encoding="utf-8"))
    key = pd.read_csv(root / cfg["outputs"]["key_csv"])
    response_parts = []
    for annotator in cfg["sampling"]["annotators"]:
        path = root / cfg["outputs"]["directory"] / f"s5_human_eval_{annotator}.csv"
        if not path.exists():
            raise HumanEvalScoreError(f"missing annotator response file: {path}")
        response_parts.append(pd.read_csv(path, dtype=str))
    joined = validate_responses(key, pd.concat(response_parts, ignore_index=True),
                                tuple(str(x) for x in cfg["sampling"]["annotators"]))
    summary, report = summarize(joined, n_boot=int(cfg["analysis"]["bootstrap_resamples"]),
                                confidence=float(cfg["analysis"]["confidence_level"]))
    response_fields = ["annotator", "item_id", "response", "correct"]
    write_csv_result(joined[response_fields].to_dict("records"),
                     root / cfg["outputs"]["responses_csv"], response_fields, args.config)
    write_csv_result(summary, root / cfg["outputs"]["summary_csv"], list(summary[0]), args.config)
    write_result(report, root / cfg["outputs"]["report_json"], args.config)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
