#!/usr/bin/env python3
"""Build the independent double-coding packet for all S4.6 gate failures."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.common.provenance import write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402
from src.eval.fit_tau import _emit, _validate  # noqa: E402


FIELDS = [
    "case_id", "plot_id", "target_level", "title_bn", "synopsis",
    "emitted_attempt", "emitted_draft", "attempt_1", "attempt_2", "attempt_3",
    "wrong_sentiment", "too_short", "off_topic", "template_repeat",
    "register_or_honorific", "other", "other_label", "coder_notes",
]


def build_rows(cases: list[dict], plots: list[dict], tau: float) -> list[dict]:
    _validate(cases)
    by_id = {row["plot_id"]: row for row in plots}
    failed = [case for case in cases if _emit(case, tau)[2]]
    rows = []
    for case in failed:
        plot = by_id[str(case["plot_id"])]
        emitted, _, _ = _emit(case, tau)
        rows.append({
            "case_id": f"{case['plot_id']}:L{case['target_level']}",
            "plot_id": case["plot_id"],
            "target_level": case["target_level"],
            "title_bn": plot["title_bn"],
            "synopsis": plot["synopsis"],
            "emitted_attempt": emitted["attempt"],
            "emitted_draft": emitted["draft"],
            "attempt_1": case["attempts"][0]["draft"],
            "attempt_2": case["attempts"][1]["draft"],
            "attempt_3": case["attempts"][2]["draft"],
            "wrong_sentiment": "",
            "too_short": "",
            "off_topic": "",
            "template_repeat": "",
            "register_or_honorific": "",
            "other": "",
            "other_label": "",
            "coder_notes": "",
        })
    return rows


def main() -> int:
    set_seed()  # inviolable global-seed rule; first action in the entry point
    ap = argparse.ArgumentParser()
    ap.add_argument("--traces", default="results/s4_tau_max_traces.jsonl")
    ap.add_argument("--tau-report", default="results/s4_tau_frontier.json")
    ap.add_argument("--plots", default="data/plots/plots_bn.csv")
    ap.add_argument("--output", default="data/annotation/s4_failure_taxonomy_sheet.csv")
    args = ap.parse_args()
    cases = [json.loads(line) for line in Path(args.traces).read_text(encoding="utf-8").splitlines() if line.strip()]
    tau_payload = json.loads(Path(args.tau_report).read_text(encoding="utf-8"))
    tau = float(tau_payload["result"]["selection"]["tau"])
    with Path(args.plots).open(encoding="utf-8-sig", newline="") as handle:
        plots = list(csv.DictReader(handle))
    rows = build_rows(cases, plots, tau)
    from io import StringIO
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    write_text_lf(args.output, buffer.getvalue())
    print(f"wrote {len(rows)} uncoded cases to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
