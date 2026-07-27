# Related Work — running annotated bibliography

> Not a chapter draft. This is the working register: one entry per paper, filled
> **when read**, never from an abstract alone. Ch.2 is assembled from these
> entries; §5.x comparison tables are assembled from the "Numbers to compare"
> field.
>
> Rule: nothing is cited in the thesis that has no entry here.
> BibTeX key must match `docs/references.bib`.

## Status legend
`[ ]` not read · `[~]` skimmed · `[x]` read + entry complete

---

## Tier 1 — Load-bearing (the thesis argument collapses without these)

### [ ] huang2024selfcorrect — Huang et al., ICLR 2024
*Large Language Models Cannot Self-Correct Reasoning Yet*
- **Role:** theoretical anchor. Justifies why the Critic must be **external**.
- **Feeds:** Ch.1 §1.1(2), Ch.2 §self-correction, RQ2 motivation.
- **Read for:** the exact claim boundary — what fails (intrinsic, no oracle) vs
  what is not tested. Do not overstate it.
- **Numbers to compare:** their self-correction deltas vs our self-critique baseline.
- **Notes:**

### [ ] kamoi2024when — Kamoi et al., TACL 2024
*When Can LLMs Actually Correct Their Own Mistakes?*
- **Role:** intrinsic-vs-extrinsic taxonomy — supplies our framing vocabulary.
- **Feeds:** Ch.2 taxonomy paragraph; positions our verifier as extrinsic feedback.
- **Notes:**

### [ ] mop2025 — Mixture-of-Personas, Findings of ACL 2025 (arXiv 2504.05019)
- **Role:** **closest competitor.** Borrow formalism (population P, K groups,
  persona g_k). Uses IMDB/SST-2 — overlaps our English arm.
- **Feeds:** Ch.2, and the head-to-head comparison table.
- **Numbers to compare:** MAUVE (this is why §C mandates `mauve-text`),
  persona-conditioning accuracy, K selection method.
- **Key question when reading:** how do they *validate* personas? If they do not
  human-validate, that gap is our contribution ①.
- **Notes:**

### [ ] sands2026 — Sands et al., NCAA 2026 (doi 10.1007/s00521-026-12247-0)
- **Role:** English persona-prompted movie reviews. Their gaps = our motivation.
- **Feeds:** Ch.1 §1.1(2), Ch.2, and directly the §5.5 cross-lingual framing.
- **Numbers to compare:** their persona-control reliability on English.
- **Notes:**

### [ ] cobbe2021verifiers — Cobbe et al. 2021
*Training Verifiers to Solve Math Word Problems*
- **Role:** origin of the trained-verifier line; our generate–verify–refine
  ancestor. Establishes that a **separately trained** verifier beats self-scoring.
- **Feeds:** Ch.2 §verifiers, Ch.3 verifier design rationale.
- **Notes:**

### [ ] selfcorrectionillusion2026 — arXiv 2606.05976
*The Self-Correction Illusion*
- **Role:** why external-role feedback works — the Critic's justification.
- **⚠️ Verify this exists and the ID is correct before citing.** Provenance is
  weaker than the others; do not carry a citation you have not opened.
- **Notes:**

---

## Tier 2 — Method citations (each defends one design choice)

| Key | Paper | Defends |
|---|---|---|
| `rousseeuw1987` | Rousseeuw 1987 | Silhouette |
| `tibshirani2001gap` | Tibshirani et al. 2001 | Gap statistic (B=100) |
| `tibshirani2005ps` | Tibshirani & Walther 2005 | Prediction strength; the PS ≥ 0.8 rule |
| `hubert1985ari` | Hubert & Arabie 1985 | ARI — incl. the trap-check |
| `fraley2002gmm` | Fraley & Raftery 2002 | GMM/BIC robustness |
| `campello2013` / `mcinnes2017` | HDBSCAN | K-free robustness check |
| `krippendorff2019` | Krippendorff 2019 | Ordinal α; the 0.667/0.80 bands |
| `artstein2008` | Artstein & Poesio 2008 | Agreement reporting practice |
| `gwet2008ac1` | Gwet 2008 | AC1 — kappa-paradox guard (needed: class 0 imbalance) |
| `guo2017calibration` | Guo et al., ICML 2017 | ECE + temperature scaling |
| `bhattacharjee2022banglabert` | Findings of NAACL 2022 | BanglaBERT backbone choice |
| `gebru2021datasheets` | Gebru et al. 2021 | Dataset card |
| `bender2018datastatement` | Bender & Friedman 2018 | Data statement + Bender Rule |
| `mitchell2019modelcards` | Mitchell et al. 2019 | Model card |
| `miller2025multires` | arXiv 2502.17020 | Multi-resolution K alternative |

## Tier 3 — Theory grounding for the three personas (§2.3)
| Key | Source | Use |
|---|---|---|
| `abercrombie1998` | Abercrombie & Longhurst, *Audiences* | consumer→fan→cultist→enthusiast |
| `funk2001pcm` | Funk & James 2001 | Psychological Continuum Model |
| `cuadrado1999` | Cuadrado & Frasquet, *J. Cultural Economics* 23(4) | **Empirical 3-cluster cinema segmentation** (36.1/28.2/35.7) — near-mirror of our scheme |
| `hunt1999` | Hunt, Bristol & Bashaw 1999 | ⚠️ often mis-attributed — **verify authorship before citing** |

## Tier 4 — Bangla NLP precedent (licensing + release practice)
| Key | Source | Use |
|---|---|---|
| `sentigold2023` | arXiv 2306.06147 | Public-API collection + anonymization + non-commercial academic licence |
| `toxlexbn2022` | Data in Brief 2022 | Dedupe + anonymize → Mendeley release path |

---

## Gap table — the sentence Ch.2 must end with

Fill as entries complete. The claim we must be able to defend is:
*persona generation (MoP), classifier gating (FUDGE/detox line), and refinement
loops (math/code) exist in separate literatures; no work joins them in a
low-resource language.*

| Work | Persona generation | Trained external verifier | Refine loop | Low-resource lang | Human-validated personas |
|---|---|---|---|---|---|
| MoP (2025) | ✓ | | | | ? |
| Sands et al. (2026) | ✓ | | | | |
| Cobbe et al. (2021) | | ✓ | ✓ | | |
| FUDGE line | | ✓ (gate) | | | |
| **This work** | ✓ | ✓ | ✓ | ✓ | ✓ |

⚠️ The empty cells are claims. Each must be verified by actually reading the
paper before the table enters the thesis — an unverified "no one has done this"
is the fastest way to lose a reviewer.
