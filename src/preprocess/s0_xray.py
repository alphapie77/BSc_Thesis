"""S0 -- X-ray of the raw xlsx.

Verification only. This script READS `data/raw/` and writes exactly one file:
the markdown report named by `output_report` in the config. It does not clean,
filter, or write any dataset. Every quantity under `claims:` in the config is
recomputed independently here and compared to the claimed value.

Run:  python -m src.preprocess.s0_xray --config configs/s0_xray.yaml
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import stamp  # noqa: E402
from src.common.seed import set_seed  # noqa: E402

# --- Measurement definitions (stated in the report so they are auditable) ----

#: A "word" is a whitespace-delimited token. No stemming, no stopword removal,
#: no tokenizer -- rule 7 of CLAUDE.md.
def word_count(text) -> int:
    if not isinstance(text, str):
        return 0
    return len(text.split())


#: Normalization used ONLY for the normalized-duplicate count. It is never
#: applied to the data itself. Unicode NFC + whitespace collapse + strip.
#: No transliteration, no character folding -- rule in CLAUDE.md.
def normalize_for_dup(text) -> str:
    if not isinstance(text, str):
        return ""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"  # supplemental symbols & pictographs
    "\U0001FA00-\U0001FAFF"
    "\U00002600-\U000026FF"  # misc symbols
    "\U00002700-\U000027BF"  # dingbats
    "\U0001F1E6-\U0001F1FF"  # regional indicators
    "\U00002B00-\U00002BFF"
    "]"
)

#: U+FE0F on its own is NOT an emoji -- it is a modifier. In this file it
#: appears orphaned after Bangla letters, i.e. residue left behind when the
#: publisher stripped the emoji. Counted separately as evidence, never as emoji.
VS16 = "️"

URL_MENTION_RE = re.compile(r"(https?://|www\.|\S+\.(?:com|net|org|bd)\b|@\w+)", re.I)


def has_emoji(text) -> bool:
    return isinstance(text, str) and bool(EMOJI_RE.search(text))


def has_url_or_mention(text) -> bool:
    return isinstance(text, str) and bool(URL_MENTION_RE.search(text))


def resolve_input(path_str: str, repo_root: Path) -> Path:
    """The config spells the filename with underscores; the file on disk uses
    spaces. Try the literal path first, then the space/underscore variant, then
    glob the directory. Fail loudly rather than guess wrong."""
    p = repo_root / path_str
    if p.exists():
        return p
    alt = p.with_name(p.name.replace("_", " "))
    if alt.exists():
        return alt
    matches = sorted(p.parent.glob("*.xlsx"))
    if len(matches) == 1:
        return matches[0]
    raise FileNotFoundError(
        f"Could not resolve input_xlsx={path_str!r}. Tried {p}, {alt}, "
        f"and glob of {p.parent} (found {len(matches)} xlsx)."
    )


def compute(df: pd.DataFrame, text_col: str, label_col: str) -> dict:
    """Independently compute every claimed quantity. Returns {name: value}."""
    text = df[text_col]
    label = df[label_col]

    # Null = row where the text is missing/blank OR the label is missing.
    text_null = text.isna() | text.astype(str).str.strip().eq("")
    label_null = label.isna()
    null_rows = (text_null | label_null)

    words = text.map(word_count)

    exact_dups = int(text.duplicated(keep="first").sum())
    norm_dups = int(text.map(normalize_for_dup).duplicated(keep="first").sum())

    short = (words < 3) & ~text_null

    # Usable = rows surviving the S1 drops: null, exact duplicate, <3 words.
    drop = null_rows | text.duplicated(keep="first") | (words < 3)
    usable_n = int((~drop).sum())

    label_counts = (
        label.dropna().astype(int).value_counts().sort_index().to_dict()
    )

    nonnull_words = words[~text_null]

    return {
        "n_rows": int(len(df)),
        "label_counts": {int(k): int(v) for k, v in label_counts.items()},
        "exact_duplicates": exact_dups,
        "normalized_duplicates": norm_dups,
        "short_reviews_lt3_words": int(short.sum()),
        "null_rows": int(null_rows.sum()),
        "usable_n": usable_n,
        "median_words": float(nonnull_words.median()),
        "max_words": int(nonnull_words.max()),
        "emoji_rows": int(text.map(has_emoji).sum()),
        "url_or_mention_rows": int(text.map(has_url_or_mention).sum()),
    }


def drop_sets(df: pd.DataFrame, text_col: str, label_col: str, dup_mode: str):
    """The three S1 drop sets as boolean masks, under one duplicate definition.

    `dup_mode` is "exact" (raw string equality) or "normalized" (NFC +
    whitespace collapse + strip). Set definitions match the claim table:
    SHORT excludes null-text rows so it stays the reported 72 rather than
    silently absorbing the missing-text row.
    """
    text = df[text_col]
    text_null = text.isna() | text.astype(str).str.strip().eq("")
    key = text if dup_mode == "exact" else text.map(normalize_for_dup)
    words = text.map(word_count)
    return {
        "NULL": text_null | df[label_col].isna(),
        "SHORT": (words < 3) & ~text_null,
        "DUP": key.duplicated(keep="first"),
    }


def decompose(df: pd.DataFrame, text_col: str, label_col: str, dup_mode: str) -> dict:
    """Inclusion-exclusion breakdown of the S1 drop union."""
    s = drop_sets(df, text_col, label_col, dup_mode)
    names = ["NULL", "SHORT", "DUP"]
    union = s["NULL"] | s["SHORT"] | s["DUP"]
    n = len(df)
    return {
        "dup_mode": dup_mode,
        "sizes": {k: int(s[k].sum()) for k in names},
        "pairwise": {
            f"{a} & {b}": int((s[a] & s[b]).sum())
            for i, a in enumerate(names)
            for b in names[i + 1:]
        },
        "triple": int((s["NULL"] & s["SHORT"] & s["DUP"]).sum()),
        "naive_sum": sum(int(s[k].sum()) for k in names),
        "union": int(union.sum()),
        "usable_n": n - int(union.sum()),
        "n_rows": n,
    }


def context(df: pd.DataFrame, text_col: str, label_col: str) -> dict:
    """Uncontested descriptive numbers -- reported, but not claim-checked."""
    text = df[text_col]
    words = text.map(word_count)
    nn = words[text.notna()]
    per_label = (
        df.assign(_w=words)
        .dropna(subset=[label_col])
        .groupby(df[label_col].dropna().astype(int))["_w"]
        .mean()
        .round(2)
        .to_dict()
    )
    text_null = text.isna() | text.astype(str).str.strip().eq("")
    dup = text.duplicated(keep="first")
    short = words < 3
    return {
        "columns": list(df.columns),
        "sheet_shape": f"{df.shape[0]} rows x {df.shape[1]} cols",
        "mean_words": round(float(nn.mean()), 2),
        "min_words": int(nn.min()),
        "reviews_ge_50_words": int((nn >= 50).sum()),
        "mean_words_by_label": {int(k): float(v) for k, v in per_label.items()},
        "rows_with_missing_text": int(text_null.sum()),
        "rows_with_missing_label": int(df[label_col].isna().sum()),
        "short_rows_that_are_also_duplicates": int((short & dup).sum()),
        "orphan_vs16_rows": int(
            text.map(lambda s: isinstance(s, str) and VS16 in s).sum()
        ),
    }


def fmt(v) -> str:
    if isinstance(v, dict):
        return " / ".join(f"{k}:{v[k]}" for k in sorted(v))
    if isinstance(v, float):
        return f"{v:g}"
    return str(v)


def build_decomposition_section(decs: list[dict]) -> str:
    """One union-decomposition table per duplicate definition."""
    blocks = []
    for d in decs:
        sz, pw = d["sizes"], d["pairwise"]
        blocks.append(
            f"""### Duplicates defined as **{d['dup_mode']}** (DUP = {sz['DUP']})

