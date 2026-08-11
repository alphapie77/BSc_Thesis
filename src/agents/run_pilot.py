#!/usr/bin/env python3
"""The 20-generation generator pilot. §4.4, decision rule pre-registered.

⛔ **NOT A RESULT.** This selects a generator. It measures nothing, and nothing
it produces may be quoted in the thesis, a paper, or a results table. Banner in
the style of `results/pilot_s35_idf.*`.

WHAT IS DECIDED HERE, AND WHAT IS NOT
-------------------------------------
Decided: **which model, and which prompt language**, by a **failure rate**.
Not decided: which is *better*. A quality difference between two models at
n = 20 is not detectable -- the same power problem that made `TIE` the registered
default, and S3.2 could not separate **seven** arms with **five seeds** each.

`LANG_CONFUSION` is decidable at this n because it is a binary with a near-zero
baseline: region A's `has_latin` is **0.09% / 0.00%**, so any Latin script in a
Bangla generation is signal rather than noise.

THE GRID
--------
2 models x 2 prompt arms x 10 dev-plots x 2 levels = 80 calls. Each *arm* sees
the registered 20 generations. Plots are taken in **frozen split order**, not
chosen -- picking plots that "look suitable" is how a pilot becomes a
demonstration.

Resumable: every generation is appended to JSONL as it completes and a re-run
skips what is already there. At free-tier throughput this is ~20 minutes; at
~5 calls/min a dropped connection should not cost the lot.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.prompts import render  # noqa: E402
from src.agents.researcher import Researcher  # noqa: E402
from src.agents.writer import Writer, completed_keys, generation_key  # noqa: E402
from src.common.provenance import write_result, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402

LATIN = re.compile(r"[A-Za-z]")


def latin_fraction(text: str) -> float:
    """Share of characters that are Latin script. The confusion detector."""
    if not text:
        return 0.0
    return sum(1 for ch in text if LATIN.match(ch)) / len(text)


def load_dev_plots(n: int) -> list[dict]:
    rows = [
        r
        for r in csv.DictReader(open("data/plots/plots_bn.csv", encoding="utf-8"))
        if r["split"] == "dev"
    ]
    # Frozen file order, first n. Not sampled, not sorted by anything.
    return rows[:n]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="configs/s4_pilot.yaml")
    ap.add_argument("--dry-run", action="store_true",
                    help="Build every prompt and print the grid; make no API call.")
    args = ap.parse_args()

    set_seed()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    out = cfg["outputs"]
    plots = load_dev_plots(int(cfg["sample"]["n_plots"]))
    levels = list(cfg["sample"]["levels"])
    arms = list(cfg["prompt_arms"])
    models = dict(cfg["models"])

    idx = yaml.safe_load(Path("configs/s4_index.yaml").read_text(encoding="utf-8"))["index"]
    researcher = Researcher(idx["persist_dir"], idx["collection"], idx["encoder"])

    total = len(models) * len(arms) * len(plots) * len(levels)
    print(f"grid: {len(models)} models x {len(arms)} prompt arms x "
          f"{len(plots)} plots x {len(levels)} levels = {total} calls")

    if args.dry_run:
        # Print the WHOLE prompt, not a slice. An earlier version truncated at
        # 1200 chars, which cut exactly the sections nobody had inspected yet --
        # the exemplars, the plot and the closing instruction. Two of the three
        # bugs found on 2026-08-11 were caught by reading a rendered artifact,
        # and a truncated artifact cannot be read.
        p = plots[0]
        for level in levels:
            r = researcher.retrieve(p["synopsis"], level)

            print(f"\n{'='*72}\nRETRIEVAL — {p['plot_id']} ({p['title_bn']}), level {level}")
            print(f"{'='*72}")
            print(f"synopsis: {len(p['synopsis'])} chars")
            print(f"retrieved {len(r.review_ids)} exemplars, "
                  f"mean {sum(len(t) for t in r.texts)/max(len(r.texts),1):.0f} chars:")
            for rid, t in zip(r.review_ids, r.texts):
                print(f"   {rid:12s} {t}")

            for arm in arms:
                prompt = render(plot=p["synopsis"], target_level=level,
                                arm=arm, exemplars=r.texts)
                print(f"\n{'-'*72}\nFULL PROMPT — arm {arm}, level {level} "
                      f"({len(prompt)} chars)\n{'-'*72}")
                print(prompt)
        print(f"\n{'='*72}")
        print("No API call made. Nothing written.")
        return 0

    done = completed_keys(out["generations_jsonl"])
    if done:
        print(f"resuming: {len(done)} generations already on disk")

    records: list[dict] = []
    for role, model in models.items():
        for arm in arms:
            writer = Writer(model, arm=arm, jsonl_path=out["generations_jsonl"])
            for p in plots:
                for level in levels:
                    key = generation_key(p["plot_id"], level, 1, arm, model)
                    if key in done:
                        continue
                    r = researcher.retrieve(p["synopsis"], level)
                    prompt = render(plot=p["synopsis"], target_level=level,
                                    arm=arm, exemplars=r.texts)
                    gen = writer.generate(prompt=prompt, plot_id=p["plot_id"],
                                          target_level=level, attempt=1)
                    records.append({"role": role, "model": model, "arm": arm,
                                    "key": gen.key, "text": gen.text,
                                    "rate_limits": gen.rate_limits})
                    print(f"  {role:6s} {arm} {p['plot_id']} L{level}  "
                          f"{gen.text[:44]!r}")

    # Re-read the whole archive so a resumed run scores everything, not only
    # what this invocation produced.
    all_gens = [
        json.loads(line)
        for line in Path(out["generations_jsonl"]).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    baseline = float(cfg["criterion"]["latin_char_baseline_pct"]) / 100.0
    cells: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for g in all_gens:
        cells[(g["model"], g["arm"])].append(g)

    # Every indexed review, to detect a generation that is a retrieved exemplar
    # copied verbatim. Spotted in the first run: BN016 L0 returned
    # "বাংলা সিনেমার মধ্যে ভালো একটা সিনেমা।", which is `bn_0230` exactly.
    # At level 0 copying is the cheap path -- short formulaic comments are easy
    # to echo and the Critic would pass them -- but a copied exemplar is not a
    # generation, and any realism metric computed over copies is measuring
    # retrieval. Counted rather than assumed, and reported per cell.
    corpus = {
        r["Movie Review"].strip()
        for r in csv.DictReader(open("data/cleaned/bn_clean.csv", encoding="utf-8"))
    }

    summary = {}
    for (model, arm), gens in sorted(cells.items()):
        fracs = [latin_fraction(g["text"]) for g in gens]
        confused = [f for f in fracs if f > baseline]
        copied = [g for g in gens if g["text"].strip() in corpus]
        by_level: dict[str, int] = {}
        for g in copied:
            k = f"L{g['target_level']}"
            by_level[k] = by_level.get(k, 0) + 1
        summary[f"{model}|{arm}"] = {
            "n": len(gens),
            "n_latin_above_baseline": len(confused),
            "max_latin_fraction": max(fracs) if fracs else 0.0,
            "mean_chars": sum(len(g["text"]) for g in gens) / len(gens) if gens else 0,
            "n_verbatim_corpus_copies": len(copied),
            "verbatim_copies_by_level": by_level,
            "verdict": "LANG_CONFUSION" if confused else "CLEAN",
        }

    # Rate limits, captured because the account tier was still unknown after the
    # /models preflight and it changes the runtime plan by ~40x.
    limits = next((g.get("rate_limits") for g in reversed(all_gens) if g.get("rate_limits")), {})

    result = {
        "NOT_A_RESULT": True,
        "banner": "Generator selection pilot. Selects a model; measures nothing.",
        "grid": {"models": models, "prompt_arms": arms,
                 "n_plots": len(plots), "levels": levels},
        "latin_baseline_fraction": baseline,
        "cells": summary,
        "observed_rate_limits": limits,
    }
    write_result(result, out["report_json"], config_path=args.config)

    lines = [
        "# S4 pilot — generator selection",
        "",
        "> ⛔ **NOT A RESULT.** This file selects a generator. It measures "
        "nothing, and nothing in it may be quoted in the thesis, a paper, or a "
        "results table. Decision rule pre-registered in `docs/protocol.md` "
        "§S4 decision 3, **before** any generation existed.",
        "",
        "| model | prompt arm | n | Latin above baseline | max Latin frac | mean chars | **verbatim corpus copies** | verdict |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for k, v in sorted(summary.items()):
        model, arm = k.split("|")
        lines.append(
            f"| `{model}` | {arm} | {v['n']} | {v['n_latin_above_baseline']} | "
            f"{v['max_latin_fraction']:.4f} | {v['mean_chars']:.0f} | "
            f"**{v['n_verbatim_corpus_copies']}** {v['verbatim_copies_by_level'] or ''} | "
            f"**{v['verdict']}** |"
        )
    lines += [
        "",
        f"Latin-script baseline: **{baseline:.4f}** of characters "
        "(region A `has_latin` = 0.09% / 0.00%, `results/s2e_regionA_k2_profile.md`), "
        "so any Latin script in a Bangla generation is signal.",
        "",
        "## What may be concluded",
        "",
        "- **If exactly one arm is `CLEAN`, it is selected**, and no quality "
        "claim is made either way.",
        "- **If both are `CLEAN`, the Bangla arm is retained as incumbent** — "
        "not because it won, but because 20 generations cannot separate arms on "
        "quality. Registered before the outputs were read.",
        "- **The model tie-break is a declared non-performance rule**: on `TIE`, "
        "lower cost and higher rate limit, and the thesis states that the data "
        "did not choose.",
        "",
        "",
        "## ⚠️ Verbatim corpus copies",
        "",
        "A generation whose text appears **exactly** in `bn_clean.csv` is a "
        "retrieved exemplar echoed back, not a generation. At level 0 this is "
        "the cheap path — short formulaic comments are easy to copy and the "
        "Critic would pass them — so the count is reported **by level**. Any "
        "realism metric computed over copies is measuring retrieval.",
        "",
        "🔴 **This is a pilot observation, not a measured rate.** It counts "
        "exact matches only; a near-copy with one word changed is not caught "
        "and would need an edit-distance check before Phase 5.",
        "",
        f"Observed rate limits: `{limits or 'none returned'}`",
    ]
    write_text_lf(out["report_md"], "\n".join(lines) + "\n")
    print(f"\nwrote {out['report_md']} and {out['report_json']}")
    for k, v in sorted(summary.items()):
        print(f"  {k:40s} {v['verdict']:15s} n={v['n']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
