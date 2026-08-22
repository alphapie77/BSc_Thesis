from src.eval.analyze_s5_length_matched_bn import emitted_text


def test_emitted_text_supports_simple_and_nested_generation():
    assert emitted_text({"result": {"emitted": {"text": "এক দুই"}}}) == "এক দুই"
    assert emitted_text({"result": {"emitted": {"generation": {"text": "তিন চার"}}}}) == "তিন চার"

