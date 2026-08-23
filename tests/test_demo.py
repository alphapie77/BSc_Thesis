from __future__ import annotations

from src.demo.service import LiveGemmaWriter


class _Response:
    status_code = 200

    @staticmethod
    def json():
        return {
            "id": "interaction-demo",
            "model": "gemma-4-26b-a4b-it",
            "status": "completed",
            "steps": [{
                "type": "model_output",
                "content": [{"type": "text", "text": "গল্পটা বেশ ভালো লেগেছে।"}],
            }],
            "usage": {"total_tokens": 20},
        }


class _Session:
    def __init__(self):
        self.calls = []

    def post(self, url, *, headers, json, timeout):
        self.calls.append((url, headers, json, timeout))
        return _Response()


def test_live_writer_uses_interactions_without_persisting(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "test-secret-not-written")
    session = _Session()
    writer = LiveGemmaWriter({
        "model": "gemma-4-26b-a4b-it",
        "seed": 42,
        "thinking_level": "minimal",
        "max_output_tokens": 80,
        "request_timeout_seconds": 120,
    }, session=session)
    gen = writer.generate(
        prompt="বাংলায় লেখো", plot_id="LIVE-test", target_level=0, attempt=1,
    )
    assert gen.text == "গল্পটা বেশ ভালো লেগেছে।"
    assert gen.provider == "gemini"
    assert gen.provenance["standing"] == "live_demo_not_scientific_result"
    body = session.calls[0][2]
    assert body["model"] == "gemma-4-26b-a4b-it"
    assert body["generation_config"] == {
        "seed": 42, "thinking_level": "minimal", "max_output_tokens": 80,
    }
    assert "test-secret-not-written" not in str(body)


def test_demo_config_keeps_verifier_b_out():
    import yaml

    cfg = yaml.safe_load(open("configs/demo.yaml", encoding="utf-8"))
    assert "verifier_b" not in str(cfg).lower()
    assert cfg["rag"]["top_k"] == 10
    assert cfg["verifier"]["tau"] == 0.4384071
    assert cfg["privacy"]["persist_user_plots"] is False
