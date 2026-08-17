#!/usr/bin/env python3
"""Read-only gate for S4.5a before the 240 generated texts are scored.

The first Kaggle attempt loaded the symbolic sklearn-1.9.0 pipeline under
sklearn 1.6.1. Joblib warned, construction continued, and predict_proba then
failed because the old LogisticRegression code expected ``multi_class`` on an
object written by the newer version. This gate checks the environment, both
archives, and an actual prediction from both halves of the Critic before the
full scoring pass begins. It writes nothing.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.critic import Critic  # noqa: E402
from src.common.seed import set_seed  # noqa: E402
from src.eval.fit_w import validate_inputs  # noqa: E402


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="configs/s4_w.yaml")
    args = ap.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))

    import sklearn

    required = str(cfg["runtime"]["scikit_learn"])
    if sklearn.__version__ != required:
        raise SystemExit(
            "REFUSED: symbolic scorer requires scikit-learn "
            f"{required}; this runtime has {sklearn.__version__}."
        )

    archives = validate_inputs(cfg)
    critic = Critic(
        verifier_a_path=cfg["artifacts"]["verifier_a"],
        symbolic_path=cfg["artifacts"]["symbolic"],
        required_sklearn_version=required,
    )

    probe = archives[cfg["inputs"][0]["name"]][0]
    neural = critic.neural(probe["text"], int(probe["target_level"]))
    symbolic = critic.symbolic(probe["text"], int(probe["target_level"]))
    for name, score in (("neural", neural), ("symbolic", symbolic)):
        if not math.isfinite(score) or not 0.0 <= score <= 1.0:
            raise SystemExit(f"REFUSED: {name} probe score is invalid: {score!r}")

    print(f"scikit-learn : {sklearn.__version__} (required {required})")
    for name, rows in archives.items():
        print(f"{name:15s}: {len(rows)} unique generations")
    print(f"neural probe  : {neural:.6f}")
    print(f"symbolic probe: {symbolic:.6f}")
    print("READY: both artifacts predicted successfully; no files were written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
