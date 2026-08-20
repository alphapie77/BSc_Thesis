#!/usr/bin/env python3
"""Migrate the clean Gemma-4 S5 checkpoint across the JSON-prefix parser repair.

The repair changes only how a provider's valid JSON prefix is decoded.  It does
not alter prompts, sampling, models, gates, or any generated text.  Because S5
requires an exact clean runner commit, this explicit one-source migration is
the only permitted way to resume the affected checkpoint.
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


SOURCE_COMMIT = "9e00d2e2b2f757166ead317a5eb9139b4d67f737"
MIGRATION_ID = "s5_gemma4_json_prefix_parser_v1"


class S5JsonPrefixMigrationError(RuntimeError):
    pass


def _read_rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    rows: list[dict] = []
    keys: set[str] = set()
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            key = row["key"]
        except Exception as exc:
            raise S5JsonPrefixMigrationError(
                f"invalid checkpoint row {path}:{lineno}: {exc}"
            ) from exc
        if not isinstance(row, dict) or not isinstance(key, str) or key in keys:
            raise S5JsonPrefixMigrationError(f"duplicate or invalid key {path}:{lineno}")
        keys.add(key)
        rows.append(row)
    return rows


def _write_rows(path: Path, rows: list[dict]) -> None:
    body = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    write_text_lf(path, body)


def migrate_rows(rows: list[dict], *, destination_commit: str, migration: dict) -> list[dict]:
    migrated: list[dict] = []
    for original in rows:
        row = deepcopy(original)
        provenance = row.get("provenance")
        source_commit = provenance.get("git_commit") if isinstance(provenance, dict) else None
        if source_commit == destination_commit:
            migrated.append(row)
            continue
        if source_commit != SOURCE_COMMIT:
            raise S5JsonPrefixMigrationError(
                f"unsupported checkpoint commit {source_commit!r}; expected "
                f"{SOURCE_COMMIT!r} or destination {destination_commit!r}"
            )
        row["source_provenance"] = provenance
        row["provenance"] = {
            **provenance,
            **migration,
            "git_commit": destination_commit,
            "stage": "checkpoint_migration",
            "scientific_generation_unchanged": True,
        }
        migrated.append(row)
    return migrated


def migrate(root: Path, cfg: dict) -> dict:
    destination = git_hash()
    if destination.endswith("-dirty") or destination == "unknown":
        raise S5JsonPrefixMigrationError(
            f"migration requires a clean committed runner, found {destination!r}"
        )
    migration = stamp(
        "configs/s5_main_bn.yaml",
        {
            "migration_id": MIGRATION_ID,
            "source_git_commit": SOURCE_COMMIT,
            "destination_git_commit": destination,
        },
    )
    paths = [
        root / cfg["outputs"]["calls_jsonl"],
        root / cfg["outputs"]["gemini_calls_jsonl"],
        root / cfg["outputs"]["cases_jsonl"],
    ]
    report = {}
    for path in paths:
        rows = _read_rows(path)
        rewritten = migrate_rows(rows, destination_commit=destination, migration=migration)
        _write_rows(path, rewritten)
        report[path.name] = {"rows": len(rewritten)}
    return {
        "migration_id": MIGRATION_ID,
        "source_commit": SOURCE_COMMIT,
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
