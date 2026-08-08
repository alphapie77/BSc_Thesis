"""Build the RQ1-H intrusion sheets — human validation, attempt 2.

    python -m src.annotate.intrusion_build --config configs/intrusion.yaml

Each set is four reviews: three from one cluster and one intruder from the
other. The annotator is asked only **which one does not belong** — no scale, no
rubric, and crucially **no named construct**, which is the second of the two
failures in attempt 1 and the one that went undiagnosed at the time.

**Length matching is the load-bearing design choice.** Every review in a set is
within `max_word_span` words of every other, so RQ1-D's binding condition —
annotators must not be able to succeed by reading length — holds **by
construction**. Attempt 1 could only measure that afterwards; here there is no
length signal to read.

Items are drawn from region A **excluding G-300**, whose items both annotators
have already seen. The clustering ran on all 1,897 region-A rows, so G was never
held out from it and excluding it costs nothing.

Interpretation is pre-registered in `docs/protocol.md`, RQ1-H, written before
this file existed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import NEWLINE, stamp, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402

FORCE = "--i-am-rebuilding-sheets-and-no-one-has-started"


def build_sets(df: pd.DataFrame, cfg, rng) -> list[dict]:
    """Length-matched intrusion sets, balanced across which cluster is the majority.

    Sampling is by length band rather than globally: a set is only valid if all
    four reviews sit within `max_word_span` words of one another, and the
    cheapest way to guarantee that is to draw all four from the same narrow
    window. Windows with too few items on either side are skipped rather than
    padded, so a set is never completed with a review that breaks the match.
    """
    ic = cfg["intrusion"]
    n_sets, span = int(ic["n_sets"]), int(ic["max_word_span"])
    size = int(ic["set_size"])
    lengths = sorted(df[cfg["length_col"]].unique())

    out, used = [], set()
    majorities = ([0] * (n_sets // 2) + [1] * (n_sets - n_sets // 2)
                  if ic["balance"] else list(rng.integers(0, 2, n_sets)))
    rng.shuffle(majorities)

    for maj in majorities:
        placed = False
        for lo in rng.permutation(lengths):
            win = df[(df[cfg["length_col"]] >= lo)
                     & (df[cfg["length_col"]] <= lo + span)
                     & (~df[cfg["id_col"]].isin(used))]
            same = win[win[cfg["cluster_col"]] == maj]
            other = win[win[cfg["cluster_col"]] == 1 - maj]
            if len(same) < size - 1 or len(other) < 1:
                continue
            pick = same.sample(size - 1, random_state=int(rng.integers(0, 2**31)))
            intr = other.sample(1, random_state=int(rng.integers(0, 2**31)))
            rows = pd.concat([pick, intr]).sample(
                frac=1, random_state=int(rng.integers(0, 2**31)))
            used.update(rows[cfg["id_col"]])
            out.append({
                "majority_cluster": int(maj),
                "intruder_id": intr[cfg["id_col"]].iloc[0],
                "rows": rows,
            })
            placed = True
            break
        if not placed:
            break                      # no window can supply another valid set
    return out


def build_pairs(df: pd.DataFrame, cfg, rng, used: set) -> list[dict]:
    """Length-matched pairs, one review from each cluster. Gate B."""
    pc = cfg["pairwise"]
    span = int(pc["max_word_span"])
    out = []
    for _ in range(int(pc["n_pairs"])):
        placed = False
        for lo in rng.permutation(sorted(df[cfg["length_col"]].unique())):
            win = df[(df[cfg["length_col"]] >= lo)
                     & (df[cfg["length_col"]] <= lo + span)
                     & (~df[cfg["id_col"]].isin(used))]
            a = win[win[cfg["cluster_col"]] == 0]
            b = win[win[cfg["cluster_col"]] == 1]
            if len(a) < 1 or len(b) < 1:
                continue
            ra = a.sample(1, random_state=int(rng.integers(0, 2**31)))
            rb = b.sample(1, random_state=int(rng.integers(0, 2**31)))
            rows = pd.concat([ra, rb]).sample(
                frac=1, random_state=int(rng.integers(0, 2**31)))
            used.update(rows[cfg["id_col"]])
            out.append({"cluster1_id": rb[cfg["id_col"]].iloc[0], "rows": rows})
            placed = True
            break
        if not placed:
            break
    return out


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/intrusion.yaml")
    ap.add_argument(FORCE, action="store_true", dest="force")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    cfg_path = Path(args.config)
    cfg = yaml.safe_load((root / cfg_path).read_text(encoding="utf-8"))
    rng = np.random.default_rng(int(cfg["seed"]))

    asg = pd.read_csv(root / cfg["input_assignments"])
    txt = pd.read_csv(root / cfg["input_csv"])[[cfg["id_col"], cfg["text_col"]]]
    df = asg.merge(txt, on=cfg["id_col"], how="left")

    sm = json.loads((root / cfg["split_map"]).read_text(encoding="utf-8"))
    banned = set().union(*(set(sm[p]) for p in cfg["exclude_parts"]))
    before = len(df)
    df = df[~df[cfg["id_col"]].isin(banned)].reset_index(drop=True)
    print(f"region A: {before} rows, {before - len(df)} excluded "
          f"({', '.join(cfg['exclude_parts'])} — already seen in attempt 1), "
          f"{len(df)} available")

    out_dir = root / cfg["outputs"]["sheet_dir"]
    if out_dir.exists() and any(out_dir.glob("*.csv")) and not args.force:
        raise SystemExit(
            f"sheets already exist in {out_dir}. Rebuilding would change what an "
            f"already-answered row refers to. If nobody has started, pass {FORCE}."
        )
    out_dir.mkdir(parents=True, exist_ok=True)

    sets = build_sets(df, cfg, rng)
    if len(sets) < int(cfg["intrusion"]["n_sets"]):
        print(f"⚠️  only {len(sets)} of {cfg['intrusion']['n_sets']} sets could be "
              f"built under the length-matching constraint. This REDUCES POWER "
              f"and is reported, not worked around by relaxing the match.")
    used = {i for s in sets for i in s["rows"][cfg["id_col"]]}
    pairs = build_pairs(df, cfg, rng, used)

    mx = int(cfg["max_chars"])

    def clip(t):
        t = " ".join(str(t).split())
        return t if len(t) <= mx else t[:mx] + " …"

    # --- annotator sheets: option letters only, answer hidden ---------------
    irows, key_rows = [], []
    for si, s in enumerate(sets, 1):
        sid = f"S{si:03d}"
        for oi, (_, r) in enumerate(s["rows"].iterrows()):
            letter = "ABCD"[oi]
            irows.append({"set_id": sid, "option": letter,
                          "review": clip(r[cfg["text_col"]])})
            if r[cfg["id_col"]] == s["intruder_id"]:
                key_rows.append({"set_id": sid, "correct_option": letter,
                                 "intruder_id": s["intruder_id"],
                                 "majority_cluster": s["majority_cluster"],
                                 "word_span": int(s["rows"][cfg["length_col"]].max()
                                                  - s["rows"][cfg["length_col"]].min())})
    prows, pkey = [], []
    for pi, p in enumerate(pairs, 1):
        pid = f"P{pi:03d}"
        for oi, (_, r) in enumerate(p["rows"].iterrows()):
            letter = "AB"[oi]
            prows.append({"pair_id": pid, "option": letter,
                          "review": clip(r[cfg["text_col"]])})
            if r[cfg["id_col"]] == p["cluster1_id"]:
                pkey.append({"pair_id": pid, "cluster1_option": letter,
                             "cluster1_id": p["cluster1_id"],
                             "word_span": int(p["rows"][cfg["length_col"]].max()
                                              - p["rows"][cfg["length_col"]].min())})

    for who in cfg["annotators"]:
        a = pd.DataFrame(irows).pivot(index="set_id", columns="option",
                                      values="review").reset_index()
        a["answer"] = ""
        a.to_csv(out_dir / f"intrusion_{who}.csv", index=False,
                 encoding="utf-8-sig", lineterminator=NEWLINE)
        b = pd.DataFrame(prows).pivot(index="pair_id", columns="option",
                                      values="review").reset_index()
        b["answer"] = ""
        b.to_csv(out_dir / f"pairwise_{who}.csv", index=False,
                 encoding="utf-8-sig", lineterminator=NEWLINE)
        print(f"wrote {out_dir / f'intrusion_{who}.csv'} ({len(a)} sets)")
        print(f"wrote {out_dir / f'pairwise_{who}.csv'} ({len(b)} pairs)")

    key = root / cfg["outputs"]["key_csv"]
    pd.DataFrame(key_rows).to_csv(key, index=False, encoding="utf-8",
                                  lineterminator=NEWLINE)
    pd.DataFrame(pkey).to_csv(str(key).replace(".csv", "_pairwise.csv"),
                              index=False, encoding="utf-8",
                              lineterminator=NEWLINE)

    spans = [k["word_span"] for k in key_rows]
    print(f"\nwrote {key} (researchers only — do NOT send this)")
    print(f"length matching: max word span within a set = {max(spans)} "
          f"(limit {cfg['intrusion']['max_word_span']}), mean {np.mean(spans):.2f}")
    print(f"majority-cluster balance: "
          f"{dict(pd.Series([k['majority_cluster'] for k in key_rows]).value_counts())}")

    prov = stamp(cfg_path.as_posix())
    write_text_lf(out_dir / "README.md", f"""# Intrusion sheets — RQ1-H, attempt 2

Generated {prov['timestamp_utc']} · commit `{prov['git_commit']}` · seed {cfg['seed']}

## For annotators — the whole instruction

**`intrusion_<you>.csv`** — each row has four reviews (A, B, C, D). Three are
alike and one is the odd one out. Put **A, B, C or D** in the `answer` column.

**`pairwise_<you>.csv`** — each row has two reviews. Put **A** or **B** in
`answer` for whichever goes into **more specific detail about the film**.

That is the entire task. There is no scale, no rubric and no guideline to read.
Work alone; do not discuss any item with the other annotator.

## For the researcher

- `intrusion_key.csv` / `intrusion_key_pairwise.csv` hold the answers.
  **Never send these.**
- {len(sets)} sets, {len(pairs)} pairs. Every set is length-matched to within
  {cfg['intrusion']['max_word_span']} words, so **length cannot be the cue** —
  RQ1-D's condition is met by construction, not by measurement.
- Items exclude G-300, which both annotators saw in attempt 1.
- Chance is **0.25** for intrusion and **0.50** for pairwise. Bands are in
  `docs/protocol.md`, RQ1-H.
""")
    print("\nRead docs/protocol.md RQ1-H before any of this is answered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
