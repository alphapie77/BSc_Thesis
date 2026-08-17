"""S3.5 -- fit the symbolic scorer and report what each family contributes.

Pre-registered in `docs/protocol.md` section "S3.5 pre-commitment" (2026-08-11), BEFORE
this file existed. Read it first. In particular:

* Weights are **learned, never hand-set** (pipeline section 3.5's own rule).
* The fit is on the **82 labelled dev rows**, per section 3.5. That is ~8 rows per
  feature. The script therefore reports a stratified cross-validated estimate
  BESIDE the resubstitution one, and labels the latter optimistic every time,
  because at this n the gap between them is the whole story.
* **F1 (IDF) is OFF by default** pending Sabbir's ruling on inviolable rule 7.
  See the rule-7 note in `features.py`.
* The hybrid neural/symbolic weight is NOT fit here. It moved to the 30
  dev-plots' generations (deviation 2026-08-11) because Verifier-A makes one
  error in 82 and the sweep on this slice is degenerate.

This script trains a logistic regression, which is one of the ten small
artifacts inviolable rule 10 permits. No LLM is fine-tuned anywhere.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import yaml
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.common.seed import set_seed
from src.common.provenance import write_result, write_text_lf
from src.symbolic.features import FeatureSpec, build_idf, extract_matrix, feature_names
from src.verifier.split_access import load_gold_ids, load_training_rows

#: Which feature belongs to which pre-registered family, and whether that family
#: was registered as gameable. Used for the leave-one-family-out table, which is
#: the point of the whole script: a gain arriving only through gameable families
#: is a NEGATIVE result about the hybrid design and must be visible as one.
FAMILY = {
    "idf_min": "F1_idf", "idf_max": "F1_idf", "idf_mean": "F1_idf",
    "n_tokens": "F2_length", "mean_word_chars": "F2_length",
    "punct_per_tok": "F3_ortho", "digit_per_tok": "F3_ortho",
    "latin_per_tok": "F3_ortho", "ends_dandi": "F3_ortho",
    "connective_frac": "F4_connective",
    "pos_frac": "F5_sentiment", "neg_frac": "F5_sentiment",
    "intensifier_frac": "F5_sentiment",
    "guiraud": "F6_richness",
}
GAMEABLE = {"F2_length", "F3_ortho", "F4_connective", "F5_sentiment"}


def _fit(x: np.ndarray, y: np.ndarray, seed: int):
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=2000, random_state=seed),
    ).fit(x, y)


def _cv_macro_f1(x: np.ndarray, y: np.ndarray, seed: int, folds: int) -> tuple[float, float]:
    """Stratified CV. The honest number at n=82; resubstitution is not."""
    skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    scores = [
        f1_score(y[te], _fit(x[tr], y[tr], seed).predict(x[te]), average="macro")
        for tr, te in skf.split(x, y)
    ]
    return float(np.mean(scores)), float(np.std(scores))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    seed = int(cfg.get("seed", 42))
    set_seed(seed)  # inviolable rule 2: first action.

    spec = FeatureSpec(enable_f1=bool(cfg["features"]["enable_f1"]))
    folds = int(cfg["fit"]["cv_folds"])
    pilot = bool(cfg.get("pilot", False))

    # ---- inviolable rule 7, enforced instead of remembered -----------------
    # Rule 7: "no TF-IDF in the main pipeline ... allowed ONLY as an
    # explicitly-labelled cheap proxy in a pilot, NEVER in a result."
    # F1 is IDF only, but the rule's text governs results, not our reading of
    # it. So: enabling F1 is permitted *only* under an explicitly pilot-labelled
    # config writing to a pilot-labelled path. Anything else refuses to run.
    # This is a guard of the same kind as split_access.py's wall -- the point is
    # that a copy-pasted config cannot quietly put IDF into a result.
    if spec.enable_f1:
        out_json = str(cfg["outputs"]["results_json"])
        if not pilot or "pilot" not in Path(out_json).name.lower():
            raise SystemExit(
                "RULE 7: enable_f1 requires `pilot: true` AND an output filename "
                f"containing 'pilot'. Got pilot={pilot}, out={out_json!r}. "
                "TF-IDF-family features may never enter a result file."
            )
        # The artifact is the newer hole in the same wall. A result file is
        # read by a human; an artifact is loaded by the Critic and its contents
        # never appear anywhere. So an IDF-enabled scorer reaching the default
        # artifact path would put rule-7 features into every generation's score
        # with nothing on screen to show it. Same guard, applied to the path
        # that is harder to notice.
        out_art = str(cfg["outputs"].get("artifact", ""))
        if out_art and "pilot" not in Path(out_art).name.lower():
            raise SystemExit(
                "RULE 7: an F1/IDF-enabled scorer may not be written to a "
                f"non-pilot artifact path. Got artifact={out_art!r}. The Critic "
                "loads artifacts silently; this is the path where a violation "
                "would leave no visible trace."
            )

    train, dev = load_training_rows(
        "A",
        split_map=cfg["inputs"]["split_map"],
        k2_assignments=cfg["inputs"]["k2_assignments"],
        cleaned_csv=cfg["inputs"]["cleaned_csv"],
    )
    if dev is None or len(dev) == 0:
        raise SystemExit("no dev rows -- section 3.5 fits the symbolic scorer on dev.")

    # Gold-300 is eval-only (rule 4). Asserted, not assumed.
    gold = set(load_gold_ids(cfg["inputs"]["split_map"]))
    touched = gold & (set(train.review_ids) | set(dev.review_ids))
    if touched:
        raise SystemExit(f"Gold-300 leak: {len(touched)} ids. Stop.")

    # IDF from TRAIN only. Building it on dev would leak the fitting
    # distribution into a feature -- the same shape of error as S3.2b's label.
    idf = build_idf(list(train.texts)) if spec.enable_f1 else None

    x_list, names = extract_matrix(list(dev.texts), spec, idf)
    x = np.asarray(x_list, dtype=float)
    y = np.asarray(dev.labels, dtype=int)

    model = _fit(x, y, seed)
    resub = float(f1_score(y, model.predict(x), average="macro"))
    cv_mean, cv_sd = _cv_macro_f1(x, y, seed, folds)

    coefs = dict(zip(names, model.named_steps["logisticregression"].coef_[0].tolist()))

    # Leave-one-family-out, on the CV estimate only. Resubstitution deltas at
    # n=82 measure fitting capacity, not contribution.
    fams = sorted({FAMILY[n] for n in names})
    loo = {}
    for fam in fams:
        keep = [i for i, n in enumerate(names) if FAMILY[n] != fam]
        if not keep:
            continue
        m, _ = _cv_macro_f1(x[:, keep], y, seed, folds)
        loo[fam] = {"cv_macro_f1_without": m, "delta": cv_mean - m,
                    "registered_gameable": fam in GAMEABLE}

    majority = float(f1_score(y, np.full_like(y, int(np.bincount(y).argmax())), average="macro"))

    result = {
        "n_dev_rows": len(dev),
        "n_train_rows_for_idf": len(train) if spec.enable_f1 else 0,
        "class_counts": dev.class_counts,
        "enable_f1_idf": spec.enable_f1,
        "n_features": len(names),
        "rows_per_feature": round(len(dev) / len(names), 2),
        "macro_f1_resubstitution_OPTIMISTIC": resub,
        "macro_f1_cv_mean": cv_mean,
        "macro_f1_cv_sd": cv_sd,
        "majority_baseline_macro_f1": majority,
        "coefficients": coefs,
        "leave_one_family_out": loo,
        "gold_touched": 0,
    }

    write_result(result, cfg["outputs"]["results_json"], args.config)

    # ---- persist the fitted scorer -----------------------------------------
    # Added 2026-08-11, and the reason is worth recording rather than treating
    # as an oversight: this script fitted a model, reported its numbers, and
    # then DISCARDED it. `results/s35_symbolic.json` carries the 11
    # coefficients -- but the estimator is a StandardScaler + LogisticRegression
    # pipeline, so without the scaler's mean/scale and the intercept the fitted
    # scorer is NOT reconstructable from anything committed.
    #
    # SS4.2's Critic is `w x VerifierA + (1-w) x symbolic`. Verifier-A had an
    # artifact; symbolic did not. The Critic was therefore unbuildable, and
    # nothing said so -- the S3.5 row in STATUS reads "BUILT + FITTED".
    # Found by inventory before writing the Critic, which is the only reason it
    # was not found by the Critic failing to load something.
    if cfg["outputs"].get("artifact"):
        import joblib
        import sklearn

        art_path = Path(cfg["outputs"]["artifact"])
        art_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "kind": "symbolic_scorer",
                "sklearn_version": sklearn.__version__,
                "pipeline": model,
                "feature_names": names,
                # The Critic must rebuild features in EXACTLY this order and
                # with exactly this spec. Storing the names beside the pipeline
                # means a mismatch raises instead of silently scoring a
                # permuted vector, which would look like a working Critic.
                "enable_f1": spec.enable_f1,
                "idf": idf,
                "fitted_on": {
                    "slice": "dev",
                    "n": len(dev),
                    "ids": list(dev.review_ids),
                },
                "cv_macro_f1_mean": cv_mean,
                "note": (
                    "Symbolic half of the SS4.2 Critic. If enable_f1 is True this "
                    "is a RULE 7 PILOT artifact and must never enter the loop -- "
                    "the Critic is required to refuse it."
                ),
            },
            art_path,
        )
        print(f"artifact -> {art_path}")

    banner = []
    if pilot:
        banner = [
            "> \u26d4 **PILOT, NOT A RESULT.** This run enables **F1 (IDF)**, which "
            "inviolable rule 7 permits *only* as an explicitly-labelled cheap proxy "
            "in a pilot, **never in a result**. Nothing in this file may be quoted "
            "in the thesis, a paper, or a results table. It exists to measure what "
            "rule 7 costs, so the cost is known rather than assumed.",
            "",
        ]

    lines = [
        "# S3.5 -- symbolic scorer" + (" (PILOT: F1/IDF enabled)" if pilot else ""),
        "",
        *banner,
        f"Fitted on **{len(dev)}** dev rows, **{len(names)}** features "
        f"(**{result['rows_per_feature']}** rows per feature). F1/IDF enabled: "
        f"**{spec.enable_f1}**.",
        "",
        "| Estimate | macro-F1 |",
        "|---|---|",
        f"| Resubstitution (**OPTIMISTIC -- fitted and scored on the same 82 rows**) | {resub:.4f} |",
        f"| Stratified {folds}-fold CV (**the honest number**) | {cv_mean:.4f} +/- {cv_sd:.4f} |",
        f"| Majority baseline | {majority:.4f} |",
        "",
        "## Leave-one-family-out (CV)",
        "",
        "| Family | CV without it | Delta | Registered gameable? |",
        "|---|---|---|---|",
    ]
    for fam, d in sorted(loo.items(), key=lambda kv: -kv[1]["delta"]):
        flag = "**yes**" if d["registered_gameable"] else "no"
        lines.append(f"| {fam} | {d['cv_macro_f1_without']:.4f} | {d['delta']:+.4f} | {flag} |")
    lines += [
        "",
        "> A contribution concentrated in the **gameable** families is "
        "pre-registered as a **negative result about the hybrid design**: it is "
        "exactly the part a generator could fake once the Reflector names the "
        "failing rule (section 4.2). See `docs/protocol.md`, S3.5 pre-commitment.",
        "",
    ]
    write_text_lf(cfg["outputs"]["results_md"], "\n".join(lines))
    print(f"resub={resub:.4f} cv={cv_mean:.4f}+/-{cv_sd:.4f} majority={majority:.4f}")


if __name__ == "__main__":
    main()
