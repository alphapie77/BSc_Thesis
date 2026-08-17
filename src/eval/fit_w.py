#!/usr/bin/env python3
"""`w` as a sensitivity curve, plus the held-out marginal-value test.

ref: `docs/protocol.md` §S4 registered decision 1, written 2026-08-11 before any
generation existed. Three scientific outcomes were pre-committed and are
reported verbatim:

  SYMBOLIC_EARNS_ITS_PLACE -- the verdict is sensitive to `w` AND the held-out
      marginal-value test favours including the symbolic term.
  SYMBOLIC_INERT -- the curve is flat in `w`. **Publishable negative result**,
      and the symbolic term is still RETAINED, because the Reflector needs a
      component that can name which rule failed and the LaBSE probe cannot.
  SYMBOLIC_HARMS -- the held-out test rejects the symbolic term.

Outcome 2 was registered as the one to expect.

PRECOMMITMENT_UNRESOLVED is not a fourth scientific outcome. It is an audit
state for an observed combination that the three registered rules do not map:
the verdict is sensitive to w, but the held-out test ties at the neural-only
endpoint. Labelling that combination INERT would silently weaken "flat in w".

WHAT IS MEASURED, AND THE LABEL'S LIMIT
---------------------------------------
The only label available on generated text is the level that was **requested**.
Every number here therefore measures *does the score agree with the
instruction*, not *is this text really level 1*: the generator's compliance is
assumed. That is the right quantity for fitting `w` -- rewarding compliance is
the Critic's job inside the loop -- and the wrong quantity for claiming the axis
was controlled. **No axis-control claim is made from this file.**

THE BASELINE IS NOT 0.5
-----------------------
S4.dev-LC measured that a **word count alone** recovers the requested level at
AUC 0.9111 (bn) and 0.9928 (en). So the reference for any hybrid score is the
length-only probe, not chance. A scorer that cannot beat counting words has not
earned its place, and the comparison is printed beside every curve.

⚠️ Both halves of the Critic were fitted on human reviews and are applied to
generated text (`kapur2026length`). That shift is why `w` is fitted here at all
rather than on dev-82, and it is restated wherever these scores appear.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.critic import Critic  # noqa: E402
from src.common.provenance import (  # noqa: E402
    write_csv_result,
    write_result,
    write_text_lf,
)
from src.common.seed import set_seed  # noqa: E402

#: Sensitivity of the *verdict*, not of a score: the share of generations whose
#: PASS/FAIL flips anywhere across the reported `w` range, at the τ that makes
#: the two endpoints most comparable (the median hybrid, so roughly half pass).
#: Registered as descriptive -- τ itself is decision 19's argmax and is not
#: selected here.
FLIP_TAU_QUANTILE = 0.5


class InputContractError(RuntimeError):
    """A declared S4.5a input is absent or not the registered archive."""


def auc(pos: list[float], neg: list[float]) -> float:
    """P(a positive scores above a negative), ties at 0.5. No sklearn needed."""
    if not pos or not neg:
        return float("nan")
    s = sum(1.0 if a > b else 0.5 if a == b else 0.0 for a in pos for b in neg)
    return s / (len(pos) * len(neg))


def dedupe(path: str | Path) -> list[dict]:
    """Read a generation archive, keeping the first row per key.

    The pilot archive carries duplicate keys from the 2026-08-12 resume bug and
    the files are append-only by design, so every consumer deduplicates.
    """
    seen: set[str] = set()
    out: list[dict] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        g = json.loads(line)
        if g["key"] in seen:
            continue
        seen.add(g["key"])
        out.append(g)
    return out


def validate_inputs(cfg: dict) -> dict[str, list[dict]]:
    """Load every declared archive and refuse a partial or malformed run."""
    validation = cfg["validation"]
    required = set(validation["required_conditions"])
    declared = {src["name"] for src in cfg["inputs"]}
    if declared != required:
        raise InputContractError(
            f"configured conditions {sorted(declared)} do not equal required "
            f"conditions {sorted(required)}"
        )

    expected_n = int(validation["expected_unique_generations_per_condition"])
    required_fields = set(validation["required_generation_fields"])
    loaded: dict[str, list[dict]] = {}
    for src in cfg["inputs"]:
        name, path = src["name"], Path(src["generations_jsonl"])
        if not path.is_file():
            raise InputContractError(f"required condition {name!r} is missing: {path}")
        rows = dedupe(path)
        if len(rows) != expected_n:
            raise InputContractError(
                f"condition {name!r} has {len(rows)} unique generations; "
                f"expected {expected_n}"
            )
        for i, row in enumerate(rows, 1):
            missing = required_fields - set(row)
            if missing:
                raise InputContractError(
                    f"condition {name!r} row {i} lacks fields {sorted(missing)}"
                )
        loaded[name] = rows
    return loaded


def score_all(critic: Critic, rows: list[dict]) -> list[dict]:
    """Neural and symbolic score per generation, for the level that was asked.

    Scored ONCE and reused across the whole `w` grid: the mixture is a weighted
    sum of two fixed numbers, so re-embedding per grid point would be 21x the
    cost for identical values -- and would invite the two halves to be computed
    under different conditions.
    """
    out = []
    for i, g in enumerate(rows, 1):
        n = critic.neural(g["text"], g["target_level"])
        s = critic.symbolic(g["text"], g["target_level"])
        out.append({
            "key": g["key"], "plot_id": g["plot_id"], "arm": g["arm"],
            "target_level": g["target_level"], "n_words": len(g["text"].split()),
            "neural": n, "symbolic": s,
        })
        if i % 20 == 0:
            print(f"    scored {i}/{len(rows)}", flush=True)
    return out


def curve(scored: list[dict], ws: list[float]) -> list[dict]:
    """AUC of the hybrid against the requested level, at each `w`.

    Positives are the level-1 requests and negatives the level-0 ones. Because
    each score is already P(y = target_level), a *good* scorer pushes BOTH
    classes up, so the discriminating quantity is the score itself only if the
    two groups are scored on the same question. They are not -- so the AUC below
    is computed on the level-1 probability `p1`, reconstructed as
    `score if target==1 else 1-score`. That reconstruction is exact and is the
    reason the Critic's asymmetric scoring does not corrupt this measurement.
    """
    rows = []
    for w in ws:
        p1_pos, p1_neg = [], []
        for r in scored:
            hybrid = w * r["neural"] + (1.0 - w) * r["symbolic"]
            p1 = hybrid if r["target_level"] == 1 else 1.0 - hybrid
            (p1_pos if r["target_level"] == 1 else p1_neg).append(p1)
        rows.append({"w": round(w, 4), "auc": auc(p1_pos, p1_neg),
                     "n_pos": len(p1_pos), "n_neg": len(p1_neg)})
    return rows


def verdict_flip_share(scored: list[dict], ws: list[float]) -> float:
    """Share of generations whose PASS/FAIL is not constant across the `w` range.

    This is what "the verdict is sensitive to `w`" means operationally. τ is set
    to the median hybrid at w = 0.5 so that roughly half pass -- the setting
    under which a flip is most possible. τ is NOT selected here; decision 19's
    argmax does that, on generations this file does not have.
    """
    mid = sorted(0.5 * r["neural"] + 0.5 * r["symbolic"] for r in scored)
    tau = statistics.median(mid) if mid else 0.5
    flipped = 0
    for r in scored:
        verdicts = {(w * r["neural"] + (1.0 - w) * r["symbolic"]) >= tau for w in ws}
        if len(verdicts) > 1:
            flipped += 1
    return flipped / len(scored) if scored else float("nan")


def marginal_value(scored: list[dict], ws: list[float], n_folds: int) -> dict:
    """Held-out test: does a mixture beat neural-only on plots it never saw?

    Grouped by `plot_id` -- both levels of a plot share a synopsis and ten
    exemplars, so splitting them would leak the plot into its own test fold.
    Per fold: pick the best `w` on the training plots, then compare that `w`
    against **w = 1.0** (neural only) on the held-out plots. Reporting the count
    of folds won is deliberate: `barata2026hybrid` rejected a cheap component in
    50 of 50 folds, and a fold count is what makes that kind of verdict legible.
    """
    plots = sorted({r["plot_id"] for r in scored})
    folds = [plots[i::n_folds] for i in range(n_folds)]
    wins, ties, losses, chosen, deltas = 0, 0, 0, [], []
    for held in folds:
        tr = [r for r in scored if r["plot_id"] not in held]
        te = [r for r in scored if r["plot_id"] in held]
        if not tr or not te:
            continue
        tr_curve = curve(tr, ws)
        best = max(tr_curve, key=lambda c: (c["auc"], c["w"]))["w"]
        te_best = curve(te, [best])[0]["auc"]
        te_neural = curve(te, [1.0])[0]["auc"]
        chosen.append(best)
        d = te_best - te_neural
        deltas.append(d)
        if d > 1e-12:
            wins += 1
        elif d < -1e-12:
            losses += 1
        else:
            ties += 1
    return {
        "n_folds": len(deltas),
        "w_chosen_per_fold": chosen,
        "delta_auc_per_fold": deltas,
        "mean_delta_auc": statistics.mean(deltas) if deltas else float("nan"),
        "folds_mixture_beats_neural_only": wins,
        "folds_tied": ties,
        "folds_neural_only_better": losses,
    }


def classify(flip_share: float, mv: dict, tol: float = 1e-6) -> str:
    """Map measurements to the registered outcomes or expose a coverage gap."""
    if mv["folds_neural_only_better"] > mv["folds_mixture_beats_neural_only"]:
        return "SYMBOLIC_HARMS"
    if flip_share <= tol and mv["folds_mixture_beats_neural_only"] == 0:
        return "SYMBOLIC_INERT"
    if mv["folds_mixture_beats_neural_only"] > mv["folds_neural_only_better"]:
        return "SYMBOLIC_EARNS_ITS_PLACE"
    return "PRECOMMITMENT_UNRESOLVED"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="configs/s4_w.yaml")
    args = ap.parse_args()

    set_seed()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    loaded_inputs = validate_inputs(cfg)
    g = cfg["grid"]
    step = float(g["w_step"])
    ws = [g["w_min"] + i * step
          for i in range(int(round((g["w_max"] - g["w_min"]) / step)) + 1)]

    critic = Critic(verifier_a_path=cfg["artifacts"]["verifier_a"],
                    symbolic_path=cfg["artifacts"]["symbolic"],
                    required_sklearn_version=cfg["runtime"]["scikit_learn"])

    per_condition, all_scores = {}, []
    for src in cfg["inputs"]:
        name = src["name"]
        rows = loaded_inputs[name]
        print(f"  {name}: scoring {len(rows)} generations ...", flush=True)
        scored = score_all(critic, rows)
        for r in scored:
            r["condition"] = name
        all_scores += scored

        block = {"n": len(scored), "curve": curve(scored, ws),
                 "verdict_flip_share": verdict_flip_share(scored, ws),
                 "marginal_value": marginal_value(
                     scored, ws, int(cfg["marginal_value"]["n_folds"]))}
        block["length_only_auc"] = {
            arm: auc([r["n_words"] for r in scored
                      if r["arm"] == arm and r["target_level"] == 1],
                     [r["n_words"] for r in scored
                      if r["arm"] == arm and r["target_level"] == 0])
            for arm in sorted({r["arm"] for r in scored})
        }
        block["outcome"] = classify(block["verdict_flip_share"],
                                   block["marginal_value"])
        per_condition[name] = block

    score_fields = ["condition", "key", "plot_id", "arm", "target_level",
                    "n_words", "neural", "symbolic"]
    write_csv_result(all_scores, cfg["outputs"]["scores_csv"], score_fields,
                     config_path=args.config)

    curve_rows = []
    for name, block in per_condition.items():
        for point in block["curve"]:
            curve_rows.append({"condition": name, **point})
    write_csv_result(
        curve_rows,
        cfg["outputs"]["curve_csv"],
        ["condition", "w", "auc", "n_pos", "n_neg"],
        config_path=args.config,
    )

    result = {
        "NOT_A_RESULT": False,
        "what_this_is": "`w` reported as a sensitivity curve (protocol.md §S4 "
                        "decision 1). No single w is selected; the curve is the "
                        "deliverable.",
        "label_limit": "The label is the REQUESTED level, so this measures "
                       "agreement with the instruction, not whether the text is "
                       "really at that level. No axis-control claim is made here.",
        "w_grid": [round(w, 4) for w in ws],
        "per_condition": per_condition,
    }
    write_result(result, cfg["outputs"]["report_json"], config_path=args.config)

    lines = [
        "# S4.5a — `w` as a sensitivity curve",
        "",
        "> `w` is **not** given a value here. `protocol.md` §S4 decision 1 "
        "registers it as a curve, and the curve is the deliverable. The three "
        "outcomes below were pre-committed on 2026-08-11, before any generation "
        "existed.",
        "",
        "> ⚠️ **The label is the level that was REQUESTED.** These numbers "
        "measure agreement with the instruction, not whether the text really "
        "sits at that level — the generator's compliance is assumed and cannot "
        "be checked without annotation. **No axis-control claim is made from "
        "this file.**",
        "",
        "> ⚠️ **The baseline is not 0.5.** A word count alone recovers the "
        "requested level at AUC 0.91–0.99 (S4.dev-LC), so the reference for any "
        "hybrid score is the length-only probe, printed in every table below.",
        "",
    ]
    for name, b in per_condition.items():
        c0 = next(c for c in b["curve"] if abs(c["w"]) < 1e-9)
        c1 = next(c for c in b["curve"] if abs(c["w"] - 1.0) < 1e-9)
        best = max(b["curve"], key=lambda c: (c["auc"], c["w"]))
        mv = b["marginal_value"]
        lines += [
            f"## {name} (n = {b['n']})",
            "",
            "| point | `w` | AUC vs requested level |",
            "|---|---|---|",
            f"| symbolic only | 0.00 | {c0['auc']:.4f} |",
            f"| best on the grid | {best['w']:.2f} | {best['auc']:.4f} |",
            f"| neural only | 1.00 | {c1['auc']:.4f} |",
            "",
            "| length-only probe (the real baseline) | AUC |",
            "|---|---|",
        ]
        for arm, a in b["length_only_auc"].items():
            lines.append(f"| {arm} | {a:.4f} |")
        lines += [
            "",
            f"**Verdict sensitivity to `w`:** {b['verdict_flip_share']:.1%} of "
            "generations change PASS/FAIL somewhere across the range (τ at the "
            "median hybrid; τ itself is decision 19's argmax and is not selected "
            "here).",
            "",
            f"**Held-out marginal value** ({mv['n_folds']} folds, grouped by "
            f"plot): mixture beats neural-only in **{mv['folds_mixture_beats_neural_only']}** "
            f"folds, ties in {mv['folds_tied']}, loses in "
            f"{mv['folds_neural_only_better']}. Mean ΔAUC "
            f"**{mv['mean_delta_auc']:+.4f}**. `w` chosen per fold: "
            f"{[round(x, 2) for x in mv['w_chosen_per_fold']]}.",
            "",
            f"### Outcome: `{b['outcome']}`",
            "",
        ]
        if b["outcome"] == "SYMBOLIC_INERT":
            lines += [
                "Registered consequence: **the symbolic term is RETAINED "
                "anyway** — the Reflector requires a component that can name "
                "which rule failed, and the LaBSE probe cannot. Retained for "
                "interpretability, not for accuracy, and reported as a negative "
                "result rather than softened.",
                "",
            ]
        elif b["outcome"] == "PRECOMMITMENT_UNRESOLVED":
            lines += [
                "**Audit finding:** this is not a fourth scientific outcome. "
                "The curve is not flat, so `SYMBOLIC_INERT` does not apply; "
                "the held-out test also does not favour the symbolic term, so "
                "`SYMBOLIC_EARNS_ITS_PLACE` does not apply; and neural-only "
                "never beats the selected mixture, so `SYMBOLIC_HARMS` does "
                "not apply. The registered rule therefore does not resolve "
                "this observed combination.",
                "",
                "**Consequence:** no hybrid-accuracy claim and no single `w` "
                "is selected. The symbolic component remains available for "
                "failed-rule naming, its separately registered interpretability "
                "role; this result does not establish predictive value.",
                "",
            ]
    write_text_lf(cfg["outputs"]["report_md"], "\n".join(lines) + "\n")
    print(f"\nwrote {cfg['outputs']['report_md']}")
    for name, b in per_condition.items():
        best = max(b["curve"], key=lambda c: (c["auc"], c["w"]))
        print(f"  {name:18s} outcome={b['outcome']:26s} "
              f"best w={best['w']:.2f} auc={best['auc']:.4f} "
              f"flip={b['verdict_flip_share']:.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
