#!/usr/bin/env python3
"""Report S4.6 retry dynamics without changing the registered loop policy."""
from __future__ import annotations

import argparse
import html
import json
import math
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.common.provenance import git_hash, write_result, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402
from src.eval.fit_tau import _emit, _validate  # noqa: E402


SCORES = ("gate_score", "symbolic_score", "verifier_b_score")


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _direction(delta: float, tolerance: float = 0.0) -> str:
    if delta > tolerance:
        return "up"
    if delta < -tolerance:
        return "down"
    return "tie"


def normalized_edit_distance(left: str, right: str) -> float:
    """Character Levenshtein distance divided by the longer string length."""
    if left == right:
        return 0.0
    if not left or not right:
        return 1.0
    if len(left) > len(right):
        left, right = right, left
    previous = list(range(len(left) + 1))
    for row, char_r in enumerate(right, 1):
        current = [row]
        for col, char_l in enumerate(left, 1):
            current.append(min(
                current[-1] + 1,
                previous[col] + 1,
                previous[col - 1] + (char_l != char_r),
            ))
        previous = current
    return previous[-1] / max(len(left), len(right))


def _attempt_summary(cases: list[dict], tau: float) -> list[dict]:
    rows = []
    for index in range(3):
        attempts = [case["attempts"][index] for case in cases]
        rows.append({
            "attempt": index + 1,
            "n": len(attempts),
            "mean_gate_a": _mean([float(a["gate_score"]) for a in attempts]),
            "mean_symbolic": _mean([float(a["symbolic_score"]) for a in attempts]),
            "mean_verifier_b": _mean([float(a["verifier_b_score"]) for a in attempts]),
            "pass_rate_if_reached": _mean([
                float(float(a["gate_score"]) >= tau) for a in attempts
            ]),
        })
    return rows


def _transition_summary(cases: list[dict], tolerance: float) -> list[dict]:
    rows = []
    for left_index in (0, 1):
        score_blocks = {}
        for score in SCORES:
            deltas = [
                float(c["attempts"][left_index + 1][score])
                - float(c["attempts"][left_index][score])
                for c in cases
            ]
            counts = Counter(_direction(value, tolerance) for value in deltas)
            score_blocks[score] = {
                "mean_delta": _mean(deltas),
                "up": counts["up"],
                "down": counts["down"],
                "tie": counts["tie"],
            }
        joint = Counter()
        edits = []
        word_deltas = []
        for case in cases:
            left = case["attempts"][left_index]
            right = case["attempts"][left_index + 1]
            a_dir = _direction(float(right["gate_score"]) - float(left["gate_score"]), tolerance)
            b_dir = _direction(
                float(right["verifier_b_score"]) - float(left["verifier_b_score"]),
                tolerance,
            )
            joint[f"a_{a_dir}__b_{b_dir}"] += 1
            edits.append(normalized_edit_distance(str(left["draft"]), str(right["draft"])))
            word_deltas.append(len(str(right["draft"]).split()) - len(str(left["draft"]).split()))
        rows.append({
            "transition": f"{left_index + 1}_to_{left_index + 2}",
            "scores": score_blocks,
            "a_b_direction_crosstab": dict(sorted(joint.items())),
            "mean_normalized_character_edit_distance": _mean(edits),
            "mean_word_count_delta": _mean([float(x) for x in word_deltas]),
            "word_count_increased": sum(x > 0 for x in word_deltas),
            "word_count_decreased": sum(x < 0 for x in word_deltas),
            "word_count_tied": sum(x == 0 for x in word_deltas),
        })
    return rows


def _policy_summary(cases: list[dict], tau: float) -> dict:
    accepted = Counter()
    emitted = Counter()
    gave_up = []
    emitted_b = []
    for case in cases:
        attempt, _, failed = _emit(case, tau)
        emitted[int(attempt["attempt"])] += 1
        emitted_b.append(float(attempt["verifier_b_score"]))
        if failed:
            gave_up.append(case)
        else:
            accepted[int(attempt["attempt"])] += 1
    passed = [case for case in cases if case not in gave_up]
    return {
        "accepted_stop_counts": {str(i): accepted[i] for i in (1, 2, 3)},
        "emitted_attempt_counts": {str(i): emitted[i] for i in (1, 2, 3)},
        "gave_up_count": len(gave_up),
        "gave_up_rate": len(gave_up) / len(cases),
        "accepted_count": len(passed),
        "emitted_mean_verifier_b": _mean(emitted_b),
        "gave_up_emitted_mean_verifier_b": _mean([
            float(_emit(case, tau)[0]["verifier_b_score"]) for case in gave_up
        ]) if gave_up else None,
        "accepted_emitted_mean_verifier_b": _mean([
            float(_emit(case, tau)[0]["verifier_b_score"]) for case in passed
        ]) if passed else None,
        "gave_up_case_ids": [
            f"{case['plot_id']}:L{case['target_level']}" for case in gave_up
        ],
    }


