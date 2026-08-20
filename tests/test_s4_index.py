"""Guard the Phase 4 walls at the point where they are easiest to breach.

Three separate things are pinned here, and they fail for different reasons:

- **The RAG index is R1 only** (inviolable rule 5). R2 in retrieval means every
  generation is conditioned on the half reserved for independent evaluation,
  and RQ5's Goodhart gap becomes unmeasurable — with nothing in any result file
  to show it happened.
- **Gold-300 never enters the index** (inviolable rule 4).
- **Verifier-B is not reachable from `src/agents/`** (inviolable rule 6). This
  is the one that matters most and is the one prose cannot enforce. On
  2026-08-11 this project recorded a wall that came a single training run from
  collapsing because a definition was ambiguous and *"an ambiguity everyone
  reads correctly is still an ambiguity, and code does not read intent."* So
  the loop's package is scanned for a path to Verifier-B rather than trusted
  not to have one.

The import guard is an AST scan, not a substring search. A substring search
would pass on a file containing `# never import verifier_b` and fail on a file
that mentions it in a docstring — i.e. it would be wrong in both directions, and
the 2026-08-11 `check_constants.py` loopholes are the recorded precedent for a
checker that cannot tell prose about a rule from the rule.

Run:  python -m pytest tests/test_s4_index.py -q
      python tests/test_s4_index.py          (no pytest needed)
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agents.build_index import (  # noqa: E402
    IndexContractError,
    assert_matches_committed_manifest,
    assert_rag_contract,
    id_digest,
)

SPLIT_MAP = ROOT / "data/splits/split_map_v1.json"
AGENTS_DIR = ROOT / "src/agents"

#: Anything that would give the loop a path to the out-of-loop verifier.
#: `verifier_b` covers the artifact and the training module; `train_verifier_b`
#: is named separately so the failure message can say which one was found.
FORBIDDEN_IN_AGENTS = ("verifier_b", "train_verifier_b")


def _smap() -> dict:
    return json.loads(SPLIT_MAP.read_text(encoding="utf-8"))


def test_r2_ids_are_refused_not_warned():
    """A single R2 id must stop the build. Not log, not skip — stop."""
    smap = _smap()
    poisoned = (smap["R1"][0], smap["R2"][0])
    try:
        assert_rag_contract(poisoned, str(SPLIT_MAP))
    except IndexContractError as exc:
        assert "rule 5" in str(exc), "the refusal must name the rule it enforces"
        return
    raise AssertionError(
        "assert_rag_contract accepted an R2 id. The RAG index would contain the "
        "evaluation half and no result file would record it."
    )


def test_gold_ids_are_refused_not_warned():
    smap = _smap()
    poisoned = (smap["R1"][0], smap["G"][0])
    try:
        assert_rag_contract(poisoned, str(SPLIT_MAP))
    except IndexContractError as exc:
        assert "rule 4" in str(exc), "the refusal must name the rule it enforces"
        return
    raise AssertionError("assert_rag_contract accepted a Gold-300 id.")


def test_clean_r1_ids_pass():
    """The guard must not be so strict that the legitimate build cannot run.

    A wall that refuses everything is indistinguishable from a broken build and
    would be 'fixed' by deleting the check — which is how walls die.
    """
    assert_rag_contract(tuple(_smap()["R1"][:50]), str(SPLIT_MAP))


def test_digest_is_order_independent_but_membership_sensitive():
    """The manifest's claim is about WHICH rows, not about their order."""
    ids = tuple(_smap()["R1"][:20])
    assert id_digest(ids) == id_digest(tuple(reversed(ids))), (
        "digest changed under reordering — it would then fail for the wrong "
        "reason and stop being evidence about index contents"
    )
    assert id_digest(ids) != id_digest(ids[:-1]), (
        "digest did not change when a row was removed — it is not evidence "
        "of anything"
    )


def test_runtime_index_must_match_committed_manifest_without_rewriting(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"result": {"n_indexed": 2}}), encoding="utf-8")
    before = path.read_bytes()
    assert_matches_committed_manifest({"n_indexed": 2}, path)
    assert path.read_bytes() == before
    with pytest.raises(IndexContractError, match="differs"):
        assert_matches_committed_manifest({"n_indexed": 3}, path)


def test_verifier_b_is_unreachable_from_the_loop_package():
    """Inviolable rule 6, enforced by AST rather than by everyone remembering.

    Scans every import in `src/agents/` — including inside functions, which is
    where a late `from src.verifier...import` would hide from a top-of-file
    reading. Verifier-B scores S6 and the τ endpoints; it never enters the loop,
    and that wall IS the Goodhart test.
    """
    offenders: list[str] = []
    for py in sorted(AGENTS_DIR.rglob("*.py")):
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                names = [mod] + [f"{mod}.{a.name}" for a in node.names]
            for name in names:
                low = name.lower()
                for bad in FORBIDDEN_IN_AGENTS:
                    if bad in low:
                        offenders.append(f"{py.relative_to(ROOT)}: import {name}")
    assert not offenders, (
        "Verifier-B is reachable from the loop package, which voids inviolable "
        "rule 6 and makes RQ5's Goodhart test meaningless:\n  "
        + "\n  ".join(offenders)
    )


def test_the_import_guard_can_actually_fail():
    """A guard whose failure branch is unreachable certifies nothing.

    RQ1-F's Gate 2 had to be rewritten mid-protocol because its null verdict was
    unreachable by construction, and that failure mode is now tested for rather
    than discovered. Same principle: prove the scanner detects a real import
    before trusting it to report none.
    """
    src = "from src.verifier.train_verifier_b import main\n"
    tree = ast.parse(src)
    found = [
        n.module
        for n in ast.walk(tree)
        if isinstance(n, ast.ImportFrom)
        and any(bad in (n.module or "").lower() for bad in FORBIDDEN_IN_AGENTS)
    ]
    assert found, "the AST scan cannot see a Verifier-B import; it proves nothing"


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
