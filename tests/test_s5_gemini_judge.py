import json
from pathlib import Path

import pytest

from src.eval.gemini_judge import (
    INTERACTIONS_URL, GeminiJudge, GeminiJudgeError, interaction_request,
    interaction_text, parse_structured_response, validate_payload,
)


class Response:
    status_code = 200
    text = ""

    def json(self):
        return {
            "id": "r1", "model": "gemma-4-26b-a4b-it", "status": "completed",
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
        assert kwargs["json"]["model"] == "gemma-4-26b-a4b-it"
        assert kwargs["json"]["generation_config"] == {
            "seed": 42, "thinking_level": "high", "max_output_tokens": 512,
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
        model="gemma-4-26b-a4b-it", prompt="p", seed=42,
        thinking_level="high", max_output_tokens=512,
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


def test_structured_response_accepts_one_valid_object_and_archives_prose_suffix():
    payload, suffix = parse_structured_response(
        '{"verdict":"PASS","target_fit_score":100,"feedback":""}\nআর কোনো মন্তব্য নেই।'
    )
    assert payload["verdict"] == "PASS"
    assert suffix == "আর কোনো মন্তব্য নেই।"
    with pytest.raises(GeminiJudgeError, match="multiple JSON"):
        parse_structured_response('{"verdict":"PASS"}\n{"verdict":"FAIL"}')


def test_call_is_archived_and_second_call_resumes(tmp_path: Path):
    session = Session()
    judge = GeminiJudge(
        model="gemma-4-26b-a4b-it", seed=42, thinking_level="high",
        archive_path=tmp_path / "g.jsonl",
        failure_archive_path=tmp_path / "failures.jsonl",
        max_output_tokens=512, transport_retry_attempts=3, requests_per_minute=30,
        tokens_per_minute=16000, requests_per_pacific_day=14400,
        safety_fraction=0.9,
        api_key="test", session=session,
    )
    first = judge.judge(key="k", prompt="p")
    second = judge.judge(key="k", prompt="p")
    assert first == second
    assert session.calls == 1
    assert first.verdict == "FAIL" and first.target_fit_score == 61


class IncompleteThenCompleteSession(Session):
    def post(self, *args, **kwargs):
        self.calls += 1
        if self.calls == 1:
            class IncompleteResponse:
                status_code = 200
                text = ""

                @staticmethod
                def json():
                    return {"id": "bad", "model": "gemma-4-26b-a4b-it", "status": "incomplete"}
            return IncompleteResponse()
        return Response()


def test_incomplete_interaction_is_archived_then_retried_without_scoring_partial_output(tmp_path: Path):
    session = IncompleteThenCompleteSession()
    judge = GeminiJudge(
        model="gemma-4-26b-a4b-it", seed=42, thinking_level="high",
        archive_path=tmp_path / "g.jsonl", failure_archive_path=tmp_path / "failures.jsonl",
        max_output_tokens=512, transport_retry_attempts=3, requests_per_minute=30,
        tokens_per_minute=16000, requests_per_pacific_day=14400,
        safety_fraction=0.9, api_key="test", session=session,
    )
    judge._reserve_rate_slot = lambda: None
    verdict = judge.judge(key="k", prompt="p")
    assert verdict.verdict == "FAIL" and session.calls == 2
    failure = json.loads((tmp_path / "failures.jsonl").read_text(encoding="utf-8"))
    assert failure["reason"] == "interaction_status_incomplete"
    accepted = json.loads((tmp_path / "g.jsonl").read_text(encoding="utf-8"))
    assert accepted["transport_attempts"] == 2
    assert accepted["discarded_transport_failure_keys"] == [failure["key"]]
