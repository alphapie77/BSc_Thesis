"""Score the RQ1-H intrusion task — Gate A and Gate B.

    python -m src.annotate.intrusion_score --config configs/intrusion.yaml

Both gates and every band are pre-registered in `docs/protocol.md`, RQ1-H,
written before a single item was answered — including the note recorded *during*
annotation that both annotators found the items hard to tell apart, and the
pre-commitment for how a failure would be reported.

**Gate A** — accuracy at picking the intruder, against a chance rate of 0.25.
**Gate B** — accuracy at picking the cluster-1 review as "more specific", against
0.50. Interpreted **only** if Gate A passes.

Significance is an **exact one-sided binomial tail**, computed here rather than
taken from scipy so the test has no hidden dependency and can be checked by hand.

**Nothing is trained.** These are counts.
"""
from __future__ import annotations

import argparse
import sys
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import NEWLINE, stamp, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402

PERCEPTIBLE = "HUMANLY_PERCEPTIBLE"
WEAK = "WEAKLY_PERCEPTIBLE"
NOT_PERCEPTIBLE = "NOT_PERCEPTIBLE"


def binom_tail(k: int, n: int, p0: float) -> float:
    """P(X >= k) under Binomial(n, p0). Exact, one-sided.

    Written out rather than imported so the number in the thesis can be checked
    with a calculator, and so the result does not depend on a library version.
    """
    return float(sum(comb(n, i) * p0**i * (1 - p0)**(n - i) for i in range(k, n + 1)))


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z**2 / n
    c = p + z**2 / (2 * n)
    h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return float((c - h) / d), float((c + h) / d)


def gate_a_band(acc: float, p: float, cfg) -> str:
    ic = cfg["intrusion"]
    if p >= ic["alpha"]:
        return NOT_PERCEPTIBLE
    return PERCEPTIBLE if acc >= ic["strong_at_or_above"] else WEAK


