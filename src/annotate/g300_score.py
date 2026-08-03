"""Score the filled G-300 sheets — Gate 1 (agreement) and Gate 2 (validity).

    python -m src.annotate.g300_score --config configs/g300.yaml

Both gates and every band are pre-registered in `docs/protocol.md`, RQ1-F,
written before a single item was annotated.

**Gate 1 — can humans agree at all?** Krippendorff's α, ordinal, over all 300.
Below 0.667 the script **does not compute Gate 2 at all**: a rating nobody
agrees on cannot validate anything, and printing a validity number next to an
unreliable one invites someone to quote the wrong half.

**Gate 2 — does the human rating recover the machine's split?** Directionless
AUC of the mean rating against `cluster_k2`, on the region-A items only, with a
bootstrap CI, and repeated **within each length band** — because RQ1-D's binding
condition (annotators must not succeed on length alone) has to be *measured*.
Instruction is not enforcement.

**Nothing is trained.** α, κ and AUC are all agreement/rank statistics.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.cluster.s2e_profile import directionless_auc  # noqa: E402
from src.common.provenance import NEWLINE, stamp, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402

RELIABLE, TENTATIVE, UNRELIABLE = "RELIABLE", "TENTATIVE", "UNRELIABLE"
WIN, MIXED, NEGATIVE, INCONCLUSIVE = "WIN", "MIXED", "NEGATIVE", "INCONCLUSIVE"


# --------------------------------------------------------------------------
# Krippendorff's alpha
# --------------------------------------------------------------------------
def coincidence(ratings: np.ndarray, categories: list) -> np.ndarray:
    """Coincidence matrix over units. `ratings` is units × raters, nan = missing.

    Units rated by fewer than two raters contribute nothing and are dropped —
    standard, and the reason α tolerates missing data at all.
    """
    idx = {c: i for i, c in enumerate(categories)}
    o = np.zeros((len(categories), len(categories)), dtype=float)
    for row in ratings:
        vals = [v for v in row if not (isinstance(v, float) and np.isnan(v))]
        m = len(vals)
        if m < 2:
            continue
        for i, a in enumerate(vals):
            for j, b in enumerate(vals):
                if i != j:
                    o[idx[a], idx[b]] += 1.0 / (m - 1)
    return o


def krippendorff_alpha(ratings: np.ndarray, categories: list,
                       metric: str = "ordinal") -> float:
    """α = 1 − D_o/D_e.

    The ordinal difference function is Krippendorff's own: the squared distance
    between two categories depends on **how many observations lie between
    them**, not on their numeric labels. That matters here — the gap between
    "verdict only" and "verdict with emphasis" is not the same size as the gap
    between "names an aspect" and "explains it", and a nominal α would score
    every disagreement as total.
    """
    o = coincidence(ratings, categories)
    n_c = o.sum(axis=1)
    n = n_c.sum()
    if n <= 1:
        return float("nan")

    k = len(categories)
    d = np.zeros((k, k), dtype=float)
    for a in range(k):
        for b in range(k):
            if a == b:
                continue
            if metric == "nominal":
                d[a, b] = 1.0
            else:
                lo, hi = min(a, b), max(a, b)
                d[a, b] = (n_c[lo:hi + 1].sum()
                           - (n_c[lo] + n_c[hi]) / 2.0) ** 2

    do = float((o * d).sum())
    de = float((np.outer(n_c, n_c) * d).sum()) / (n - 1)
    if de == 0:
        # Every observation in one category: nothing to disagree about, and no
        # scale on which to express agreement either. nan, not 1.0 — reporting
        # perfect reliability for a degenerate distribution would be false.
        return float("nan")
    return float(1.0 - do / de)


def weighted_kappa(a: np.ndarray, b: np.ndarray, categories: list) -> float:
    """Cohen's κ with linear weights. Two raters only, by definition."""
    k = len(categories)
    idx = {c: i for i, c in enumerate(categories)}
    o = np.zeros((k, k))
    for x, y in zip(a, b):
        o[idx[x], idx[y]] += 1
    n = o.sum()
    if n == 0:
        return float("nan")
    w = np.array([[abs(i - j) / (k - 1) for j in range(k)] for i in range(k)])
    e = np.outer(o.sum(1), o.sum(0)) / n
    den = float((w * e).sum())
    return float(1.0 - (w * o).sum() / den) if den else float("nan")


