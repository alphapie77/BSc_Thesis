# Thesis structure and end-to-end process audit

**Audit date:** 2026-08-23
**Scope:** seven active chapter drafts and their audited source artifacts.

## Structural result

- Every chapter has exactly one level-1 chapter heading.
- Numbered sections are continuous inside Chapters 1--7.
- Level-3 headings are used only for the four genuine RQ subsections under
  Section 7.2. Table captions are bold captions, not headings or TOC entries.
- All 14 planned tables are present in their target chapters.
- Chapter summaries close every chapter.

## End-to-end process coverage

| Process stage | Where the method is explained | Where evidence/results appear | Standing |
|---|---|---|---|
| Research problem, construct and four RQs | Chapter 1 §§1.1--1.4 | Table 1.1 | Complete |
| Literature position and research gap | Chapter 2 §§2.1--2.9 | Table 2.1 | Complete; bibliography audit remains separate |
| Research design and data-role separation | Chapter 3 §3.1 | frozen pipeline contracts | Complete; review/plot roles and Gold/R1/R2 privileges stated before analysis |
| Raw review audit and cleaning | Chapter 3 §§3.2--3.3 | Table 3.1; `s0_data_xray`, `s1_cleaning_log` | Complete |
| Near-duplicate removal and frozen Gold/R1/R2 split | Chapter 3 §3.3 | Table 3.1; frozen split map | Complete; threshold and isolation rules stated |
| Plot harvesting, review, licensing and dev/eval freeze | Chapter 3 §3.4 | 120 plots, 30/90 split; harvest report/dataset card; Appendix D | Complete; 120/120 exact revisions attributed |
| Source-confound rejection and axis construction | Chapter 3 §§3.5--3.6 | Table 3.2; Region-A/B S2 artifacts | Complete; negative clusterability retained |
| Human construct validation and operational levels | Chapter 3 §§3.7--3.9 | Table 3.3; G-300 and intrusion reports | Complete; failed first instrument retained |
| Verifier candidates, circularity baseline and calibration | Chapter 4 §§4.1--4.6 | Table 4.1; S3 artifacts | Complete; B calibration null retained |
| Verifier privilege/isolation wall | Chapter 4 §4.7 | A/R1 versus B/R2 table and executable guard | Complete |
| Retrieval, prompting, agents, gates and retry policy | Chapter 5 §§5.1--5.7 | Tables 5.1--5.2; S4 artifacts | Complete |
| Frozen main-run execution and provenance contract | Chapter 5 §§5.8--5.9 | Case/score manifests and environment snapshot | Complete |
| Full 5,400-case results and registered inference | Chapter 6 §§6.1--6.5 | Tables 6.1--6.2; Figure 6.1 | Complete |
| Generated-output human evaluation | Chapter 6 §6.6 | Table 6.3; human report | Complete |
| Length, diversity and corpus-realism sensitivity | Chapter 6 §§6.7--6.8 | Table 6.4; Figure 6.2 | Complete with stated limitations |
| Four RQ answers, validity, ethics, practical implications, future work and conclusion | Chapter 7 §§7.1--7.12 | Tables 7.1--7.2 | Complete; no institutional approval/exemption claim is made |

## Important non-completions that are not structural gaps

- The institutional ethics determination remains pending and must not be
  represented as approval.
- CC BY-SA attribution is complete in Appendix D; that appendix must remain in
  every distribution containing the plot derivative.
- Figures 3.1, 3.2, 4.1, 4.2, 5.1 and placement of existing Figure 5.2 remain
  visual-production tasks; their underlying process and evidence are already in
  the chapters.
- Verified abstract, keywords, assembly order, reproducibility/ethics/
  responsible-NLP appendices and the generative-AI declaration are complete.
  University-template pagination, institutional fields, table widths,
  automatically generated lists and researcher-authored acknowledgements remain
  final-document assembly tasks.

No item in this audit authorizes rerunning the frozen 5,400 generations.
