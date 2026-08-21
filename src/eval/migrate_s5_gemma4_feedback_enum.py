#!/usr/bin/env python3
"""Restart only S5 row 8 after the observed unbounded-feedback API failure.

The 2026-08-21 checkpoint proves that Gemma-4 can hit its output cap while
repeating free-text feedback.  This migration retires the affected row-8
judgments, their conditioned Writer retries, their partial transport responses,
and their condition rows.  The nine unaffected conditions retain their emitted
drafts, exact source provenance, and resume value.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import git_hash, stamp, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402


# Both clean checkpoints used the same unbounded row-8 feedback interface.
# The 2e archive predates transport-failure archiving; 19f adds that sidecar.
# Either may be safely partitioned into the repaired row-8 restart.
SOURCE_COMMITS = (
    "2e919895975da75b2d6e0cfc25c4b0bdc4d7475e",
    "19fbee01d0a584f13a8e6f4f4d615729d71bad21",
)
CONDITION = "gemma4_26b_a4b_judge_loop"
MIGRATION_ID = "s5_gemma4_feedback_enum_v1"


class S5FeedbackEnumMigrationError(RuntimeError):
    pass


def _read(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    rows, seen = [], set()
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            key = row["key"]
        except Exception as exc:
            raise S5FeedbackEnumMigrationError(f"invalid {path}:{lineno}: {exc}") from exc
        if not isinstance(key, str) or key in seen:
            raise S5FeedbackEnumMigrationError(f"duplicate or invalid key {path}:{lineno}")
        seen.add(key)
        rows.append(row)
    return rows


def _write(path: Path, rows: list[dict]) -> None:
    write_text_lf(path, "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))


def _condition(row: dict) -> str | None:
    value = row.get("condition")
    if isinstance(value, str):
        return value
    try:
        key = json.loads(row["key"].split("|transport_incomplete=", 1)[0])
    except (KeyError, TypeError, json.JSONDecodeError):
        return None
    return key.get("condition") if isinstance(key, dict) else None


def partition_rows(
    rows: list[dict], *, destination_commit: str, migration: dict,
) -> tuple[list[dict], list[dict]]:
    active, retired = [], []
    for original in rows:
        row = deepcopy(original)
        provenance = row.get("provenance")
        source = provenance.get("git_commit") if isinstance(provenance, dict) else None
        if source == destination_commit:
            active.append(row)
            continue
        if source not in SOURCE_COMMITS:
            raise S5FeedbackEnumMigrationError(
                f"unsupported checkpoint commit {source!r}; expected one of "
                f"{SOURCE_COMMITS!r} or destination {destination_commit!r}"
            )
        if _condition(row) == CONDITION:
            row["source_provenance"] = provenance
            row["superseded"] = {
                **migration,
                "reason": "unbounded_feedback_hit_output_cap",
                "replacement_feedback_contract": "enum_target_template_v1",
            }
            retired.append(row)
            continue
        row["source_provenance"] = provenance
        row["provenance"] = {
            **provenance,
            **migration,
            "git_commit": destination_commit,
            "stage": "checkpoint_migration",
            "scientific_generation_unchanged": True,
        }
        active.append(row)
    return active, retired


def migrate(root: Path, cfg: dict) -> dict:
    destination = git_hash()
    if destination.endswith("-dirty") or destination == "unknown":
        raise S5FeedbackEnumMigrationError(
            f"migration requires a clean committed runner, found {destination!r}"
        )
    migration = stamp("configs/s5_main_bn.yaml", {
        "migration_id": MIGRATION_ID,
        "source_git_commits": list(SOURCE_COMMITS),
        "destination_git_commit": destination,
    })
    outputs = cfg["outputs"]
    pairs = [
        (outputs["calls_jsonl"], outputs["superseded_gemma4_feedback_v1_calls_jsonl"]),
        (outputs["gemini_calls_jsonl"], outputs["superseded_gemma4_feedback_v1_judge_calls_jsonl"]),
        (outputs["gemini_transport_failures_jsonl"], outputs["superseded_gemma4_feedback_v1_transport_failures_jsonl"]),
        (outputs["cases_jsonl"], outputs["superseded_gemma4_feedback_v1_cases_jsonl"]),
    ]
    report = {}
    for active_name, retired_name in pairs:
        active_path, retired_path = root / active_name, root / retired_name
        active, retired = partition_rows(
            _read(active_path), destination_commit=destination, migration=migration,
        )
        existing_retired = _read(retired_path)
        known = {row["key"] for row in existing_retired}
        existing_retired.extend(row for row in retired if row["key"] not in known)
        _write(active_path, active)
        _write(retired_path, existing_retired)
        report[active_path.name] = {"active": len(active), "superseded": len(retired)}
    return {
        "migration_id": MIGRATION_ID,
        "source_commits": list(SOURCE_COMMITS),
        "destination_commit": destination,
        "files": report,
    }


def main() -> int:
    set_seed()
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/s5_main_bn.yaml")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    cfg = yaml.safe_load((root / args.config).read_text(encoding="utf-8"))
    print(json.dumps(migrate(root, cfg), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
