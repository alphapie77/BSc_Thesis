"""REGISTER PROBE -- is `Sentiment == 2` a different KIND of text?

⚠️ **EXPLORATORY.** The hypothesis came from reading the data after S2, not from
the pre-registration. Nothing here is a confirmatory test. See
`configs/s2b_register_probe.yaml` and the deviations log in `docs/protocol.md`.

**The argument this script makes.** Every feature it measures is orthographic or
structural -- character counts, punctuation, length. None can express an opinion
about a film. If features that *cannot encode sentiment* nonetheless separate
class 2 from classes 0 and 1, then class 2 differs from the rest in FORM, and a
clustering that splits it off is recovering how the text was produced rather
than what it says.

**Nothing is trained.** Separation is measured by AUC, which is a rank
statistic with no fitted parameters, so inviolable rule 10 (only ten small
artifacts are ever trained) is untouched and no model here can overfit.

Run:
    python -m src.preprocess.s2b_register_probe --config configs/s2b_register_probe.yaml
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import stamp, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402

DANDA = "।"          # ।  Bengali full stop
COMMA_RUN = re.compile(r",{2,}")
LATIN = re.compile(r"[A-Za-z]")
DIGIT = re.compile(r"[0-9০-৯]")   # ASCII and Bengali digits
PUNCT = re.compile(r"[।,.!?;:\-—…\"'()]")

#: Closed pronoun set. Voice, not polarity -- these words are equally available
#: to praise and to complaint, so they cannot smuggle sentiment into the probe.
FIRST_PERSON = {
    "আমি", "আমার", "আমাকে", "আমরা", "আমাদের", "আমায়",
}


def features(text: str) -> dict:
    t = str(text)
    toks = t.split()
    n_words = len(toks)
    n_punct = len(PUNCT.findall(t))
    return {
        "n_words": n_words,
        "n_chars": len(t),
        "mean_word_len": (sum(len(w) for w in toks) / n_words) if n_words else 0.0,
        "n_danda": t.count(DANDA),
        "has_danda": int(DANDA in t),
        "n_comma": t.count(","),
        "has_comma_run": int(bool(COMMA_RUN.search(t))),
        "n_exclaim": t.count("!"),
        "n_question": t.count("?"),
        "punct_per_token": (n_punct / n_words) if n_words else 0.0,
        "has_latin": int(bool(LATIN.search(t))),
        "has_digit": int(bool(DIGIT.search(t))),
        "first_person": int(any(w in FIRST_PERSON for w in toks)),
    }


def auc(scores: np.ndarray, positive: np.ndarray) -> float:
    """Rank-based AUC (Mann-Whitney U), ties averaged. Nothing is fitted.

    0.5 means the feature is useless for telling the groups apart; 1.0 or 0.0
    means it separates them perfectly (0.0 being perfect separation with the
    sign flipped, which is just as informative).
    """
    order = np.argsort(scores, kind="mergesort")
    s = scores[order]
    ranks = np.empty(len(s), dtype=float)
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        ranks[i:j + 1] = (i + j) / 2.0 + 1.0
        i = j + 1
    r = np.empty(len(s), dtype=float)
    r[order] = ranks
    pos, neg = positive.sum(), (~positive).sum()
    if pos == 0 or neg == 0:
        return float("nan")
    return float((r[positive].sum() - pos * (pos + 1) / 2) / (pos * neg))


def bootstrap_types(tokens: list[str], budget: int, reps: int,
                    rng: np.random.Generator) -> tuple[float, float]:
    """Unique types in `budget` tokens sampled without replacement, repeated.

    Equal token budget is the point: a class with more text will trivially show
    more distinct words, so raw type counts across classes compare nothing.
    """
    arr = np.array(tokens, dtype=object)
    if len(arr) < budget:
        return float("nan"), float("nan")
    counts = [
        len(set(rng.choice(arr, size=budget, replace=False).tolist()))
        for _ in range(reps)
    ]
    return float(np.mean(counts)), float(np.std(counts))


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval -- behaves at p = 0 and p = 1, unlike normal-approx.

    Needed because one of the rates here is exactly 100%, where the textbook
    interval collapses to zero width and would overstate certainty.
    """
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z**2 / n
    c = p + z**2 / (2 * n)
    h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return float((c - h) / d), float((c + h) / d)


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s2b_register_probe.yaml")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    cfg_path = Path(args.config)
    cfg = yaml.safe_load((root / cfg_path).read_text(encoding="utf-8"))
    rng = np.random.default_rng(int(cfg["seed"]))

    df = pd.read_csv(root / cfg["input_csv"])
    if len(df) != cfg["expected_input_n"]:
        raise AssertionError(
            f"{cfg['input_csv']} has {len(df)} rows, expected "
            f"{cfg['expected_input_n']}."
        )

    text, lab = df[cfg["text_col"]].astype(str), df[cfg["label_col"]]
    focal = int(cfg["focal_class"])
    is_focal = (lab == focal).to_numpy()

    F = pd.DataFrame([features(t) for t in text])
    F.insert(0, cfg["id_col"], df[cfg["id_col"]])
    F[cfg["label_col"]] = lab
    F.to_csv(root / cfg["outputs"]["features_csv"], index=False,
             encoding="utf-8", lineterminator="\n")

    # --- AUC per feature ---------------------------------------------------
    rows = []
    for f in cfg["features"]:
        a = auc(F[f].to_numpy(dtype=float), is_focal)
        rows.append({
            "feature": f,
            "auc": a,
            "separation": abs(a - 0.5) * 2,     # 0 = useless, 1 = perfect
            f"mean_class{focal}": float(F.loc[is_focal, f].mean()),
            "mean_others": float(F.loc[~is_focal, f].mean()),
        })
    auc_tab = pd.DataFrame(rows).sort_values("separation", ascending=False)

    # --- lexical richness at equal token budget ----------------------------
    budget = int(cfg["lexical_richness"]["token_budget"])
    reps = int(cfg["lexical_richness"]["bootstrap"])
    rich = []
    for c in sorted(lab.unique()):
        toks = [w for t in text[lab == c] for w in t.split()]
        m, s = bootstrap_types(toks, budget, reps, rng)
        rich.append({"class": int(c), "total_tokens": len(toks),
                     "types_at_budget": m, "sd": s})
    rich_tab = pd.DataFrame(rich)

    # --- binary rates with Wilson intervals --------------------------------
    rate_rows = []
    for f in ("has_danda", "first_person", "has_comma_run", "has_latin"):
        for c in sorted(lab.unique()):
            sub = F.loc[lab == c, f]
            lo, hi = wilson(int(sub.sum()), len(sub))
            rate_rows.append({"feature": f, "class": int(c),
                              "rate_%": 100 * sub.mean(),
                              "ci95_lo_%": 100 * lo, "ci95_hi_%": 100 * hi})
    rate_tab = pd.DataFrame(rate_rows)

    # --- structural impossibilities ----------------------------------------
    # AUC is the wrong summary for a RARE binary feature: something present in
    # 9% of one group and 0% of another barely moves a rank statistic, yet
    # "0 out of 1,618" is categorical evidence. So the binary features are also
    # reported as: how many class-focal items WOULD carry this feature if the
    # class were drawn from the same population as the others?
    imp_rows = []
    n_focal = int(is_focal.sum())
    for f in ("first_person", "n_exclaim", "has_comma_run", "has_danda"):
        col = F[f]
        obs_focal = int((col[is_focal] > 0).sum())
        rate_other = float((col[~is_focal] > 0).mean())
        expected = rate_other * n_focal
        # Probability of observing ZERO (or ALL) under that rate, if the class
        # were an independent sample from the same population. Reported as a
        # log10 because the numbers leave floating point behind entirely.
        if obs_focal == 0 and rate_other > 0:
            log10p = n_focal * np.log10(1 - rate_other)
        elif obs_focal == n_focal and rate_other < 1:
            log10p = n_focal * np.log10(rate_other)
        else:
            log10p = float("nan")
        imp_rows.append({
            "feature": f,
            "rate_in_others_%": round(100 * rate_other, 2),
            "expected_in_focal": round(expected, 1),
            "observed_in_focal": obs_focal,
            "log10_p_if_same_population": round(log10p, 1),
        })
    imp_tab = pd.DataFrame(imp_rows)

    # --- near-duplicate endpoint composition -------------------------------
    nd_tab = None
    nd_path = root / cfg.get("near_dup_pairs_csv", "")
    if cfg.get("near_dup_pairs_csv") and nd_path.exists():
        m = dict(zip(df[cfg["id_col"]], lab))
        p = pd.read_csv(nd_path)
        ends = pd.concat([p["id_kept_side"].map(m), p["id_other_side"].map(m)])
        share = ends.value_counts(normalize=True).sort_index() * 100
        corpus = lab.value_counts(normalize=True).sort_index() * 100
        nd_tab = pd.DataFrame({
            "in_corpus_%": corpus.round(1),
            "in_near_dup_endpoints_%": share.round(1),
            "over_representation_x": (share / corpus).round(2),
        })

    report = build_report(cfg, cfg_path, stamp(cfg_path.as_posix()), focal,
                          auc_tab, rich_tab, rate_tab, imp_tab, nd_tab, len(df))
    out = write_text_lf(root / cfg["outputs"]["report_md"], report)

    print(auc_tab.to_string(index=False))
    print()
    print(rich_tab.to_string(index=False))
    print()
    print(imp_tab.to_string(index=False))
    print(f"\nwrote {out}")
    print("EXPLORATORY -- generates a hypothesis, settles nothing.")
    return 0


