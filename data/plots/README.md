# Bangla plot synopses — 130, harvested from bn.wikipedia

**Target:** 130 (30 dev + 100 eval, disjoint) · **File:** `plots_bn.csv`

```bash
python -m src.preprocess.plots_scrape --probe "মনপুরা"   # <-- START HERE, 2 seconds
python -m src.preprocess.plots_scrape                     # harvest
python -m src.preprocess.plots_scrape --sample 130        # draw 130, seed 42
python -m src.preprocess.plots_check                      # validate
# ... read them; delete non-plots from the harvest and re-sample ...
python -m src.preprocess.plots_check --assign-split       # once, at 130
```

> **Run `--probe` first.** This scraper was written in an environment that
> cannot reach bn.wikipedia, so its network path has never executed. `--probe`
> fetches **one** article and prints every step — response shape, section
> headings found, which one matched, the extracted text, the quality verdict. If
> something is wrong you see it in two seconds instead of as an empty CSV twenty
> minutes later. Its diagnostics are tested against five failure modes: healthy
> response, no matching heading, missing page, unexpected response shape, and a
> dead connection.

## Why scraped rather than hand-written

Not only because it is faster. Hand-writing was the worse method:

1. **Hand-written summaries would carry one person's register into the inputs.**
   The thesis generates Bangla audience reviews *from these plots*, so the plot
   text is part of the experiment. 130 summaries in the experimenter's own voice
   is an uncontrolled variable sitting at the top of every generation.
2. **Selection bias disappears.** Collecting by hand means collecting the films
   you thought of — the famous ones, with the longest articles. Harvesting a
   category and sampling with a seed has no opinion about which films matter.
3. **It is checkable.** `source_url` + `revision_id` lets a reviewer fetch the
   exact text used. A hand-written paraphrase can be checked against nothing.

## Licence — an obligation, not a footnote

bn.wikipedia text is **CC BY-SA 4.0**: reusable **with attribution and
share-alike**. Every row stores `revision_id`, `revision_timestamp` and
`licence`, so the exact revision is citable.

**The dataset card must carry the attribution before anything is published,** and
if the plot set is released it must be released under a compatible licence.
This is a condition of use. It is also why verbatim extraction is *correct* here
and paraphrasing would not have been better — a paraphrase of a CC BY-SA text is
a derivative work either way, and it loses the ability to point at a revision.

## The three steps

**1. Harvest.** Walks the seed categories in `configs/plots_scrape.yaml`, pulls
each article's plot section, applies the quality gate (3–12 sentences, ≥120
characters, must contain Bangla), and writes every survivor to
`plots_bn_harvest.csv`. Rate-limited to one request per second with a
contactable User-Agent, because this is someone else's free server.

Read `results/plots_harvest_report.md` afterwards. A large "no plot section"
count is expected — most bn.wikipedia film articles are stubs. It only matters
if the survivors fall short of 130.

**2. Sample 130.** Blind, seed 42, from everything that qualified. Harvest-then-
sample is deliberate: choosing which harvested films to keep, by eye, would put
the selection bias straight back in.

If the harvest yields fewer than 130, **widen `categories` or relax `quality`
and re-harvest — do not hand-pick to make up the difference.**

**3. Read them.** The gate is mechanical: it counts characters and sentences. It
cannot tell a plot summary from a production-history paragraph that happened to
sit under a matching heading. Anything that is not a plot gets **deleted from the
harvest and the sample redrawn**, not patched by hand.

## Leave `split` empty until the end

It is assigned once, at 130, by `plots_check --assign-split`, seed 42.

*Why:* filling it during collection would make the first 30 films the dev set,
and the first 30 films in any list are the ones that surfaced first. Every
threshold tuned on dev would then be tuned on easy cases and the eval-100 would
be systematically harder. The tool refuses to reassign once it is set — the
eval-100 is the only held-out element S6 has, and losing it invalidates the
experiment.

## Why these are committed to git

The corpus has **no movie-title column**, so reviews cannot be mapped to films.
That is why the held-out-films split was dropped and these 130 plots replaced it.
They are the held-out element of the entire evaluation. Unlike every other
derived file here, they are committed.
