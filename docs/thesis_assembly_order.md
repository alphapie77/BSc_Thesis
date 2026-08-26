# Final thesis assembly order

No university `.docx`, LaTeX class or formatting guide is currently present in
the repository. This order defines content placement without inventing local
margin, font, signature or binding rules.

## Front matter

1. University title page — institutional fields pending
2. Candidate declaration — exact university wording pending
3. Supervisor certificate/approval page — exact university wording pending
4. Acknowledgements — researcher-authored personal text pending
5. Abstract — `docs/chapters/abstract.md`; keywords and remaining front-matter
   fields — `docs/thesis_front_matter.md`
6. Table of contents
7. List of tables
8. List of figures
9. List of algorithms — generated from Algorithms 5.1 and 5.2
10. Abbreviations and symbols — `docs/thesis_abbreviations.md`

## Main text

1. `docs/chapters/chapter1/Introduction.md`
2. `docs/chapters/chapter2/Related_Work.md`
3. `docs/chapters/chapter3/Research_Methodology.md`
4. `docs/chapters/chapter4/Verification_and_Validation.md`
5. `docs/chapters/chapter5/Neuro_Symbolic_Multi_Agent_Framework.md`
6. `docs/chapters/chapter6/Experimental_Results_and_Analysis.md`
7. `docs/chapters/chapter7/Discussion_and_Limitations.md`
8. `docs/chapters/chapter8/Conclusion_and_Future_Work.md` — conclusion, contributions and future
   work. This material was promoted out of Chapter 7 under the Phase 1 structure
   recommendation in `docs/thesis_phase1_audit_report.md` §3. If the university
   template later mandates exactly seven chapters, Chapters 7 and 8 will require
   an explicit structural merge rather than parallel duplicate sections.

## End matter

1. `docs/generative_ai_declaration.md`
2. References rendered from `docs/chapters/references.bib` under IEEE style;
   this file contains exactly the works cited by Chapters 1–8. The larger
   `docs/references_ieee.bib` remains the master research registry and is not
   rendered wholesale in the submitted thesis.
3. Appendix A — `docs/appendices/appendix_a_reproducibility.md`
4. Appendix B — `docs/appendices/appendix_b_human_evaluation_ethics.md`
5. Appendix C — `docs/appendices/appendix_c_responsible_nlp.md`
6. Appendix D — `docs/appendices/appendix_d_plot_attribution.md`
7. Appendix E — `docs/appendices/appendix_e_symbolic_prompts_traces.md`
8. Appendix F — `docs/appendices/appendix_f_supplementary_results.md`
9. Appendix G — `docs/appendices/appendix_g_artifact_provenance.md`
10. Appendix H — `docs/appendices/appendix_h_postrun_interface.md`

Figures will be inserted only after the non-visual content and disclosures above
are stable. Final pagination and automatically generated lists wait for the
university template.
