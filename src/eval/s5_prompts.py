"""Phase-5-only critic/control prompts; Writer base prompt remains centralized."""

from __future__ import annotations

from src.agents.prompts import load_definition
from src.eval.gemini_judge import FAIL_FEEDBACK_BY_TARGET


def self_critique_prompt(*, base_prompt: str, draft: str, target_level: int) -> str:
    return (
        f"{base_prompt}\n\nতোমার লেখা মন্তব্য:\n{draft.strip()}\n\n"
        f"মন্তব্যটি চাওয়া স্তর {target_level}-এর সঙ্গে কতটা মেলে তা সমালোচনা করো। "
        "এক বা দুইটি বাংলা বাক্যে শুধু কী বদলানো দরকার বলো; নতুন মন্তব্য লিখো না।"
    )


def role_control_messages(
    *, base_prompt: str, draft: str, critique: str, role: str
) -> list[dict]:
    """Place the same critique under a native Gemma assistant or user turn.

    Gemma-3 accepts only alternating user/model turns.  Both conditions therefore
    use the identical three-slot topology ``user, assistant, user``.  The shared
    critique is appended to the draft in the intrinsic condition and prepended
    to the revision request in the external condition.  No synthetic filler
    turn is introduced.
    """
    if role not in {"assistant", "user"}:
        raise ValueError("critique role must be assistant or user")
    critique_block = f"সমালোচনা:\n{critique}"
    revision = "সমালোচনাটি মেনে মন্তব্যটি সংশোধন করো। শুধু নতুন বাংলা মন্তব্যটি লেখো।"
    assistant_content = draft.strip()
    user_content = revision
    if role == "assistant":
        assistant_content = f"{assistant_content}\n\n{critique_block}"
    else:
        user_content = f"{critique_block}\n\n{revision}"
    return [
        {"role": "user", "content": base_prompt},
        {"role": "assistant", "content": assistant_content},
        {"role": "user", "content": user_content},
    ]


def gemini_judge_prompt(
    *, plot: str, draft: str, target_level: int, arm: str = "bn"
) -> str:
    definition = load_definition(arm)
    return (
        "তুমি একটি মূল্যায়নকারী; নতুন মন্তব্য লিখবে না। নিচের operational "
        "definition অনুযায়ী draft-টি requested level মেনে চলে কি না বিচার করো।\n\n"
        f"OPERATIONAL DEFINITION:\n{definition}\n\n"
        f"REQUESTED LEVEL: {target_level}\n\nPLOT:\n{plot.strip()}\n\n"
        f"DRAFT:\n{draft.strip()}\n\n"
        "শুধু schema-র JSON object দাও, অন্য কোনো লেখা নয়। "
        "PASS হলে feedback অবশ্যই খালি string। FAIL হলে feedback অবশ্যই হুবহু এই "
        f"একটি string: {FAIL_FEEDBACK_BY_TARGET[target_level]!r}। "
        "target_fit_score 0 থেকে 100-এর পূর্ণসংখ্যা।"
    )
