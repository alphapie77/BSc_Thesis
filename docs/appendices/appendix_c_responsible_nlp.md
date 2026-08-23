# Appendix C — Responsible NLP and artifact checklist

| Reporting item | Repository evidence | Status for submission |
|---|---|---|
| Language named precisely | Bangla (Bengali), Bengali script; native-speaker evaluation in Chapters 1/6/7 | Complete |
| Intended use | Research and pre-writing hypothesis generation, not audience prediction or autonomous decisions | Complete |
| Data provenance | `docs/dataset_card.md`; source-confound limitation retained | Complete with limitation |
| Personal/sensitive data | Coded human responses; identities and consent kept private | Complete |
| Human evaluation | Appendix B, HEDS record, blinded instrument and scorer | Complete |
| Ethics standing | Consent/data handling reported; no institutional approval or exemption claimed | Complete as disclosure; no institutional classification asserted |
| Licences | Review-source record; 120-row plot corpus CC BY-SA attribution in Appendix D | Complete; Appendix D must ship with any plot derivative |
| Models and versions | Chapters 4/5, Appendix A, configs and environment snapshots | Complete |
| Hyperparameters/search ranges | Appendix A plus versioned YAML configs | Complete by artifact reference |
| Number of runs/seeds | Five-seed verifier sensitivity; Phase-5 seeds 42/43/44 as blocks | Complete |
| Statistical uncertainty | Paired bootstrap, BH correction, McNemar; human item bootstrap | Complete |
| Compute hardware | Environment snapshots and Appendix A | Complete |
| Compute hours | Not reconstructed without timestamp-based script | **Pending if venue requires a scalar** |
| Negative/null results | Clusterability, first human instrument, B calibration and symbolic weight verdict retained | Complete |
| Generative-AI disclosure | `docs/generative_ai_declaration.md` | Complete, subject to venue wording |
| Artifact release safeguards | Raw data read-only; private consent excluded; provider payload archives external/manifested | Complete |

This checklist is a repository audit, not a claim of compliance with an unknown
university or venue form. The final submission should transfer these answers
into the required official checklist verbatim and preserve the section links.
