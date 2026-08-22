import pytest

from src.eval.analyze_s5_diversity_realism_bn import distinct, js_discrete, ngrams


def test_ngram_and_distinct_preserve_whitespace_tokens_without_normalising_bangla():
    assert ngrams(["আমি", "ভালো"], 2) == [("আমি", "ভালো")]
    assert distinct(["আমি ভালো", "আমি ভালো"], 1) == pytest.approx(.5)
    assert distinct(["আমি ভালো", "আমি ভালো"], 2) == pytest.approx(.5)


def test_exact_discrete_js_is_symmetric_and_zero_for_identical_lengths():
    assert js_discrete([1, 2, 2], [1, 2, 2]) == pytest.approx(0)
    assert js_discrete([1, 1], [2, 2]) == pytest.approx(1)
    assert js_discrete([1, 2], [2, 3]) == pytest.approx(js_discrete([2, 3], [1, 2]))
