from __future__ import annotations

from src.demo.service import LiveGemmaWriter, PlotFaithfulnessJudge


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


def test_ready_initializes_artifacts_without_verifier_b(monkeypatch):
    from src.demo import api

    class _Demo:
        cfg = {"rag": {"collection": "reviews_r1"}}

    monkeypatch.setattr(api, "service", lambda: _Demo())
    assert api.ready() == {
        "status": "ready",
        "backend_initialized": True,
        "verifier_b_loaded": False,
        "rag": "reviews_r1",
    }


def test_demo_config_keeps_verifier_b_out():
    import yaml

    cfg = yaml.safe_load(open("configs/demo.yaml", encoding="utf-8"))
    assert "verifier_b" not in str(cfg).lower()
    assert cfg["rag"]["top_k"] == 10
    assert cfg["verifier"]["tau"] == 0.4384071
    assert cfg["privacy"]["persist_user_plots"] is False


class _FaithResponse:
    status_code = 200

    @staticmethod
    def json():
        return {
            "id": "faith-demo",
            "model": "gemma-4-31b-it",
            "status": "completed",
            "steps": [{
                "type": "model_output",
                "content": [{"type": "text", "text": (
                    '{"verdict":"SUPPORTED","support_score":96,'
                    '"explanation":"উল্লেখটি প্লটে আছে।","unsupported_claims":[]}'
                )}],
            }],
        }


class _FaithSession(_Session):
    def post(self, url, *, headers, json, timeout):
        self.calls.append((url, headers, json, timeout))
        return _FaithResponse()


def test_plot_faithfulness_check_is_source_bounded_and_structured(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "test-secret-not-written")
    session = _FaithSession()
    judge = PlotFaithfulnessJudge({
        "model": "gemma-4-31b-it",
        "seed": 42,
        "thinking_level": "minimal",
        "max_output_tokens": 220,
        "request_timeout_seconds": 120,
    }, session=session)
    result = judge.evaluate(
        plot="রাশেদ সত্য প্রকাশ করে।",
        response_text="রাশেদের সত্য প্রকাশের দৃশ্যটি ভালো লেগেছে।",
    )
    assert result["status"] == "supported"
    assert result["support_score"] == 96
    body = session.calls[0][2]
    assert "PLOT:\nরাশেদ সত্য প্রকাশ করে।" in body["input"]
    assert body["response_format"]["mime_type"] == "application/json"
    assert body["model"] == "gemma-4-31b-it"
    assert "test-secret-not-written" not in str(body)
