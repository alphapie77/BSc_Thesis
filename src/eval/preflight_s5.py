#!/usr/bin/env python3
"""CPU-only Phase-5 preflight; no eval text is generated or scored by B."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.prompts import render  # noqa: E402
from src.common.seed import set_seed  # noqa: E402
from src.eval.s5_contract import (  # noqa: E402
    CONDITIONS,
    REPLICATE_SEEDS,
    S5ContractError,
    load_eval_plots,
    select_static_examples,
    symbolic_scores_from_s4,
    threshold_for_acceptance_rate,
)
from src.eval.gemini_judge import (  # noqa: E402
    REQUIRED_MODEL, REQUIRED_SEED, REQUIRED_THINKING_LEVEL,
)
from src.verifier.split_access import _read_split_map, load_training_rows  # noqa: E402


def _must_exist(path: str, *, kind: str = "file") -> Path:
    p = Path(path)
    ok = p.is_dir() if kind == "dir" else p.is_file()
    if not ok:
        raise S5ContractError(f"required {kind} is missing: {p}")
    return p


def preflight(cfg: dict) -> dict:
    if tuple(cfg.get("conditions", ())) != CONDITIONS:
        raise S5ContractError("config condition order does not match the frozen registry")
    if tuple(cfg.get("replicate_seeds", ())) != REPLICATE_SEEDS:
        raise S5ContractError("replicate seeds must be exactly [42, 43, 44]")
    judge = cfg.get("gemini_judge", {})
    if judge.get("model") != REQUIRED_MODEL:
        raise S5ContractError(f"row 8 model must be {REQUIRED_MODEL}")
    if judge.get("transport") != "interactions_v1beta":
        raise S5ContractError("row 8 must use the Gemini Interactions v1beta transport")
    if "temperature" in judge:
        raise S5ContractError("Gemma 4 judge must not receive temperature")
    if judge.get("seed") != REQUIRED_SEED:
        raise S5ContractError(f"row 8 seed must be {REQUIRED_SEED}")
    if judge.get("thinking_level") != REQUIRED_THINKING_LEVEL:
        raise S5ContractError(
            f"row 8 thinking level must be {REQUIRED_THINKING_LEVEL}"
        )
    if int(judge.get("max_output_tokens", 0)) != 512:
        raise S5ContractError("Gemma-4 judge max_output_tokens must be exactly 512")
    if int(judge.get("transport_retry_attempts", 0)) != 3:
        raise S5ContractError("Gemma-4 incomplete-response retry budget must be exactly 3")
    observed_limits = (
        int(judge.get("requests_per_minute", 0)),
        int(judge.get("tokens_per_minute", 0)),
        int(judge.get("requests_per_pacific_day", 0)),
    )
    if observed_limits != (30, 16000, 14400):
        raise S5ContractError("Gemma-4 limits must match AI Studio: 30/16000/14400")
    if not 0.5 <= float(judge.get("safety_fraction", 0)) < 1.0:
        raise S5ContractError("Gemma-4 safety fraction must be in [0.5,1.0)")
    sample = cfg["sample"]
    if sample != {
        "split": "eval", "n_plots": 90, "levels": [0, 1],
        "prompt_arm": "bn", "length_controlled": True,
    }:
        raise S5ContractError("Bangla Phase-5 sample surface has drifted")

    inputs = cfg["inputs"]
    for key in (
        "plots_csv", "split_map", "k2_assignments", "cleaned_csv",
        "s4_scores_csv", "verifier_a", "symbolic_scorer", "rag_manifest",
    ):
        _must_exist(inputs[key])
    _must_exist(cfg["rag"]["persist_dir"], kind="dir")

    plots = load_eval_plots(inputs["plots_csv"], expected_n=sample["n_plots"])
    rows, dev = load_training_rows(
        "A",
        split_map=inputs["split_map"],
        k2_assignments=inputs["k2_assignments"],
        cleaned_csv=inputs["cleaned_csv"],
        hold_out_dev=False,
    )
    if dev is not None:  # defensive: row 2 and RAG share the full registered R1 pool
        raise S5ContractError("unexpected dev subtraction from the static/RAG pool")
    static_schedules = {}
    for replicate_seed in REPLICATE_SEEDS:
        for plot in plots:
            for level in sample["levels"]:
                key = f"{replicate_seed}|{plot.plot_id}|L{level}"
                static_schedules[key] = select_static_examples(
                    rows,
                    per_level=int(cfg["static_few_shot"]["per_level"]),
                    seed=int(cfg["static_few_shot"]["selection_seed"]),
                    instance_key=key,
                )
    static = static_schedules[f"42|{plots[0].plot_id}|L0"]
    split = _read_split_map(inputs["split_map"])
    if set(static.review_ids) & (set(split["R2"]) | set(split["G"])):
        raise S5ContractError("R2 or G reached the static few-shot prompt")

    scores = symbolic_scores_from_s4(inputs["s4_scores_csv"])
    symbolic_tau, symbolic_passes = threshold_for_acceptance_rate(
        scores, target_rate=float(cfg["symbolic_gate"]["target_first_pass_rate"])
    )
    expected_tau = float(cfg["symbolic_gate"]["expected_tau"])
    if abs(symbolic_tau - expected_tau) > 1e-15:
        raise S5ContractError(
            f"symbolic tau recomputed as {symbolic_tau}, config says {expected_tau}"
        )
    if symbolic_passes != int(cfg["symbolic_gate"]["expected_passes"]):
        raise S5ContractError("symbolic acceptance-budget match has drifted")

    rag = json.loads(Path(inputs["rag_manifest"]).read_text(encoding="utf-8"))["result"]
    if rag.get("partition") != "R1" or rag.get("r2_ids_present") != 0 or rag.get("gold_ids_present") != 0:
        raise S5ContractError("the persisted RAG manifest does not prove an R1-only index")
    if rag.get("n_indexed") != len(rows):
        raise S5ContractError("static pool and persisted RAG index have different R1 sizes")

    # Render both base conditions now. This catches a missing definition marker,
    # target-level line, or strict exemplar-count failure before a GPU loads.
    example_plot = plots[0]
    zero = render(
        plot=example_plot.synopsis, target_level=0, arm="bn",
        length_controlled=True,
    )
    few = render(
        plot=example_plot.synopsis, target_level=0, arm="bn",
        exemplars=static.by_level[0], length_controlled=True,
    )
    if zero == few or any(t in zero for t in static.texts):
        raise S5ContractError("zero-shot/static prompt separation failed")

    per_replicate = len(plots) * len(sample["levels"]) * len(CONDITIONS)
    return {
        "status": "READY_NO_GENERATION",
        "conditions": list(CONDITIONS),
        "replicate_seeds": list(REPLICATE_SEEDS),
        "eval_plots": len(plots),
        "levels": sample["levels"],
        "condition_cases_per_language_per_replicate": per_replicate,
        "condition_cases_per_language": per_replicate * len(REPLICATE_SEEDS),
        "static_schedule_cases": len(static_schedules),
        "static_schedule_digest": __import__("hashlib").sha256(
            "\n".join(
                f"{key}:{','.join(value.review_ids)}"
                for key, value in sorted(static_schedules.items())
            ).encode("utf-8")
        ).hexdigest(),
        "sample_static_example_ids": list(static.review_ids),
        "static_counts": {str(k): len(v) for k, v in static.by_level.items()},
        "symbolic_tau": symbolic_tau,
        "symbolic_dev_passes": symbolic_passes,
        "symbolic_dev_cases": len(scores),
        "rag_n_indexed": rag["n_indexed"],
        "gemini_model": judge["model"],
        "gemini_transport": judge["transport"],
        "gemini_seed": judge["seed"],
        "gemini_thinking_level": judge["thinking_level"],
        "judge_max_output_tokens": judge["max_output_tokens"],
        "judge_transport_retry_attempts": judge["transport_retry_attempts"],
        "judge_rate_limits": {
            "rpm": judge["requests_per_minute"],
            "tpm": judge["tokens_per_minute"],
            "rpd": judge["requests_per_pacific_day"],
            "safety_fraction": judge["safety_fraction"],
        },
        "verifier_b_loaded": False,
        "sample_prompt_chars": {"zero_shot": len(zero), "static_few_shot": len(few)},
    }


def main() -> int:
    set_seed()  # inviolable global-seed rule; first action in the entry point
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s5_main_bn.yaml")
    args = ap.parse_args()
    with open(args.config, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    print(json.dumps(preflight(cfg), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