def bootstrap_auc_ci(score: np.ndarray, pos: np.ndarray, reps: int, ci: float,
                     rng: np.random.Generator) -> tuple[float, float, float]:
    """Percentile bootstrap over items. Returns (point, lo, hi)."""
    point = directionless_auc(score, pos)
    n = len(score)
    out = []
    for _ in range(reps):
        i = rng.integers(0, n, n)
        if pos[i].all() or not pos[i].any():
            continue                      # a resample with one class has no AUC
        out.append(directionless_auc(score[i], pos[i]))
    if not out:
        return point, float("nan"), float("nan")
    a = (1 - ci) / 2
    return point, float(np.quantile(out, a)), float(np.quantile(out, 1 - a))


def gate1_band(alpha: float, cfg) -> str:
    g = cfg["gate1"]
    if not np.isfinite(alpha):
        return UNRELIABLE
    if alpha >= g["reliable_at_or_above"]:
        return RELIABLE
    return TENTATIVE if alpha >= g["tentative_at_or_above"] else UNRELIABLE


def permutation_p(score: np.ndarray, pos: np.ndarray, reps: int,
                  rng: np.random.Generator) -> tuple[float, float]:
    """p-value and the null 95th percentile for a DIRECTIONLESS AUC.

    ⚠️ **A bootstrap CI cannot test chance here, and the first version of this
    file wrongly assumed it could.** `directionless_auc` is `max(a, 1-a)`, so
    every bootstrap resample is bounded below by 0.50 and the lower CI bound
    essentially never reaches it. The `NEGATIVE` verdict was therefore almost
    unreachable — the test was rigged toward finding an effect, which is the
    worst direction for the one number that decides RQ1. Caught by the smoke
    test before any real annotation, and amended in RQ1-F while nothing had
    been observed.

    A permutation null is the right instrument: shuffling cluster membership
    destroys any association while preserving the ceiling and the class
    balance, so the null distribution sits where a directionless statistic
    actually sits under chance — well above 0.50 at small n.

    The bootstrap CI is still reported, for the **precision** of the estimate.
    It just no longer decides anything.
    """
    obs = directionless_auc(score, pos)
    null = np.array([directionless_auc(score, rng.permutation(pos))
                     for _ in range(reps)])
    # +1 in both terms: a permutation p-value can never honestly be 0.
    p = float((np.sum(null >= obs) + 1) / (reps + 1))
    return p, float(np.quantile(null, 0.95))


