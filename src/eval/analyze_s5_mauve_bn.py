#!/usr/bin/env python3
"""Compute a Bangla-primary LaBSE-feature MAUVE sensitivity analysis.

``mauve-text`` defaults to English GPT-2 Large.  Its documented precomputed
feature API lets MAUVE operate over LaBSE instead: this keeps the comparison in
the thesis's registered multilingual representation, but is explicitly *not*
reported as directly MoP-comparable default-GPT2 MAUVE.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import write_csv_result, write_result
from src.common.seed import set_seed
from src.eval.analyze_s5_diversity_realism_bn import emitted_text, load_cases


class S5MauveError(RuntimeError):
    pass


def real_texts(cleaned: Path, assignments: Path, region: str) -> dict[int, list[str]]:
    if not cleaned.is_file() or not assignments.is_file():
        raise S5MauveError("missing frozen cleaned corpus or axis assignments")
    with open(cleaned, encoding="utf-8", newline="") as fh:
        reviews = {r["review_id"]: r["Movie Review"] for r in csv.DictReader(fh)}
    groups: dict[int, list[str]] = defaultdict(list)
    with open(assignments, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("region") == region and row.get("review_id") in reviews:
                groups[int(row["cluster_k2"])].append(reviews[row["review_id"]])
    if set(groups) != {0, 1}:
        raise S5MauveError("real reference must contain both frozen axis levels")
    return groups


def choose_reference(texts: list[str], n: int, level: int) -> list[str]:
    if len(texts) < n:
        raise S5MauveError(f"reference level {level} has {len(texts)} texts, need {n}")
    rng = np.random.default_rng(42 + level)
    return [texts[i] for i in sorted(rng.choice(len(texts), n, replace=False).tolist())]


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s5_mauve_bn.yaml")
    ap.add_argument("--device", default=None)
    args = ap.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parents[2]
    resolve = lambda x: Path(x) if Path(x).is_absolute() else root / x
    cases = load_cases(resolve(cfg["inputs"]["cases_jsonl"]))
    try:
        import mauve
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise S5MauveError("install mauve-text and sentence-transformers before running") from exc
    generated: dict[tuple[str, int], list[str]] = defaultdict(list)
    for row in cases:
        generated[(row["condition"], int(row["target_level"]))].append(emitted_text(row))
    n_ref = int(cfg["reference"]["per_level_n"])
    real = real_texts(resolve(cfg["inputs"]["cleaned_csv"]),
                      resolve(cfg["inputs"]["k2_assignments"]), cfg["reference"]["region"])
    references = {level: choose_reference(texts, n_ref, level) for level, texts in real.items()}
    device = args.device or "cpu"
    encoder = SentenceTransformer(cfg["reference"]["encoder"], device=device)
    # Embed each unique corpus exactly once; inference order cannot affect it.
    all_texts = [text for texts in generated.values() for text in texts] + references[0] + references[1]
    unique_texts = list(dict.fromkeys(all_texts))
    vectors = encoder.encode(unique_texts, batch_size=64, show_progress_bar=True,
                             convert_to_numpy=True, normalize_embeddings=False)
    features = {text: vector for text, vector in zip(unique_texts, vectors)}
    rows = []
    for (condition, level), texts in sorted(generated.items()):
        if len(texts) != n_ref:
            raise S5MauveError(f"{condition}/L{level}: got {len(texts)}, expected {n_ref}")
        result = mauve.compute_mauve(
            p_features=np.asarray([features[text] for text in texts]),
            q_features=np.asarray([features[text] for text in references[level]]),
            seed=42, num_buckets="auto", verbose=False,
        )
        rows.append({
            "condition": condition, "target_level": level,
            "n_generated": len(texts), "n_real_reference": n_ref,
            "labse_feature_mauve": float(result.mauve),
            "feature_encoder": cfg["reference"]["encoder"],
            "interpretation": "LaBSE-feature MAUVE; not directly comparable to default-GPT2 MoP MAUVE",
        })
    write_csv_result(rows, resolve(cfg["outputs"]["labse_mauve_csv"]), list(rows[0]), args.config)
    report = {
        "status": "S5_BN_LABSE_MAUVE_PASS", "n_cases": len(cases),
        "feature_encoder": cfg["reference"]["encoder"], "per_level_n": n_ref,
        "default_gpt2_mauve": "NOT_RUN: unsuitable as a Bangla semantic headline; MoP comparability is not claimed",
        "sample_size_limitation": "mauve-text recommends thousands of texts; n=270 per cell is a small-sample sensitivity analysis only",
        "generated_sentiment_js": "PENDING: no independent registered generated-text sentiment scorer",
    }
    write_result(report, resolve(cfg["outputs"]["report_json"]), args.config)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
