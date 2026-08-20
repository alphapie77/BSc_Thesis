import json

import pytest

from src.eval.migrate_s5_checkpoint_gemma4 import (
    CheckpointMigrationError,
    NEW_CONDITION,
    OLD_CONDITION,
    SOURCE_COMMIT,
    partition_rows,
)


CURRENT = "new-clean-commit"
MIGRATION = {
    "timestamp_utc": "2026-08-21T00:00:00+00:00",
    "git_commit": CURRENT,
    "migration_id": "test",
}


def _call(condition, *, provider="local", model="google/gemma-3-12b-it"):
    key = json.dumps({
        "condition": condition, "provider": provider, "model": model,
    }, sort_keys=True)
    return {"key": key, "condition": condition,
            "provenance": {"git_commit": SOURCE_COMMIT}}


def test_local_migration_preserves_shared_calls_and_retires_old_judge_revisions():
    shared = _call("shared_rag_initial")
    old_retry = _call(OLD_CONDITION)
    active, retired = partition_rows(
        [shared, old_retry], kind="local", current_commit=CURRENT,
        migration_provenance=MIGRATION,
    )
    assert len(active) == len(retired) == 1
    assert active[0]["source_provenance"]["git_commit"] == SOURCE_COMMIT
    assert active[0]["provenance"]["git_commit"] == CURRENT
    assert json.loads(retired[0]["key"])["condition"] == OLD_CONDITION
    assert retired[0]["superseded"]["replacement_condition"] == NEW_CONDITION


def test_every_old_hosted_judge_call_is_superseded():
    row = _call(OLD_CONDITION, provider="gemini", model="gemini-3.6-flash")
    active, retired = partition_rows(
        [row], kind="gemini", current_commit=CURRENT,
        migration_provenance=MIGRATION,
    )
    assert active == [] and len(retired) == 1


def test_case_migration_keeps_other_conditions_only():
    rows = [
        {"key": "old", "condition": OLD_CONDITION,
         "provenance": {"git_commit": SOURCE_COMMIT}},
        {"key": "keep", "condition": "zero_shot",
         "provenance": {"git_commit": SOURCE_COMMIT}},
    ]
    active, retired = partition_rows(
        rows, kind="case", current_commit=CURRENT,
        migration_provenance=MIGRATION,
    )
    assert [x["key"] for x in active] == ["keep"]
    assert [x["key"] for x in retired] == ["old"]


def test_unknown_checkpoint_commit_is_refused():
    row = _call("zero_shot")
    row["provenance"]["git_commit"] = "unknown-source"
    with pytest.raises(CheckpointMigrationError, match="unsupported commit"):
        partition_rows(
            [row], kind="local", current_commit=CURRENT,
            migration_provenance=MIGRATION,
        )