def gate2_band(point: float, p: float, bands_ok: bool, cfg) -> str:
    g = cfg["gate2"]
    if p >= g["alpha"]:
        return (INCONCLUSIVE if point > g["inconclusive_point_estimate_above"]
                else NEGATIVE)
    if point >= g["auc_threshold"]:
        return WIN if bands_ok else MIXED
    return MIXED


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/g300.yaml")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    cfg_path = Path(args.config)
    cfg = yaml.safe_load((root / cfg_path).read_text(encoding="utf-8"))
    rng = np.random.default_rng(int(cfg["seed"]))
    cats = list(cfg["scale"])
    who = list(cfg["annotators"])

    sheets = {}
    for w in who:
        p = root / cfg["outputs"]["sheet_dir"] / f"g300_sheet_{w}.csv"
        if not p.exists():
            raise SystemExit(
                f"{p} not found. Run `python -m src.annotate.g300_build` first, "
                f"then have annotator {w} fill the `rating` column."
            )
        s = pd.read_csv(p, dtype={"item_id": str})
        s["rating"] = pd.to_numeric(s["rating"], errors="coerce")
        bad = s.loc[s["rating"].notna() & ~s["rating"].isin(cats), "item_id"]
        if len(bad):
            raise SystemExit(
                f"annotator {w} used values outside {cats} on "
                f"{len(bad)} item(s): {list(bad)[:10]}. Fix the sheet; the "
                f"script will not guess what was meant."
            )
        sheets[w] = s.set_index("item_id")["rating"]

    R = pd.DataFrame(sheets)
    filled = R.notna().sum().to_dict()

    # The ratings, and only the ratings, go under version control. The sheets
    # themselves carry 300 rows of the licensed corpus and are gitignored for
    # the same reason `data/cleaned/` is; the sheets are also regenerable from
    # the frozen split and the seed, whereas **the ratings are not regenerable
    # by anything** -- two people spent hours producing them. So they are
    # extracted here as text-free (item_id, annotator, rating) and committed.
    long = R.stack(dropna=True).rename("rating").reset_index()
    long.columns = ["item_id", "annotator", "rating"]
    long["rating"] = long["rating"].astype(int)
    long.sort_values(["item_id", "annotator"]).to_csv(
        root / cfg["outputs"]["ratings_csv"], index=False, encoding="utf-8",
        lineterminator=NEWLINE)
    complete = R.dropna()
    if len(complete) == 0:
        raise SystemExit(
            f"no item has been rated by all of {who} yet "
            f"(filled so far: {filled}). Nothing to score."
        )

    # --- Gate 1 -------------------------------------------------------------
    alpha_o = krippendorff_alpha(R.to_numpy(dtype=float), cats, "ordinal")
    alpha_n = krippendorff_alpha(R.to_numpy(dtype=float), cats, "nominal")
    g1 = gate1_band(alpha_o, cfg)
    kap = (weighted_kappa(complete[who[0]].to_numpy(dtype=int),
                          complete[who[1]].to_numpy(dtype=int), cats)
           if len(who) == 2 else float("nan"))
    diff = (complete[who[0]] - complete[who[1]]).abs() if len(who) == 2 else None
    exact = float((diff == 0).mean()) if diff is not None else float("nan")
    within1 = float((diff <= 1).mean()) if diff is not None else float("nan")

    dist = pd.DataFrame({w: complete[w].value_counts().reindex(cats, fill_value=0)
                         for w in who})
    dist.index.name = "rating"

    print(f"Gate 1 — alpha(ordinal) = {alpha_o:.4f}  [{g1}]   "
          f"alpha(nominal) = {alpha_n:.4f}")
    print(f"         weighted kappa = {kap:.4f}   exact {100*exact:.1f}%   "
          f"within 1 {100*within1:.1f}%   n = {len(complete)}")

    # --- Gate 2 (only if Gate 1 permits) ------------------------------------
    g2 = None
    key = pd.read_csv(root / cfg["outputs"]["key_csv"], dtype={"item_id": str})
    per = key.merge(complete.mean(axis=1).rename("mean_rating"),
                    left_on="item_id", right_index=True, how="left")
    per["rating_" + who[0]] = per["item_id"].map(sheets[who[0]])
    per["rating_" + who[1]] = per["item_id"].map(sheets[who[1]])
    per.to_csv(root / cfg["outputs"]["per_item_csv"], index=False,
               encoding="utf-8", lineterminator=NEWLINE)

    band_tab = auc_tab = None
    if g1 == UNRELIABLE:
        print("\nGate 2 NOT COMPUTED — Gate 1 returned UNRELIABLE. "
              "Pre-registered in RQ1-F: a rating nobody agrees on cannot "
              "validate anything.")
    else:
        v = per.dropna(subset=["cluster_k2", "mean_rating"])
        pos = (v["cluster_k2"] == 1).to_numpy()
        sc = v["mean_rating"].to_numpy(dtype=float)
        point, lo, hi = bootstrap_auc_ci(sc, pos, int(cfg["gate2"]["bootstrap"]),
                                         float(cfg["gate2"]["ci"]), rng)
        pval, null95 = permutation_p(sc, pos, int(cfg["gate2"]["permutations"]),
                                     rng)

        b = pd.qcut(v["n_words"], int(cfg["gate2"]["length_bands"]),
                    duplicates="drop")
        rows = []
        for name in b.cat.categories:
            m = (b == name).to_numpy()
            rows.append({
                "length_band": str(name), "n": int(m.sum()),
                "auc": (directionless_auc(sc[m], pos[m])
                        if 0 < pos[m].sum() < m.sum() else float("nan")),
            })
        band_tab = pd.DataFrame(rows)
        finite = band_tab["auc"].dropna()
        bands_ok = bool(len(finite) and (finite >= 0.60).all())
        g2 = gate2_band(point, pval, bands_ok, cfg)
        auc_tab = (point, lo, hi, pval, null95, bands_ok, len(v))
        print(f"\nGate 2 — AUC {point:.4f}  {100*cfg['gate2']['ci']:.0f}% CI "
              f"[{lo:.4f}, {hi:.4f}]  permutation p = {pval:.4f} "
              f"(null p95 {null95:.4f})  n = {len(v)}  ->  {g2}")
        print(band_tab.to_string(index=False))

    out = write_text_lf(
        root / cfg["outputs"]["report_md"],
        build_report(cfg, cfg_path, stamp(cfg_path.as_posix()), who, filled,
                     len(complete), alpha_o, alpha_n, g1, kap, exact, within1,
                     dist, auc_tab, band_tab, g2))
    print(f"\nwrote {out}")
    print("Read docs/protocol.md RQ1-F before interpreting this.")
    return 0


