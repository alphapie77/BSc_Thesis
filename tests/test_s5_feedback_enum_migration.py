import json

from src.eval.migrate_s5_gemma4_feedback_enum import (
    CONDITION, SOURCE_COMMITS, partition_rows,
)


def _row(condition: str, commit: str = SOURCE_COMMITS[0]) -> dict:
    return {
        "key": json.dumps({"condition": condition}, sort_keys=True),
        "condition": condition,
        "provenance": {"git_commit": commit},
    }


def test_only_affected_row_eight_is_retired_and_other_conditions_migrate():
    active, retired = partition_rows(
        [_row("zero_shot"), _row(CONDITION)],
        destination_commit="new-clean", migration={"migration_id": "test"},
    )
    assert [row["condition"] for row in active] == ["zero_shot"]
    assert active[0]["provenance"]["git_commit"] == "new-clean"
    assert active[0]["provenance"]["scientific_generation_unchanged"] is True
    assert [row["condition"] for row in retired] == [CONDITION]
    assert retired[0]["superseded"]["replacement_feedback_contract"] == "enum_target_template_v1"


def test_transport_retry_checkpoint_is_also_an_allowed_source():
    active, retired = partition_rows(
        [_row("zero_shot", SOURCE_COMMITS[1]), _row(CONDITION, SOURCE_COMMITS[1])],
        destination_commit="new-clean", migration={"migration_id": "test"},
    )
    assert len(active) == len(retired) == 1
