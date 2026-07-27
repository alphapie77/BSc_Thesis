"""Install latest -> then FREEZE. Run once after every deliberate dependency change.

Rationale: the pipeline requires pinned versions in the appendix, but pinning by
hand goes stale. So we install latest, then capture exactly what landed.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.common.provenance import stamp  # noqa: E402

KEY = [
    "numpy", "pandas", "scipy", "scikit-learn", "torch", "transformers",
    "sentence-transformers", "hdbscan", "umap-learn", "langgraph", "chromadb",
    "statsmodels", "mauve-text", "netcal",
]


def main() -> None:
    freeze = subprocess.check_output(
        [sys.executable, "-m", "pip", "freeze"]
    ).decode()
    (ROOT / "requirements.lock.txt").write_text(freeze, encoding="utf-8")

    versions = {}
    for line in freeze.splitlines():
        if "==" in line:
            name, ver = line.split("==", 1)
            if name.lower() in KEY:
                versions[name.lower()] = ver

    out = {"_provenance": stamp(), "key_versions": versions}
    p = ROOT / "results" / "env_snapshot.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print("wrote requirements.lock.txt and results/env_snapshot.json")
    for k, v in sorted(versions.items()):
        print(f"  {k:24s} {v}")
    missing = [k for k in KEY if k not in versions]
    if missing:
        print("\nNOT INSTALLED (fine if that phase hasn't started):", ", ".join(missing))


if __name__ == "__main__":
    main()
