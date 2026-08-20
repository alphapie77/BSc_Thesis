from src.eval.s5_contract import assert_identical_critique_bytes
from src.eval.s5_prompts import gemini_judge_prompt, role_control_messages


def test_role_control_changes_only_critique_role():
    kw = {"base_prompt": "base", "draft": "draft", "critique": "একই bytes"}
    intrinsic = role_control_messages(**kw, role="assistant")
    external = role_control_messages(**kw, role="user")
    assert len(intrinsic) == len(external)
    for i, (a, b) in enumerate(zip(intrinsic, external)):
        assert a["content"] == b["content"]
        if i == 3:
            assert (a["role"], b["role"]) == ("assistant", "user")
        else:
            assert a["role"] == b["role"]
    assert_identical_critique_bytes(intrinsic[3]["content"], external[3]["content"])


def test_gemini_prompt_contains_exact_case_material():
    prompt = gemini_judge_prompt(plot="কাহিনি", draft="মন্তব্য", target_level=1)
    assert "কাহিনি" in prompt and "মন্তব্য" in prompt
    assert "REQUESTED LEVEL: 1" in prompt
    assert "Verifier-A" not in prompt and "Verifier-B" not in prompt
