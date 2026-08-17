#!/usr/bin/env python3
"""Attempt-1 generations on the 30 dev-plots. The input `w` and τ are fitted on.

WHY THIS IS A SEPARATE SCRIPT FROM `run_pilot.py`
--------------------------------------------------
The pilot answers *which generator*; this answers nothing at all. It produces the
substrate that `w` (protocol.md §S4 decision 1) and τ (decision 2, and decision
19's argmax) are estimated from, and neither may be estimated from the 82 human
dev rows: `kapur2026length` show the length/specificity relation is flat or
reversed in machine text, which is the whole reason the fit moved off dev-82.

WHAT IS DELIBERATELY ABSENT
---------------------------
**No Critic and no Reflector.** The Critic takes `w` and τ as required arguments
with no defaults, and both are unknown until these generations exist. Running the
loop here would mean choosing a `w` in order to fit `w`. Attempt 1 only.

WHAT THESE GENERATIONS ARE ALLOWED TO BE USED FOR
--------------------------------------------------
1. Fitting `w` as a sensitivity curve (decision 1) and τ (decisions 2, 19).
2. **§5.1 row 1 evidence, hence α_lo.** `prompts.render()` is the one template
   shared with the loop's attempt 1 (decision 5), so row-1 parity holds by
   construction rather than by audit.

They are NOT a quality result and no model claim rests on them.

REPORTED BESIDE THE GENERATIONS, BECAUSE IT WAS REGISTERED BEFORE THEY EXISTED
------------------------------------------------------------------------------
- **Mean length per target level** (`docs/axis_definition.md` §3c). If level-1
  generations are shorter than level-0 by roughly the corpus gap (13.12 → 8.85
  mean words), axis control **may not be claimed as specificity** — it may be
  length. This is a pre-registered diagnostic, not a post-hoc check.
- **Verbatim exemplar copying.** The first Groq run emitted `bn_0230` exactly.
  A copied exemplar is not a generation, and any realism metric over copies
  measures retrieval.
- **Non-Bangla script leakage**, split by prompt-language arm.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.prompts import render  # noqa: E402
from src.agents.researcher import Researcher  # noqa: E402
from src.agents.run_pilot import latin_fraction, load_dev_plots  # noqa: E402
from src.agents.writer import completed_keys, generation_key  # noqa: E402
from src.common.provenance import write_result, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402

#: Devanagari and Malayalam ranges, minus U+0964/U+0965 (danda, double danda),
#: which Bangla shares and the corpus uses. Counting the danda as foreign script
#: was the first version's bug: it made 18 of 20 generations look "confused"
#: when the actual leak rate was 1 in 20.
_DANDA = {0x0964, 0x0965}


def foreign_script_chars(text: str) -> dict[str, int]:
    """Non-Bangla letters by script. Latin, Devanagari, Malayalam."""
    out: dict[str, int] = defaultdict(int)
    for ch in text:
        o = ord(ch)
        if o in _DANDA:
            continue
        if 0x0900 <= o <= 0x097F:
            out["devanagari"] += 1
        elif 0x0D00 <= o <= 0x0D7F:
            out["malayalam"] += 1
        elif ("A" <= ch <= "Z") or ("a" <= ch <= "z"):
            out["latin"] += 1
    return dict(out)


def length_only_auc(l1: list[int], l0: list[int]) -> float:
    """P(a level-1 generation is longer than a level-0 one), ties at 0.5.

    The content-blind probe of `2607.18508` §4.1, reduced to its one usable
    feature here: we have a single generator, so their *generator-identity*
    shortcut cannot exist and length is the whole of it. **0.5 is no signal;
    1.0 means the target level is fully recoverable from a word count.**

    Reported beside every axis-level number, always. The free-length run scored
    0.9894 (bn) and 1.0000 (en), and the pre-registered length diagnostic still
    returned a pass — because it fixed a direction. A quantity with no direction
    in it cannot fail that way.
    """
    if not l1 or not l0:
        return float("nan")
    s = sum(1.0 if a > b else 0.5 if a == b else 0.0 for a in l1 for b in l0)
    return s / (len(l1) * len(l0))


def matched_pairs(pairs: list[tuple[int, int]], tol: float) -> int:
    """Pairs whose two lengths are within `tol` of the longer. `2607.18508` §3.

    Zero means **no length-matched evaluation is possible** on this archive, and
    that is a finding rather than a missing table: it says every level-1 output
    is longer than its level-0 counterpart by more than the tolerance, with no
    exceptions to build a slice from.
    """
    return sum(1 for a, b in pairs if abs(a - b) < tol * max(a, b))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="configs/s4_devplots.yaml")
    ap.add_argument("--dry-run", action="store_true",
                    help="Render prompts and print them; generate nothing.")
    ap.add_argument("--model-path", action="append", default=[], metavar="ARM=PATH",
                    help="Where an arm's weights load from (a Kaggle Models "
                         "mount). Load location only: identity, and every "
                         "generation key, still come from the config's model id.")
    args = ap.parse_args()

    set_seed()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    out = cfg["outputs"]
    plots = load_dev_plots(int(cfg["sample"]["n_plots"]))
    levels = list(cfg["sample"]["levels"])
    arms = list(cfg["prompt_arms"])
    models = dict(cfg["models"])
    provider = cfg.get("provider", "local")
    # One factor, one flag. False for the free-length archive, true for the
    # length-controlled one; the two configs differ by this and nothing else.
    length_controlled = bool(cfg.get("prompt_length_controlled", False))
    if length_controlled:
        print("prompt: LENGTH-CONTROLLED "
              f"(<= {cfg.get('length_cap_words')} words, identical at both levels)")

    if len(plots) != int(cfg["sample"]["n_plots"]):
        raise SystemExit(
            f"expected {cfg['sample']['n_plots']} dev plots, found {len(plots)} — "
            "the frozen plots split changed, which it must not have"
        )

    idx = yaml.safe_load(Path("configs/s4_index.yaml").read_text(encoding="utf-8"))["index"]
    # CPU: see Researcher.__init__. LaBSE must not hold VRAM while a 12B
    # generator loads beside it on a 16 GB card.
    researcher = Researcher(idx["persist_dir"], idx["collection"], idx["encoder"],
                            device="cpu")

    total = len(models) * len(arms) * len(plots) * len(levels)
    print(f"grid: {len(models)} model x {len(arms)} prompt arms x "
          f"{len(plots)} plots x {len(levels)} levels = {total} generations")

    if args.dry_run:
        p = plots[0]
        for level in levels:
            r = researcher.retrieve(p["synopsis"], level)
            for arm in arms:
                prompt = render(plot=p["synopsis"], target_level=level,
                                arm=arm, exemplars=r.texts,
                                length_controlled=length_controlled)
                print(f"\n{'-'*72}\nFULL PROMPT — {p['plot_id']}, arm {arm}, "
                      f"level {level} ({len(prompt)} chars)\n{'-'*72}")
                print(prompt)
        print("\nNothing generated, nothing written.")
        return 0

    model_paths = {}
    for spec in args.model_path:
        role, _, path = spec.partition("=")
        if not path:
            raise SystemExit(f"--model-path expects ARM=PATH, got: {spec!r}")
        if role not in models:
            raise SystemExit(f"--model-path role {role!r} not in {sorted(models)}")
        model_paths[role] = path

    done = completed_keys(out["generations_jsonl"])
    if done:
        print(f"resuming: {len(done)} generations already on disk")

    # ALL retrieval first, then the encoder is released, then the generator
    # loads. Retrieval depends on nothing the generator produces (attempt 1 has
    # no feedback), so interleaving them only means holding two models at once.
    # Doing it in one pass also makes every prompt exist before any generation
    # does, which is the order the dry-run already prints in.
    print("retrieving exemplars for every (plot, level) ...", flush=True)
    prompts: dict[tuple[str, int, str], str] = {}
    for p in plots:
        for level in levels:
            r = researcher.retrieve(p["synopsis"], level)
            for arm in arms:
                prompts[(p["plot_id"], level, arm)] = render(
                    plot=p["synopsis"], target_level=level, arm=arm,
                    exemplars=r.texts, length_controlled=length_controlled)
    del researcher
    import gc
    gc.collect()
    try:
        import torch
        torch.cuda.empty_cache()
    except Exception:
        pass
    print(f"  {len(prompts)} prompts built; retrieval encoder released")

    import time as _time
    started = _time.monotonic()
    n_done = len(done)
    for role, model in models.items():
        pending = [
            1 for arm in arms for p in plots for level in levels
            if generation_key(p["plot_id"], level, 1, arm, model,
                              provider=provider) not in done
        ]
        if not pending:
            print(f"{role}: all generations on disk; model not loaded")
            continue
        if provider == "local":
            from src.agents.local_writer import LocalWriter  # heavy; deferred
            writer = LocalWriter(
                model, arm=arms[0], jsonl_path=out["generations_jsonl"],
                batch_size=int(cfg["batch_size"]),
                quantization=cfg.get("quantization"),
                max_new_tokens=int(cfg["max_new_tokens"]),
                model_path=model_paths.get(role),
            )
        else:
            from src.agents.writer import Writer
            writer = Writer(model, arm=arms[0], jsonl_path=out["generations_jsonl"])

        for arm in arms:
            writer.arm = arm
            for p in plots:
                for level in levels:
                    key = generation_key(p["plot_id"], level, 1, arm, model,
                                         provider=provider)
                    if key in done:
                        continue
                    prompt = prompts[(p["plot_id"], level, arm)]
                    gen = writer.generate(prompt=prompt, plot_id=p["plot_id"],
                                          target_level=level, attempt=1)
                    n_done += 1
                    elapsed = _time.monotonic() - started
                    rate = (n_done - len(done)) / max(elapsed, 1e-9)
                    remaining = (total - n_done) / rate if rate > 0 else 0
                    print(f"  [{n_done:3d}/{total}] {arm} {p['plot_id']} L{level}  "
                          f"eta {remaining/60:4.1f}m  {gen.text[:40]!r}", flush=True)
        if provider == "local":
            import gc

            import torch
            del writer
            gc.collect()
            torch.cuda.empty_cache()

    # ---- report -----------------------------------------------------------
    # Deduplicate by key on read. The pilot's archive carries 20 duplicate keys
    # from the 2026-08-12 resume bug; the archive is append-only, so every
    # consumer deduplicates rather than the file being rewritten.
    seen: set[str] = set()
    gens: list[dict] = []
    for line in Path(out["generations_jsonl"]).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        g = json.loads(line)
        if g["key"] in seen:
            continue
        seen.add(g["key"])
        gens.append(g)

    corpus = {
        r["Movie Review"].strip()
        for r in csv.DictReader(open("data/cleaned/bn_clean.csv", encoding="utf-8"))
    }
    baseline = float(cfg["report"]["latin_char_baseline_pct"]) / 100.0

    # The pre-registered length diagnostic (axis_definition.md §3c). Reported
    # per prompt arm as well as pooled, because the arm is a factor.
    lengths: dict[str, list[int]] = defaultdict(list)
    cells: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for g in gens:
        cells[(g["arm"], g["target_level"])].append(g)
        lengths[f"{g['arm']}|L{g['target_level']}"].append(len(g["text"].split()))

    per_cell = {}
    for (arm, level), rows in sorted(cells.items()):
        wl = [len(r["text"].split()) for r in rows]
        leaks = [foreign_script_chars(r["text"]) for r in rows]
        per_cell[f"{arm}|L{level}"] = {
            "n": len(rows),
            "mean_words": statistics.mean(wl) if wl else 0.0,
            "median_words": statistics.median(wl) if wl else 0,
            "n_truncated": sum(1 for r in rows if r.get("finish_reason") == "length"),
            "n_with_foreign_script": sum(1 for f in leaks if f),
            "n_latin_above_baseline": sum(
                1 for r in rows if latin_fraction(r["text"]) > baseline),
            "n_verbatim_corpus_copies": sum(
                1 for r in rows if r["text"].strip() in corpus),
        }

    # The registered diagnostic's own number: the level gap, against the corpus
    # gap of 13.12 -> 8.85 mean words (= 4.27). Computed, never eyeballed.
    gaps = {}
    for arm in arms:
        a = per_cell.get(f"{arm}|L0", {}).get("mean_words")
        b = per_cell.get(f"{arm}|L1", {}).get("mean_words")
        if a is not None and b is not None:
            gaps[arm] = a - b
    CORPUS_GAP = 13.12 - 8.85  # ref: docs/axis_definition.md §3, from the data

    # The two quantities the free-length run needed and did not have. Both are
    # direction-free, which is precisely why they survive an outcome the
    # registered diagnostic was written the wrong way round to catch.
    tol = float(cfg["report"].get("matched_slice_tolerance", 0.15))
    probe: dict[str, float] = {}
    matched: dict[str, int] = {}
    for arm in arms:
        by_plot: dict[str, dict[int, int]] = defaultdict(dict)
        for g in gens:
            if g["arm"] == arm:
                by_plot[g["plot_id"]][g["target_level"]] = len(g["text"].split())
        pairs = [(v[0], v[1]) for v in by_plot.values() if 0 in v and 1 in v]
        probe[arm] = length_only_auc([p[1] for p in pairs], [p[0] for p in pairs])
        matched[arm] = matched_pairs(pairs, tol)

    result = {
        "NOT_A_RESULT": True,
        "banner": "Attempt-1 dev-plot generations. The substrate `w` and τ are "
                  "fitted on. No Critic ran; no quality claim is made here.",
        "grid": {"models": models, "prompt_arms": arms,
                 "n_plots": len(plots), "levels": levels},
        "n_generations": len(gens),
        "per_cell": per_cell,
        "level_length_gap_words": gaps,
        "corpus_level_gap_words": CORPUS_GAP,
        "length_diagnostic": {
            arm: ("LENGTH_MAY_EXPLAIN_LEVEL" if g >= CORPUS_GAP else "GAP_BELOW_CORPUS")
            for arm, g in gaps.items()
        },
        "prompt_length_controlled": length_controlled,
        "length_cap_words": cfg.get("length_cap_words"),
        "length_only_auc": probe,
        "matched_pairs": matched,
        "matched_slice_tolerance": tol,
        # The verdict that supersedes `length_diagnostic` for any axis-control
        # claim. Direction-free, so the 2026-08-16 failure mode cannot recur.
        "length_confound": {
            arm: ("LENGTH_RECOVERS_LEVEL" if a >= 0.90 else
                  "LENGTH_PARTIAL" if a >= 0.70 else "LENGTH_WEAK")
            for arm, a in probe.items()
        },
    }
    write_result(result, out["report_json"], config_path=args.config)

    lines = [
        "# S4.dev — attempt-1 generations on the 30 dev-plots"
        + (" (LENGTH-CONTROLLED)" if length_controlled else " (free length)"),
        "",
        "> ⛔ **NOT A RESULT.** These generations are the substrate `w` "
        "(`protocol.md` §S4 decision 1) and τ (decisions 2, 19) are fitted on. "
        "No Critic ran — it requires both, and both are unknown until this file "
        "exists. Attempt 1 only; no loop, no Reflector.",
        "",
        "| prompt arm | level | n | mean words | median | truncated | foreign script | Latin > baseline | verbatim copies |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for k, v in per_cell.items():
        arm, level = k.split("|")
        lines.append(
            f"| {arm} | {level} | {v['n']} | {v['mean_words']:.1f} | "
            f"{v['median_words']} | {v['n_truncated']} | "
            f"{v['n_with_foreign_script']} | {v['n_latin_above_baseline']} | "
            f"**{v['n_verbatim_corpus_copies']}** |"
        )
    lines += [
        "",
        "## The pre-registered length diagnostic",
        "",
        "Registered in `docs/axis_definition.md` §3c **before any generation "
        "existed**: if level-1 generations are shorter than level-0 by an amount "
        f"comparable to the corpus gap (**{CORPUS_GAP:.2f}** mean words, "
        "13.12 → 8.85), then axis control **may not be claimed as specificity** "
        "— it may be length.",
        "",
        "| prompt arm | L0 − L1 mean words | verdict |",
        "|---|---|---|",
    ]
    for arm, g in gaps.items():
        v = "🔴 `LENGTH_MAY_EXPLAIN_LEVEL`" if g >= CORPUS_GAP else "`GAP_BELOW_CORPUS`"
        lines.append(f"| {arm} | {g:+.2f} | {v} |")
    lines += [
        "",
        "⚠️ A verdict of `GAP_BELOW_CORPUS` does **not** establish that the "
        "distinction is specificity. It establishes only that the length "
        "explanation is not as strong here as in the human corpus. The construct "
        "claim rests on RQ1-H's human validation, not on this table.",
        "",
        "🔴 **And on 2026-08-16 that verdict was UNINFORMATIVE.** The rule above "
        "fixes a *direction* — it asks whether level 1 came out shorter — and the "
        "free-length run produced the opposite: level 1 was 25–34 words *longer*. "
        "The test passed while the confound it exists to catch was at its "
        "strongest. The table below replaces it for any axis-control claim, "
        "because it has no direction in it.",
        "",
        "## The length confound, measured without a direction",
        "",
        "**Content-blind probe** (`2607.18508` §4.1): P(a level-1 generation is "
        "longer than a level-0 one). **0.5 = length says nothing about the level; "
        "1.0 = the level is fully recoverable from a word count.** "
        "**Matched pairs**: same-plot L0/L1 pairs within "
        f"{tol:.0%} of the longer — the slice any length-neutral claim would have "
        "to be made on. **Zero means no such claim can be made at all.**",
        "",
        f"Prompt length control: **{'ON' if length_controlled else 'OFF'}**"
        + (f" (≤ {cfg.get('length_cap_words')} words, identical at both levels)"
           if length_controlled else " (free length)"),
        "",
        "| prompt arm | length-only AUC | verdict | matched pairs (of 30) |",
        "|---|---|---|---|",
    ]
    for arm in arms:
        a = probe.get(arm, float("nan"))
        v = ("🔴 `LENGTH_RECOVERS_LEVEL`" if a >= 0.90 else
             "⚠️ `LENGTH_PARTIAL`" if a >= 0.70 else "`LENGTH_WEAK`")
        lines.append(f"| {arm} | {a:.4f} | {v} | **{matched.get(arm, 0)}** |")
    lines += [
        "",
        "Reference — the **free-length** run of 2026-08-16: AUC **0.9894** (bn) "
        "and **1.0000** (en), **0** matched pairs in either arm. In the en arm "
        "the ranges did not overlap at all (longest L0 = 15 words, shortest "
        "L1 = 25), so no length-matched evaluation existed to be run.",
        "",
        "⚠️ `2601.01768` finds LLMs track their own output length poorly, so a "
        "length clause is expected to shift the distribution rather than enforce "
        "a bound. **If the AUC stays ≥ 0.90 and the matched slice stays empty, "
        "the control FAILED** — and that is reported as a failure, not softened.",
        "",
        "## Non-Bangla script",
        "",
        "The danda (`U+0964`) is **excluded** from the foreign-script count: "
        "Bangla shares it and the corpus uses it. Counting it was the first "
        "version's bug, and it inflated the pilot's apparent leak rate from "
        "1-in-20 to 18-in-20.",
    ]
    write_text_lf(out["report_md"], "\n".join(lines) + "\n")
    print(f"\nwrote {out['report_md']} and {out['report_json']}")
    for k, v in per_cell.items():
        print(f"  {k:8s} n={v['n']:3d}  mean_words={v['mean_words']:5.1f}  "
              f"trunc={v['n_truncated']}  copies={v['n_verbatim_corpus_copies']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