def _oracle_summary(cases: list[dict], tau: float) -> dict:
    baseline = _mean([float(c["attempts"][0]["verifier_b_score"]) for c in cases])
    selected = _mean([float(_emit(c, tau)[0]["verifier_b_score"]) for c in cases])
    forced_a = _mean([float(_emit(c, None)[0]["verifier_b_score"]) for c in cases])
    oracle_b = _mean([
        max(float(a["verifier_b_score"]) for a in c["attempts"]) for c in cases
    ])
    denominator = oracle_b - baseline
    return {
        "status": "post_hoc_descriptive_only_not_a_selection_rule",
        "attempt1_baseline_b": baseline,
        "selected_tau_b": selected,
        "forced3_a_selected_b": forced_a,
        "best_of_three_b_oracle": oracle_b,
        "selected_tau_fraction_of_b_oracle_gain": (
            (selected - baseline) / denominator if denominator > 0 else None
        ),
        "forced3_a_fraction_of_b_oracle_gain": (
            (forced_a - baseline) / denominator if denominator > 0 else None
        ),
    }


def analyse(cases: list[dict], tau: float, tolerance: float = 0.0) -> dict:
    _validate(cases)
    global_block = {
        "attempts": _attempt_summary(cases, tau),
        "transitions": _transition_summary(cases, tolerance),
        "policy": _policy_summary(cases, tau),
        "oracle_diagnostic": _oracle_summary(cases, tau),
    }
    levels = {}
    for level in (0, 1):
        subset = [c for c in cases if int(c["target_level"]) == level]
        levels[str(level)] = {
            "n": len(subset),
            "attempts": _attempt_summary(subset, tau),
            "transitions": _transition_summary(subset, tolerance),
            "policy": _policy_summary(subset, tau),
            "oracle_diagnostic": _oracle_summary(subset, tau),
        }
    return {
        "method": "descriptive_retry_dynamics_on_frozen_max_traces",
        "n_cases": len(cases),
        "tau": tau,
        "max_attempts": 3,
        "score_roles": {
            "gate_score": "verifier_a_in_loop",
            "symbolic_score": "diagnostic_only",
            "verifier_b_score": "evaluation_only",
        },
        "direction_tolerance": tolerance,
        "global": global_block,
        "per_level": levels,
        "failure_taxonomy": {
            "status": "pending_independent_double_coding",
            "available_three_time_gate_failures": global_block["policy"]["gave_up_count"],
            "requested_by_spec": 50,
            "substitution_or_oversampling": "forbidden",
        },
    }


def _polyline(points: list[tuple[float, float]], colour: str) -> str:
    coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{coords}" fill="none" stroke="{colour}" stroke-width="3"/>'


