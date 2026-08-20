#!/usr/bin/env python3
"""Fit the post-S4.5a neural-gate quality/cost frontier from max traces.

The input contains exactly three generated attempts per dev case, each scored
by Verifier-A (gate) and Verifier-B (evaluation only). Ordinary thresholds are
replayed over prefixes; the explicit FORCED_3 endpoint ignores early PASS.
No model is loaded here, so the rule-6 wall remains structural.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.common.provenance import write_result  # noqa: E402
from src.common.seed import SEED, set_seed  # noqa: E402


def _validate(cases: list[dict], expected_cases: int | None = None) -> None:
    if expected_cases is not None and len(cases) != expected_cases:
        raise ValueError(f"expected {expected_cases} cases, found {len(cases)}")
    keys: set[tuple[str, int]] = set()
    for case in cases:
        key = (str(case["plot_id"]), int(case["target_level"]))
        if key in keys:
            raise ValueError(f"duplicate case {key}")
        keys.add(key)
        attempts = case.get("attempts", [])
        if len(attempts) != 3:
            raise ValueError(f"{key}: FORCED_3 requires exactly 3 attempts")
        if [int(a["attempt"]) for a in attempts] != [1, 2, 3]:
            raise ValueError(f"{key}: attempts must be ordered 1,2,3")
        for a in attempts:
            for name in ("gate_score", "symbolic_score", "verifier_b_score"):
                value = float(a[name])
                if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                    raise ValueError(f"{key} attempt {a['attempt']}: invalid {name}")


def _emit(case: dict, tau: float | None) -> tuple[dict, int, bool]:
    """Return emitted attempt, LLM calls, and gave_up.

    `tau=None` is the explicit FORCED_3 policy. Ties in best-of-three go to the
    earliest attempt, matching LoopState.best_of_trace().
    """
    attempts = case["attempts"]
    if tau is not None:
        for a in attempts:
            if float(a["gate_score"]) >= tau:
                k = int(a["attempt"])
                return a, 2 * k - 1, False
    best = max(attempts, key=lambda a: (float(a["gate_score"]), -int(a["attempt"])))
    return best, 5, tau is not None


def frontier_row(cases: list[dict], tau: float | None) -> dict:
    emitted = [_emit(c, tau) for c in cases]
    n = len(emitted)
    return {
        "policy": "FORCED_3" if tau is None else "THRESHOLD",
        "tau": tau,
        "n": n,
        "quality_b": sum(float(a["verifier_b_score"]) for a, _, _ in emitted) / n,
        "mean_calls": sum(calls for _, calls, _ in emitted) / n,
        "first_pass_rate": (
            0.0 if tau is None else
            sum(float(c["attempts"][0]["gate_score"]) >= tau for c in cases) / n
        ),
        "final_accept_rate": (
            0.0 if tau is None else 1.0 - sum(g for _, _, g in emitted) / n
        ),
        "gave_up_rate": 0.0 if tau is None else sum(g for _, _, g in emitted) / n,
        "mean_emitted_attempt": sum(int(a["attempt"]) for a, _, _ in emitted) / n,
    }


def candidate_thresholds(cases: list[dict]) -> list[float]:
    """Observed-score thresholds, plus 0; no uniform probability grid."""
    scores = {float(a["gate_score"]) for c in cases for a in c["attempts"]}
    return sorted({0.0, *scores})


def choose_tau(rows: list[dict], alpha_lo: float, alpha_hi: float) -> dict:
    best = None
    for row in rows:
        efficiency = (row["quality_b"] - alpha_lo) / row["mean_calls"]
        candidate = {**row, "efficiency": efficiency}
        # Deterministic tie: fewer calls, then smaller tau.
        key = (efficiency, -row["mean_calls"], -float(row["tau"]))
        if best is None or key > best[0]:
            best = (key, candidate)
    chosen = best[1]
    achievable = alpha_hi - alpha_lo
    chosen["alpha_lo"] = alpha_lo
    chosen["alpha_hi"] = alpha_hi
    chosen["fraction_of_achievable"] = (
        (chosen["quality_b"] - alpha_lo) / achievable if achievable > 0 else None
    )
    return chosen


def permutation_test(cases: list[dict], n_shuffles: int, seed: int) -> dict:
    """Descriptive level comparison on attempt-1 Verifier-A scores."""
    groups = {
        level: [float(c["attempts"][0]["gate_score"]) for c in cases
                if int(c["target_level"]) == level]
        for level in (0, 1)
    }
    if not groups[0] or not groups[1]:
        raise ValueError("both target levels are required")
    observed = sum(groups[1]) / len(groups[1]) - sum(groups[0]) / len(groups[0])
    values = groups[0] + groups[1]
    n0 = len(groups[0])
    rng = random.Random(seed)
    extreme = 0
    for _ in range(n_shuffles):
        shuffled = values.copy()
        rng.shuffle(shuffled)
        delta = sum(shuffled[n0:]) / len(groups[1]) - sum(shuffled[:n0]) / n0
        extreme += abs(delta) >= abs(observed)
    return {
        "statistic": "attempt1_mean_gate_score_level1_minus_level0",
        "observed": observed,
        "n_level0": len(groups[0]),
        "n_level1": len(groups[1]),
        "shuffles": n_shuffles,
        "p_value_two_sided": (extreme + 1) / (n_shuffles + 1),
        "interpretation": "descriptive_not_a_gate",
    }


def fit(cases: list[dict], *, shuffles: int = 5000, seed: int = SEED) -> dict:
    _validate(cases)
    thresholds = candidate_thresholds(cases)
    rows = [frontier_row(cases, tau) for tau in thresholds]
    alpha_lo = frontier_row(cases, 0.0)["quality_b"]
    forced = frontier_row(cases, None)
    alpha_hi = forced["quality_b"]
    levels = {}
    for level in (0, 1):
        subset = [c for c in cases if int(c["target_level"]) == level]
        levels[str(level)] = {
            "frontier": [frontier_row(subset, tau) for tau in thresholds],
            "forced_3": frontier_row(subset, None),
        }
    return {
        "method": "global_neural_gate_frontier_with_per_level_reporting",
        "gate": "verifier_a_only",
        "symbolic_role": "diagnostic_only",
        "evaluator": "verifier_b_only",
        "n_cases": len(cases),
        "threshold_source": "observed_gate_scores",
        "frontier": rows,
        "forced_3": forced,
        "selection": choose_tau(rows, alpha_lo, alpha_hi),
        "per_level": levels,
        "level_score_permutation": permutation_test(cases, shuffles, seed),
    }


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def main() -> int:
    set_seed()  # inviolable global-seed rule; first action in the entry point
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s4_tau.yaml")
    args = ap.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    cases = _read_jsonl(Path(cfg["input"]["max_traces_jsonl"]))
    _validate(cases, int(cfg["input"]["expected_cases"]))
    result = fit(
        cases,
        shuffles=int(cfg["analysis"]["permutation_shuffles"]),
        seed=int(cfg.get("seed", SEED)),
    )
    write_result(result, cfg["output"]["report_json"], config_path=args.config)
    chosen = result["selection"]
    print(
        f"tau*={chosen['tau']:.8g} quality_B={chosen['quality_b']:.6f} "
        f"calls={chosen['mean_calls']:.3f}; wrote {cfg['output']['report_json']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
