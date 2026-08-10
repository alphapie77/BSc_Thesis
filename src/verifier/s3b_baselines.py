"""S3.2b -- the baselines S3.2 should have had. Pre-registered in protocol.md.

S3.2 reported seven arms at 0.93-0.96 macro-F1 and compared them only with each
other. A reader's first question is the one the table cannot answer: *0.96
against what?* This step answers it with three reference points, in increasing
order of how much they threaten the ablation:

1. **majority class** -- the floor. Establishes that the number is not just the
   class prior wearing a transformer.
2. **length rule** -- one feature, fitted on TRAIN. S2e measured `length_auc` at
   0.6764, so length is the strongest known surface confound in this data, and a
   verifier that merely rediscovers it would be worthless.
3. **frozen LaBSE + logistic regression** -- the one that matters.

Why (3) is the real test, stated plainly because it is uncomfortable: **the
`cluster_k2` label was created by running k-means on LaBSE embeddings.** So a
linear probe on those same embeddings is not an ordinary baseline -- it is the
label's own generating geometry, asked to reproduce itself. If it scores as well
as the fine-tuned arms, then every arm in S3.2 was recovering a boundary that
already existed in LaBSE space, and the seven-arm table is a measurement of the
label's construction rather than of the backbones. That would not invalidate
RQ2 -- which needs a well-defined reproducible label, and has one -- but it
would strip the ablation of any claim about backbones, and it is far better
found here than at viva.

Buckmann et al. (2024) make the same point from the other direction: penalised
logistic regression on a small model's embeddings matches or beats much larger
models in the tens-of-shot regime.

Run:
    python -m src.verifier.s3b_baselines --config configs/s3b_baselines.yaml
"""

from __future__ import annotations

import os

# Same one-GPU pin as S3.2, for the same reason (see that module's header).
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")

import argparse
import json
import sys
from pathlib import Path

from src.common.seed import set_seed
from src.common import provenance
from src.verifier import compare
from src.verifier.split_access import load_training_rows

set_seed()


def _load_yaml(path):
    import yaml
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def majority_baseline(train, dev) -> list[int]:
    """Predict the training majority class for everything."""
    maj = max(train.class_counts, key=train.class_counts.get)
    return [maj] * len(dev)


def length_baseline(train, dev) -> tuple[list[int], dict]:
    """Best single word-count threshold, chosen on TRAIN and applied to dev.

    Fitted on train rather than dev on purpose: a threshold tuned on the
    evaluation set would flatter the baseline and make the arms look worse by
    comparison, which is the opposite of the error we are guarding against.
    """
    tr_len = [len(t.split()) for t in train.texts]
    dv_len = [len(t.split()) for t in dev.texts]
    best = None
    for thr in range(0, max(tr_len) + 1):
        for direction in (">", "<="):
            pred = [
                (1 if l > thr else 0) if direction == ">" else (1 if l <= thr else 0)
                for l in tr_len
            ]
            f1 = compare.macro_f1(list(train.labels), pred)
            if best is None or f1 > best[0]:
                best = (f1, thr, direction)
    _, thr, direction = best
    pred = [
        (1 if l > thr else 0) if direction == ">" else (1 if l <= thr else 0)
        for l in dv_len
    ]
    return pred, {"threshold": thr, "direction": direction, "train_macro_f1": round(best[0], 6)}


def labse_probe_baseline(train, dev, cfg) -> list[int]:
    """Frozen LaBSE embeddings + L2 logistic regression. The circularity test.

    Nothing is fine-tuned: the encoder that generated the label is frozen and a
    linear head is fitted on top. If this reaches the fine-tuned arms, the arms
    were recovering the label's own geometry.
    """
    from sentence_transformers import SentenceTransformer
    from sklearn.linear_model import LogisticRegression

    model = SentenceTransformer(cfg["labse_model"])
    Xtr = model.encode(list(train.texts), batch_size=64, show_progress_bar=False,
                       normalize_embeddings=True)
    Xdv = model.encode(list(dev.texts), batch_size=64, show_progress_bar=False,
                       normalize_embeddings=True)
    clf = LogisticRegression(max_iter=2000, random_state=42)
    clf.fit(Xtr, list(train.labels))
    return [int(p) for p in clf.predict(Xdv)]


