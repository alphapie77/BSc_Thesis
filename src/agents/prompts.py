#!/usr/bin/env python3
"""The one prompt renderer. §5.1 row 1 and the loop are the same function.

This file exists to make open decision 10 unrepresentable rather than merely
satisfied. §5.1 row 1 (zero-shot, 1 call) **is** α_lo, the lower endpoint of
decision 19's τ objective, so if row 1's prompt stated the axis requirement less
fully than the loop's, the loop's measured "gain" would be partly the difference
between two prompts -- and τ* would inherit it. Huang et al. §5 document exactly
that artefact (81.8 standard vs 75.1 self-corrected, once the requirement was
stated up front).

So there is **one** renderer. Row 1 is `render(exemplars=(), feedback=None)`.
The two prompts cannot drift because there is nothing for them to drift from:
the shared text has a single source, and a test asserts the identity.

THE DEFINITION IS READ FROM DISK, NOT PASTED HERE
--------------------------------------------------
`docs/axis_definition.md` is the artifact §4.2 requires ("the axis-level
operational definition, verbatim from Phase 2"). Copying it into a docstring
would create a second copy, and this repo has now logged three separate
incidents of corrected and uncorrected text living in two places with only one
edited. The markers are parsed; if they are missing, this raises rather than
silently rendering a prompt with no definition in it -- which would look like a
working Writer producing bad generations.

TWO LANGUAGE ARMS, ONE STRUCTURE
--------------------------------
`protocol.md` §S4 and `docs/axis_definition.md` §3e register prompt language as
a pilot factor, not a decision: `2502.15603` and `2402.10588` support English
instructions, while `2606.08994` (language confusion) and `2606.19668`
(code-switching degrades) argue against a naive switch. **Invariant in both
arms: the exemplars are real Bangla, the plot is Bangla, and the output must be
Bangla.** Only the instruction wrapper changes.
"""

from __future__ import annotations

import re
from pathlib import Path

AXIS_DOC = Path(__file__).resolve().parents[2] / "docs" / "axis_definition.md"

_MARKERS = {
    "bn": ("<!-- AXIS_DEFINITION_BEGIN -->", "<!-- AXIS_DEFINITION_END -->"),
    "en": ("<!-- AXIS_DEFINITION_EN_BEGIN -->", "<!-- AXIS_DEFINITION_EN_END -->"),
}

#: §4.2 fixes ten exemplars. Repeated here only so a short retrieval is caught:
#: a prompt that is sometimes top-6 is a different prompt, and the variation
#: would land inside the generations without appearing in any config.
EXPECTED_EXEMPLARS = 10


#: The definition block headings are written with BENGALI digits (স্তর ০ / স্তর ১),
#: so the Bangla arm's target line must use them too. With ASCII digits the
#: prompt says "স্তর 1" while the section it refers to is headed "স্তর ১", and
#: the model is left to infer that those name the same thing. Caught by reading
#: the rendered prompt rather than by a test -- which is why the rendered prompt
#: is printed and inspected before any generation runs.
BN_DIGITS = {0: "০", 1: "১"}


class PromptContractError(RuntimeError):
    """Raised when the prompt cannot be built to specification."""


def load_definition(arm: str, *, path: Path | str = AXIS_DOC) -> str:
    """Extract one language arm's definition block from the docs artifact."""
    if arm not in _MARKERS:
        raise PromptContractError(f"arm must be one of {sorted(_MARKERS)}, got {arm!r}")
    begin, end = _MARKERS[arm]
    text = Path(path).read_text(encoding="utf-8")
    if begin not in text or end not in text:
        raise PromptContractError(
            f"markers {begin} / {end} not found in {path}. The prompt would "
            "otherwise render with no axis definition in it, which looks like a "
            "working Writer producing bad generations."
        )
    block = text.split(begin, 1)[1].split(end, 1)[0].strip()
    if not block:
        raise PromptContractError(f"{arm} definition block is empty in {path}.")
    # Strip markdown heading hashes: the model is being given an instruction,
    # not a document, and '###' is noise that varies with how the doc is edited.
    return re.sub(r"^#{1,6}\s*", "", block, flags=re.MULTILINE).strip()


_WRAPPER = {
    "bn": {
        "task": (
            "তুমি একজন সাধারণ বাংলাদেশি দর্শক। নিচের ছবিটি দেখে ফেসবুক বা "
            "ইউটিউবে যেমন মন্তব্য করতে, ঠিক তেমন একটি মন্তব্য লেখো।"
        ),
        "definition_header": "দুই ধরনের মন্তব্য হয়:",
        "target": "তোমাকে লিখতে হবে **স্তর {level}** ধরনের মন্তব্য।",
        "exemplars_header": "আসল দর্শকেরা এভাবে লেখেন — উদাহরণ:",
        "plot_header": "ছবির কাহিনি:",
        "retry_header": "তোমার আগের মন্তব্য:",
        "feedback_header": "যা ঠিক করতে হবে — ঠিক এই জিনিসগুলোই:",
        "closing": "শুধু মন্তব্যটি লেখো, বাংলায়। আর কিছু লিখো না।",
        # Registered 2026-08-16. IDENTICAL at both levels -- that is the whole
        # point: a different cap per level would re-tie length to level, by hand
        # this time. 20 is derived from region A, not chosen: level 0 averages
        # 13.12 words and level 1 averages 8.85, and the corpus median is 8.
        "length": "এক-দুই বাক্যে লেখো, ২০ শব্দের মধ্যে।",
    },
    "en": {
        "task": (
            "You are an ordinary Bangladeshi viewer. Write the kind of comment "
            "you would leave on Facebook or YouTube after watching the film below."
        ),
        "definition_header": "There are two kinds of comment:",
        "target": "You must write a **Level {level}** comment.",
        "exemplars_header": "This is how real viewers write — examples:",
        "plot_header": "The film's story:",
        "retry_header": "Your previous comment:",
        "feedback_header": "Fix exactly these issues:",
        "closing": "Write only the comment, in Bangla. Nothing else.",
        "length": "Write one or two sentences, at most 20 words.",
    },
}


