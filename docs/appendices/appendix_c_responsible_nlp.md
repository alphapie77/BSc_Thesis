# Appendix C — Responsible NLP and artifact statement

This statement consolidates the study's intended use, data governance, human
evaluation, computational reporting and release boundaries. It describes the
evidence available for this thesis rather than asserting compliance with an
external institutional or venue-specific checklist.

**Table C.1. Responsible-NLP reporting and artifact-release statement**

| Reporting item | Evidence and study standing | Status |
|---|---|---|
| Language named precisely | Bangla (Bengali), Bengali script; native-speaker evaluation in Chapters 1/6/7 | Complete |
| Intended use | Research and pre-writing hypothesis generation, not audience prediction or autonomous decisions | Complete |
| Data provenance | `docs/dataset_card.md`; source-confound limitation retained | Complete with limitation |
| Personal/sensitive data | Coded human responses; identities and consent kept private | Complete |
| Human evaluation | Appendix B, HEDS record, blinded instrument and scorer | Complete |
| Ethics standing | Consent/data handling reported; no institutional approval or exemption claimed | Complete as disclosure; no institutional classification asserted |
| Licences | Review-source record; the 120-plot corpus is attributed under CC BY-SA in Appendix D | Reported with redistribution condition |
| Models and versions | Chapters 4/5, Appendix A, configs and environment snapshots | Complete |
| Hyperparameters/search ranges | Appendix A plus versioned YAML configs | Complete by artifact reference |
| Number of runs/seeds | Five-seed verifier sensitivity; Phase-5 seeds 42/43/44 as blocks | Complete |
| Statistical uncertainty | Paired bootstrap, BH correction, McNemar; human item bootstrap | Complete |
| Compute hardware | Environment snapshots and Appendix A | Complete |
| Compute hours | No canonical consolidated wall-clock total exists; hardware, calls, tokens and producing runtime snapshots are reported instead | Not claimed |
| Negative/null results | Clusterability, first human instrument, B calibration and symbolic weight verdict retained | Complete |
| Generative-AI disclosure | The declaration preceding the references identifies the roles of generative assistance and researcher verification | Reported |
| Artifact release safeguards | Raw data read-only; private consent excluded; provider payload archives external/manifested | Complete |

The principal foreseeable misuse is to present generated comments as measured
audience opinion or market evidence. The study does not support that use. It
also does not support demographic profiling, individual-level inference,
automated marketing decisions or box-office forecasting. Any release of the
plot corpus retains the attribution and share-alike obligations recorded in
Appendix D, while private participant identities and consent records remain
outside the research artifact.
