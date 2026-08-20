from src.eval.s5_contract import assert_identical_critique_bytes
from src.eval.s5_prompts import gemini_judge_prompt, role_control_messages


def test_role_control_uses_native_alternation_and_moves_exact_critique_bytes():
    kw = {"base_prompt": "base", "draft": "draft", "critique": "একই bytes"}
    intrinsic = role_control_messages(**kw, role="assistant")
    external = role_control_messages(**kw, role="user")
    assert [m["role"] for m in intrinsic] == ["user", "assistant", "user"]
    assert [m["role"] for m in external] == ["user", "assistant", "user"]
    assert intrinsic[0] == external[0]
    assert intrinsic[1]["content"].startswith("draft")
    assert external[1]["content"] == "draft"
    assert "একই bytes" in intrinsic[1]["content"]
    assert "একই bytes" not in intrinsic[2]["content"]
    assert "একই bytes" not in external[1]["content"]
    assert "একই bytes" in external[2]["content"]
    assert_identical_critique_bytes(kw["critique"], kw["critique"])
    revision = "সমালোচনাটি মেনে মন্তব্যটি সংশোধন করো। শুধু নতুন বাংলা মন্তব্যটি লেখো।"
    assert sum(revision in m["content"] for m in intrinsic) == 1
    assert sum(revision in m["content"] for m in external) == 1


def test_gemini_prompt_contains_exact_case_material():
    prompt = gemini_judge_prompt(plot="কাহিনি", draft="মন্তব্য", target_level=1)
    assert "কাহিনি" in prompt and "মন্তব্য" in prompt
    assert "REQUESTED LEVEL: 1" in prompt
    assert "Verifier-A" not in prompt and "Verifier-B" not in prompt