def render_svg(result: dict, frontier: list[dict], provenance: str) -> str:
    """Dependency-free two-panel figure: frontier and per-attempt dynamics."""
    width, height = 1120, 510
    chunks = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17202a}.title{font-size:18px;font-weight:700}.lab{font-size:13px}.small{font-size:11px;fill:#566573}</style>',
        '<text x="35" y="30" class="title">S4.6 — quality/cost frontier and retry dynamics</text>',
    ]
    # Panel A: cost (1..5) versus independent B quality.
    x0, y0, w, h = 60, 70, 470, 350
    chunks += [f'<line x1="{x0}" y1="{y0+h}" x2="{x0+w}" y2="{y0+h}" stroke="#333"/>',
               f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+h}" stroke="#333"/>',
               f'<text x="{x0}" y="{y0-12}" class="title">A. Threshold frontier</text>']
    rows = sorted(frontier, key=lambda row: float(row["mean_calls"]))
    points = []
    for row in rows:
        x = x0 + (float(row["mean_calls"]) - 1.0) / 4.0 * w
        y = y0 + (1.0 - float(row["quality_b"])) * h
        points.append((x, y))
    chunks.append(_polyline(points, "#2874a6"))
    for calls in (1, 2, 3, 4, 5):
        x = x0 + (calls - 1) / 4 * w
        chunks.append(f'<text x="{x-4}" y="{y0+h+22}" class="lab">{calls}</text>')
    for quality in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = y0 + (1-quality)*h
        chunks.append(f'<text x="{x0-38}" y="{y+4}" class="lab">{quality:.2g}</text>')
    chosen = result["global"]["policy"]
    tau = result["tau"]
    selected = min(frontier, key=lambda row: abs(float(row["tau"]) - tau))
    sx = x0 + (float(selected["mean_calls"])-1)/4*w
    sy = y0 + (1-float(selected["quality_b"]))*h
    chunks += [f'<circle cx="{sx}" cy="{sy}" r="7" fill="#c0392b"/>',
               f'<text x="{sx+10}" y="{sy-8}" class="lab">selected tau={tau:.3f}</text>',
               f'<text x="{x0+w/2-35}" y="{y0+h+45}" class="lab">mean LLM calls</text>',
               f'<text transform="translate(16 {y0+h/2+45}) rotate(-90)" class="lab">Verifier-B quality</text>']
    # Panel B: mean score by attempt, one line per scorer.
    x1, y1, w1, h1 = 620, 70, 440, 350
    chunks += [f'<line x1="{x1}" y1="{y1+h1}" x2="{x1+w1}" y2="{y1+h1}" stroke="#333"/>',
               f'<line x1="{x1}" y1="{y1}" x2="{x1}" y2="{y1+h1}" stroke="#333"/>',
               f'<text x="{x1}" y="{y1-12}" class="title">B. Scores by attempted revision</text>']
    series = (("mean_gate_a", "Verifier-A gate", "#c0392b"),
              ("mean_symbolic", "symbolic diagnostic", "#7d3c98"),
              ("mean_verifier_b", "Verifier-B evaluation", "#1e8449"))
    attempts = result["global"]["attempts"]
    for key, label, colour in series:
        pts = []
        for row in attempts:
            x = x1 + (int(row["attempt"])-1)/2*w1
            y = y1 + (1-float(row[key]))*h1
            pts.append((x, y))
        chunks.append(_polyline(pts, colour))
        for x, y in pts:
            chunks.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{colour}"/>')
        legend_y = y1 + 18 + 22*series.index((key, label, colour))
        chunks += [f'<line x1="{x1+245}" y1="{legend_y}" x2="{x1+275}" y2="{legend_y}" stroke="{colour}" stroke-width="3"/>',
                   f'<text x="{x1+282}" y="{legend_y+4}" class="lab">{html.escape(label)}</text>']
    for attempt in (1, 2, 3):
        x = x1 + (attempt-1)/2*w1
        chunks.append(f'<text x="{x-4}" y="{y1+h1+22}" class="lab">{attempt}</text>')
    chunks += [f'<text x="{x1+w1/2-28}" y="{y1+h1+45}" class="lab">attempt</text>',
               f'<text x="35" y="485" class="small">accepted stops: {chosen["accepted_stop_counts"]}; gave up: {chosen["gave_up_count"]}/60. Attempt 3 is not a monotonic improvement.</text>',
               f'<text x="800" y="485" class="small">git: {html.escape(provenance)}</text>',
               '</svg>']
    return "\n".join(chunks) + "\n"


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    set_seed()  # inviolable global-seed rule; first action in the entry point
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s4_dynamics.yaml")
    args = ap.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    cases = _read_jsonl(Path(cfg["input"]["max_traces_jsonl"]))
    _validate(cases, int(cfg["input"]["expected_cases"]))
    if any(len(c["attempts"]) != int(cfg["input"]["expected_attempts"]) for c in cases):
        raise ValueError("unexpected attempt count")
    tau_payload = json.loads(Path(cfg["input"]["tau_report_json"]).read_text(encoding="utf-8"))
    tau_result = tau_payload["result"]
    tau = float(tau_result["selection"]["tau"])
    result = analyse(cases, tau, float(cfg["analysis"]["direction_tolerance"]))
    write_result(result, cfg["output"]["report_json"], config_path=args.config)
    write_text_lf(
        cfg["output"]["figure_svg"],
        render_svg(result, tau_result["frontier"], git_hash()),
    )
    policy = result["global"]["policy"]
    print(
        f"tau={tau:.7f}; accepted={policy['accepted_count']}/{len(cases)}; "
        f"gave_up={policy['gave_up_count']}; wrote {cfg['output']['report_json']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
