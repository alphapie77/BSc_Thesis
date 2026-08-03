"""S2e — WHAT IS THE K=2 PARTITION MADE OF?

    python -m src.cluster.s2e_profile --config configs/s2e_profile.yaml

Gate G1 selected K = 2 and stopped there. It never persisted the labels, and it
never asked what separates the two halves. Both gaps are closed here, in that
order, because **G-300 stratification needs the labels** and **G-300 itself
should not be spent on a partition nobody has looked at**.

**Interpretation is pre-registered** in `docs/protocol.md`, "RQ1-D
pre-commitment", written before this file existed. The analysis is exploratory
in origin — the decision to profile was made after seeing G1 — but what each
outcome *means* was fixed while the numbers were still unknown. That distinction
is stated in the report itself, not just here.

**The one number that matters** is `length_auc`: how well raw word count alone
predicts cluster membership. Reviews here average ~8 words, and on L2-normalised
LaBSE embeddings of very short text, length is a plausible dominant axis. If a
ruler reproduces the encoder's cut, the cut is not a persona structure.

**Nothing is trained.** K-Means is refitted only to reproduce G1's own labels
(same seed, same config, verified against G1's published numbers before use).
AUC and Cliff's delta are rank statistics with no fitted parameters, and the
log-odds prior is fixed, not estimated. Inviolable rule 10 is untouched, and so
is rule 7: whitespace tokens only, no stemming, no stopword removal, no TF-IDF.
No quantity computed here is ever used as a model input.
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from pathlib import Path

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("USE_TF", "0")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.cluster.s2d_ktable import embed  # noqa: E402
from src.common.provenance import NEWLINE, stamp, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402
from src.preprocess.s2b_register_probe import (  # noqa: E402
    auc, bootstrap_types, features, wilson,
)

LENGTH_DOMINATED = "LENGTH_DOMINATED"
LENGTH_CONFOUNDED = "LENGTH_CONFOUNDED"
NOT_LENGTH = "NOT_LENGTH"


# --------------------------------------------------------------------------
# Effect sizes. Rank-based throughout: nothing is fitted, nothing assumes
# normality, and 8-word review lengths are nowhere near normal.
# --------------------------------------------------------------------------
def directionless_auc(scores: np.ndarray, positive: np.ndarray) -> float:
    """`max(auc, 1 - auc)`.

    Which cluster K-Means happens to call 0 is arbitrary — it depends on
    centroid initialisation, not on the data. So a feature that predicts
    membership perfectly in the "wrong" direction (AUC 0.02) is exactly as
    diagnostic as one that predicts it perfectly in the "right" one (0.98), and
    the pre-registered bands in RQ1-D are written against this quantity.
    """
    a = auc(scores, positive)
    return float(max(a, 1.0 - a)) if np.isfinite(a) else float("nan")


def cliffs_delta(a: float) -> float:
    """Cliff's delta from AUC. `2*auc - 1`, in [-1, 1]; 0 = no difference.

    Reported alongside AUC because AUC's floor is 0.5 and readers routinely
    misread 0.6 as "60% right". Delta's floor is 0, which is harder to misread.
    """
    return float(2.0 * a - 1.0)


# --------------------------------------------------------------------------
# Distinctive vocabulary — Monroe, Colaresi & Quinn (2008)
# --------------------------------------------------------------------------
def log_odds_with_prior(counts_a: Counter, counts_b: Counter,
                        prior_strength: float, min_count: int) -> pd.DataFrame:
    """Z-scored log-odds ratio with an informative Dirichlet prior.

    The naive alternatives both fail on a corpus this small. Raw frequency
    ranking returns the most common words in the language, so it needs a
    stopword list — which inviolable rule 7 forbids, and rightly: a stopword
    list for Bangla is a modelling choice nobody in this project has justified.
    An unsmoothed log-odds ratio does the opposite, exploding for words seen
    twice, so it returns hapaxes and typos.

    Monroe's prior fixes both at once by shrinking every word toward its
    corpus-wide rate in proportion to how rare it is. Frequent words move
    little because the evidence is strong; rare words move a lot because it is
    not. That is why **no stopword removal is needed** — and why this method
    was chosen over the alternatives rather than for convenience.

    Returns one row per word with the z-score; sign gives the side.
    """
    vocab = set(counts_a) | set(counts_b)
    total = Counter(counts_a) + Counter(counts_b)
    n_total = sum(total.values())
    n_a, n_b = sum(counts_a.values()), sum(counts_b.values())
    if n_total == 0:
        return pd.DataFrame(columns=["word", "count_a", "count_b", "z"])

    rows = []
    for w in vocab:
        if total[w] < min_count:
            continue
        alpha = prior_strength * total[w] / n_total
        ya, yb = counts_a[w], counts_b[w]
        # Odds of w against everything else, in each group, both smoothed.
        oa = (ya + alpha) / (n_a + prior_strength - ya - alpha)
        ob = (yb + alpha) / (n_b + prior_strength - yb - alpha)
        delta = np.log(oa) - np.log(ob)
        var = 1.0 / (ya + alpha) + 1.0 / (yb + alpha)
        rows.append({"word": w, "count_a": ya, "count_b": yb,
                     "log_odds_delta": float(delta),
                     "z": float(delta / np.sqrt(var))})
    out = pd.DataFrame(rows)
    return out.sort_values("z", ascending=False).reset_index(drop=True)


def length_verdict(length_auc: float, cfg) -> str:
    b = cfg["length_bands"]
    if length_auc >= b["dominated_at_or_above"]:
        return LENGTH_DOMINATED
    if length_auc >= b["confounded_at_or_above"]:
        return LENGTH_CONFOUNDED
    return NOT_LENGTH


# --------------------------------------------------------------------------
def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s2e_profile.yaml")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    cfg_path = Path(args.config)
    cfg = yaml.safe_load((root / cfg_path).read_text(encoding="utf-8"))
    rng = np.random.default_rng(int(cfg["seed"]))
    k = int(cfg["k"])

    # --- exactly G1's rows, in exactly G1's order ---------------------------
    asg = pd.read_csv(root / cfg["input_assignments"])
    if len(asg) != cfg["expected_n"]:
        raise AssertionError(
            f"{cfg['input_assignments']} has {len(asg)} rows, expected "
            f"{cfg['expected_n']}."
        )
    ids = set(asg[cfg["id_col"]])
    df = pd.read_csv(root / cfg["input_csv"])
    df = df[df[cfg["id_col"]].isin(ids)].sort_values(
        cfg["id_col"], kind="mergesort").reset_index(drop=True)
    assert len(df) == len(asg), "id mismatch between assignments and bn_clean"
    text = df[cfg["text_col"]].astype(str)
    sent = df[cfg["label_col"]].to_numpy()

    emb = embed(text.tolist(), cfg, root)

    from sklearn.cluster import KMeans
    from sklearn.metrics import adjusted_rand_score, silhouette_score

    km = KMeans(n_clusters=k, n_init=int(cfg["kmeans"]["n_init"]),
                random_state=int(cfg["kmeans"]["random_state"])).fit(emb)
    lab = km.labels_

    # --- GUARD: is this G1's partition, or merely *a* K=2 partition? --------
    # Same code, same seed, same data must give the same numbers. If it does
    # not, something drifted — the config, the cache, the embedding — and every
    # sentence below would describe a partition the thesis never selected. That
    # is a worse failure than not running, so it stops here.
    sil = float(silhouette_score(emb, lab))
    ari_sent = float(adjusted_rand_score(sent, lab))
    ktab = pd.read_csv(root / cfg["guard"]["ktable_csv"])
    g1 = ktab[ktab["K"] == k].iloc[0]
    tol = float(cfg["guard"]["tolerance"])
    for name, got, want in (("silhouette", sil, float(g1["silhouette"])),
                            ("ari_vs_sentiment", ari_sent,
                             float(g1["ari_vs_sentiment"]))):
        if abs(got - want) > tol:
            raise AssertionError(
                f"this is NOT the partition G1 selected: {name} = {got:.8f} "
                f"here, {want:.8f} in {cfg['guard']['ktable_csv']}. Something "
                f"drifted between the two configs or the embedding cache is "
                f"stale. Fix that before reading any profile."
            )
    print(f"guard OK — reproduced G1's K={k}: silhouette {sil:.6f}, "
          f"ARI vs Sentiment {ari_sent:.6f}")

    # --- geometry: how comfortably does each review sit in its cluster? -----
    d = np.linalg.norm(emb[:, None, :] - km.cluster_centers_[None, :, :], axis=2)
    order = np.argsort(d, axis=1)
    d_own = d[np.arange(len(d)), lab]
    d_other = d[np.arange(len(d)), order[:, 1]]
    margin = d_other - d_own      # near zero = the point could go either way

    out_asg = pd.DataFrame({
        cfg["id_col"]: df[cfg["id_col"]],
        "cluster_k2": lab,
        cfg["label_col"]: sent,
        "region": asg.sort_values(cfg["id_col"], kind="mergesort")
                     ["region"].to_numpy(),
        "dist_to_own_centroid": d_own,
        "margin": margin,
        "n_words": [len(t.split()) for t in text],
    })
    out_asg.to_csv(root / cfg["outputs"]["assignments_csv"], index=False,
                   encoding="utf-8", lineterminator=NEWLINE)

    is_one = lab == 1        # "positive" side for every AUC below

    # --- surface features ---------------------------------------------------
    F = pd.DataFrame([features(t) for t in text])
    F.insert(0, cfg["id_col"], df[cfg["id_col"]])
    F["cluster_k2"] = lab
    F.to_csv(root / cfg["outputs"]["features_csv"], index=False,
             encoding="utf-8", lineterminator=NEWLINE)

    rows = []
    for f in cfg["features"]:
        v = F[f].to_numpy(dtype=float)
        a = directionless_auc(v, is_one)
        rows.append({
            "feature": f,
            "auc_directionless": a,
            "cliffs_delta": cliffs_delta(a),
            "mean_cluster0": float(v[~is_one].mean()),
            "mean_cluster1": float(v[is_one].mean()),
            "median_cluster0": float(np.median(v[~is_one])),
            "median_cluster1": float(np.median(v[is_one])),
        })
    feat_tab = pd.DataFrame(rows).sort_values(
        "auc_directionless", ascending=False).reset_index(drop=True)

    length_auc = float(feat_tab.loc[
        feat_tab["feature"] == cfg["length_feature"], "auc_directionless"].iloc[0])
    verdict = length_verdict(length_auc, cfg)
    top_feat = feat_tab.iloc[0]

    # --- binary rates with Wilson intervals ---------------------------------
    rate_rows = []
    for f in ("has_danda", "first_person", "has_comma_run", "has_latin",
              "has_digit"):
        for c in (0, 1):
            sub = F.loc[lab == c, f]
            lo, hi = wilson(int(sub.sum()), len(sub))
            rate_rows.append({"feature": f, "cluster": c, "n": len(sub),
                              "rate_%": 100 * float(sub.mean()),
                              "ci95_lo_%": 100 * lo, "ci95_hi_%": 100 * hi})
    rate_tab = pd.DataFrame(rate_rows)

    # --- lexical richness at an equal token budget --------------------------
    budget = int(cfg["lexical_richness"]["token_budget"])
    reps = int(cfg["lexical_richness"]["bootstrap"])
    rich = []
    for c in (0, 1):
        toks = [w for t in text[lab == c] for w in t.split()]
        m, s = bootstrap_types(toks, budget, reps, rng)
        rich.append({"cluster": c, "n_reviews": int((lab == c).sum()),
                     "total_tokens": len(toks), "types_at_budget": m, "sd": s})
    rich_tab = pd.DataFrame(rich)

    # --- sentiment composition ----------------------------------------------
    cross = pd.crosstab(pd.Series(lab, name="cluster_k2"),
                        pd.Series(sent, name=cfg["label_col"]))
    cross_pct = (cross.div(cross.sum(axis=1), axis=0) * 100).round(1)

    # --- distinctive vocabulary ----------------------------------------------
    ca = Counter(w for t in text[lab == 0] for w in t.split())
    cb = Counter(w for t in text[lab == 1] for w in t.split())
    lo_tab = log_odds_with_prior(ca, cb, float(cfg["log_odds"]["prior_strength"]),
                                 int(cfg["log_odds"]["min_count"]))
    lo_tab = lo_tab.rename(columns={"count_a": "count_c0", "count_b": "count_c1"})
    lo_tab.to_csv(root / cfg["outputs"]["logodds_csv"], index=False,
                  encoding="utf-8", lineterminator=NEWLINE)
    top_n = int(cfg["log_odds"]["top_n"])
    lo_c0 = lo_tab.head(top_n)                       # z high  -> cluster 0
    lo_c1 = lo_tab.tail(top_n).iloc[::-1]            # z low   -> cluster 1

    # --- the examples Sabbir actually reads ---------------------------------
    mx = int(cfg["examples"]["max_chars"])

    def clip(t):
        t = " ".join(str(t).split())
        return t if len(t) <= mx else t[:mx] + " …"

    reps_ex = {}
    for c in (0, 1):
        idx = np.where(lab == c)[0]
        idx = idx[np.argsort(d_own[idx])][:int(cfg["examples"]["n_representative"])]
        reps_ex[c] = [(df[cfg["id_col"]].iloc[i], int(sent[i]),
                       len(text.iloc[i].split()), clip(text.iloc[i]))
                      for i in idx]
    bidx = np.argsort(margin)[:int(cfg["examples"]["n_boundary"])]
    boundary = [(df[cfg["id_col"]].iloc[i], int(lab[i]), float(margin[i]),
                 len(text.iloc[i].split()), clip(text.iloc[i])) for i in bidx]

    report = build_report(
        cfg, cfg_path, stamp(cfg_path.as_posix()), len(df), k, lab, sil,
        ari_sent, feat_tab, length_auc, verdict, top_feat, rate_tab, rich_tab,
        cross, cross_pct, lo_c0, lo_c1, reps_ex, boundary, margin, d_own,
    )
    out = write_text_lf(root / cfg["outputs"]["report_md"], report)

    print(feat_tab.to_string(index=False))
    print(f"\nlength_auc ({cfg['length_feature']}) = {length_auc:.4f}"
          f"  ->  {verdict}")
    print(f"strongest surface feature: {top_feat['feature']} "
          f"AUC {top_feat['auc_directionless']:.4f}")
    print(f"\nwrote {out}")
    print("Read docs/protocol.md RQ1-D before interpreting this.")
    return 0


def build_report(cfg, cfg_path, prov, n, k, lab, sil, ari_sent, feat_tab,
                 length_auc, verdict, top_feat, rate_tab, rich_tab, cross,
                 cross_pct, lo_c0, lo_c1, reps_ex, boundary, margin,
                 d_own) -> str:
    def md(t, f=".4f"):
        return t.to_markdown(index=False, floatfmt=f)

    n0, n1 = int((lab == 0).sum()), int((lab == 1).sum())
    hl = float(cfg["surface_auc_headline"])
    top_auc = float(top_feat["auc_directionless"])

    band = {
        LENGTH_DOMINATED: f"""**{LENGTH_DOMINATED}** — `length_auc` =
{length_auc:.4f} ≥ {cfg['length_bands']['dominated_at_or_above']}.

