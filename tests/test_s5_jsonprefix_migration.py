from src.eval.migrate_s5_checkpoint_jsonprefix import (
    MIGRATION_ID,
    PARSER_REPAIR_COMMIT,
    SOURCE_COMMIT,
    S5JsonPrefixMigrationError,
    migrate_rows,
)


DESTINATION = "f" * 40
MIGRATION = {
    "migration_id": MIGRATION_ID,
    "source_git_commit": SOURCE_COMMIT,
    "destination_git_commit": DESTINATION,
}


def test_migration_preserves_row_and_records_the_exact_source_provenance():
    row = {"key": "k", "text": "অপরিবর্তিত", "provenance": {"git_commit": SOURCE_COMMIT}}
    migrated = migrate_rows([row], destination_commit=DESTINATION, migration=MIGRATION)
    assert migrated[0]["text"] == "অপরিবর্তিত"
    assert migrated[0]["source_provenance"] == row["provenance"]
    assert migrated[0]["provenance"]["git_commit"] == DESTINATION
    assert migrated[0]["provenance"]["scientific_generation_unchanged"] is True


def test_migration_refuses_unknown_checkpoint_commit():
    row = {"key": "k", "provenance": {"git_commit": "unknown"}}
    try:
        migrate_rows([row], destination_commit=DESTINATION, migration=MIGRATION)
    except S5JsonPrefixMigrationError as exc:
        assert "unsupported checkpoint commit" in str(exc)
    else:
        raise AssertionError("unknown source commit must be refused")


def test_migration_accepts_the_parser_repair_checkpoint_for_transport_retry_repair():
    row = {"key": "k", "provenance": {"git_commit": PARSER_REPAIR_COMMIT}}
    migrated = migrate_rows([row], destination_commit=DESTINATION, migration=MIGRATION)
    assert migrated[0]["provenance"]["git_commit"] == DESTINATION
