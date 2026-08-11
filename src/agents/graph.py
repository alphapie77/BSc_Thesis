#!/usr/bin/env python3
"""The loop. §4.2's control flow, and nothing else lives here.

Deliberately plain Python rather than LangGraph objects. §4.0's identity
sentence is *"a compound AI system implementing the evaluator-optimizer
workflow ... control flow is predefined"* -- and a predefined control flow written
as four `if`s is honest about being one. A graph library would add a dependency,
a serialisation format and a scheduler to express: try, judge, reflect, retry.
`langgraph` stays in `requirements.in` because §4.4 names it and a later
visualisation may want it; the loop does not need it to be correct.

**Never describe this as an autonomous multi-agent system** (§4.0). Two of the
four components make no LLM call at all.

WHAT THE LOOP GUARANTEES
------------------------
* FAIL & attempt < 3 -> back to the Researcher with the query **anchored**.
* FAIL & attempt = 3 -> emit best-of-3 by hybrid with `gave_up=True`.
* Every attempt is snapshotted into `trace` **before** the next one starts.
* `E[calls]` is countable from the trace: one Writer call per attempt, one
  Reflector call per FAIL except the last. Decision 19's cost model depends on
  that being true, so the counts are recorded rather than assumed.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.state import MAX_ATTEMPTS, LoopState  # noqa: E402


@dataclass
class LoopResult:
    state: LoopState
    emitted: dict
    writer_calls: int
    reflector_calls: int

    @property
    def gave_up(self) -> bool:
        return self.state.gave_up

    @property
    def llm_calls(self) -> int:
        """What decision 19's E[calls] counts. Researcher and Critic are free."""
        return self.writer_calls + self.reflector_calls


def run_loop(
    *,
    plot_id: str,
    plot: str,
    target_level: int,
    researcher,
    writer,
    critic,
    reflector,
    w: float,
    tau: float,
    arm: str = "bn",
) -> LoopResult:
    """One plot, one level, up to three attempts. `w` and `tau` are required."""
    from src.agents.prompts import render

    state = LoopState(plot_id=plot_id, plot=plot, target_level=target_level)
    writer_calls = reflector_calls = 0
    feedback_keywords: list[str] | None = None
    previous_ids: tuple[str, ...] | None = None
    # Carried locally, and the reason is a real bug this caught. `advance()`
    # clears `state.feedback`, which is correct for scores and verdict -- they
    # belong to the attempt that produced them and a stale PASS must not land on
    # a new draft. But the Reflector's feedback is produced FOR the next attempt.
    # Reading it off the state after advancing gave None, so every retry prompt
    # was silently identical to attempt 1's except for the previous draft: the
    # loop would have looked like it was retrying and been re-rolling the dice.
    pending_feedback: str | None = None

    while True:
        retrieval = researcher.retrieve(
            plot,
            target_level,
            feedback_keywords=feedback_keywords,
            previous_ids=previous_ids,
        )
        state.retrieved = list(retrieval.review_ids)
        previous_ids = retrieval.review_ids

        prompt = render(
            plot=plot,
            target_level=target_level,
            arm=arm,
            exemplars=retrieval.texts,
            previous_draft=state.trace[-1]["draft"] if state.trace else None,
            feedback=pending_feedback,
        )
        gen = writer.generate(
            prompt=prompt,
            plot_id=plot_id,
            target_level=target_level,
            attempt=state.attempt,
        )
        writer_calls += 1
        state.draft = gen.text

        j = critic.judge(state.draft, target_level, w=w, tau=tau)
        state.neural_score = j.neural_score
        state.symbolic_score = j.symbolic_score
        state.hybrid = j.hybrid
        state.verdict = j.verdict

        if j.verdict == "PASS":
            return LoopResult(state, state.snapshot(), writer_calls, reflector_calls)

        if state.attempt >= MAX_ATTEMPTS:
            # No Reflector call here, and that is not an optimisation: there is
            # no further attempt to feed, so a call would cost a request and buy
            # nothing -- and it would inflate E[calls] against the cost model
            # decision 19 derived, which charges 2(1-q) + 2(1-q)^2.
            return LoopResult(
                state, state.finalize_give_up(), writer_calls, reflector_calls
            )

        feedback, failed = reflector.reflect(critic, state.draft, target_level)
        reflector_calls += 1
        state.feedback = feedback
        pending_feedback = feedback
        state.failed_rules = failed
        # Feedback keywords AUGMENT the query; the original plot stays anchored
        # inside `researcher.build_query`. Query drift would read in the results
        # as the loop failing to improve rather than as retrieval decaying.
        feedback_keywords = failed
        state.advance()