Word count alone reproduces most of the encoder's cut. Under RQ1-D this
partition **may not be called a persona structure**, and **G-300 may not be run
on it as though it were one**. The two permitted responses were fixed in
advance: report RQ1 as a negative result on *data-derived* personas — which
RQ1-C already established as publishable — or re-operationalise personas on
engagement features with length explicitly controlled, as a separate and clearly
labelled analysis.

**This does not show the halves are not personas.** Real personas plausibly do
differ in length. It shows the persona claim is **unsupported**, which is a
different and weaker statement, and the thesis must make it in that form.""",
        LENGTH_CONFOUNDED: f"""**{LENGTH_CONFOUNDED}** — `length_auc` =
{length_auc:.4f}, in [{cfg['length_bands']['confounded_at_or_above']},
{cfg['length_bands']['dominated_at_or_above']}).

Length is a **major but not sole** component of the cut. Under RQ1-D, G-300 may
proceed on two conditions, neither optional: the annotation guideline is written
so that annotators cannot succeed by reading length alone, and **length is
reported next to every persona claim in the thesis** — main text, not a
footnote.""",
        NOT_LENGTH: f"""**{NOT_LENGTH}** — `length_auc` = {length_auc:.4f} <
{cfg['length_bands']['confounded_at_or_above']}.

