"""Close out a pipeline step: scaffold a lab-notebook entry, enforce the rest.

Design principle: this tool automates the SCAFFOLD and the ENFORCEMENT.
It never writes reasoning. Auto-generated justification is plausible-sounding
text nobody thought through -- the exact thing a reviewer catches.

Usage:
    python src/common/step_close.py --step S1 --title "rule-based cleaning" \
        --feeds "Ch.3 Preprocessing" --results results/s1_cleaning_log.json

Then FILL THE TODOs BY HAND before committing. `--check` refuses to pass while
any TODO remains.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.common.provenance import git_hash  # noqa: E402

NOTEBOOK = ROOT / "docs" / "lab_notebook.md"
RELATED = ROOT / "docs" / "related_work.md"
PROTOCOL = ROOT / "docs" / "protocol.md"
STATUS = ROOT / "docs" / "STATUS.md"
OPEN_MARKER = "## Open decisions"
LAST_UPDATED_RE = re.compile(r"\*\*Last updated:\*\* (\d{4}-\d{2}-\d{2})")

TEMPLATE = """
## {today} -- {step}: {title}
**Feeds:** {feeds}
**Commit:** `{commit}`
**Artifacts:** {artifacts}

### Numbers
{numbers}

### Decisions made (and why)
- TODO: what was decided, what the alternative was, why this one. One bullet per
  decision. If nothing was decided, write "None -- mechanical execution of {step}."

### Findings (things we did not expect)
- TODO: anything that contradicts the pipeline spec, the S0 table, or your prior.
  If nothing surprised you, write "None." -- but check twice before writing it.

### Consequences for downstream steps
- TODO: what must change because of the above. Cross-reference the deviations log
  if the pipeline spec is now wrong.

### Citations needed
- TODO: any method used here that needs a reference -> add to docs/related_work.md
  with status `[ ]`, and cite it in Ch.3 next to this decision.
