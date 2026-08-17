#!/usr/bin/env python3
"""Critic -- the deterministic judge. §4.2 component 3, and the thesis's centre.

Explicitly **not** an LLM. §4.2 calls that "the architecture's soul", and it is
the direct application of the Self-Correction Illusion finding: what works is
feedback from an *external* role, not a model grading itself.

⛔ THREE THINGS THIS FILE REFUSES TO DO
---------------------------------------
1. **It has no default `w` and no default `τ`.** Both are required arguments and
   there is no fallback. `w` is fitted on the 30 dev-plots' generations and
   reported as a sensitivity curve, never a point (protocol.md §S4 decision 1);
   τ is selected by decision 19's argmax. A default here would become a value by
   use, which is exactly how `0.6/0.4` survived in the spec for months with no
   derivation anywhere.
2. **It refuses a symbolic artifact carrying `enable_f1=True`.** That is a
   rule-7 pilot object. The amendment packet is unsigned, and an artifact is
   loaded silently -- unlike a result file, nothing about its contents appears
   on screen.
3. **It never touches Verifier-B.** Inviolable rule 6: B scores S6 and the τ
   endpoints only. That wall *is* the Goodhart test, and
   `tests/test_s4_index.py` AST-scans this package to keep it real.

WHAT "SCORE" MEANS HERE, AND WHY IT IS NOT p(cluster_k2 = 1)
------------------------------------------------------------
Both models predict `cluster_k2 ∈ {0, 1}`. The Critic asks a different question:
*is this draft at the level that was requested?* So the score is
**P(y = target_level)**, which for level 0 is `1 - p1`. Scoring `p1` regardless
of the target would make every level-0 request fail by construction, and the
loop would burn three attempts on every one of them while looking like a model
that cannot write level-0 text.

⚠️ A DISTRIBUTION SHIFT THAT IS REGISTERED, NOT SOLVED
------------------------------------------------------
Both halves were fitted on **human** reviews and are applied here to **generated**
text. `kapur2026length` shows the length/specificity relation is flat or
reversed in machine text, which is why `w` moved off dev-82 onto dev-plot
generations in the first place. The scores are used as specified; the shift is
stated wherever they appear.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.symbolic.features import FeatureSpec, extract, feature_names  # noqa: E402
from src.verifier.calibration import apply_temperature  # noqa: E402


class CriticContractError(RuntimeError):
    """Raised when the Critic cannot judge to specification."""


@dataclass(frozen=True)
class Judgement:
    """§4.2: 'Out: verdict + both scores.' Both, always -- the parts are the point."""

    neural_score: float
    symbolic_score: float
    hybrid: float
    verdict: str  # "PASS" | "FAIL"
    w: float
    tau: float
    target_level: int


class Critic:
    def __init__(
        self,
        *,
        verifier_a_path: str | Path = "artifacts/verifier_a.joblib",
        symbolic_path: str | Path = "artifacts/symbolic_scorer.joblib",
        required_sklearn_version: str | None = None,
    ):
        import joblib
        import sklearn
        import warnings

        if (required_sklearn_version is not None
                and sklearn.__version__ != required_sklearn_version):
            raise CriticContractError(
                "scikit-learn runtime does not match the symbolic artifact: "
                f"required {required_sklearn_version}, found {sklearn.__version__}. "
                "Refusing before joblib can construct an incompatible estimator."
            )

        a = joblib.load(verifier_a_path)
        if not isinstance(a, dict) or "head" not in a:
            raise CriticContractError(
                f"{verifier_a_path} is not the expected dict from train_verifier_a.py."
            )
        if a.get("role") != "A":
            # Cheap, and it is the one mistake that would void RQ5 invisibly.
            raise CriticContractError(
                f"in-loop verifier must have role 'A', got {a.get('role')!r}. "
                "Inviolable rule 6: Verifier-B never enters the loop."
            )

        # The symbolic pipeline is a native sklearn object, unlike Verifier-A's
        # small dict wrapper. Its 1.9.0 -> 1.6.1 load emitted a warning and then
        # crashed only on predict_proba (`multi_class` was absent). A warning is
        # therefore already a failed contract, not something to scroll past.
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            s = joblib.load(symbolic_path)
        version_warnings = [
            str(w.message) for w in caught
            if "Version" in type(w.message).__name__
        ]
        if version_warnings:
            raise CriticContractError(
                "symbolic scorer pickle version mismatch: "
                + version_warnings[0].split("\n")[0]
            )
        if s.get("enable_f1"):
            raise CriticContractError(
                f"{symbolic_path} was fitted with enable_f1=True. That is a RULE 7 "
                "PILOT artifact and may not enter the loop. The rule-7 amendment "
                "(docs/rule7_amendment_packet.md) is unsigned; until it is signed "
                "the Critic uses the F1-disabled scorer only."
            )

        self._spec = FeatureSpec(enable_f1=False)
        expected = feature_names(self._spec)
        if list(s.get("feature_names", [])) != expected:
            # Order, not just membership: the pipeline consumes a positional
            # vector, so a permutation scores silently and wrongly.
            raise CriticContractError(
                "symbolic feature names/order do not match this build.\n"
                f"  artifact: {s.get('feature_names')}\n  expected: {expected}"
            )

        self._head = a["head"]
        self._temperature = a.get("temperature")
        self._normalize = bool(a.get("normalize_embeddings", True))
        self._encoder_name = a["encoder"]
        self._encoder = None  # lazy: the Critic is constructed in tests too
        self._symbolic = s["pipeline"]

    def _embed(self, text: str):
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer

            self._encoder = SentenceTransformer(self._encoder_name)
        return self._encoder.encode(
            [text], normalize_embeddings=self._normalize, show_progress_bar=False
        )

    def neural(self, draft: str, target_level: int) -> float:
        p1 = float(self._head.predict_proba(self._embed(draft))[0, 1])
        if self._temperature:
            # Reported on the calibrated scale so τ reads as a probability
            # (`kotte2026ucci` Thm 1). Accuracy-preserving, so this cannot move
            # any item across any threshold -- verified on dev-82 in decision 17
            # (0 rank inversions), which is why it is safe to apply inside a
            # thresholding loop at all.
            p1 = apply_temperature([p1], self._temperature)[0]
        return p1 if target_level == 1 else 1.0 - p1

    def symbolic(self, draft: str, target_level: int) -> float:
        row = [[extract(draft, self._spec)[k] for k in feature_names(self._spec)]]
        p1 = float(self._symbolic.predict_proba(row)[0, 1])
        return p1 if target_level == 1 else 1.0 - p1

    def judge(self, draft: str, target_level: int, *, w: float, tau: float) -> Judgement:
        """§4.2's hybrid. `w` and `tau` are required and have no defaults."""
        if not 0.0 <= w <= 1.0:
            raise CriticContractError(f"w must be in [0,1], got {w!r}")
        if not 0.0 <= tau <= 1.0:
            raise CriticContractError(f"tau must be in [0,1], got {tau!r}")
        if target_level not in (0, 1):
            raise CriticContractError(
                f"target_level must be 0 or 1 (K=2 since 2026-08-03), got {target_level!r}"
            )
        n = self.neural(draft, target_level)
        s = self.symbolic(draft, target_level)
        hybrid = w * n + (1.0 - w) * s
        # >= not >: at τ = 0 the Critic must never reject, because decision 19
        # defines α_lo as exactly that -- "τ=0, the Critic never rejects, = §5.1
        # row 1". With a strict inequality a score of 0.0 would FAIL and α_lo
        # would not be the row it is defined to be.
        return Judgement(
            neural_score=n,
            symbolic_score=s,
            hybrid=hybrid,
            verdict="PASS" if hybrid >= tau else "FAIL",
            w=w,
            tau=tau,
            target_level=target_level,
        )