def score_block(sheets: dict, key: pd.DataFrame, id_col: str, ans_col: str,
                correct_col: str, chance: float, cfg) -> dict:
    """Per-annotator and pooled accuracy, with exact binomial tails."""
    out = {"per_annotator": {}, "n_items": len(key)}
    correct_map = dict(zip(key[id_col], key[correct_col]))
    hits_all, n_all = 0, 0
    picks = {}
    for who, df in sheets.items():
        m = df.dropna(subset=[ans_col])
        got = m[ans_col].astype(str).str.strip().str.upper()
        picks[who] = dict(zip(m[id_col], got))
        ok = int(sum(correct_map.get(i) == g for i, g in zip(m[id_col], got)))
        n = len(m)
        lo, hi = wilson(ok, n)
        out["per_annotator"][who] = {
            "n": n, "correct": ok, "accuracy": ok / n if n else float("nan"),
            "p_exact": binom_tail(ok, n, chance), "ci_lo": lo, "ci_hi": hi,
        }
        hits_all += ok
        n_all += n
    out["pooled"] = {
        "n": n_all, "correct": hits_all,
        "accuracy": hits_all / n_all if n_all else float("nan"),
        "p_exact": binom_tail(hits_all, n_all, chance),
    }
    ids = list(key[id_col])
    both = [i for i in ids if all(i in picks[w] for w in picks)]
    ws = list(picks)
    out["annotator_agreement"] = (
        float(np.mean([picks[ws[0]][i] == picks[ws[1]][i] for i in both]))
        if len(ws) == 2 and both else float("nan"))
    out["chance"] = chance
    return out


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/intrusion.yaml")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    cfg_path = Path(args.config)
    cfg = yaml.safe_load((root / cfg_path).read_text(encoding="utf-8"))
    d = root / cfg["outputs"]["sheet_dir"]
    who = list(cfg["annotators"])

    ikey = pd.read_csv(root / cfg["outputs"]["key_csv"])
    pkey = pd.read_csv(str(root / cfg["outputs"]["key_csv"])
                       .replace(".csv", "_pairwise.csv"))
    isheets = {w: pd.read_csv(d / f"intrusion_{w}.csv", dtype=str) for w in who}
    psheets = {w: pd.read_csv(d / f"pairwise_{w}.csv", dtype=str) for w in who}

    A = score_block(isheets, ikey, "set_id", "answer", "correct_option",
                    float(cfg["intrusion"]["chance"]), cfg)
    band = gate_a_band(A["pooled"]["accuracy"], A["pooled"]["p_exact"], cfg)

    print(f"GATE A — intrusion (chance {A['chance']:.2f}, n={A['n_items']} sets)")
    for w, r in A["per_annotator"].items():
        print(f"  {w}: {r['correct']}/{r['n']} = {r['accuracy']:.3f}  "
              f"p={r['p_exact']:.4f}  95% CI [{r['ci_lo']:.3f}, {r['ci_hi']:.3f}]")
    print(f"  pooled: {A['pooled']['correct']}/{A['pooled']['n']} = "
          f"{A['pooled']['accuracy']:.3f}  p={A['pooled']['p_exact']:.4f}")
    print(f"  the two annotators picked the same option "
          f"{100*A['annotator_agreement']:.1f}% of the time")
    print(f"  -> {band}\n")

    B = score_block(psheets, pkey, "pair_id", "answer", "cluster1_option",
                    float(cfg["pairwise"]["chance"]), cfg)
    print(f"GATE B — pairwise (chance {B['chance']:.2f}, n={B['n_items']} pairs)"
          + ("" if band != NOT_PERCEPTIBLE else "   [NOT INTERPRETED — Gate A failed]"))
    for w, r in B["per_annotator"].items():
        print(f"  {w}: {r['correct']}/{r['n']} = {r['accuracy']:.3f}  "
              f"p={r['p_exact']:.4f}")
    print(f"  pooled: {B['pooled']['correct']}/{B['pooled']['n']} = "
          f"{B['pooled']['accuracy']:.3f}  p={B['pooled']['p_exact']:.4f}")
    print(f"  the two annotators picked the same option "
          f"{100*B['annotator_agreement']:.1f}% of the time")

    rows = []
    for blk, name, k in ((A, "intrusion", "set_id"), (B, "pairwise", "pair_id")):
        for w, r in blk["per_annotator"].items():
            rows.append({"block": name, "annotator": w, **r})
        rows.append({"block": name, "annotator": "POOLED", **blk["pooled"]})
    pd.DataFrame(rows).to_csv(root / cfg["outputs"]["responses_csv"], index=False,
                              encoding="utf-8", lineterminator=NEWLINE)

    out = write_text_lf(root / cfg["outputs"]["report_md"],
                        build_report(cfg, cfg_path, stamp(cfg_path.as_posix()),
                                     A, B, band, ikey))
    print(f"\nwrote {out}")
    print("Read docs/protocol.md RQ1-H before interpreting this.")
    return 0