| Term | Rows |
|---|---|
| \\|NULL\\| | {sz['NULL']} |
| \\|SHORT\\| | {sz['SHORT']} |
| \\|DUP\\| | {sz['DUP']} |
| \\|NULL ∩ SHORT\\| | {pw['NULL & SHORT']} |
| \\|NULL ∩ DUP\\| | {pw['NULL & DUP']} |
| \\|SHORT ∩ DUP\\| | {pw['SHORT & DUP']} |
| \\|NULL ∩ SHORT ∩ DUP\\| | {d['triple']} |
| naive sum (overlaps double-counted) | {d['naive_sum']} |
| **\\|union\\|** | **{d['union']}** |
| **usable_n = {d['n_rows']} − union** | **{d['usable_n']}** |
"""
        )
    return "\n".join(blocks)


def reconcile_claimed_usable(cfg, decs) -> str:
    """Explain the claimed usable_n from the observed numbers.

    Written as a derivation rather than a fixed sentence: it checks which (if
    any) duplicate definition reproduces the claim under naive subtraction, so
    the text cannot drift away from the computed values.
    """
    claimed_usable = int(cfg["claims"]["usable_n"])
    claimed_null = int(cfg["claims"]["null_rows"])

    for d in decs:
        sz = d["sizes"]
        naive_val = d["n_rows"] - d["naive_sum"]
        if naive_val != claimed_usable:
            continue
        return (
            f"The claimed `usable_n` of {claimed_usable} is reproduced exactly by "
            f"naive subtraction under the **{d['dup_mode']}** duplicate "
            f"definition: {sz['NULL']} + {sz['SHORT']} + {sz['DUP']} = "
            f"{d['naive_sum']}, and {d['n_rows']} − {d['naive_sum']} = "
            f"{naive_val}.\n\n"
            f"Two consequences. First, that subtraction uses **{sz['NULL']}** null "
            f"rows — the observed count — while the S0 table's `null_rows` row "
            f"reports {claimed_null}. The table is therefore internally "
            f"inconsistent with its own `usable_n`, and the defect is in how "
            f"`null_rows` was **reported**, not in the null handling behind the "
            f"arithmetic. Second, the subtraction still treats the three drop "
            f"sets as disjoint, so it double-counts the "
            f"{d['pairwise']['SHORT & DUP']} rows in SHORT ∩ DUP. The union is "
            f"{d['union']}, not {d['naive_sum']}, giving usable_n = "
            f"**{d['usable_n']}**."
        )

    tried = ", ".join(
        f"{d['dup_mode']}: {d['n_rows']} − {d['naive_sum']} = "
        f"{d['n_rows'] - d['naive_sum']}"
        for d in decs
    )
    return (
        f"The claimed `usable_n` of {claimed_usable} is **not** reproduced by "
        f"naive subtraction under either duplicate definition ({tried}), so how "
        f"it was derived cannot be reconstructed from the observed counts."
    )


def build_report(cfg, cfg_path, input_path, obs, ctx, prov, decs) -> str:
    claims = cfg["claims"]
    rows, n_match = [], 0
    for key, claimed in claims.items():
        observed = obs[key]
        # Compare on normalized forms so {0:1665} vs {"0":1665} does not
        # produce a spurious mismatch.
        if isinstance(claimed, dict):
            same = {int(k): int(v) for k, v in claimed.items()} == observed
        else:
            same = float(claimed) == float(observed)
        n_match += same
        rows.append(
            f"| `{key}` | {fmt(claimed)} | {fmt(observed)} | "
            f"{'MATCH' if same else '**MISMATCH**'} |"
        )

    mismatches = len(claims) - n_match
    verdict = (
        "All claimed quantities were reproduced."
        if mismatches == 0
        else f"**{mismatches} of {len(claims)} claims did not reproduce.** "
        "The S0 table in `docs/research_pipeline_en.md` is wrong for those rows "
        "and must be corrected to the observed values. The observed column is "
        "authoritative; do not adopt the claimed number."
    )

    ctx_rows = "\n".join(f"| `{k}` | {fmt(v)} |" for k, v in ctx.items())

    return f"""# S0 — Data X-ray

