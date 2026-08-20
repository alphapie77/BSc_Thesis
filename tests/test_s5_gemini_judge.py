import json
from pathlib import Path

import pytest

from src.eval.gemini_judge import GeminiJudge, GeminiJudgeError, validate_payload


class Response:
    status_code = 200
    text = ""

    def json(self):
        return {
            "candidates": [{"content": {"parts": [{"text": json.dumps({
                "verdict": "FAIL", "target_fit_score": 61,
                "feedback": "আরও নির্দিষ্ট করে লেখো।",
            }, ensure_ascii=False)}]}}],
            "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 8},
            "modelVersion": "gemini-2.5-flash",
            "responseId": "r1",
        }


class Session:
    def __init__(self):
        self.calls = 0

    def post(self, *args, **kwargs):
        self.calls += 1
        assert kwargs["json"]["generationConfig"]["temperature"] == 0
        assert kwargs["json"]["generationConfig"]["responseMimeType"] == "application/json"
        return Response()


def test_schema_validation_refuses_extra_fields_and_pass_feedback():
    assert validate_payload({"verdict": "PASS", "target_fit_score": 90, "feedback": ""})
    with pytest.raises(GeminiJudgeError):
        validate_payload({"verdict": "PASS", "target_fit_score": 90, "feedback": "না"})
    with pytest.raises(GeminiJudgeError):
        validate_payload({"verdict": "FAIL", "target_fit_score": 50, "feedback": "x", "extra": 1})


def test_call_is_archived_and_second_call_resumes(tmp_path: Path):
    session = Session()
    judge = GeminiJudge(
        model="gemini-2.5-flash", archive_path=tmp_path / "g.jsonl",
        api_key="test", session=session,
    )
    first = judge.judge(key="k", prompt="p")
    second = judge.judge(key="k", prompt="p")
    assert first == second
    assert session.calls == 1
    assert first.verdict == "FAIL" and first.target_fit_score == 61
