"""S1 -- rule-based cleaning of the raw Bangla review file.

Reads `data/raw/` (never writes it) and produces exactly two files:
`data/cleaned/bn_clean.csv` and `results/s1_cleaning_log.json`.

The step order in `configs/s1_clean.yaml` IS the protocol -- the surviving row
count depends on it, because `normalize_whitespace` creates new exact duplicates
that `drop_exact_duplicates` then removes. Do not reorder.

What this step deliberately does NOT do:
  * no stemming, no stopword removal (rule 7 -- contextual encoders need
    natural text);
  * no character normalization of the stored text: whitespace only. NFC is used
    as a *comparison key* for near-identical duplicate detection and is never
    written back;
  * no near-duplicate (cosine >= 0.95) removal -- that needs LaBSE and is
    deferred to S2. So the count here is `n_after_rule_based_cleaning`, not the
    final `usable_n`.

`review_id` is assigned from the ORIGINAL raw row index before any row is
dropped, so an id always points at the same raw record. The split map
references these ids -- they must never be regenerated.

Run:  python -m src.preprocess.s1_clean --config configs/s1_clean.yaml
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import write_result  # noqa: E402
from src.common.seed import set_seed  # noqa: E402
from src.preprocess.s0_xray import resolve_input, word_count  # noqa: E402

#: Ids look like `bn_0042`. The `bn_` prefix is not decoration: a bare
#: zero-padded numeric string is silently coerced back to an int by pandas /
#: Excel on read, which would destroy the padding and break the frozen split
#: map. The prefix makes the column unambiguously textual.
ID_PREFIX = "bn_"

URL_RE = re.compile(r"(?:https?://|www\.)\S+", re.I)
HTML_RE = re.compile(r"<[^>]+>")
MENTION_RE = re.compile(r"@\w+")


def make_review_id(raw_index: int, width: int) -> str:
    return f"{ID_PREFIX}{raw_index:0{width}d}"


def norm_key(text: str) -> str:
    """Comparison key for normalized-duplicate detection. Never stored."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", str(text))).strip()


# --- The six steps. Each returns (new_df, info_dict). ------------------------
# A step either drops rows or edits text, never both, so the log is unambiguous.

def step_drop_null(df, cfg):
    text, label = df[cfg["text_col"]], df[cfg["label_col"]]
    bad = text.isna() | text.astype(str).str.strip().eq("") | label.isna()
    return df[~bad].copy(), {
        "rows_dropped": int(bad.sum()),
        "detail": {
            "missing_or_blank_text": int(
                (text.isna() | text.astype(str).str.strip().eq("")).sum()
            ),
            "missing_label": int(label.isna().sum()),
        },
    }


def step_strip_url_html_mentions(df, cfg):
    col = cfg["text_col"]
    before = df[col]
    after = before.str.replace(URL_RE, " ", regex=True)
    after = after.str.replace(HTML_RE, " ", regex=True)
    after = after.str.replace(MENTION_RE, " ", regex=True)
    df = df.copy()
    df[col] = after
    return df, {
        "rows_dropped": 0,
        "rows_text_modified": int((before != after).sum()),
        "detail": {
            "rows_matching_url": int(before.str.contains(URL_RE).sum()),
            "rows_matching_html": int(before.str.contains(HTML_RE).sum()),
            "rows_matching_mention": int(before.str.contains(MENTION_RE).sum()),
        },
    }


def step_normalize_whitespace(df, cfg):
    col = cfg["text_col"]
    before = df[col]
    after = before.str.replace(r"\s+", " ", regex=True).str.strip()
    df = df.copy()
    df[col] = after
    return df, {
        "rows_dropped": 0,
        "rows_text_modified": int((before != after).sum()),
        "detail": {"note": "whitespace only -- no character normalization"},
    }


def step_drop_exact_duplicates(df, cfg):
    dup = df[cfg["text_col"]].duplicated(keep="first")
    return df[~dup].copy(), {
        "rows_dropped": int(dup.sum()),
        "detail": {"key": "raw string equality, keep first occurrence"},
    }


def step_drop_normalized_duplicates(df, cfg):
    dup = df[cfg["text_col"]].map(norm_key).duplicated(keep="first")
    return df[~dup].copy(), {
        "rows_dropped": int(dup.sum()),
        "detail": {
            "key": "NFC + whitespace-collapse + strip, keep first occurrence",
            "note": "comparison key only; stored text is unchanged",
        },
    }


def step_drop_short(df, cfg):
    short = df[cfg["text_col"]].map(word_count) < cfg["min_words"]
    return df[~short].copy(), {
        "rows_dropped": int(short.sum()),
        "detail": {"min_words": cfg["min_words"], "tokenizer": "str.split()"},
    }


STEPS = {
    "drop_null": step_drop_null,
    "strip_url_html_mentions": step_strip_url_html_mentions,
    "normalize_whitespace": step_normalize_whitespace,
    "drop_exact_duplicates": step_drop_exact_duplicates,
    "drop_normalized_duplicates": step_drop_normalized_duplicates,
    "drop_short": step_drop_short,
}

EXPECTED_FINAL_N = 4730


