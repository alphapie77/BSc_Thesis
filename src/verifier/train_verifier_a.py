"""S3.3a -- fit Verifier-A: frozen LaBSE + L2 logistic head, on R1's 804 rows.

Pre-registered in `docs/protocol.md` section "S3.3 pre-commitment".

**What this is, and why it looks too simple.** Verifier-A is the in-loop gate of
the §4.2 Critic. Decision 16 (2026-08-10) chose a *frozen* encoder with a linear
head over a fine-tuned BanglaBERT, on the evidence of S3.2b: the probe scored
**0.9866** against the best fine-tuned arm's 0.9647, i.e. it was 1.8 dev items
*ahead* while training in seconds. The mechanism is not mysterious --
`cluster_k2` was produced by k-means on LaBSE embeddings, so the label is close
to a linear boundary in that space.

**That is a stated weakness, not a hidden one.** A verifier which is a linear
function of LaBSE may be trivially gameable by a generator whose text is scored
in that same space, and that is precisely the failure RQ5 hunts. It is why
Verifier-B is a different model family on different data (protocol.md S3.2c),
and why nothing in this file may ever be used to score S6.

**Relationship to S3.2b.** That step already fitted this exact model as a
*baseline*, to test circularity. This step fits it as the *artifact*, persists
it, and calibrates it. The dev macro-F1 here must reproduce S3.2b's 0.9866
exactly; the script fails loudly if it does not, because a drift would mean the
data, the encoder version or the split moved underneath us.

Run:
    python -m src.verifier.train_verifier_a --config configs/s3c_verifier_a.yaml
"""

from __future__ import annotations

import os

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")

import argparse
import csv
import json
from pathlib import Path

from src.common.seed import set_seed
from src.common import provenance
from src.verifier import calibration, compare
from src.verifier.split_access import load_gold_ids, load_training_rows

set_seed()

#: S3.2b's measured value for this identical model. A mismatch is a stop, not a
#: warning: it means something moved that nothing was supposed to move.
S3B_REFERENCE_MACRO_F1 = 0.9866


def _load_yaml(path):
    import yaml

    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _assert_expected(cfg, train, dev) -> None:
    exp = cfg["expected"]
    problems = []
    if len(train) != exp["train_n"]:
        problems.append(f"train n {len(train)} != {exp['train_n']}")
    if len(dev) != exp["dev_n"]:
        problems.append(f"dev n {len(dev)} != {exp['dev_n']}")
    if train.class_counts != {int(k): v for k, v in exp["train_class_counts"].items()}:
        problems.append(f"train class counts {train.class_counts} != {exp['train_class_counts']}")
    if dev.class_counts != {int(k): v for k, v in exp["dev_class_counts"].items()}:
        problems.append(f"dev class counts {dev.class_counts} != {exp['dev_class_counts']}")
    if problems:
        raise SystemExit(
            "The data moved under a frozen split:\n  - "
            + "\n  - ".join(problems)
            + "\nDo not train. Either the split map, the K=2 assignments or the "
            "cleaned corpus has changed, and every Phase 3 number is stated "
            "against the old ones."
        )


