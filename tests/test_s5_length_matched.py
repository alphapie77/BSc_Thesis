import hashlib
from pathlib import Path

from src.eval.analyze_s5_length_matched_bn import emitted_text


ROOT = Path(__file__).resolve().parents[1]


def test_emitted_text_supports_simple_and_nested_generation():
    assert emitted_text({"result": {"emitted": {"text": "এক দুই"}}}) == "এক দুই"
    assert emitted_text({"result": {"emitted": {"generation": {"text": "তিন চার"}}}}) == "তিন চার"


def test_frozen_s5_inputs_have_registered_hashes():
    assert hashlib.sha256((ROOT / "results/s5_main_bn_cases.jsonl").read_bytes()).hexdigest() == (
        "816a631be36f7e0a5918eb0298f7dce0c62b195ec80f43c8873ed923f94b3fd3")
    assert hashlib.sha256((ROOT / "results/s5_main_bn_verifier_b_scores.jsonl").read_bytes()).hexdigest() == (
        "0a7de4b67fe41186d291cc15578401c21df4ae8fe378cf21c0f1c52385ca23f4")
