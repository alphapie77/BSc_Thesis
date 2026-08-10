"""S3.3b -- fit Verifier-B: the S3.2 BanglaBERT recipe, retrained on R2's 888 rows.

Pre-registered in `docs/protocol.md` section "S3.3 pre-commitment".

**Verifier-B is the wall.** It scores S6 and never enters the loop (inviolable
rule 6). RQ5's Goodhart test is the gap between what Verifier-A says about the
loop's output and what Verifier-B says about the same output; if the two are
entangled, the gap measures nothing and the rule exists to prevent exactly that.

**The ambiguity this file closes.** Decision 16 (2026-08-10) defined Verifier-B
as *"the fine-tuned BanglaBERT from S3.2"*. But `configs/s3_backbone.yaml` sets
`role: A`, so every S3.2 arm trained on **R1** -- Verifier-A's data. Read
literally, that sentence put A and B on the same rows. Nobody read it that way,
which is why it survived review; **code does not read intent.** The binding
definition, fixed 2026-08-11 and enforced here: Verifier-B is the *recipe* --
same backbone, same budget, same seeds -- **retrained on R2**. No S3.2
checkpoint is loaded. This module has no code path that could load one.

**Three things are deliberately not chosen by looking at a score.** The learning
rate is the pipeline §3.1 default (`schneider2025overtuning`: ~10% of tuned runs
generalise worse than the default, worst under exactly our conditions). The
persisted artifact is the seed-42 model, declared before any number exists. And
dev-82 is a reporting surface only.

Needs a GPU. Run it from `notebooks/s3d_verifier_b_kaggle.ipynb` with **Save &
Run All (Commit)**, not an interactive session -- checkpoints in `/kaggle/working`
do not survive across sessions, which cost four hours on 2026-08-09.

Run:
    python -m src.verifier.train_verifier_b --config configs/s3d_verifier_b.yaml
    python -m src.verifier.train_verifier_b --config ... --dry-run   # CPU, no model
"""

from __future__ import annotations

import os

# Same one-GPU pin as S3.2, for the same reason: on a 2-GPU host the arms were
# not on equal hardware and the comparison silently stopped being one.
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

#: S3.2's BanglaBERT arm, trained on R1. Reported beside B's number as context
#: only -- it is a DIFFERENT model on DIFFERENT data and the two are not a
#: before/after pair.
S3_BANGLABERT_ON_R1 = 0.9647

#: protocol.md S3.3 three-outcome commitment: at or below the S3.2b length rule
#: means something is broken, not that BanglaBERT is weak.
BROKEN_FLOOR = 0.6197


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
            "The data moved under a frozen split:\n  - " + "\n  - ".join(problems)
        )


def _assert_wall(cfg, train, dev) -> None:
    """The A/B wall and the G-300 wall, checked rather than remembered."""
    smap = json.loads(Path(cfg["inputs"]["split_map"]).read_text(encoding="utf-8"))
    r1, gold = set(smap["R1"]), set(smap["G"])
    ids = set(train.review_ids)

    leak = ids & r1
    if leak:
        raise SystemExit(
            f"🔴 {len(leak)} of Verifier-B's training ids are in R1 — Verifier-A's "
            "partition. This collapses inviolable rule 6 and makes RQ5's Goodhart "
            "gap unmeasurable. Stop and do not train."
        )
    if ids & gold:
        raise SystemExit(f"{len(ids & gold)} Gold-300 ids reached training. Stop.")
    if set(dev.review_ids) & ids:
        raise SystemExit("dev rows are inside Verifier-B's training set. Stop.")


