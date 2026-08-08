"""Pin the RQ1-H intrusion instrument's invariants.

The whole claim of attempt 2 rests on two properties that are easy to break and
invisible once broken:

**Length matching.** If a set is not length-matched, annotators can succeed by
reading length, and RQ1-D's binding condition silently reverts from
"satisfied by construction" to "not satisfied at all" — with no symptom in any
number the study produces.

**Blinding.** If the sheets carry the answer, the cluster, or the review ids,
Gate A measures nothing. Nothing in the accuracy figure would reveal it.

Run:  python -m pytest tests/test_intrusion.py -q
      python tests/test_intrusion.py          (no pytest needed)
"""
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CFG = yaml.safe_load((ROOT / "configs" / "intrusion.yaml").read_text(encoding="utf-8"))
DIR = ROOT / CFG["outputs"]["sheet_dir"]
KEY = ROOT / CFG["outputs"]["key_csv"]


def _built():
    return KEY.exists() and (DIR / "intrusion_A.csv").exists()


def test_every_set_is_length_matched():
    """The load-bearing property. Not a preference — RQ1-D's condition."""
    if not _built():
        return
    k = pd.read_csv(KEY)
    limit = CFG["intrusion"]["max_word_span"]
    bad = k[k["word_span"] > limit]
    assert len(bad) == 0, (
        f"{len(bad)} set(s) exceed the {limit}-word span, so length is a usable "
        f"cue in them and RQ1-D's condition is NOT met by construction: "
        f"{bad['set_id'].tolist()[:5]}"
    )


def test_majority_cluster_is_balanced():
    """Otherwise the accuracy figure is partly a measure of which cluster is easier."""
    if not _built():
        return
    k = pd.read_csv(KEY)
    counts = k["majority_cluster"].value_counts()
    assert abs(counts.get(0, 0) - counts.get(1, 0)) <= 1, (
        f"majority-cluster imbalance: {dict(counts)}"
    )


def test_the_correct_answer_is_not_always_in_the_same_position():
    """A positional habit would let an annotator score above chance blind."""
    if not _built():
        return
    k = pd.read_csv(KEY)
    top = k["correct_option"].value_counts().iloc[0]
    assert top < 0.5 * len(k), (
        f"the answer sits in one position {top}/{len(k)} times — an annotator "
        f"could beat chance without reading anything"
    )


def test_the_sheets_leak_nothing():
    if not _built():
        return
    for name in ("intrusion_A.csv", "intrusion_B.csv",
                 "pairwise_A.csv", "pairwise_B.csv"):
        p = DIR / name
        if not p.exists():
            continue
        df = pd.read_csv(p, dtype=str)
        blob = df.to_csv(index=False)
        for banned in ("bn_", "cluster", "intruder", "correct", "n_words"):
            assert banned not in blob, f"'{banned}' appears in {name}"
        assert df["answer"].isna().all() or (df["answer"].fillna("") == "").all()


def test_both_annotators_get_identical_sheets():
    if not _built():
        return
    for stem in ("intrusion", "pairwise"):
        a, b = DIR / f"{stem}_A.csv", DIR / f"{stem}_B.csv"
        if a.exists() and b.exists():
            assert pd.read_csv(a, dtype=str).equals(pd.read_csv(b, dtype=str)), \
                f"{stem}: A and B differ"


def test_no_review_is_reused_across_items():
    """A repeated review would let an annotator answer by recognition."""
    if not _built():
        return
    seen = []
    for stem in ("intrusion", "pairwise"):
        p = DIR / f"{stem}_A.csv"
        if not p.exists():
            continue
        df = pd.read_csv(p, dtype=str)
        cols = [c for c in df.columns if c in list("ABCD")]
        seen += [v for c in cols for v in df[c].dropna()]
    assert len(seen) == len(set(seen)), (
        f"{len(seen) - len(set(seen))} review(s) appear more than once"
    )


def test_g300_items_are_excluded():
    """Both annotators saw G-300 in attempt 1; reusing it would not be blind."""
    assert CFG["exclude_parts"] == ["G"]


def test_the_preregistered_bands_are_unchanged():
    assert CFG["intrusion"]["chance"] == 0.25
    assert CFG["intrusion"]["strong_at_or_above"] == 0.45
    assert CFG["pairwise"]["chance"] == 0.50
    assert CFG["intrusion"]["set_size"] == 4, (
        "set size sets the chance rate. Changing it changes Gate A's null and "
        "is a protocol change (RQ1-H), not a tuning knob."
    )


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed} passed, {failed} failed (of {len(fns)})")
    raise SystemExit(1 if failed else 0)
