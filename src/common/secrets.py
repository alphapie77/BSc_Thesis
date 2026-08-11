#!/usr/bin/env python3
"""Read API keys from `.env`, and refuse to let one reach a result file.

Sabbir's choice, 2026-08-11: keys live in `.env` rather than in the shell
environment. `.env` is already on line 39 of `.gitignore` and nothing matching
it has ever been tracked -- both checked before this file was written.

WHY A TEN-LINE READER INSTEAD OF `python-dotenv`
------------------------------------------------
Adding a dependency means editing `requirements.in`, reinstalling, and
regenerating `requirements.lock.txt` -- and the lock is a provenance artifact
that appears in the appendix. A parser this small is not worth that, and it is
also fewer moving parts in the one file that touches secrets.

THE PART THAT MATTERS MORE THAN THE PARSING
-------------------------------------------
`redact()` exists because Phase 4 writes JSONL traces of every attempt, and a
trace is the one artifact designed to record *everything*. A key that reaches a
config dump, an error message, or a provenance stamp is in git forever, and
deleting it later does not remove it from history. So the key is fetched at the
call site and never stored on a config object.

Nothing here is clever. This file is an appendix artifact a reviewer may read to
check that the secret handling is real.
"""

from __future__ import annotations

import os
from pathlib import Path

#: Where the key lives. Repo root, gitignored.
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

#: How much of a key may appear in a log line, ever.
_VISIBLE_PREFIX = 4


class MissingSecretError(RuntimeError):
    """Raised when a required key is absent. Names the fix, not just the fault."""


def load_env(path: str | Path = ENV_FILE, *, override: bool = False) -> dict[str, str]:
    """Parse `KEY=value` lines into os.environ. Returns what it set.

    Deliberately does NOT override an existing environment variable unless asked:
    if someone has already exported a key for this shell, a file on disk should
    not silently replace it. Blank lines, `#` comments and surrounding quotes are
    handled; nothing else is, because nothing else is needed.
    """
    path = Path(path)
    loaded: dict[str, str] = {}
    if not path.exists():
        return loaded
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue
        if override or key not in os.environ:
            os.environ[key] = value
        loaded[key] = value
    return loaded


def require(name: str) -> str:
    """Return a secret or raise with the instructions for fixing it."""
    load_env()
    value = os.environ.get(name, "").strip()
    if not value:
        raise MissingSecretError(
            f"{name} is not set.\n"
            f"  Create {ENV_FILE} containing a single line:\n"
            f"      {name}=your_key_here\n"
            f"  It is gitignored (.gitignore line 39). Never commit it, and if a\n"
            f"  key is ever exposed, revoke it in the provider console rather\n"
            f"  than deleting the file -- git history keeps what was committed."
        )
    return value


def redact(text: str, *, secrets: list[str] | None = None) -> str:
    """Replace any known secret in `text` with a stub before it is written.

    Every Phase 4 artifact that could contain a prompt, a config echo, an error
    or a provenance stamp goes through this. The JSONL trace is the reason: it
    is designed to record everything about an attempt, which is exactly the
    property that makes it dangerous.
    """
    values = secrets if secrets is not None else _known_secret_values()
    out = text
    for value in values:
        if value and len(value) > _VISIBLE_PREFIX:
            out = out.replace(value, f"{value[:_VISIBLE_PREFIX]}...REDACTED")
    return out


def _known_secret_values() -> list[str]:
    """Values of anything in the environment whose name looks like a secret."""
    markers = ("API_KEY", "TOKEN", "SECRET", "PASSWORD")
    return [
        v
        for k, v in os.environ.items()
        if any(m in k.upper() for m in markers) and v.strip()
    ]
