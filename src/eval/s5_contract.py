#!/usr/bin/env python3
"""Pure Phase-5 contracts, kept separate from expensive generation.

Nothing in this module loads a model or calls a provider.  It makes the choices
that must be frozen before eval text exists testable on CPU: the ten-condition
registry, eval-only plot surface, static few-shot draw, symbolic acceptance-
budget match, compute-prefix rule, role-control byte equality, and resume keys.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


CONDITIONS = (
    "zero_shot",
    "static_few_shot",
    "rag_only",
    "rag_neural_loop",
    "rag_symbolic_loop",
    "rag_neural_symbolic_feedback",
    "intrinsic_self_critique",
    "external_role_self_critique",
    "gemma4_26b_a4b_judge_loop",
    "blind_resampling",
)

REPLICATE_SEEDS = (42, 43, 44)
INTERNAL_CALL_GROUPS = (
    "shared_rag_initial", "shared_self_critique", "shared_role_revision",
)


class S5ContractError(RuntimeError):
    """Raised before generation when a Phase-5 comparison would be invalid."""


@dataclass(frozen=True)
class EvalPlot:
    plot_id: str
    synopsis: str
    language: str


@dataclass(frozen=True)
class StaticExamples:
    seed: int
    review_ids: tuple[str, ...]
    texts: tuple[str, ...]
    labels: tuple[int, ...]

    @property
    def by_level(self) -> dict[int, tuple[str, ...]]:
        return {
            level: tuple(t for t, y in zip(self.texts, self.labels) if y == level)
            for level in (0, 1)
        }


def load_eval_plots(path: str | Path, *, expected_n: int = 90) -> tuple[EvalPlot, ...]:
    """Load exactly the frozen eval plots; refuse dev or duplicate IDs."""
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    chosen = [r for r in rows if r.get("split") == "eval"]
    if len(chosen) != expected_n:
        raise S5ContractError(
            f"expected exactly {expected_n} eval plots, found {len(chosen)} in {path}"
        )
    ids = [r["plot_id"] for r in chosen]
    if len(set(ids)) != len(ids):
        raise S5ContractError("duplicate plot_id in the Phase-5 eval surface")
    if any(not r.get("synopsis", "").strip() for r in chosen):
        raise S5ContractError("an eval plot has an empty synopsis")
    return tuple(
        EvalPlot(r["plot_id"], r["synopsis"], r.get("language", ""))
        for r in sorted(chosen, key=lambda x: x["plot_id"])
    )


def select_static_examples(
    rows, *, per_level: int = 10, seed: int = 42, instance_key: str = ""
) -> StaticExamples:
    """A deterministic instance-randomized draw from role-A/R1 rows.

    ``instance_key`` is plot/level/replicate, never plot text or an outcome.
    IDs are sorted before sampling, so an input-file reorder cannot alter the
    treatment. The derived RNG isolates one case from execution order and
    resume state. Role and partition are checked again at point of use.
    """
    if getattr(rows, "role", None) != "A" or getattr(rows, "partition", None) != "R1":
        raise S5ContractError("static examples must come through role A from R1")
    triples = sorted(zip(rows.review_ids, rows.texts, rows.labels), key=lambda x: x[0])
    material = f"S5_STATIC_V1|{seed}|{instance_key}".encode("utf-8")
    derived_seed = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    rng = random.Random(derived_seed)
    selected: list[tuple[str, str, int]] = []
    for level in (0, 1):
        pool = [x for x in triples if int(x[2]) == level]
        if len(pool) < per_level:
            raise S5ContractError(
                f"level {level} has {len(pool)} R1 rows; need {per_level}"
            )
        selected.extend(rng.sample(pool, per_level))
    selected.sort(key=lambda x: (int(x[2]), x[0]))
    return StaticExamples(
        seed=derived_seed,
        review_ids=tuple(x[0] for x in selected),
        texts=tuple(x[1] for x in selected),
        labels=tuple(int(x[2]) for x in selected),
    )


def threshold_for_acceptance_rate(
    scores: Sequence[float], *, target_rate: float
) -> tuple[float, int]:
    """Choose an observed-score threshold, ties going to the stricter value."""
    if not scores or not 0.0 <= target_rate <= 1.0:
        raise S5ContractError("scores must be non-empty and target_rate in [0,1]")
    vals = [float(x) for x in scores]
    if any(not math.isfinite(x) or not 0.0 <= x <= 1.0 for x in vals):
        raise S5ContractError("all gate scores must be finite probabilities")
    # One candidate above max permits an explicit zero-accept policy.
    candidates = set(vals)
    candidates.add(math.nextafter(max(vals), math.inf))
    n = len(vals)
    ranked = []
    for tau in candidates:
        accepted = sum(x >= tau for x in vals)
        ranked.append((abs(accepted / n - target_rate), -tau, tau, accepted))
    _, _, tau, accepted = min(ranked)
    return tau, accepted


def symbolic_scores_from_s4(
    path: str | Path, *, condition: str = "length_controlled", arm: str = "bn"
) -> tuple[float, ...]:
    with open(path, encoding="utf-8", newline="") as fh:
        rows = [
            r for r in csv.DictReader(fh)
            if r.get("condition") == condition and r.get("arm") == arm
        ]
    if len(rows) != 60:
        raise S5ContractError(
            f"symbolic threshold requires 60 frozen cases, found {len(rows)}"
        )
    return tuple(float(r["symbolic"]) for r in rows)


def largest_prefix_within_budget(
    candidate_compute: Sequence[float], *, budget: float
) -> int:
    """Return largest nested prefix whose cumulative realized compute fits."""
    if budget <= 0 or not candidate_compute:
        raise S5ContractError("budget and candidate pool must be positive")
    total = 0.0
    best = 0
    for i, cost in enumerate(candidate_compute, start=1):
        cost = float(cost)
        if not math.isfinite(cost) or cost <= 0:
            raise S5ContractError("each candidate compute cost must be positive")
        total += cost
        if total <= budget:
            best = i
    if best == 0:
        raise S5ContractError("row-6 budget cannot fund even one row-9 sample")
    return best


def assert_identical_critique_bytes(left: str, right: str) -> str:
    """Gate rows 7a/7b on exact UTF-8 bytes and return their shared digest."""
    a, b = left.encode("utf-8"), right.encode("utf-8")
    if a != b:
        raise S5ContractError("rows 7a/7b do not carry byte-identical critique text")
    return hashlib.sha256(a).hexdigest()


def generation_key(
    *, condition: str, replicate_seed: int, plot_id: str, target_level: int,
    call_role: str, call_index: int, arm: str, provider: str, model: str
) -> str:
    """Collision-resistant identity for every Phase-5 generative call."""
    if condition not in (*CONDITIONS, *INTERNAL_CALL_GROUPS):
        raise S5ContractError(f"unknown Phase-5 condition {condition!r}")
    if replicate_seed not in REPLICATE_SEEDS:
        raise S5ContractError(f"unregistered replicate seed {replicate_seed}")
    if target_level not in (0, 1) or call_index < 1:
        raise S5ContractError("target level must be 0/1 and call_index >= 1")
    payload = {
        "condition": condition,
        "replicate_seed": replicate_seed,
        "plot_id": plot_id,
        "target_level": target_level,
        "call_role": call_role,
        "call_index": call_index,
        "arm": arm,
        "provider": provider,
        "model": model,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sampling_seed(call_key: str) -> int:
    """Stable 31-bit RNG seed; independent of execution order and resume state."""
    digest = hashlib.sha256(f"S5_SAMPLE_V1|{call_key}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % (2**31 - 1)