def _finetune_probs(train, dev, cfg: dict, seed: int, lr: float):
    """The S3.2 fine-tuning loop, returning probabilities as well as predictions.

    Mirrors `backends.finetune_predict` step for step. It is duplicated rather
    than parameterised because that function's behaviour is pinned to a
    completed result (`results/s3_backbone_ablation.json`), and adding a branch
    to it would mean the code that produced that table is no longer the code in
    the repository. Probabilities are needed here and were not needed there: the
    ablation compared hard predictions; a verifier has to be calibrated.
    """
    set_seed(seed)
    import torch
    from torch.utils.data import DataLoader, TensorDataset
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    m, t = cfg["model"], cfg["training"]
    tok = AutoTokenizer.from_pretrained(m["model"])
    model = AutoModelForSequenceClassification.from_pretrained(m["model"], num_labels=2)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    def encode(rows) -> TensorDataset:
        enc = tok(
            list(rows.texts),
            truncation=True,
            padding="max_length",
            max_length=t["max_length"],
            return_tensors="pt",
        )
        return TensorDataset(enc["input_ids"], enc["attention_mask"], torch.tensor(rows.labels))

    loader = DataLoader(
        encode(train),
        batch_size=t["batch_size"],
        shuffle=True,
        generator=torch.Generator().manual_seed(seed),
    )
    opt = torch.optim.AdamW(model.parameters(), lr=lr)

    model.train()
    for _ in range(t["epochs"]):
        for ids, mask, y in loader:
            opt.zero_grad()
            out = model(input_ids=ids.to(device), attention_mask=mask.to(device), labels=y.to(device))
            out.loss.backward()
            opt.step()

    model.eval()
    preds: list[int] = []
    probs: list[float] = []
    with torch.no_grad():
        for ids, mask, _ in DataLoader(encode(dev), batch_size=t["batch_size"]):
            logits = model(input_ids=ids.to(device), attention_mask=mask.to(device)).logits
            p = torch.softmax(logits, dim=-1)[:, 1]
            probs.extend(p.cpu().tolist())
            preds.extend(logits.argmax(dim=-1).cpu().tolist())
    return model, tok, preds, probs


def _stub(train, dev, seed: int):
    """CPU dry-run: shape-correct output, no model, no download.

    Exists so that the wall assertions, the config contract, the provenance
    stamp and the markdown renderer are all exercised before an hour of GPU time
    is spent -- the `--check-arms` lesson from 2026-08-09, applied here as
    `--dry-run`.
    """
    import random

    rng = random.Random(seed)
    probs = [rng.random() for _ in range(len(dev))]
    return None, None, [1 if p >= 0.5 else 0 for p in probs], probs


def _redirect_outputs_for_dry_run(cfg: dict) -> None:
    """Point every output at `results/_dryrun/` and refuse `results/` itself.

    Added 2026-08-11 after the first `--dry-run` wrote four files into
    `results/` containing scores from a random number generator. They were
    deleted within the minute and nothing cited them -- but a file in `results/`
    is, by this project's own artifact index, something a reader may check, and
    "it was obviously a dry run" is not a property the filename carried.

    A dry run proves the plumbing works. It must not be able to leave anything
    behind that looks like it proved more.
    """
    scratch = Path("results/_dryrun")
    scratch.mkdir(parents=True, exist_ok=True)
    for key, value in list(cfg["outputs"].items()):
        cfg["outputs"][key] = str(scratch / Path(value).name)


