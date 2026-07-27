"""Every result file must be able to answer: which code, which config, when?"""
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path


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
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"_provenance": stamp(config_path), "result": obj}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
