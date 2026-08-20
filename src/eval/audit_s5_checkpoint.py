#!/usr/bin/env python3
"""Read-only integrity audit and handoff report for an exported S5 checkpoint.

The generator itself owns resumption.  This tool never edits an archive; it
proves what is present, rejects malformed/mixed provenance, and reports the
earliest chunk boundary that is safe to rerun after an interruption.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import write_result
from src.common.seed import set_seed
from src.eval.s5_contract import CONDITIONS, REPLICATE_SEEDS, load_eval_plots


class S5CheckpointAuditError(RuntimeError):
    """The archive cannot safely be described as a resumable S5 checkpoint."""


def _rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    output: list[dict] = []
    keys: set[str] = set()
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            key = row["key"]
        except Exception as exc:
            raise S5CheckpointAuditError(f"invalid row {path.name}:{lineno}: {exc}") from exc
        if not isinstance(row, dict) or not isinstance(key, str) or key in keys:
            raise S5CheckpointAuditError(f"duplicate or invalid key {path.name}:{lineno}")
        keys.add(key)
        output.append(row)
    return output


def _commit(rows: list[dict], *, label: str) -> set[str]:
    commits = {row.get("provenance", {}).get("git_commit") for row in rows}
    if None in commits:
        raise S5CheckpointAuditError(f"{label} contains a row without provenance.git_commit")
    return commits


def audit_checkpoint(
    checkpoint_dir: str | Path, config_path: str | Path, *, seed: int = 42,
    chunk_size: int = 20, expected_commit: str | None = None,
) -> dict:
    """Audit active S5 archives without loading a model or modifying data."""
    if seed not in REPLICATE_SEEDS:
        raise S5CheckpointAuditError(f"seed must be one of {REPLICATE_SEEDS}")
    if chunk_size < 1:
        raise S5CheckpointAuditError("chunk_size must be positive")

    root = Path(__file__).resolve().parents[2]
    cfg_path = Path(config_path)
    if not cfg_path.is_absolute():
        cfg_path = root / cfg_path
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    checkpoint = Path(checkpoint_dir)
    outputs = cfg["outputs"]
    local = _rows(checkpoint / Path(outputs["calls_jsonl"]).name)
    judge = _rows(checkpoint / Path(outputs["gemini_calls_jsonl"]).name)
    cases = _rows(checkpoint / Path(outputs["cases_jsonl"]).name)

    commits = set().union(
        _commit(local, label="local calls"), _commit(judge, label="judge calls"),
        _commit(cases, label="cases"),
    )
    if len(commits) > 1:
        raise S5CheckpointAuditError(f"mixed active runner commits: {sorted(commits)}")
    commit = next(iter(commits), None)
    if expected_commit is not None and commit != expected_commit:
        raise S5CheckpointAuditError(
            f"checkpoint commit {commit!r}, expected {expected_commit!r}"
        )

    plots = load_eval_plots(root / cfg["inputs"]["plots_csv"])
    base_cases = [(plot.plot_id, int(level)) for plot in plots for level in cfg["sample"]["levels"]]
    known = {
        f"S5BN|s{seed}|{plot_id}|L{level}|{condition}"
        for plot_id, level in base_cases for condition in CONDITIONS
    }
    completed: set[str] = set()
    for row in cases:
        row_seed = row.get("replicate_seed")
        if row_seed not in REPLICATE_SEEDS:
            raise S5CheckpointAuditError(f"case has invalid replicate seed: {row_seed!r}")
        if row.get("condition") not in CONDITIONS:
            raise S5CheckpointAuditError(f"case has unknown condition: {row.get('condition')!r}")
        if row.get("verifier_b_score") is not None:
            raise S5CheckpointAuditError("Verifier-B score appeared in an S5 generation checkpoint")
        if row.get("provenance", {}).get("verifier_b_loaded") is not False:
            raise S5CheckpointAuditError("S5 case does not prove that Verifier-B stayed unloaded")
        if row_seed == seed:
            if row["key"] not in known:
                raise S5CheckpointAuditError(f"case outside frozen seed-{seed} surface: {row['key']}")
            completed.add(row["key"])

    complete_base, partial_base = 0, 0
    first_missing: int | None = None
    for offset, (plot_id, level) in enumerate(base_cases):
        wanted = {f"S5BN|s{seed}|{plot_id}|L{level}|{condition}" for condition in CONDITIONS}
        n_done = len(wanted & completed)
        if n_done == len(CONDITIONS):
            complete_base += 1
        elif n_done:
            partial_base += 1
            first_missing = offset if first_missing is None else first_missing
        elif first_missing is None:
            first_missing = offset

    resume_start = None if first_missing is None else (first_missing // chunk_size) * chunk_size
    return {
        "status": "S5_CHECKPOINT_AUDIT_PASS",
        "checkpoint_dir": str(checkpoint),
        "runner_commit": commit,
        "seed": seed,
        "archive_rows": {"local_calls": len(local), "hosted_judge_calls": len(judge), "cases": len(cases)},
        "seed_condition_counts": dict(sorted(Counter(row["condition"] for row in cases if row.get("replicate_seed") == seed).items())),
        "seed_progress": {
            "base_cases_total": len(base_cases),
            "base_cases_complete": complete_base,
            "base_cases_partial": partial_base,
            "condition_cases_complete": len(completed),
            "condition_cases_total": len(base_cases) * len(CONDITIONS),
        },
        "next_handoff": {
            "earliest_incomplete_base_case": first_missing,
            "safe_resume_start": resume_start,
            "safe_resume_limit": chunk_size if resume_start is not None else 0,
        },
    }


def main() -> int:
    set_seed()
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint-dir", required=True)
    parser.add_argument("--config", default="configs/s5_main_bn.yaml")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--chunk-size", type=int, default=20)
    parser.add_argument("--expected-commit")
    parser.add_argument("--out", help="optional provenance-stamped JSON report")
    args = parser.parse_args()
    report = audit_checkpoint(
        args.checkpoint_dir, args.config, seed=args.seed, chunk_size=args.chunk_size,
        expected_commit=args.expected_commit,
    )
    if args.out:
        write_result(report, args.out, args.config)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
