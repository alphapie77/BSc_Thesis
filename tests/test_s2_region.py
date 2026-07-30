"""Pin the region boundary and the restricted-run safeguards.

`region_of` decides which of the two source corpora a review belongs to, and
that assignment now sits underneath a claim in the thesis. An off-by-one at the
boundary would silently move ~1 review between corpora and, worse, would go
unnoticed because both answers look plausible.

The cache guard matters just as much: a restricted run must not read or write
`labse_emb_bn_clean.npy`, which is keyed to the full corpus by row count. If it
did, a later full run would load embeddings for a subset and the row-count
assertion would be the only thing standing between that and a silently wrong
result.

Run:  python -m pytest tests/test_s2_region.py -q
      python tests/test_s2_region.py          (no pytest needed)
"""
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cluster.s2_pilot import region_of  # noqa: E402

A, B = "A_organic", "B_uniform"
BOUNDARY = 1999


def test_boundary_is_exclusive_on_the_left():
    """Row 1998 is the LAST organic row; 1999 is the first uniform one.

    `results/s2c_region_split.md` reports region A as rows 0-1998 (n = 1,999).
    If this ever flips, that n becomes 2,000 and every downstream count is off.
    """
    got = region_of(np.array(["bn_1997", "bn_1998", "bn_1999", "bn_2000"]), BOUNDARY)
    assert list(got) == [A, A, B, B], got


def test_endpoints():
    got = region_of(np.array(["bn_0000", "bn_4999"]), BOUNDARY)
    assert list(got) == [A, B], got


def test_ids_are_parsed_by_row_number_not_string_order():
    """'bn_0999' < 'bn_1000' lexically too, but 'bn_999' would not be.

    review_id is zero-padded today; parsing as an int rather than comparing
    strings means an unpadded id would still land in the right region.
    """
    got = region_of(np.array(["bn_999", "bn_0999", "bn_2001"]), BOUNDARY)
    assert list(got) == [A, A, B], got


def test_region_counts_match_the_cleaned_corpus():
    """Against the real file: 1,910 organic rows, 2,820 uniform, 4,730 total.

    These are the numbers in STATUS fact (split). If the parsing or the boundary
    drifts, this test fails before a report quotes the wrong figure.
    """
    import pandas as pd
    csv = ROOT / "data" / "cleaned" / "bn_clean.csv"
    if not csv.exists():
        print("  (skipped: bn_clean.csv is gitignored and absent)")
        return
    d = pd.read_csv(csv)
    r = region_of(d["review_id"].to_numpy(), BOUNDARY)
    n_a, n_b = int((r == A).sum()), int((r == B).sum())
    assert n_a == 1910, f"region A is {n_a}, expected 1910"
    assert n_b == 2820, f"region B is {n_b}, expected 2820"
    # Region A must contain no class-2 rows -- this is the whole finding.
    assert int((d.loc[r == A, "Sentiment"] == 2).sum()) == 0


def test_regionA_config_cannot_touch_the_full_corpus_cache():
    """A restricted run must not share the embedding cache with a full run."""
    cfg = yaml.safe_load(
        (ROOT / "configs" / "s2_pilot_regionA.yaml").read_text(encoding="utf-8")
    )
    assert cfg["region"]["restrict_to"] == A
    assert cfg["embedding"]["cache_npy"] is None, "restricted run must not cache"
    full = yaml.safe_load(
        (ROOT / "configs" / "s2_pilot.yaml").read_text(encoding="utf-8")
    )
    for key in ("near_dup_pairs_csv", "report_md", "cluster_assignments_csv"):
        assert cfg["outputs"][key] != full["outputs"][key], (
            f"regionA would overwrite the full-corpus {key}"
        )


def test_regionA_keeps_the_instrument_identical():
    """Only the subset changes. Seed, encoder, K and the bands must not.

    A subset run whose settings also drifted would confound "does structure
    survive in region A" with "does structure appear under different settings".
    """
    a = yaml.safe_load(
        (ROOT / "configs" / "s2_pilot_regionA.yaml").read_text(encoding="utf-8")
    )
    f = yaml.safe_load(
        (ROOT / "configs" / "s2_pilot.yaml").read_text(encoding="utf-8")
    )
    assert a["seed"] == f["seed"]
    assert a["embedding"]["model"] == f["embedding"]["model"]
    assert a["embedding"]["max_seq_length"] == f["embedding"]["max_seq_length"]
    assert a["clustering"]["k"] == f["clustering"]["k"]
    assert a["clustering"]["n_init"] == f["clustering"]["n_init"]
    assert a["clustering"]["random_state"] == f["clustering"]["random_state"]
    assert a["near_duplicate"]["primary_threshold"] == \
        f["near_duplicate"]["primary_threshold"]
    assert a["near_duplicate"]["sweep_thresholds"] == \
        f["near_duplicate"]["sweep_thresholds"]
    assert a["trap_check"]["bands"] == f["trap_check"]["bands"], \
        "the pre-registered bands must not change for the subset run"
    assert a["clustering"]["cluster_in_umap_space"] is False   # rule 9


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
