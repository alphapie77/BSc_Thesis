#!/usr/bin/env python3
"""Migrate the clean Gemini-3.6 S5 checkpoint to the Gemma-4 judge row.

All non-judge treatments are byte-preserved. The old judge cases, hosted judge
responses, and judge-conditioned local revisions are retained in explicit
``superseded`` archives and excluded from the active checkpoint. Migration is
idempotent and refuses unknown source commits.
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


SOURCE_COMMIT = "510a95c41151f9a251e6e5528ae6a25b323064f1"
OLD_CONDITION = "gemini_judge_loop"
NEW_CONDITION = "gemma4_26b_a4b_judge_loop"
MIGRATION_ID = "s5_gemini36_to_gemma4_26b_a4b_v1"


class CheckpointMigrationError(RuntimeError):
    pass


def _read_rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    rows = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            if not isinstance(row, dict) or "key" not in row:
                raise ValueError("row is not an object with a key")
        except Exception as exc:
            raise CheckpointMigrationError(
                f"invalid checkpoint row {path}:{lineno}: {exc}"
            ) from exc
        rows.append(row)
    keys = [row["key"] for row in rows]
    if len(keys) != len(set(keys)):
        raise CheckpointMigrationError(f"duplicate keys in {path}")
    return rows


def _write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    write_text_lf(path, body)


def _condition(row: dict, kind: str) -> str | None:
    if kind == "gemini":
        try:
            return json.loads(row["key"]).get("condition")
        except Exception as exc:
            raise CheckpointMigrationError(f"invalid Gemini call key: {exc}") from exc
    if kind == "local":
        try:
            return json.loads(row["key"]).get("condition")
        except Exception as exc:
            raise CheckpointMigrationError(f"invalid local call key: {exc}") from exc
    if kind == "case":
        return row.get("condition")
    raise AssertionError(kind)


def partition_rows(
    rows: list[dict], *, kind: str, current_commit: str, migration_provenance: dict,
) -> tuple[list[dict], list[dict]]:
    """Return active and superseded rows, refusing ambiguous provenance."""
    active, superseded = [], []
    for original in rows:
        row = deepcopy(original)
        commit = row.get("provenance", {}).get("git_commit")
        condition = _condition(row, kind)
        if commit == current_commit:
            if condition == OLD_CONDITION:
                raise CheckpointMigrationError(
                    "current-commit checkpoint still contains the retired Gemini-3.6 condition"
                )
            active.append(row)
            continue
        if commit != SOURCE_COMMIT:
            raise CheckpointMigrationError(
                f"checkpoint row came from unsupported commit {commit!r}; expected "
                f"{SOURCE_COMMIT!r} or current {current_commit!r}"
            )

        retire = kind == "gemini" or condition == OLD_CONDITION
        if retire:
            row["superseded"] = {
                **migration_provenance,
                "reason": "Gemini-3.6 quota replacement; never reused by Gemma-4 row",
                "replacement_condition": NEW_CONDITION,
            }
            superseded.append(row)
        else:
            row["source_provenance"] = row["provenance"]
            row["provenance"] = {
                **migration_provenance,
                "stage": "checkpoint_migration",
                "scientific_generation_unchanged": True,
            }
            active.append(row)
    return active, superseded


def _merge_superseded(path: Path, incoming: list[dict]) -> list[dict]:
    merged = {row["key"]: row for row in _read_rows(path)}
    for row in incoming:
        existing = merged.get(row["key"])
        if existing is not None and existing != row:
            raise CheckpointMigrationError(
                f"conflicting superseded row for key {row['key']} in {path}"
            )
        merged[row["key"]] = row
    return list(merged.values())


def migrate(root: Path, cfg: dict) -> dict:
    current = git_hash()
    if current.endswith("-dirty") or current == "unknown":
        raise CheckpointMigrationError(
            f"migration requires a clean committed runner, found {current!r}"
        )
    migration_provenance = stamp(
        "configs/s5_main_bn.yaml",
        {
            "migration_id": MIGRATION_ID,
            "source_git_commit": SOURCE_COMMIT,
            "destination_git_commit": current,
        },
    )
    outputs = cfg["outputs"]
    specs = (
        ("local", outputs["calls_jsonl"], outputs["superseded_gemini36_writer_calls_jsonl"]),
        ("gemini", outputs["gemini_calls_jsonl"], outputs["superseded_gemini36_calls_jsonl"]),
        ("case", outputs["cases_jsonl"], outputs["superseded_gemini36_cases_jsonl"]),
    )
    report = {}
    for kind, active_name, superseded_name in specs:
        active_path = root / active_name
        superseded_path = root / superseded_name
        rows = _read_rows(active_path)
        active, retired = partition_rows(
            rows, kind=kind, current_commit=current,
            migration_provenance=migration_provenance,
        )
        archived = _merge_superseded(superseded_path, retired)
        _write_rows(active_path, active)
        if archived:
            _write_rows(superseded_path, archived)
        report[kind] = {
            "input": len(rows), "active": len(active),
            "newly_superseded": len(retired), "superseded_archive": len(archived),
        }
    return {
        "migration_id": MIGRATION_ID,
        "source_commit": SOURCE_COMMIT,
        "destination_commit": current,
        "files": report,
    }


def main() -> int:
    set_seed()  # inviolable global-seed rule; first action in the entry point
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s5_main_bn.yaml")
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[2]
    cfg = yaml.safe_load((root / args.config).read_text(encoding="utf-8"))
    print(json.dumps(migrate(root, cfg), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
