"""S3.2 -- verifier backbone ablation. Pre-registered in docs/protocol.md.

Seven arms, five seeds, winner decided by paired bootstrap. Run:

    python -m src.verifier.s3_backbone_ablation --config configs/s3_backbone.yaml
    python -m src.verifier.s3_backbone_ablation --config ... --dry-run

`--dry-run` exercises every step except the fine-tuning itself, using a
deterministic stub predictor. It exists so the split contract, the bootstrap,
the tie-break and the file writing can be checked on a laptop **before** GPU
time is spent, rather than discovering at hour three that the dev set had 84
rows in it.

The stub's scores are meaningless by construction and every artifact it writes
is stamped `dry_run: true`. A dry-run result must never be read as a result.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import sys
import zlib
from pathlib import Path

from src.common.seed import set_seed
from src.common import provenance
from src.verifier import compare
from src.verifier.split_access import load_gold_ids, load_training_rows

set_seed()  # first action, before anything imports torch (inviolable rule 2)


def _load_yaml(path: str | Path) -> dict:
    try:
        import yaml
    except ImportError:  # pragma: no cover
        sys.exit("PyYAML is required: pip install pyyaml")
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _assert_expected(train, dev, expected: dict) -> None:
    """Refuse to run if the data is not the data the pre-registration describes.

    This is not defensive padding. The n was written into protocol.md on
    2026-08-08 *before any result existed*, precisely so that a weak number
    later could not be blamed on the method. If n has drifted, the comparison to
    that pre-registration is void, and the right move is to stop and find out
    why -- not to train on whatever happens to be there.
    """
    problems = []
    if len(train) != expected["train_n"]:
        problems.append(f"train n = {len(train)}, pre-registered {expected['train_n']}")
    if train.class_counts != {int(k): v for k, v in expected["train_class_counts"].items()}:
        problems.append(f"train classes = {train.class_counts}, pre-registered {expected['train_class_counts']}")
    if dev is None:
        problems.append("dev slice is missing")
    else:
        if len(dev) != expected["dev_n"]:
            problems.append(f"dev n = {len(dev)}, pre-registered {expected['dev_n']}")
        if dev.class_counts != {int(k): v for k, v in expected["dev_class_counts"].items()}:
            problems.append(f"dev classes = {dev.class_counts}, pre-registered {expected['dev_class_counts']}")
    if problems:
        raise SystemExit(
            "S3.2 refuses to run -- the data does not match the pre-registration:\n  - "
            + "\n  - ".join(problems)
            + "\nFix the cause, or amend protocol.md and log a deviation. Do not "
              "edit the expected counts to match the data."
        )


def _stub_predict(train, dev, arm: dict, seed: int, lr: float) -> list[int]:
    """A deterministic stand-in for a fine-tuned model. Dry-run only.

    Deliberately weak and deliberately arm-dependent: it thresholds review
    length at the training median, with the threshold nudged by a hash of the
    arm key and seed. That gives the plumbing realistic-looking, *varying*,
    reproducible predictions without pretending to be a model. If this ever
    produced a good score it would mean the task is trivially length-solvable,
    which S2e already measured (length_auc 0.6764) and which the guideline
    controls for.
    """
    lengths = sorted(len(t.split()) for t in train.texts)
    median = lengths[len(lengths) // 2]
    # zlib.crc32, NOT the builtin hash(): Python randomises string hashing per
    # process, and set_seed()'s PYTHONHASHSEED assignment cannot undo that
    # because the interpreter reads it at startup. The first dry run of this
    # script was not reproducible across processes for exactly this reason, and
    # the check that caught it is `--dry-run` run twice. A stub is allowed to be
    # meaningless; it is not allowed to be non-deterministic.
    nudge = (zlib.crc32(f"{arm['key']}:{seed}".encode()) % 5) - 2
    majority = max(train.class_counts, key=train.class_counts.get)
    minority = 1 - majority
    return [minority if len(t.split()) > median + nudge else majority for t in dev.texts]


def _train_and_predict(train, dev, arm: dict, seed: int, lr: float, cfg: dict) -> list[int]:
    """Fine-tune one arm at one seed and return its dev predictions.

    Imported lazily so that --dry-run, the tests, and the split-contract check
    all work on a machine with no torch installed.
    """
    kind = arm.get("kind", "finetune")
    if kind == "finetune":
        from src.verifier.backends import finetune_predict
        return finetune_predict(train, dev, arm, seed, lr, cfg)
    if kind == "setfit":
        from src.verifier.backends import setfit_predict
        return setfit_predict(train, dev, arm, seed, lr, cfg)
    if kind == "nli_transfer":
        from src.verifier.backends import nli_transfer_predict
        return nli_transfer_predict(train, dev, arm, seed, lr, cfg)
    raise ValueError(f"unknown arm kind {kind!r} for arm {arm['key']!r}")


def run(config_path: str, dry_run: bool = False) -> dict:
    cfg = _load_yaml(config_path)
    inputs, training, decision = cfg["inputs"], cfg["training"], cfg["decision"]

    train, dev = load_training_rows(
        cfg["role"],
        split_map=inputs["split_map"],
        k2_assignments=inputs["k2_assignments"],
        cleaned_csv=inputs["cleaned_csv"],
    )
    _assert_expected(train, dev, cfg["expected"])

    # Recorded in the result file so a reader can verify the wall held, rather
    # than trusting that it did.
    gold = set(load_gold_ids(inputs["split_map"]))
    touched = set(train.review_ids) | set(dev.review_ids)
    assert not (gold & touched), "Gold-300 leaked into S3.2 -- stop."

    y_true = list(dev.labels)
    per_seed: list[dict] = []
    best_pred: dict[str, list[int]] = {}
    mean_scores: dict[str, float] = {}

    # Checkpoint after every arm. The real run is ~70 fine-tunings against a
    # 12h session cap, so a crash in arm 6 would otherwise discard five arms'
    # worth of GPU time -- and Kaggle's weekly quota is 30h, which makes that a
    # real cost rather than an inconvenience. Resuming is safe because each arm
    # is trained independently and seeds are fixed: a resumed arm would produce
    # the same numbers it produced before.
    ckpt_path = Path(str(out_json := cfg["outputs"]["results_json"]).replace(".json", ".ckpt.json"))
    done: dict[str, dict] = {}
    if ckpt_path.exists() and not dry_run:
        done = json.loads(ckpt_path.read_text(encoding="utf-8"))
        print(f"resuming: {sorted(done)} already complete (delete {ckpt_path} to force a fresh run)")

    for arm in cfg["arms"]:
        if arm["key"] in done:
            saved = done[arm["key"]]
            per_seed.extend(saved["per_seed"])
            best_pred[arm["key"]] = saved["best_pred"]
            mean_scores[arm["key"]] = saved["mean_score"]
            continue
        scores_by_lr: dict[float, list[float]] = {}
        preds_by_lr: dict[float, list[list[int]]] = {}
        for lr, seed in itertools.product(training["learning_rates"], training["seeds"]):
            set_seed(seed)
            pred = (
                _stub_predict(train, dev, arm, seed, lr)
                if dry_run
                else _train_and_predict(train, dev, arm, seed, lr, cfg)
            )
            score = compare.macro_f1(y_true, pred)
            scores_by_lr.setdefault(lr, []).append(score)
            preds_by_lr.setdefault(lr, []).append(pred)
            per_seed.append(
                {"arm": arm["key"], "lr": lr, "seed": seed, "macro_f1": round(score, 6)}
            )

        # The learning rate is a nuisance parameter, not a finding: pick the one
        # with the better MEAN across seeds, then compare arms at that setting.
        # Picking the best single (lr, seed) run would be selecting on the noise
        # the whole decision rule exists to avoid.
        best_lr = max(scores_by_lr, key=lambda k: sum(scores_by_lr[k]) / len(scores_by_lr[k]))
        seed_scores = scores_by_lr[best_lr]
        mean_scores[arm["key"]] = sum(seed_scores) / len(seed_scores)
        # Representative prediction = the seed whose score is the median, so the
        # paired test runs on a typical run rather than a lucky one.
        order = sorted(range(len(seed_scores)), key=lambda i: seed_scores[i])
        best_pred[arm["key"]] = preds_by_lr[best_lr][order[len(order) // 2]]

        if not dry_run:
            done[arm["key"]] = {
                "per_seed": [r for r in per_seed if r["arm"] == arm["key"]],
                "best_pred": best_pred[arm["key"]],
                "mean_score": mean_scores[arm["key"]],
            }
            ckpt_path.parent.mkdir(parents=True, exist_ok=True)
            provenance.write_text_lf(ckpt_path, json.dumps(done, indent=2) + "\n")
            print(f"[checkpoint] {arm['key']} done, mean macro-F1 {mean_scores[arm['key']]:.4f}")

    arm_keys = [a["key"] for a in cfg["arms"]]
    pairs, p_values = [], []
    for a, b in itertools.combinations(arm_keys, 2):
        res = compare.paired_bootstrap(
            y_true, best_pred[a], best_pred[b],
            arm_a=a, arm_b=b,
            n_resamples=decision["n_resamples"],
        )
        pairs.append(res)
        p_values.append(res.p_value)

    rejected = compare.benjamini_hochberg(p_values, alpha=decision["alpha"])
    significant = {(r.arm_a, r.arm_b) for r, ok in zip(pairs, rejected) if ok}
    outcome = compare.verdict(arm_keys, mean_scores, significant)

    result = {
        "dry_run": dry_run,
        "verdict": outcome,
        "n_train": len(train),
        "n_dev": len(dev),
        "train_class_counts": train.class_counts,
        "dev_class_counts": dev.class_counts,
        "gold_ids_touched": 0,
        "seeds": training["seeds"],
        "mean_macro_f1": {k: round(v, 6) for k, v in sorted(mean_scores.items(), key=lambda kv: -kv[1])},
        "seed_sd": {
            k: round(_sd([r["macro_f1"] for r in per_seed if r["arm"] == k]), 6)
            for k in arm_keys
        },
        "pairwise": [
            {
                "arm_a": r.arm_a, "arm_b": r.arm_b,
                "diff": round(r.observed_diff, 6),
                "p": round(r.p_value, 6),
                "ci95": [round(r.ci_low, 6), round(r.ci_high, 6)],
                "significant_bh": ok,
            }
            for r, ok in zip(pairs, rejected)
        ],
    }

    out = cfg["outputs"]
    provenance.write_result(result, out["results_json"], config_path=config_path)
    _write_per_seed(out["per_seed_csv"], per_seed)
    provenance.write_text_lf(out["results_md"], _render_md(result, cfg))
    return result


def _sd(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = sum(xs) / len(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


def _write_per_seed(path: str, rows: list[dict]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["arm", "lr", "seed", "macro_f1"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def _render_md(result: dict, cfg: dict) -> str:
    banner = (
        "> ⛔ **DRY RUN — NOT A RESULT.** Predictions came from a deterministic\n"
        "> length-threshold stub, not from any trained model. This file exists to\n"
        "> prove the plumbing works before GPU time is spent.\n\n"
        if result["dry_run"] else ""
    )
    lines = [
        "# S3.2 — verifier backbone ablation",
        "",
        banner + f"**Verdict: `{result['verdict']}`**",
        "",
        f"- train n = **{result['n_train']}** {result['train_class_counts']}"
        f" · dev n = **{result['n_dev']}** {result['dev_class_counts']}",
        f"- seeds: {result['seeds']} · decision rule: **paired bootstrap**"
        f" ({cfg['decision']['n_resamples']} resamples, BH at α={cfg['decision']['alpha']})",
        "- Gold-300 rows touched: **0**. R2 not read (role A → R1).",
        "",
        "⚠️ The winner is selected on **weak-label macro-F1 — label *reproduction*,",
        "not validity.** No human-validated accuracy exists for any verifier",
        "(deviation of 2026-08-08). Any defence of the backbone choice must say so.",
        "",
        "## Mean macro-F1 (± SD across seeds — sensitivity, not the decision rule)",
        "",
        "| Arm | mean macro-F1 | SD |",
        "|---|---|---|",
    ]
    for arm, score in result["mean_macro_f1"].items():
        lines.append(f"| `{arm}` | {score:.4f} | {result['seed_sd'][arm]:.4f} |")
    lines += ["", "## Pairwise paired bootstrap", "",
              "| A | B | diff | 95% CI | p | significant (BH) |", "|---|---|---|---|---|---|"]
    for p in result["pairwise"]:
        mark = "**yes**" if p["significant_bh"] else "no"
        lines.append(
            f"| `{p['arm_a']}` | `{p['arm_b']}` | {p['diff']:+.4f} | "
            f"[{p['ci95'][0]:+.4f}, {p['ci95'][1]:+.4f}] | {p['p']:.4f} | {mark} |"
        )
    if result["verdict"] == "TIE":
        lines += [
            "",
            "## Tie — and it was pre-registered as the likely outcome",
            "",
            "No arm significantly beats every other. Per protocol.md §S3.2 the tie is",
            f"**reported as the result**, and the tie-break `{cfg['decision']['tie_break']}`",
            "is applied on non-performance grounds. The thesis must state that **the",
            "backbone choice was not determined by the data.**",
        ]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--dry-run", action="store_true",
                    help="stub the models; check plumbing without a GPU")
    args = ap.parse_args()
    res = run(args.config, dry_run=args.dry_run)
    print(json.dumps({k: res[k] for k in ("dry_run", "verdict", "n_train", "n_dev")}, indent=2))
    print("mean macro-F1:", json.dumps(res["mean_macro_f1"], indent=2))


if __name__ == "__main__":
    main()
