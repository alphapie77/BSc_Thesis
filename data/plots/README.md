# Bangla plot synopses — 130 needed, hand-collected

**Target:** 130 (30 dev + 100 eval, disjoint) · **File:** `plots_bn.csv`
**Check progress:** `python -m src.preprocess.plots_check`

## Why this is the critical path

Everything else in this thesis is code, and code runs overnight. These 130 do
not. At 5 per day it is **26 working days**, and S6 — the entire experiment —
cannot start without them. This is the only track that cannot be caught up later,
which is why it starts now rather than when it is needed.

They are also the **held-out element of the whole evaluation**: the corpus has no
movie-title column, so reviews cannot be mapped to films, and these plots are
what replaced the held-out-films split. Losing them invalidates S6. They are
committed to git for that reason, unlike every other derived file.

## The daily 5

1. Open a Bangla film on **bn.wikipedia.org** (or bmdb.com.bd).
2. Read the plot section. Write **3–8 sentences in your own words**.
3. Paste the **exact page URL** into `source_url`.
4. Fill the row. Leave `split` **empty** — see below.
5. Run `python -m src.preprocess.plots_check` before you close the laptop.

## Rules that matter

- **`source_url` is not optional.** It is the one field that cannot be
  reconstructed later. Provenance fact (c) in `docs/STATUS.md` is a live record
  of what an unrecorded source costs — 60% of the review corpus now has an
  unrecoverable origin, and the thesis carries that as a permanent limitation.
  Do not create a second one.
- **Summarise, do not paste.** A copied Wikipedia paragraph is someone else's
  text and a copyright problem in an appendix. 3–8 sentences in your own words.
  The checker rejects anything under 2 or over 12 sentences.
- **Leave `split` empty.** It is assigned once, at 130, by
  `--assign-split` with seed 42.

  *Why:* if you filled it in as you went, the first 30 films would become the dev
  set — and the first 30 films anyone thinks of are the famous ones with the
  longest articles. Every threshold tuned on dev would then be tuned on easy
  cases, and the eval-100 would be systematically harder. Collect blind, split
  once.
- **No duplicate films**, even under different `plot_id`s. Easy to do across
  sessions, so the checker looks for repeated titles, synopses and URLs.
- **Vary the films.** Different decades, genres, and both hits and flops. A set
  of 130 blockbusters would make the evaluation easier than the claim implies.

## Columns

| Column | What goes in it |
|---|---|
| `plot_id` | `BN001` … `BN130` |
| `language` | `bn` |
| `title_bn` | Bangla title |
| `title_en` | English/romanised title, if there is one |
| `synopsis` | **3–8 sentences, your own words** |
| `n_sentences` | leave blank — the checker counts it |
| `source_url` | exact page URL, **required** |
| `source_type` | `wikipedia_bn` \| `bmdb` \| `self_written` |
| `collected_date` | `YYYY-MM-DD` |
| `split` | **leave empty** until 130 |

## When you reach 130

```bash
python -m src.preprocess.plots_check                 # must report no problems
python -m src.preprocess.plots_check --assign-split  # once, seed 42
```

Then commit. From that point the split is frozen, exactly like
`data/splits/split_map_v1.json`, and the tool refuses to reassign it.
