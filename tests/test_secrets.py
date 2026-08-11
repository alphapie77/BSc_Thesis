"""Guard the one file that touches secrets.

The redaction test is the load-bearing one. Phase 4 writes a JSONL trace of
every attempt, and a trace is *designed* to record everything — which is exactly
what makes it the likeliest place for a key to end up in git. Deleting a
committed key later does not remove it from history.

Run:  python -m pytest tests/test_secrets.py -q
      python tests/test_secrets.py          (no pytest needed)
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.common.secrets import (  # noqa: E402
    MissingSecretError,
    load_env,
    redact,
    require,
)


def _tmp_env(body: str) -> str:
    fh = tempfile.NamedTemporaryFile("w", suffix=".env", delete=False, encoding="utf-8")
    fh.write(body)
    fh.close()
    return fh.name


def test_parses_keys_comments_blanks_and_quotes():
    path = _tmp_env(
        "# a comment\n"
        "\n"
        'GROQ_API_KEY="gsk_quoted"\n'
        "OTHER_KEY = plain \n"
        "malformed line without equals\n"
    )
    os.environ.pop("GROQ_API_KEY", None)
    os.environ.pop("OTHER_KEY", None)
    loaded = load_env(path)
    assert loaded["GROQ_API_KEY"] == "gsk_quoted", loaded
    assert loaded["OTHER_KEY"] == "plain", loaded
    assert "malformed line without equals" not in loaded


def test_does_not_silently_override_an_exported_variable():
    """A file on disk must not replace what the shell already set."""
    path = _tmp_env("GROQ_API_KEY=from_file\n")
    os.environ["GROQ_API_KEY"] = "from_shell"
    load_env(path)
    assert os.environ["GROQ_API_KEY"] == "from_shell"
    load_env(path, override=True)
    assert os.environ["GROQ_API_KEY"] == "from_file"


def test_missing_secret_names_the_fix_not_just_the_fault():
    os.environ.pop("DEFINITELY_ABSENT_KEY", None)
    try:
        require("DEFINITELY_ABSENT_KEY")
    except MissingSecretError as exc:
        msg = str(exc)
        assert ".env" in msg and "gitignore" in msg and "revoke" in msg, msg
        return
    raise AssertionError("require() returned for an absent secret")


def test_redact_removes_a_key_from_text():
    """The one that matters: a key must not survive into a written artifact."""
    key = "gsk_abcdefghijklmnop"
    os.environ["GROQ_API_KEY"] = key
    line = f'{{"error": "auth failed for {key}", "attempt": 2}}'
    out = redact(line)
    assert key not in out, "the full key survived redaction"
    assert "gsk_...REDACTED" in out, out


def test_redact_finds_secrets_by_name_pattern():
    os.environ["SOMETHING_TOKEN"] = "tok_verysecretvalue"
    assert "tok_verysecretvalue" not in redact("leaked tok_verysecretvalue here")


def test_redact_ignores_short_values_rather_than_mangling_text():
    """A 3-character 'secret' would otherwise redact ordinary words."""
    os.environ["TINY_API_KEY"] = "abc"
    assert redact("abc appears in ordinary text") == "abc appears in ordinary text"


def _run_all() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL  {fn.__name__}\n        {exc}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run_all())
