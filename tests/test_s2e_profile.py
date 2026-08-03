"""Validate the S2e statistics against cases with a known answer.

The three quantities this file guards are ones whose failure mode is silent:

* `directionless_auc` — if it were direction-*ful*, the pre-registered RQ1-D
  bands would fire or not fire depending on which half K-Means happened to label
  0, which is an artefact of centroid initialisation. The verdict would then be
  a coin flip wearing a threshold.
* `log_odds_with_prior` — an unsmoothed version returns typos and a raw-frequency
  version returns "the"; both produce a plausible-looking ranked list either way,
  and neither announces that it is wrong.
* `length_verdict` — thresholds copied by hand from a document are exactly the
  kind of thing that drifts. Pinned here, and pinned again against the config.

Run:  python -m pytest tests/test_s2e_profile.py -q
      python tests/test_s2e_profile.py          (no pytest needed)
"""
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cluster.s2e_profile import (  # noqa: E402
    LENGTH_CONFOUNDED, LENGTH_DOMINATED, NOT_LENGTH, cliffs_delta,
    directionless_auc, length_verdict, log_odds_with_prior,
)

CFG = yaml.safe_load((ROOT / "configs" / "s2e_profile.yaml").read_text(encoding="utf-8"))
CFG_G1 = yaml.safe_load((ROOT / "configs" / "s2d_ktable.yaml").read_text(encoding="utf-8"))


def test_directionless_auc_ignores_which_half_is_called_zero():
    """The whole point of the name. Flipping the labels must change nothing."""
    x = np.array([1.0, 2, 3, 4, 5, 6, 7, 8], dtype=float)
    pos = np.array([0, 0, 0, 0, 1, 1, 1, 1], dtype=bool)
    assert directionless_auc(x, pos) == directionless_auc(x, ~pos)


def test_directionless_auc_is_one_when_separated_and_half_when_not():
    x = np.array([1.0, 2, 3, 10, 11, 12])
    sep = np.array([0, 0, 0, 1, 1, 1], dtype=bool)
    assert directionless_auc(x, sep) == 1.0, "perfect separation did not score 1"

    flat = np.ones(200)
    grp = np.array([True, False] * 100)
    assert abs(directionless_auc(flat, grp) - 0.5) < 1e-9, (
        "a constant feature appeared informative"
    )


def test_directionless_auc_never_below_half():
    """It is a max over a value and its complement, so 0.5 is a hard floor."""
    rng = np.random.default_rng(0)
    for _ in range(50):
        x = rng.normal(size=60)
        pos = rng.random(60) < 0.5
        assert directionless_auc(x, pos) >= 0.5 - 1e-12


def test_cliffs_delta_is_zero_at_chance_and_one_at_perfect():
    assert abs(cliffs_delta(0.5)) < 1e-12
    assert abs(cliffs_delta(1.0) - 1.0) < 1e-12


def test_log_odds_gives_a_one_sided_word_a_one_sided_z():
    a = Counter({"ভালো": 40, "ছবি": 60})
    b = Counter({"বাজে": 40, "ছবি": 60})
    t = log_odds_with_prior(a, b, prior_strength=100.0, min_count=5)
    z = dict(zip(t["word"], t["z"]))
    assert z["ভালো"] > 0, "a word exclusive to group A did not score positive"
    assert z["বাজে"] < 0, "a word exclusive to group B did not score negative"


def test_log_odds_gives_an_evenly_split_word_a_z_of_zero():
    """A word used identically by both halves carries no information.

    This is the property that makes stopword removal unnecessary: common words
    are common on both sides, so the statistic ignores them without anyone
    having to write a Bangla stopword list — a modelling choice this project has
    not justified and inviolable rule 7 forbids.
    """
    a = Counter({"এই": 300, "x": 100})
    b = Counter({"এই": 300, "y": 100})
    t = log_odds_with_prior(a, b, prior_strength=100.0, min_count=5)
    z = dict(zip(t["word"], t["z"]))
    assert abs(z["এই"]) < 1e-9, f"a perfectly balanced word scored z={z['এই']}"


def test_log_odds_shrinks_rare_words_more_than_frequent_ones():
    """The reason for the prior: 5-out-of-5 is weaker evidence than 500-out-of-500.

    An unsmoothed log-odds ratio scores both as infinite and returns the hapax
    at the top of the list. This must not.
    """
    a = Counter({"rare": 5, "frequent": 500, "shared": 5000})
    b = Counter({"shared": 5000})
    t = log_odds_with_prior(a, b, prior_strength=500.0, min_count=5)
    z = dict(zip(t["word"], t["z"]))
    assert z["frequent"] > z["rare"], (
        f"the rare word was not shrunk more (rare {z['rare']:.2f} vs "
        f"frequent {z['frequent']:.2f}) — the prior is not doing its job"
    )


def test_log_odds_drops_words_below_min_count():
    a = Counter({"seen_once": 1, "common": 50})
    b = Counter({"common": 50})
    t = log_odds_with_prior(a, b, prior_strength=100.0, min_count=5)
    assert "seen_once" not in set(t["word"]), "a hapax survived min_count"


def test_length_verdict_bands_are_exactly_the_preregistered_ones():
    """Boundaries are inclusive-below, matching RQ1-D's ">= " wording."""
    assert length_verdict(0.75, CFG) == LENGTH_DOMINATED
    assert length_verdict(0.7499, CFG) == LENGTH_CONFOUNDED
    assert length_verdict(0.65, CFG) == LENGTH_CONFOUNDED
    assert length_verdict(0.6499, CFG) == NOT_LENGTH
    assert length_verdict(0.50, CFG) == NOT_LENGTH


def test_the_preregistered_thresholds_are_unchanged():
    """A silent edit here is a change to RQ1-D, so it fails loudly instead."""
    assert CFG["length_bands"]["dominated_at_or_above"] == 0.75, (
        "the LENGTH_DOMINATED cutoff moved. That is a protocol change "
        "(docs/protocol.md, RQ1-D) and must be logged as a deviation."
    )
    assert CFG["length_bands"]["confounded_at_or_above"] == 0.65
    assert CFG["surface_auc_headline"] == 0.80
    assert CFG["length_feature"] == "n_words"


def test_s2e_profiles_the_SAME_partition_g1_selected():
    """S2e must re-derive G1's labels, not a different K=2 solution.

    Identical embedding and K-Means settings are a precondition for that. The
    script also verifies it numerically at runtime against the published table,
    but a config that has drifted should fail here — at test time, before a run
    burns a Kaggle session and produces a report about the wrong partition.
    """
    assert CFG["embedding"] == CFG_G1["embedding"], (
        "configs/s2e_profile.yaml and configs/s2d_ktable.yaml disagree on the "
        "embedding. S2e would profile a partition G1 never selected."
    )
    assert CFG["kmeans"] == CFG_G1["kmeans"]
    for key in ("input_assignments", "input_csv", "id_col", "label_col",
                "text_col", "expected_n", "seed"):
        assert CFG[key] == CFG_G1[key], f"configs disagree on {key}"
    assert CFG["k"] in CFG_G1["k_range"]


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