def _sd(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    mu = sum(xs) / len(xs)
    return (sum((x - mu) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


def run(config_path: str, dry_run: bool = False) -> dict:
    cfg = _load_yaml(config_path)
    if cfg["role"] != "B":
        raise SystemExit(
            f"config declares role {cfg['role']!r}. This script trains Verifier-B "
            "and must draw R2. A config that says 'A' here would train the S6 "
            "evaluator on the in-loop verifier's data — the exact failure the "
            "2026-08-11 disambiguation exists to prevent."
        )

    if dry_run:
        _redirect_outputs_for_dry_run(cfg)

    train, dev = load_training_rows(
        "B",
        split_map=cfg["inputs"]["split_map"],
        k2_assignments=cfg["inputs"]["k2_assignments"],
        cleaned_csv=cfg["inputs"]["cleaned_csv"],
    )
    _assert_expected(cfg, train, dev)
    _assert_wall(cfg, train, dev)
    if set(load_gold_ids(cfg["inputs"]["split_map"])) & set(dev.review_ids):
        raise SystemExit("Gold-300 ids reached the dev slice. Stop.")

    y = list(dev.labels)
    lrs = cfg["training"]["learning_rates"]
    if len(lrs) != 1:
        raise SystemExit(
            f"{len(lrs)} learning rates configured. protocol.md S3.3 decision 1 "
            "fixes exactly one, taken from the spec and never selected. Two would "
            "reintroduce the selection this design refuses."
        )
    lr = float(lrs[0])

    keep_seed = cfg["artifact_selection"]["seed"]
    if cfg["artifact_selection"]["rule"] != "global_seed":
        raise SystemExit("only the pre-registered `global_seed` artifact rule is implemented.")
    if keep_seed not in cfg["training"]["seeds"]:
        raise SystemExit(f"artifact seed {keep_seed} is not among the trained seeds.")

    per_seed, kept = [], None
    for seed in cfg["training"]["seeds"]:
        model, tok, preds, probs = (
            _stub(train, dev, seed) if dry_run else _finetune_probs(train, dev, cfg, seed, lr)
        )
        f1 = compare.macro_f1(y, preds)
        per_seed.append({"seed": seed, "lr": lr, "macro_f1": round(f1, 6),
                         "errors": sum(1 for a, b in zip(y, preds) if a != b)})
        if seed == keep_seed:
            kept = {"model": model, "tok": tok, "preds": preds, "probs": probs, "macro_f1": f1}

    scores = [r["macro_f1"] for r in per_seed]
    mean_f1 = sum(scores) / len(scores)

    cal = None
    if cfg["calibration"]["enabled"]:
        cal = calibration.calibrate(
            y,
            kept["probs"],
            n_bins=cfg["calibration"]["n_bins"],
            n_resamples=cfg["calibration"]["n_resamples"],
        ).to_dict()

    if kept["macro_f1"] <= BROKEN_FLOOR:
        verdict = "BROKEN_CHECK_FOR_BUG"
    elif kept["macro_f1"] >= 0.90:
        verdict = "COMPETENT_EVALUATOR"
    else:
        verdict = "WEAKER_EVALUATOR_BOUND_RQ5"

    art = Path(cfg["outputs"]["artifact"])
    art.parent.mkdir(parents=True, exist_ok=True)
    if not dry_run:
        save_dir = art.with_suffix("")
        kept["model"].save_pretrained(save_dir)
        kept["tok"].save_pretrained(save_dir)
        import joblib

        joblib.dump(
            {
                "role": "B",
                "backbone": cfg["model"]["model"],
                "weights_dir": str(save_dir),
                "temperature": (cal or {}).get("temperature"),
                "seed": keep_seed,
                "trained_on": {"partition": "R2", "n": len(train), "ids": list(train.review_ids)},
                "note": (
                    "S6 EVALUATION ONLY. This artifact must never be called from "
                    "src/agents/ — inviolable rule 6, and RQ5 is the reason."
                ),
            },
            art,
        )

    with open(cfg["outputs"]["per_seed_csv"], "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["seed", "lr", "macro_f1", "errors"])
        w.writeheader()
        w.writerows(per_seed)
    with open(cfg["outputs"]["dev_predictions_csv"], "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["review_id", "y_true", "y_pred", "p_cluster1", "correct"])
        for rid, t_, p_, pp in zip(dev.review_ids, y, kept["preds"], kept["probs"]):
            w.writerow([rid, t_, p_, f"{pp:.6f}", int(t_ == p_)])

    result = {
        "role": "B",
        "verdict": verdict,
        "dry_run": dry_run,
        "model": cfg["model"]["model"],
        "n_train": len(train),
        "train_class_counts": train.class_counts,
        "n_dev": len(dev),
        "dev_class_counts": dev.class_counts,
        "learning_rate": lr,
        "hyperparameters_selected": "none — one lr, taken from pipeline §3.1",
        "artifact_seed": keep_seed,
        "artifact_selection_rule": "global_seed, pre-declared; NOT best-of-five",
        "dev_macro_f1_artifact": round(kept["macro_f1"], 6),
        "dev_macro_f1_mean_over_seeds": round(mean_f1, 6),
        "dev_macro_f1_sd_over_seeds": round(_sd(scores), 6),
        "per_seed": per_seed,
        "one_dev_item_in_macro_f1": round(1.0 / len(y), 6),
        "s3_banglabert_on_R1_for_context": S3_BANGLABERT_ON_R1,
        "calibration": cal,
        "artifact": str(art),
    }
    provenance.write_result(result, cfg["outputs"]["results_json"], config_path=config_path)
    provenance.write_text_lf(cfg["outputs"]["results_md"], _render(result))
    return result


def _render(r: dict) -> str:
    one = r["one_dev_item_in_macro_f1"]
    lines = [
        "# S3.3b — Verifier-B (S6 evaluation only; never in the loop)",
        "",
        f"**Verdict `{r['verdict']}`**" + ("  ⚠️ **DRY RUN — no model was trained**" if r["dry_run"] else ""),
        "",
        f"`{r['model']}`, the S3.2 **recipe** retrained on **R2, n = {r['n_train']}** "
        f"({r['train_class_counts']}); evaluated on **dev-{r['n_dev']}** ({r['dev_class_counts']}).",
        "",
        f"- **dev macro-F1 {r['dev_macro_f1_artifact']:.4f}** (the persisted seed-"
        f"{r['artifact_seed']} model).",
        f"- Across 5 seeds: **{r['dev_macro_f1_mean_over_seeds']:.4f} ± "
        f"{r['dev_macro_f1_sd_over_seeds']:.4f}** — reported as a sensitivity band, "
        "not as a score distribution for model comparison (Bethard 2022).",
        f"- One dev item = **{one:.4f}** macro-F1.",
        f"- Learning rate **{r['learning_rate']:.0e}**, hyperparameters selected: "
        f"**{r['hyperparameters_selected']}**.",
        f"- Artifact chosen by **{r['artifact_selection_rule']}**.",
        "",
        "## The wall, and what it is made of",
        "",
        "| | Verifier-A | Verifier-B |",
        "|---|---|---|",
        "| Data | R1 (804) | **R2 (888)** — disjoint by the frozen split |",
        "| Pretraining | LaBSE, multilingual | BanglaBERT, Bangla-native ELECTRA |",
        "| Adaptation | frozen + linear head | fine-tuned end to end |",
        "| Tokenizer | LaBSE | BanglaBERT |",
        "",
        "The original design separated A and B **only by split**. After decision 16",
        "the separation is methodological as well — which `mahmoud2026rubric` make",
        "the standard, and which `wang2026hacking` justify by naming",
        "evaluator–policy co-adaptation as a mechanism of reward hacking.",
        "",
        f"⚠️ S3.2's BanglaBERT arm scored {r['s3_banglabert_on_R1_for_context']} — "
        "**on R1**. It is a different model on different data and is quoted here as",
        "context only, never as a before/after pair with the number above.",
        "",
        "🔴 **No claim that either verifier is better may be made from dev-82.** At",
        f"{one:.4f} per item the expected A−B difference is under two reviews, and",
        "that limit was pre-committed before either was trained.",
        "",
    ]
    if r["verdict"] == "BROKEN_CHECK_FOR_BUG":
        lines += [
            "## 🔴 Below the pre-registered floor",
            "",
            f"Verifier-B is at or below the S3.2b length rule ({BROKEN_FLOOR}). Per the",
            "three-outcome commitment this is **checked for a bug before it is",
            "believed** — R2's labels, the tokenizer, or the retraining. It is not",
            "reported as evidence that BanglaBERT is weak.",
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
                "**Pre-committed null statement fires:** *calibration could not be",
                "established at this sample size.*",
                "",
            ]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--dry-run", action="store_true",
                    help="CPU shape check: exercises the walls and the renderer, trains nothing.")
    a = ap.parse_args()
    r = run(a.config, dry_run=a.dry_run)
    print(json.dumps({k: r[k] for k in
                      ("role", "verdict", "n_train", "n_dev",
                       "dev_macro_f1_artifact", "dev_macro_f1_sd_over_seeds")}, indent=2))


if __name__ == "__main__":
    main()
