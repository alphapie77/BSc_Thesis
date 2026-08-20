#!/usr/bin/env python3
"""Structured Gemini critic for S5 row 8, with append-only resume archive."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

from src.common.provenance import stamp
from src.common.secrets import require


SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["PASS", "FAIL"]},
        "target_fit_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "feedback": {"type": "string"},
    },
    "required": ["verdict", "target_fit_score", "feedback"],
}


class GeminiJudgeError(RuntimeError):
    pass


def structured_generation_config() -> dict:
    """Return the legacy generateContent-compatible structured-output config.

    The v1beta ``responseSchema`` field accepts an OpenAPI subset and rejected
    ``additionalProperties`` on the live 2026-08-20 endpoint. Exact-key
    enforcement remains in :func:`validate_payload`, after JSON parsing.
    """
    return {
        "temperature": 0,
        "responseMimeType": "application/json",
        "responseSchema": SCHEMA,
    }


@dataclass(frozen=True)
class GeminiVerdict:
    verdict: str
    target_fit_score: int
    feedback: str
    usage: dict
    model_version: str | None
    response_id: str | None
    key: str


def _sentence_count(text: str) -> int:
    return sum(text.count(mark) for mark in ("।", ".", "?", "!"))


def validate_payload(payload: dict) -> tuple[str, int, str]:
    if set(payload) != {"verdict", "target_fit_score", "feedback"}:
        raise GeminiJudgeError("Gemini judge JSON has missing or extra fields")
    verdict = payload["verdict"]
    score = payload["target_fit_score"]
    feedback = payload["feedback"].strip()
    if verdict not in {"PASS", "FAIL"}:
        raise GeminiJudgeError(f"invalid judge verdict {verdict!r}")
    if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
        raise GeminiJudgeError("target_fit_score must be an integer in [0,100]")
    if verdict == "PASS" and feedback:
        raise GeminiJudgeError("PASS feedback must be empty")
    if verdict == "FAIL" and (not feedback or _sentence_count(feedback) > 2):
        raise GeminiJudgeError("FAIL feedback must be one or two Bangla sentences")
    return verdict, score, feedback


def load_archive(path: str | Path) -> dict[str, dict]:
    p = Path(path)
    if not p.exists():
        return {}
    rows = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
            rows[row["key"]] = row
        except Exception:
            continue
    return rows


class GeminiJudge:
    def __init__(
        self, *, model: str, archive_path: str | Path,
        api_key: str | None = None, session=None,
    ):
        if model != "gemini-2.5-flash":
            raise GeminiJudgeError("row 8 model must be stable gemini-2.5-flash")
        self.model = model
        self.archive_path = Path(archive_path)
        self.api_key = api_key or require("GOOGLE_API_KEY")
        if session is None:
            import requests
            session = requests
        self.session = session
        self.cached = load_archive(self.archive_path)

    def judge(self, *, key: str, prompt: str) -> GeminiVerdict:
        if key in self.cached:
            row = self.cached[key]
            verdict, score, feedback = validate_payload(row["parsed"])
            return GeminiVerdict(
                verdict, score, feedback, row.get("usage", {}),
                row.get("model_version"), row.get("response_id"), key,
            )
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        body = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": structured_generation_config(),
        }
        started = time.monotonic()
        response = self.session.post(url, json=body, timeout=120)
        if response.status_code != 200:
            raise GeminiJudgeError(
                f"Gemini HTTP {response.status_code}: {response.text[:300]}"
            )
        raw = response.json()
        try:
            text = raw["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(text)
            verdict, score, feedback = validate_payload(parsed)
        except Exception as exc:
            raise GeminiJudgeError(f"invalid structured Gemini response: {exc}") from exc
        row = {
            "key": key,
            "prompt": prompt,
            "parsed": parsed,
            "raw": raw,
            "usage": raw.get("usageMetadata", {}),
            "model": self.model,
            "model_version": raw.get("modelVersion"),
            "response_id": raw.get("responseId"),
            "latency_seconds": time.monotonic() - started,
            "provenance": stamp(config_path="configs/s5_main_bn.yaml"),
        }
        self.archive_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.archive_path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            fh.flush()
        self.cached[key] = row
        return GeminiVerdict(
            verdict, score, feedback, row["usage"], row["model_version"],
            row["response_id"], key,
        )
