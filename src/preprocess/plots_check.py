"""Validate the Bangla plot collection, and assign the dev/eval split once.

Two commands, and the separation between them matters:

    python -m src.preprocess.plots_check                 # check progress + errors
    python -m src.preprocess.plots_check --assign-split  # ONCE, when done

**Why the split is assigned at the end, not as you collect.** If `split` were
filled in row by row, the first 30 plots would become the dev set -- and the
first 30 films anyone collects are the ones they thought of first: the famous
ones, the ones with long Wikipedia articles. The dev set would then differ
systematically from the eval set, and every threshold tuned on dev would be
tuned on easy cases. Collect the whole set blind, then split once with seed 42.

`--assign-split` refuses to run twice. The assignment is committed to git and is
as frozen as the review split map: the eval set is the only held-out element the
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

#: The pipeline spec asks for 130 = 30 dev + 100 eval. bn.wikipedia does not
#: have 130 Bangla-film articles carrying a usable plot section: the harvest
#: tops out at ~124 after person articles are excluded, and the only ways past
#: that were to relax the quality gate (admitting two-sentence plots) or to add
#: the language-neutral by-year categories (admitting Tamil and Hindi films).
#: Both trade the corpus's validity for an arbitrary round number.
#:
#: So the target follows the data. `N_DEV` is fixed at 30 because the dev slice
#: exists to tune the loop threshold and 30 is the smallest defensible number
#: for that; **eval takes whatever remains**. Losing a few eval plots costs a
#: little power in a bootstrap CI. Padding the set with thin or non-Bangla plots
#: would cost validity, which no amount of n buys back.
#:
#: Logged in docs/protocol.md (Deviations, 2026-07-31).
N_DEV = 30
MIN_EVAL = 80          # below this, stop and reconsider rather than proceed
TARGET = 130           # aspiration, not a gate -- reported against, not enforced
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
    if done:
        print(f"  would split {N_DEV} dev / {done - N_DEV} eval "
              f"(floor for eval is {MIN_EVAL})")
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
    elif done - N_DEV >= MIN_EVAL:
        print(f"\nEnough to split -- run with --assign-split to freeze "
              f"{N_DEV} dev / {done - N_DEV} eval.")

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
    n = len(df)
    n_eval = n - N_DEV
    if n_eval < MIN_EVAL:
        sys.exit(
            f"only {n} plots ({n_eval} would be eval, floor is {MIN_EVAL}).\n"
            "Harvest more before splitting. Do NOT relax the quality gate or add "
            "the by-year categories to get here -- both trade the corpus's "
            "validity for a number."
        )
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
    shuffled["split"] = ["dev"] * N_DEV + ["eval"] * n_eval
    out = shuffled.sort_values("plot_id").reset_index(drop=True)
    out.to_csv(root / PLOTS, index=False, encoding="utf-8",
               lineterminator=NEWLINE)
    print(f"assigned {N_DEV} dev / {n_eval} eval with seed 42 and wrote {PLOTS}.")
    if n != TARGET:
        print(f"NOTE: {n} plots, not the spec's {TARGET}. This is the logged\n              deviation (protocol.md, 2026-07-31) -- eval takes what remains\n              rather than the set being padded to a round number.")
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