def build_report(cfg, cfg_path, prov, A, B, band, ikey) -> str:
    ic = cfg["intrusion"]
    pa = A["pooled"]

    verdict = {
        PERCEPTIBLE: f"""**{PERCEPTIBLE}.** Pooled accuracy **{pa['accuracy']:.3f}**
against a chance rate of {A['chance']:.2f}, exact one-sided binomial
**p = {pa['p_exact']:.4g}**, and at or above the pre-registered
{ic['strong_at_or_above']} threshold.

The K = 2 partition corresponds to a distinction people can see **without being
told what it is** — and, because every set was length-matched to within
{ic['max_word_span']} words, **without length as a cue**. This is stronger than
RQ1 required.""",
        WEAK: f"""**{WEAK}.** Pooled accuracy **{pa['accuracy']:.3f}** beats
chance ({A['chance']:.2f}, p = {pa['p_exact']:.4g}) but sits below the
pre-registered {ic['strong_at_or_above']} threshold.

Above chance and slight. Every persona-adjacent claim in the thesis carries this
number and its interval.""",
        NOT_PERCEPTIBLE: f"""**{NOT_PERCEPTIBLE}.** Pooled accuracy
**{pa['accuracy']:.3f}** against a chance rate of {A['chance']:.2f}; exact
one-sided binomial **p = {pa['p_exact']:.4g}**, above the {ic['alpha']} cutoff.

**Under RQ1-H this is a genuine negative, not an inconclusive result.** The
instrument cannot collapse the way the rating scale did, and it names no
construct, so failure here is not a failure of the scale or of our vocabulary.

⚠️ **But the claim is bounded, exactly as pre-committed before these numbers
existed.** In region A `length_auc` is **0.676**, so length is a genuine
*component* of the cut and not only a confound. Matching every set to within
{ic['max_word_span']} words removed that component, so what was tested is the
**residual, non-length** distinction. The finding is therefore:

> *The K = 2 split was not recoverable by human annotators once length was held
> constant.*

It is **not** "humans cannot perceive the K = 2 split", and it must not be
written that way. A length-unmatched re-run would be easier to pass and is
**forbidden** by RQ1-H for that reason; it belongs in Future Work.""",
    }[band]

    def tab(blk, label):
        rows = [{"annotator": w, "correct": r["correct"], "n": r["n"],
                 "accuracy": r["accuracy"], "p_exact": r["p_exact"]}
                for w, r in blk["per_annotator"].items()]
        rows.append({"annotator": "**pooled**", "correct": blk["pooled"]["correct"],
                     "n": blk["pooled"]["n"], "accuracy": blk["pooled"]["accuracy"],
                     "p_exact": blk["pooled"]["p_exact"]})
        return pd.DataFrame(rows).to_markdown(index=False, floatfmt=".4f")

    gate_b = (f"""_Not interpreted — Gate A returned `{NOT_PERCEPTIBLE}`._
Pre-registered in RQ1-H: Gate B asks whether the distinction is *specificity*,
which is only a meaningful question once a distinction has been shown. The
numbers are printed below for completeness and **carry no claim**.

{tab(B, 'pairwise')}"""
              if band == NOT_PERCEPTIBLE else f"""{tab(B, 'pairwise')}

Chance is {B['chance']:.2f}. The two annotators agreed with each other on
**{100*B['annotator_agreement']:.1f}%** of pairs.""")

    return f"""# RQ1-H — Human validation, attempt 2: the intrusion task

> **Both gates were pre-registered in `docs/protocol.md` (RQ1-H) before a single
> item was answered.** So was the note recorded *during* annotation, that both
> annotators independently reported the items looking alike — together with the
> pre-commitment for how a failure would be worded. Read that section first.
>
> **Attempt 1 (step 5k) is not superseded.** It is reported in full: its rating
> scale collapsed, α = 0.4970, and RQ1 was inconclusive. This is a second
> attempt with a different instrument, and it is labelled that way throughout.

- **Config:** `{cfg_path}` · **Generated (UTC):** {prov['timestamp_utc']}
- **Commit:** `{prov['git_commit']}` · **Seed:** {cfg['seed']}
- **{A['n_items']} intrusion sets**, each 4 reviews (3 alike + 1 intruder),
  **length-matched to within {ic['max_word_span']} words**, drawn from region A
  **excluding G-300** — text neither annotator had seen.
- **Nothing is trained.** These are counts, and the significance test is an
  exact binomial tail computed in-repo so it can be checked by hand.

## Gate A — is the split perceptible at all?

{verdict}

{tab(A, 'intrusion')}

The two annotators chose the **same option** on
**{100*A['annotator_agreement']:.1f}%** of sets. That is a separate quantity
from accuracy: it measures whether they were seeing the same thing as each
other, whether or not it was the intruder.

⚠️ **The pooled row is not {A['pooled']['n']} independent trials.** Both
annotators judged the same {A['n_items']} sets, so the pooled p-value is
optimistic. The per-annotator rows are the honest tests; pooled is reported for
completeness.

## Gate B — is the distinction *specificity*?

{gate_b}

## What this settles

- **This is RQ1's arbiter.** S2f eliminated valence and verbosity; nothing
  cheaper than annotators remained.
- **It says nothing about region B**, whose own K = 2 split correlates with no
  measurable feature at all (`s2d_ktable_regionB.md`).
- **It cannot show there is cluster structure.** G1 established there is none
  (silhouette 0.053, HDBSCAN 100% noise). At best this concerns a **cut through
  a continuum** that humans can or cannot see.
"""


if __name__ == "__main__":
    raise SystemExit(main())
