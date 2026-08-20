#!/usr/bin/env python3
"""Structured Gemini critic for S5 row 8, with append-only resume archive."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

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

INTERACTIONS_URL = (
    "https://generativelanguage.googleapis.com/v1beta/interactions"
)
REQUIRED_MODEL = "gemma-4-26b-a4b-it"
REQUIRED_SEED = 42
REQUIRED_THINKING_LEVEL = "high"
PACIFIC = ZoneInfo("America/Los_Angeles")


class GeminiJudgeError(RuntimeError):
    pass


def interaction_request(
    *, model: str, prompt: str, seed: int, thinking_level: str,
    max_output_tokens: int,
) -> dict:
    """Return the Gemini-3 Interactions structured-output request."""
    return {
        "model": model,
        "input": prompt,
        "response_format": {
            "type": "text",
            "mime_type": "application/json",
            "schema": SCHEMA,
        },
        "generation_config": {
            "seed": seed,
            "thinking_level": thinking_level,
            "max_output_tokens": max_output_tokens,
        },
    }


def interaction_text(raw: dict) -> str:
    """Extract the sole text payload from a completed Interaction response."""
    if raw.get("status") != "completed":
        raise GeminiJudgeError(
            f"Gemini interaction status is {raw.get('status')!r}, not completed"
        )
    texts = [
        part["text"]
        for step in raw.get("steps", [])
        if step.get("type") == "model_output"
        for part in step.get("content", [])
        if part.get("type") == "text" and isinstance(part.get("text"), str)
    ]
    if len(texts) != 1 or not texts[0].strip():
        raise GeminiJudgeError(
            f"expected one Gemini model-output text part, found {len(texts)}"
        )
    return texts[0]


def parse_structured_response(text: str) -> tuple[dict, str]:
    """Decode one JSON object and losslessly retain any non-JSON suffix.

    Gemma's Interactions structured-output mode can occasionally append prose
    after an otherwise valid object.  The verdict may be used only when the
    leading object passes the frozen schema below; the suffix is retained in
    the append-only archive for audit.  A second JSON value is ambiguous and
    remains a hard failure.
    """
    decoder = json.JSONDecoder()
    start = len(text) - len(text.lstrip())
    try:
        payload, end = decoder.raw_decode(text, idx=start)
    except json.JSONDecodeError as exc:
        raise GeminiJudgeError(f"response does not begin with JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise GeminiJudgeError("structured Gemini response must begin with an object")
    suffix = text[end:].strip()
    if suffix:
        try:
            decoder.raw_decode(suffix)
        except json.JSONDecodeError:
            pass
        else:
            raise GeminiJudgeError("structured Gemini response contains multiple JSON values")
    return payload, suffix


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
        self, *, model: str, seed: int, thinking_level: str,
        archive_path: str | Path,
        max_output_tokens: int,
        requests_per_minute: int,
        tokens_per_minute: int,
        requests_per_pacific_day: int,
        safety_fraction: float,
        api_key: str | None = None, session=None,
    ):
        if model != REQUIRED_MODEL:
            raise GeminiJudgeError(f"row 8 model must be stable {REQUIRED_MODEL}")
        if seed != REQUIRED_SEED:
            raise GeminiJudgeError(f"row 8 seed must be {REQUIRED_SEED}")
        if thinking_level != REQUIRED_THINKING_LEVEL:
            raise GeminiJudgeError(
                f"row 8 thinking level must be {REQUIRED_THINKING_LEVEL}"
            )
        self.model = model
        self.seed = seed
        self.thinking_level = thinking_level
        if not 128 <= max_output_tokens <= 1024:
            raise GeminiJudgeError("judge max_output_tokens must be in [128,1024]")
        self.max_output_tokens = int(max_output_tokens)
        if requests_per_minute != 30 or tokens_per_minute != 16000:
            raise GeminiJudgeError("Gemma-4 limits must match AI Studio: 30 RPM, 16K TPM")
        if requests_per_pacific_day != 14400:
            raise GeminiJudgeError("Gemma-4 daily limit must match AI Studio: 14.4K RPD")
        if not 0.5 <= safety_fraction < 1.0:
            raise GeminiJudgeError("rate-limit safety fraction must be in [0.5,1.0)")
        self.requests_per_minute = int(requests_per_minute)
        self.tokens_per_minute = int(tokens_per_minute)
        self.requests_per_pacific_day = int(requests_per_pacific_day)
        self.safety_fraction = float(safety_fraction)
        self.safe_rpm = max(1, int(self.requests_per_minute * self.safety_fraction))
        self.safe_tpm = max(1, int(self.tokens_per_minute * self.safety_fraction))
        self.safe_rpd = max(1, int(self.requests_per_pacific_day * self.safety_fraction))
        self.archive_path = Path(archive_path)
        self.api_key = api_key or require("GOOGLE_API_KEY")
        if session is None:
            import requests
            session = requests
        self.session = session
        self.cached = load_archive(self.archive_path)
        self._last_request_epoch = self._latest_request_epoch()

    @staticmethod
    def _row_timestamp(row: dict) -> datetime | None:
        value = row.get("provenance", {}).get("timestamp_utc")
        if not isinstance(value, str):
            return None
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    def _latest_request_epoch(self) -> float | None:
        timestamps = [
            parsed.timestamp()
            for row in self.cached.values()
            if (parsed := self._row_timestamp(row)) is not None
        ]
        return max(timestamps, default=None)

    def _requests_today(self) -> int:
        today = datetime.now(timezone.utc).astimezone(PACIFIC).date()
        return sum(
            1 for row in self.cached.values()
            if (parsed := self._row_timestamp(row)) is not None
            and parsed.astimezone(PACIFIC).date() == today
        )

    @staticmethod
    def _row_tokens(row: dict) -> int:
        usage = row.get("usage", {})
        for key in ("total_tokens", "totalTokenCount"):
            value = usage.get(key)
            if isinstance(value, int) and value >= 0:
                return value
        input_tokens = usage.get("total_input_tokens", 0)
        output_tokens = usage.get("total_output_tokens", 0)
        if all(isinstance(x, int) and x >= 0 for x in (input_tokens, output_tokens)):
            return input_tokens + output_tokens
        return 0

    def _recent_usage(self, now_epoch: float) -> tuple[int, int, float | None]:
        recent = []
        for row in self.cached.values():
            parsed = self._row_timestamp(row)
            if parsed is None:
                continue
            epoch = parsed.timestamp()
            if 0 <= now_epoch - epoch < 60:
                recent.append((epoch, self._row_tokens(row)))
        return (
            len(recent), sum(tokens for _, tokens in recent),
            min((epoch for epoch, _ in recent), default=None),
        )

    def _reserve_rate_slot(self) -> None:
        used = self._requests_today()
        if used >= self.safe_rpd:
            raise GeminiJudgeError(
                f"local safety cap reached: {used}/"
                f"{self.safe_rpd} Gemma requests on the "
                "current Pacific day; resume after midnight Pacific"
            )
        while True:
            now = time.time()
            recent_requests, recent_tokens, oldest = self._recent_usage(now)
            request_full = recent_requests >= self.safe_rpm
            # Reserve 1,500 tokens for the next request. The realized usage is
            # archived and drives later slots; 1,500 exceeds the 937-token
            # observed Gemini-3.6 smoke call while leaving 10% provider headroom.
            token_full = recent_tokens + 1500 > self.safe_tpm
            if not request_full and not token_full:
                break
            if oldest is None:
                raise GeminiJudgeError("rate limiter has no timestamp for recent usage")
            time.sleep(max(0.1, 60.1 - (now - oldest)))
        minimum_interval = 60.0 / self.safe_rpm
        if self._last_request_epoch is not None:
            remaining = minimum_interval - (time.time() - self._last_request_epoch)
            if remaining > 0:
                time.sleep(remaining)
        self._last_request_epoch = time.time()

    def judge(self, *, key: str, prompt: str) -> GeminiVerdict:
        if key in self.cached:
            row = self.cached[key]
            verdict, score, feedback = validate_payload(row["parsed"])
            return GeminiVerdict(
                verdict, score, feedback, row.get("usage", {}),
                row.get("model_version"), row.get("response_id"), key,
            )
        body = interaction_request(
            model=self.model, prompt=prompt, seed=self.seed,
            thinking_level=self.thinking_level,
            max_output_tokens=self.max_output_tokens,
        )
        self._reserve_rate_slot()
        started = time.monotonic()
        response = self.session.post(
            INTERACTIONS_URL,
            headers={"x-goog-api-key": self.api_key, "Content-Type": "application/json"},
            json=body,
            timeout=120,
        )
        if response.status_code != 200:
            raise GeminiJudgeError(
                f"Gemini HTTP {response.status_code}: {response.text[:300]}"
            )
        raw = response.json()
        try:
            text = interaction_text(raw)
            parsed, trailing_text = parse_structured_response(text)
            verdict, score, feedback = validate_payload(parsed)
        except Exception as exc:
            raise GeminiJudgeError(f"invalid structured Gemini response: {exc}") from exc
        row = {
            "key": key,
            "prompt": prompt,
            "parsed": parsed,
            "trailing_text": trailing_text,
            "raw": raw,
            "usage": raw.get("usage", {}),
            "model": self.model,
            "seed": self.seed,
            "thinking_level": self.thinking_level,
            "max_output_tokens": self.max_output_tokens,
            "model_version": raw.get("model"),
            "response_id": raw.get("id"),
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
