# Thesis A-to-Z consistency audit — 2026-08-23

## Scope and authority

This audit read the seven active chapters, front matter, appendices, assembly
order, table/figure manifest, STATUS, protocol and normative pipeline against
the frozen result artifacts. On quantities, STATUS and computed artifacts were
treated as authoritative; on methods, `research_pipeline_en.md` was treated as
authoritative. Historical English-arm material was not reintroduced because the
researcher explicitly deferred it outside the active four-RQ thesis. No model
generation, split, threshold, score or statistical test was rerun.

## End-to-end coverage

| Thesis stage | Active location | Audit finding |
|---|---|---|
| Problem, claim boundary and four RQs | Chapters 1 and 7 | Present; response generation is distinguished from audience prediction and discrete personas |
| Literature and gap | Chapter 2 | Present across synthetic audiences, self-correction, RAG, neuro-symbolic validation, Goodhart risk, Bangla NLP and human evaluation |
| Raw review provenance and cleaning | Chapter 3.1 | Present with exact workbook hash, 5,000→4,730 audit and unrecoverable row-level source limitation |
| Frozen Gold/R1/R2 partition | Chapter 3.2 | Present; Gold-300 is described as eval-only and absent from training/RAG/tuning |
| Plot stimuli and licensing | Chapter 3.3 and Appendix D | Present: 3,135 candidates→124 mechanical survivors→120 frozen plots→30/90 split; revision-level attribution retained |
| Construct discovery and validation | Chapter 3.4–3.8 | Present, including rejected source clusters, failed Gold-300 ordinal instrument and successful fresh-R1 comparative instrument |
| Verifier development and isolation | Chapter 4 | Present; A is in-loop, B is outcome-only, and B calibration null is retained |
| Agent roles and intervention contracts | Chapter 5 | Present; audit added the missing bounded-workflow defence and model-calling-role disclosure |
| Frozen 5,400-case execution | Chapters 5.8 and 6.1–6.2 | Present with registered key surface, seeds as blocks, archive integrity and 7,068 local/654 hosted calls |
| Automated, human and sensitivity results | Chapter 6 | Present; audit added previously omitted Distinct-1/2 and Self-BLEU-4 ranges |
| Interpretation, threats and responsible use | Chapter 7 and Appendices B/C | Present; no institutional approval/exemption is claimed, while consent and convenience-sample pressure are disclosed |

## Corrections made by this audit

1. Table 5.1 previously mixed a three-Writer-attempt ceiling with total logical
   model calls. It now separates Writer calls from Reflector/critique/judge
   calls, which is consistent with the observed symbolic-loop mean of 3.630.
2. Chapter 5 previously used an autonomous-system caption without the normative
   workflow qualification. It now states that two roles call a model, two are
   deterministic/tool roles, routing is bounded, and no single-agent-vs-
   multi-agent architecture ablation was performed.
3. Chapters 1 and 7 no longer define the work through the retired audience-
   simulation wording.
4. Chapter 6 now reports the frozen lexical-diversity ranges instead of naming
   Distinct-n and Self-BLEU only in limitations.
5. Active submission text no longer presents an institutional ethics
   determination as a required pending result. It reports only evidenced adult
   consent/data handling and makes no approval or exemption claim.
6. The bibliography now follows first citation in final assembly order. All
   cited entries precede the retained uncited research registry; chapter keys,
   BibTeX keys and the CSV identity map were remapped together.

## Literature closure

Consensus was attempted first with four narrow 2025–2026 searches, but the
configured account had exhausted its 30-search monthly quota and returned no
new records. The audit therefore does not misrepresent Consensus closure as
complete. alphaXiv discovery and full-paper inspection identified Saleh et al.
(2026, arXiv:2606.30524), whose controlled comparison cautions that added
multi-agent complexity may improve structure without improving lexical quality
and can impose large token cost. This evidence changed Chapter 5's terminology
and claim boundary; it did not change the frozen experiment.

## Items that cannot honestly be completed from repository evidence

- The researcher subsequently confirmed Mendeley Data version 3 and supplied
  DOI `10.17632/vwp7gnj3d6.3`; Chapter 3 and the bibliography now cite that
  version. The exact download date remains unrecorded, so the local workbook is
  additionally bound by SHA-256 rather than dated from filesystem metadata.
- University template fields, declaration wording, acknowledgements and final
  pagination remain external author/institution inputs.
- A consolidated compute-hours scalar is not reconstructed; existing runtime
  provenance remains the evidence unless a venue explicitly requires it.
- Remaining planned figures are separate visual work. Their absence does not
  imply a missing experimental stage because every associated table/result is
  already present and source-mapped.

## Citation-order contract

`src/common/order_thesis_bibliography.py` scans the thesis in declared assembly
order, assigns `b1`, `b2`, … by first appearance, then appends uncited registry
records in their prior order. It refuses unresolved citations and updates
`docs/references_ieee.bib`, active thesis citation tokens and
`docs/reference_key_map_full.csv` under one mapping. Uncited papers are retained
for traceability, not forced into the prose.
