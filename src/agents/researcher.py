#!/usr/bin/env python3
"""Researcher -- the deterministic tool-caller. SS4.2 component 1.

Makes NO LLM call, by contract. That is not an implementation detail: SS4.0's
identity sentence rests on it ("2 of 4 components make no LLM calls"), and
decision 19's cost model charges zero calls for this component, so an LLM here
would silently invalidate E[calls] and therefore tau*.

⛔ FORCED DEVIATION FROM SS4.2, and it is not a preference
-----------------------------------------------------------
SS4.2 specifies "ChromaDB query from plot **key-phrases**". We do not extract
key-phrases. The query is the LaBSE embedding of the plot text itself.

Both available ways to get key-phrases are closed to us:

  * TF-IDF / IDF-based keyphrase extraction -- **inviolable rule 7** forbids
    TF-IDF in the main pipeline, and the rule-7 amendment is unsigned
    (docs/rule7_amendment_packet.md).
  * An LLM call -- that would make the Researcher generative, break its own
    contract, break SS4.0's naming, and add an uncounted call to E[calls].

So the only route consistent with both constraints is dense retrieval over the
whole synopsis, which is what LaBSE is for. Logged as a deviation, not silently
adopted.

⚠️ KNOWN RISK, recorded rather than hidden: a GRANULARITY MISMATCH. The plots
are multi-sentence synopses; the indexed reviews average ~8 words. Embedding a
long document to retrieve very short ones is not what either text length is
ideal for, and retrieval may be weak. SS4.2 already requires exemplar overlap to
be logged per attempt, and that log is the instrument that will show it -- so the
risk is measurable rather than merely acknowledged.

THE RETRY CONTRACT
------------------
SS4.2: on retry "the original persona+plot query ALWAYS stays anchored; feedback
keywords only AUGMENT, never replace." Implemented literally -- the retry query
string begins with the original query string, and a test asserts that. The
failure this prevents is query drift: three attempts chasing the Reflector's
last sentence and retrieving exemplars less and less related to the plot, which
would look like the loop failing to improve rather than like retrieval decaying.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

#: SS4.2: "cosine, top-10, within same persona label". The word persona is
#: retired; the filter is not. ref: docs/research_pipeline_en.md SS4.2
TOP_K = 10

#: SS4.2's routing-ablation trigger: "if overlap <50% with no pass-rate gain,
#: disable re-retrieval and route retries straight to the Writer". Pre-committed
#: in docs/protocol.md SS4 decision 4. Not tuned here.
OVERLAP_DISABLE_BELOW = 0.50


@dataclass(frozen=True)
class Retrieval:
    """What the Researcher returns, plus what SS4.6 needs to audit it."""

    review_ids: tuple[str, ...]
    texts: tuple[str, ...]
    query_text: str
    #: Fraction of ids shared with the previous attempt. None on attempt 1.
    #: SS4.2 requires this logged per attempt; it is the only evidence that
    #: re-retrieval does anything, and the input to the SS5.1b routing ablation.
    overlap_with_previous: float | None


def build_query(plot: str, feedback_keywords: list[str] | None = None) -> str:
    """Anchored query. The original text always leads; feedback only appends.

    Deliberately string concatenation rather than a weighted embedding average:
    the anchoring property has to be CHECKABLE. A test can assert that the
    original query is a prefix of the retry query; it cannot assert anything
    comparable about two averaged vectors, and an unverifiable guarantee is the
    kind this project has already been bitten by.
    """
    query = plot.strip()
    # Filter BEFORE testing for emptiness. `["", "  "]` is a truthy list, so the
    # obvious `if feedback_keywords:` appends a trailing space and produces a
    # query that differs from attempt 1's by whitespace alone -- enough to change
    # the embedding, and therefore to make "re-retrieval changed the exemplars"
    # true for no reason. Caught by test_empty_and_whitespace_feedback_changes_nothing.
    kept = [k.strip() for k in (feedback_keywords or []) if k.strip()]
    if kept:
        query = query + " " + " ".join(kept)
    return query


def overlap(previous: tuple[str, ...] | None, current: tuple[str, ...]) -> float | None:
    """|intersection| / |current|. None when there is no previous attempt."""
    if previous is None:
        return None
    if not current:
        return 0.0
    return len(set(previous) & set(current)) / len(current)


class Researcher:
    """Queries the R1-only index. Holds no state beyond its handles."""

    def __init__(self, persist_dir: str, collection: str, encoder_name: str,
                 *, device: str | None = None):
        """`device` pins the encoder. Default (None) keeps sentence-transformers'
        own choice, which is CUDA when a GPU exists.

        Retrieval and generation compete for the same VRAM: LaBSE sits on the
        GPU for the whole run while a 12B generator is loaded beside it, and on
        a 16 GB T4 that margin matters. Retrieval is 60 short queries for the
        dev-plots -- seconds on CPU -- so callers that also load a generator
        pass device="cpu". The embedding is identical either way; only the
        placement changes.
        """
        from chromadb import PersistentClient
        from chromadb.config import Settings
        from sentence_transformers import SentenceTransformer

        self._client = PersistentClient(
            path=persist_dir, settings=Settings(anonymized_telemetry=False)
        )
        self._collection = self._client.get_collection(collection)
        self._encoder = SentenceTransformer(encoder_name, device=device)

    def retrieve(
        self,
        plot: str,
        target_level: int,
        *,
        feedback_keywords: list[str] | None = None,
        previous_ids: tuple[str, ...] | None = None,
        k: int = TOP_K,
    ) -> Retrieval:
        query_text = build_query(plot, feedback_keywords)
        # normalize_embeddings so inner product is cosine, matching the space
        # the collection was created with in build_index.py. A mismatch here is
        # silent and would degrade retrieval without raising.
        vec = self._encoder.encode(
            [query_text], normalize_embeddings=True, show_progress_bar=False
        ).tolist()

        res = self._collection.query(
            query_embeddings=vec,
            n_results=k,
            # The axis-level filter is SS4.2's "within same persona label".
            # Applied in the query rather than by post-filtering, so k really is
            # k: post-filtering would return fewer than 10 exemplars whenever
            # the top-10 straddled both levels, and the Writer's prompt would
            # quietly vary in length between calls.
            where={"axis_level": int(target_level)},
        )
        ids = tuple(res["ids"][0])
        texts = tuple(res["documents"][0])
        return Retrieval(
            review_ids=ids,
            texts=texts,
            query_text=query_text,
            overlap_with_previous=overlap(previous_ids, ids),
        )