def render(
    *,
    plot: str,
    target_level: int,
    arm: str = "bn",
    exemplars: tuple[str, ...] = (),
    previous_draft: str | None = None,
    feedback: str | None = None,
    definition: str | None = None,
    strict_exemplar_count: bool = True,
    length_controlled: bool = False,
) -> str:
    """Build the Writer's prompt. §5.1 row 1 is this with no exemplars, no feedback.

    Section order is §4.2's, unchanged: [definition] + [exemplars] + [plot], and
    on retry + [previous draft + feedback]. The order is part of the contract
    because the appendix prints these verbatim and a reordered prompt is a
    different experimental condition.

    `length_controlled` appends ONE sentence, identical at both levels, capping
    the comment at 20 words. Registered 2026-08-16 after the free-length run
    measured level-1 outputs at 38-40 mean words against level-0's 6-13, so that
    **length alone separated the levels at AUC 0.9894 (bn) and 1.0000 (en)** and
    no length-matched slice could be built from them -- 0 matched pairs under
    `2607.18508`'s criterion, in either arm. The clause is a FACTOR, not a
    replacement: the free-length archive is retained as the condition that
    measures what the model does when left alone, which is to read "specific" as
    "long" -- the inversion of the corpus, and what `kapur2026length` predicted.

    ⚠️ `2601.01768` finds LLMs track their own output length poorly, so the
    clause is expected to shift the distribution rather than enforce a bound.
    That is why the achieved lengths and the matched-slice size are both
    reported: the control is measured, never assumed to have worked.
    """
    w = _WRAPPER[arm] if arm in _WRAPPER else None
    if w is None:
        raise PromptContractError(f"arm must be one of {sorted(_WRAPPER)}, got {arm!r}")
    if target_level not in (0, 1):
        raise PromptContractError(
            f"target_level must be 0 or 1 (K=2 since 2026-08-03), got {target_level!r}"
        )
    if exemplars and strict_exemplar_count and len(exemplars) != EXPECTED_EXEMPLARS:
        raise PromptContractError(
            f"§4.2 fixes {EXPECTED_EXEMPLARS} exemplars; got {len(exemplars)}. "
            "A prompt of a different length is a different prompt, and the "
            "variation would not appear in any config."
        )

    definition = definition if definition is not None else load_definition(arm)

    # The target level goes AFTER the definition, not before it. The definition
    # describes both levels; naming the target first would have the model read
    # the contrast already knowing which side it is on, and the level-0
    # description would then read as a list of things to avoid -- i.e. it would
    # become the negative constraint that `2601.08070` says backfires, smuggled
    # in by ordering rather than by wording.
    parts = [
        w["task"],
        "",
        w["definition_header"],
        definition,
        "",
        w["target"].format(
            level=BN_DIGITS[target_level] if arm == "bn" else target_level
        ),
    ]

    if exemplars:
        parts += ["", w["exemplars_header"]]
        parts += [f"- {e.strip()}" for e in exemplars]

    parts += ["", w["plot_header"], plot.strip()]

    # Retry block last, so that everything before it is byte-identical to the
    # attempt-1 prompt. That is what makes the loop's added information
    # inspectable: the diff between attempts is exactly this block.
    if previous_draft is not None or feedback is not None:
        if previous_draft is not None:
            parts += ["", w["retry_header"], previous_draft.strip()]
        if feedback is not None:
            parts += ["", w["feedback_header"], feedback.strip()]

    # Length clause immediately before the closing instruction, so the two
    # instructions about *form* sit together and nothing between the plot and
    # the closing changes between conditions except this one line. The diff
    # between a free-length and a length-controlled prompt is therefore exactly
    # one sentence, which is what makes it a factor rather than a rewrite.
    if length_controlled:
        parts += ["", w["length"]]

    parts += ["", w["closing"]]
    return "\n".join(parts)


def row1_prompt(*, plot: str, target_level: int, arm: str = "bn") -> str:
    """§5.1 row 1 -- zero-shot, one call. Defined in terms of `render`, on purpose.

    Not a separate template. If this were its own string, decision 10 would be a
    thing to remember rather than a property of the code, and Huang et al. §5's
    artefact would be one careless edit away.
    """
    return render(plot=plot, target_level=target_level, arm=arm)
