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

#: Default article for `--probe`. A well-known Bangladeshi film whose
#: bn.wikipedia article has a real plot section.
DEFAULT_PROBE_TITLE = "মনপুরা"

BANGLA = re.compile(r"[ঀ-৿]")
SENT_END = re.compile(r"[।!?]")
LICENCE = "CC BY-SA 4.0"
PLOTS_OUT = Path("data/plots/plots_bn.csv")
COLUMNS = ["plot_id", "language", "title_bn", "title_en", "synopsis",
           "n_sentences", "source_url", "source_type", "collected_date", "split"]


def ssl_context() -> "ssl.SSLContext":
    """TLS context that trusts certifi's CA bundle rather than the OS store.

    On Windows, `urllib` verifies against the system certificate store, which on
    an under-updated machine still carries expired roots -- producing
    `CERTIFICATE_VERIFY_FAILED: certificate has expired` against a server whose
    certificate is perfectly valid. `certifi` ships a current bundle and is
    already a dependency (via `requests`), so pointing at it fixes the cause.

    Verification stays ON. Turning it off would "work" and is not an option:
    this fetches text that becomes evaluation data, and an unverified connection
    means the provenance recorded per row -- the whole point of storing revision
    ids -- guarantees nothing.
    """
    import ssl
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


class Api:
    def __init__(self, cfg):
        self.url = cfg["api"]
        self.ua = cfg["user_agent"]
        self.delay = float(cfg["request_delay_seconds"])
        self._last = 0.0
        self.calls = 0
        self.ssl = ssl_context()
        self.timeout = float(cfg.get("timeout_seconds", 60))
        self.retries = int(cfg.get("retries", 4))

    def get(self, **params) -> dict:
        """One API call, retried with backoff.

        A run touches >1,200 articles over several minutes; a transient timeout
        somewhere in the middle is not an exceptional event, it is the expected
        case. Without retries the first blip discards everything fetched so far.
        """
        params.setdefault("format", "json")
        params.setdefault("formatversion", "2")
        q = urllib.parse.urlencode(params)
        req = urllib.request.Request(f"{self.url}?{q}",
                                     headers={"User-Agent": self.ua})

        last_err = None
        for attempt in range(self.retries):
            wait = self.delay - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            try:
                with urllib.request.urlopen(
                        req, timeout=self.timeout, context=self.ssl) as r:
                    data = json.loads(r.read().decode("utf-8"))
                self._last = time.time()
                self.calls += 1
                if "error" in data:
                    raise RuntimeError(f"API error: {data['error']}")
                return data
            except Exception as e:
                self._last = time.time()
                last_err = e
                if attempt < self.retries - 1:
                    back = 2 ** (attempt + 1)
                    print(f"\n  {type(e).__name__}: retrying in {back}s "
                          f"({attempt + 2}/{self.retries})", flush=True)
                    time.sleep(back)
        raise last_err


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


def harvest(api: Api, cfg, titles: dict[str, str], root: Path
            ) -> tuple[pd.DataFrame, dict]:
    """Fetch plot sections, checkpointing so a crash never costs the whole run.

    The first attempt at this lost 1,225 articles' worth of work to one read
    timeout. State is now written every `checkpoint_every` batches, and a re-run
    skips titles already processed -- including ones that were rejected, so a
    resumed run does not re-fetch every stub it has already seen.
    """
    state_path = root / cfg["outputs"]["state_json"]
    out_path = root / cfg["outputs"]["harvest_csv"]

    rows, rejects, processed = [], {}, set()
    if state_path.exists():
        st = json.loads(state_path.read_text(encoding="utf-8"))
        processed = set(st.get("processed", []))
        rejects = st.get("rejects", {})
        if out_path.exists():
            rows = pd.read_csv(out_path).to_dict("records")
        print(f"resuming: {len(processed)} titles already processed, "
              f"{len(rows)} usable so far")

    def save():
        state_path.parent.mkdir(parents=True, exist_ok=True)
        write_text_lf(state_path, json.dumps(
            {"processed": sorted(processed), "rejects": rejects},
            ensure_ascii=False, indent=1) + "\n")
        if rows:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(rows).to_csv(out_path, index=False, encoding="utf-8",
                                      lineterminator=NEWLINE)

    names = [t for t in titles if t not in processed]
    batch = int(cfg["batch_size"])
    every = int(cfg.get("checkpoint_every", 5))
    q = cfg["quality"]
    print(f"{len(names)} to fetch, {batch} per request")

    for bi, i in enumerate(range(0, len(names), batch)):
        chunk = names[i:i + batch]
        try:
            data = api.get(
                action="query", prop="extracts|revisions|info",
                titles="|".join(chunk), explaintext="1",
                rvprop="ids|timestamp", inprop="url",
            )
        except Exception as e:
            # One dead batch must not end the run. Record and move on; the
            # titles stay unprocessed so a later run retries them.
            k = f"batch failed ({type(e).__name__})"
            rejects[k] = rejects.get(k, 0) + len(chunk)
            print(f"\n  skipping batch of {len(chunk)}: {type(e).__name__}")
            save()
            continue

        processed.update(chunk)
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
        if bi % every == 0:
            save()
        print(f"  fetched {min(i + batch, len(names))}/{len(names)} "
              f"-> {len(rows)} usable", end="\r", flush=True)

    save()
    print()
    return pd.DataFrame(rows), rejects


