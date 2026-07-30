"""S2 THRESHOLD AUDIT -- build a blinded review sheet for the 0.90 vs 0.95 choice.

The S2 sensitivity curve is not constant. At t = 0.90 the trap-check lands in
Band 2; at 0.95 and 0.98 in Band 1. The gap is ~220 extra rows removed. Whether
0.90 is defensible turns on whether those extra removals are genuine
near-duplicates or merely *similar* short reviews -- a question about Bangla
text, not about ARI.

**The sheet is blinded on purpose.** It carries no cosine, no threshold, and no
marking of which pairs are controls. An annotator who can see that a pair sits
at 0.94 is no longer judging whether it is a duplicate; they are judging whether
0.94 sounds high. Control pairs from outside the contested band are shuffled in
so the annotator's own standard can be checked: if pairs at >= 0.98 are not
called duplicates either, the disagreement is about the definition of
"duplicate", not about where to put the threshold.

**This script decides nothing.** It writes an empty `verdict` column. The
judgement is recorded by hand, and the key is not opened until it is filled.

Run:
    python -m src.cluster.s2_audit_pairs --config configs/s2_audit.yaml
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import NEWLINE, stamp  # noqa: E402
from src.common.seed import set_seed  # noqa: E402

#: Columns the annotator fills. Kept deliberately small -- a long form invites
#: skimming, and this judgement is the whole point of the exercise.
VERDICT_COL = "is_duplicate"
NOTE_COL = "note"

VERDICT_HELP = (
    "duplicate / not_duplicate / unsure -- 'duplicate' means the two texts say "
    "the same thing in the same words, such that keeping both would double-count "
    "one opinion. Two different people making the same short generic comment "
    "IS a duplicate for this purpose. Two texts that merely share a topic or a "
    "sentiment are NOT."
)


def load_pairs(cfg, repo_root: Path) -> pd.DataFrame:
    path = repo_root / cfg["input_pairs_csv"]
    if not path.exists():
        raise SystemExit(
            f"{path} not found.\n"
            "It is written by src/cluster/s2_pilot.py and is gitignored, so it "
            "does not arrive with a clone -- bring it back from the Kaggle run "
            "(it is in s2_outputs.zip)."
        )
    df = pd.read_csv(path)
    required = {"id_kept_side", "id_other_side", "cosine",
                "text_kept_side", "text_other_side"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"{path} is missing columns: {sorted(missing)}")
    return df


def stratified_sample(df: pd.DataFrame, lo: float, hi: float, n: int,
                      strata: int, rng: np.random.Generator) -> pd.DataFrame:
    """Draw ~n pairs spread evenly across [lo, hi).

    Even spread matters: the density of near-duplicate cosines is not uniform,
    and a plain random draw would over-represent whichever end is denser. A
    verdict that flips partway through the band is invisible in a sample taken
    only from its edge.
    """
    band = df[(df["cosine"] >= lo) & (df["cosine"] < hi)]
    if band.empty:
        raise SystemExit(
            f"No pairs in [{lo}, {hi}). Nothing is in dispute between those "
            "thresholds, which would itself be worth knowing -- check the "
            "sensitivity table in results/s2_pilot_ari_trapcheck.md."
        )

    edges = np.linspace(lo, hi, strata + 1)
    per = max(1, n // strata)
    picked = []
    for k in range(strata):
        s_lo, s_hi = edges[k], edges[k + 1]
        sub = band[(band["cosine"] >= s_lo) & (band["cosine"] < s_hi)]
        if sub.empty:
            continue
        take = min(per, len(sub))
        picked.append(sub.sample(n=take, random_state=int(rng.integers(0, 2**31))))

    out = pd.concat(picked) if picked else band.head(0)

    # Top up from the whole band if thin strata left us short of n.
    if len(out) < n:
        rest = band.drop(index=out.index)
        if len(rest):
            take = min(n - len(out), len(rest))
            out = pd.concat(
                [out, rest.sample(n=take, random_state=int(rng.integers(0, 2**31)))]
            )
    return out


def controls(df: pd.DataFrame, cfg, rng: np.random.Generator) -> pd.DataFrame:
    """Pairs from outside the contested band, to calibrate the annotator."""
    cc = cfg["controls"]
    lo = float(cfg["band"]["lo"])
    high = df[df["cosine"] >= 0.98]
    low = df[(df["cosine"] >= lo) & (df["cosine"] < lo + 0.01)]

    out = []
    for sub, k, tag in ((high, cc["n_high"], "control_high"),
                        (low, cc["n_low"], "control_low")):
        if len(sub) and k:
            picked = sub.sample(n=min(int(k), len(sub)),
                                random_state=int(rng.integers(0, 2**31))).copy()
            picked["_role"] = tag
            out.append(picked)
    return pd.concat(out) if out else df.head(0).assign(_role=[])


def main() -> int:
    set_seed()

    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s2_audit.yaml")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    cfg_path = Path(args.config)
    cfg = yaml.safe_load((repo_root / cfg_path).read_text(encoding="utf-8"))

    rng = np.random.default_rng(int(cfg["seed"]))
    pairs = load_pairs(cfg, repo_root)

    lo, hi = float(cfg["band"]["lo"]), float(cfg["band"]["hi"])
    sc = cfg["sample"]

    contested = stratified_sample(
        pairs, lo, hi, int(sc["n"]), int(sc["strata"]), rng
    ).copy()
    contested["_role"] = "contested"

    ctrl = controls(pairs, cfg, rng)

    sheet = pd.concat([contested, ctrl]).drop_duplicates(
        subset=["id_kept_side", "id_other_side"]
    )
    # Shuffle so role is not inferable from position. The annotator must not be
    # able to tell a control from a contested pair.
    sheet = sheet.sample(frac=1.0, random_state=int(rng.integers(0, 2**31)))
    sheet = sheet.reset_index(drop=True)
    sheet.insert(0, "item", [f"A{i:03d}" for i in range(1, len(sheet) + 1)])

    # --- the blinded sheet: text only -------------------------------------
    review = pd.DataFrame({
        "item": sheet["item"],
        "text_a": sheet["text_kept_side"],
        "text_b": sheet["text_other_side"],
        VERDICT_COL: "",
        NOTE_COL: "",
    })
    out_sheet = repo_root / cfg["outputs"]["review_sheet_csv"]
    out_sheet.parent.mkdir(parents=True, exist_ok=True)
    review.to_csv(out_sheet, index=False, encoding="utf-8", lineterminator=NEWLINE)

    # --- the key: everything the sheet deliberately hides ------------------
    prov = stamp(cfg_path.as_posix())
    key = pd.DataFrame({
        "item": sheet["item"],
        "role": sheet["_role"],
        "cosine": sheet["cosine"].round(6),
        "id_kept_side": sheet["id_kept_side"],
        "id_other_side": sheet["id_other_side"],
    })
    out_key = repo_root / cfg["outputs"]["key_csv"]
    key.to_csv(out_key, index=False, encoding="utf-8", lineterminator=NEWLINE)

    n_band = int(((pairs["cosine"] >= lo) & (pairs["cosine"] < hi)).sum())
    print(f"pairs in the contested band [{lo}, {hi}): {n_band}")
    print(f"sheet: {len(review)} items "
          f"({(sheet['_role'] == 'contested').sum()} contested, "
          f"{(sheet['_role'] != 'contested').sum()} control)")
    print(f"wrote {out_sheet}  <- annotate this ({VERDICT_COL}: {VERDICT_HELP})")
    print(f"wrote {out_key}    <- DO NOT open until the sheet is filled")
    print(f"provenance: {prov['timestamp_utc']} @ {prov['git_commit']}")
    print("\nThis script decided nothing. The threshold decision is recorded by "
          "hand in docs/lab_notebook.md, with this sheet as its evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