def run(config_path: str) -> dict:
    cfg = _load_yaml(config_path)
    if cfg["role"] != "A":
        raise SystemExit(
            f"this script trains Verifier-A; config declares role {cfg['role']!r}. "
            "Verifier-B has its own script and its own partition."
        )

    train, dev = load_training_rows(
        "A",
        split_map=cfg["inputs"]["split_map"],
        k2_assignments=cfg["inputs"]["k2_assignments"],
        cleaned_csv=cfg["inputs"]["cleaned_csv"],
    )
    _assert_expected(cfg, train, dev)

    # Inviolable rule 4, checked rather than remembered.
    gold = set(load_gold_ids(cfg["inputs"]["split_map"]))
    touched = set(train.review_ids) | set(dev.review_ids)
    if gold & touched:
        raise SystemExit(f"{len(gold & touched)} Gold-300 ids reached this script. Stop.")

    from sentence_transformers import SentenceTransformer
    from sklearn.linear_model import LogisticRegression

    m = cfg["model"]
    encoder = SentenceTransformer(m["labse_model"])
    enc = lambda rows: encoder.encode(  # noqa: E731
        list(rows.texts),
        batch_size=64,
        show_progress_bar=False,
        normalize_embeddings=m["normalize_embeddings"],
    )
    Xtr, Xdv = enc(train), enc(dev)

    clf = LogisticRegression(
        penalty=m["penalty"], C=m["C"], max_iter=m["max_iter"], random_state=42
    )
    clf.fit(Xtr, list(train.labels))

    y = list(dev.labels)
    pred = [int(p) for p in clf.predict(Xdv)]
    p_pos = [float(p[1]) for p in clf.predict_proba(Xdv)]
    macro_f1 = compare.macro_f1(y, pred)
    errors = [i for i, (t, p) in enumerate(zip(y, pred)) if t != p]

    # Reproduction check against S3.2b. One dev item is 1/82; anything larger
    # than half an item is a real change, not floating point.
    drift = abs(macro_f1 - S3B_REFERENCE_MACRO_F1)
    if drift > 0.5 / len(y):
        raise SystemExit(
            f"dev macro-F1 {macro_f1:.4f} differs from S3.2b's measured "
            f"{S3B_REFERENCE_MACRO_F1} by {drift:.4f} (> half a dev item). "
            "This is the same model on the same rows, so something moved: check "
            "the LaBSE revision, the split map and the K=2 assignments before "
            "believing either number."
        )

    cal = None
    if cfg["calibration"]["enabled"]:
        cal = calibration.calibrate(
            y,
            p_pos,
            n_bins=cfg["calibration"]["n_bins"],
            n_resamples=cfg["calibration"]["n_resamples"],
        ).to_dict()

    art = Path(cfg["outputs"]["artifact"])
    art.parent.mkdir(parents=True, exist_ok=True)
    import joblib

    joblib.dump(
        {
            "role": "A",
            "encoder": m["labse_model"],
            "normalize_embeddings": m["normalize_embeddings"],
            "head": clf,
            "temperature": (cal or {}).get("temperature"),
            "trained_on": {"partition": "R1", "n": len(train), "ids": list(train.review_ids)},
            "note": (
                "In-loop gate. Never use this artifact to score S6 -- that is "
                "Verifier-B's job and the wall between them is inviolable rule 6."
            ),
        },
        art,
    )

    with open(cfg["outputs"]["dev_predictions_csv"], "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["review_id", "y_true", "y_pred", "p_cluster1", "correct"])
        for rid, t, p, pp in zip(dev.review_ids, y, pred, p_pos):
            w.writerow([rid, t, p, f"{pp:.6f}", int(t == p)])

    result = {
        "role": "A",
        "model": f"frozen {m['labse_model']} + L2 logistic",
        "n_train": len(train),
        "train_class_counts": train.class_counts,
        "n_dev": len(dev),
        "dev_class_counts": dev.class_counts,
        "dev_macro_f1": round(macro_f1, 6),
        "dev_errors": len(errors),
        "one_dev_item_in_macro_f1": round(1.0 / len(y), 6),
        "s3b_reference_macro_f1": S3B_REFERENCE_MACRO_F1,
        "reproduces_s3b": True,
        "calibration": cal,
        "artifact": str(art),
        "hyperparameters_selected": "none -- C, penalty and max_iter are library "
        "defaults fixed in the config, per protocol.md S3.3 decision 1",
    }
    provenance.write_result(result, cfg["outputs"]["results_json"], config_path=config_path)
    provenance.write_text_lf(cfg["outputs"]["results_md"], _render(result))
    return result


def _render(r: dict) -> str:
    lines = [
        "# S3.3a — Verifier-A (the in-loop gate)",
        "",
        f"**{r['model']}**, trained on **R1, n = {r['n_train']}** "
        f"({r['train_class_counts']}), evaluated on **dev-{r['n_dev']}** "
        f"({r['dev_class_counts']}).",
        "",
        f"- dev macro-F1 **{r['dev_macro_f1']:.4f}** — **{r['dev_errors']} error(s) "
        f"on {r['n_dev']} items**.",
        f"- One dev item = **{r['one_dev_item_in_macro_f1']:.4f}** macro-F1. Read every",
        "  gap below in items, not in decimal places.",
        f"- Reproduces S3.2b's measured **{r['s3b_reference_macro_f1']}** for the same",
        "  model on the same rows, which is the point of running the check.",
        f"- Hyperparameters selected: **{r['hyperparameters_selected']}**.",
        "",
        "## What this number is NOT",
        "",
        "It is **label reproduction**, not persona detection. `cluster_k2` was",
        "produced by k-means on LaBSE embeddings, so a linear probe on those same",
        "embeddings is the label's own generating geometry asked to reproduce",
        "itself (S3.2b, `CIRCULARITY_CONFIRMED`). The label is nonetheless real —",
        "RQ1-H showed humans perceive the distinction at 0.78/0.84 against 0.25",
        "chance — it is simply *linear in LaBSE space*.",
        "",
        "⚠️ **The stated weakness, kept in the open:** a verifier that is a linear",
        "function of LaBSE may be trivially gameable by a generator scored in that",
        "same space. That is why Verifier-B is a different family on different data,",
        "and it is the failure RQ5 exists to detect.",
        "",
    ]
    c = r.get("calibration")
    if c:
        lines += [
            "## S3.4 calibration — **descriptive**",
            "",
            f"Temperature **{c['temperature']:.4f}**, fitted on {c['temperature_fitted_on']}.",
            "",
            "| | before | after |",
            "|---|---|---|",
            f"| ECE ({c['n_bins']} bins) | {c['ece_before']:.4f} | {c['ece_after']:.4f} |",
            f"| Brier | {c['brier_before']:.4f} | {c['brier_after']:.4f} |",
            f"| NLL | {c['nll_before']:.4f} | {c['nll_after']:.4f} |",
            "",
            f"ΔECE = **{c['ece_delta']:+.4f}**, bootstrap 95% CI "
            f"**[{c['ece_delta_ci_low']:+.4f}, {c['ece_delta_ci_high']:+.4f}]** → "
            f"**`{c['verdict']}`**.",
            "",
        ]
        if c["verdict"] == "CALIBRATION_NOT_ESTABLISHED":
            lines += [
                "**Pre-committed null statement fires (protocol.md, 2026-08-08):**",
                "*calibration could not be established at this sample size.* The",
                "improvement is smaller than its own uncertainty, and 82 rows over",
                "5 bins is ~16 samples per bin. This is reported as the outcome it",
                "is, not softened — and §4.5's τ is therefore a sensitivity curve,",
                "never a point.",
                "",
            ]
        lines += [
            "🔴 **Context for this table (protocol.md, 2026-08-11).** Decision 16",
            "originally defended Verifier-A as *natively calibrated*. That clause was",
            "withdrawn: `zhang2026tabpfn` measure logistic heads on frozen encoders",
            "across 22,820 episodes and find them **best on accuracy, near-worst on",
            "ECE and NLL**. The choice of Verifier-A stands; that sentence does not.",
            "",
        ]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    a = ap.parse_args()
    r = run(a.config)
    print(json.dumps({k: r[k] for k in ("role", "n_train", "n_dev", "dev_macro_f1", "dev_errors")}, indent=2))


if __name__ == "__main__":
    main()