The cut is not primarily about how much people wrote. Under RQ1-D this
**removes the cheapest alternative explanation and does nothing more**. It is
not evidence that the halves are personas; G-300 remains the arbiter, exactly as
in RQ1 Band 1.""",
    }[verdict]

    headline = ""
    if top_auc >= hl:
        headline = f"""
### ⚠️ Headline finding: a regular expression does the encoder's job

`{top_feat['feature']}` reaches AUC **{top_auc:.4f}** ≥ {hl}. A property
computable with a few lines of string handling separates the two halves about as
well as a 768-dimensional multilingual sentence encoder. Under RQ1-D this is
**reported as a finding about the corpus**, whatever the feature turns out to
be, and it carries the same consequence for that feature as `{LENGTH_DOMINATED}`
does for length.
"""

    def ex_block(items):
        return "\n".join(
            f"| `{i}` | {s} | {w} | {t} |" for i, s, w, t in items)

    reps_md = "\n\n".join(
        f"""#### Cluster {c} — the {len(reps_ex[c])} reviews closest to its centre

| id | Sentiment | words | review |
|---|---|---|---|
{ex_block(reps_ex[c])}""" for c in (0, 1))

    bnd_md = "\n".join(
        f"| `{i}` | {c} | {m:.4f} | {w} | {t} |" for i, c, m, w, t in boundary)

    return f"""# S2e — What is the K = 2 partition made of? (region A)

