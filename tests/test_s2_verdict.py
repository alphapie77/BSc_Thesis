"""Pin the S2 trap-check verdict to the pre-registration in docs/protocol.md.

The band boundaries here are not implementation details -- they are the
pre-registered RQ1 claim (protocol.md, 2026-07-28, written before any ARI value
existed). A change that makes these tests fail is a change to the
pre-registration and must be logged as a protocol deviation.

Run:  python -m pytest tests/test_s2_verdict.py -q
      python tests/test_s2_verdict.py          (no pytest needed)
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cluster.s2_pilot import (  # noqa: E402
    NO_CLAIM,
    NOT_SENTIMENT_ALIGNED,
    PARTIAL_OVERLAP,
    PERSONA_CLAIM_FAILS,
    RESIDUAL_TEST_REQUIRED,
    verdict,
)

CFG = yaml.safe_load((ROOT / "configs" / "s2_pilot.yaml").read_text(encoding="utf-8"))
BANDS = CFG["trap_check"]["bands"]

#: Every PASS-like verdict. A degenerate partition must never produce one.
CLAIM_VERDICTS = {NOT_SENTIMENT_ALIGNED, PARTIAL_OVERLAP, PERSONA_CLAIM_FAILS}


def _res(ari, degenerate=False, shares=None, bad=None):
    return {
        "ari": ari,
        "degenerate": degenerate,
        "degenerate_clusters": bad or ([0] if degenerate else []),
        "cluster_shares": shares or ({0: 0.96, 1: 0.02, 2: 0.02} if degenerate
                                     else {0: 0.34, 1: 0.33, 2: 0.33}),
    }


def test_degenerate_with_low_ari_returns_no_claim():
    """THE failure mode this ordering exists to prevent.

    A degenerate partition scores LOW ARI by construction -- it fails to
    partition rather than being independent of sentiment. Under the old
    ARI-only logic this printed PASS, i.e. the strongest possible claim from
    the weakest possible clustering.
    """
    v = verdict(_res(0.0001, degenerate=True), BANDS)
    assert v["verdict"] == NO_CLAIM
    assert v["band"] == 0
    assert v["verdict"] not in CLAIM_VERDICTS
    assert "PASS" not in v["verdict"]


def test_degeneracy_overrides_every_ari_value():
    """Degeneracy is the first gate: no ARI, however extreme, escapes Band 0."""
    for ari in (-0.5, 0.0, 0.05, 0.19, 0.20, 0.45, 0.60, 0.61, 0.95, 1.0):
        v = verdict(_res(ari, degenerate=True), BANDS)
        assert v["verdict"] == NO_CLAIM, f"ARI {ari} escaped Band 0"
        assert v["band"] == 0
        assert v["verdict"] not in CLAIM_VERDICTS


def test_band_1_not_sentiment_aligned():
    for ari in (-0.10, 0.0, 0.1999):
        v = verdict(_res(ari), BANDS)
        assert (v["band"], v["verdict"]) == (1, NOT_SENTIMENT_ALIGNED), ari
        assert v["markers"] == []


def test_band_2_partial_overlap_requires_residual_test():
    for ari in (0.20, 0.35, 0.60):
        v = verdict(_res(ari), BANDS)
        assert (v["band"], v["verdict"]) == (2, PARTIAL_OVERLAP), ari
        assert RESIDUAL_TEST_REQUIRED in v["markers"], ari


def test_band_3_persona_claim_fails():
    for ari in (0.6001, 0.75, 1.0):
        v = verdict(_res(ari), BANDS)
        assert (v["band"], v["verdict"]) == (3, PERSONA_CLAIM_FAILS), ari


def test_boundaries_are_exactly_the_registered_values():
    """0.20 and 0.60 belong to Band 2 (the protocol writes 0.20 <= ARI <= 0.60)."""
    assert verdict(_res(0.1999), BANDS)["band"] == 1
    assert verdict(_res(0.2000), BANDS)["band"] == 2
    assert verdict(_res(0.6000), BANDS)["band"] == 2
    assert verdict(_res(0.6001), BANDS)["band"] == 3


def test_config_matches_the_pre_registration():
    """Config values are the protocol's numbers, not arbitrary constants."""
    assert BANDS["not_sentiment_aligned_below"] == 0.20
    assert BANDS["partial_overlap_range"] == [0.20, 0.60]
    assert BANDS["persona_claim_fails_above"] == 0.60
    assert BANDS["no_claim"] == "degenerate"
    share = CFG["trap_check"]["degenerate_cluster_share"]
    assert (share["min"], share["max"]) == (0.05, 0.70)


def test_only_band_2_carries_a_marker():
    assert verdict(_res(0.0, degenerate=True), BANDS)["markers"] == []
    assert verdict(_res(0.1), BANDS)["markers"] == []
    assert verdict(_res(0.4), BANDS)["markers"] == [RESIDUAL_TEST_REQUIRED]
    assert verdict(_res(0.9), BANDS)["markers"] == []


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
