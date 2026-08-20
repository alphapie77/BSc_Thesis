import json

import pytest

from src.eval.audit_s5_checkpoint import S5CheckpointAuditError, audit_checkpoint
from src.eval.s5_contract import CONDITIONS, load_eval_plots


ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
COMMIT = "9e00d2e2b2f757166ead317a5eb9139b4d67f737"


def _case(plot_id, level, condition):
    return {
        "key": f"S5BN|s42|{plot_id}|L{level}|{condition}",
        "plot_id": plot_id, "target_level": level, "replicate_seed": 42,
        "condition": condition, "verifier_b_score": None,
        "provenance": {"git_commit": COMMIT, "verifier_b_loaded": False},
    }


def _write_jsonl(path, rows):
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_audit_reports_same_chunk_resume_until_the_full_chunk_is_complete(tmp_path):
    plot = load_eval_plots(ROOT / "data/plots/plots_bn.csv")[0]
    rows = [_case(plot.plot_id, 0, condition) for condition in CONDITIONS]
    _write_jsonl(tmp_path / "s5_main_bn_cases.jsonl", rows)
    report = audit_checkpoint(tmp_path, ROOT / "configs/s5_main_bn.yaml", expected_commit=COMMIT)
    assert report["status"] == "S5_CHECKPOINT_AUDIT_PASS"
    assert report["seed_progress"]["condition_cases_complete"] == 10
    assert report["next_handoff"] == {
        "earliest_incomplete_base_case": 1,
        "safe_resume_start": 0,
        "safe_resume_limit": 20,
    }


def test_audit_rejects_verifier_b_in_generation_checkpoint(tmp_path):
    plot = load_eval_plots(ROOT / "data/plots/plots_bn.csv")[0]
    row = _case(plot.plot_id, 0, CONDITIONS[0])
    row["verifier_b_score"] = 0.8
    _write_jsonl(tmp_path / "s5_main_bn_cases.jsonl", [row])
    with pytest.raises(S5CheckpointAuditError, match="Verifier-B"):
        audit_checkpoint(tmp_path, ROOT / "configs/s5_main_bn.yaml", expected_commit=COMMIT)
