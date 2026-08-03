"""S2f — the residual test: how much of the K=2 cut is valence and verbosity?

    python -m src.cluster.s2f_residual --config configs/s2f_residual.yaml

S2e returned `LENGTH_CONFOUNDED` (length_auc 0.6764) and, in the same report, a
cluster × Sentiment table whose φ is **0.3981** while its ARI is **0.1522**. Two
cheap variables are each doing real work. The question left open is whether,
**together**, they do all of it — because if they do, G-300 would be paying
three annotators to rediscover two columns already in the CSV.

**This test is voluntary.** RQ1 Band 2 requires a residual test at ARI ≥ 0.20
and we are below it. It runs because ARI is the wrong instrument for this
association and this project has already been misled by it once
(`s2b_register_probe.md`: φ 0.565 against V 0.410). Interpretation is
pre-registered in `docs/protocol.md`, RQ1-E, written before this file existed.

**Test C's estimate is deliberately optimistic.** Cell-majority accuracy is
fitted and scored on the same rows — a resubstitution estimate, and therefore an
**upper bound** on what sentiment and length explain. Every place that number is
printed, that sentence is printed with it. An upper bound is the honest
direction to err in here: it makes the "these two explain everything" verdict
*easier* to reach, so a low lift is strong evidence rather than a lucky split.

**Nothing is trained**, and no embedding is needed — this runs off
`s2e_regionA_k2_assignments.csv` and the cleaned text on any laptop. AUC and φ
are rank/contingency statistics; richness is sampling at a fixed token budget.
Rules 7 and 10 untouched: whitespace tokens only, no stemming, no stopword
removal, no TF-IDF.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.cluster.s2e_profile import directionless_auc  # noqa: E402
from src.common.provenance import NEWLINE, stamp, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402
from src.preprocess.s2b_register_probe import bootstrap_types  # noqa: E402

EXPLAINED = "EXPLAINED_BY_SENTIMENT_AND_LENGTH"
PARTIAL = "PARTIALLY_EXPLAINED"
RESIDUAL = "RESIDUAL_SURVIVES"


def phi(a: int, b: int, c: int, d: int) -> float:
    """φ for a 2×2 table. Returns nan when a margin is empty.

    Reported as |φ| downstream: the sign says which cluster leans positive,
    which is an artefact of K-Means labelling, not a property of the data.
    """
    den = float((a + b) * (c + d) * (a + c) * (b + d))
    if den <= 0:
        return float("nan")
    return float((a * d - b * c) / np.sqrt(den))


def cell_majority_accuracy(cells: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Predict `y` by each cell's own majority. Returns (accuracy, baseline).

    ⚠️ Resubstitution: the majorities are read from the same rows they are
    scored on, so this OVERSTATES how much the cell variables explain. That is
    the useful direction of error — it makes "the cheap variables explain the
    cut" easier to conclude, so failing to reach the threshold is strong
    evidence that something else is doing the work.
    """
    correct = 0
    for c in np.unique(cells):
        m = cells == c
        vals, counts = np.unique(y[m], return_counts=True)
        correct += int(counts.max())
    baseline = float(np.bincount(y).max() / len(y))
    return float(correct / len(y)), baseline


