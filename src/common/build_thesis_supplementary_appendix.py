"""Render Appendix F only from audited CSV result files."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def rows(name: str) -> list[dict[str, str]]:
    with (ROOT / "results" / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def table(headers: list[str], body: list[list[str]]) -> list[str]:
    return [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
        *("| " + " | ".join(r) + " |" for r in body),
    ]


def f(value: str, digits: int = 4) -> str:
    return f"{float(value):.{digits}f}"


def main() -> None:
    out = [
        "# Appendix F — Supplementary numerical results",
        "",
        "This appendix is mechanically rendered from the audited CSV files named",
        "under each table. Seeds are sensitivity or pairing blocks, not independent",
        "studies. No value in this appendix is recomputed from model outputs.",
        "",
        "## F.1 Verifier per-seed sensitivity",
        "",
    ]
    a = rows("s3_backbone_per_seed.csv")
    out += table(
        ["Backbone", "Learning rate", "Seed", "Macro-F1"],
        [[r["arm"], r["lr"], r["seed"], f(r["macro_f1"])] for r in a],
    )
    out += ["", "Source: `results/s3_backbone_per_seed.csv`.", ""]
    b = rows("s3d_verifier_b_per_seed.csv")
    out += table(
        ["Verifier-B seed", "Learning rate", "Macro-F1", "Errors"],
        [[r["seed"], r["lr"], f(r["macro_f1"]), r["errors"]] for r in b],
    )
    out += [
        "",
        "Source: `results/s3d_verifier_b_per_seed.csv`. The persisted artifact is",
        "seed 42 by the preregistered global-seed rule, not the best seed.",
        "",
        "## F.2 Phase-5 per-replicate descriptive outcomes",
        "",
    ]
    scored = rows("s5_main_bn_scored_cases.csv")
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for r in scored:
        grouped[(r["condition"], r["target_level"], r["replicate_seed"])].append(r)
    phase5 = []
    for key in sorted(grouped):
        cell = grouped[key]
        mean_b = sum(float(r["verifier_b_target_probability"]) for r in cell) / len(cell)
        success = sum(int(r["verifier_b_binary_success"]) for r in cell) / len(cell)
        phase5.append([*key, str(len(cell)), f"{mean_b:.6f}", f"{success:.4f}"])
    out += table(
        ["Condition", "Level", "Replicate seed", "n", "Mean Verifier-B target probability", "Binary success rate"],
        phase5,
    )
    out += [
        "",
        "Source: deterministic grouping of `results/s5_main_bn_scored_cases.csv`;",
        "each row is 90 held-out plots. These replicate rows are descriptive",
        "sensitivity blocks and are not treated as three independent studies.",
        "",
        "## F.3 Same-case Goodhart transitions",
        "",
    ]
    g = rows("s5_main_bn_goodhart_paired_transitions.csv")
    out += table(
        ["Condition", "Transition", "Paired cases", "Δ Verifier-A", "Δ Verifier-B", "Δ(A−B)", "Standing"],
        [[r["condition"], f'{r["from_attempt"]}→{r["to_attempt"]}', r["n_paired_cases"],
          f(r["mean_a_delta"], 6), f(r["mean_b_delta"], 6),
          f(r["mean_a_minus_b_delta"], 6), r["interpretation"]] for r in g],
    )
    out += [
        "",
        "Source: `results/s5_main_bn_goodhart_paired_transitions.csv`. These are",
        "selection-aware adjacent transitions among continuing failed cases, not",
        "population effects over all 540 cases in a condition.",
        "",
        "## F.4 Diversity and short-output diagnostics",
        "",
    ]
    d = rows("s5_main_bn_diversity.csv")
    out += table(
        ["Condition", "Level", "n", "Under 4 words", "Rate", "Distinct-1", "Distinct-2", "Self-BLEU-4"],
        [[r["condition"], r["target_level"], r["n"], r["n_texts_under_4_words"],
          f(r["rate_texts_under_4_words"]), f(r["distinct_1"]),
          f(r["distinct_2"]), f(r["self_bleu_4"])] for r in d],
    )
    out += ["", "Source: `results/s5_main_bn_diversity.csv`.", ""]
    js = rows("s5_main_bn_length_js.csv")
    mauve = {(r["condition"], r["target_level"]): r for r in rows("s5_main_bn_labse_mauve.csv")}
    out += ["## F.5 Length-distribution and LaBSE-feature MAUVE sensitivity", ""]
    out += table(
        ["Condition", "Level", "Generated n", "Real length-reference n", "Length JS", "MAUVE generated/real n", "LaBSE-feature MAUVE"],
        [[r["condition"], r["target_level"], r["n_generated"], r["n_real_regionA"],
          f(r["js_length_exact_word_count"], 6),
          f'{mauve[(r["condition"], r["target_level"])]["n_generated"]}/{mauve[(r["condition"], r["target_level"])]["n_real_reference"]}',
          f(mauve[(r["condition"], r["target_level"])]["labse_feature_mauve"], 6)] for r in js],
    )
    out += [
        "",
        "Sources: `results/s5_main_bn_length_js.csv` and",
        "`results/s5_main_bn_labse_mauve.csv`. MAUVE uses LaBSE features with",
        "270 generated and 270 real texts per cell; it is a small-sample",
        "sensitivity analysis and is not comparable to default GPT-2-feature MAUVE.",
        "No sentiment-JS value is supplied because no independent registered",
        "generated-text sentiment scorer exists.",
        "",
    ]
    target = ROOT / "docs" / "appendices" / "appendix_f_supplementary_results.md"
    target.write_text("\n".join(out), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
