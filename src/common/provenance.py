"""Every result file must be able to answer: which code, which config, when?"""
import csv
import io
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

#: Newline for every text artifact this repo writes.
#:
#: Python's text mode translates "\n" to os.linesep on write, so the SAME script
#: on the SAME data emits LF on Kaggle/Linux and CRLF on Windows. Git (with
#: core.autocrlf unset, which is this repo's state) records that as a real diff:
#: a re-run then shows hundreds of changed lines with zero changed content, and
#: a genuinely changed number hides inside the noise. Byte-identical output
#: across hosts is part of the reproducibility contract, not cosmetics -- the
#: pipeline is explicitly meant to run on Windows locally and Linux on Kaggle.
#:
#: Every writer of a text artifact must pass this. See also `.gitattributes`,
#: which enforces the same thing at the git layer for anything that slips past.
NEWLINE = "\n"


def write_text_lf(path: str | Path, text: str) -> Path:
    """Write UTF-8 text with LF endings on every platform. See NEWLINE."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline=NEWLINE)
    return path


def _git(*args) -> str:
    return subprocess.check_output(
        ["git", *args], stderr=subprocess.DEVNULL
    ).decode()


def git_hash() -> str:
    """HEAD, suffixed `-dirty` only when a TRACKED file is modified.

    The suffix previously came from bare `git status --porcelain`, which also
    lists **untracked** files. Every run creates untracked artifacts -- its own
    outputs, caches, a copied input -- so every stamp came out `-dirty` and the
    flag stopped distinguishing anything. A signal that is always on is not a
    signal; the one case it exists to catch (a result produced from edited but
    uncommitted source) became invisible.

    `-uno` restricts the check to tracked modifications, which is the question
    the flag is actually asking. Untracked files are not ignored, merely
    reported separately -- see `untracked_files` in `stamp()`, because a new
    source file that was never committed is a real provenance gap and should
    not be silently dropped either.
    """
    try:
        head = _git("rev-parse", "HEAD").strip()
        modified = _git("status", "--porcelain", "-uno").strip()
        return head + ("-dirty" if modified else "")
    except Exception:
        return "unknown"


def untracked_count() -> int | None:
    """How many untracked files exist. None if git cannot answer."""
    try:
        out = _git("ls-files", "--others", "--exclude-standard").strip()
        return len(out.splitlines()) if out else 0
    except Exception:
        return None


def stamp(config_path: str | None = None, extra: dict | None = None) -> dict:
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_hash(),
        # Reported alongside, never folded into git_commit. A non-zero count is
        # not necessarily a problem (run outputs are untracked by design), but
        # it is the reader's business, not something to hide behind a flag.
        "untracked_files": untracked_count(),
        "config": config_path,
        "python": platform.python_version(),
        "platform": platform.platform(),
        **(extra or {}),
    }


def write_result(obj: dict, path: str | Path, config_path: str | None = None) -> Path:
    """Write a result JSON with a provenance header attached."""
    payload = {"_provenance": stamp(config_path), "result": obj}
    # Trailing newline: a file without one shows as "\ No newline at end of file"
    # in every diff and makes appending a line look like editing the last one.
    return write_text_lf(
        path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    )


def write_csv_result(
    rows: list[dict],
    path: str | Path,
    fieldnames: list[str],
    config_path: str | None = None,
) -> Path:
    """Write a CSV whose every row carries the same provenance stamp.

    A sidecar is too easy to separate from the table it describes, and a
    comment preamble stops the file being an ordinary CSV. Repeating the six
    small provenance fields keeps the artifact self-describing while remaining
    readable by standard CSV tooling.
    """
    meta = stamp(config_path)
    provenance = {
        "_timestamp_utc": meta["timestamp_utc"],
        "_git_commit": meta["git_commit"],
        "_untracked_files": meta["untracked_files"],
        "_config": meta["config"],
        "_python": meta["python"],
        "_platform": meta["platform"],
    }
    provenance_fields = list(provenance)
    overlap = set(fieldnames) & set(provenance_fields)
    if overlap:
        raise ValueError(f"CSV fieldnames collide with provenance fields: {sorted(overlap)}")

    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=[*provenance_fields, *fieldnames])
    writer.writeheader()
    for row in rows:
        writer.writerow({**provenance, **{name: row[name] for name in fieldnames}})
    return write_text_lf(path, buf.getvalue())