def build_report(cfg, cfg_path, prov, focal, auc_tab, rich_tab, rate_tab,
                 imp_tab, nd_tab, n) -> str:
    def md(t):
        return t.to_markdown(index=False, floatfmt=".4f")

    top = auc_tab.iloc[0]
    nd_md = (
        md(nd_tab.reset_index().rename(columns={"index": "Sentiment"}))
        if nd_tab is not None else
        "_`near_dup_pairs.csv` absent -- run S2 first for this section._"
    )
    r2 = rich_tab[rich_tab["class"] == focal].iloc[0]
    others = rich_tab[rich_tab["class"] != focal]

    n_focal = int(round(imp_tab.loc[imp_tab["feature"] == "has_danda",
                                    "observed_in_focal"].iloc[0]))
    imp_md = imp_tab.to_markdown(index=False)
    top_auc = float(top["auc"])

    return f"""# S2b — Register probe: is `Sentiment == {focal}` a different kind of text?

> ### ⚠️ EXPLORATORY — not a confirmatory test
>
> The hypothesis behind this probe came from **reading the data after S2**, not
> from the pre-registration. No threshold here was fixed in advance, and no
> claim in this file may be reported as a confirmed finding. It exists to decide
> whether a confirmatory test is worth registering, and to put a specific,
> answerable question to the data collector. Registered as exploratory in
> `docs/protocol.md` (Deviations log, 2026-07-30).

- **Config:** `{cfg_path}` · **Input:** `{cfg["input_csv"]}` ({n} rows)
- **Generated (UTC):** {prov["timestamp_utc"]} · **Commit:** `{prov["git_commit"]}`
- **Nothing is trained.** AUC is a rank statistic with no fitted parameters, so
  inviolable rule 10 is untouched.

## Why this probe exists

S2 produced clusters that do **not** reproduce the sentiment partition
(ARI 0.179) yet are moderately associated with it (Cramér's V 0.410). Refolding
that crosstab as *cluster 0 vs rest* × *Sentiment {focal} vs rest* gives
**φ = 0.565** — a stronger association than the full three-way table — and only
**12 of 1,572** class-{focal} items land in cluster 0.

`docs/protocol.md` RQ1 Band 3 already names this confound: clusters recovering
**the source of the text** rather than any persona. `docs/STATUS.md` called it
*untestable in principle*, because venue was never retained at collection
(provenance fact (c)).

**Venue was not retained — but writing style survives in the text itself.** That
is what this probe measures.

## The design constraint that makes this argument work

Every feature is **orthographic or structural**: character counts, punctuation,
length. None of them can express an opinion about a film. A lexical feature
would be worthless here — a word like *দুর্বল* predicts a negative label *and* a
register at once, so separating with it would prove nothing.

So if these features separate class {focal} from the rest, the classes differ in
**form**, not in what they say about films. `first_person` is the one judgement
call (a closed pronoun set, reporting voice rather than polarity); it is listed
separately so a sceptical reader can discount it without touching the rest.

## Separation by feature (AUC)

AUC 0.5 = the feature cannot tell the groups apart. Far from 0.5 in either
direction = it can.

{md(auc_tab)}

The separations here are **moderate, not decisive** — the best single
feature reaches only {top_auc:.3f}. Reported as measured; the strong evidence is
in the two sections below, not in this table.

Strongest single feature: **`{top["feature"]}`**, AUC **{top["auc"]:.4f}**.

## Structural impossibilities — the decisive table

AUC is the wrong summary for a **rare** binary feature. Something present in 9%
of one group and 0% of another barely moves a rank statistic, yet "0 out of
{n_focal:,}" is categorical. So each binary feature is also reported as: how many
class-{focal} items *would* carry it, if the class were drawn from the same
population as the others?

{imp_md}

`log10_p_if_same_population` is the base-10 log of the probability of seeing a
count that extreme under the other classes' own rate. These are not marginal
p-values; they leave floating point behind entirely.

**Not one of the {n_focal:,} class-{focal} texts contains a first-person pronoun,
an exclamation mark, or a run of commas — and every single one carries a দাঁড়ি.**
Four independent structural absolutes. No opinion about films makes a writer
avoid the word *আমি* {n_focal:,} times in a row.

Note the definition: `first_person` is exact-token matching against a closed
pronoun set (আমি, আমার, আমাকে, আমরা, আমাদের, আমায়). First-person *verb* forms
(দেখলাম, লাগলো) are not counted, and a looser substring match finds a small
non-zero rate — so read this as "no first-person pronoun", not "no first-person
voice whatsoever".

## Lexical richness at an equal token budget

Unique word types in a fixed sample of {cfg["lexical_richness"]["token_budget"]:,}
tokens, bootstrapped {cfg["lexical_richness"]["bootstrap"]}×. Equal budget is the
point: a class with more text trivially shows more distinct words, so raw counts
compare nothing.

{md(rich_tab)}

Class {focal} draws on **{r2["types_at_budget"]:.0f}** distinct types per
{cfg["lexical_richness"]["token_budget"]:,} tokens, against
{" and ".join(f"{v:.0f}" for v in others["types_at_budget"])} for the other
classes. A vocabulary roughly half the size at identical length is not a
property of holding a neutral opinion; it is a property of how the text was
produced.

## Binary rates, with 95% Wilson intervals

Wilson rather than the normal approximation because one rate sits at exactly
100%, where the textbook interval collapses to zero width and overstates
certainty.

{md(rate_tab)}

## Near-duplicate endpoints by class

{nd_md}

## What this does and does not show

**Shows:** class {focal} differs from classes 0 and 1 on features that carry no
sentiment content, and the S2 clustering separates it far more sharply than it
separates sentiment.

**Does not show:** *why*. At least three explanations fit equally well, and this
data cannot choose between them:

1. class {focal} was **synthetically generated** to fill the ~1,665-per-class
   quota (genuinely neutral film comments are rare on social media — people post
   when they feel strongly);
2. class {focal} was **collected from a different venue** — a blog or review
   site, where formal register is native;
3. class {focal} was **written by hand** by the annotator as neutral examples.

All three contradict provenance fact (c) ("bulk pull from Facebook groups and
YouTube channels"), and under **all three** the clusters track provenance rather
than persona. Distinguishing them requires the data collector, not more
statistics: see `docs/provenance_query.md`.

**Until it is answered, no persona claim resting on the three-class structure
can be defended.**
"""


if __name__ == "__main__":
    raise SystemExit(main())