> **Interpretation was pre-registered in `docs/protocol.md` (RQ1-D) before this
> script existed.** Read that section first.
>
> ### The honest label on this analysis
>
> **Exploratory in origin, pre-registered in interpretation.** The decision to
> profile came *after* seeing G1's table, so this is not a confirmatory test and
> is not reported as one. What was fixed before the numbers were known is what
> each outcome would be taken to **mean** — because with a stable K already in
> hand, any difference found between the halves will look like a persona unless
> somebody wrote down in advance what would *not* count as one.

- **Config:** `{cfg_path}` · **n:** {n} (region A, post-dedup) · **K:** {k}
- **Generated (UTC):** {prov['timestamp_utc']} · **Commit:** `{prov['git_commit']}`
- **Seed:** {cfg['seed']} · Cluster sizes: **{n0}** / **{n1}**
  ({100*n0/n:.1f}% / {100*n1/n:.1f}%)
- **Guard passed:** this run reproduced G1's own silhouette ({sil:.6f}) and
  ARI vs Sentiment ({ari_sent:.6f}) to within {cfg['guard']['tolerance']:g}, so
  these are the labels G1 selected — not merely *a* K=2 solution.
- **Nothing is trained.** AUC and Cliff's delta are rank statistics; the
  log-odds prior is fixed, not estimated. Rules 7 and 10 intact.

