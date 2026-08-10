"""S3.5 symbolic features -- six families, pre-registered 2026-08-11.

Read `docs/protocol.md` section "S3.5 pre-commitment" before changing anything here.
The families are fixed in that document; this file is only their translation
into code, and a family added here without a matching pre-registration entry is
a protocol violation, not a feature.

Two properties this module deliberately has:

* **No I/O and no state.** Every function takes text (and, for IDF, a
  pre-built table) and returns numbers. That makes the whole pool testable
  without the corpus, which matters because these features end up inside a
  generation loop where a silent NaN would be invisible.
* **Whitespace tokens only.** No stemming, no stopword removal, no
  normalisation of Bangla characters beyond splitting on whitespace
  (inviolable rules 7 and the Bangla-text rule in CLAUDE.md). The corpus has
  two Unicode encodings of several words (open decision 13) and they are
  deliberately NOT collapsed here either -- collapsing would silently change
  type counts in F6.

**Gameability is annotated per family, on purpose.** Mahmoud et al. (2026) show
presence-based reward criteria are the ones that get hacked, and section 4.2's Reflector
tells the Writer which rule failed. F2-F5 are therefore registered as gameable
in advance so that a gain arriving only through them is legible as such.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

#: Bangla sentence terminator (dandi). Counted, never stripped.
DANDI = "\u0964"

#: Latin-script characters -- present in a Bangla corpus as code-switching.
_LATIN = re.compile(r"[A-Za-z]")
_DIGIT = re.compile(r"[0-9\u09e6-\u09ef]")  # ASCII and Bangla digits
_PUNCT = re.compile(r"[!?,;:\-\u2014\u2013.\u0964]")

#: ---------------------------------------------------------------------------
#: Lexicons. PROVENANCE MATTERS AND IS STATED: these are the example terms given
#: in pipeline section 3.5, extended only where the extension is obvious inflection.
#: They are NOT a validated Bangla sentiment or discourse resource -- no such
#: resource was found that we could verify, and inventing one silently would be
#: worse than a short list with its limits declared. Reported in Ch.5 as a
#: limitation of F4/F5, which are in any case the gameable families.
#: ---------------------------------------------------------------------------
INTENSIFIERS = frozenset("\u0996\u09c1\u09ac \u09a6\u09be\u09b0\u09c1\u09a3 \u0985\u09b8\u09be\u09a7\u09be\u09b0\u09a3 \u09ad\u09c0\u09b7\u09a3 \u09ac\u09c7\u09b6 \u09b8\u09c7\u09b0\u09be \u09aa\u09c1\u09b0\u09cb".split())
POSITIVE = frozenset("\u09ad\u09be\u09b2\u09cb \u09b8\u09c1\u09a8\u09cd\u09a6\u09b0 \u0985\u09b8\u09be\u09a7\u09be\u09b0\u09a3 \u09b8\u09c7\u09b0\u09be \u09a6\u09be\u09b0\u09c1\u09a3 \u09ae\u09be\u09b0\u09be\u09a4\u09cd\u09ae\u0995".split())
NEGATIVE = frozenset("\u09ac\u09be\u099c\u09c7 \u09ab\u09be\u09b2\u09a4\u09c1 \u0996\u09be\u09b0\u09be\u09aa \u09ac\u09bf\u09b0\u0995\u09cd\u09a4\u09bf\u0995\u09b0 \u09ac\u09be\u099c\u09c7\u09b0 \u09a8\u09be \u09a8\u09be\u0987".split())
CONNECTIVES = frozenset("\u0995\u09bf\u09a8\u09cd\u09a4\u09c1 \u09a4\u09be\u0987 \u0995\u09be\u09b0\u09a3 \u09af\u09a6\u09bf\u0993 \u09a4\u09ac\u09c7 \u09ac\u09b0\u0982 \u0985\u09a5\u099a".split())


def tokenize(text: str) -> list[str]:
    """Whitespace split. Nothing else. See module docstring."""
    return text.split()


# ---------------------------------------------------------------------------
# F1 -- IDF statistics.  GAMEABILITY: LOW.
# ---------------------------------------------------------------------------
# Raising mean IDF requires using genuinely rarer words, which IS the construct
# (Ko, Durrett & Li 2019). It cannot be satisfied vacuously, which is exactly the
# property Mahmoud et al. find presence criteria lack.
#
# RULE-7 NOTE, LEFT IN THE SOURCE ON PURPOSE: inviolable rule 7 forbids TF-IDF
# "in the main pipeline ... never in a result". This family is IDF only -- three
# scalar summaries of a review's own tokens. It builds no document-term matrix,
# replaces no encoder, and never alters text fed to LaBSE or BanglaBERT. Whether
# that is inside or outside rule 7 is SABBIR'S RULING, not this file's
# assumption, which is why `enable_f1` exists and defaults to False.
# ---------------------------------------------------------------------------

def build_idf(documents: list[str]) -> dict[str, float]:
    """Smoothed IDF over whitespace tokens.

    MUST be built from training rows only. Building it over dev or G would leak
    the evaluation distribution into a feature and make the dev number
    meaningless -- the same class of error S3.2b found in the label itself.
    """
    n = len(documents)
    df: Counter[str] = Counter()
    for doc in documents:
        df.update(set(tokenize(doc)))
    # +1 smoothing so an unseen token gets the max value rather than a division
    # error; an unseen word is maximally specific, which is the right direction.
    return {t: math.log((n + 1) / (c + 1)) + 1.0 for t, c in df.items()}


def idf_stats(text: str, idf: dict[str, float], default: float | None = None) -> dict[str, float]:
    toks = tokenize(text)
    if not toks:
        return {"idf_min": 0.0, "idf_max": 0.0, "idf_mean": 0.0}
    fallback = default if default is not None else (max(idf.values()) if idf else 1.0)
    vals = [idf.get(t, fallback) for t in toks]
    return {"idf_min": min(vals), "idf_max": max(vals), "idf_mean": sum(vals) / len(vals)}


# ---------------------------------------------------------------------------
# F2 -- length and shape.  GAMEABILITY: HIGH (trivially).
# Retained because it is genuinely predictive -- Ko et al. report a length
# baseline of 0.581 Spearman against their full system's 0.702 -- and because
# hiding a predictive feature is worse than reporting a gameable one.
# ---------------------------------------------------------------------------
def length_shape(text: str) -> dict[str, float]:
    toks = tokenize(text)
    n = len(toks)
    return {
        "n_tokens": float(n),
        "mean_word_chars": (sum(len(t) for t in toks) / n) if n else 0.0,
    }


# ---------------------------------------------------------------------------
# F3 -- normalised orthography.  GAMEABILITY: MEDIUM.
# Every count is divided by token count. Raw counts would re-encode length and
# smuggle F2 back in under another name.
# ---------------------------------------------------------------------------
def orthography(text: str) -> dict[str, float]:
    toks = tokenize(text)
    n = max(len(toks), 1)
    stripped = text.rstrip()
    return {
        "punct_per_tok": len(_PUNCT.findall(text)) / n,
        "digit_per_tok": len(_DIGIT.findall(text)) / n,
        "latin_per_tok": len(_LATIN.findall(text)) / n,
        "ends_dandi": 1.0 if stripped.endswith(DANDI) else 0.0,
    }


# ---------------------------------------------------------------------------
# F4 -- discourse connectives.  GAMEABILITY: HIGH.
# ---------------------------------------------------------------------------
def connectives(text: str) -> dict[str, float]:
    toks = tokenize(text)
    n = max(len(toks), 1)
    return {"connective_frac": sum(t in CONNECTIVES for t in toks) / n}


# ---------------------------------------------------------------------------
# F5 -- sentiment-bearing fraction.  GAMEABILITY: HIGH.
# Fractions, not counts, for the same reason as F3.
# ---------------------------------------------------------------------------
def sentiment_fraction(text: str) -> dict[str, float]:
    toks = tokenize(text)
    n = max(len(toks), 1)
    return {
        "pos_frac": sum(t in POSITIVE for t in toks) / n,
        "neg_frac": sum(t in NEGATIVE for t in toks) / n,
        "intensifier_frac": sum(t in INTENSIFIERS for t in toks) / n,
    }


# ---------------------------------------------------------------------------
# F6 -- length-corrected lexical richness.  GAMEABILITY: LOW-MEDIUM.
# Guiraud's index V/sqrt(N), never raw type-token ratio: TTR falls
# mechanically as N grows, so on an 8-word corpus raw TTR is close to a length
# feature wearing a different name. S2e's richness inversion -- cluster 1 is 33%
# shorter yet ~18% richer -- survived a length control in ALL FOUR bands, which
# is why this family is here at all.
# ---------------------------------------------------------------------------
def richness(text: str) -> dict[str, float]:
    toks = tokenize(text)
    n = len(toks)
    if n == 0:
        return {"guiraud": 0.0}
    return {"guiraud": len(set(toks)) / math.sqrt(n)}


@dataclass(frozen=True)
class FeatureSpec:
    """Which families are on. F1 defaults OFF pending the rule-7 ruling."""

    enable_f1: bool = False


def feature_names(spec: FeatureSpec) -> list[str]:
    names: list[str] = []
    if spec.enable_f1:
        names += ["idf_min", "idf_max", "idf_mean"]
    names += ["n_tokens", "mean_word_chars"]
    names += ["punct_per_tok", "digit_per_tok", "latin_per_tok", "ends_dandi"]
    names += ["connective_frac"]
    names += ["pos_frac", "neg_frac", "intensifier_frac"]
    names += ["guiraud"]
    return names


def extract(text: str, spec: FeatureSpec, idf: dict[str, float] | None = None) -> dict[str, float]:
    """All enabled families for one review, as a flat ordered dict."""
    out: dict[str, float] = {}
    if spec.enable_f1:
        if idf is None:
            raise ValueError("enable_f1=True requires an idf table (see build_idf).")
        out.update(idf_stats(text, idf))
    out.update(length_shape(text))
    out.update(orthography(text))
    out.update(connectives(text))
    out.update(sentiment_fraction(text))
    out.update(richness(text))
    return out


def extract_matrix(
    texts: list[str], spec: FeatureSpec, idf: dict[str, float] | None = None
) -> tuple[list[list[float]], list[str]]:
    names = feature_names(spec)
    rows = [[extract(t, spec, idf)[k] for k in names] for t in texts]
    return rows, names
