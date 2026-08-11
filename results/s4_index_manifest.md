# S4.1 — the R1-only retrieval index

**886** rows from **R1**, encoded with `sentence-transformers/LaBSE`, cosine space, collection `r1_regionA_k2`.

| Axis level | Rows |
|---|---|
| 0 | 534 |
| 1 | 352 |

## The contract, verified rather than asserted

- **R2 ids present: 0.** Inviolable rule 5 — the RAG index is R1 only.
- **Gold-300 ids present: 0.** Inviolable rule 4 — G is eval-only.

Both are checked in `build_index.py` *before* any vector is written, and the build raises rather than warns. They are checked a second time there against the split map directly, independently of `split_access`, because the frozen split is a promise and a second check is a mechanism.

**Row-set digest (SHA-256 over sorted ids):** `85fc2d7d7ad3281b9dd99a7a0a01f8221a5e7ab762d1c69a0924bbc4468b45bb`

The digest is the reviewable part. An index is a binary blob and its contents cannot be read off a diff; this changes if a single row moves, so a rebuild that claims to be identical can be checked rather than believed.

## What this file does NOT establish

Nothing about retrieval quality. It records what went in, not whether the top-10 for a given query is useful — that is the Researcher's contract (§4.2) and is measured by exemplar overlap per attempt, reported in the loop dynamics (§4.6).
