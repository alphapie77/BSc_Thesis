#!/usr/bin/env python3
"""Score completed S5 Bangla cases once with sealed Verifier-B.

Generation archives are inputs and never edited.  This is the first S5 entry
point allowed to import Verifier-B; its separate score archive makes the wall
between optimisation (A) and outcome scoring (B) inspectable.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import yaml

from src.common.provenance import stamp, write_csv_result, write_result, write_text_lf
from src.common.seed import set_seed
from src.eval.s5_contract import CONDITIONS, REPLICATE_SEEDS, load_eval_plots
from src.eval.verifier_b_score import target_probabilities


class S5ScoreError(RuntimeError):
    """The S5 archive is incomplete, mixed, or unsafe to score."""


def _read_jsonl(path: Path) -> list[dict]:
    rows, keys = [], set()
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            key = row["key"]
        except Exception as exc:
            raise S5ScoreError(f"invalid {path.name}:{lineno}: {exc}") from exc
        if not isinstance(key, str) or key in keys:
            raise S5ScoreError(f"duplicate/invalid key in {path.name}:{lineno}")
        keys.add(key)
        rows.append(row)
    return rows


def _emitted_text(row: dict) -> str:
    emitted = row.get("result", {}).get("emitted", {})
    generation = emitted.get("generation", emitted)
    text = generation.get("text") if isinstance(generation, dict) else None
    if not isinstance(text, str) or not text.strip():
        raise S5ScoreError(f"{row.get('key')}: emitted text is missing")
    return text


def _expected_keys(plots, seeds) -> set[str]:
    return {
        f"S5BN|s{seed}|{plot.plot_id}|L{level}|{condition}"
        for seed in seeds for plot in plots for level in (0, 1)
        for condition in CONDITIONS
    }


def validate_cases(rows: list[dict], *, plots, seeds: tuple[int, ...]) -> None:
    expected = _expected_keys(plots, seeds)
    actual = {row["key"] for row in rows}
    if actual != expected:
        raise S5ScoreError(
            f"S5 surface is incomplete/mixed: got {len(actual)}, expected {len(expected)}; "
            f"missing={len(expected - actual)}, extra={len(actual - expected)}"
        )
    for row in rows:
        if row.get("replicate_seed") not in seeds or row.get("condition") not in CONDITIONS:
            raise S5ScoreError(f"{row['key']}: unregistered seed or condition")
        if row.get("language") != "bn":
            raise S5ScoreError(f"{row['key']}: this scorer is Bangla-only")
        if row.get("verifier_b_score") is not None:
            raise S5ScoreError(f"{row['key']}: B leaked into the generation archive")
        if row.get("provenance", {}).get("verifier_b_loaded") is not False:
            raise S5ScoreError(f"{row['key']}: generation provenance does not prove B wall")
        _emitted_text(row)


def score_rows(rows: list[dict], *, artifact: str, weights: str | None, batch_size: int,
               device: str | None, threshold: float, config_path: str) -> list[dict]:
    # Score the final emission and every loop attempt.  The latter is required
    # for the A−B-over-attempt Goodhart diagnostic; it never feeds generation.
    requests = [(row["key"], "final", _emitted_text(row), int(row["target_level"])) for row in rows]
    for row in rows:
        for attempt in row.get("result", {}).get("attempts", []):
            gen = attempt.get("generation", {})
            text = gen.get("text") if isinstance(gen, dict) else None
            index = attempt.get("attempt")
            if not isinstance(text, str) or not text.strip() or not isinstance(index, int):
                raise S5ScoreError(f"{row['key']}: malformed loop attempt")
            requests.append((row["key"], f"attempt_{index}", text, int(row["target_level"])))
    texts = [x[2] for x in requests]
    levels = [x[3] for x in requests]
    probabilities = target_probabilities(
        texts, levels, artifact_path=artifact, weights_path=weights,
        batch_size=batch_size, device=device,
    )
    if len(probabilities) != len(requests):
        raise S5ScoreError("Verifier-B returned the wrong number of scores")
    b_values = {(key, label): float(p) for (key, label, _, _), p in zip(requests, probabilities)}
    provenance = stamp(config_path, {"stage": "outcome_scoring", "verifier_b_loaded": True})
    output = []
    for row in rows:
        score = b_values[(row["key"], "final")]
        if not 0.0 <= score <= 1.0:
            raise S5ScoreError(f"{row['key']}: B returned non-probability {score}")
        result = row["result"]
        neural = result.get("final_scores", {}).get("neural_score")
        attempts = []
        for attempt in result.get("attempts", []):
            index = int(attempt["attempt"])
            a_score = attempt.get("neural_score")
            attempts.append({
                "attempt": index,
                "verifier_b_target_probability": b_values[(row["key"], f"attempt_{index}")],
                "verifier_a_target_probability": None if a_score is None else float(a_score),
            })
        output.append({
            "key": row["key"], "plot_id": row["plot_id"],
            "replicate_seed": int(row["replicate_seed"]),
            "target_level": int(row["target_level"]), "condition": row["condition"],
            "verifier_b_target_probability": score,
            "verifier_b_binary_success": int(score >= threshold),
            "verifier_a_target_probability": None if neural is None else float(neural),
            "gave_up": bool(result.get("gave_up", False)),
            "logical_generator_calls": int(result["logical_generator_calls"]),
            "logical_generator_tokens": int(result["logical_generator_tokens"]),
            "attempt_scores": attempts,
            "provenance": provenance,
        })
    return output


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s5_score_bn.yaml")
    ap.add_argument("--verifier-b-path", help="mounted directory holding verifier_b.joblib")
    ap.add_argument("--verifier-b-weights", help="mounted Hugging Face weights directory")
    ap.add_argument("--device", default=None)
    args = ap.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parents[2]
    resolve = lambda p: Path(p) if Path(p).is_absolute() else root / p
    cases_path = resolve(cfg["inputs"]["cases_jsonl"])
    rows = _read_jsonl(cases_path)
    plots = load_eval_plots(resolve(cfg["inputs"]["plots_csv"]))
    seeds = tuple(int(x) for x in cfg["replicate_seeds"])
    if seeds != REPLICATE_SEEDS:
        raise S5ScoreError(f"replicate seeds must remain {REPLICATE_SEEDS}")
    validate_cases(rows, plots=plots, seeds=seeds)
    artifact = args.verifier_b_path or str(resolve(cfg["inputs"]["verifier_b_artifact"]))
    threshold = float(cfg["scoring"]["binary_success_threshold"])
    scored = score_rows(rows, artifact=artifact, weights=args.verifier_b_weights,
                        batch_size=int(cfg["scoring"]["batch_size"]), device=args.device,
                        threshold=threshold, config_path=args.config)
    score_path = resolve(cfg["outputs"]["b_scores_jsonl"])
    write_text_lf(score_path, "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in scored))
    csv_rows = [{k: v for k, v in row.items() if k != "provenance"} for row in scored]
    write_csv_result(csv_rows, resolve(cfg["outputs"]["scored_cases_csv"]),
                     list(csv_rows[0]), args.config)
    manifest = {
        "status": "S5_BN_VERIFIER_B_SCORING_PASS", "n_cases": len(scored),
        "counts_by_condition": dict(sorted(Counter(x["condition"] for x in scored).items())),
        "replicate_seeds": list(seeds), "binary_success_threshold": threshold,
        "source_cases_sha256": hashlib.sha256(cases_path.read_bytes()).hexdigest(),
        "verifier_b_loaded_only_in_this_post_generation_step": True,
    }
    write_result(manifest, resolve(cfg["outputs"]["score_manifest_json"]), args.config)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
