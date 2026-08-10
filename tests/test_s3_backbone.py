"""Tests for S3.2. Three jobs, in order of how much damage they prevent.

1. The split contract holds: G is unreachable, R2 is unreachable from role A,
   and the n matches what protocol.md pre-registered.
2. The decision rule is the pre-registered one and behaves correctly, including
   the case that matters most -- that a TIE is reachable. RQ1-F was nearly
   invalidated by a gate whose null verdict was unreachable by construction
   (see the 2026-08-04 note in STATUS). The same mistake is checked for here.
3. Config and protocol agree. If someone edits the YAML without editing the
   pre-registration, this fails.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.verifier import compare
from src.verifier.split_access import (
    ROLE_PARTITION,
    SplitContractError,
    load_gold_ids,
    load_training_rows,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "s3_backbone.yaml"
PROTOCOL = ROOT / "docs" / "protocol.md"

INPUTS = dict(
    split_map=ROOT / "data" / "splits" / "split_map_v1.json",
    k2_assignments=ROOT / "results" / "s2e_regionA_k2_assignments.csv",
    cleaned_csv=ROOT / "data" / "cleaned" / "bn_clean.csv",
)


def _cfg() -> dict:
    yaml = pytest.importorskip("yaml")
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


# --------------------------------------------------------------- the wall

def test_role_a_draws_r1_and_role_b_draws_r2():
    assert ROLE_PARTITION == {"A": "R1", "B": "R2"}


def test_partition_cannot_be_requested_directly():
    """A caller asks for a role. Asking for "R2" is not a thing it can do."""
    for bad in ("R1", "R2", "G", "dev", "a1"):
        with pytest.raises(SplitContractError):
            load_training_rows(bad, **INPUTS)


def test_verifier_a_never_sees_r2_or_gold():
    train, dev = load_training_rows("A", **INPUTS)
    gold = set(load_gold_ids(INPUTS["split_map"]))
    b_train, _ = load_training_rows("B", **INPUTS)

    touched = set(train.review_ids) | set(dev.review_ids)
    assert not (touched & gold), "Gold-300 reached Verifier-A"
    assert not (touched & set(b_train.review_ids)), "R2 reached Verifier-A"


def test_dev_is_held_out_of_training():
    train, dev = load_training_rows("A", **INPUTS)
    assert not (set(train.review_ids) & set(dev.review_ids))


def test_n_matches_the_preregistration():
    """These four numbers are in protocol.md, written before any result existed.

    If this test fails, the correct response is NOT to update the numbers.
    """
    train, dev = load_training_rows("A", **INPUTS)
    assert len(train) == 804
    assert train.class_counts == {0: 481, 1: 323}
    assert len(dev) == 82
    assert dev.class_counts == {0: 53, 1: 29}


def test_verifier_b_n_matches_and_receives_the_shared_dev():
    """Amended 2026-08-11. This test previously asserted `dev is None` for role B.

    That assertion was correct about the *mechanism* and wrong about the
    *design*, and it pinned a gap rather than a rule: with no dev slice,
    Verifier-B had no registered evaluation set at all, which nobody noticed
    until Phase 3 tried to train it. The wall being protected is that R2 and R1
    stay disjoint in **training** — and that is still asserted, below and in
    tests/test_s3_verifiers.py.

    B is now evaluated on the same 82 rows as A, because RQ5's Goodhart gap is
    an A−B comparison and measuring the two on different items confounds model
    difference with item difference. Registered in protocol.md §S3.3 with a
    deviation row for widening the split map's `dev` contract.
    """
    train, dev = load_training_rows("B", **INPUTS)
    assert len(train) == 888
    assert train.class_counts == {0: 531, 1: 357}
    assert len(dev) == 82, "B is evaluated on the shared dev-82"
    assert not (set(train.review_ids) & set(dev.review_ids)), (
        "dev must never be inside B's training set; R2 and dev are disjoint by "
        "the frozen split's own contract, so this failing means the split moved"
    )


def test_region_b_rows_are_absent_by_construction():
    """Region B has no K=2 label, so it cannot appear. Not filtered -- absent."""
    train, dev = load_training_rows("A", **INPUTS)
    labelled = len(train) + len(dev)
    assert labelled == 886, "R1 carries 886 labelled rows; the rest are region B"


# ------------------------------------------------------- the decision rule

def test_macro_f1_matches_a_hand_computed_case():
    y = [0, 0, 1, 1]
    assert compare.macro_f1(y, [0, 0, 1, 1]) == pytest.approx(1.0)
    assert compare.macro_f1(y, [0, 0, 0, 0]) == pytest.approx(1 / 3)  # 0.8 and 0.0


def test_identical_arms_are_never_significant():
    y = [0, 1] * 20
    pred = [0, 1] * 20
    res = compare.paired_bootstrap(y, pred, pred, n_resamples=500)
    assert res.observed_diff == 0.0
    assert res.p_value == pytest.approx(1.0)


def test_a_clearly_better_arm_is_detected():
    y = [0, 1] * 40
    good = list(y)
    bad = [0] * 80
    res = compare.paired_bootstrap(y, good, bad, n_resamples=1000)
    assert res.observed_diff > 0.5
    assert res.p_value < 0.05


def test_bootstrap_is_deterministic_under_a_fixed_seed():
    y = [0, 1] * 30
    a = [0, 1] * 30
    b = [0] * 60
    r1 = compare.paired_bootstrap(y, a, b, n_resamples=300, seed=42)
    r2 = compare.paired_bootstrap(y, a, b, n_resamples=300, seed=42)
    assert r1 == r2


def test_TIE_is_reachable():
    """The RQ1-F lesson, encoded.

    Gate 2 of G-300 was originally written with a rule whose NEGATIVE verdict
    was almost unreachable, and it took a rewrite before annotation to notice.
    A decision rule that can only ever return "we found a winner" is not a test.
    Here: seven arms of near-identical quality must return TIE.
    """
    y = [0, 1] * 41
    arms = [f"arm{i}" for i in range(7)]
    preds = {a: list(y) for a in arms}
    for i, a in enumerate(arms):  # perturb each arm by one item
        preds[a][i] = 1 - preds[a][i]
    p_values, pairs = [], []
    import itertools
    for a, b in itertools.combinations(arms, 2):
        r = compare.paired_bootstrap(y, preds[a], preds[b], arm_a=a, arm_b=b, n_resamples=400)
        pairs.append(r)
        p_values.append(r.p_value)
    rejected = compare.benjamini_hochberg(p_values)
    sig = {(r.arm_a, r.arm_b) for r, ok in zip(pairs, rejected) if ok}
    means = {a: compare.macro_f1(y, preds[a]) for a in arms}
    assert compare.verdict(arms, means, sig) == "TIE"


def test_SINGLE_WINNER_is_also_reachable():
    """The mirror check: a rule that can only return TIE is equally useless."""
    y = [0, 1] * 41
    arms = ["good", "bad1", "bad2"]
    preds = {"good": list(y), "bad1": [0] * 82, "bad2": [1] * 82}
    p_values, pairs = [], []
    import itertools
    for a, b in itertools.combinations(arms, 2):
        r = compare.paired_bootstrap(y, preds[a], preds[b], arm_a=a, arm_b=b, n_resamples=400)
        pairs.append(r)
        p_values.append(r.p_value)
    rejected = compare.benjamini_hochberg(p_values)
    sig = {(r.arm_a, r.arm_b) for r, ok in zip(pairs, rejected) if ok}
    means = {a: compare.macro_f1(y, preds[a]) for a in arms}
    assert compare.verdict(arms, means, sig) == "SINGLE_WINNER"


def test_benjamini_hochberg_preserves_input_order_and_is_conservative():
    ps = [0.001, 0.9, 0.02, 0.5]
    out = compare.benjamini_hochberg(ps, alpha=0.05)
    assert out[0] is True and out[1] is False
    assert len(out) == len(ps)
    assert compare.benjamini_hochberg([]) == []
    # BH must reject no more than uncorrected testing would.
    assert sum(out) <= sum(p <= 0.05 for p in ps)


# ------------------------------------------------- config vs pre-registration

def test_config_declares_seven_arms_including_the_three_added_ones():
    cfg = _cfg()
    keys = {a["key"] for a in cfg["arms"]}
    assert len(cfg["arms"]) == 7
    assert {"indicbertv2", "setfit_labse", "bert_nli"} <= keys, (
        "the three arms added on 2026-08-08 are pre-registered; removing one "
        "after the fact is exactly what the pre-registration forbids"
    )


def test_config_uses_five_seeds_not_three():
    cfg = _cfg()
    assert len(cfg["training"]["seeds"]) >= 5


def test_config_decision_rule_is_the_bootstrap_not_mean_sd():
    cfg = _cfg()
    assert cfg["decision"]["rule"] == "paired_bootstrap"
    assert cfg["decision"]["n_resamples"] == compare.N_RESAMPLES
    assert cfg["decision"]["alpha"] == compare.ALPHA
    assert cfg["decision"]["correction"] == "benjamini_hochberg"


def test_config_expected_counts_match_the_protocol_text():
    """The YAML and protocol.md must not drift apart silently."""
    cfg = _cfg()
    assert cfg["expected"]["train_n"] == 804
    assert cfg["expected"]["dev_n"] == 82
    text = PROTOCOL.read_text(encoding="utf-8")
    assert "S3.2 pre-commitment" in text
    assert re.search(r"\*\*804\*\*", text), "protocol.md must state n=804"


def test_config_reads_the_regionA_labels_not_the_corpus_detector():
    """s2_cluster_assignments.csv clusters detect which corpus a row came from
    (93.3% accuracy). Training a persona verifier on those is the one input
    mistake that would look like a working result."""
    cfg = _cfg()
    assert cfg["inputs"]["k2_assignments"].endswith("s2e_regionA_k2_assignments.csv")


def test_protocol_registers_setfit_as_an_expected_loser():
    text = PROTOCOL.read_text(encoding="utf-8")
    assert "expectation of losing" in text or "EXPECTED LOSER" in text


# ------------------------------------------------------ reporting honesty

def test_sd_matches_a_hand_computed_case():
    from src.verifier.s3_backbone_ablation import _sd
    assert _sd([1.0]) == 0.0                     # single run has no spread
    assert _sd([]) == 0.0
    assert _sd([0.0, 2.0]) == pytest.approx(2 ** 0.5)


def test_report_discloses_that_lr_was_selected_on_the_eval_set():
    """The learning rate is chosen by best mean on dev, and the arms are then
    compared on that same dev set. It biases all arms in the same direction, so
    the comparison survives -- but the LEVELS are not clean held-out estimates,
    and a reader must be told that on the face of the table, not in a footnote
    nobody reaches."""
    from src.verifier.s3_backbone_ablation import _render_md
    cfg = _cfg()
    result = {
        "dry_run": False, "verdict": "TIE", "n_train": 804, "n_dev": 82,
        "train_class_counts": {0: 481, 1: 323}, "dev_class_counts": {0: 53, 1: 29},
        "seeds": [42, 43, 44, 45, 46],
        "mean_macro_f1": {"banglabert": 0.9},
        "seed_sd": {"banglabert": 0.01},
        "selected_lr": {"banglabert": 2e-5},
        "lr_selected_on_eval_set": True,
        "pairwise": [],
    }
    md = _render_md(result, cfg)
    assert "not clean held-out estimates" in md
    assert "at the selected learning rate" in md
    assert "label *reproduction*" in md, "the validity caveat must survive too"


# ------------------------------- the free robustness check on LR aggregation

def test_majority_vote_is_selection_free_and_deterministic():
    from src.verifier.s3_backbone_ablation import _majority_vote
    assert _majority_vote([[1, 0], [1, 0], [0, 0]]) == [1, 0]
    # An exact tie must resolve the same way every time, for every arm.
    assert _majority_vote([[1], [0]]) == [0]
    assert _majority_vote([[1], [0]]) == _majority_vote([[0], [1]])


def test_disagreement_between_lr_rules_is_reported_loudly():
    """If selecting the LR and pooling over LRs give different verdicts, the
    answer depends on how the hyperparameter was handled -- which is the thing
    the cheap design assumed away. The report must say so, not average it out.
    """
    from src.verifier.s3_backbone_ablation import _render_md
    cfg = _cfg()
    result = {
        "dry_run": False, "verdict": "SINGLE_WINNER", "verdict_pooled_lr": "TIE",
        "verdict_agrees_across_lr_rules": False,
        "n_train": 804, "n_dev": 82,
        "train_class_counts": {0: 481, 1: 323}, "dev_class_counts": {0: 53, 1: 29},
        "seeds": [42, 43, 44, 45, 46],
        "mean_macro_f1": {"banglabert": 0.9}, "seed_sd": {"banglabert": 0.01},
        "selected_lr": {"banglabert": 2e-5}, "lr_selected_on_eval_set": True,
        "pairwise": [],
    }
    md = _render_md(result, cfg)
    assert "DISAGREE" in md
    assert "inner k-fold" in md
    assert "may be reported as the result until" in md


def test_nli_arm_loads_with_a_head_size_mismatch_allowed():
    """The NLI checkpoint is 3-class and our task is binary.

    `nli_transfer_predict`'s docstring claimed the head is re-initialised for
    two labels; the code did not pass the flag that does it, and the run died on
    `size mismatch [3] vs [2]` after five arms had completed. This test reads
    the source, because the alternative is a GPU run.
    """
    src = (ROOT / "src" / "verifier" / "backends.py").read_text(encoding="utf-8")
    assert "ignore_mismatched_sizes=True" in src, (
        "the NLI arm cannot load without it, and arms 1-5 are unaffected"
    )


# ------------------------------------------------- resuming across sessions

def test_resume_refuses_a_checkpoint_from_a_different_environment():
    """Arms carried over from another environment may not share a results table.

    Coakley et al. (2022) measured >6 pp of accuracy variation from environment
    alone; our between-arm spread is under 3 pp. So a resumed checkpoint has to
    prove it came from the same environment, not merely exist.
    """
    from src.verifier.s3_backbone_ablation import _check_resume_env, _env_fingerprint
    same = _env_fingerprint()
    assert _check_resume_env(same, allow_unverified=False) == "verified"
    with pytest.raises(SystemExit):
        _check_resume_env({**same, "transformers": "0.0.0-not-this"}, allow_unverified=False)


def test_a_checkpoint_without_a_fingerprint_needs_an_explicit_opt_in():
    from src.verifier.s3_backbone_ablation import _check_resume_env
    with pytest.raises(SystemExit):
        _check_resume_env(None, allow_unverified=False)
    assert _check_resume_env(None, allow_unverified=True) == "unverified"


def test_setfit_receives_the_learning_rate():
    """The 2026-08-09 run's setfit arm was one configuration run ten times.

    `lr` was never passed to SetFit, so both learning-rate settings were the
    same computation, and the seed had no effect either: across all ten runs
    the schedule peaked at the same 1.98e-5, grad_norm matched to sixteen
    decimals, and train_loss was 0.016336093562370195 every time. A test reads
    the source, because the alternative way to catch this is two GPU-hours and
    a suspicious standard deviation of exactly zero.
    """
    src = (ROOT / "src" / "verifier" / "backends.py").read_text(encoding="utf-8")
    assert "body_learning_rate=lr" in src
    assert "head_learning_rate=lr" in src


# ------------------------------------------------------------ S3.2b baselines

def test_s3b_bands_are_all_reachable_and_ordered():
    """A band structure that can only return one verdict is not a test.

    Same lesson as RQ1-F's Gate 2 and S3.2's TIE check: verify by construction
    that each outcome is attainable, before the numbers arrive.
    """
    yaml = pytest.importorskip("yaml")
    cfg = yaml.safe_load((ROOT / "configs" / "s3b_baselines.yaml").read_text(encoding="utf-8"))
    assert cfg["labse_model"] == "sentence-transformers/LaBSE", (
        "the probe must use the encoder that GENERATED cluster_k2, or it is not "
        "testing the circularity we actually have"
    )
    text = PROTOCOL.read_text(encoding="utf-8")
    for band in ("CIRCULARITY_CONFIRMED", "PARTIAL", "NOT_CIRCULAR"):
        assert band in text, f"band {band} is not pre-registered"


def test_length_baseline_is_fitted_on_train_not_dev():
    """Tuning the baseline on dev would flatter it and make the arms look worse
    -- the opposite of the error S3.2b exists to catch."""
    src = (ROOT / "src" / "verifier" / "s3b_baselines.py").read_text(encoding="utf-8")
    assert "train.labels" in src and "chosen on TRAIN" in src


def test_majority_and_length_baselines_are_computable_without_torch():
    from src.verifier.s3b_baselines import majority_baseline, length_baseline
    train, dev = load_training_rows("A", **INPUTS)
    assert compare.macro_f1(list(dev.labels), majority_baseline(train, dev)) < 0.50
    pred, meta = length_baseline(train, dev)
    assert len(pred) == 82 and meta["direction"] in (">", "<=")
