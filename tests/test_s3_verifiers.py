"""S3.3 -- tests for the A/B wall and the two verifier configs.

The 2026-08-11 deviation that disambiguated Verifier-B ends with a prevention
clause: *"the Verifier-B training config must assert `role: B` and a test must
fail if its training ids intersect R1."* This file is that test, plus the
config-vs-protocol agreement checks the S3.2 tests established as the pattern.

Nothing here needs torch, sklearn or a network -- these must run in the CPU
pre-commit hook, not only on Kaggle.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from src.verifier import calibration
from src.verifier.split_access import SplitContractError, load_training_rows

ROOT = Path(__file__).resolve().parents[1]
SPLIT_MAP = ROOT / "data/splits/split_map_v1.json"
K2 = ROOT / "results/s2e_regionA_k2_assignments.csv"
CLEAN = ROOT / "data/cleaned/bn_clean.csv"
CFG_A = ROOT / "configs/s3c_verifier_a.yaml"
CFG_B = ROOT / "configs/s3d_verifier_b.yaml"


def _cfg(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _rows(role):
    return load_training_rows(role, split_map=SPLIT_MAP, k2_assignments=K2, cleaned_csv=CLEAN)


# --------------------------------------------------------------------------
# The wall. These are the tests that exist because breaking them silently is
# possible and would leave an artifact that looks correct.
# --------------------------------------------------------------------------

def test_verifier_b_training_ids_never_intersect_R1():
    """Inviolable rule 6, as an assertion rather than a memory.

    Decision 16 said Verifier-B was "the fine-tuned BanglaBERT from S3.2", and
    every S3.2 arm was `role: A` -> R1. One training run away from collapsing
    the wall that RQ5 measures.
    """
    smap = json.loads(SPLIT_MAP.read_text(encoding="utf-8"))
    train_b, _ = _rows("B")
    assert not (set(train_b.review_ids) & set(smap["R1"]))


def test_verifier_a_and_b_training_sets_are_disjoint():
    train_a, _ = _rows("A")
    train_b, _ = _rows("B")
    assert not (set(train_a.review_ids) & set(train_b.review_ids))


def test_gold_300_reaches_neither_verifier():
    smap = json.loads(SPLIT_MAP.read_text(encoding="utf-8"))
    gold = set(smap["G"])
    for role in ("A", "B"):
        train, dev = _rows(role)
        assert not (gold & set(train.review_ids)), f"G leaked into {role}'s training set"
        assert not (gold & set(dev.review_ids)), f"G leaked into {role}'s dev slice"


def test_dev_is_the_same_82_rows_for_both_roles():
    """Registered 2026-08-11: A and B are measured on identical items, because
    an A-B gap measured on different items confounds model with item."""
    _, dev_a = _rows("A")
    _, dev_b = _rows("B")
    assert len(dev_a) == len(dev_b) == 82
    assert dev_a.review_ids == dev_b.review_ids
    assert dev_a.labels == dev_b.labels


def test_dev_is_held_out_of_both_training_sets():
    for role in ("A", "B"):
        train, dev = _rows(role)
        assert not (set(train.review_ids) & set(dev.review_ids))


def test_partitions_are_not_directly_selectable():
    with pytest.raises(SplitContractError):
        load_training_rows("R2", split_map=SPLIT_MAP, k2_assignments=K2, cleaned_csv=CLEAN)


# --------------------------------------------------------------------------
# The configs must agree with STATUS's verified facts and with protocol.md.
# --------------------------------------------------------------------------

def test_config_expected_n_matches_the_frozen_split():
    for path, role, n in ((CFG_A, "A", 804), (CFG_B, "B", 888)):
        cfg = _cfg(path)
        train, dev = _rows(role)
        assert cfg["role"] == role
        assert cfg["expected"]["train_n"] == len(train) == n
        assert cfg["expected"]["dev_n"] == len(dev) == 82
        assert {int(k): v for k, v in cfg["expected"]["train_class_counts"].items()} == train.class_counts
        assert {int(k): v for k, v in cfg["expected"]["dev_class_counts"].items()} == dev.class_counts


def test_verifier_b_declares_role_B():
    """The prevention clause of the 2026-08-11 deviation, verbatim."""
    assert _cfg(CFG_B)["role"] == "B"


def test_verifier_b_has_exactly_one_learning_rate():
    """protocol.md S3.3 decision 1: the lr is taken from the spec, never selected.

    Two would silently reintroduce selection on the 82-row reporting slice --
    the condition schneider2025overtuning identify as the worst case for
    picking a configuration that generalises worse than the default.
    """
    lrs = _cfg(CFG_B)["training"]["learning_rates"]
    assert len(lrs) == 1
    assert float(lrs[0]) == 2.0e-5


def test_verifier_b_artifact_is_not_chosen_by_score():
    sel = _cfg(CFG_B)["artifact_selection"]
    assert sel["rule"] == "global_seed"
    assert sel["seed"] == 42
    assert sel["seed"] in _cfg(CFG_B)["training"]["seeds"]


def test_verifier_b_budget_matches_the_S32_recipe_except_the_lr():
    """Verifier-B is the S3.2 *recipe* retrained, so the budget must be identical.

    If epochs, batch size, max_length or the seed list drift, B stops being the
    recipe and the sentence "same backbone, same budget, same seeds" in
    protocol.md becomes false.
    """
    s32 = _cfg(ROOT / "configs/s3_backbone.yaml")["training"]
    b = _cfg(CFG_B)["training"]
    for key in ("seeds", "epochs", "batch_size", "max_length"):
        assert b[key] == s32[key], f"{key} drifted from the S3.2 recipe"


def test_verifier_b_backbone_is_the_S32_banglabert_arm():
    arms = {a["key"]: a for a in _cfg(ROOT / "configs/s3_backbone.yaml")["arms"]}
    assert _cfg(CFG_B)["model"]["model"] == arms["banglabert"]["model"]


def test_verifier_a_uses_the_same_labse_string_as_s3b():
    """If it is a different encoder, S3.2b's 0.9866 does not describe this
    artifact and the reproduction check in train_verifier_a is meaningless."""
    assert _cfg(CFG_A)["model"]["labse_model"] == _cfg(ROOT / "configs/s3b_baselines.yaml")["labse_model"]


def test_both_verifiers_calibrate_with_five_bins():
    """The 2026-08-08 S3.4 amendment: 5 bins, not the 10 of guo2017calibration.
    82 rows over 10 bins is ~8 samples per bin."""
    for path in (CFG_A, CFG_B):
        c = _cfg(path)["calibration"]
        assert c["enabled"] is True
        assert c["n_bins"] == calibration.N_BINS == 5
        assert c["descriptive"] is True


def test_verifier_a_declares_no_tuned_hyperparameters():
    m = _cfg(CFG_A)["model"]
    assert m["head"] == "logistic_regression"
    assert m["penalty"] == "l2"
    assert m["C"] == 1.0


# --------------------------------------------------------------------------
# Calibration arithmetic. Small, checkable, no model required.
# --------------------------------------------------------------------------

def test_ece_is_zero_for_a_perfectly_calibrated_predictor():
    y = [1] * 70 + [0] * 30
    p = [0.7] * 100
    assert calibration.expected_calibration_error(y, p, n_bins=5) == pytest.approx(0.0, abs=1e-9)


def test_ece_is_large_for_a_confidently_wrong_predictor():
    y = [0] * 50
    p = [0.99] * 50
    assert calibration.expected_calibration_error(y, p, n_bins=5) == pytest.approx(0.99, abs=1e-9)


def test_temperature_above_one_softens_overconfidence():
    y = [1] * 60 + [0] * 40
    p = [0.99] * 60 + [0.99] * 40  # 60% accurate, 99% confident
    t = calibration.fit_temperature(y, p)
    assert t > 1.0
    softened = calibration.apply_temperature(p, t)
    assert max(softened) < max(p)


def test_temperature_of_one_leaves_probabilities_unchanged():
    p = [0.1, 0.5, 0.9]
    assert calibration.apply_temperature(p, 1.0) == pytest.approx(p, abs=1e-9)


def test_calibration_reports_the_null_when_there_is_nothing_to_fix():
    """The pre-committed null statement must be REACHABLE.

    RQ1-F's Gate 2 had to be rewritten mid-protocol because its null verdict was
    nearly unreachable by construction. The same failure mode is tested for here
    rather than discovered later: an already-calibrated predictor must return
    CALIBRATION_NOT_ESTABLISHED, not a small spurious improvement.
    """
    y = [1] * 70 + [0] * 30
    p = [0.7] * 100
    r = calibration.calibrate(y, p, n_resamples=400)
    assert r.verdict == "CALIBRATION_NOT_ESTABLISHED"


def test_calibration_report_serialises():
    y = [1, 0] * 20
    p = [0.8, 0.3] * 20
    d = calibration.calibrate(y, p, n_resamples=200).to_dict()
    json.dumps(d)  # must not raise -- it goes straight into a result file
    assert d["n_bins"] == 5
    assert "in-sample" in d["temperature_fitted_on"]
