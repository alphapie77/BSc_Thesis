"""REGION SPLIT -- the corpus is two corpora joined at a row number.

⚠️ **EXPLORATORY.** Registered in `docs/protocol.md`. It **supersedes the framing
of `s2b_register_probe`**: s2b asked whether class 2 is a different kind of text
and answered yes, but class 2 exists only in the second half of the raw file, so
what looked like a property of the neutral *class* is a property of a *region*.
Rows 3665-4330 are labelled 0 and carry the same uniform signature as the
neutral rows; rows 499-896, also labelled 0, do not.

The grouping variable is therefore `raw_row`, not `Sentiment`. This is
recoverable only because `review_id` derives from the raw row order of the
source `.xlsx`.

Rule 1 holds: the raw file is opened read-only and nothing is written to it.

Run:
    python -m src.preprocess.s2c_region_split --config configs/s2c_region_split.yaml
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import stamp, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402
from src.preprocess.s2b_register_probe import features  # noqa: E402


def label_runs(v: np.ndarray) -> list[tuple[int, int, float, int]]:
    """Contiguous runs of identical label, as (start, end, label, length)."""
    runs, start = [], 0
    for i in range(1, len(v) + 1):
        same = (
            i < len(v)
            and (v[i] == v[i - 1] or (pd.isna(v[i]) and pd.isna(v[i - 1])))
        )
        if not same:
            runs.append((start, i - 1, v[start], i - start))
            start = i
    return runs


def region_stats(F: pd.DataFrame, texts: pd.Series) -> dict:
    toks = [w for t in texts for w in str(t).split()]
    return {
        "n": len(F),
        "danda_%": 100 * F["has_danda"].mean(),
        "first_person_%": 100 * F["first_person"].mean(),
        "exclaim_%": 100 * (F["n_exclaim"] > 0).mean(),
        "comma_run_%": 100 * F["has_comma_run"].mean(),
        "median_words": float(F["n_words"].median()),
        "types_per_1k_tokens": 1000 * len(set(toks)) / len(toks) if toks else float("nan"),
    }


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s2c_region_split.yaml")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    cfg_path = Path(args.config)
    cfg = yaml.safe_load((root / cfg_path).read_text(encoding="utf-8"))

    raw = pd.read_excel(root / cfg["input_xlsx"])          # READ ONLY (rule 1)
    text = raw[cfg["text_col"]].astype(str)
    lab = raw[cfg["label_col"]]
    F = pd.DataFrame([features(t) for t in text])

    b = int(cfg["boundary_row"])
    A, B = cfg["region_a_name"], cfg["region_b_name"]
    region = np.where(np.arange(len(raw)) < b, A, B)

    runs = [r for r in label_runs(lab.values) if r[3] >= 50]
    run_tab = pd.DataFrame([
        {"rows": f"{s}-{e}", "label": ("null" if pd.isna(l) else int(l)),
         "n": n, **region_stats(F.iloc[s:e + 1], text.iloc[s:e + 1])}
        for s, e, l, n in runs
    ])

    reg_tab = pd.DataFrame([
        {"region": r, **region_stats(F[region == r], text[region == r])}
        for r in (A, B)
    ])

    comp = pd.crosstab(region, lab.fillna(-1)).rename(columns={-1.0: "unlabelled"})

    # Rolling changepoint in the danda rate.
    w = int(cfg["rolling_window"])
    roll = F["has_danda"].rolling(w, center=True).mean() * 100
    trace = pd.DataFrame({
        "row": list(range(b - 150, b + 151, 25)),
    })
    trace["danda_%_rolling"] = [roll.iloc[r] for r in trace["row"]]
    trace["label"] = [
        ("null" if pd.isna(lab.iloc[r]) else int(lab.iloc[r])) for r in trace["row"]
    ]

    # How the cleaned corpus inherits the split.
    clean = pd.read_csv(root / cfg["input_clean_csv"])
    clean["raw_row"] = clean[cfg["id_col"]].str.replace("bn_", "", regex=False).astype(int)
    clean["region"] = np.where(clean["raw_row"] < b, A, B)
    clean_comp = pd.crosstab(clean["region"], clean[cfg["label_col"]], margins=True)

    report = build_report(cfg, cfg_path, stamp(cfg_path.as_posix()),
                          run_tab, reg_tab, comp, trace, clean_comp, A, B, b)
    out = write_text_lf(root / cfg["outputs"]["report_md"], report)

    print(reg_tab.to_string(index=False))
    print()
    print(clean_comp.to_string())
    print(f"\nwrote {out}")
    print("EXPLORATORY -- supersedes the framing in s2b_register_probe.md")
    return 0


def build_report(cfg, cfg_path, prov, run_tab, reg_tab, comp, trace,
                 clean_comp, A, B, b) -> str:
    def md(t, idx=False):
        return t.to_markdown(index=idx, floatfmt=".1f")

    a_row = reg_tab.iloc[0]
    b_row = reg_tab.iloc[1]
    n_b = int(b_row["n"])
    pct_b = 100 * n_b / (int(a_row["n"]) + n_b)

    return f"""# S2c — The corpus is two corpora, joined at row {b}

