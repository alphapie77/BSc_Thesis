import json
import ast
from pathlib import Path

import pytest

from src.eval.s5_contract import (
    CONDITIONS,
    REPLICATE_SEEDS,
    S5ContractError,
    assert_identical_critique_bytes,
    generation_key,
    largest_prefix_within_budget,
    load_eval_plots,
    select_static_examples,
    sampling_seed,
    symbolic_scores_from_s4,
    threshold_for_acceptance_rate,
)
from src.verifier.split_access import load_training_rows
from src.eval.preflight_s5 import preflight
from src.eval.run_s5_main_bn import S5ResumeError, _jsonl_by_key

import yaml


ROOT = Path(__file__).resolve().parents[1]


def _r1_rows():
    rows, dev = load_training_rows(
        "A",
        split_map=ROOT / "data/splits/split_map_v1.json",
        k2_assignments=ROOT / "results/s2e_regionA_k2_assignments.csv",
        cleaned_csv=ROOT / "data/cleaned/bn_clean.csv",
        hold_out_dev=False,
    )
    assert dev is None
    return rows


def test_condition_and_replicate_registry_is_frozen():
    assert len(CONDITIONS) == 10
    assert len(set(CONDITIONS)) == 10
    assert REPLICATE_SEEDS == (42, 43, 44)


def test_phase5_surface_is_exactly_the_90_eval_plots():
    plots = load_eval_plots(ROOT / "data/plots/plots_bn.csv")
    assert len(plots) == 90
    assert all(p.plot_id.startswith("BN") and p.synopsis for p in plots)


def test_static_examples_are_stable_stratified_and_r1_only():
    rows = _r1_rows()
    first = select_static_examples(rows, instance_key="42|BN002|L0")
    second = select_static_examples(rows, instance_key="42|BN002|L0")
    other = select_static_examples(rows, instance_key="43|BN002|L0")
    assert first == second
    assert first.review_ids != other.review_ids
    assert first.labels.count(0) == first.labels.count(1) == 10
    assert set(first.review_ids) <= set(rows.review_ids)
    split = json.loads((ROOT / "data/splits/split_map_v1.json").read_text(encoding="utf-8"))
    assert not (set(first.review_ids) & set(split["R2"]))
    assert not (set(first.review_ids) & set(split["G"]))


def test_symbolic_threshold_recomputes_the_frozen_39_of_60_match():
    scores = symbolic_scores_from_s4(ROOT / "results/s4_w_scores.csv")
    tau, accepted = threshold_for_acceptance_rate(scores, target_rate=0.65)
    assert tau == pytest.approx(0.18166513482099075, abs=1e-15)
    assert accepted == 39


def test_compute_prefix_is_nested_and_refuses_zero_affordability():
    assert largest_prefix_within_budget([10, 11, 12, 13, 14], budget=34) == 3
    with pytest.raises(S5ContractError, match="even one"):
        largest_prefix_within_budget([10, 11], budget=9)


def test_external_role_control_requires_exact_utf8_bytes():
    digest = assert_identical_critique_bytes("ভালো", "ভালো")
    assert len(digest) == 64
    with pytest.raises(S5ContractError, match="byte-identical"):
        assert_identical_critique_bytes("ভালো", "ভাল")


def test_generation_keys_separate_conditions_seeds_and_call_roles():
    keys = {
        generation_key(
            condition=c,
            replicate_seed=s,
            plot_id="BN002",
            target_level=1,
            call_role=role,
            call_index=i,
            arm="bn",
            provider="local",
            model="google/gemma-3-12b-it",
        )
        for c in CONDITIONS
        for s in REPLICATE_SEEDS
        for role, i in (("writer", 1), ("critic", 1), ("writer", 2))
    }
    assert len(keys) == 10 * 3 * 3
    assert len({sampling_seed(k) for k in keys}) == len(keys)
    assert sampling_seed(next(iter(keys))) == sampling_seed(next(iter(keys)))


def test_real_config_passes_cpu_preflight_without_loading_verifier_b():
    with open(ROOT / "configs/s5_main_bn.yaml", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    result = preflight(cfg)
    assert result["status"] == "READY_NO_GENERATION"
    assert result["condition_cases_per_language_per_replicate"] == 1800
    assert result["condition_cases_per_language"] == 5400
    assert result["static_schedule_cases"] == 90 * 2 * 3
    assert result["static_counts"] == {"0": 10, "1": 10}
    assert result["symbolic_dev_passes"] == 39
    assert result["gemini_model"] == "gemma-4-26b-a4b-it"
    assert result["gemini_transport"] == "interactions_v1beta"
    assert result["gemini_seed"] == 42
    assert result["gemini_thinking_level"] == "high"
    assert result["judge_max_output_tokens"] == 512
    assert result["judge_transport_retry_attempts"] == 3
    assert result["judge_feedback_contract"] == "enum_target_template_v1"
    assert result["judge_rate_limits"] == {
        "rpm": 30, "tpm": 16000, "rpd": 14400, "safety_fraction": 0.9,
    }
    assert result["verifier_b_loaded"] is False


def test_generation_runner_does_not_import_verifier_b():
    source = (ROOT / "src/eval/run_s5_main_bn.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    assert not any("verifier_b" in name.lower() for name in imported)


def test_config_preserves_realized_s4_single_item_batch_path():
    with open(ROOT / "configs/s5_main_bn.yaml", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    assert cfg["writer"]["batch_size"] == 1


def test_resume_archive_requires_clean_exact_commit_and_unique_valid_rows(tmp_path):
    path = tmp_path / "calls.jsonl"
    clean = {
        "key": "k1", "provenance": {"git_commit": "abc123"},
    }
    path.write_text(json.dumps(clean) + "\n", encoding="utf-8")
    assert set(_jsonl_by_key(path, expected_commit="abc123")) == {"k1"}

    path.write_text(json.dumps(clean) + "\n" + json.dumps(clean) + "\n", encoding="utf-8")
    with pytest.raises(S5ResumeError, match="duplicate"):
        _jsonl_by_key(path, expected_commit="abc123")

    path.write_text(json.dumps(clean) + "\n", encoding="utf-8")
    with pytest.raises(S5ResumeError, match="expected clean runner"):
        _jsonl_by_key(path, expected_commit="different")

    path.write_text("not-json\n", encoding="utf-8")
    with pytest.raises(S5ResumeError, match="invalid checkpoint row"):
        _jsonl_by_key(path, expected_commit="abc123")
