#!/usr/bin/env python3
"""Exploratory post-hoc hybrid-vs-neural contrast on frozen S5 scores."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import write_result
from src.common.seed import set_seed
from src.eval.analyze_s5_bn import mcnemar_exact, paired_bootstrap
from src.eval.s5_contract import CONDITIONS, REPLICATE_SEEDS


class PosthocContrastError(RuntimeError):
    pass


def load_scores(path: Path) -> list[dict]:
    rows, seen = [], set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        key = row.get("key")
        if not key or key in seen:
            raise PosthocContrastError(f"missing/duplicate key at line {line_number}")
        seen.add(key)
        rows.append(row)
    expected = 90 * 2 * len(REPLICATE_SEEDS) * len(CONDITIONS)
    if len(rows) != expected:
        raise PosthocContrastError(f"need frozen 5,400-score surface, got {len(rows)}")
    if {row.get("condition") for row in rows} != set(CONDITIONS):
        raise PosthocContrastError("condition registry is incomplete")
    return rows


def pair_conditions(rows: list[dict], treatment: str, comparator: str) -> list[tuple[dict, dict]]:
    if treatment not in CONDITIONS or comparator not in CONDITIONS or treatment == comparator:
        raise PosthocContrastError("contrast conditions must be distinct frozen conditions")
    indexed = {row["key"]: row for row in rows}
    pairs = []
    for row in rows:
        if row["condition"] != treatment:
            continue
        comparator_key = row["key"].rsplit("|", 1)[0] + "|" + comparator
        if comparator_key not in indexed:
            raise PosthocContrastError(f"missing comparator for {row['key']}")
        other = indexed[comparator_key]
        pairing_a = (row["plot_id"], int(row["target_level"]), int(row["replicate_seed"]))
        pairing_b = (other["plot_id"], int(other["target_level"]), int(other["replicate_seed"]))
        if pairing_a != pairing_b:
            raise PosthocContrastError(f"pairing mismatch for {row['key']}")
        pairs.append((row, other))
    if len(pairs) != 90 * 2 * len(REPLICATE_SEEDS):
        raise PosthocContrastError(f"need 540 exact pairs, got {len(pairs)}")
    return sorted(pairs, key=lambda pair: pair[0]["key"])


def summarize(pairs: list[tuple[dict, dict]], *, n_boot: int, confidence: float,
              rng: np.random.Generator) -> dict:
    probability_delta = np.array([
        float(t["verifier_b_target_probability"]) - float(c["verifier_b_target_probability"])
        for t, c in pairs
    ])
    point, low, high, p_value = paired_bootstrap(
        probability_delta, n=n_boot, rng=rng, confidence=confidence
    )
    treatment_success = np.array([int(t["verifier_b_binary_success"]) for t, _ in pairs])
    comparator_success = np.array([int(c["verifier_b_binary_success"]) for _, c in pairs])
    treatment_only = int(np.sum((treatment_success == 1) & (comparator_success == 0)))
    comparator_only = int(np.sum((treatment_success == 0) & (comparator_success == 1)))
    return {
        "n_pairs": len(pairs),
        "verifier_b_target_probability_delta": point,
        "naive_post_selection_ci_95": [low, high],
        "descriptive_unadjusted_bootstrap_p": p_value,
        "treatment_only_binary_success": treatment_only,
        "comparator_only_binary_success": comparator_only,
        "descriptive_unadjusted_mcnemar_p": mcnemar_exact(treatment_only, comparator_only),
        "binary_accuracy_delta": float((treatment_success - comparator_success).mean()),
        "mean_generator_calls_delta": float(np.mean([
            float(t["logical_generator_calls"]) - float(c["logical_generator_calls"])
            for t, c in pairs
        ])),
        "mean_generator_tokens_delta": float(np.mean([
            float(t["logical_generator_tokens"]) - float(c["logical_generator_tokens"])
            for t, c in pairs
        ])),
    }


def main() -> int:
    set_seed()
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/s5_posthoc_hybrid_vs_neural_bn.yaml")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = root / config_path
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    score_path = root / config["input"]["verifier_b_scores_jsonl"]
    output_path = root / config["output"]["result_json"]
    treatment = config["contrast"]["treatment"]
    comparator = config["contrast"]["comparator"]
    n_boot = int(config["statistics"]["bootstrap_resamples"])
    confidence = float(config["statistics"]["confidence_level"])

    rows = load_scores(score_path)
    pairs = pair_conditions(rows, treatment, comparator)
    rng = np.random.default_rng(42)
    result = {
        "status": "EXPLORATORY_POSTHOC_COMPLETE",
        "scientific_standing": "post_hoc_exploratory_not_in_confirmatory_family",
        "selection_disclosure": (
            "The direct contrast was added after the registered nine-vs-zero-shot results were "
            "known and after the hybrid condition was observed to have the largest zero-shot effect."
        ),
        "interpretation_rule": (
            "Report effect, compute delta, and selection caveat together. Do not use the naive "
            "interval or unadjusted p-values as confirmatory evidence of hybrid superiority."
        ),
        "treatment": treatment,
        "comparator": comparator,
        "pairing_unit": "plot_id x target_level x replicate_seed",
        "overall": summarize(pairs, n_boot=n_boot, confidence=confidence, rng=rng),
        "by_target_level": {
            str(level): summarize(
                [(t, c) for t, c in pairs if int(t["target_level"]) == level],
                n_boot=n_boot, confidence=confidence, rng=rng,
            )
            for level in (0, 1)
        },
        "input": {
            "path": str(score_path.relative_to(root)).replace("\\", "/"),
            "sha256": hashlib.sha256(score_path.read_bytes()).hexdigest(),
            "n_frozen_scores": len(rows),
            "generation_rerun": False,
            "verifier_b_rescoring": False,
        },
    }
    write_result(result, output_path, str(config_path.relative_to(root)).replace("\\", "/"))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
