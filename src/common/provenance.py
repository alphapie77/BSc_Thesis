"""Every result file must be able to answer: which code, which config, when?"""
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


def git_hash() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        )
        dirty = subprocess.check_output(
            ["git", "status", "--porcelain"], stderr=subprocess.DEVNULL
        )
        return out.decode().strip() + ("-dirty" if dirty.strip() else "")
    except Exception:
        return "unknown"


def stamp(config_path: str | None = None, extra: dict | None = None) -> dict:
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_hash(),
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