def probe(api: Api, cfg, title: str) -> int:
    """Fetch ONE article and show exactly what came back.

    This code has never touched the real API -- it was written in an environment
    that cannot reach bn.wikipedia. Rather than let a full harvest fail slowly
    and opaquely, `--probe` makes the first contact cheap and legible: two
    seconds, one article, and every intermediate step printed. If the response
    shape or the heading list is wrong, it is visible here instead of showing up
    as an empty CSV twenty minutes later.
    """
    print(f"probing: {title}\nAPI: {cfg['api']}\n")
    try:
        data = api.get(action="query", prop="extracts|revisions|info",
                       titles=title, explaintext="1",
                       rvprop="ids|timestamp", inprop="url")
    except Exception as e:
        msg = str(e)
        print(f"REQUEST FAILED: {type(e).__name__}: {msg}")
        if "CERTIFICATE_VERIFY_FAILED" in msg or "SSL" in msg:
            try:
                import certifi
                print(f"\nUsing certifi bundle: {certifi.where()}")
                print("Still failing with a current bundle. Try:")
                print("    pip install --upgrade certifi")
                print("If your machine is behind a corporate proxy that "
                      "re-signs TLS, its root must be added to that bundle.")
            except ImportError:
                print("\ncertifi is NOT installed -- that is the cause. Run:")
                print("    pip install certifi")
            print("\nDo NOT disable verification: this text becomes evaluation "
                  "data, and unverified transport makes the per-row provenance "
                  "meaningless.")
        elif "403" in msg:
            print("\n403 -- the User-Agent may be rejected. Put a real contact "
                  "address in `user_agent` in the config.")
        return 1

    pages = data.get("query", {}).get("pages")
    if pages is None:
        print("UNEXPECTED RESPONSE SHAPE. Raw keys:", list(data))
        print(json.dumps(data, ensure_ascii=False)[:800])
        print("\n-> formatversion=2 was expected. Check the `api` URL.")
        return 1

    page = pages[0]
    if "missing" in page:
        print(f"page not found: {title!r} -- try an exact bn.wikipedia title.")
        return 1

    print(f"title      : {page.get('title')}")
    print(f"url        : {page.get('fullurl')}")
    print(f"revision   : {page.get('revisions', [{}])[0].get('revid')}")
    extract = page.get("extract", "") or ""
    print(f"extract    : {len(extract)} chars")
    if not extract:
        print("\nEMPTY EXTRACT -- prop=extracts may be unavailable. "
              "Fall back to action=parse.")
        return 1

    sections = split_sections(extract)
    print(f"\nsections   : {len(sections)}")
    for h in sections:
        mark = "  <-- MATCHES plot_headings" if h.replace(" ", "") in {
            x.replace(" ", "") for x in cfg["plot_headings"]} else ""
        print(f"  - {h}{mark}")

    head, body = pick_plot(sections, cfg["plot_headings"])
    if not head:
        print("\nNO PLOT SECTION MATCHED.")
        print("-> add the right heading above to `plot_headings` in the config.")
        return 1

    body = truncate(re.sub(r"\n+", " ", body), int(cfg["quality"]["max_sentences"]))
    reason = quality_reason(body, cfg["quality"])
    print(f"\nplot heading : {head!r}")
    print(f"sentences    : {n_sentences(body)} · chars: {len(body)}")
    print(f"quality      : {reason or 'PASS'}")
    print(f"\n--- extracted text ---\n{body[:600]}")
    print("\nProbe OK. Run the full harvest." if not reason else
          "\nExtraction works but this article fails the gate -- try another.")
    return 0 if not reason else 1


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
    # nargs="?" so `--probe` works with no argument. Typing a Bangla title on a
    # Windows console is its own small ordeal, and the first thing anyone runs
    # should not require it.
    ap.add_argument("--probe", metavar="TITLE", nargs="?",
                    const=DEFAULT_PROBE_TITLE, default="",
                    help="fetch ONE article and print every step. Run this "
                         f"first. Defaults to {DEFAULT_PROBE_TITLE}.")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    cfg = yaml.safe_load((root / args.config).read_text(encoding="utf-8"))

    if args.sample:
        return do_sample(cfg, root, args.sample)

    api = Api(cfg)
    if args.probe:
        return probe(api, cfg, args.probe)
    print("discovering film articles...")
    titles = discover(api, cfg)
    print(f"{len(titles)} candidate articles\n\nfetching plot sections...")
    df, rejects = harvest(api, cfg, titles, root)

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