def build_report(cfg, cfg_path, prov, who, filled, n_complete, alpha_o, alpha_n,
                 g1, kap, exact, within1, dist, auc_tab, band_tab, g2) -> str:
    g1_txt = {
        RELIABLE: f"""**{RELIABLE}** — α = {alpha_o:.4f} ≥
{cfg['gate1']['reliable_at_or_above']}. The construct is reliably annotatable.
Gate 2 proceeds.""",
        TENTATIVE: f"""**{TENTATIVE}** — α = {alpha_o:.4f}, in
[{cfg['gate1']['tentative_at_or_above']},
{cfg['gate1']['reliable_at_or_above']}). Gate 2 proceeds, and **every persona
claim in the thesis carries this α with it**.""",
        UNRELIABLE: f"""**{UNRELIABLE}** — α = {alpha_o:.4f} <
{cfg['gate1']['tentative_at_or_above']}.

**The construct is not reliably annotatable by humans, and Gate 2 was not
computed.** Pre-registered in RQ1-F: a rating nobody agrees on cannot validate
anything. RQ1 is reported as a **negative result** — publishable under RQ1-C —
and the failure is attributed to the construct, not to the annotators.""",
    }[g1]

    if auc_tab is None:
        g2_txt = "_Not computed — see Gate 1._"
        bands_md = ""
    else:
        point, lo, hi, pval, null95, bands_ok, nv = auc_tab
        g2_txt = {
            WIN: f"""**RQ1 WINS.** AUC **{point:.4f}** (CI [{lo:.4f}, {hi:.4f}],
permutation p = **{pval:.4f}**, n = {nv}), threshold
{cfg['gate2']['auc_threshold']}, and it survives **within
every length band**. The K=2 partition corresponds to a distinction humans
perceive and agree on, and is not a length artefact. The halves may be called
personas — **with the qualifications already on record**: there is no cluster
structure in this space (silhouette 0.053, HDBSCAN 100% noise), so this is a
humanly-recognised *cut*, not two discovered groups.""",
            MIXED: f"""**MIXED.** AUC **{point:.4f}** (CI [{lo:.4f}, {hi:.4f}],
permutation p = **{pval:.4f}**, n = {nv}). The association beats chance, but
either the point estimate is below {cfg['gate2']['auc_threshold']}, or it fails
inside at least one length band. Reported band by band below; the persona claim
is disclosed as length-entangled and the failing band is **named, not averaged
away**.""",
            NEGATIVE: f"""**RQ1 IS A NEGATIVE RESULT.** AUC **{point:.4f}**,
permutation p = **{pval:.4f}** — indistinguishable from chance, whose own 95th
percentile at this n sits at **{null95:.4f}** (n = {nv}).

Humans agree with each other but **not with the machine**. The K=2 cut is
reproducible, is not sentiment, is not verbosity — and is **not a distinction
people make**. This is the most informative negative outcome available and is
reported as a finding, exactly as RQ1-C pre-committed.""",
            INCONCLUSIVE: f"""**INCONCLUSIVE AT THIS N.** AUC **{point:.4f}**,
permutation p = **{pval:.4f}** — above the {cfg['gate2']['alpha']} cutoff, so
chance is not excluded. But the point estimate is above
{cfg['gate2']['inconclusive_point_estimate_above']}, chance's own 95th
percentile sits at **{null95:.4f}** at this n, and the CI [{lo:.4f}, {hi:.4f}]
is **{hi - lo:.3f} wide**.

Pre-registered in RQ1-F: this is **not** written up as a refutation. Only 123 of
the frozen G-300 are in region A, and that is a power limit, not a result. The
honest statement is that the study **cannot decide** at this n.""",
        }[g2]
        bands_md = f"""
### Within each length band — RQ1-D's binding condition, measured

The guideline tells annotators that length is not the criterion. Instruction is
not enforcement, so the same AUC is recomputed with length held roughly fixed.
**If it collapses here, the annotators were reading length whatever the rubric
said.**

{band_tab.to_markdown(index=False, floatfmt=".4f")}

All bands ≥ 0.60: **{'yes' if bands_ok else 'NO'}**.
"""

    return f"""# G-300 — human validation of the K = 2 partition

> **Both gates were pre-registered in `docs/protocol.md` (RQ1-F) before a single
> item was annotated.** Read that section first.
>
> ### Two constraints, recorded rather than worked around
>
> **Only {int(band_tab['n'].sum()) if band_tab is not None else 123} of the
> frozen G-300 are in region A** and therefore carry a K = 2 label. The split map
> is frozen (inviolable rule 3) and was **not** regenerated. All 300 are
> annotated; Gate 2 runs on the region-A subset and its reduced power is stated
> as a number.
>
> **Two annotators, not the three RQ1 states** — logged as a deviation. With two
> there is no majority, so the adjudication rule was fixed in advance:
> **disagreements are not resolved.** The gold value is the mean of the two
> ratings and the disagreement rate is reported below. Adjudicating after seeing
> the data is how an IAA figure gets laundered.

- **Config:** `{cfg_path}` · **Generated (UTC):** {prov['timestamp_utc']}
- **Commit:** `{prov['git_commit']}` · **Seed:** {cfg['seed']}
- Ratings filled: {', '.join(f'{w} {c}' for w, c in filled.items())} · items
  rated by **all** annotators: **{n_complete}**
- **Nothing is trained.** α, κ and AUC are agreement/rank statistics.

## Gate 1 — can humans agree at all?

{g1_txt}

| Statistic | Value |
|---|---|
| Krippendorff's α (**ordinal**) | **{alpha_o:.4f}** |
| Krippendorff's α (nominal, for reference) | {alpha_n:.4f} |
| Cohen's κ (linear weights) | {kap:.4f} |
| Exact agreement | {100 * exact:.1f}% |
| Agreement within 1 point | {100 * within1:.1f}% |

Ordinal α is the pre-registered figure. The nominal value is shown only because
the gap between them is informative: it is the part of the agreement that comes
from **near misses on an ordered scale** rather than from exact matches.

### Rating distribution per annotator

{dist.to_markdown()}

A distribution concentrated in one or two categories caps α mechanically —
there is little variance for agreement to be measured against — and is reported
here so that a low α is not misread as disagreement when it is actually
degeneracy.

## Gate 2 — does the human rating recover the machine's split?

{g2_txt}
{bands_md}
## What this settles, and what it does not

- **This is the arbiter for RQ1.** S2f eliminated valence and verbosity, so no
  cheaper instrument remained.
- **It does not establish that region A contains cluster structure.** It cannot:
  G1 already showed there is none (silhouette 0.053, monotone gap, HDBSCAN 100%
  noise). At best this shows a **reproducible, humanly-recognisable cut through
  a continuum** — which is a real finding, and is not the same sentence as
  "we discovered two audience personas".
- **It says nothing about region B**, which carries no K = 2 label at all.
"""


if __name__ == "__main__":
    raise SystemExit(main())