> ### ⚠️ EXPLORATORY — and it supersedes `s2b_register_probe.md`
>
> `s2b` asked whether **class 2** is a different kind of text and answered yes.
> That was true but **mis-framed**. Class 2 exists only in the second half of the
> raw file, so what looked like a property of the neutral *class* is a property
> of a *region of the file*. Rows 3665–4330 are labelled **0 (negative)** and
> carry the same uniform signature; rows 499–896, also labelled 0, do not.
>
> Read this file instead of s2b's conclusions. s2b's measurements stand; its
> interpretation does not.

- **Config:** `{cfg_path}` · **Generated (UTC):** {prov["timestamp_utc"]}
- **Commit:** `{prov["git_commit"]}`
- The raw `.xlsx` is opened **read-only** (inviolable rule 1).

## The finding

The source file is **not** one corpus. It is two, concatenated:

{md(reg_tab)}

Region **{B}** is **{n_b:,} of {int(a_row["n"]) + n_b:,} rows — {pct_b:.0f}% of the
corpus.** It carries a signature no organically collected comment thread
produces: **{b_row["danda_%"]:.1f}%** of its rows are দাঁড়ি-terminated against
{a_row["danda_%"]:.1f}% in region {A}, **{b_row["first_person_%"]:.1f}%** contain a
first-person pronoun against {a_row["first_person_%"]:.1f}%, and it draws
**{b_row["types_per_1k_tokens"]:.0f}** word types per 1,000 tokens against
{a_row["types_per_1k_tokens"]:.0f}.

## Label composition — the giveaway

{md(comp, idx=True)}

**Region {A} contains no class-2 rows at all.** Every one of the 1,670 neutral
reviews sits in region {B}. That is why `s2b` read the split as a property of
class 2: the neutral class is perfectly nested inside the second corpus.

## The seam is sharp, not gradual

Rolling {cfg["rolling_window"]}-row mean of the দাঁড়ি rate across raw row order:

{md(trace)}

A gradual drift would suggest a changing population of commenters. A step
function over ~50 rows suggests two files pasted together.

## Per-run breakdown

Contiguous label runs of ≥ 50 rows. Note rows 3665–4330 and 3000–3664: **label 0
and label 1**, deep in region {B}, both carrying the region's signature rather
than their class's.

{md(run_tab)}

## How the cleaned corpus inherits it

{md(clean_comp, idx=True)}

## What this does to S2

The S2 clustering put **1,814** items in cluster 0 — 823 class-0, 979 class-1,
and only **12** class-2. Region {A} after cleaning holds **1,910** items — 948
class-0, 962 class-1, **0** class-2. Those two groups are close enough that the
obvious reading is that **cluster 0 is approximately region {A}**: the encoder
recovered which file a review came from.

This cannot be confirmed here, because `s2_pilot.py` does not persist cluster
assignments — the decisive number, `ARI(cluster_labels, region)`, requires a
re-run that saves them. **Until that is computed, the correspondence is
suggestive, not established.**

## Consequences

1. **Every result computed over the full corpus is confounded by this split**,
   including the S2 trap-check itself.
2. The RQ1 persona claim cannot rest on three-class structure that is
   substantially a two-corpus structure.
3. Provenance fact (c) — "bulk pull from Facebook groups and YouTube channels" —
   cannot describe region {B}. The collector's recollection (2026-07-30: "same
   way") is **inconsistent with the file's own layout**. This is not evidence of
   bad faith: there is no written collection log (fact (a)), the recollection is
   old, and a second source merged in at assembly time is easy to forget.
   `docs/protocol.md` already pre-committed that a computed test **supersedes**
   the recall-based provenance table where the two disagree.
4. **Region {A} is still a usable corpus**: {int(clean_comp.loc[A, "All"]):,}
   cleaned rows, organic register, two classes. Smaller and binary, but real.
"""


if __name__ == "__main__":
    raise SystemExit(main())