Verification of the S0 claims in `docs/research_pipeline_en.md` against the raw
file. **Read-only step:** no data was cleaned, filtered, or written.

- **Config:** `{cfg_path}`
- **Input:** `{input_path}` (sheet `{cfg['sheet']}`)
- **Text column:** `{cfg['text_col']}` · **Label column:** `{cfg['label_col']}`
- **Seed:** {cfg['seed']}
- **Generated (UTC):** {prov['timestamp_utc']}
- **Git commit:** `{prov['git_commit']}`
- **Python:** {prov['python']} · **Platform:** {prov['platform']}

## Claim verification

| Quantity | Claimed | Observed | Flag |
|---|---|---|---|
{chr(10).join(rows)}

**Result: {n_match}/{len(claims)} match.** {verdict}

## Union decomposition of the S1 drop set

The three drop sets overlap, so subtracting their sizes independently
double-counts rows. The union is computed once and subtracted once. Set
definitions are in "Measurement definitions" below; `SHORT` excludes the
missing-text row so it stays the reported count of {decs[0]['sizes']['SHORT']}.

{reconcile_claimed_usable(cfg, decs)}

**The claim-checked `usable_n` above uses the EXACT duplicate definition**
(DUP = {decs[0]['sizes']['DUP']}), matching the pipeline's own "Removed in
cleaning" wording for the 204 figure. The normalized variant is reported below
so the choice is visible rather than buried; it is a decision for S1, not for
this verification step.