def main() -> int:
    set_seed()

    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s1_clean.yaml")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    cfg_path = Path(args.config)
    cfg = yaml.safe_load((repo_root / cfg_path).read_text(encoding="utf-8"))

    for flag in ("stemming", "stopword_removal"):
        if cfg.get(flag):
            raise ValueError(f"{flag}=true violates inviolable rule 7; refusing to run.")

    input_path = resolve_input(cfg["input_xlsx"], repo_root)
    df = pd.read_excel(input_path, sheet_name=0)
    n_raw = len(df)

    # Ids first, from the raw row index, before anything is dropped.
    width = len(str(n_raw - 1))
    df.insert(0, "review_id", [make_review_id(i, width) for i in range(n_raw)])
    if df["review_id"].duplicated().any():
        raise AssertionError("review_id is not unique")

    log_steps = [{"step": "load_raw", "rows_after": n_raw, "rows_dropped": 0}]
    for name in cfg["steps"]:
        if name not in STEPS:
            raise KeyError(f"Unknown step {name!r}; known: {sorted(STEPS)}")
        before_n = len(df)
        df, info = STEPS[name](df, cfg)
        entry = {"step": name, "rows_before": before_n, "rows_after": len(df), **info}
        if before_n - len(df) != info["rows_dropped"]:
            raise AssertionError(f"step {name}: reported drops != actual row delta")
        log_steps.append(entry)

    df[cfg["label_col"]] = df[cfg["label_col"]].astype(int)

    final_n = len(df)
    if final_n != EXPECTED_FINAL_N:
        raise AssertionError(
            f"n_after_rule_based_cleaning = {final_n}, expected {EXPECTED_FINAL_N}. "
            "Either the step order in the config changed or the raw file did. "
            "Investigate before accepting this number -- do not edit the assert."
        )

    # Per-class drop accounting. Computed, not asserted: the raw distribution is
    # re-read from the raw label column so the two distributions are directly
    # comparable, and the unlabelled row is held out of the per-class arithmetic
    # because it belongs to no class.
    raw_labels = pd.read_excel(input_path, sheet_name=0)[cfg["label_col"]]
    raw_dist = {
        int(k): int(v)
        for k, v in raw_labels.dropna().astype(int).value_counts().sort_index().items()
    }
    post_dist = {
        int(k): int(v)
        for k, v in df[cfg["label_col"]].value_counts().sort_index().items()
    }
    per_class_drops = {k: raw_dist[k] - post_dist.get(k, 0) for k in sorted(raw_dist)}
    n_unlabelled = int(raw_labels.isna().sum())
    total_dropped = n_raw - final_n
    if sum(per_class_drops.values()) + n_unlabelled != total_dropped:
        raise AssertionError(
            f"per-class drops {per_class_drops} + {n_unlabelled} unlabelled "
            f"!= total dropped {total_dropped}"
        )

    out_csv = repo_root / cfg["outputs"]["cleaned_csv"]
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False, encoding="utf-8")

    write_result(
        {
            "input_xlsx": input_path.relative_to(repo_root).as_posix(),
            "seed": cfg["seed"],
            "n_raw": n_raw,
            "step_order": list(cfg["steps"]),
            "steps": log_steps,
            "n_after_rule_based_cleaning": final_n,
            "expected_final_n": EXPECTED_FINAL_N,
            "class_balance": {
                "label_distribution_raw": raw_dist,
                "label_distribution_post_clean": post_dist,
                "per_class_drops": per_class_drops,
                "per_class_drops_sum": sum(per_class_drops.values()),
                "unlabelled_rows_dropped": n_unlabelled,
                "total_rows_dropped": total_dropped,
                "note": (
                    f"Per-class drops sum to {sum(per_class_drops.values())}, not "
                    f"{total_dropped}. The remaining {n_unlabelled} dropped row has a "
                    "missing Sentiment label and therefore belongs to no class, so it "
                    "cannot appear in any per-class count. "
                    f"{sum(per_class_drops.values())} + {n_unlabelled} = "
                    f"{total_dropped}."
                ),
                "balance_note": (
                    "The raw file is curated to near-uniform balance; cleaning breaks "
                    "it. Drops concentrate in class 0. Downstream steps must not "
                    "assume a balanced set after S1."
                ),
            },
            "review_id": {
                "format": f"{ID_PREFIX}<raw_row_index zero-padded to {width}>",
                "derived_from": "0-based row index of the raw xlsx, pre-drop",
                "n_unique": int(df["review_id"].nunique()),
                "first": df["review_id"].iloc[0],
                "last": df["review_id"].iloc[-1],
                "frozen": "referenced by the split map -- never regenerate",
                "read_with": "pd.read_csv(..., dtype={'review_id': str})",
            },
            "columns_written": list(df.columns),
            "not_done_here": {
                "near_duplicate_cosine_threshold": cfg[
                    "near_duplicate_cosine_threshold"
                ],
                "near_duplicate_stage": cfg["near_duplicate_stage"],
                "stemming": cfg["stemming"],
                "stopword_removal": cfg["stopword_removal"],
                "note": (
                    "final usable_n is pending near-duplicate removal in S2; "
                    f"{final_n} is the rule-based count only"
                ),
            },
        },
        repo_root / cfg["outputs"]["log_json"],
        config_path=cfg_path.as_posix(),
    )

    print(f"wrote {out_csv} ({final_n} rows)")
    print(f"wrote {repo_root / cfg['outputs']['log_json']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
