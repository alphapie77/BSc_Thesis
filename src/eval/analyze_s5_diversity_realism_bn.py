#!/usr/bin/env python3
"""Bangla S5 lexical-diversity and exact-length-distribution diagnostics.

No text is normalised, stemmed, or stripped of stopwords.  MAUVE and generated
sentiment JS are intentionally not substituted here: each needs a defensible,
registered feature/evaluator choice that the current protocol does not supply.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import write_csv_result, write_result
from src.common.seed import set_seed


class S5RealismError(RuntimeError):
    pass


def emitted_text(row: dict) -> str:
    emitted = row.get("result", {}).get("emitted", {})
    generation = emitted.get("generation", emitted)
    text = generation.get("text") if isinstance(generation, dict) else None
    if not isinstance(text, str) or not text.strip():
        raise S5RealismError(f"{row.get('key')}: missing emitted text")
    return text


def ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    return [tuple(tokens[i:i + n]) for i in range(max(0, len(tokens) - n + 1))]


def distinct(texts: list[str], n: int) -> float:
    grams = [g for text in texts for g in ngrams(text.split(), n)]
    return len(set(grams)) / len(grams) if grams else 0.0


def js_discrete(left: list[int], right: list[int]) -> float:
    if not left or not right:
        raise S5RealismError("JS requires two non-empty distributions")
    a, b = Counter(left), Counter(right)
    support = set(a) | set(b)
    n_a, n_b = len(left), len(right)
    total = 0.0
    for value in support:
        p, q = a[value] / n_a, b[value] / n_b
        midpoint = (p + q) / 2
        if p:
            total += .5 * p * math.log2(p / midpoint)
        if q:
            total += .5 * q * math.log2(q / midpoint)
    return total


def self_bleu(texts: list[str], order: int) -> float:
    try:
        from nltk.translate.bleu_score import sentence_bleu
    except ImportError as exc:
        raise S5RealismError("Self-BLEU requires nltk; install it in the analysis runtime") from exc
    if len(texts) < 2:
        raise S5RealismError("Self-BLEU requires at least two texts")
    weights = tuple([1 / order] * order)
    tokenized = [text.split() for text in texts]
    # No smoothing: a zero is a real signal for short Bangla outputs, not an
    # imputed overlap. This preserves the metric's conventional interpretation.
    scores = [
        sentence_bleu(tokenized[:i] + tokenized[i + 1:], hypothesis, weights=weights)
        for i, hypothesis in enumerate(tokenized)
    ]
    return sum(scores) / len(scores)


def load_cases(path: Path) -> list[dict]:
    rows, keys = [], set()
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("key") in keys:
            raise S5RealismError(f"duplicate case key at {lineno}")
        keys.add(row.get("key")); rows.append(row)
    if len(rows) != 5400:
        raise S5RealismError(f"need completed 5,400-case archive, got {len(rows)}")
    return rows


def real_lengths(cleaned: Path, assignments: Path, region: str) -> dict[int, list[int]]:
    with open(cleaned, encoding="utf-8", newline="") as fh:
        reviews = {r["review_id"]: r["Movie Review"] for r in csv.DictReader(fh)}
    groups = defaultdict(list)
    with open(assignments, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("region") == region:
                text = reviews.get(row["review_id"])
                if text is not None:
                    groups[int(row["cluster_k2"])].append(len(text.split()))
    if set(groups) != {0, 1}:
        raise S5RealismError(f"real reference must have both levels, got {sorted(groups)}")
    return groups


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s5_diversity_realism_bn.yaml")
    args = ap.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parents[2]
    resolve = lambda x: Path(x) if Path(x).is_absolute() else root / x
    cases = load_cases(resolve(cfg["inputs"]["cases_jsonl"]))
    order = int(cfg["metrics"]["self_bleu_max_order"])
    if order != 4:
        raise S5RealismError("self-BLEU order is frozen at 4")
    generated = defaultdict(list)
    for row in cases:
        generated[(row["condition"], int(row["target_level"]))].append(emitted_text(row))
    references = real_lengths(resolve(cfg["inputs"]["cleaned_csv"]),
                              resolve(cfg["inputs"]["k2_assignments"]),
                              cfg["metrics"]["real_reference_region"])
    diversity_rows, js_rows = [], []
    for (condition, level), texts in sorted(generated.items()):
        lengths = [len(text.split()) for text in texts]
        diversity_rows.append({
            "condition": condition, "target_level": level, "n": len(texts),
            "distinct_1": distinct(texts, 1), "distinct_2": distinct(texts, 2),
            "self_bleu_4": self_bleu(texts, order),
        })
        js_rows.append({
            "condition": condition, "target_level": level, "n_generated": len(lengths),
            "n_real_regionA": len(references[level]),
            "js_length_exact_word_count": js_discrete(lengths, references[level]),
        })
    write_csv_result(diversity_rows, resolve(cfg["outputs"]["diversity_csv"]),
                     list(diversity_rows[0]), args.config)
    write_csv_result(js_rows, resolve(cfg["outputs"]["length_js_csv"]),
                     list(js_rows[0]), args.config)
    preflight = {
        "status": "S5_BN_DIVERSITY_LENGTH_REALISM_PASS",
        "n_cases": len(cases), "self_bleu_order": order,
        "mauve": {"status": "PENDING", "reason": "mauve-text defaults to English gpt2-large; no Bangla feature model is registered"},
        "sentiment_js": {"status": "PENDING", "reason": "no independent registered generated-text sentiment scorer exists"},
        "warning": "No MAUVE or generated-sentiment claim may be made from this output.",
    }
    write_result(preflight, resolve(cfg["outputs"]["preflight_json"]), args.config)
    print(json.dumps(preflight, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
