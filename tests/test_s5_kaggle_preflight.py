import json
from pathlib import Path

import pytest

from src.eval.preflight_s5_kaggle import (
    KagglePreflightError, validate_gemini_api, validate_model_path,
    validate_role_templates,
)
from src.eval.gemini_judge import FAIL_FEEDBACK_BY_TARGET


class Tokenizer:
    def apply_chat_template(self, messages, **kwargs):
        roles = [m["role"] for m in messages]
        if roles != ["user", "assistant", "user"]:
            raise ValueError(f"roles do not alternate: {roles}")
        return "|".join(f"{m['role']}:{m['content']}" for m in messages)


def test_role_sequences_render_and_preserve_one_critique():
    result = validate_role_templates(Tokenizer())
    assert result["intrinsic"] > 0 and result["external"] > 0


def test_model_path_requires_gemma3_and_real_weight_payload(tmp_path: Path):
    (tmp_path / "config.json").write_text(json.dumps({
        "model_type": "gemma3_text", "architectures": ["Gemma3ForCausalLM"]
    }), encoding="utf-8")
    (tmp_path / "tokenizer_config.json").write_text("{}", encoding="utf-8")
    (tmp_path / "model.safetensors").write_bytes(b"x" * 10)
    assert validate_model_path(tmp_path, min_weight_bytes=10)["weight_bytes"] == 10
    (tmp_path / "config.json").write_text('{"model_type":"bert"}', encoding="utf-8")
    with pytest.raises(KagglePreflightError, match="Gemma-3"):
        validate_model_path(tmp_path, min_weight_bytes=10)


class Response:
    status_code = 200
    text = ""

    def __init__(self, verdict="PASS"):
        self.verdict = verdict

    def json(self):
        feedback = "" if self.verdict == "PASS" else FAIL_FEEDBACK_BY_TARGET[0]
        return {
            "id": "r", "model": "gemma-4-26b-a4b-it", "status": "completed",
            "steps": [{"type": "model_output", "content": [{
                "type": "text", "text": json.dumps({
                    "verdict": self.verdict, "target_fit_score": 100, "feedback": feedback
                }),
            }]}],
        }


class Session:
    def __init__(self):
        self.calls = 0

    def post(self, url, **kwargs):
        self.calls += 1
        assert "secret" not in url
        assert kwargs["headers"]["x-goog-api-key"] == "secret"
        assert kwargs["json"]["generation_config"] == {
            "seed": 42, "thinking_level": "high", "max_output_tokens": 512,
        }
        schema = kwargs["json"]["response_format"]["schema"]
        assert "additionalProperties" not in schema
        return Response("PASS" if self.calls == 1 else "FAIL")


def test_gemini_runtime_gate_uses_the_registered_schema():
    out = validate_gemini_api(
        api_key="secret", model="gemma-4-26b-a4b-it", seed=42,
        thinking_level="high", max_output_tokens=512, session=Session()
    )
    assert [x["verdict"] for x in out["probes"]] == ["PASS", "FAIL"]
    assert out["model_version"] == "gemma-4-26b-a4b-it"