"""


def _extract_numbers(paths: list[str]) -> str:
    """Pull top-level scalars out of result JSONs. Numbers only, never prose."""
    lines = []
    for p in paths:
        fp = ROOT / p
        lines.append(f"- `{p}`")
        if not fp.exists():
            lines.append("  - MISSING at scaffold time")
            continue
        if fp.suffix == ".json":
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
            except Exception as e:
                lines.append(f"  - unreadable: {e}")
                continue
            body = data.get("result", data)
            for k, v in body.items():
                if isinstance(v, (int, float, str, bool)):
                    lines.append(f"  - `{k}` = {v}")
                elif isinstance(v, dict) and all(
                    isinstance(x, (int, float, str, bool)) for x in v.values()
                ):
                    lines.append(f"  - `{k}` = {v}")
        else:
            lines.append(f"  - (see file; {fp.stat().st_size} bytes)")
    return "\n".join(lines) if lines else "- TODO: paste the key figures."


def scaffold(args) -> None:
    if not NOTEBOOK.exists():
        sys.exit("docs/lab_notebook.md not found.")
    text = NOTEBOOK.read_text(encoding="utf-8")
    entry = TEMPLATE.format(
        today=date.today().isoformat(),
        step=args.step,
        title=args.title,
        feeds=args.feeds or "TODO: which thesis section does this feed?",
        commit=git_hash(),
        artifacts=", ".join(f"`{r}`" for r in args.results) or "TODO",
        numbers=_extract_numbers(args.results),
    )
    # Insert above the "Open decisions" table so it stays last.
    if OPEN_MARKER in text:
        head, tail = text.split(OPEN_MARKER, 1)
        text = head.rstrip() + "\n\n---\n" + entry + "\n---\n\n" + OPEN_MARKER + tail
    else:
        text = text.rstrip() + "\n\n---\n" + entry
    NOTEBOOK.write_text(text, encoding="utf-8")
    print(f"Scaffolded {args.step} entry in docs/lab_notebook.md.")
    print("Now FILL THE TODOs BY HAND. `--check` will fail until you do.")


STATUS_NUDGE = (
    "Update the step row and the parallel-track counts (plot synopses, "
    "base-paper reading, gold-300) at the same time -- bumping the date "
    "alone just makes the staleness silent again."
)


def _staged_files() -> list[str]:
    try:
        return subprocess.check_output(
            ["git", "diff", "--cached", "--name-only"], stderr=subprocess.DEVNULL
        ).decode().split()
    except Exception:
        return []


def _todo_finding() -> str | None:
    if not NOTEBOOK.exists():
        return "docs/lab_notebook.md is missing."
    todos = [
        f"{NOTEBOOK.name}:{i}"
        for i, ln in enumerate(NOTEBOOK.read_text(encoding="utf-8").splitlines(), 1)
        if "TODO" in ln
    ]
    if not todos:
        return None
    return f"{len(todos)} unfilled TODO(s) in lab_notebook.md (first: {todos[0]})"


def _status_finding() -> str | None:
    if not STATUS.exists():
        return (
            "docs/STATUS.md is missing -- it is the single source of truth for "
            f"progress. {STATUS_NUDGE}"
        )
    m = LAST_UPDATED_RE.search(STATUS.read_text(encoding="utf-8"))
    if not m:
        return (
            "docs/STATUS.md has no '**Last updated:** YYYY-MM-DD' line, so "
            f"staleness cannot be checked. {STATUS_NUDGE}"
        )
    today = date.today().isoformat()
    if m.group(1) != today:
        return (
            f"docs/STATUS.md is stale: last updated {m.group(1)}, today is "
            f"{today}. {STATUS_NUDGE}"
        )
    return None


def check() -> int:
    """Block on what makes a result undefendable; warn about everything else.

    Blockers are scoped to the staged diff so routine work is not held hostage
    to end-of-step bookkeeping: a docs typo fix must not demand a STATUS date
    bump. Only a staged diff that touches `results/` or `src/` -- i.e. an actual
    step closing -- triggers the notebook and STATUS requirements.

    Warnings never block. `protocol.md` is legitimately unfrozen until after S2,
    and having read no papers yet is a real-but-not-committable problem; making
    either of them exit non-zero would train `--no-verify` into a reflex and
    destroy the one check that matters (a number committed without its
    reasoning).

    With nothing staged this is a manual status readout: everything is reported
    as informational and the exit code is 0.
    """
    staged = _staged_files()
    manual = not staged
    touches_code = any(
        f.startswith("results/") or f.startswith("src/") for f in staged
    )
    closing_a_step = touches_code and not manual

    todo = _todo_finding()
    status = _status_finding()
    orphan_results = (
        any(f.startswith("results/") for f in staged)
        and "docs/lab_notebook.md" not in staged
    )
    unfrozen = PROTOCOL.exists() and "Frozen at commit: ____" in PROTOCOL.read_text(
        encoding="utf-8"
    )
    no_paper_read = RELATED.exists() and "[x]" not in RELATED.read_text(
        encoding="utf-8"
    )

    blockers, warnings, info = [], [], []

    if orphan_results:
        blockers.append(
            "results/ is staged but docs/lab_notebook.md is not. A number "
            "without its reasoning is unusable in the thesis."
        )
    if todo:
        (blockers if closing_a_step else info).append(todo)
    if status:
        (blockers if closing_a_step else info).append(status)
    if unfrozen:
        warnings.append("protocol.md is still unfrozen (expected until after S2).")
    if no_paper_read:
        warnings.append("No paper marked [x] in docs/related_work.md yet.")

    if manual:
        # Nothing staged: pure readout. Blockers cannot apply -- they are all
        # defined against a staged diff.
        findings = info + warnings + blockers
        print("step_close --check (status readout; nothing staged)")
        if not findings:
            print("  nothing outstanding.")
        for f in findings:
            print(f"  - {f}")
        print("Exit 0: informational only. Blockers are evaluated at commit time.")
        return 0

    if blockers:
        print("step_close --check: BLOCKING")
        for b in blockers:
            print(f"  - {b}")
    for w in warnings:
        print(f"warning (not blocking): {w}")
    for i in info:
        print(f"note (not blocking here): {i}")

    if blockers:
        return 1
    scope = "step-closing diff" if closing_a_step else "docs-only diff"
    print(f"OK -- no blockers for this {scope}.")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", help="e.g. S1, S2")
    ap.add_argument("--title", default="")
    ap.add_argument("--feeds", default="")
    ap.add_argument("--results", nargs="*", default=[])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        sys.exit(check())
    if not args.step:
        ap.error("--step required unless --check")
    scaffold(args)


if __name__ == "__main__":
    main()
