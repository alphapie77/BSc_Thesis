"""Pin the Critic's refusals. Each one prevents a silent, uninterpretable result.

No model is loaded: the arithmetic and the contract checks are exercised against
a stub, because the properties being guarded are properties of the *contract*,
not of LaBSE.

Run:  python -m pytest tests/test_s4_critic.py -q
      python tests/test_s4_critic.py          (no pytest needed)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agents.critic import (  # noqa: E402
    Critic,
    CriticContractError,
    FrozenBinaryLogisticHead,
    Judgement,
)


class StubCritic(Critic):
    """A Critic with the two models replaced by fixed scores."""

    def __init__(self, neural: float, symbolic: float):  # noqa: D107
        self._n, self._s = neural, symbolic

    def neural(self, draft, target_level):  # noqa: D102
        return self._n if target_level == 1 else 1.0 - self._n

    def symbolic(self, draft, target_level):  # noqa: D102
        return self._s if target_level == 1 else 1.0 - self._s


def test_symbolic_score_cannot_move_the_verdict():
    assert StubCritic(0.6, 0.0).judge("d", 1, tau=0.5).verdict == "PASS"
    assert StubCritic(0.4, 1.0).judge("d", 1, tau=0.5).verdict == "FAIL"


def test_score_is_probability_of_the_TARGET_level_not_of_level_1():
    """Otherwise every level-0 request fails by construction.

    The loop would then burn all three attempts on every level-0 plot while
    looking like a model that cannot write level-0 text — a result with a cause
    nothing in `trace` would reveal.
    """
    c = StubCritic(0.9, 0.9)
    assert c.judge("d", 1, tau=0.5).verdict == "PASS"
    # Tolerance, not equality: 1.0 - 0.9 is 0.09999999999999998, and an exact
    # comparison here fails for a reason that has nothing to do with the
    # property being tested. A test that fails on float representation teaches
    # people to distrust the suite.
    assert abs(c.judge("d", 0, tau=0.5).neural_score - 0.1) < 1e-12
    assert c.judge("d", 0, tau=0.5).verdict == "FAIL"


def test_tau_zero_never_rejects_because_alpha_lo_is_defined_as_that():
    """Decision 19 defines α_lo as τ=0, never reject, = §5.1 row 3.

    With a strict inequality a hybrid of exactly 0.0 would FAIL, and α_lo would
    not be the row it is defined to be — quietly changing the lower endpoint of
    the τ objective.
    """
    assert StubCritic(0.0, 0.0).judge("d", 1, tau=0.0).verdict == "PASS"


def test_tau_has_no_default():
    c = StubCritic(0.5, 0.5)
    for kwargs in ({},):
        try:
            c.judge("d", 1, **kwargs)
        except TypeError:
            continue
        raise AssertionError(f"judge() accepted {kwargs} — a default exists")


def test_out_of_range_tau_and_level_are_refused():
    c = StubCritic(0.5, 0.5)
    for bad in ({"tau": -0.1}, {"tau": 1.1}):
        try:
            c.judge("d", 1, **bad)
        except CriticContractError:
            continue
        raise AssertionError(f"judge() accepted {bad}")
    try:
        c.judge("d", 2, tau=0.5)
    except CriticContractError:
        return
    raise AssertionError("judge() accepted level 2; K has been 2 since 2026-08-03")


def test_both_scores_are_always_returned_with_neural_gate_score():
    """§4.2: 'Out: verdict + both scores.' RQ3 and RQ5 need the parts.

    A hybrid alone cannot answer whether the symbolic term earned its place, and
    cannot show the Mahmoud et al. gaming signature — symbolic rising across
    attempts while Verifier-B stays flat.
    """
    j = StubCritic(0.8, 0.2).judge("d", 1, tau=0.4)
    assert isinstance(j, Judgement)
    assert j.neural_score == 0.8 and j.symbolic_score == 0.2
    assert j.gate_score == j.neural_score == 0.8 and j.tau == 0.4


def test_the_module_never_references_verifier_b():
    """Inviolable rule 6, checked here too and not only by the package scan."""
    src = (ROOT / "src/agents/critic.py").read_text(encoding="utf-8").lower()
    assert "verifier_b" not in src, "the Critic mentions Verifier-B"


def test_frozen_logistic_head_uses_portable_binary_arithmetic():
    """A's sklearn-1.6.1 methods must not run inside the 1.9.0 runtime."""
    class Fitted:
        coef_ = [[2.0, -1.0]]
        intercept_ = [0.5]
        classes_ = [0, 1]

    head = FrozenBinaryLogisticHead(Fitted())
    probs = head.predict_proba([[0.0, 0.0], [1.0, 0.0]])
    assert probs.shape == (2, 2)
    assert abs(float(probs[0].sum()) - 1.0) < 1e-12
    assert float(probs[1, 1]) > float(probs[0, 1])


def test_frozen_logistic_head_refuses_wrong_class_contract():
    class WrongClasses:
        coef_ = [[1.0]]
        intercept_ = [0.0]
        classes_ = [1, 2]

    try:
        FrozenBinaryLogisticHead(WrongClasses())
    except CriticContractError:
        return
    raise AssertionError("a non-[0,1] Verifier-A head was accepted")


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
