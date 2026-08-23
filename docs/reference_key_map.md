# Stable IEEE bibliography-key map

The final consolidated bibliography is `docs/references_ieee.bib`. Source prose
uses `b1`, `b2`, ... as stable BibTeX keys. IEEE rendering converts these to
numeric citations such as `[1]` and `[2]`; the letter `b` is not printed.

> **SUPERSEDED SNAPSHOT.** This page preserves the earlier 29-source core audit
> and must not be used as the current key authority. The active seven chapters
> cite 55 unique sources; the thesis library contains 143 entries. Use
> `docs/reference_key_map_full.csv` for the current `b` keys, metadata standing,
> identifiers, and cited/uncited status.

This page documents the historical 29 chapter-cited core records in readable form. The
complete machine-auditable map for **all 141 records (`b1`--`b141`)** is
`docs/reference_key_map_full.csv`. Keys `b30`--`b141` consolidate the unique
records from the earlier 127-entry research registry after DOI/eprint/title
deduplication; the registry itself remains unchanged as an audit trail.

| Key | Short reference | Verification source/status | Primary thesis use |
|---|---|---|---|
| b1 | Lappas & Filippas, synthetic-audience review | DOI/DBLP verified; not indexed by alphaXiv title resolver | scope and validity limits |
| b2 | Mixture-of-Personas | arXiv 2504.05019 | persona-conditioned generation |
| b3 | SimAB | alphaXiv full first page, 2603.01024 | recent synthetic-audience system |
| b4 | Lewis et al., RAG | alphaXiv PDF, 2005.11401 | foundational RAG |
| b5 | Yang & Klein, FUDGE | alphaXiv PDF + ACL metadata | classifier-guided generation |
| b6 | Self-Refine | alphaXiv PDF, 2303.17651 | intrinsic iterative refinement |
| b7 | Reflexion | alphaXiv PDF, 2303.11366 | verbal feedback and memory |
| b8 | Huang et al. | alphaXiv PDF + ICLR status | intrinsic self-correction limits |
| b9 | Kamoi et al. | alphaXiv PDF + TACL DOI | self-correction taxonomy |
| b10 | Mirzaei | alphaXiv PDF, 2607.28576 | equal-token resampling control |
| b11 | HybridRAG-BN | alphaXiv PDF, 2608.13004 | closest Bangla RAG-verifier adjacency |
| b12 | SymDiag | alphaXiv PDF + printed KDD DOI | neuro-symbolic diagnosis/repair |
| b13 | Akter et al., EST | ACL Anthology primary record and DOI | proxy gaming/Goodhart boundary |
| b14 | BanglaBERT | alphaXiv PDF + ACL Anthology metadata | Bangla encoder |
| b15 | LaBSE | alphaXiv PDF + ACL Anthology metadata | embeddings/retrieval/clustering |
| b16 | Kiritchenko & Mohammad | ACL Anthology primary record | comparative annotation |
| b17 | Fageot et al. | alphaXiv PDF, 2602.08033; authors resolved | ratings plus comparisons |
| b18 | HEDS 3.0 | alphaXiv PDF + ACL Anthology metadata | human-evaluation reporting |
| b19 | Krippendorff | publisher metadata | agreement coefficient |
| b20 | MAUVE | alphaXiv discovery + NeurIPS record | distributional text comparison |
| b21 | Liu & Meng | alphaXiv full-paper record, 2604.22273 | iteration dynamics |
| b22 | Guo et al. | PMLR primary record | temperature scaling/calibration |
| b23 | Rousseeuw | DOI metadata | silhouette |
| b24 | Tibshirani et al. | DOI metadata | gap statistic |
| b25 | Tibshirani & Walther | DOI metadata | prediction strength |
| b26 | Hubert & Arabie | DOI metadata | adjusted Rand index |
| b27 | McInnes et al. | JOSS DOI metadata | HDBSCAN implementation |
| b28 | Benjamini & Hochberg | DOI metadata | multiplicity correction |
| b29 | Dror et al. | ACL Anthology primary record | NLP significance testing |

## Audit corrections made on 2026-08-23

- The first pass incorrectly described the 29 currently cited records as the
  complete bibliography. The corrected consolidation retains those stable keys
  and appends all 112 unique research-registry records as `b30`--`b141`.
- Forty arXiv discovery records had their author lists resolved through
  alphaXiv metadata. Twenty-one abbreviated non-arXiv author lists were checked
  against publisher, proceedings, or primary-paper metadata. The canonical
  file now contains no `and others`, unresolved, unverified, or not-read audit
  marker; reading status remains recorded separately in the full CSV map.

- The old `axiv2602_08033_comparisonsandratings` entry had unresolved authors.
  AlphaXiv resolves them as Julien Fageot, Matthias Grossglauser, Lê-Nguyên
  Hoang, Matteo Tacchi-Bénard and Oscar Villemaud; this is now `b17`.
- The old `shihab2025est` entry had stale title/year/author ordering and lacked
  the final venue. The final primary record is Akter, Shihab and Sharma,
  Findings of ACL 2026, pp. 10554–10583, DOI
  `10.18653/v1/2026.findings-acl.513`; this is now `b13`.
- AlphaXiv's exact-title resolver did not locate the Lappas–Filippas IEEE Access
  article and returned SimAB instead. The article was therefore verified via
  DOI `10.1109/ACCESS.2026.3703706` and DBLP, while SimAB is retained separately
  as `b3`.
- `HybridRAG-BN` is added as adjacent, not direct, prior work: it is Bangla
  KBQA with BM25/BGE-M3, Gemma generation and a LoRA-fine-tuned verifier. The
  present thesis generates cinema responses, does not fine-tune an LLM and
  keeps its outcome verifier outside the loop.