def verdict_c(lift_pp: float, cfg) -> str:
    t = cfg["test_c"]
    if lift_pp >= t["explained_at_or_above"]:
        return EXPLAINED
    if lift_pp >= t["partial_at_or_above"]:
        return PARTIAL
    return RESIDUAL


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s2f_residual.yaml")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    cfg_path = Path(args.config)
    cfg = yaml.safe_load((root / cfg_path).read_text(encoding="utf-8"))
    rng = np.random.default_rng(int(cfg["seed"]))

    a = pd.read_csv(root / cfg["input_assignments"])
    if len(a) != cfg["expected_n"]:
        raise AssertionError(
            f"{cfg['input_assignments']} has {len(a)} rows, expected "
            f"{cfg['expected_n']}. This must be S2e's own output."
        )
    txt = pd.read_csv(root / cfg["input_csv"])[[cfg["id_col"], cfg["text_col"]]]
    df = a.merge(txt, on=cfg["id_col"], how="left")
    assert df[cfg["text_col"]].notna().all(), "a review_id in S2e has no text"

    clu = df[cfg["cluster_col"]].to_numpy()
    sen = df[cfg["label_col"]].to_numpy()
    wds = df[cfg["length_col"]].to_numpy(dtype=float)
    text = df[cfg["text_col"]].astype(str)
    n = len(df)

    # Quartile edges are DERIVED. Choosing cut points by hand after seeing the
    # table is how a residual test gets tuned into agreement.
    band = pd.qcut(wds, int(cfg["length_bands"]["n_quantiles"]), duplicates="drop")
    band_names = [str(b) for b in band.categories]
    bidx = band.codes

    # --- Test A: length within a sentiment class ---------------------------
    a_rows = []
    for s in sorted(set(sen)):
        m = sen == s
        a_rows.append({
            "Sentiment": int(s), "n": int(m.sum()),
            "auc_length_vs_cluster": directionless_auc(wds[m], clu[m] == 1),
            "mean_words_cluster0": float(wds[m & (clu == 0)].mean()),
            "mean_words_cluster1": float(wds[m & (clu == 1)].mean()),
        })
    a_tab = pd.DataFrame(a_rows)
    a_min = float(a_tab["auc_length_vs_cluster"].min())
    a_pass = a_min >= float(cfg["test_a"]["independent_at_or_above"])

    # --- Test B: sentiment within a length band ----------------------------
    b_rows = []
    for i, name in enumerate(band_names):
        m = bidx == i
        t = pd.crosstab(clu[m], sen[m])
        t = t.reindex(index=[0, 1], columns=sorted(set(sen)), fill_value=0)
        p = phi(int(t.iloc[0, 0]), int(t.iloc[0, 1]),
                int(t.iloc[1, 0]), int(t.iloc[1, 1]))
        b_rows.append({
            "length_band": name, "n": int(m.sum()),
            "abs_phi_cluster_vs_sentiment": abs(p),
            "cluster1_share_%": 100 * float((clu[m] == 1).mean()),
        })
    b_tab = pd.DataFrame(b_rows)
    b_min = float(b_tab["abs_phi_cluster_vs_sentiment"].min())
    b_pass = b_min >= float(cfg["test_b"]["independent_at_or_above"])
    b_worst = b_tab.loc[b_tab["abs_phi_cluster_vs_sentiment"].idxmin(), "length_band"]

    # --- Test C: the decisive one ------------------------------------------
    cells = np.array([f"S{s}|{band_names[i]}" for s, i in zip(sen, bidx)])
    acc, base = cell_majority_accuracy(cells, clu)
    lift = 100 * (acc - base)
    vc = verdict_c(lift, cfg)

    # Decomposition. "Sentiment and length together" is not a useful summary if
    # one of them is doing all the work, and the joint number cannot tell you
    # which. Same estimator, three cell definitions.
    acc_s, _ = cell_majority_accuracy(np.array([f"S{s}" for s in sen]), clu)
    acc_l, _ = cell_majority_accuracy(
        np.array([band_names[i] for i in bidx]), clu)
    decomp = pd.DataFrame([
        {"conditioning_on": "nothing (marginal baseline)", "accuracy_%": 100 * base,
         "lift_pp": 0.0},
        {"conditioning_on": "Sentiment only", "accuracy_%": 100 * acc_s,
         "lift_pp": 100 * (acc_s - base)},
        {"conditioning_on": "length band only", "accuracy_%": 100 * acc_l,
         "lift_pp": 100 * (acc_l - base)},
        {"conditioning_on": "both (the 8 cells)", "accuracy_%": 100 * acc,
         "lift_pp": lift},
    ])

    c_rows = []
    for c in sorted(set(cells)):
        m = cells == c
        c_rows.append({
            "cell": c, "n": int(m.sum()),
            "cluster1_share_%": 100 * float((clu[m] == 1).mean()),
            "cell_majority": int(np.bincount(clu[m]).argmax()),
        })
    c_tab = pd.DataFrame(c_rows)
    c_tab["deviation_from_marginal_pp"] = (
        c_tab["cluster1_share_%"] - 100 * float((clu == 1).mean())).abs()
    c_tab.to_csv(root / cfg["outputs"]["cells_csv"], index=False,
                 encoding="utf-8", lineterminator=NEWLINE)

    # --- Test D: richness inversion under a length control ------------------
    tok = {}
    for i, name in enumerate(band_names):
        for c in (0, 1):
            m = (bidx == i) & (clu == c)
            tok[(name, c)] = [w for t in text[m] for w in t.split()]
    smallest = min(len(v) for v in tok.values())
    budget = max(int(cfg["test_d"]["min_budget"]), int(smallest // 50) * 50)
    reps = int(cfg["test_d"]["bootstrap"])

    d_rows = []
    for name in band_names:
        row = {"length_band": name, "budget": budget}
        for c in (0, 1):
            toks = tok[(name, c)]
            m_, s_ = ((float("nan"), float("nan")) if len(toks) < budget
                      else bootstrap_types(toks, budget, reps, rng))
            row[f"n_reviews_c{c}"] = int(((bidx == band_names.index(name))
                                          & (clu == c)).sum())
            row[f"types_c{c}"] = m_
            row[f"sd_c{c}"] = s_
        row["inversion_holds"] = bool(row["types_c1"] > row["types_c0"]) \
            if np.isfinite(row["types_c1"]) and np.isfinite(row["types_c0"]) else None
        d_rows.append(row)
    d_tab = pd.DataFrame(d_rows)
    held = [r["inversion_holds"] for r in d_rows]
    d_state = ("ALL" if all(h is True for h in held)
               else "NONE" if all(h is False for h in held)
               else "MIXED")

    report = build_report(cfg, cfg_path, stamp(cfg_path.as_posix()), n,
                          a_tab, a_min, a_pass, b_tab, b_min, b_pass, b_worst,
                          c_tab, acc, base, lift, vc, d_tab, d_state, budget,
                          float((clu == 1).mean()), decomp)
    out = write_text_lf(root / cfg["outputs"]["report_md"], report)

    print(a_tab.to_string(index=False)); print()
    print(b_tab.to_string(index=False)); print()
    print(c_tab.to_string(index=False)); print()
    print(d_tab.to_string(index=False)); print()
    print(decomp.to_string(index=False)); print()
    print(f"A: min AUC(length|sentiment) = {a_min:.4f}  -> "
          f"{'independent' if a_pass else 'ENTANGLED'}")
    print(f"B: min |phi|(sentiment|band) = {b_min:.4f}  -> "
          f"{'independent' if b_pass else 'NOT in ' + str(b_worst)}")
    print(f"C: cell-majority accuracy {100*acc:.1f}% vs baseline {100*base:.1f}% "
          f"= +{lift:.1f} pp  ->  {vc}")
    print("   (resubstitution: an UPPER BOUND on what the two variables explain)")
    print(f"D: richness inversion holds in {d_state} bands (budget {budget})")
    print(f"\nwrote {out}")
    print("Read docs/protocol.md RQ1-E before interpreting this.")
    return 0


def build_report(cfg, cfg_path, prov, n, a_tab, a_min, a_pass, b_tab, b_min,
                 b_pass, b_worst, c_tab, acc, base, lift, vc, d_tab, d_state,
                 budget, share1, decomp) -> str:
    def md(t, f=".4f"):
        return t.to_markdown(index=False, floatfmt=f)

    near = abs(lift - float(cfg["test_c"]["partial_at_or_above"]))
    boundary = ""
    if near <= 2.0:
        other = (PARTIAL if lift < cfg["test_c"]["partial_at_or_above"]
                 else RESIDUAL)
        boundary = f"""
> ### ⚠️ This verdict sits **{near:.1f} pp** from its threshold
>
> The lift is **{lift:.1f} pp** against a cutoff of
> **{cfg['test_c']['partial_at_or_above']}**. A different quartile binning, a
> different corpus draw, or a handful of reviews moving cells could return
> **{other}** instead. The threshold was fixed in advance and is applied as
> written — but a verdict this close to its own boundary is **weak evidence, and
> is to be reported as weak** wherever it appears. It is not rounded, softened,
> or restated as a comfortable margin.
"""

    band_c = {
        EXPLAINED: f"""**{EXPLAINED}** — lift **+{lift:.1f} pp**
≥ {cfg['test_c']['explained_at_or_above']}.

Sentiment and length **largely account for the partition**. The cut is a valence
× verbosity grid, and under RQ1-E **the persona claim is unsupported**: G-300
would be paying three annotators to rediscover two columns already present in
the CSV. RQ1 is reported as a negative result on *data-derived* personas —
publishable, and already anticipated by RQ1-C.""",
        PARTIAL: f"""**{PARTIAL}** — lift **+{lift:.1f} pp**, between
{cfg['test_c']['partial_at_or_above']} and {cfg['test_c']['explained_at_or_above']}.

Substantial but partial. Under RQ1-E, G-300 proceeds — and **both** variables
are reported as controls beside every persona claim, with the residual stated
explicitly as the part being annotated.""",
        RESIDUAL: f"""**{RESIDUAL}** — lift **+{lift:.1f} pp** <
{cfg['test_c']['partial_at_or_above']}.

Most of the partition is explained by **neither** variable. Whatever LaBSE is
cutting on, it is not valence and not verbosity — and under RQ1-E that makes
G-300 the right place to spend, because no cheaper instrument has explained the
cut.

**This does not show the halves are personas.** It shows the two cheapest
explanations have been eliminated: a stronger position than S2e left us in, and
a weaker one than a persona claim requires.""",
    }[vc]

    d_band = {
        "ALL": """The inversion **holds in every length band**. It survives its
most obvious control, so the halves differ in **kind** and not only in **size**.
Under RQ1-E this is the strongest pre-G-300 evidence for the persona reading —
still not proof, and still subordinate to G-300.""",
        "MIXED": """The inversion **holds in some bands and not others**. Under
RQ1-E it is reported band by band and **never aggregated into one sentence**.""",
        "NONE": """The inversion **does not survive the length control**. It was
a length artefact. Under RQ1-E it is **withdrawn**, and the withdrawal is stated
wherever the claim was made — including in `s2e_regionA_k2_profile.md`, which
reported the raw inversion without this control.""",
    }[d_state]

    return f"""# S2f — The residual test: is the K = 2 cut just valence and verbosity?

> **Interpretation was pre-registered in `docs/protocol.md` (RQ1-E) before this
> script existed.** Read that section first.
>
> ### Why this ran when the pre-registration did not require it
>
> RQ1 Band 2 makes a residual test mandatory at ARI ≥ 0.20. S2e reports
> **0.1522** — Band 1 — so nothing was owed. It ran anyway because ARI is the
> wrong instrument for this association, and this project has been misled by it
> once already (`s2b_register_probe.md`: φ 0.565 against V 0.410). The same 2×2
> that gives ARI 0.1522 gives **φ = 0.3981** and a 19.3-point accuracy lift.
>
> **This does not move the corpus into Band 2 and revises no band assignment.**
> It is voluntary and additional, and it is labelled that way everywhere.

- **Config:** `{cfg_path}` · **n:** {n} (region A, post-dedup, K = 2)
- **Generated (UTC):** {prov['timestamp_utc']} · **Commit:** `{prov['git_commit']}`
- **Seed:** {cfg['seed']} · Marginal cluster-1 share: **{100*share1:.1f}%**
- **No embedding required.** This runs off S2e's assignments and the cleaned
  text. **Nothing is trained** — AUC and φ are rank/contingency statistics and
  richness is sampling at a fixed budget. Rules 7 and 10 intact.

## Verdict — Test C, the decisive one

{band_c}
{boundary}
### Which variable is actually doing the work?

"Sentiment and length together" is not a useful summary when one of them may be
doing all the work, and the joint number cannot tell you which. Same estimator,
three cell definitions:

{md(decomp, ".1f")}

**Read the gap between the last two rows.** That is what length adds *once
sentiment is already known* — and it is the honest measure of the length
confound at the level of prediction, as opposed to the level of correlation that
S2e's `length_auc` reports.

### The number, with the caveat that must always travel with it

Cell-majority accuracy **{100*acc:.1f}%** against a marginal baseline of
**{100*base:.1f}%** → lift **+{lift:.1f} pp**.

⚠️ **This is a resubstitution estimate.** Each cell's majority is read from the
same rows it is scored on, so it **overstates** how much sentiment and length
explain. That is the useful direction of error: it makes the "cheap variables
explain everything" verdict *easier* to reach, so a **low** lift is strong
evidence, while a high one is a ceiling rather than a measurement.

### The eight cells

{md(c_tab, ".1f")}

A cell share near the marginal {100*share1:.1f}% means that knowing a review's
sentiment and length tells you nothing about which half it landed in. Shares
near 0 or 100 mean the opposite.

## Test A — does length separate the halves *within* a sentiment class?

Directionless AUC of `n_words` against cluster, computed separately per
sentiment class. Reported figure is the **minimum**: length is only
"independent" if it works in *both* classes.

{md(a_tab)}

**min = {a_min:.4f}** → {'**independent of sentiment**' if a_pass else '**ENTANGLED** — in at least one class, length does not separate the halves, so the length effect is partly carried by sentiment and must be reported as entangled rather than additive'}
(threshold {cfg['test_a']['independent_at_or_above']}).

## Test B — does sentiment separate the halves *within* a length band?

|φ| inside each quartile band of `n_words`. Bands are quartile-derived, not
hand-chosen; edges appear in the table. Reported figure is the **minimum**
across bands.

{md(b_tab)}

**min = {b_min:.4f}** in band `{b_worst}` → {'**independent of length**, in every band' if b_pass else f'**not independent**: in `{b_worst}` sentiment does not separate the halves. Named rather than averaged away'}
(threshold {cfg['test_b']['independent_at_or_above']}).

## Test D — does the lexical-richness inversion survive a length control?

S2e found cluster 1 **{100*(1-8.85/13.12):.0f}% shorter yet drawing ~18% more word
types** at an equal token budget. Pure length predicts the opposite, which makes
this the strongest available evidence that the halves differ in kind — and also
the claim most likely to be a length artefact. So it is recomputed **inside each
length band**, at a common budget of **{budget:,} tokens** derived from the
smallest band × cluster cell, so that no cell is compared at a size it cannot
supply.

{md(d_tab)}

{d_band}

## What this step does NOT settle

1. **That the halves are personas.** Eliminating valence and verbosity is not
   the same as establishing an audience distinction. Only G-300 can do that.
2. **That no other cheap variable explains the cut.** Two were tested because
   two were implicated by S2e. A third may exist and would be worth testing if
   named.
3. **Anything with more confidence than a resubstitution bound allows.** Test C
   is a ceiling, not a measurement, and every use of it says so.
"""


if __name__ == "__main__":
    raise SystemExit(main())
