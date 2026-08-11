"""Pin the Reflector's decomposition. Which rules failed must be COMPUTED.

§4.2 wants "which symbolic rules failed", not a model's opinion about which
rules failed. The symbolic scorer is a linear logistic on standardised
features, so `coef · z` is the exact per-feature contribution to the logit —
nothing is estimated and nothing is re-fitted. These tests hold that property,
because the moment it becomes an approximation the Critic stops being a tool
and starts being a second judge.

A stub pipeline stands in for the fitted one: the arithmetic is what is being
tested, not LaBSE and not the real coefficients.

Run:  python -m pytest tests/test_s4_reflector.py -q
      python tests/test_s4_reflector.py          (no pytest needed)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from src.agents.reflector import (  # noqa: E402
    MAX_RULES_NAMED,
    Reflector,
    failed_rules,
    render_feedback_prompt,
)
from src.symbolic.features import FeatureSpec, feature_names  # noqa: E402

NAMES = feature_names(FeatureSpec(enable_f1=False))
DRAFT = "ছবিটা খুব ভালো হইছে অসাধারণ"


class _LR:
    def __init__(self, coef):
        self.coef_ = np.array([coef], dtype=float)


class _Scaler:
    """Centred, and that is not cosmetic — it is what makes ABSENCE reportable.

    An earlier version of this stub used `mean_ = 0`, and the test asking
    whether "no connecting words" can be reported then failed. The reason is
    worth keeping: with no centring, a feature whose value is **zero**
    contributes `coef × 0 = 0`, which is not negative, so **the most actionable
    feedback there is — you used none of X — would be structurally
    unreportable**.

    The real fitted scaler subtracts a positive corpus mean, so absence becomes
    a negative z and is detected. The stub was wrong; the code was right. Kept
    as a comment because the property is easy to break and hard to notice: it
    lives in the scaler, not in the Reflector.
    """

    def __init__(self, n, mean=0.05):
        self.mean_ = np.full(n, mean)
        self.scale_ = np.ones(n)


class _Pipe:
    def __init__(self, coef):
        self.named_steps = {
            "standardscaler": _Scaler(len(coef)),
            "logisticregression": _LR(coef),
        }


class StubCritic:
    def __init__(self, coef):
        self._symbolic = _Pipe(coef)


def test_only_features_pushing_away_from_the_target_are_returned():
    """A rule that HELPED must never be reported as a failure.

    Naming a feature that was already pushing the right way sends the Writer to
    fix something that is not broken, and the next attempt is spent on it.
    """
    coef = [0.0] * len(NAMES)
    coef[NAMES.index("n_tokens")] = -1.0        # pushes toward level 0
    coef[NAMES.index("guiraud")] = +1.0         # pushes toward level 1
    rules = failed_rules(StubCritic(coef), DRAFT, target_level=1)
    got = {r.feature for r in rules}
    assert "n_tokens" in got
    assert "guiraud" not in got, "a helping feature was reported as failing"


def test_the_sign_flips_with_the_target_level():
    """Level 0 is not "not level 1" by accident — the whole decomposition flips.

    Without this, every level-0 request would be told to fix the features that
    were already correct for it.
    """
    coef = [0.0] * len(NAMES)
    coef[NAMES.index("n_tokens")] = -1.0
    at1 = {r.feature for r in failed_rules(StubCritic(coef), DRAFT, 1)}
    at0 = {r.feature for r in failed_rules(StubCritic(coef), DRAFT, 0)}
    assert "n_tokens" in at1 and "n_tokens" not in at0


def test_at_most_three_rules_are_named():
    """Error-LOCALISED feedback beats generic (Tyen et al. 2024); a list of all
    eleven features is generic again by volume."""
    coef = [-1.0] * len(NAMES)
    rules = failed_rules(StubCritic(coef), DRAFT, target_level=1)
    assert len(rules) <= MAX_RULES_NAMED == 3


def test_rules_are_ordered_worst_first():
    coef = [0.0] * len(NAMES)
    coef[NAMES.index("n_tokens")] = -0.5
    coef[NAMES.index("guiraud")] = -5.0
    rules = failed_rules(StubCritic(coef), DRAFT, target_level=1)
    assert rules[0].contribution <= rules[-1].contribution


def test_gameable_families_are_flagged_not_hidden():
    """RQ5 needs to know when feedback pointed at a gameable family.

    mahmoud2026rubric found presence-based criteria are the category that gets
    hacked, and §3.5 labelled ours individually. If the Reflector names one, the
    trace has to say so — otherwise the gaming signature cannot be attributed.
    """
    coef = [0.0] * len(NAMES)
    coef[NAMES.index("intensifier_frac")] = -1.0   # F5_sentiment, gameable
    rules = failed_rules(StubCritic(coef), DRAFT, target_level=1)
    assert rules and rules[0].gameable is True
    assert rules[0].family == "F5_sentiment"


def test_feedback_prompt_asks_for_instructions_not_a_rewrite():
    """If the Reflector writes the comment, the Writer is no longer the writer.

    The loop would then be measuring the Reflector, and §4.2's role separation —
    which §4.0 calls the architecture's soul — would exist only on paper.
    """
    # POSITIVE coefficient: connectives push toward level 1. The draft has
    # none, so its standardised value is below the mean and the contribution is
    # negative — i.e. "you used no connecting words" is reportable.
    #
    # ⚠️ The sign was wrong twice while writing this test. With a NEGATIVE
    # coefficient, connectives push toward level 0, so their absence HELPS
    # level 1 and correctly does not appear as a failure. The arithmetic was
    # right both times and the test's premise was not — which is the argument
    # for the test existing: this sign convention is genuinely easy to invert,
    # and inverting it in `reflector.py` would send the Writer to fix whatever
    # was already correct, on every single retry.
    coef = [0.0] * len(NAMES)
    coef[NAMES.index("connective_frac")] = +1.0
    rules = failed_rules(StubCritic(coef), DRAFT, target_level=1)
    p = render_feedback_prompt(DRAFT, 1, rules, arm="bn")
    assert "নতুন মন্তব্য লিখো না" in p
    assert "সংযোজক শব্দ" in p, "feature names must be humanised, not raw columns"


def test_the_prompt_never_carries_a_raw_column_name():
    coef = [-1.0] * len(NAMES)
    rules = failed_rules(StubCritic(coef), DRAFT, target_level=1)
    p = render_feedback_prompt(DRAFT, 1, rules)
    for raw in ("connective_frac", "pos_frac", "n_tokens", "guiraud"):
        assert raw not in p, f"raw feature name {raw!r} leaked into the prompt"


def test_reflect_returns_the_named_features_for_the_trace():
    """§4.6 reads failed rules off the trace; the list must come back."""
    coef = [0.0] * len(NAMES)
    coef[NAMES.index("n_tokens")] = -1.0
    r = Reflector(lambda prompt, **kw: "আরও নির্দিষ্ট করো")
    feedback, named = r.reflect(StubCritic(coef), DRAFT, 1)
    assert feedback == "আরও নির্দিষ্ট করো"
    assert named == ["n_tokens"]


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
