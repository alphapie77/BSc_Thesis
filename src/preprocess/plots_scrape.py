"""Harvest Bangla film plot summaries from bn.wikipedia via the MediaWiki API.

Stdlib only (`urllib`) so it runs anywhere without new dependencies.

    python -m src.preprocess.plots_scrape --config configs/plots_scrape.yaml
    python -m src.preprocess.plots_scrape --config ... --sample 130

Phase 1 (`--config` alone) discovers film articles from the seed categories,
fetches each one's plot section, applies the quality gate, and writes every
survivor to the harvest CSV with its **revision id**. Phase 2 (`--sample N`)
draws the final N with seed 42 and writes `data/plots/plots_bn.csv`.

The two phases are separate on purpose. Harvest everything that qualifies, then
sample blind. Choosing which harvested films to keep, by eye, would put the
selection bias straight back in.

**Licence — a condition, not bookkeeping.** bn.wikipedia text is CC BY-SA 4.0:
reusable **with attribution and share-alike**. Every row carries `revision_id`
and `licence` so the exact text is citable and the obligation is discharegable.
The dataset card must carry the attribution before anything is published.

**Rate limiting.** One request per `request_delay_seconds`, with a descriptive
User-Agent. This is someone else's server and it is free.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import NEWLINE, stamp, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402

BANGLA = re.compile(r"[ঀ-৿]")
SENT_END = re.compile(r"[।!?]")
LICENCE = "CC BY-SA 4.0"
PLOTS_OUT = Path("data/plots/plots_bn.csv")
COLUMNS = ["plot_id", "language", "title_bn", "title_en", "synopsis",
           "n_sentences", "source_url", "source_type", "collected_date", "split"]


class Api:
    def __init__(self, cfg):
        self.url = cfg["api"]
        self.ua = cfg["user_agent"]
        self.delay = float(cfg["request_delay_seconds"])
        self._last = 0.0
        self.calls = 0

    def get(self, **params) -> dict:
        params.setdefault("format", "json")
        params.setdefault("formatversion", "2")
        wait = self.delay - (time.time() - self._last)
        if wait > 0:
            time.sleep(wait)
        q = urllib.parse.urlencode(params)
        req = urllib.request.Request(f"{self.url}?{q}",
                                     headers={"User-Agent": self.ua})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
        self._last = time.time()
        self.calls += 1
        if "error" in data:
            raise RuntimeError(f"API error: {data['error']}")
        return data


def discover(api: Api, cfg) -> dict[str, str]:
    """Article titles in the seed categories. Returns {title: category}."""
    found: dict[str, str] = {}
    for cat in cfg["categories"]:
        queue, depth = [(cat, 0)], {}
        depth[cat] = 0
        n_before = len(found)
        while queue:
            title, d = queue.pop(0)
            cont = {}
            while True:
                data = api.get(
                    action="query", list="categorymembers", cmtitle=title,
                    cmlimit="500", cmtype="page|subcat", **cont,
                )
                for m in data.get("query", {}).get("categorymembers", []):
                    t = m["title"]
                    if t.startswith("বিষয়শ্রেণী:") or t.startswith("Category:"):
                        if d < int(cfg["category_depth"]) and t not in depth:
                            depth[t] = d + 1
                            queue.append((t, d + 1))
                    elif m.get("ns", 0) == 0:
                        found.setdefault(t, cat)
                if "continue" not in data or \
                        len(found) - n_before >= int(cfg["max_pages_per_category"]):
                    break
                cont = data["continue"]
            if len(found) - n_before >= int(cfg["max_pages_per_category"]):
                break
        print(f"  {cat}: +{len(found) - n_before} articles "
              f"(running total {len(found)})")
    return found


def split_sections(extract: str) -> dict[str, str]:
    """Plain-text extract -> {heading: body}. Level-2 headings only.

    `explaintext` renders headings as `== Heading ==` on their own line, which
    is why this can be done without an HTML parser.
    """
    out, current, buf = {}, "__lead__", []
    for line in extract.splitlines():
        m = re.match(r"^==+\s*(.+?)\s*==+$", line.strip())
        if m:
            out[current] = "\n".join(buf).strip()
            current, buf = m.group(1).strip(), []
        else:
            buf.append(line)
    out[current] = "\n".join(buf).strip()
    return out


def pick_plot(sections: dict[str, str], headings: list[str]) -> tuple[str, str]:
    """First section whose heading matches. Returns (heading, text)."""
    wanted = {h.replace(" ", "") for h in headings}
    for head, body in sections.items():
        if head.replace(" ", "") in wanted and body.strip():
            return head, body.strip()
    return "", ""


def n_sentences(text: str) -> int:
    return len([p for p in SENT_END.split(text) if p.strip()])


def truncate(text: str, max_sent: int) -> str:
    """Cut at a sentence boundary rather than dropping a long-but-good plot."""
    parts = SENT_END.split(text)
    ends = SENT_END.findall(text)
    if len(parts) <= max_sent:
        return text.strip()
    out = "".join(p + (ends[i] if i < len(ends) else "")
                  for i, p in enumerate(parts[:max_sent]))
    return out.strip()


def quality_reason(text: str, q) -> str:
    """Empty string = passes. Otherwise the reason, for the reject tally."""
    if q["require_bangla"] and not BANGLA.search(text):
        return "no Bangla characters"
    if len(text) < int(q["min_chars"]):
        return f"under {q['min_chars']} chars"
    if len(text) > int(q["max_chars"]):
        return f"over {q['max_chars']} chars"
    if n_sentences(text) < int(q["min_sentences"]):
        return f"under {q['min_sentences']} sentences"
    return ""


def harvest(api: Api, cfg, titles: dict[str, str]) -> tuple[pd.DataFrame, dict]:
    rows, rejects = [], {}
    names = list(titles)
    batch = int(cfg["batch_size"])
    q = cfg["quality"]

    for i in range(0, len(names), batch):
        chunk = names[i:i + batch]
        data = api.get(
            action="query", prop="extracts|revisions|info",
            titles="|".join(chunk), explaintext="1",
            rvprop="ids|timestamp", inprop="url",
        )
        for page in data.get("query", {}).get("pages", []):
            title = page.get("title", "")
            if "missing" in page:
                rejects["missing page"] = rejects.get("missing page", 0) + 1
                continue
            extract = page.get("extract", "") or ""
            head, body = pick_plot(split_sections(extract), cfg["plot_headings"])
            if not body:
                rejects["no plot section"] = rejects.get("no plot section", 0) + 1
                continue
            body = truncate(re.sub(r"\n+", " ", body), int(q["max_sentences"]))
            reason = quality_reason(body, q)
            if reason:
                rejects[reason] = rejects.get(reason, 0) + 1
                continue
            revs = page.get("revisions", [{}])
            rows.append({
                "title_bn": title,
                "synopsis": body,
                "n_sentences": n_sentences(body),
                "source_url": page.get("fullurl", ""),
                "revision_id": revs[0].get("revid", ""),
                "revision_timestamp": revs[0].get("timestamp", ""),
                "plot_heading": head,
                "seed_category": titles[title],
                "licence": LICENCE,
            })
        print(f"  fetched {min(i + batch, len(names))}/{len(names)} "
              f"-> {len(rows)} usable", end="\r")
    print()
    return pd.DataFrame(rows), rejects


def do_sample(cfg, root: Path, n: int) -> int:
    """Draw the final N from the harvest, blind, with the global seed."""
    hp = root / cfg["outputs"]["harvest_csv"]
    if not hp.exists():
        sys.exit(f"{hp} not found -- run the harvest first.")
    h = pd.read_csv(hp)
    if len(h) < n:
        sys.exit(
            f"harvest has {len(h)} plots, need {n}. Widen `categories` or relax "
            f"`quality` in the config and re-harvest -- do NOT hand-pick to make "
            f"up the difference, that is the bias this step exists to avoid."
        )
    set_seed()
    s = h.sample(n=n, random_state=42).sort_values("title_bn").reset_index(drop=True)
    s.insert(0, "plot_id", [f"BN{i:03d}" for i in range(1, n + 1)])
    s["language"] = "bn"
    s["title_en"] = ""
    s["source_type"] = "wikipedia_bn"
    s["collected_date"] = pd.Timestamp.utcnow().strftime("%Y-%m-%d")
    s["split"] = ""          # assigned once, later, by plots_check --assign-split

    out = root / PLOTS_OUT
    extra = ["revision_id", "revision_timestamp", "licence"]
    s[COLUMNS + extra].to_csv(out, index=False, encoding="utf-8",
                              lineterminator=NEWLINE)
    print(f"sampled {n} of {len(h)} with seed 42 -> {PLOTS_OUT}")
    print("Next: eyeball them, then `python -m src.preprocess.plots_check`.")
    print(f"`split` is left empty on purpose -- assign it once at {n}.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/plots_scrape.yaml")
    ap.add_argument("--sample", type=int, default=0,
                    help="draw this many from an existing harvest and stop")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    cfg = yaml.safe_load((root / args.config).read_text(encoding="utf-8"))

    if args.sample:
        return do_sample(cfg, root, args.sample)

    api = Api(cfg)
    print("discovering film articles...")
    titles = discover(api, cfg)
    print(f"{len(titles)} candidate articles\n\nfetching plot sections...")
    df, rejects = harvest(api, cfg, titles)

    if df.empty:
        sys.exit(
            "nothing passed the quality gate. Check `plot_headings` against a "
            "real article first -- bn.wikipedia heading spellings vary."
        )
    df = df.drop_duplicates(subset=["title_bn"]).reset_index(drop=True)
    out = root / cfg["outputs"]["harvest_csv"]
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8", lineterminator=NEWLINE)

    write_text_lf(root / cfg["outputs"]["report_md"],
                  build_report(cfg, args.config, stamp(args.config), df,
                               rejects, len(titles), api.calls))
    print(f"\n{len(df)} usable plots -> {cfg['outputs']['harvest_csv']}")
    print(f"rejected: {sum(rejects.values())}  {rejects}")
    print(f"\nNext: python -m src.preprocess.plots_scrape --sample 130")
    return 0


def build_report(cfg, cfg_path, prov, df, rejects, n_candidates, calls) -> str:
    rej = "\n".join(f"| {k} | {v} |" for k, v in
                    sorted(rejects.items(), key=lambda x: -x[1])) or "| — | 0 |"
    bycat = df["seed_category"].value_counts()
    cat = "\n".join(f"| {k} | {v} |" for k, v in bycat.items())
    return f"""# Plot harvest — bn.wikipedia

