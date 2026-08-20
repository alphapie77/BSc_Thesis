from dataclasses import dataclass

from src.agents.researcher import Retrieval
from src.eval.gemini_judge import GeminiVerdict
from src.eval.s5_engine import (
    run_gemini_loop, run_resampling, run_role_controls, run_verifier_loop,
)


@dataclass
class Gen:
    key: str
    text: str
    seed: int = 42
    finish_reason: str = "stop"
    usage: dict = None

    def __post_init__(self):
        if self.usage is None:
            self.usage = {"total_tokens": 10}


class Critic:
    _symbolic = None

    def neural(self, text, level):
        return float(text.split()[-1])

    def symbolic(self, text, level):
        return float(text.split()[-1])


class Researcher:
    def retrieve(self, *args, **kwargs):
        return Retrieval(tuple(f"id{i}" for i in range(10)), tuple(f"e{i}" for i in range(10)), "q", None)


def caller_factory(scores):
    calls = []

    def call_fn(**kw):
        calls.append(kw)
        score = scores.pop(0) if kw["call_role"].startswith("writer") or kw["call_role"] in {"candidate", "revision"} else 0.0
        return Gen(f"k{len(calls)}", f"draft {score}")
    return call_fn, calls


def test_neural_loop_generic_feedback_has_same_call_shape_and_stops():
    call_fn, calls = caller_factory([0.8])
    result = run_verifier_loop(
        condition="rag_neural_loop", initial_gen=Gen("i", "draft 0.1"),
        plot="p", plot_id="BN", target_level=0, arm="bn",
        initial_retrieval=Researcher().retrieve(), researcher=Researcher(),
        critic=Critic(), call_fn=call_fn, gate="neural", tau=0.5,
        symbolic_feedback=False,
    )
    assert result["emitted"]["attempt"] == 2
    assert [x["call_role"] for x in calls] == ["reflector_generic", "writer_retry"]
    assert result["logical_generator_calls"] == 3


def test_role_controls_share_critique_seed_and_use_valid_role_topology():
    call_fn, calls = caller_factory([0.4, 0.5])
    a, b = run_role_controls(
        initial_gen=Gen("i", "draft 0.2"), base_prompt="base",
        plot_id="BN", target_level=0, call_fn=call_fn,
    )
    assert a["critique_generation"]["key"] == b["critique_generation"]["key"]
    intrinsic, external = calls[1]["messages"], calls[2]["messages"]
    assert [m["role"] for m in intrinsic] == ["user", "assistant", "user"]
    assert [m["role"] for m in external] == ["user", "assistant", "user"]
    critique = "draft 0.0"
    assert critique in intrinsic[1]["content"] and critique not in intrinsic[2]["content"]
    assert critique not in external[1]["content"] and critique in external[2]["content"]
    assert calls[1]["sampling_group"] == calls[2]["sampling_group"] == "shared_role_revision"


class Judge:
    def __init__(self):
        self.n = 0

    def judge(self, *, key, prompt):
        self.n += 1
        verdict = "PASS" if self.n == 2 else "FAIL"
        return GeminiVerdict(verdict, 40 + self.n, "আরও ঠিক করো।" if verdict == "FAIL" else "", {}, "m", "r", key)


def test_gemini_loop_obeys_structured_verdict():
    call_fn, _ = caller_factory([0.7])
    out = run_gemini_loop(
        condition="gemma4_26b_a4b_judge_loop", initial_gen=Gen("i", "draft 0.2"),
        base_prompt="base", plot="p", plot_id="BN", target_level=0,
        rag_texts=tuple(f"e{i}" for i in range(10)), arm="bn",
        call_fn=call_fn, gemini=Judge(), judge_key_fn=lambda i: f"j{i}",
    )
    assert len(out["attempts"]) == 2 and out["emitted"]["attempt"] == 2


def test_resampling_matches_largest_realized_prefix_and_a_selects():
    call_fn, _ = caller_factory([0.2, 0.9, 0.3, 0.4])
    out = run_resampling(
        initial_gen=Gen("i", "draft 0.1"), rag_prompt="p", target_level=0,
        critic=Critic(), call_fn=call_fn, row6_token_budget=31,
    )
    assert out["primary_prefix"] == 3
    assert out["emitted"]["index"] == 3
    assert len(out["prefix_frontier"]) == 5
