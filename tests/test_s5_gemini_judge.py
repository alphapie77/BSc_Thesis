import json
from pathlib import Path

import pytest

from src.eval.gemini_judge import (
    INTERACTIONS_URL, GeminiJudge, GeminiJudgeError, interaction_request,
    interaction_text, validate_payload,
)


class Response:
    status_code = 200
    text = ""

    def json(self):
        return {
            "id": "r1", "model": "gemini-3.6-flash", "status": "completed",
            "steps": [{"type": "model_output", "content": [{
                "type": "text", "text": json.dumps({
                    "verdict": "FAIL", "target_fit_score": 61,
                    "feedback": "আরও নির্দিষ্ট করে লেখো।",
                }, ensure_ascii=False),
            }]}],
            "usage": {"total_input_tokens": 10, "total_output_tokens": 8},
        }


class Session:
    def __init__(self):
        self.calls = 0

    def post(self, *args, **kwargs):
        self.calls += 1
        assert args[0] == INTERACTIONS_URL
        assert kwargs["headers"]["x-goog-api-key"] == "test"
        assert kwargs["json"]["model"] == "gemini-3.6-flash"
        assert kwargs["json"]["generation_config"] == {
            "seed": 42, "thinking_level": "medium",
        }
        assert "temperature" not in kwargs["json"]
        return Response()


def test_schema_validation_refuses_extra_fields_and_pass_feedback():
    assert validate_payload({"verdict": "PASS", "target_fit_score": 90, "feedback": ""})
    with pytest.raises(GeminiJudgeError):
        validate_payload({"verdict": "PASS", "target_fit_score": 90, "feedback": "না"})
    with pytest.raises(GeminiJudgeError):
        validate_payload({"verdict": "FAIL", "target_fit_score": 50, "feedback": "x", "extra": 1})


def test_interactions_transport_uses_structured_output_without_sampling_knobs():
    body = interaction_request(
        model="gemini-3.6-flash", prompt="p", seed=42,
        thinking_level="medium",
    )
    assert body["input"] == "p" and "temperature" not in body
    assert body["response_format"]["mime_type"] == "application/json"
    schema = body["response_format"]["schema"]
    assert "additionalProperties" not in schema
    assert set(schema["required"]) == {
        "verdict", "target_fit_score", "feedback",
    }


def test_interaction_text_requires_one_completed_model_output():
    raw = Response().json()
    assert json.loads(interaction_text(raw))["verdict"] == "FAIL"
    raw["status"] = "failed"
    with pytest.raises(GeminiJudgeError, match="not completed"):
        interaction_text(raw)


def test_call_is_archived_and_second_call_resumes(tmp_path: Path):
    session = Session()
    judge = GeminiJudge(
        model="gemini-3.6-flash", seed=42, thinking_level="medium",
        archive_path=tmp_path / "g.jsonl",
        api_key="test", session=session,
    )
    first = judge.judge(key="k", prompt="p")
    second = judge.judge(key="k", prompt="p")
    assert first == second
    assert session.calls == 1
    assert first.verdict == "FAIL" and first.target_fit_score == 61
