#!/usr/bin/env python3
"""Pre-specified S5 Bangla tables and paired inference from sealed B scores."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import yaml

from src.common.provenance import write_csv_result, write_result
from src.common.seed import set_seed
from src.eval.s5_contract import CONDITIONS, REPLICATE_SEEDS


class S5AnalysisError(RuntimeError):
    pass


def _rows(path: Path) -> list[dict]:
    output, keys = [], set()
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("key") in keys:
            raise S5AnalysisError(f"duplicate score key at {n}")
        keys.add(row.get("key")); output.append(row)
    return output


def paired_bootstrap(delta: np.ndarray, *, n: int, rng: np.random.Generator,
                     confidence: float) -> tuple[float, float, float, float]:
    if delta.size == 0:
        raise S5AnalysisError("empty paired comparison")
    point = float(delta.mean())
    means = np.empty(n, dtype=float)
    for start in range(0, n, 250):
        width = min(250, n - start)
        indices = rng.integers(0, delta.size, size=(width, delta.size))
        means[start:start + width] = delta[indices].mean(axis=1)
    alpha = (1.0 - confidence) / 2.0
    lo, hi = np.quantile(means, [alpha, 1.0 - alpha]).tolist()
    # Two-sided bootstrap sign test, kept as a descriptive p-value for BH.
    p = min(1.0, 2.0 * min(float(np.mean(means <= 0)), float(np.mean(means >= 0))))
    return point, float(lo), float(hi), p


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    m = len(p_values)
    order = sorted(range(m), key=lambda i: p_values[i])
    adjusted = [0.0] * m
    running = 1.0
    for rank in range(m, 0, -1):
        index = order[rank - 1]
        running = min(running, p_values[index] * m / rank)
        adjusted[index] = running
    return adjusted


def mcnemar_exact(better: int, worse: int) -> float:
    """Two-sided exact binomial McNemar p, no scipy version dependency."""
    n = better + worse
    if n == 0:
        return 1.0
    k = min(better, worse)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2.0 * tail)


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s5_analysis_bn.yaml")
    args = ap.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parents[2]
    resolve = lambda p: Path(p) if Path(p).is_absolute() else root / p
    scores = _rows(resolve(cfg["inputs"]["b_scores_jsonl"]))
    seeds = tuple(int(x) for x in cfg["replicate_seeds"])
    if seeds != REPLICATE_SEEDS:
        raise S5AnalysisError(f"seeds must remain {REPLICATE_SEEDS}")
    by_key = {x["key"]: x for x in scores}
    if len(scores) != 90 * 2 * len(CONDITIONS) * len(seeds):
        raise S5AnalysisError(f"need complete 5,400-case score archive, got {len(scores)}")
    if {x["condition"] for x in scores} != set(CONDITIONS):
        raise S5AnalysisError("score archive has incomplete condition registry")

    master = []
    groups = defaultdict(list)
    for row in scores:
        groups[(row["condition"], row["target_level"])].append(row)
    for (condition, level), rows in sorted(groups.items()):
        values = np.array([x["verifier_b_target_probability"] for x in rows], float)
        success = np.array([x["verifier_b_binary_success"] for x in rows], float)
        master.append({"condition": condition, "target_level": level, "n": len(rows),
                       "verifier_b_mean_target_probability": float(values.mean()),
                       "verifier_b_binary_accuracy": float(success.mean()),
                       "mean_generator_calls": float(np.mean([x["logical_generator_calls"] for x in rows])),
                       "mean_generator_tokens": float(np.mean([x["logical_generator_tokens"] for x in rows])),
                       "gave_up_rate": float(np.mean([x["gave_up"] for x in rows]))})
    write_csv_result(master, resolve(cfg["outputs"]["master_table_csv"]), list(master[0]), args.config)

    baseline = cfg["statistics"]["baseline_condition"]
    n_boot = int(cfg["statistics"]["bootstrap_resamples"])
    confidence = float(cfg["statistics"]["confidence_level"])
    rng = np.random.default_rng(42)
    comparisons = []
    # Pair strictly inside plot × level × replicate; condition is the sole change.
    for condition in CONDITIONS:
        if condition == baseline:
            continue
        pairs = []
        for row in scores:
            if row["condition"] != condition:
                continue
            base_key = row["key"].rsplit("|", 1)[0] + "|" + baseline
            if base_key not in by_key:
                raise S5AnalysisError(f"missing paired baseline for {row['key']}")
            pairs.append((row, by_key[base_key]))
        delta = np.array([a["verifier_b_target_probability"] - b["verifier_b_target_probability"] for a, b in pairs])
        point, lo, hi, p = paired_bootstrap(delta, n=n_boot, rng=rng, confidence=confidence)
        a_success = np.array([a["verifier_b_binary_success"] for a, _ in pairs])
        b_success = np.array([b["verifier_b_binary_success"] for _, b in pairs])
        comparisons.append({"condition": condition, "baseline": baseline, "n_pairs": len(pairs),
                            "b_probability_delta": point, "ci_low": lo, "ci_high": hi,
                            "bootstrap_p": p,
                            "mcnemar_p": mcnemar_exact(int(np.sum((a_success == 1) & (b_success == 0))), int(np.sum((a_success == 0) & (b_success == 1)))),
                            "discordant_condition_only_success": int(np.sum((a_success == 1) & (b_success == 0))),
                            "discordant_baseline_only_success": int(np.sum((a_success == 0) & (b_success == 1)))})
    qvals = benjamini_hochberg([x["bootstrap_p"] for x in comparisons])
    for row, q in zip(comparisons, qvals):
        row["bh_q_bootstrap_p"] = q
    write_csv_result(comparisons, resolve(cfg["outputs"]["paired_statistics_csv"]), list(comparisons[0]), args.config)

    # Goodhart is descriptive: B stays external and no row is selected by it.
    goodhart = []
    for row in scores:
        for attempt in row.get("attempt_scores", []):
            a = attempt.get("verifier_a_target_probability")
            if a is not None:
                goodhart.append({"condition": row["condition"], "target_level": row["target_level"],
                                 "replicate_seed": row["replicate_seed"], "attempt": attempt["attempt"],
                                 "verifier_a": a, "verifier_b": attempt["verifier_b_target_probability"],
                                 "a_minus_b": float(a) - float(attempt["verifier_b_target_probability"])})
    write_csv_result(goodhart, resolve(cfg["outputs"]["goodhart_by_attempt_csv"]), list(goodhart[0]), args.config)
    result = {"status": "S5_BN_ANALYSIS_PASS", "n_scored_cases": len(scores),
              "n_paired_comparisons": len(comparisons), "bootstrap_resamples": n_boot,
              "confidence_level": confidence, "bh_family": "9 planned vs zero-shot comparisons",
              "note": "Replicate seeds are paired blocking/sensitivity factors; no best seed is selected."}
    write_result(result, resolve(cfg["outputs"]["analysis_json"]), args.config)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
