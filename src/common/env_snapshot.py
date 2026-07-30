"""Install latest -> then FREEZE. Run once after every deliberate dependency change.

Rationale: the pipeline requires pinned versions in the appendix, but pinning by
hand goes stale. So we install latest, then capture exactly what landed.

Two modes, because this pipeline runs on two hosts:

* **No arguments** — the canonical local freeze. Overwrites the committed
  `requirements.lock.txt` and `results/env_snapshot.json`. Run this on the
  machine that owns the dependency set (Windows, locally).

* **`--out <path>`** — a *read-only-to-the-lock* snapshot. Records the current
  environment to `<path>` and does NOT touch `requirements.lock.txt`. This is
  the mode for a remote host (Kaggle), where the installed versions are the
  host's, not ours.

The distinction exists because a result must be attributable to the environment
that actually produced it. Running the no-argument mode on Kaggle would replace
the record of the local environment with a Linux freeze, and every earlier result
would then point at a lock file describing a machine it never ran on.

Usage:
    python src/common/env_snapshot.py
    python src/common/env_snapshot.py --out results/env_snapshot_s2_kaggle.json \\
        --note "Kaggle T4, S2 pilot run"
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.common.provenance import stamp, write_text_lf  # noqa: E402

KEY = [
    "numpy", "pandas", "scipy", "scikit-learn", "torch", "transformers",
    "sentence-transformers", "hdbscan", "umap-learn", "langgraph", "chromadb",
    "statsmodels", "mauve-text", "netcal",
]


def _freeze() -> str:
    return subprocess.check_output(
        [sys.executable, "-m", "pip", "freeze"]
    ).decode()


def _key_versions(freeze: str) -> dict:
    versions = {}
    for line in freeze.splitlines():
        if "==" in line:
            name, ver = line.split("==", 1)
            if name.lower() in KEY:
                versions[name.lower()] = ver
    return versions


def _gpu() -> dict:
    """Record the accelerator, if any. Part of 'which machine produced this'."""
    try:
        import torch
    except Exception:
        return {"torch": "not installed"}
    info = {"torch": torch.__version__, "cuda_available": bool(torch.cuda.is_available())}
    if info["cuda_available"]:
        info["cuda_version"] = torch.version.cuda
        info["device_name"] = torch.cuda.get_device_name(0)
        info["device_count"] = torch.cuda.device_count()
    return info


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out",
        help=(
            "write the snapshot here and DO NOT touch requirements.lock.txt. "
            "Use this on any host that is not the canonical local machine."
        ),
    )
    ap.add_argument("--note", default="", help="free-text host description")
    args = ap.parse_args()

    freeze = _freeze()
    versions = _key_versions(freeze)

    extra = {"accelerator": _gpu()}
    if args.note:
        extra["note"] = args.note

    if args.out:
        # Remote/secondary host: snapshot only. The lock file is the local
        # machine's record and must not be overwritten from here.
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = ROOT / out_path
        if out_path.name == "requirements.lock.txt":
            sys.exit(
                "--out must not target requirements.lock.txt. That file is the "
                "canonical local freeze; use no-argument mode on the local "
                "machine to regenerate it."
            )
        payload = {
            "_provenance": stamp(extra=extra),
            "mode": "snapshot_only (requirements.lock.txt NOT modified)",
            "key_versions": versions,
            "pip_freeze": freeze.splitlines(),
        }
        write_text_lf(out_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        print(f"wrote {out_path} (snapshot only; lock file untouched)")
    else:
        write_text_lf(ROOT / "requirements.lock.txt", freeze)
        payload = {"_provenance": stamp(extra=extra), "key_versions": versions}
        write_text_lf(
            ROOT / "results" / "env_snapshot.json",
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        )
        print("wrote requirements.lock.txt and results/env_snapshot.json")

    for k, v in sorted(versions.items()):
        print(f"  {k:24s} {v}")
    acc = extra["accelerator"]
    print(f"  {'accelerator':24s} {acc.get('device_name', 'CPU / none')}")
    missing = [k for k in KEY if k not in versions]
    if missing:
        print("\nNOT INSTALLED (fine if that phase hasn't started):", ", ".join(missing))


if __name__ == "__main__":
    main()
