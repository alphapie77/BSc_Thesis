#!/usr/bin/env python3
"""Reflector -- error-localised feedback. §4.2 component 4, FAIL only.

§4.2: "not random critique but **which symbolic rules failed** + which level the
neural confidence leaned toward, rendered in natural language." Two halves, and
the split matters:

* **Which rules failed is computed, not asked.** `failed_rules()` is
  deterministic -- it decomposes the symbolic score into per-feature signed
  contributions and returns the ones pushing away from the target level. This is
  the single thing the symbolic half provides that the LaBSE probe cannot, and
  §S3.5 registers interpretability (not accuracy) as the reason it is retained
  at all.
* **Only the rendering is generative**, and it is a small call.

⚠️ A REGISTERED HAZARD, NOT AN OVERSIGHT
----------------------------------------
Telling the Writer which rule failed is close to handing it the rubric.
`mahmoud2026rubric` found rubric-based judges preferred the RL checkpoint on
85.8% of prompts while rubric-free judges preferred the BASE model on 78.4% --
gains concentrated in presence-based criteria, losses everywhere else -- and
named the mechanism "hacking the rubric, not the verifier". **Our §3.5 pool is
almost entirely presence/count-based, and our design is strictly worse than
theirs: their policies had to discover the rubric, ours is handed it.**

This is already logged (protocol.md, 2026-08-11, RQ3 row) with the consequence
pre-registered: **symbolic scores rising across attempts while Verifier-B stays
flat is the gaming signature**, and it is evidence for RQ5 rather than a
surprise. The Reflector implements §4.2 as specified; the risk is instrumented,
not designed away.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.symbolic.features import FeatureSpec, extract, feature_names  # noqa: E402
from src.symbolic.s35_scorer import FAMILY, GAMEABLE  # noqa: E402

#: How many failing rules to name. Not a tuning knob: Tyen et al. 2024 and the
#: Self-Refine ablation both find error-LOCALISED feedback beats generic, and a
#: list naming every one of eleven features is generic again by volume.
#: Three is the smallest number that can express a pattern rather than a point.
#: ref: docs/research_pipeline_en.md §4.2 (justification paragraph)
MAX_RULES_NAMED = 3


@dataclass(frozen=True)
class FailedRule:
    feature: str
    family: str
    contribution: float  # signed, negative = pushing away from the target level
    gameable: bool


def failed_rules(
    critic,
    draft: str,
    target_level: int,
    *,
    limit: int = MAX_RULES_NAMED,
) -> list[FailedRule]:
    """Which symbolic features pushed this draft away from the target level.

    Decomposition, not attribution-by-ablation: the symbolic model is a linear
    logistic on standardised features, so `coef * z` IS the exact per-feature
    contribution to the logit. Nothing is estimated and nothing is re-fitted,
    which keeps this deterministic -- the Critic must stay a tool, not a judge
    with opinions (CRITIC, ICLR 2024).
    """
    spec = FeatureSpec(enable_f1=False)
    names = feature_names(spec)
    pipe = critic._symbolic
    scaler = pipe.named_steps["standardscaler"]
    lr = pipe.named_steps["logisticregression"]

    values = [extract(draft, spec)[n] for n in names]
    z = [(v - m) / s for v, m, s in zip(values, scaler.mean_, scaler.scale_)]
    contributions = [float(c) * float(zi) for c, zi in zip(lr.coef_[0], z)]

    # A positive logit contribution pushes toward level 1. If the target is
    # level 0, the sign flips -- the same arithmetic the Critic uses to score
    # P(y = target_level) rather than p(level 1).
    signed = [c if target_level == 1 else -c for c in contributions]

    failing = [
        FailedRule(
            feature=n,
            family=FAMILY[n],
            contribution=s,
            gameable=FAMILY[n] in GAMEABLE,
        )
        for n, s in zip(names, signed)
        if s < 0
    ]
    failing.sort(key=lambda r: r.contribution)
    return failing[:limit]


_RENDER_PROMPT = {
    "bn": (
        "নিচের মন্তব্যটি একটি স্বয়ংক্রিয় যাচাইয়ে পাশ করেনি।\n\n"
        "মন্তব্য:\n{draft}\n\n"
        "যা চাওয়া হয়েছিল: স্তর {level} ধরনের মন্তব্য।\n"
        "যাচাইয়ে যে দিকগুলো দুর্বল এসেছে: {rules}\n"
        "স্বয়ংক্রিয় স্কোর ঝুঁকেছে অন্য স্তরের দিকে।\n\n"
        "এক বা দুই বাক্যে লেখো, ঠিক কী বদলালে মন্তব্যটি স্তর {level} হবে। "
        "নতুন মন্তব্য লিখো না — শুধু নির্দেশনা দাও, বাংলায়।"
    ),
    "en": (
        "The comment below did not pass an automated check.\n\n"
        "Comment:\n{draft}\n\n"
        "What was asked for: a Level {level} comment.\n"
        "Aspects the check found weak: {rules}\n"
        "The automated score leaned toward the other level.\n\n"
        "In one or two sentences, say exactly what to change so the comment "
        "becomes Level {level}. Do not write a new comment — give instructions "
        "only, in Bangla."
    ),
}

#: Human-readable names, so the feedback names a property rather than a column.
#: "connective_frac is low" is not actionable; "no connecting words" is.
_FEATURE_BN = {
    "n_tokens": "মন্তব্যের দৈর্ঘ্য",
    "mean_word_chars": "শব্দের গড় দৈর্ঘ্য",
    "punct_per_tok": "যতিচিহ্নের ব্যবহার",
    "digit_per_tok": "সংখ্যার ব্যবহার",
    "latin_per_tok": "ইংরেজি অক্ষরের ব্যবহার",
    "ends_dandi": "দাঁড়ি দিয়ে শেষ করা",
    "connective_frac": "সংযোজক শব্দ (কিন্তু, তবে, কারণ)",
    "pos_frac": "ইতিবাচক শব্দের অনুপাত",
    "neg_frac": "নেতিবাচক শব্দের অনুপাত",
    "intensifier_frac": "জোরালো বিশেষণ (খুব, অসাধারণ)",
    "guiraud": "শব্দভাণ্ডারের বৈচিত্র্য",
}


def render_feedback_prompt(
    draft: str, target_level: int, rules: list[FailedRule], *, arm: str = "bn"
) -> str:
    named = ", ".join(_FEATURE_BN.get(r.feature, r.feature) for r in rules) or "—"
    return _RENDER_PROMPT[arm].format(draft=draft.strip(), level=target_level, rules=named)


class Reflector:
    """Renders computed failures into instructions. FAIL only, never on PASS."""

    def __init__(self, generate_fn, *, arm: str = "bn"):
        # Injected rather than constructed: the Reflector is a small call on the
        # same transport as the Writer, and duplicating the retry/backoff logic
        # would let the two drift apart on exactly the behaviour that matters
        # when a 30-hour run meets a 429.
        self._generate = generate_fn
        self._arm = arm

    def reflect(self, critic, draft: str, target_level: int, **kw) -> tuple[str, list[str]]:
        rules = failed_rules(critic, draft, target_level)
        prompt = render_feedback_prompt(draft, target_level, rules, arm=self._arm)
        feedback = self._generate(
            prompt=prompt, target_level=target_level, **kw
        )
        return feedback, [r.feature for r in rules]
