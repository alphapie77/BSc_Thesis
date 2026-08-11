"""Pin the copy detector. A copied exemplar passes the Critic by construction.

Verifier-A was trained on exactly these reviews, so a real corpus review is the
highest-scoring thing the loop can emit. Without this check the system could
report an excellent first-attempt pass rate, a healthy τ frontier and strong
§5.4 realism while doing retrieval — every number measuring the corpus against
itself.

Run:  python -m pytest tests/test_copy_check.py -q
      python tests/test_copy_check.py          (no pytest needed)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.eval.copy_check import jaccard, max_similarity, report, tokens  # noqa: E402

EX = "বাংলা সিনেমার মধ্যে ভালো একটা সিনেমা।"


def test_identical_text_scores_one():
    assert jaccard(EX, EX) == 1.0


def test_the_near_copy_exact_match_would_miss_scores_high():
    """The whole reason this file exists.

    The pilot caught an exact copy. A model has no reason to copy exactly
    rather than approximately, and exact matching would have called this clean.
    """
    near = "বাংলা সিনেমার মধ্যে ভালো একটি সিনেমা।"  # একটা -> একটি
    assert near != EX, "this test needs a genuine near-copy, not the original"
    assert jaccard(EX, near) > 0.6, jaccard(EX, near)


def test_unrelated_bangla_text_scores_low():
    other = "শেষ দৃশ্যে ববির অভিনয় দেখে চোখে পানি এসে গেল"
    assert jaccard(EX, other) < 0.2, jaccard(EX, other)


def test_empty_input_does_not_crash_or_claim_similarity():
    assert jaccard("", EX) == 0.0
    assert max_similarity("", [EX]) == (0.0, -1)


def test_max_similarity_reports_which_candidate():
    cands = ["একদম বাজে", EX, "গানগুলো সুন্দর"]
    score, idx = max_similarity(EX, cands)
    assert idx == 1 and score == 1.0


def test_no_stemming_or_stopword_removal():
    """Inviolable rule 7 forbids both — and they would be wrong here anyway.

    The question is whether one string was copied from another. Normalising the
    two toward each other is precisely the wrong direction: it manufactures
    similarity and would hide the failure this detector exists to find.
    """
    assert tokens("ভালো ভালো ছবি") == {"ভালো", "ছবি"}
    assert "the" in tokens("the film was good")


def test_report_separates_shown_exemplars_from_the_corpus():
    """Resembling one of the ten it was just shown is the failure mode.

    Resembling some unrelated review is a coincidence of a small formulaic
    domain. Merging the two would let ordinary domain similarity mask real
    copying, or vice versa.
    """
    gens = [{"key": "k1", "text": EX, "target_level": 0}]
    r = report(gens, {"k1": [EX]}, ["অন্য কিছু", EX])
    assert r["n_exact_corpus_matches"] == 1
    assert r["similarity_to_exemplars_shown"]["max"] == 1.0
    assert "similarity_to_corpus_sample" in r


def test_no_threshold_is_applied():
    """A cutoff would be a decision constant with no criterion."""
    r = report([{"key": "k", "text": EX, "target_level": 1}], {"k": [EX]}, [EX])
    flat = str(r).lower()
    for word in ("threshold", "cutoff", "is_copy", "verdict"):
        assert word not in flat.replace("no threshold", ""), word


def _run_all() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL  {fn.__name__}\n        {exc}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run_all())
