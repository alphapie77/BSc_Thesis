"""Guard the frozen split map. It is the one artifact nothing can recover from.

`data/splits/split_map_v1.json` defines what every downstream number means. If
it changes, results computed before the change and after it were measured
against different data — and **no other check in this repo would notice**. The
verifier would train, the loop would run, the numbers would look fine.

So the invariants are asserted here permanently, not just in the script that
wrote the map once. Each of these has a specific way of ruining the thesis
silently:

- **G leaking into R1/R2** — the gold set stops being held out, and every
  accuracy figure measured against it is inflated by an unknown amount.
- **R1 leaking into R2** — Verifier-B saw what Verifier-A trained on, so
  "the loop improves the score" and "the loop games the scorer" become
  indistinguishable. That wall *is* the Goodhart test.
- **dev outside R1** — thresholds tuned on eval data.
- **rows lost or duplicated** — n no longer means what the tables say.
- **strata drifting** — region is the confound; if G's region mix differs from
  R's, the gold set is measuring a different corpus.

Run:  python -m pytest tests/test_split_map.py -q
      python tests/test_split_map.py          (no pytest needed)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "data" / "splits" / "split_map_v1.json"
ASSIGN = ROOT / "results" / "s2_cluster_assignments.csv"
EXPECTED_N = 4625
TOLERANCE_PP = 2.0     # percentage points a stratum may drift from the corpus


def load():
    return json.loads(MAP.read_text(encoding="utf-8"))


def parts(m):
    return set(m["G"]), set(m["R1"]), set(m["R2"]), set(m["dev"])


def test_map_exists_and_is_committed():
    assert MAP.exists(), (
        "split_map_v1.json is missing. It is committed to git on purpose; if it "
        "is gone, do NOT regenerate it -- recover it from history."
    )


def test_counts_and_no_duplicates():
    m = load()
    G, R1, R2, dev = parts(m)
    assert len(m["G"]) == len(G), "duplicate ids inside G"
    assert len(m["R1"]) == len(R1), "duplicate ids inside R1"
    assert len(m["R2"]) == len(R2), "duplicate ids inside R2"
    assert len(G) == 300, f"G is {len(G)}, expected 300"
    assert len(dev) == 200, f"dev is {len(dev)}, expected 200"
    assert len(G | R1 | R2) == EXPECTED_N, (
        f"union is {len(G | R1 | R2)}, expected {EXPECTED_N}"
    )


def test_no_leakage_between_any_two_parts():
    G, R1, R2, _ = parts(load())
    assert not (G & R1), f"{len(G & R1)} gold ids appear in R1 -- G is not held out"
    assert not (G & R2), f"{len(G & R2)} gold ids appear in R2"
    assert not (R1 & R2), (
        f"{len(R1 & R2)} ids in both R1 and R2 -- Verifier-B is contaminated and "
        "the Goodhart test is void"
    )


def test_dev_slice_comes_only_from_r1():
    G, R1, R2, dev = parts(load())
    assert dev <= R1, "dev contains ids outside R1 -- thresholds tuned on eval data"
    assert not (dev & G), "dev overlaps gold"


def test_split_covers_exactly_the_deduped_corpus():
    if not ASSIGN.exists():
        print("  (skipped: s2_cluster_assignments.csv absent)")
        return
    import pandas as pd
    ids = set(pd.read_csv(ASSIGN)["review_id"])
    G, R1, R2, _ = parts(load())
    union = G | R1 | R2
    assert union == ids, (
        f"{len(ids - union)} corpus rows are in no part; "
        f"{len(union - ids)} split ids are not in the corpus"
    )


def test_strata_are_proportional_to_the_corpus():
    """G, R1 and R2 must each mirror the corpus on region and sentiment.

    Region especially: it is the confound the whole design now controls for. A
    gold set with a different region mix would measure a different corpus.
    """
    if not ASSIGN.exists():
        print("  (skipped: s2_cluster_assignments.csv absent)")
        return
    import pandas as pd
    d = pd.read_csv(ASSIGN)
    G, R1, R2, dev = parts(load())
    problems = []
    for col in ("region", "Sentiment"):
        lookup = dict(zip(d["review_id"], d[col]))
        base = d[col].value_counts(normalize=True) * 100
        for name, part in (("G", G), ("R1", R1), ("R2", R2), ("dev", dev)):
            got = pd.Series([lookup[i] for i in part]).value_counts(
                normalize=True) * 100
            for key, pct in base.items():
                diff = abs(got.get(key, 0.0) - pct)
                if diff > TOLERANCE_PP:
                    problems.append(
                        f"{name}.{col}={key}: {got.get(key, 0.0):.1f}% vs corpus "
                        f"{pct:.1f}% (drift {diff:.1f}pp > {TOLERANCE_PP})"
                    )
    assert not problems, "\n  " + "\n  ".join(problems)


def test_contract_is_recorded_in_the_map():
    """The map must carry its own rules, so a reader needs no other file."""
    m = load()
    assert "_contract" in m, "the map does not state what each part is for"
    c = m["_contract"]
    assert "EVAL ONLY" in c.get("G", ""), "G's eval-only contract is not recorded"
    assert "Goodhart" in c.get("R2", ""), "R2's wall is not explained in the map"
    assert "_provenance" in m and m["_provenance"].get("input_sha256"), (
        "the map does not record the hash of the input it was built from"
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
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    raise SystemExit(1 if failed else 0)
