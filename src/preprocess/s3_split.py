"""Freeze the G / R1 / R2 split. Runs ONCE, then never again.

    python -m src.preprocess.s3_split --config configs/s3_split.yaml

**This script refuses to overwrite an existing split map.** That is not
politeness — every result computed after a regeneration would be measured
against different data than every result computed before it, and nothing in the
pipeline would raise an error. `--i-am-recreating-the-split-and-i-know-why`
exists as a deliberate escape hatch and demands a written reason that is stored
inside the map.

Stratified on `Sentiment x region`. The pipeline asks for cluster-stratified
gold, but the full-corpus clustering turned out to identify which of the two
source corpora a review came from with 93.3% accuracy, and Gate G1 has not
settled K. Stratifying the gold set on a file seam would be worse than not
stratifying on clusters at all. See `configs/s3_split.yaml`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import stamp, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402


def stratified_take(df: pd.DataFrame, n: int, strata: list[str],
                    rng: np.random.Generator) -> pd.Index:
    """Take n rows, allocated across strata in proportion to their size.

    Largest-remainder allocation, so the parts sum to exactly n instead of
    drifting by a row or two after rounding -- a split that is 299 or 301 is a
    split someone will have to explain.
    """
    sizes = df.groupby(strata, observed=True).size()
    exact = sizes / sizes.sum() * n
    alloc = np.floor(exact).astype(int)
    short = n - alloc.sum()
    if short > 0:
        order = (exact - alloc).sort_values(ascending=False).index
        for key in list(order)[:short]:
            alloc[key] += 1

    picked = []
    for key, k in alloc.items():
        if k == 0:
            continue
        cell = df[(df[strata] == pd.Series(dict(zip(strata, key)))).all(axis=1)] \
            if len(strata) > 1 else df[df[strata[0]] == key]
        picked.append(cell.sample(n=int(k), random_state=int(
            rng.integers(0, 2**31))).index)
    return pd.Index(np.concatenate(picked)) if picked else pd.Index([])


def composition(df: pd.DataFrame, idx, strata) -> dict:
    sub = df.loc[idx]
    return {
        "n": int(len(sub)),
        "by_region": {str(k): int(v) for k, v in
                      sub[strata[1]].value_counts().sort_index().items()},
        "by_sentiment": {str(k): int(v) for k, v in
                         sub[strata[0]].value_counts().sort_index().items()},
        "by_stratum": {f"{a}|{b}": int(v) for (a, b), v in
                       sub.groupby(strata, observed=True).size().items()},
    }


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s3_split.yaml")
    ap.add_argument("--i-am-recreating-the-split-and-i-know-why", metavar="REASON",
                    default="", help="deliberate override; the reason is stored "
                                     "in the new map")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    cfg = yaml.safe_load((root / args.config).read_text(encoding="utf-8"))
    out = root / cfg["output"]
    override = getattr(args, "i_am_recreating_the_split_and_i_know_why")

    if out.exists() and not override:
        old = json.loads(out.read_text(encoding="utf-8"))
        sys.exit(
            f"{cfg['output']} already exists and is FROZEN.\n"
            f"  created: {old.get('_provenance', {}).get('timestamp_utc')}\n"
            f"  commit : {old.get('_provenance', {}).get('git_commit')}\n\n"
            "Every result computed after a regeneration would be measured "
            "against different data than every result before it, and nothing "
            "would raise an error. If you truly must, pass\n"
            "  --i-am-recreating-the-split-and-i-know-why \"<reason>\"\n"
            "and the reason is stored inside the new map."
        )

    src = root / cfg["input_assignments"]
    if not src.exists():
        sys.exit(f"{cfg['input_assignments']} not found -- run S2 first.")
    df = pd.read_csv(src)
    if len(df) != cfg["expected_n"]:
        raise AssertionError(
            f"{cfg['input_assignments']} has {len(df)} rows, expected "
            f"{cfg['expected_n']}. The near-duplicate threshold moved; the "
            "split must not be built on a different row set."
        )

    idc, lab, reg = cfg["id_col"], cfg["label_col"], cfg["region_col"]
    if df[idc].duplicated().any():
        raise AssertionError(f"{idc} is not unique")
    df = df.sort_values(idc, kind="mergesort").reset_index(drop=True)
    strata = [lab, reg]
    rng = np.random.default_rng(int(cfg["seed"]))

    g_idx = stratified_take(df, int(cfg["sizes"]["gold"]), strata, rng)
    rest = df.drop(index=g_idx)
    n_r1 = int(round(len(rest) * float(cfg["sizes"]["r1_fraction"])))
    r1_idx = stratified_take(rest, n_r1, strata, rng)
    r2_idx = rest.drop(index=r1_idx).index
    dev_idx = stratified_take(df.loc[r1_idx], int(cfg["sizes"]["dev_slice"]),
                              strata, rng)

    # --- invariants. Each of these has a specific way of silently ruining the
    # --- thesis, so each is asserted rather than assumed.
    sets = {"G": set(df.loc[g_idx, idc]), "R1": set(df.loc[r1_idx, idc]),
            "R2": set(df.loc[r2_idx, idc])}
    assert not sets["G"] & sets["R1"], "G leaks into R1 -- gold is no longer held out"
    assert not sets["G"] & sets["R2"], "G leaks into R2"
    assert not sets["R1"] & sets["R2"], "R1 leaks into R2 -- Verifier-B is contaminated"
    assert len(sets["G"] | sets["R1"] | sets["R2"]) == len(df), "rows lost"
    dev = set(df.loc[dev_idx, idc])
    assert dev <= sets["R1"], "the dev slice must come from R1 only"

    payload = {
        "_provenance": stamp(args.config, extra={
            "input": cfg["input_assignments"],
            "input_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
            "stratified_on": strata,
            "recreated_reason": override or None,
        }),
        "_contract": {
            "G": "EVAL ONLY. Never enters training, the RAG index, prompts, or "
                 "threshold tuning.",
            "R1": "Verifier-A + RAG index + dev slice.",
            "R2": "Verifier-B only. Never enters the loop -- this wall is the "
                  "Goodhart test.",
            "dev": "Subset of R1. Threshold sweep only.",
            "frozen": "Committed to git. Never regenerate.",
        },
        "counts": {k: len(v) for k, v in sets.items()} | {"dev": len(dev)},
        "composition": {
            "G": composition(df, g_idx, strata),
            "R1": composition(df, r1_idx, strata),
            "R2": composition(df, r2_idx, strata),
            "dev": composition(df, dev_idx, strata),
        },
        "G": sorted(sets["G"]),
        "R1": sorted(sets["R1"]),
        "R2": sorted(sets["R2"]),
        "dev": sorted(dev),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    write_text_lf(out, json.dumps(payload, ensure_ascii=False, indent=1) + "\n")

    print(f"wrote {cfg['output']}")
    for k in ("G", "R1", "R2", "dev"):
        c = payload["composition"][k]
        print(f"  {k:4s} n={c['n']:<5} region={c['by_region']} "
              f"sentiment={c['by_sentiment']}")
    print("\nFROZEN. Commit it now. This script will refuse to overwrite it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
