"""Phase-5-only critic/control prompts; Writer base prompt remains centralized."""

from __future__ import annotations

from src.agents.prompts import load_definition


def self_critique_prompt(*, base_prompt: str, draft: str, target_level: int) -> str:
    return (
        f"{base_prompt}\n\nতোমার লেখা মন্তব্য:\n{draft.strip()}\n\n"
        f"মন্তব্যটি চাওয়া স্তর {target_level}-এর সঙ্গে কতটা মেলে তা সমালোচনা করো। "
        "এক বা দুইটি বাংলা বাক্যে শুধু কী বদলানো দরকার বলো; নতুন মন্তব্য লিখো না।"
    )


def role_control_messages(
    *, base_prompt: str, draft: str, critique: str, role: str
) -> list[dict]:
    """Only the critique message role differs between intrinsic/external rows."""
    if role not in {"assistant", "user"}:
        raise ValueError("critique role must be assistant or user")
    return [
        {"role": "user", "content": base_prompt},
        {"role": "assistant", "content": draft.strip()},
        {"role": "user", "content": "এখন একটি সমালোচনা দেওয়া হবে।"},
        {"role": role, "content": critique},
        {
            "role": "user",
            "content": "সমালোচনাটি মেনে মন্তব্যটি সংশোধন করো। শুধু নতুন বাংলা মন্তব্যটি লেখো।",
        },
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
        "PASS হলে feedback খালি রাখো। FAIL হলে সর্বোচ্চ দুইটি বাংলা বাক্যে "
        "নির্দিষ্ট সংশোধন বলো। target_fit_score 0 থেকে 100-এর পূর্ণসংখ্যা।"
    )
