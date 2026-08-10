"""Tests for the S3.5 symbolic scorer.

These pin the things that would silently corrupt a result rather than crash:
rule-7 gating on F1, no-stemming/no-normalisation on tokens, length-correction
in F3 and F6, and the family map staying in sync with the feature list.
"""

from __future__ import annotations

import math

import pytest

from src.symbolic import features as F


DANDI = "\u0964"
POS = "\u09ad\u09be\u09b2\u09cb"          # bhalo
INTENS = "\u0996\u09c1\u09ac"              # khub
CONN = "\u0995\u09bf\u09a8\u09cd\u09a4\u09c1"  # kintu


# --- rule 7 gating -------------------------------------------------------
def test_f1_is_off_by_default():
    """Rule 7 forbids TF-IDF in a result. F1 must never switch itself on."""
    assert F.FeatureSpec().enable_f1 is False


def test_f1_names_absent_when_disabled():
    names = F.feature_names(F.FeatureSpec(enable_f1=False))
    assert not any(n.startswith("idf_") for n in names)


def test_enabling_f1_without_idf_table_raises():
    """Silently producing zeros would be worse than crashing."""
    with pytest.raises(ValueError):
        F.extract("abc", F.FeatureSpec(enable_f1=True), idf=None)


# --- rule 7 / Bangla text rule: tokens are untouched ---------------------
def test_tokenizer_does_not_normalise_or_stem():
    text = f"{POS}i {POS}"
    assert F.tokenize(text) == [f"{POS}i", POS]


def test_two_unicode_forms_stay_distinct():
    """Open decision 13: the corpus holds two encodings of some words.

    Collapsing them here would silently change F6's type counts, so the
    tokenizer must keep them apart until Sabbir rules on decision 13.
    """
    a = "\u0985\u09ad\u09bf\u09a8\u09df"              # with U+09DF
    b = "\u0985\u09ad\u09bf\u09a8\u09af\u09bc"       # with U+09AF U+09BC
    assert a != b
    assert F.richness(f"{a} {b}")["guiraud"] == pytest.approx(2 / math.sqrt(2))


# --- F3 / F6: length must not sneak back in ------------------------------
def test_orthography_is_normalised_by_length():
    """Raw counts would re-encode length and smuggle F2 in under another name."""
    short = F.orthography("a! b")
    long = F.orthography("a! b c d e f g h")
    assert short["punct_per_tok"] > long["punct_per_tok"]


def test_guiraud_not_raw_ttr():
    """Raw TTR is 1.0 for any all-unique text regardless of length; Guiraud is not."""
    two = F.richness("a b")["guiraud"]
    eight = F.richness("a b c d e f g h")["guiraud"]
    assert two != pytest.approx(eight)
    assert eight == pytest.approx(8 / math.sqrt(8))


# --- F1 behaviour --------------------------------------------------------
def test_rarer_words_score_higher_idf():
    """The gaming argument for F1 depends on this direction holding."""
    docs = ["common word"] * 20 + ["rare"]
    idf = F.build_idf(docs)
    assert idf["rare"] > idf["common"]


def test_unseen_token_gets_max_idf():
    idf = F.build_idf(["a b", "a c"])
    stats = F.idf_stats("zzz", idf)
    assert stats["idf_mean"] == pytest.approx(max(idf.values()))


def test_idf_built_from_documents_not_tokens():
    """df counts documents, so repeating a word inside one doc must not matter."""
    assert F.build_idf(["x x x x"])["x"] == pytest.approx(F.build_idf(["x"])["x"])


# --- empty / degenerate input --------------------------------------------
@pytest.mark.parametrize("fn", [F.length_shape, F.orthography, F.connectives,
                                F.sentiment_fraction, F.richness])
def test_empty_text_is_finite(fn):
    """A NaN inside a generation loop is invisible until it poisons a score."""
    for v in fn("").values():
        assert math.isfinite(v)


def test_all_features_finite_on_empty():
    vals = F.extract("", F.FeatureSpec(enable_f1=False))
    assert all(math.isfinite(v) for v in vals.values())


# --- family map stays in sync -------------------------------------------
def test_every_feature_has_a_family():
    from src.symbolic.s35_scorer import FAMILY
    for name in F.feature_names(F.FeatureSpec(enable_f1=True)):
        assert name in FAMILY, f"{name} has no pre-registered family"


def test_gameable_families_are_the_registered_four():
    """F2-F5 are registered gameable in advance; F1 and F6 are not."""
    from src.symbolic.s35_scorer import GAMEABLE
    assert GAMEABLE == {"F2_length", "F3_ortho", "F4_connective", "F5_sentiment"}


# --- lexicon sanity ------------------------------------------------------
def test_sentiment_and_intensifier_fire():
    out = F.sentiment_fraction(f"{POS} {INTENS} x y")
    assert out["pos_frac"] > 0 and out["intensifier_frac"] > 0


def test_connective_fires():
    assert F.connectives(f"{CONN} x")["connective_frac"] == pytest.approx(0.5)


def test_dandi_termination_detected():
    assert F.orthography(f"x y{DANDI}")["ends_dandi"] == 1.0
    assert F.orthography("x y")["ends_dandi"] == 0.0


def test_matrix_column_order_matches_names():
    texts = [f"{POS} x", f"{INTENS} y z"]
    rows, names = F.extract_matrix(texts, F.FeatureSpec(enable_f1=False))
    assert len(rows) == 2 and all(len(r) == len(names) for r in rows)
    assert rows[0][names.index("n_tokens")] == 2.0
    assert rows[1][names.index("n_tokens")] == 3.0
