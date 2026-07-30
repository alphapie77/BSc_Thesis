"""Validate the Bangla plot collection, and assign the dev/eval split once.

Two commands, and the separation between them matters:

    python -m src.preprocess.plots_check                 # check progress + errors
    python -m src.preprocess.plots_check --assign-split  # ONCE, at 130 plots

**Why the split is assigned at the end, not as you collect.** If `split` were
filled in row by row, the first 30 plots would become the dev set -- and the
first 30 films anyone collects are the ones they thought of first: the famous
ones, the ones with long Wikipedia articles. The dev set would then differ
systematically from the eval set, and every threshold tuned on dev would be
tuned on easy cases. Collect all 130 blind, then split once with seed 42.

`--assign-split` refuses to run twice. The assignment is committed to git and is
as frozen as the review split map: the eval-100 is the only held-out element the
whole evaluation rests on.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import NEWLINE  # noqa: E402
from src.common.seed import set_seed  # noqa: E402

PLOTS = Path("data/plots/plots_bn.csv")
TARGET, N_DEV, N_EVAL = 130, 30, 100
BANGLA = re.compile(r"[ঀ-৿]")
URL = re.compile(r"^https?://\S+$")
REQUIRED = ["plot_id", "language", "title_bn", "synopsis", "source_url",
            "source_type", "collected_date"]


def sentences(text: str) -> int:
    """Count sentences by দাঁড়ি, tolerating a missing final one."""
    parts = [p for p in re.split(r"[।!?]", str(text)) if p.strip()]
    return len(parts)


def check(df: pd.DataFrame) -> list[str]:
    errs = []

    def bad(mask, msg):
        for pid in df.loc[mask, "plot_id"].tolist():
            errs.append(f"{pid}: {msg}")

    for col in REQUIRED:
        if col not in df.columns:
            return [f"missing column: {col}"]
        bad(df[col].isna() | (df[col].astype(str).str.strip() == ""),
            f"empty {col}")

    dup = df["plot_id"].duplicated(keep=False)
    bad(dup, "duplicate plot_id")

    # Same film entered twice under different ids -- easy to do across sessions.
    for col in ("title_bn", "synopsis"):
        d = df[col].astype(str).str.strip().str.lower()
        bad(d.duplicated(keep=False) & (d != ""), f"duplicate {col}")

    bad(~df["synopsis"].astype(str).apply(lambda s: bool(BANGLA.search(s))),
        "synopsis has no Bangla characters")

    # source_url is the one field that cannot be reconstructed later. Provenance
    # fact (c) is what an unrecorded source costs; do not repeat it here.
    bad(~df["source_url"].astype(str).apply(lambda s: bool(URL.match(s.strip()))),
        "source_url is not a URL")
    bad(df["source_url"].astype(str).str.strip().duplicated(keep=False),
        "duplicate source_url")

    n = df["synopsis"].astype(str).apply(sentences)
    bad(n < 2, "synopsis under 2 sentences -- too thin to generate from")
    bad(n > 12, "synopsis over 12 sentences -- summarise, do not paste the article")

    return errs


def report(df: pd.DataFrame) -> int:
    errs = check(df) if len(df) else []
    done = len(df)
    print(f"plots collected: {done} / {TARGET}")
    if done < TARGET:
        left = TARGET - done
        print(f"  {left} to go  ->  {left / 5:.0f} more days at 5/day")
    bar = int(40 * done / TARGET)
    print("  [" + "#" * bar + "." * (40 - bar) + "]")

    if "source_type" in df.columns and done:
        print("\nby source:")
        for k, v in df["source_type"].value_counts().items():
            print(f"  {k:20s} {v}")

    if "split" in df.columns and df["split"].notna().any() \
            and (df["split"].astype(str).str.strip() != "").any():
        print("\nsplit assigned:")
        for k, v in df["split"].value_counts().items():
            print(f"  {k:20s} {v}")
    elif done >= TARGET:
        print(f"\n{TARGET} reached -- run with --assign-split to freeze "
              f"{N_DEV} dev / {N_EVAL} eval.")

    if errs:
        print(f"\n{len(errs)} problem(s):")
        for e in errs[:25]:
            print(f"  - {e}")
        if len(errs) > 25:
            print(f"  ... and {len(errs) - 25} more")
        return 1
    if done:
        print("\nno problems.")
    return 0


def assign_split(df: pd.DataFrame, root: Path) -> int:
    if len(df) != TARGET:
        sys.exit(f"need exactly {TARGET} plots to split, found {len(df)}.")
    if (df["split"].astype(str).str.strip() != "").any():
        sys.exit(
            "split is already assigned. It is frozen on purpose -- the eval-100 "
            "is the only held-out element of the evaluation. Refusing to "
            "reassign."
        )
    errs = check(df)
    if errs:
        sys.exit(f"{len(errs)} validation problem(s); fix them before splitting.")

    set_seed()
    shuffled = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    shuffled["split"] = ["dev"] * N_DEV + ["eval"] * N_EVAL
    out = shuffled.sort_values("plot_id").reset_index(drop=True)
    out.to_csv(root / PLOTS, index=False, encoding="utf-8",
               lineterminator=NEWLINE)
    print(f"assigned {N_DEV} dev / {N_EVAL} eval with seed 42 and wrote {PLOTS}.")
    print("Commit this now. It is frozen from here on.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--assign-split", action="store_true")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    path = root / PLOTS
    if not path.exists():
        sys.exit(f"{PLOTS} not found. Copy data/plots/plots_bn_template.csv to it.")

    df = pd.read_csv(path, dtype=str).fillna("")
    df = df[df["plot_id"].astype(str).str.strip() != ""]

    if args.assign_split:
        return assign_split(df, root)
    return report(df)


if __name__ == "__main__":
    raise SystemExit(main())
