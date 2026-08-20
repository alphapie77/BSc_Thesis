"""Pin the loop's control flow and its call accounting.

Decision 19's τ* divides quality by E[calls] = 1 + 2(1−q) + 2(1−q)². If the loop
makes one call more or fewer than that model assumes, τ* is computed against a
cost that never happened — and nothing downstream would show it.

All four components are stubs. The properties here belong to the control flow.

Run:  python -m pytest tests/test_s4_graph.py -q
      python tests/test_s4_graph.py          (no pytest needed)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agents.graph import run_loop  # noqa: E402
from src.agents.researcher import Retrieval  # noqa: E402
from src.agents.state import MAX_ATTEMPTS  # noqa: E402

TEN = tuple(f"উদাহরণ {i}" for i in range(10))


class StubResearcher:
    def __init__(self):
        self.queries = []

    def retrieve(self, plot, level, *, feedback_keywords=None, previous_ids=None, k=10):
        self.queries.append(feedback_keywords)
        return Retrieval(tuple(f"id{i}" for i in range(10)), TEN, plot, None)


class StubGen:
    def __init__(self, text):
        self.text = text


class StubWriter:
    def __init__(self):
        self.prompts = []

    def generate(self, *, prompt, plot_id, target_level, attempt, **kw):
        self.prompts.append(prompt)
        return StubGen(f"draft {attempt}")


class StubCritic:
    """Scores rise with attempt; `passes_at` decides when PASS first happens."""

    def __init__(self, passes_at):
        self.passes_at = passes_at
        self.n = 0
        self._symbolic = None

    def judge(self, draft, level, *, tau):
        from src.agents.critic import Judgement

        self.n += 1
        score = 0.1 * self.n
        verdict = "PASS" if self.n >= self.passes_at else "FAIL"
        return Judgement(score, 1.0 - score, score, verdict, tau, level)


class StubReflector:
    def __init__(self):
        self.calls = 0

    def reflect(self, critic, draft, level, **kw):
        self.calls += 1
        return f"feedback {self.calls}", ["connective_frac"]


def _run(passes_at, **kwargs):
    r, wr, c, rf = StubResearcher(), StubWriter(), StubCritic(passes_at), StubReflector()
    res = run_loop(
        plot_id="BN001", plot="কাহিনি", target_level=1,
        researcher=r, writer=wr, critic=c, reflector=rf, tau=0.5, **kwargs,
    )
    return res, r, wr, rf


def test_pass_on_first_attempt_costs_one_call_and_no_reflection():
    res, _, _, rf = _run(passes_at=1)
    assert res.writer_calls == 1 and rf.calls == 0
    assert res.llm_calls == 1, "α_lo is row 3 (RAG-only) at one call"
    assert not res.gave_up


def test_three_failures_give_up_and_make_exactly_two_reflector_calls():
    """The last FAIL gets no Reflector call: there is no attempt left to feed.

    A call there would cost a request, buy nothing, and inflate E[calls] against
    the model decision 19 derived — 2(1−q) + 2(1−q)², which charges reflections
    for the first two failures only.
    """
    res, _, _, rf = _run(passes_at=99)
    assert res.writer_calls == MAX_ATTEMPTS == 3
    assert rf.calls == 2, f"expected 2 reflections, got {rf.calls}"
    assert res.llm_calls == 5
    assert res.gave_up is True


def test_giving_up_emits_the_best_attempt_not_the_last():
    res, _, _, _ = _run(passes_at=99)
    assert res.emitted["gate_score"] == max(
        t["gate_score"] for t in res.state.trace + [res.emitted]
    )


def test_trace_holds_every_earlier_attempt():
    res, _, _, _ = _run(passes_at=99)
    assert len(res.state.trace) == MAX_ATTEMPTS - 1
    assert [t["draft"] for t in res.state.trace] == ["draft 1", "draft 2"]


def test_feedback_keywords_reach_the_researcher_only_after_a_failure():
    _, r, _, _ = _run(passes_at=3)
    assert r.queries[0] is None, "attempt 1 must query with no feedback"
    assert r.queries[1] == ["connective_frac"]


def test_the_retry_prompt_contains_the_previous_draft_and_the_feedback():
    _, _, wr, _ = _run(passes_at=3)
    assert "draft 1" in wr.prompts[1] and "feedback 1" in wr.prompts[1]
    assert "draft 1" not in wr.prompts[0], "attempt 1 cannot contain a previous draft"


def test_forced_three_continues_after_pass_without_calling_it_gave_up():
    res, _, _, rf = _run(passes_at=1, force_all_attempts=True)
    assert res.writer_calls == 3 and rf.calls == 2 and res.llm_calls == 5
    assert res.gave_up is False


def _run_all() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL  {fn.__name__}\n        {exc}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run_all())