{build_decomposition_section(decs)}
| Duplicate definition | union | usable_n |
|---|---|---|
| exact (DUP = {decs[0]['sizes']['DUP']}) | {decs[0]['union']} | **{decs[0]['usable_n']}** |
| normalized (DUP = {decs[1]['sizes']['DUP']}) | {decs[1]['union']} | **{decs[1]['usable_n']}** |

## Measurement definitions

These fix how each observed number was computed, so the table is reproducible:

- **word** — a whitespace-delimited token (`str.split()`). No tokenizer, no
  stemming, no stopword removal.
- **null row** — the review text is missing or whitespace-only, **or** the
  sentiment label is missing.
- **exact duplicate** — a review string identical to an earlier one, counted as
  occurrences beyond the first.
- **normalized duplicate** — same, after Unicode NFC + whitespace collapse +
  strip. Applied for counting only; the data itself is never normalized.
- **usable_n** — rows surviving the three S1 drops (null, exact duplicate,
  <3 words), computed as a single union so rows failing several conditions are
  not double-counted.
- **median/max words** — over rows with non-null text.
- **emoji row** — contains a pictographic character from the Unicode emoji
  blocks (emoticons, pictographs, transport, dingbats, misc symbols, regional
  indicators). A bare `U+FE0F` (VARIATION SELECTOR-16) is a modifier, not an
  emoji, and is **not** counted here — it is reported separately as
  `orphan_vs16_rows` below.
- **url/mention row** — matches `http(s)://`, `www.`, a bare `*.com/.net/.org/.bd`
  token, or an `@handle`.

## Additional observed context (not claim-checked)

| Quantity | Observed |
|---|---|
{ctx_rows}
"""


def main() -> int:
    set_seed()

    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/s0_xray.yaml")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    cfg_path = Path(args.config)
    cfg = yaml.safe_load((repo_root / cfg_path).read_text(encoding="utf-8"))

    input_path = resolve_input(cfg["input_xlsx"], repo_root)
    df = pd.read_excel(input_path, sheet_name=cfg["sheet"])

    for col in (cfg["text_col"], cfg["label_col"]):
        if col not in df.columns:
            raise KeyError(f"Column {col!r} not in sheet; found {list(df.columns)}")

    obs = compute(df, cfg["text_col"], cfg["label_col"])
    ctx = context(df, cfg["text_col"], cfg["label_col"])
    decs = [
        decompose(df, cfg["text_col"], cfg["label_col"], "exact"),
        decompose(df, cfg["text_col"], cfg["label_col"], "normalized"),
    ]
    prov = stamp(str(cfg_path))

    out = repo_root / cfg["output_report"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        build_report(
            cfg, cfg_path.as_posix(), input_path.relative_to(repo_root).as_posix(),
            obs, ctx, prov, decs,
        ),
        encoding="utf-8",
    )
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
