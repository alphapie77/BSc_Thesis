#!/usr/bin/env python3
"""Resumable Bangla Phase-5 generation runner. Verifier-B is absent by design."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.critic import Critic  # noqa: E402
from src.agents.prompts import render  # noqa: E402
from src.agents.researcher import Researcher  # noqa: E402
from src.common.provenance import stamp  # noqa: E402
from src.common.seed import set_seed  # noqa: E402
from src.eval.gemini_judge import GeminiJudge  # noqa: E402
from src.eval.preflight_s5 import preflight  # noqa: E402
from src.eval.s5_contract import (  # noqa: E402
    CONDITIONS, REPLICATE_SEEDS, generation_key, load_eval_plots,
    sampling_seed, select_static_examples,
)
from src.eval.s5_engine import (  # noqa: E402
    generation_view, run_gemini_loop, run_resampling, run_role_controls,
    run_verifier_loop, score_draft, token_cost,
)
from src.verifier.split_access import load_training_rows  # noqa: E402


def _jsonl_by_key(path: str | Path) -> dict[str, dict]:
    p = Path(path)
    if not p.exists():
        return {}
    out = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
            out[row["key"]] = row
        except Exception:
            continue
    return out


def _case_key(seed: int, plot_id: str, level: int, condition: str) -> str:
    return f"S5BN|s{seed}|{plot_id}|L{level}|{condition}"


def _append_case(path: str | Path, row: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        fh.flush()


class CallAdapter:
    def __init__(self, writer, archive: dict[str, dict], *, replicate_seed: int,
                 plot_id: str, target_level: int, arm: str, model: str):
        self.writer = writer
        self.archive = archive
        self.replicate_seed = replicate_seed
        self.plot_id = plot_id
        self.target_level = target_level
        self.arm = arm
        self.model = model

    def __call__(
        self, *, condition: str, call_role: str, call_index: int,
        attempt: int, prompt: str | None = None,
        messages: list[dict] | None = None, sampling_group: str | None = None,
    ):
        key = generation_key(
            condition=condition, replicate_seed=self.replicate_seed,
            plot_id=self.plot_id, target_level=self.target_level,
            call_role=call_role, call_index=call_index, arm=self.arm,
            provider="local", model=self.model,
        )
        if key in self.archive:
            return SimpleNamespace(**self.archive[key])
        seed_key = key
        if sampling_group is not None:
            seed_key = generation_key(
                condition=sampling_group, replicate_seed=self.replicate_seed,
                plot_id=self.plot_id, target_level=self.target_level,
                call_role=call_role, call_index=call_index, arm=self.arm,
                provider="local", model=self.model,
            )
        common = dict(
            plot_id=self.plot_id, target_level=self.target_level,
            attempt=attempt, key=key, sample_seed=sampling_seed(seed_key),
            condition=condition, replicate_seed=self.replicate_seed,
            call_role=call_role,
        )
        if messages is not None:
            gen = self.writer.generate_messages(messages=messages, **common)
        else:
            gen = self.writer.generate(prompt=prompt, **common)
        self.archive[key] = vars(gen)
        return gen


def _simple_result(condition: str, gen, critic, level: int) -> dict:
    return {
        "condition": condition,
        "emitted": generation_view(gen),
        "final_scores": score_draft(critic, gen.text, level),
        "logical_generator_calls": 1,
        "logical_generator_tokens": token_cost(gen),
    }


def _emitted_text(result: dict) -> str:
    emitted = result["emitted"]
    if "generation" in emitted:
        return emitted["generation"]["text"]
    return emitted["text"]


def _attach_final_scores(result: dict, critic, level: int) -> dict:
    if "final_scores" not in result:
        result["final_scores"] = score_draft(critic, _emitted_text(result), level)
    return result


def main() -> int:
    set_seed()  # inviolable global-seed rule; first action in the entry point
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s5_main_bn.yaml")
    ap.add_argument("--model-path")
    ap.add_argument("--replicate-seed", type=int, choices=REPLICATE_SEEDS)
    ap.add_argument("--start", type=int, default=0, help="zero-based base-case offset")
    ap.add_argument("--limit", type=int, help="number of plot-level base cases")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    readiness = preflight(cfg)
    if args.dry_run:
        print(json.dumps(readiness, ensure_ascii=False, indent=2))
        print("Nothing generated, nothing written.")
        return 0
    if args.replicate_seed is None or not args.model_path:
        raise SystemExit("actual run requires --replicate-seed and --model-path")

    seed = args.replicate_seed
    inputs, sample, out = cfg["inputs"], cfg["sample"], cfg["outputs"]
    plots = load_eval_plots(inputs["plots_csv"], expected_n=sample["n_plots"])
    base_cases = [(p, int(level)) for p in plots for level in sample["levels"]]
    if args.start < 0:
        raise SystemExit("--start must be non-negative")
    if args.limit is not None:
        if args.limit < 1:
            raise SystemExit("--limit must be positive")
        base_cases = base_cases[args.start:args.start + args.limit]
    else:
        base_cases = base_cases[args.start:]

    rows, _ = load_training_rows(
        "A", split_map=inputs["split_map"],
        k2_assignments=inputs["k2_assignments"],
        cleaned_csv=inputs["cleaned_csv"], hold_out_dev=False,
    )
    # Credential failure must happen before LaBSE and the 12B Writer load.
    # Construction is network-free: the first request is made inside row 8.
    gemini = GeminiJudge(
        model=cfg["gemini_judge"]["model"],
        seed=int(cfg["gemini_judge"]["seed"]),
        thinking_level=cfg["gemini_judge"]["thinking_level"],
        archive_path=out["gemini_calls_jsonl"],
    )
    rag_cfg = cfg["rag"]
    researcher = Researcher(
        rag_cfg["persist_dir"], rag_cfg["collection"], rag_cfg["encoder"],
        device="cpu",
    )
    critic = Critic(
        verifier_a_path=inputs["verifier_a"],
        symbolic_path=inputs["symbolic_scorer"],
        required_sklearn_version=str(cfg["runtime"]["scikit_learn"]),
        encoder_device="cpu",
    )
    from src.agents.local_writer import LocalWriter
    writer_cfg = cfg["writer"]
    writer = LocalWriter(
        writer_cfg["model"], arm=sample["prompt_arm"],
        jsonl_path=out["calls_jsonl"], batch_size=int(writer_cfg["batch_size"]),
        quantization=writer_cfg["quantization"],
        max_new_tokens=int(writer_cfg["max_new_tokens"]),
        model_path=args.model_path,
    )
    call_archive = _jsonl_by_key(out["calls_jsonl"])
    completed = _jsonl_by_key(out["cases_jsonl"])
    total_rows = len(base_cases) * len(CONDITIONS)
    already = sum(
        _case_key(seed, p.plot_id, level, c) in completed
        for p, level in base_cases for c in CONDITIONS
    )
    print(f"S5 seed {seed}: {already}/{total_rows} condition-cases already complete")

    written = already
    for p, level in base_cases:
        wanted = {
            c for c in CONDITIONS
            if _case_key(seed, p.plot_id, level, c) not in completed
        }
        if not wanted:
            continue
        adapter = CallAdapter(
            writer, call_archive, replicate_seed=seed, plot_id=p.plot_id,
            target_level=level, arm=sample["prompt_arm"], model=writer_cfg["model"],
        )
        zero_prompt = render(
            plot=p.synopsis, target_level=level, arm=sample["prompt_arm"],
            length_controlled=True,
        )
        static = select_static_examples(
            rows, per_level=int(cfg["static_few_shot"]["per_level"]),
            seed=int(cfg["static_few_shot"]["selection_seed"]),
            instance_key=f"{seed}|{p.plot_id}|L{level}",
        )
        few_prompt = render(
            plot=p.synopsis, target_level=level, arm=sample["prompt_arm"],
            exemplars=static.by_level[level], length_controlled=True,
        )
        rag = researcher.retrieve(p.synopsis, level)
        rag_prompt = render(
            plot=p.synopsis, target_level=level, arm=sample["prompt_arm"],
            exemplars=rag.texts, length_controlled=True,
        )
        zero = adapter(
            condition="zero_shot", call_role="writer", call_index=1,
            prompt=zero_prompt, attempt=1,
        )
        few = adapter(
            condition="static_few_shot", call_role="writer", call_index=1,
            prompt=few_prompt, attempt=1,
        )
        initial = adapter(
            condition="shared_rag_initial", call_role="writer", call_index=1,
            prompt=rag_prompt, attempt=1,
        )
        results = {
            "zero_shot": _simple_result("zero_shot", zero, critic, level),
            "static_few_shot": _simple_result("static_few_shot", few, critic, level),
            "rag_only": _simple_result("rag_only", initial, critic, level),
        }
        results["rag_neural_loop"] = run_verifier_loop(
            condition="rag_neural_loop", initial_gen=initial, plot=p.synopsis,
            plot_id=p.plot_id, target_level=level, arm=sample["prompt_arm"],
            initial_retrieval=rag, researcher=researcher, critic=critic,
            call_fn=adapter, gate="neural", tau=float(cfg["neural_gate"]["tau"]),
            symbolic_feedback=False,
        )
        results["rag_symbolic_loop"] = run_verifier_loop(
            condition="rag_symbolic_loop", initial_gen=initial, plot=p.synopsis,
            plot_id=p.plot_id, target_level=level, arm=sample["prompt_arm"],
            initial_retrieval=rag, researcher=researcher, critic=critic,
            call_fn=adapter, gate="symbolic",
            tau=float(cfg["symbolic_gate"]["expected_tau"]),
            symbolic_feedback=True,
        )
        results["rag_neural_symbolic_feedback"] = run_verifier_loop(
            condition="rag_neural_symbolic_feedback", initial_gen=initial,
            plot=p.synopsis, plot_id=p.plot_id, target_level=level,
            arm=sample["prompt_arm"], initial_retrieval=rag,
            researcher=researcher, critic=critic, call_fn=adapter,
            gate="neural", tau=float(cfg["neural_gate"]["tau"]),
            symbolic_feedback=True,
        )
        role_a, role_b = run_role_controls(
            initial_gen=initial, base_prompt=rag_prompt, plot_id=p.plot_id,
            target_level=level, call_fn=adapter,
        )
        results["intrinsic_self_critique"] = role_a
        results["external_role_self_critique"] = role_b
        judge_model = cfg["gemini_judge"]["model"]
        results["gemini_judge_loop"] = run_gemini_loop(
            condition="gemini_judge_loop", initial_gen=initial,
            base_prompt=rag_prompt, plot=p.synopsis, plot_id=p.plot_id,
            target_level=level, rag_texts=rag.texts, arm=sample["prompt_arm"],
            call_fn=adapter, gemini=gemini,
            judge_key_fn=lambda attempt: generation_key(
                condition="gemini_judge_loop", replicate_seed=seed,
                plot_id=p.plot_id, target_level=level, call_role="judge",
                call_index=attempt, arm=sample["prompt_arm"],
                provider="gemini", model=judge_model,
            ),
        )
        results["blind_resampling"] = run_resampling(
            initial_gen=initial, rag_prompt=rag_prompt, target_level=level,
            critic=critic, call_fn=adapter,
            row6_token_budget=results["rag_neural_symbolic_feedback"]["logical_generator_tokens"],
            max_candidates=int(cfg["blind_resampling"]["max_candidates"]),
        )

        for condition in CONDITIONS:
            if condition not in wanted:
                continue
            result = _attach_final_scores(results[condition], critic, level)
            key = _case_key(seed, p.plot_id, level, condition)
            row = {
                "key": key, "plot_id": p.plot_id, "target_level": level,
                "language": "bn", "prompt_arm": sample["prompt_arm"],
                "replicate_seed": seed, "condition": condition,
                "result": result,
                "static_schedule_ids": list(static.review_ids) if condition == "static_few_shot" else None,
                "verifier_b_score": None,
                "provenance": stamp(args.config, {"stage": "generation", "verifier_b_loaded": False}),
            }
            _append_case(out["cases_jsonl"], row)
            completed[key] = row
            written += 1
            print(f"[{written}/{total_rows}] {p.plot_id} L{level} {condition}", flush=True)
    print(f"complete seed {seed}: {written}/{total_rows}; Verifier-B was never loaded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