## Why this step exists at all

G1 established two things and left a third unanswered.

**Established:** the cut is reproducible (prediction strength 0.860, bootstrap
ARI 0.940 ± 0.029), and it is **not** the sentiment split (ARI {ari_sent:.4f},
Band 1).

**Also established, and easy to overlook:** there are no separated groups here
to find. Silhouette {sil:.4f}, a gap statistic that rises monotonically and is
satisfied at no K, and HDBSCAN classifying **100%** of points as noise. The
recorded reading is *a highly reproducible bisection of a space with no
separated groups*.

**Unanswered:** a reproducible bisection of a continuum is exactly what K-Means
produces when it cuts along the single dominant direction of variation. **What
is that direction?** This step asks — before 300 human annotations are spent
finding out the expensive way.

## Verdict

{band}
{headline}
## The decisive table: can a surface feature do the encoder's job?

AUC is reported **directionless** — `max(auc, 1-auc)` — because which half
K-Means labels 0 is an artefact of initialisation, not a property of the data.
0.5 means the feature cannot tell the halves apart at all; 1.0 means it
separates them perfectly. Cliff's delta is the same information on a 0-centred
scale, included because AUC's floor of 0.5 is routinely misread.

{md(feat_tab)}

**Read the top row first.** If it is a length or punctuation feature with a high
AUC, the encoder found something a ruler could have found.

