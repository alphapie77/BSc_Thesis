import json
from pathlib import Path

import pytest

from src.eval.preflight_s5_kaggle import (
    KagglePreflightError, validate_gemini_api, validate_model_path,
    validate_role_templates,
)


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

    def json(self):
        return {
            "candidates": [{"content": {"parts": [{"text": json.dumps({
                "verdict": "PASS", "target_fit_score": 100, "feedback": ""
            })}]}}],
            "modelVersion": "gemini-2.5-flash",
        }


class Session:
    def post(self, url, **kwargs):
        assert "secret" in url
        return Response()


def test_gemini_runtime_gate_uses_the_registered_schema():
    out = validate_gemini_api(
        api_key="secret", model="gemini-2.5-flash", session=Session()
    )
    assert out["verdict"] == "PASS" and out["model_version"] == "gemini-2.5-flash"