- **Config:** `{cfg_path}` · **Generated (UTC):** {prov["timestamp_utc"]}
- **Commit:** `{prov["git_commit"]}` · **API calls:** {calls}

## Yield

| | |
|---|---|
| candidate articles discovered | {n_candidates} |
| passed the quality gate | **{len(df)}** |
| rejected | {sum(rejects.values())} |

### Why articles were rejected

| Reason | Count |
|---|---|
{rej}

Most bn.wikipedia film articles are stubs, so a large "no plot section" count is
expected rather than a fault. It matters only if the survivors fall below 130.

### By seed category

| Category | Plots |
|---|---|
{cat}

## Licence — an obligation, not a note

Text is **{LICENCE}** from bn.wikipedia: reusable **with attribution and
share-alike**. Every row carries `revision_id` and `revision_timestamp`, so the
exact revision used is citable and a reviewer can fetch it. **The dataset card
must carry the attribution before anything is published.**

## Sentence-length distribution

| Statistic | Sentences |
|---|---|
| min | {df["n_sentences"].min()} |
| median | {df["n_sentences"].median():.0f} |
| max | {df["n_sentences"].max()} |

## What still needs a human

The gate is mechanical: it counts characters and sentences. It cannot tell a
plot summary from a production-history paragraph that happened to sit under a
matching heading. **Read the sampled 130 before using them.** Anything that is
not a plot gets deleted, and the sample is redrawn — not patched by hand.
"""


if __name__ == "__main__":
    raise SystemExit(main())
