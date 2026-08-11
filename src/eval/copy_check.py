#!/usr/bin/env python3
"""Is a generation a retrieved exemplar wearing a disguise?

The pilot's first run produced `"বাংলা সিনেমার মধ্যে ভালো একটা সিনেমা।"` for
BN016 at level 0 — **`bn_0230`, verbatim**, and one of the ten exemplars shown
in that very prompt. Exact-match counting caught it. It would not catch the same
comment with one word changed, and there is no reason to expect a model to copy
exactly rather than approximately.

WHY THIS MATTERS MORE THAN IT LOOKS
-----------------------------------
A copied exemplar **passes the Critic by construction**. Verifier-A was trained
on exactly these reviews, so a real corpus review is the highest-scoring thing
the loop can emit. So the system could report an excellent first-attempt pass
rate, a healthy τ frontier and strong §5.4 realism — while doing retrieval.
**Every one of those numbers would be measuring the corpus against itself.**

⚠️ This is close to, but not the same as, RQ5's Goodhart test. Gaming means
exploiting the verifier's blind spots; copying means bypassing generation
entirely. Both inflate the same metrics and they need separating in the write-up,
so the copy rate is reported **beside** the A−B gap rather than folded into it.

WHAT COUNTS AS A COPY, AND WHAT DOES NOT
-----------------------------------------
Token-level Jaccard against the exemplars **actually shown in that prompt**, not
against the whole corpus. A generation resembling some unrelated review is a
coincidence of a small, formulaic domain; resembling one of the ten it was just
shown is the failure mode. Both are reported, because the difference between
them is itself informative.

No threshold is baked in. The distribution is reported and the reader sets the
line — a cutoff here would be a decision constant with no criterion, which is
the defect this project spent 2026-08-11 removing.
"""

from __future__ import annotations

import re

_TOKEN = re.compile(r"\S+")


def tokens(text: str) -> set[str]:
    """Whitespace tokens, lowercased. No stemming, no stopword removal.

    Inviolable rule 7 forbids both, and they would be wrong here anyway: the
    question is whether one string was copied from another, and normalising the
    two toward each other is precisely the wrong direction.
    """
    return {t.lower() for t in _TOKEN.findall(text or "")}


def jaccard(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def max_similarity(text: str, candidates: list[str]) -> tuple[float, int]:
    """Closest candidate and its index. (0.0, -1) when there are none."""
    best, idx = 0.0, -1
    for i, c in enumerate(candidates):
        s = jaccard(text, c)
        if s > best:
            best, idx = s, i
    return best, idx


def report(
    generations: list[dict],
    exemplars_by_key: dict[str, list[str]],
    corpus: list[str],
) -> dict:
    """Copy statistics for a set of generations.

    `exemplars_by_key` maps a generation key to the ten exemplars its prompt
    contained. Missing keys fall back to corpus-wide comparison, and the two
    populations are reported separately rather than merged.
    """
    exact = 0
    shown_sims: list[float] = []
    corpus_sims: list[float] = []
    by_level: dict[int, list[float]] = {}

    corpus_set = {c.strip() for c in corpus}

    for g in generations:
        text = (g.get("text") or "").strip()
        level = int(g.get("target_level", -1))
        if text in corpus_set:
            exact += 1

        shown = exemplars_by_key.get(g.get("key", ""))
        if shown:
            s, _ = max_similarity(text, shown)
            shown_sims.append(s)
            by_level.setdefault(level, []).append(s)
        c, _ = max_similarity(text, corpus[:2000])
        corpus_sims.append(c)

    def stats(xs: list[float]) -> dict:
        if not xs:
            return {"n": 0}
        xs = sorted(xs)
        return {
            "n": len(xs),
            "mean": sum(xs) / len(xs),
            "median": xs[len(xs) // 2],
            "p90": xs[int(0.9 * (len(xs) - 1))],
            "max": xs[-1],
        }

    return {
        "n_generations": len(generations),
        "n_exact_corpus_matches": exact,
        "similarity_to_exemplars_shown": stats(shown_sims),
        "similarity_to_corpus_sample": stats(corpus_sims),
        "similarity_to_exemplars_by_level": {
            str(k): stats(v) for k, v in sorted(by_level.items())
        },
        "note": (
            "Token Jaccard. No threshold is applied: the distribution is the "
            "report and the reader draws the line. Similarity to the exemplars "
            "SHOWN is the failure mode; similarity to unrelated corpus reviews "
            "is a property of a small formulaic domain and is reported for "
            "contrast, not as evidence of copying."
        ),
    }
