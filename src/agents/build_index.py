#!/usr/bin/env python3
"""Build the R1-only retrieval index the Researcher queries.

This is pipeline step 16's hidden prerequisite. SS4.2 specifies a Researcher
that "queries ChromaDB, top-10, within the same axis level, R1 index only" --
and no index existed. There was no config for one, no script, and nothing in
`configs/`. The component contract was written as though the index were a given.

WHAT THIS FILE IS REALLY FOR
----------------------------
Inviolable rule 5 says the RAG index is R1 only, and rule 4 says Gold-300 never
enters it. Both are one-line sentences in CLAUDE.md, and on 2026-08-11 this
project recorded a wall that came one training run from collapsing because a
rule lived in prose and the code did not read it (`protocol.md`, Verifier-B's
data definition). So the rules are enforced here as **refusals**, and the
refusals are pinned by tests:

    - ids are drawn through `split_access`, which takes a ROLE, not a partition
    - every id is checked against R2 and G before a single vector is written
    - the manifest records a digest of exactly what went in, so a later reader
      can verify the claim instead of trusting this docstring

The manifest is the point of the script as much as the index is. An index is a
binary blob; a reviewer cannot see what is inside it. The manifest can be
diffed, and its `id_digest` changes if a single row moves.

WHAT IS DELIBERATELY NOT HERE
-----------------------------
No retrieval, no top-k, no query construction. Those belong to the Researcher
(SS4.2) and are tested against a built index. Building and querying are separated
so that "the index contains the wrong rows" and "the query is wrong" can never
be the same bug.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.provenance import write_result, write_text_lf  # noqa: E402
from src.common.seed import set_seed  # noqa: E402
from src.verifier.split_access import (  # noqa: E402
    SplitContractError,
    _read_split_map,
    load_training_rows,
)


class IndexContractError(RuntimeError):
    """Raised when the index would contain rows the RAG contract forbids."""


def id_digest(review_ids: tuple[str, ...]) -> str:
    """A stable digest of exactly which rows are in the index.

    Sorted before hashing so that insertion order cannot change the digest --
    the claim being made is about SET MEMBERSHIP, not about ordering, and a
    digest that moves when the order moves would fail for the wrong reason.
    """
    joined = "\n".join(sorted(review_ids))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def assert_rag_contract(review_ids: tuple[str, ...], split_map_path: str) -> None:
    """Refuse to build if R2 or Gold-300 has reached the index.

    Deliberately checked here rather than trusted from `split_access`, even
    though `split_access` already returns R1 for role A. Two independent checks
    of the same wall cost nothing and fail differently: if the split map is ever
    edited (it is frozen -- inviolable rule 3 -- but frozen is a promise, not a
    mechanism), this catches it at the point of use.
    """
    smap = _read_split_map(split_map_path)
    ids = set(review_ids)

    leaked_r2 = ids & set(smap["R2"])
    if leaked_r2:
        raise IndexContractError(
            f"{len(leaked_r2)} R2 ids reached the RAG index. Inviolable rule 5: "
            "RAG index = R1 only. R2 in retrieval means every generation is "
            "conditioned on the half reserved for independent evaluation, and "
            "no downstream number can be separated from that. Stop."
        )

    leaked_g = ids & set(smap["G"])
    if leaked_g:
        raise IndexContractError(
            f"{len(leaked_g)} Gold-300 ids reached the RAG index. Inviolable "
            "rule 4: G is eval-only -- it never enters training, the RAG index, "
            "prompts, or threshold tuning. Stop."
        )


def build(cfg: dict) -> dict:
    """Embed R1's region-A labelled rows and persist them as a Chroma collection."""
    inputs = cfg["inputs"]

    # role "A" -- the Researcher serves the in-loop Writer, and the in-loop half
    # is R1. Asked as a role rather than a partition on purpose: a config that
    # could name "R2" is a config that can be copy-pasted into contamination.
    # `hold_out_dev=False` because the dev rows are R1 review text like any
    # other and the index is not a fitted object -- nothing is estimated from
    # them here. The slice they are held out of is the verifier's, not this one.
    rows, _ = load_training_rows(
        "A",
        split_map=inputs["split_map"],
        k2_assignments=inputs["k2_assignments"],
        cleaned_csv=inputs["cleaned_csv"],
        hold_out_dev=False,
    )
    assert_rag_contract(rows.review_ids, inputs["split_map"])

    idx = cfg["index"]
    from chromadb import PersistentClient
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer

    encoder = SentenceTransformer(idx["encoder"])
    # normalize_embeddings so that inner product IS cosine. Stated because the
    # collection is created with a cosine space below and the two must agree;
    # a mismatch here is silent and would degrade retrieval without erroring.
    vectors = encoder.encode(
        list(rows.texts),
        batch_size=64,
        show_progress_bar=False,
        normalize_embeddings=True,
    ).tolist()

    persist_dir = Path(idx["persist_dir"])
    persist_dir.mkdir(parents=True, exist_ok=True)
    client = PersistentClient(
        path=str(persist_dir), settings=Settings(anonymized_telemetry=False)
    )

    # Rebuild from scratch rather than upsert. An index that accumulates across
    # runs cannot be reasoned about: its contents would depend on run history
    # rather than on the config, and `id_digest` would stop meaning anything.
    try:
        client.delete_collection(idx["collection"])
    except Exception:
        pass
    collection = client.create_collection(
        name=idx["collection"],
        metadata={"hnsw:space": idx["metric"]},
    )

    collection.add(
        ids=list(rows.review_ids),
        documents=list(rows.texts),
        embeddings=vectors,
        # `axis_level` is the retrieval filter SS4.2 requires ("within same
        # persona label" -- the word persona is retired, the filter is not).
        # `cluster_k2` survives as the frozen VARIABLE name only; the metadata
        # key uses the permitted vocabulary so that prompts and logs built from
        # it never reintroduce the retired term.
        metadatas=[{"axis_level": int(lab)} for lab in rows.labels],
    )

    return {
        "n_indexed": len(rows),
        "partition": rows.partition,
        "axis_level_counts": {str(k): v for k, v in rows.class_counts.items()},
        "encoder": idx["encoder"],
        "metric": idx["metric"],
        "collection": idx["collection"],
        "persist_dir": str(persist_dir),
        "id_digest_sha256": id_digest(rows.review_ids),
        "r2_ids_present": 0,
        "gold_ids_present": 0,
    }


