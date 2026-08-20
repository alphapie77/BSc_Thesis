"""Pure orchestration of the ten S5 conditions over injected call adapters."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass

from src.agents.prompts import render
from src.agents.reflector import failed_rules, render_feedback_prompt
from src.eval.s5_contract import largest_prefix_within_budget
from src.eval.s5_prompts import (
    gemini_judge_prompt,
    role_control_messages,
    self_critique_prompt,
)


def _field(obj, name, default=None):
    return getattr(obj, name, obj.get(name, default) if isinstance(obj, dict) else default)


def generation_view(gen) -> dict:
    return {
        "key": _field(gen, "key"),
        "text": _field(gen, "text"),
        "usage": _field(gen, "usage", {}),
        "seed": _field(gen, "seed"),
        "finish_reason": _field(gen, "finish_reason"),
    }


def token_cost(gen) -> int:
    usage = _field(gen, "usage", {}) or {}
    total = usage.get("total_tokens") or usage.get("totalTokenCount")
    if total is None:
        total = sum(
            int(usage.get(k, 0)) for k in (
                "prompt_tokens", "completion_tokens", "promptTokenCount",
                "candidatesTokenCount", "thoughtsTokenCount",
            )
        )
    if int(total) <= 0:
        raise RuntimeError("generation has no positive realized token cost")
    return int(total)


def score_draft(critic, draft: str, target_level: int) -> dict:
    return {
        "neural_score": float(critic.neural(draft, target_level)),
        "symbolic_score": float(critic.symbolic(draft, target_level)),
    }


def run_verifier_loop(
    *, condition: str, initial_gen, plot: str, plot_id: str, target_level: int,
    arm: str, initial_retrieval, researcher, critic, call_fn, gate: str,
    tau: float, symbolic_feedback: bool, max_attempts: int = 3,
) -> dict:
    """Rows 4–6. Same Reflector call count; only diagnostics and gate vary."""
    attempts = []
    logical_generations = [initial_gen]
    gen = initial_gen
    retrieval = initial_retrieval
    feedback = None
    for attempt in range(1, max_attempts + 1):
        scores = score_draft(critic, _field(gen, "text"), target_level)
        gate_score = scores[f"{gate}_score"]
        attempts.append({
            "attempt": attempt,
            "generation": generation_view(gen),
            **scores,
            "gate": gate,
            "gate_score": gate_score,
            "verdict": "PASS" if gate_score >= tau else "FAIL",
            "retrieved_ids": list(retrieval.review_ids),
            "feedback": feedback,
        })
        if gate_score >= tau:
            emitted = attempts[-1]
            break
        if attempt == max_attempts:
            emitted = max(attempts, key=lambda x: (x["gate_score"], -x["attempt"]))
            break
        rules = failed_rules(critic, _field(gen, "text"), target_level) if symbolic_feedback else []
        feedback_prompt = render_feedback_prompt(
            _field(gen, "text"), target_level, rules, arm=arm
        )
        feedback_gen = call_fn(
            condition=condition,
            call_role="reflector_symbolic" if symbolic_feedback else "reflector_generic",
            call_index=attempt,
            prompt=feedback_prompt,
            attempt=attempt,
        )
        logical_generations.append(feedback_gen)
        feedback = _field(feedback_gen, "text")
        keywords = [r.feature for r in rules] if symbolic_feedback else None
        retrieval = researcher.retrieve(
            plot, target_level, feedback_keywords=keywords,
            previous_ids=tuple(attempts[-1]["retrieved_ids"]),
        )
        retry_prompt = render(
            plot=plot, target_level=target_level, arm=arm,
            exemplars=retrieval.texts,
            previous_draft=_field(gen, "text"), feedback=feedback,
            length_controlled=True,
        )
        gen = call_fn(
            condition=condition, call_role="writer_retry",
            call_index=attempt + 1, prompt=retry_prompt, attempt=attempt + 1,
        )
        logical_generations.append(gen)
    return {
        "condition": condition,
        "attempts": attempts,
        "emitted": emitted,
        "gave_up": all(a["verdict"] == "FAIL" for a in attempts),
        "logical_generator_calls": len(logical_generations),
        "logical_generator_tokens": sum(token_cost(x) for x in logical_generations),
    }


def run_role_controls(
    *, initial_gen, base_prompt: str, plot_id: str, target_level: int, call_fn,
) -> tuple[dict, dict]:
    critique_gen = call_fn(
        condition="shared_self_critique", call_role="critique", call_index=1,
        prompt=self_critique_prompt(
            base_prompt=base_prompt, draft=_field(initial_gen, "text"),
            target_level=target_level,
        ), attempt=1,
    )
    critique = _field(critique_gen, "text")
    outputs = []
    for condition, role in (
        ("intrinsic_self_critique", "assistant"),
        ("external_role_self_critique", "user"),
    ):
        revised = call_fn(
            condition=condition, call_role="revision", call_index=1,
            sampling_group="shared_role_revision",
            messages=role_control_messages(
                base_prompt=base_prompt, draft=_field(initial_gen, "text"),
                critique=critique, role=role,
            ), attempt=2,
        )
        outputs.append({
            "condition": condition,
            "initial_generation": generation_view(initial_gen),
            "critique_generation": generation_view(critique_gen),
            "critique_role": role,
            "emitted": generation_view(revised),
            "logical_generator_calls": 3,
            "logical_generator_tokens": sum(
                token_cost(x) for x in (initial_gen, critique_gen, revised)
            ),
        })
    return outputs[0], outputs[1]


def run_gemini_loop(
    *, condition: str, initial_gen, base_prompt: str, plot: str, plot_id: str,
    target_level: int, rag_texts: tuple[str, ...], arm: str, call_fn, gemini,
    judge_key_fn, max_attempts: int = 3,
) -> dict:
    attempts, logical_generations = [], [initial_gen]
    gen = initial_gen
    feedback = None
    for attempt in range(1, max_attempts + 1):
        verdict = gemini.judge(
            key=judge_key_fn(attempt),
            prompt=gemini_judge_prompt(
                plot=plot, draft=_field(gen, "text"),
                target_level=target_level, arm=arm,
            ),
        )
        attempts.append({
            "attempt": attempt,
            "generation": generation_view(gen),
            "judge": {
                "key": verdict.key, "verdict": verdict.verdict,
                "target_fit_score": verdict.target_fit_score,
                "feedback": verdict.feedback, "usage": verdict.usage,
                "model_version": verdict.model_version,
            },
        })
        if verdict.verdict == "PASS":
            emitted = attempts[-1]
            break
        if attempt == max_attempts:
            emitted = max(
                attempts,
                key=lambda x: (x["judge"]["target_fit_score"], -x["attempt"]),
            )
            break
        feedback = verdict.feedback
        prompt = render(
            plot=plot, target_level=target_level, arm=arm,
            exemplars=rag_texts, previous_draft=_field(gen, "text"),
            feedback=feedback, length_controlled=True,
        )
        gen = call_fn(
            condition=condition, call_role="writer_retry",
            call_index=attempt + 1, prompt=prompt, attempt=attempt + 1,
        )
        logical_generations.append(gen)
    return {
        "condition": condition,
        "attempts": attempts,
        "emitted": emitted,
        "gave_up": all(a["judge"]["verdict"] == "FAIL" for a in attempts),
        "logical_generator_calls": len(logical_generations),
        "logical_generator_tokens": sum(token_cost(x) for x in logical_generations),
        "logical_judge_calls": len(attempts),
    }


def run_resampling(
    *, initial_gen, rag_prompt: str, target_level: int, critic, call_fn,
    row6_token_budget: int, max_candidates: int = 5,
) -> dict:
    candidates = [initial_gen]
    for index in range(2, max_candidates + 1):
        candidates.append(call_fn(
            condition="blind_resampling", call_role="candidate",
            call_index=index, prompt=rag_prompt, attempt=index,
        ))
    costs = [token_cost(x) for x in candidates]
    prefix = largest_prefix_within_budget(costs, budget=row6_token_budget)
    scored = [
        {"index": i, "generation": generation_view(gen),
         **score_draft(critic, _field(gen, "text"), target_level)}
        for i, gen in enumerate(candidates, start=1)
    ]
    frontier = []
    for n in range(1, max_candidates + 1):
        best = max(scored[:n], key=lambda x: (x["neural_score"], -x["index"]))
        frontier.append({"prefix": n, "cumulative_tokens": sum(costs[:n]), "selected_index": best["index"]})
    emitted = max(scored[:prefix], key=lambda x: (x["neural_score"], -x["index"]))
    return {
        "condition": "blind_resampling", "candidates": scored,
        "prefix_frontier": frontier, "primary_prefix": prefix,
        "emitted": emitted, "row6_token_budget": row6_token_budget,
        "logical_generator_calls": prefix,
        "logical_generator_tokens": sum(costs[:prefix]),
    }