def run(config_path: str) -> dict:
    cfg = _load_yaml(config_path)
    train, dev = load_training_rows(
        "A",
        split_map=cfg["inputs"]["split_map"],
        k2_assignments=cfg["inputs"]["k2_assignments"],
        cleaned_csv=cfg["inputs"]["cleaned_csv"],
    )
    if len(train) != 804 or len(dev) != 82:
        raise SystemExit(
            f"n drifted: train {len(train)} dev {len(dev)}; expected 804/82. "
            "The baselines must sit on exactly the data S3.2 used or they are "
            "not comparable to it."
        )
    y = list(dev.labels)

    scores, detail = {}, {}
    scores["majority"] = compare.macro_f1(y, majority_baseline(train, dev))
    lp, lmeta = length_baseline(train, dev)
    scores["length_rule"] = compare.macro_f1(y, lp)
    detail["length_rule"] = lmeta
    scores["labse_probe"] = compare.macro_f1(y, labse_probe_baseline(train, dev, cfg))

    # The seven arms, read back so the comparison lives in one artifact.
    arms = json.loads(Path(cfg["inputs"]["s3_result"]).read_text(encoding="utf-8"))["result"]
    arm_means = arms["mean_macro_f1"]
    best_arm, best_score = max(arm_means.items(), key=lambda kv: kv[1])

    # Pre-registered band. One dev item is 1/82 = 0.0122 of macro-F1 at this
    # class balance, and "within one item" is the resolution the dev set has.
    one_item = 1.0 / len(y)
    gap = best_score - scores["labse_probe"]
    if gap <= one_item:
        verdict = "CIRCULARITY_CONFIRMED"
    elif scores["labse_probe"] <= max(scores["majority"], scores["length_rule"]) + one_item:
        verdict = "NOT_CIRCULAR"
    else:
        verdict = "PARTIAL"

    result = {
        "verdict": verdict,
        "n_train": len(train), "n_dev": len(dev),
        "one_dev_item_in_macro_f1": round(one_item, 6),
        "baselines": {k: round(v, 6) for k, v in scores.items()},
        "baseline_detail": detail,
        "best_arm": best_arm,
        "best_arm_macro_f1": round(best_score, 6),
        "gap_best_arm_minus_labse_probe": round(gap, 6),
        "gap_in_dev_items": round(gap / one_item, 2),
        "arm_means_for_reference": arm_means,
    }
    provenance.write_result(result, cfg["outputs"]["results_json"], config_path=config_path)
    provenance.write_text_lf(cfg["outputs"]["results_md"], _render(result))
    return result


def _render(r: dict) -> str:
    b = r["baselines"]
    lines = [
        "# S3.2b — the baselines S3.2 should have had",
        "",
        f"**Verdict: `{r['verdict']}`**",
        "",
        f"- dev n = **{r['n_dev']}**, so one item = **{r['one_dev_item_in_macro_f1']:.4f}** macro-F1.",
        "  Every gap below is also given in items, because at this n a difference",
        "  of 0.03 is three reviews and should be read that way.",
        "",
        "| Reference point | macro-F1 |",
        "|---|---|",
        f"| majority class | {b['majority']:.4f} |",
        f"| length rule (fitted on TRAIN) | {b['length_rule']:.4f} |",
        f"| **frozen LaBSE + logistic regression** | **{b['labse_probe']:.4f}** |",
        f"| best fine-tuned arm (`{r['best_arm']}`) | {r['best_arm_macro_f1']:.4f} |",
        "",
        f"**Best arm − frozen probe = {r['gap_best_arm_minus_labse_probe']:+.4f} "
        f"({r['gap_in_dev_items']:.1f} dev items).**",
        "",
    ]
    if r["verdict"] == "CIRCULARITY_CONFIRMED":
        lines += [
            "## ⛔ The ablation measured the label's construction",
            "",
            "A frozen linear probe on the encoder that GENERATED the label matches",
            "the best fine-tuned arm to within one dev item. Every arm in S3.2 was",
            "recovering a boundary that already existed in LaBSE space.",
            "",
            "**Consequences, per protocol.md §S3.2b:**",
            "- The seven-arm table may support **no claim about backbones**. It is",
            "  reported as a demonstration that the label is linearly recoverable.",
            "- The `TIE` verdict stands but is re-explained: the arms are",
            "  indistinguishable because the task is near-saturated by construction,",
            "  not because backbones are interchangeable in general.",
            "- **Verifier-A should be reconsidered**: if a logistic regression on",
            "  frozen embeddings matches a fine-tuned BanglaBERT, the fine-tuning is",
            "  not earning its cost inside the Phase 4 loop.",
        ]
    elif r["verdict"] == "PARTIAL":
        lines += [
            "## Fine-tuning adds something over the generating geometry",
            "",
            "The frozen probe beats the surface baselines but does not reach the",
            "fine-tuned arms. The gap above is the verifier's actual contribution,",
            "and it is what should be quoted — not the raw 0.96, which any model",
            "with access to LaBSE-shaped features can approach.",
        ]
    else:
        lines += [
            "## The k-means boundary is NOT linearly recoverable",
            "",
            "Unexpected: the frozen probe sits at surface-baseline level. The label",
            "is therefore not a simple linear cut in LaBSE space, and the fine-tuned",
            "arms are doing real work. This strengthens S3.2 rather than weakening",
            "it — and it should be checked for a bug before it is believed.",
        ]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    a = ap.parse_args()
    r = run(a.config)
    print(json.dumps({k: r[k] for k in
                      ("verdict", "baselines", "best_arm_macro_f1",
                       "gap_best_arm_minus_labse_probe", "gap_in_dev_items")}, indent=2))


if __name__ == "__main__":
    main()
