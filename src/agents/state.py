#!/usr/bin/env python3
"""The loop's state object -- SS4.1, and nothing beyond it.

No LLM call, no model, no retrieval. This module exists so that the four
components in SS4.2 agree on what they are passing each other before any of them
is written, and so that `trace` is a guarantee rather than an intention.

WHY `trace` IS NOT OPTIONAL
---------------------------
SS4.1 says "trace: list[full snapshot of every previous attempt] -- nothing is
lost", and SS4.6 then wants the attempt distribution, the per-attempt score
growth, and a hand-coded taxonomy of 50 three-time failures. **Those analyses
are impossible to reconstruct after the fact.** If an attempt overwrites the
draft in place, the failed drafts -- which ARE the raw material of the failure
taxonomy -- are gone, and the only way to get them back is to pay for every
generation a second time.

So `advance()` snapshots before it mutates, and the snapshot is a deep copy.
A shallow copy would leave every trace entry pointing at the same mutable
dicts, and the trace would show three identical rows: a bug that looks like a
finding ("the loop is not changing anything").

WHAT IS DELIBERATELY ABSENT
---------------------------
- No `w`, no tau. They have no values (protocol.md SS4 decisions 1 and 2) and a
  default here would become one by use.
- No scoring, no thresholding. That is the Critic's.
- No Verifier-B, ever (inviolable rule 6, pinned by tests/test_s4_index.py).
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Literal

#: SS4.2's loop control: "FAIL & attempt<3 -> Researcher; FAIL & attempt=3 ->
#: emit best-of-3 with gave_up=True". Not a tunable -- SS4.6 must EARN it with
#: the per-iteration curves, and `scfeedbackcontrol` reports stability
#: thresholds past which repeated refinement degrades.
#: ref: docs/research_pipeline_en.md SS4.2, SS4.6
MAX_ATTEMPTS = 3

Verdict = Literal["PASS", "FAIL"]


@dataclass
class LoopState:
    """SS4.1's state dict, as an object that refuses to lose history."""

    # --- immutable input --------------------------------------------------
    plot_id: str
    plot: str
    target_level: int

    # --- written by the Researcher ----------------------------------------
    retrieved: list[str] = field(default_factory=list)

    # --- written by the Writer --------------------------------------------
    draft: str | None = None

    # --- written by the Critic --------------------------------------------
    neural_score: float | None = None
    symbolic_score: float | None = None
    hybrid: float | None = None
    verdict: Verdict | None = None

    # --- written by the Reflector (FAIL only) ------------------------------
    feedback: str | None = None
    failed_rules: list[str] = field(default_factory=list)

    # --- loop control ------------------------------------------------------
    attempt: int = 1
    gave_up: bool = False
    trace: list[dict[str, Any]] = field(default_factory=list)

    def snapshot(self) -> dict[str, Any]:
        """A deep copy of everything an attempt produced.

        Deep, not shallow: a shallow copy shares `retrieved` and `failed_rules`
        with the live state, so all three trace rows would end up showing the
        final attempt's values -- which reads as "the loop changed nothing"
        rather than as a copying bug.
        """
        return copy.deepcopy(
            {
                "attempt": self.attempt,
                "retrieved": self.retrieved,
                "draft": self.draft,
                "neural_score": self.neural_score,
                "symbolic_score": self.symbolic_score,
                "hybrid": self.hybrid,
                "verdict": self.verdict,
                "feedback": self.feedback,
                "failed_rules": self.failed_rules,
            }
        )

    def advance(self) -> None:
        """Archive this attempt and begin the next. Snapshot BEFORE mutating."""
        if self.attempt >= MAX_ATTEMPTS:
            raise RuntimeError(
                f"advance() past attempt {MAX_ATTEMPTS}. At the cap the loop "
                "emits best-of-3 with gave_up=True (SS4.2); it does not retry."
            )
        self.trace.append(self.snapshot())
        self.attempt += 1
        # Scores and verdict are cleared: carrying a previous attempt's score
        # into the next one is how a stale PASS survives a changed draft.
        self.neural_score = None
        self.symbolic_score = None
        self.hybrid = None
        self.verdict = None
        self.feedback = None
        self.failed_rules = []

    def best_of_trace(self) -> dict[str, Any]:
        """The highest-hybrid attempt, including the current one.

        SS4.2: on FAIL at attempt 3, "emit best-of-3 by hybrid with
        gave_up=True". Ties break toward the EARLIEST attempt -- if two drafts
        score identically, the loop did not earn the extra calls, and choosing
        the later one would quietly flatter the loop in exactly the metric
        (calls per accepted generation) that decision 19's tau objective
        divides by.
        """
        candidates = [*self.trace, self.snapshot()]
        scored = [c for c in candidates if c["hybrid"] is not None]
        if not scored:
            raise RuntimeError("no scored attempt exists; the Critic never ran.")
        return max(scored, key=lambda c: (c["hybrid"], -c["attempt"]))

    def finalize_give_up(self) -> dict[str, Any]:
        """Mark the run as exhausted and return the emitted attempt."""
        best = self.best_of_trace()
        self.gave_up = True
        return best