def render_md(res: dict, cfg: dict) -> str:
    lines = [
        "# S4.1 — the R1-only retrieval index",
        "",
        f"**{res['n_indexed']}** rows from **{res['partition']}**, encoded with "
        f"`{res['encoder']}`, cosine space, collection `{res['collection']}`.",
        "",
        "| Axis level | Rows |",
        "|---|---|",
    ]
    for level, n in sorted(res["axis_level_counts"].items()):
        lines += [f"| {level} | {n} |"]
    lines += [
        "",
        "## The contract, verified rather than asserted",
        "",
        "- **R2 ids present: 0.** Inviolable rule 5 — the RAG index is R1 only.",
        "- **Gold-300 ids present: 0.** Inviolable rule 4 — G is eval-only.",
        "",
        "Both are checked in `build_index.py` *before* any vector is written, "
        "and the build raises rather than warns. They are checked a second time "
        "there against the split map directly, independently of `split_access`, "
        "because the frozen split is a promise and a second check is a mechanism.",
        "",
        f"**Row-set digest (SHA-256 over sorted ids):** `{res['id_digest_sha256']}`",
        "",
        "The digest is the reviewable part. An index is a binary blob and its "
        "contents cannot be read off a diff; this changes if a single row moves, "
        "so a rebuild that claims to be identical can be checked rather than "
        "believed.",
        "",
        "## What this file does NOT establish",
        "",
        "Nothing about retrieval quality. It records what went in, not whether "
        "the top-10 for a given query is useful — that is the Researcher's "
        "contract (§4.2) and is measured by exemplar overlap per attempt, "
        "reported in the loop dynamics (§4.6).",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve rows and check the RAG contract without loading the "
             "encoder or writing an index. Runs on CPU in seconds and is what "
             "CI uses -- the wall is testable without a model.",
    )
    args = ap.parse_args()

    set_seed()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))

    if args.dry_run:
        inputs = cfg["inputs"]
        rows, _ = load_training_rows(
            "A",
            split_map=inputs["split_map"],
            k2_assignments=inputs["k2_assignments"],
            cleaned_csv=inputs["cleaned_csv"],
            hold_out_dev=False,
        )
        assert_rag_contract(rows.review_ids, inputs["split_map"])
        print(
            f"dry-run OK: {len(rows)} R1 region-A rows would be indexed, "
            f"levels {rows.class_counts}, digest "
            f"{id_digest(rows.review_ids)[:16]}... "
            "No R2 ids, no Gold-300 ids. Nothing written."
        )
        return

    res = build(cfg)
    write_result(res, cfg["outputs"]["manifest_json"], config_path=args.config)
    write_text_lf(cfg["outputs"]["manifest_md"], render_md(res, cfg))
    print(
        f"indexed {res['n_indexed']} rows -> {res['persist_dir']} "
        f"({res['collection']}); manifest at {cfg['outputs']['manifest_json']}"
    )


if __name__ == "__main__":
    try:
        main()
    except (IndexContractError, SplitContractError) as exc:
        raise SystemExit(f"REFUSED: {exc}")
