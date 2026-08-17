#!/usr/bin/env python3
"""Reclassify an existing S4.5a result without rescoring generations.

The first Kaggle report exposed a coverage gap in the pre-registered mapping:
the curve was sensitive to w while every held-out fold selected the neural-only
endpoint.  The measurements are retained verbatim.  This audit changes only
the outcome label and report interpretation, preserves the scoring provenance,
and writes fresh audit provenance through the repository result writer.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import write_result, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402
from src.eval.fit_w import classify  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="configs/s4_w.yaml")
    args = ap.parse_args()
    set_seed()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    json_path = Path(cfg["outputs"]["report_json"])
    md_path = Path(cfg["outputs"]["report_md"])
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    scoring_provenance = payload.pop("_provenance")
    result = payload["result"]

    changed = 0
    for block in result["per_condition"].values():
        corrected = classify(block["verdict_flip_share"], block["marginal_value"])
        if corrected != block["outcome"]:
            block["outcome_as_emitted_by_dda307c"] = block["outcome"]
            block["outcome"] = corrected
            changed += 1
    if changed == 0:
        raise RuntimeError("audit found no outcome labels to correct")

    result["scoring_provenance"] = scoring_provenance
    result["audit_note"] = (
        "Measurements are unchanged. The original classifier called the "
        "sensitive-curve/held-out-tie combination SYMBOLIC_INERT even though "
        "the registered definition requires a flat curve. The corrected label "
        "exposes that the three pre-registered outcomes did not cover the "
        "observed combination."
    )
    write_result(result, json_path, config_path=args.config)

    text = md_path.read_text(encoding="utf-8")
    old_heading = "### Outcome: `SYMBOLIC_INERT`"
    if text.count(old_heading) != changed:
        raise RuntimeError("markdown outcome count does not match JSON corrections")
    old_consequence = (
        "Registered consequence: **the symbolic term is RETAINED anyway** — "
        "the Reflector requires a component that can name which rule failed, "
        "and the LaBSE probe cannot. Retained for interpretability, not for "
        "accuracy, and reported as a negative result rather than softened."
    )
    replacement = (
        "### Audit state: `PRECOMMITMENT_UNRESOLVED`\n\n"
        "**This is not a fourth scientific outcome.** The curve is not flat, "
        "so `SYMBOLIC_INERT` does not apply; the held-out test does not favour "
        "the symbolic term, so `SYMBOLIC_EARNS_ITS_PLACE` does not apply; and "
        "neural-only never beats the selected mixture, so `SYMBOLIC_HARMS` "
        "does not apply. The registered rule does not resolve this combination.\n\n"
        "**Consequence:** no hybrid-accuracy claim and no single `w` is selected. "
        "The symbolic component remains available for its separately registered "
        "failed-rule-naming role; this result does not establish predictive value."
    )
    text = text.replace(old_heading + "\n\n" + old_consequence, replacement)
    banner = (
        "> 🔴 **Verdict audit:** the Kaggle measurements below are unchanged, "
        "but the original outcome mapper did not cover the observed "
        "sensitive-curve/held-out-tie combination. The audit state below "
        "supersedes the emitted `SYMBOLIC_INERT` labels.\n\n"
    )
    marker = "> ⚠️ **The label is the level that was REQUESTED.**"
    if marker not in text:
        raise RuntimeError("report banner insertion point not found")
    text = text.replace(marker, banner + marker, 1)
    write_text_lf(md_path, text)
    print(f"audited {changed} condition(s); measurements unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
