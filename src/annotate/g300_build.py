"""Build the blinded G-300 annotation sheets.

    python -m src.annotate.g300_build --config configs/g300.yaml

Produces one sheet per annotator plus a calibration sheet, all blinded, and a
**key** file that annotators never receive. Interpretation and procedure are
pre-registered in `docs/protocol.md`, RQ1-F; the rubric annotators actually read
is `docs/g300_annotation_guideline.md`.

**What blinding means here, concretely.** The sheets carry an opaque `item_id`
and the review text, and nothing else. No cluster, no K, no region, no
`Sentiment`, no word count, no `review_id` — `review_id` is ordered by position
in the source file, and position in the source file *is* the region variable
(fact (split)), so shipping it would hand over the confound the study controls
for. Order is shuffled once under the global seed, so nothing can be inferred
from where an item sits either.

**The sheets are written once and never rewritten.** Rebuilding after annotation
has begun would silently change what a filled row refers to, so the script
refuses to overwrite an existing sheet unless told to.
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


def main() -> int:
    set_seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/g300.yaml")
    ap.add_argument(FORCE, action="store_true", dest="force",
                    help="overwrite existing sheets. Only safe before anyone "
                         "has entered a single rating.")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    cfg_path = Path(args.config)
    cfg = yaml.safe_load((root / cfg_path).read_text(encoding="utf-8"))
    rng = np.random.default_rng(int(cfg["seed"]))

    sm = json.loads((root / cfg["split_map"]).read_text(encoding="utf-8"))
    g_ids, dev_ids = list(sm["G"]), list(sm["dev"])
    df = pd.read_csv(root / cfg["input_csv"])
    asg = pd.read_csv(root / cfg["assignments"])[
        ["review_id", "cluster_k2", "region", "n_words"]]

    out_dir = root / cfg["outputs"]["sheet_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(out_dir.glob("g300_sheet_*.csv"))
    if existing and not args.force:
        raise SystemExit(
            f"{len(existing)} sheet(s) already exist in {out_dir}:\n  "
            + "\n  ".join(p.name for p in existing)
            + f"\n\nRebuilding would change what an already-filled row refers "
              f"to. If genuinely nobody has started, pass {FORCE}."
        )

    def build(ids, prefix):
        sub = df[df[cfg["id_col"]].isin(set(ids))].copy()
        sub = sub.sort_values(cfg["id_col"], kind="mergesort").reset_index(drop=True)
        order = rng.permutation(len(sub))
        sub = sub.iloc[order].reset_index(drop=True)
        sub["item_id"] = [f"{prefix}{i + 1:03d}" for i in range(len(sub))]
        return sub

    # --- calibration: dev only, and never a guideline example ---------------
    excl = set(cfg["calibration"]["exclude_ids"])
    cal_pool = [i for i in dev_ids if i not in excl]
    dropped = len(dev_ids) - len(cal_pool)
    cal_ids = list(rng.choice(cal_pool, size=int(cfg["calibration"]["n"]),
                              replace=False))
    cal = build(cal_ids, "C")

    main_sheet = build(g_ids, "G")
    if len(main_sheet) != len(g_ids):
        raise AssertionError(
            f"{len(main_sheet)} of {len(g_ids)} G ids found in "
            f"{cfg['input_csv']}. The split map and the corpus disagree."
        )

    # --- what the annotators get: two columns, one of them blank ------------
    for who in cfg["annotators"]:
        for sheet, tag in ((cal, "calibration"), (main_sheet, "sheet")):
            blind = pd.DataFrame({
                "item_id": sheet["item_id"],
                "review": sheet[cfg["text_col"]].astype(str)
                          .map(lambda t: " ".join(t.split())),
                "rating": "",
                "note": "",
            })
            p = out_dir / f"g300_{tag}_{who}.csv"
            blind.to_csv(p, index=False, encoding="utf-8-sig",
                         lineterminator=NEWLINE)
            print(f"wrote {p}  ({len(blind)} items)")

    # utf-8-sig above is deliberate: Excel on Windows opens a plain UTF-8 CSV as
    # mojibake, and an annotator who cannot read the Bangla will not fill it in.

    # --- the key: researchers only ------------------------------------------
    key = main_sheet[["item_id", cfg["id_col"], cfg["label_col"]]].merge(
        asg, left_on=cfg["id_col"], right_on="review_id", how="left")
    key = key.drop(columns=["review_id"]) if "review_id" in key.columns \
        and cfg["id_col"] != "review_id" else key
    key_path = root / cfg["outputs"]["key_csv"]
    key.to_csv(key_path, index=False, encoding="utf-8", lineterminator=NEWLINE)

    in_a = int(key["cluster_k2"].notna().sum())
    comp = (key.dropna(subset=["cluster_k2"])
               .groupby(["cluster_k2", cfg["label_col"]]).size().to_dict())

    prov = stamp(cfg_path.as_posix())
    write_text_lf(out_dir / "README.md", f"""# G-300 annotation sheets — do not edit by hand

Generated {prov['timestamp_utc']} from commit `{prov['git_commit']}`, seed
{cfg['seed']}.

## For annotators

Read **`docs/g300_annotation_guideline.md`** first, all of it. Then:

1. `g300_calibration_<you>.csv` — 20 practice items. Both annotators do these
   **separately**, then discuss **once**. These do not count.
2. `g300_sheet_<you>.csv` — the 300 real items. **No discussion from here on**
   until both of you have finished.

Fill only the `rating` column (0–3) and optionally `note`. Do not reorder,
delete or add rows.

## For the researcher

- `g300_key.csv` maps `item_id` → `{cfg['id_col']}`, `{cfg['label_col']}`,
  `cluster_k2`, `region`, `n_words`. **It is not shipped to annotators.**
- Of the 300 items, **{in_a} are in region A** and therefore carry a K=2 label;
  Gate 2 runs on those. Composition (cluster, sentiment): {comp}
- Calibration drew from `dev` after excluding {dropped} id(s) quoted as worked
  examples in the guideline — an annotator who has just read the rubric would be
  recalling those, not judging them.
- Sheets are written in `utf-8-sig` so Excel on Windows renders Bangla instead
  of mojibake.
""")

    print(f"\nwrote {key_path}  (researchers only — do NOT send this)")
    print(f"region-A items in G-300: {in_a} of {len(key)}   composition {comp}")
    print(f"calibration: {cfg['calibration']['n']} from dev, "
          f"{dropped} guideline example(s) excluded")
    print("\nRead docs/protocol.md RQ1-F before any of this is annotated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