## Binary rates, with 95% Wilson intervals

Wilson rather than the normal approximation: these rates can sit at or near 0%
and 100%, where the textbook interval collapses to zero width and overstates
certainty.

{md(rate_tab, ".2f")}

## Lexical richness at an equal token budget

Unique word types in a fixed sample of {cfg['lexical_richness']['token_budget']:,}
tokens, bootstrapped {cfg['lexical_richness']['bootstrap']}×. Equal budget is the
whole point: the larger half would trivially show more distinct words otherwise,
and the comparison would mean nothing.

{md(rich_tab)}

## Sentiment composition of each half

Counts:

{cross.to_markdown()}

Row percentages:

{cross_pct.to_markdown()}

ARI against Sentiment is {ari_sent:.4f}, so this is **not** a relabelling of the
sentiment classes — but the composition is reported in full anyway, because
"not identical to sentiment" and "independent of sentiment" are different
claims and only the first is established.

## Distinctive vocabulary — a reading aid, not evidence

Log-odds ratio with an informative Dirichlet prior (Monroe, Colaresi & Quinn
2008), z-scored, over whitespace tokens. **No stemming, no stopword removal, no
TF-IDF** — Monroe's prior shrinks each word toward its corpus-wide rate in
proportion to how rare it is, which is precisely why stopword removal is
unnecessary and why this method was chosen over the alternatives. Inviolable
rule 7 intact.

**Under RQ1-D, no claim in the thesis may rest on these lists.** They are here
so a human can look at the two halves and form a judgement; ranked terms are not
a test.

### Terms characteristic of cluster 0

{md(lo_c0, ".3f")}

### Terms characteristic of cluster 1

{md(lo_c1, ".3f")}

## The reviews themselves — this is the part to read

Everything above is scaffolding for this section. Read the two blocks and ask
one question: **do these read like two kinds of viewer, or like two lengths of
the same viewer?**

{reps_md}

## How sharp is the boundary?

Margin = distance to the other centroid minus distance to one's own. Near zero
means the review could have gone either way; the assignment is a coin flip that
the seed happened to settle. Median margin **{float(np.median(margin)):.4f}**,
and **{100*float((margin < 0.02).mean()):.1f}%** of reviews sit within 0.02 of
the boundary.

| id | cluster | margin | words | review |
|---|---|---|---|---|
{bnd_md}

If a large share of the corpus sits near the boundary, that is the silhouette of
{sil:.4f} made concrete — the halves are two sides of one crowd, not two crowds.

## What this step does NOT settle — in either direction

1. **That the halves are personas.** No statistic here can establish that. Only
   G-300, with three annotators and κ/α, can.
2. **That the halves are *not* personas, because a surface feature separates
   them.** Real personas plausibly differ in length and punctuation. A
   `{LENGTH_DOMINATED}` verdict shows the persona claim is **unsupported**, not
   that it is false — a weaker statement, and the one the thesis must make.
3. **Anything at all from the vocabulary lists on their own.**

## What to do next

The verdict above selects the branch, and both branches were written before the
number was known. Whichever applies, the outstanding decision is Sabbir's, not a
statistic's: **STATUS open decision 12** — the title and framing say *three
personas* throughout the pipeline, the pre-defence report and the conference
draft, and that language now needs revisiting for two, and qualifying for what
"persona" is here allowed to mean.
"""


if __name__ == "__main__":
    raise SystemExit(main())
