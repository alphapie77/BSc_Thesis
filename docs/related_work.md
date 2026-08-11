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

### [x] huang2024selfcorrect — Huang et al., ICLR 2024
*Large Language Models Cannot Self-Correct Reasoning Yet* · arXiv 2310.01798 v2
- **Role:** theoretical anchor. Justifies why the Critic must be **external**.
- **Feeds:** Ch.1 §1.1(2), Ch.2 §self-correction, RQ2 motivation, §5.1 ablation design.
- **Read:** 2026-08-01. ⚠️ **Read by Claude, not by Sabbir** — see the note at the
  end of this entry. Sections and table numbers below are from the arXiv v2 HTML.

**The claim, exactly as they scope it (§2, ¶ "Consequently…"):** they define
**intrinsic self-correction** as self-correction *"without any external or human
feedback"*, and state that all unqualified uses of "self-correction" in the
paper mean that setting. The finding is that LLMs *"struggle to self-correct
their responses without external feedback, and at times, their performance even
degrades"* (abstract).

**What the claim does NOT cover** — this is the boundary the entry was told to
find:
- Only **reasoning** benchmarks: GSM8K (1,319 items), CommonSenseQA (1,221 dev),
  HotpotQA (100). **No generation task, no persona control, no low-resource
  language.**
- Only **intrinsic** correction. External feedback is explicitly *endorsed*
  (below), not refuted.
- The title's *"Yet"* is load-bearing: they frame it as the current state, not a
  ceiling.
- Models tested: GPT-3.5-Turbo, GPT-4, GPT-4-Turbo, Llama-2-70b-chat.

**Numbers (Tables 2–4), accuracy %:**

| Setting | Model | GSM8K | CommonSenseQA | HotpotQA |
|---|---|---|---|---|
| Standard prompting | GPT-3.5 | 75.9 | 75.8 | 26.0 |
| Self-correct **with oracle** | GPT-3.5 | **84.3** | **89.7** | **29.0** |
| Self-correct **intrinsic**, r1 → r2 | GPT-3.5 | 75.1 → **74.7** | 38.1 → **41.8** | 25.0 → 25.0 |
| Standard prompting | GPT-4 | 95.5 | 82.0 | 49.0 |
| Self-correct **intrinsic**, r1 → r2 | GPT-4 | 91.5 → **89.0** | 79.5 → 80.0 | 49.0 → **43.0** |
| Standard prompting | Llama-2-70b | 62.0 | 64.0 | — |
| Self-correct **intrinsic**, r1 → r2 | Llama-2-70b | 43.5 → **36.5** | 37.5 → **36.5** | — |

Every intrinsic number is **at or below** its standard-prompting baseline. The
oracle row is the one that improves — and they argue (§3.2) that oracle results
*"can only be regarded as indicative of an oracle's performance"*, since if you
already hold the ground truth there is little reason to run the model at all.

**Why it degrades (§3.3):** on GSM8K, GPT-3.5 keeps its first answer 74.7% of
the time; among the rest it is **more likely to change a correct answer to an
incorrect one** than the reverse. Their diagnosis: *"LLMs cannot properly judge
the correctness of their reasoning."* **This is the sentence our whole design
rests on** — it is a claim about the *judge*, not about the *generator*, which
is exactly why we externalise the judge.

**Two further results, both of which bite on our ablation table:**
- **§4 — multi-agent debate is self-consistency in disguise.** At a matched
  9 model calls: debate **83.0** vs self-consistency **88.2** on GSM8K. The gain
  people attribute to "critique" is really selection across generations.
- **§5 — a prompt-design confound.** Self-Refine's reported gain on
  CommonGen-Hard came partly from stating the requirement *only* in the feedback
  prompt. Putting it in the initial prompt instead: standard **81.8** vs **75.1**
  after self-correction. So "self-correction helped" can just mean "the second
  prompt was more informative than the first".

**They endorse our approach by name (§6, "Leveraging external feedback"):**
*"when valid external feedback is available, it is beneficial to leverage it
properly"*, citing **Cobbe et al. 2021**, Lightman et al. 2023 and Wang et al.
2023b — *"train a verifier or a critique model on a high-quality dataset to
verify or refine LLM outputs"*. That is this thesis, in a low-resource language,
on a generation task. **Huang et al. is not an obstacle we route around; it is
the paper that names our direction as the promising one.**

**How to cite it without overstating (use this wording):**
> Huang et al. (2024) show that *intrinsic* self-correction — without external
> feedback — fails to improve, and often degrades, LLM performance on reasoning
> benchmarks, and attribute this to the model's inability to judge the
> correctness of its own output. This motivates externalising the judge; it does
> not by itself establish that an external verifier helps on persona-controlled
> generation in Bangla, which is what RQ2 tests.

❌ **Do not write** "Huang et al. proved LLMs cannot self-correct, therefore we
use an external verifier." They did not test our setting, and an examiner who
has read the paper will say so.

**Consequences for our design (raised as open questions, not adopted):**
1. **Inference-cost matching.** §6 asks that self-correction be compared against
   baselines *"with comparable inference costs"*. Our ablation rows 1–3 are
   single-call; rows 4–8 loop. Row 6 beating row 1 may be partly a call-count
   effect. → see open decision 9.
2. **A self-consistency / best-of-N baseline at matched calls** is the strong
   baseline they demand, and our table has none. → open decision 9.
3. **Prompt parity.** Row 1's zero-shot persona prompt must state the persona
   requirement as fully as the verifier feedback does, or our gain is §5's
   confound wearing our variable names. → open decision 10.

**Follow-up reading this entry generated:** Cobbe et al. 2021 (already Tier-1 —
now clearly load-bearing, since Huang et al. point at it as the alternative);
Wang et al. 2022 self-consistency (needed for the baseline above); Madaan et al.
2023 Self-Refine (the paper §5 critiques, and the closest thing to our loop
without a trained verifier).

> **Provenance of this entry.** Claude read the paper and wrote this; Sabbir has
> not read it yet. The file's own rule is *"filled when read, never from an
> abstract alone"* — that rule is satisfied for the *content* (full text, v2),
> but not for the *reader*. **Everything above is checkable against the section
> and table numbers given.** An examiner will ask Sabbir about this paper
> directly, and this entry is a summary, not a substitute for the two hours it
> takes to read §3 and §6.

> **All six Tier-1 entries below were briefed on 2026-08-01 in
> `docs/base_papers_brief.md`**, with reading depth tagged per paper (📗 body
> read / 📘 partial / 📙 abstract + record). That file carries the numbers, the
> quotes and the design consequences; these entries carry the register fields.
> **Read by Claude, not by Sabbir** — the depth tags in the brief are the honest
> record of what was actually read.

### [~] kamoi2024when — Kamoi et al., TACL 2024
*When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey* · TACL 12: 1417–1440
- **Role:** intrinsic-vs-extrinsic taxonomy — supplies our framing vocabulary.
- **Feeds:** Ch.2 taxonomy paragraph; **Ch.1 gap sentence**; decision 9.
- 🎁 **§5.2: *"Fine-tuning enables self-correction when large training data is
  available but is unexplored for small training data."*** Our verifier trains on
  **R1 = 2,162 rows**. A TACL survey names our exact regime as *unexplored* —
  a gap sentence we do not have to argue for.
- **§5.1:** *"Self-correction is effective in tasks where reliable external
  feedback is available"* — the sentence RQ2 rests on.
- **RQ1 finding:** *no* prior work shows successful correction from **prompted-LLM**
  feedback → predicts our row 7 loses, which is why it is the right baseline.
- **§6 "Strong Baselines":** *"Self-correction is often not compared with
  sufficiently strong baselines"* — independent confirmation of decision 9.
- **Taxonomy (Table 1)** — use this vocabulary: Intrinsic / Oracle /
  Fair-Asymmetric / Unfair-Asymmetric / **Cross-Model**. ⬛ **We must place our
  own system in it before a reviewer does** — REFINER and RL4F (a large LM with a
  trained T5 feedback model) sit under Cross-Model and are the closest structural
  analogue to ours.
- ⬛ **Get their experiment-design checklist and run §5.1 against it before S6.**

### [x] mop2025 — Mixture-of-Personas (arXiv 2504.05019) ⚠️ venue unverified
- **Role:** **closest competitor.** Borrow formalism (population P, K groups,
  persona g_k). Uses IMDB/SST-2 — overlaps our English arm.
- **Feeds:** Ch.2, and the head-to-head comparison table.
- **Numbers to compare:** MAUVE (this is why §C mandates `mauve-text`),
  persona-conditioning accuracy, K selection method.
- **Key question when reading:** how do they *validate* personas? If they do not
  human-validate, that gap is our contribution ①.
- **Notes:**

- **✅ [x] ENTRY COMPLETE (2026-08-01, from the PDF).** Every register field
  below is now filled from §4.1–4.5.
- **✅ Persona validation: NONE.** §4 has only Steerability / Synthetic Data
  Generation / Transferability / Ablations, plus §7 Limitations. No human
  evaluation anywhere. **Contribution ① stands.**
- **✅ K selection: THERE IS NONE. K is fixed at 100 by hand.** §4.1: *"we choose
  the number of personas to be 100 … We then run K-Means and the persona
  synthesizer to extract 100 persona descriptions."* No K-table, no stability
  analysis, no selection criterion. **Our Gate G1 (7 criteria, bootstrap ARI,
  prediction strength) is therefore contribution ②** — and note the conceptual
  gap: they model a population as **100 micro-personas**; we model **3 audience
  types**. Different granularity, and Ch.2 should say so rather than imply we do
  the same thing at different K.
- **✅ Datasets — the pipeline's claim is CONFIRMED:** AGNews (topic) + **Yelp,
  SST-2, IMDB** (sentiment).
- **✅ MAUVE: yes, primary alignment metric**, alongside **FID** and **KL Cosine**
  (their own diversity metric: KL between pairwise-cosine histograms). Encoder
  `all-mpnet-base-v2`; base LLM Llama3-8B-Instruct for MoP *and* all baselines;
  5,000 synthetic responses per method; top M=4 persona–exemplar pairs per input.
  **§C's mandate to use `mauve-text` is justified — the numbers are comparable.**
- **⚠️ Persona-conditioning accuracy: they never measure it.** Alignment is
  distributional (FID / MAUVE / KL Cosine) plus downstream F1. **There is no
  per-persona controllability number in the paper** — which is exactly the axis
  RQ2 measures. Another gap.

**Numbers to compare (Table 1, AGNews / Yelp / SST-2 / IMDB):**

| | FID ↓ | MAUVE ↑ | KL Cosine ↓ |
|---|---|---|---|
| MoP AGNews | **0.951** | **0.871** | 0.069 |
| MoP Yelp | 0.948 | 0.826 | 0.067 |
| MoP SST-2 | 1.131 | 0.855 | 0.319 |
| MoP IMDB | 0.771 | 0.865 | 0.039 |
| best baseline (PICLe/ProGen/AttrPrompt) | 1.769–4.736 | 0.537–0.767 | — |
| MoP improvement | 46–69% | **+13.6% to +41.3%** | 33–80% |

**Table 2 — downstream F1** (DistilBERT trained on 5,000 synthetic samples,
tested on golden test set):

| | AGNews | Yelp | SST-2 | IMDB |
|---|---|---|---|---|
| Golden data | 0.903 | 0.896 | 0.919 | 0.877 |
| **MoP** | 0.871 | 0.867 | 0.845 | **0.865** |
| AttrPrompt | 0.836 | 0.864 | 0.838 | 0.793 |

**Table 4 — ablation, and this one matters to us:**

| | FID ↓ | MAUVE ↑ | KL Cosine ↓ |
|---|---|---|---|
| MoP | 0.951 | 0.871 | 0.069 |
| **w/o exemplars** | **3.694** | **0.552** | **0.560** |
| w/o persona synthesiser | 1.674 | 0.807 | 0.174 |
| w/ random personas | 1.814 | 0.622 | 0.061 |

🔑 **Removing the exemplars is far more damaging than removing the persona
synthesiser** (MAUVE 0.871 → 0.552 vs → 0.807). **The exemplars carry most of
the benefit, not the persona descriptions.** Since our RAG layer is structurally
their exemplar layer, this predicts our row 3 (RAG only) may beat rows 1–2
(persona prompting) by more than expected — and it is an argument that our
ablation is right to separate them.
- **Transferability (Table 3):** MoP trained on Llama3-8B transfers to
  Gemma2-9B (MAUVE 0.957) and Mistral-7B (0.869) without retraining.
- **Formalism to adopt:** p(y|x) = Σₖ πₖ · p_LM(y|gₖ, x), Σπₖ = 1; plus a second
  level weighting in-context exemplars. Our RAG over R1 ≈ their exemplar level.
- ⚠️ **Venue unverified** — arXiv shows no venue, not "Findings of ACL 2025".
  ⚠️ **"IMDB/SST-2" unverified** — abstract names no dataset.
- ⚠️ **Venue still unverified** — arXiv shows none; the pipeline's "Findings of
  ACL 2025" remains unconfirmed. Everything else in this entry is now filled.
### [~] sands2026 — Sands et al., NCAA 2026 (doi 10.1007/s00521-026-12247-0)
- **Role:** English persona-prompted movie reviews. Their gaps = our motivation.
- **Feeds:** Ch.1 §1.1(2), Ch.2, and directly the §5.5 cross-lingual framing.
- **Numbers to compare:** their persona-control reliability on English.
- **Notes:**

- **Their gap is our target:** *"a noticeable gap in emotional richness and
  stylistic coherence"* vs IMDb, despite fluent, structurally complete output.
- **Generator warning:** GPT-4o overemphasises positive emotions; DeepSeek-V3
  most balanced; Gemini-2.0 excessive emotional intensity.
- **Design gap we exploit:** they feed subtitles + screenplays, which exist only
  post-production. Ours is pre-release — synopsis only.
- ⬛ Body not read; read the results section before citing a metric.
### [~] cobbe2021verifiers — Cobbe et al. 2021
*Training Verifiers to Solve Math Word Problems*
- **Role:** origin of the trained-verifier line; our generate–verify–refine
  ancestor. Establishes that a **separately trained** verifier beats self-scoring.
- **Feeds:** Ch.2 §verifiers, Ch.3 verifier design rationale.
- **Notes:**

- **Load-bearing, not background:** Huang §6 names this as the alternative to
  intrinsic correction.
- **Key claim:** *"verification scales more effectively with increased data than
  a finetuning baseline"* — pre-empts "why not fine-tune the generator?".
- **Honest difference:** their verifier **ranks** (best-of-N); ours **gates and
  refines**. Best-of-N is also the cost-matched baseline decision 9 needs.
- ⬛ Body not read (no arXiv HTML for 2021).
### [~] selfcorrectionillusion2026 — arXiv 2606.05976
*The Self-Correction Illusion*
- **Role:** why external-role feedback works — the Critic's justification.
- **⚠️ Verify this exists and the ID is correct before citing.** Provenance is
  weaker than the others; do not carry a citation you have not opened.
- **Notes:**

---

- **Claim:** willingness to correct depends on the chat-template **role label**,
  not the claim's content. Byte-identical claim (SHA-256), only the role varies.
- **Numbers:** +23 to +93 pp; 10/13 cells significant, 3 exceptions all ceiling
  (L₀ ≥ 67%); 9/13 survive Holm–Bonferroni and BH; 26/30 per-task flips on
  Llama-70B logic.
- **Mechanism:** bare wrapper 17–23 pp, role tag a further ~30 pp; nonsense
  `<xqzy>` 30% vs `<memory>` 70%; within-thought duplication control only
  +6.7 pp (p=0.26) → +46.7 pp pure role-tag effect.
- 🔴 **Self-distrust control:** telling the agent to verify its own thoughts
  gives 0–23% vs 70% for the relabel. **Naive self-distrust is not a
  substitute** — which is why our row 7 should lose, mechanistically.
- ⚠️ **Scope:** measured on a *failure pool* (tasks where intrinsic correction
  already failed), so lifts are on a pre-selected subset.
- → **open decision 11**: add row 7b, self-critique under an external role.
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
| `gwet2008ac1` + `vach2023ac1` | Gwet 2008; **Vach & Gerke 2023** | AC1 as the kappa-paradox guard — **and the 2023 critique showing AC1 is not a kappa substitute: it rises mechanically with prevalence skew, so it must never be quoted alone.** Used in the G-300 round-1 diagnosis |
| `clavie2026latentterms` | Clavié et al. 2026, arXiv 2605.29384 | 🔴 **Inverts rule 7's premise.** SAEs on *frozen* dense retrievers extract quasi-Zipfian features that BM25 (i.e. IDF) scores unmodified; **~1/3 are purely lexical**. IDF is not alien to a contextual encoder — the encoder already internalised it. ⚠️ **Cuts both ways:** if IDF is already inside LaBSE, adding it to symbolic may raise its correlation with Verifier-A, which is what the hybrid exists to avoid. Retrieval paper — transfer gap stated at every citation |
| `barata2026hybrid` | Barata 2026, arXiv 2608.02112 | 🔴 **The counterweight, cited against our own preferred conclusion.** A cheap third component took **zero weight in 50/50 folds** and *forcing* it in lowered held-out MRR. *"Standalone benchmark performance is insufficient to establish marginal value in hybrid retrieval."* **Our F1 pilot's +18 is standalone.** Supplies the gate design for rule 7b and for the S3.5 weight: training-fold-only selection, held-out eval, paired bootstrap + Holm, forced-inclusion check |
| `magsarjav2026preprocessing` | Magsarjav et al. 2026, arXiv 2606.24055 | Cited for what it does **not** cover: a 2026 preprocessing study that states it focuses on *"word-based sentiment analysis"*, not BERT-class models. **The 2026 literature still has not tested rule 7's premise on contextual encoders.** Reviewed studies call stopword removal/stemming *"not so important"* — low impact, not harmful. Cited beside **rule 7a**: under-evidenced, but nearly free to keep |
| `guo2017calibration` | Guo et al., ICML 2017 | ECE + temperature scaling. 🔴 **`.bib` entry was MISSING until 2026-08-11** — listed here, never defined, would have failed only at compile. ⚠️ **Cite for the METHOD, not the finding:** their result is over-confidence corrected by T > 1; measured Verifier-A is **under**-confident (T = 0.10918 < 1, ECE 0.11836 → 0.00537). Verifier-B matches their direction (T = 1.09949) but its ΔECE CI straddles zero |
| `bhattacharjee2022banglabert` | Findings of NAACL 2022 | BanglaBERT backbone choice |
| `gebru2021datasheets` | Gebru et al. 2021 | Dataset card |
| `bender2018datastatement` | Bender & Friedman 2018 | Data statement + Bender Rule |
| `mitchell2019modelcards` | Mitchell et al. 2019 | Model card |
| `miller2025multires` | arXiv 2502.17020 | Multi-resolution K alternative |
| `monroe2008fightinwords` | Monroe, Colaresi & Quinn, *Political Analysis* 16(4) | Log-odds with an informative Dirichlet prior. Defends **two** things: the required provenance probe (protocol.md), and S2e's distinctive-vocabulary lists. Chosen because its prior makes **stopword removal unnecessary** — the alternative would be a hand-built Bangla stopword list, which nothing in this project justifies and inviolable rule 7 forbids. |

## Tier 3 — Theory grounding for the ~~three personas~~ audience-engagement construct (§2.3)

> ⚠️ **Heading and contents both need a pass (2026-08-10).** This tier was
> assembled to ground a *three-persona typology*. The typology is gone: K = 2
> since 2026-08-03, and the terminology deviation of 2026-08-10 retires
> *persona* and *type* altogether in favour of an **engagement-specificity
> axis**. `cuadrado1999` in particular was listed as a "near-mirror of our
> scheme" — it is a **3-cluster** cinema segmentation and is no longer a mirror
> of anything we claim. These sources may still ground the *construct* of
> graded audience engagement, which is what Tier 6 says our data supports; they
> no longer support a claim about discrete audience types. **Not silently
> deleted — each entry needs a re-read against the axis framing.**

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

## Tier 5 — Phase 3 method citations (added 2026-08-08)

> **Read status: every entry below is `[ ]` — not read.** They came from a
> Consensus search on 2026-08-08 and exist as index records plus abstracts. They
> are listed here because `protocol.md` §S3.2 and §S3.4 now *rest on them*, and
> the rule of this file is that nothing is cited without an entry. **The rule
> that entries are filled only when read still holds** — these are placeholders
> carrying their own warning, not completed entries.
>
> ⚠️ **Three of them are load-bearing and must be read before the S3.2 result is
> written up**, because each is the sole basis for a design decision:
> `bethard2022seeds` (why the decision rule is not mean ± SD),
> `laurer2023bertnli` (why an arm was added), and `beliveau2024smalldata` (why
> SetFit is registered as an expected loser).

### 5a — Experimental methodology: seeds, variance, model comparison

| Key | Source | What it is used for | Read |
|---|---|---|---|
| `bethard2022seeds` | Bethard 2022, arXiv (22 cit.) | 🔴 **Load-bearing.** Names "vary only the seed to build score distributions for performance comparison" a **risky** use, and sensitivity measurement a **safe** one. This is why S3.2's winner is decided by paired bootstrap, not by best mean ± SD. **It contradicted our own protocol of 2026-08-07.** | `[ ]` |
| `gundersen2023conclusions` | Gundersen et al. 2023, ACM REP (16 cit.) | Small effect sizes + few repetitions → wrong conclusions. Supports 5 seeds over 3. | `[ ]` |
| `casola2022transformers` | Casola et al. 2022, *Machine Learning with Applications* (66 cit.) | Only ~20% of transformer papers report multiple runs; low robustness to seed and hyperparameters. | `[ ]` |
| `coakley2022implementation` | Coakley et al. 2022, IEEE e-Science (4 cit.) | 🔴 **Load-bearing, three times over.** 780 runs across 13 hardware and 4 software environments; **>6 pp** accuracy range from environment alone. Justifies discarding attempt 1, pinning the environment, gating checkpoint resume, and the Ch.4 claim that our 3.5 pp spread is below measurement resolution. | `[ ]` |
| `teodorescu2025kfold` | Teodorescu et al. 2025, *Computers* (61 cit.) | k-fold selection is valid within a model class, unreliable **across** classes. Our seven arms span three. Ch.5 limitation. | `[ ]` |
| `fu2023stability` | Fu et al. 2023, arXiv (4 cit.) | Theoretical stability bound for full fine-tuning vs head tuning — the mechanism behind the instability we are guarding against at n=804. | `[ ]` |
| `xue2023reproducibility` | Xue et al. 2023, venue ⚠️ unverified (3 cit.) | **Cited as a rejected alternative.** Recommends blocked 3×2 CV over repeated standard splits on SNR grounds; rejected 2026-08-08 because it re-draws the train/dev boundary inside R1. Must be represented fairly, which means reading it. | `[ ]` |

### 5b — Small-n classification: the two added arms

| Key | Source | What it is used for | Read |
|---|---|---|---|
| `laurer2023bertnli` | Laurer et al. 2023, *Political Analysis* (266 cit.) | 🔴 **Load-bearing.** +10.7–18.3 pp over classical models at 100–2,500 training texts, *particularly on imbalanced data*. Sole justification for adding the BERT-NLI arm. Our case: 804 rows, ~40% minority. | `[ ]` |
| `tunstall2022setfit` | Tunstall et al. 2022, arXiv (312 cit.) | The SetFit method itself — prompt-free contrastive fine-tuning of a Sentence Transformer. Our LaBSE body is already in the pipeline. | `[ ]` |
| `beliveau2024smalldata` | Beliveau et al. 2024, arXiv (2 cit.) | 🔴 **Load-bearing.** Closest published setting to ours — non-English, small, imbalanced, domain-specific — and finds **BERT-like > SetFit > LLM**. Sole basis for pre-registering SetFit as an *expected loser*, which is what makes either S3.2 outcome informative. | `[ ]` |
| `bucher2024finetuned` | Bucher et al. 2024, arXiv (122 cit.) | Fine-tuned small models beat zero-shot generative models in classification. Supporting, not load-bearing. | `[ ]` |

### 5c — Calibration at small n

| Key | Source | What it is used for | Read |
|---|---|---|---|
| `balanya2022adaptivetemp` | Balanya et al. 2022, *Neural Computing and Applications* (73 cit.) | Expressive calibrators fail under data scarcity; simple scaling stays robust. Why S3.4 **keeps** plain temperature scaling rather than upgrading it. | `[ ]` |
| `guo2025smart` | Guo et al. 2025, arXiv (2 cit.) | Cited **only** for its statement of the bias/variance dilemma under insufficient validation data. We do not adopt SMART. | `[ ]` |

### 5d — The Bangla backbone disagreement

> **These six are cited together and only together.** Individually each looks
> like a result; together they are the argument. Two of them (`hassin2026`,
> `mazumder2025`) use the **same BanglaBlend dataset** and report a **different
> ordering**. That is the point: "BanglaBERT because it is Bangla-native" cannot
> be defended by citation, so the S3.2 ablation has to do the work.
>
> ⚠️ **Citation-count health check, stated rather than hidden:** four of these
> six have **0 citations** and are 2025–2026 conference papers. They are
> adequate as evidence that *the field disagrees* — a disagreement needs only
> that the claims were made and published. They are **not** adequate as evidence
> that any particular model is best, and none is used that way.

| Key | Reported winner | Dataset / n | Cit. | Read |
|---|---|---|---|---|
| `hasan2025banglaemotion` | BanglaBERT (0.83) | Bangla emotion, 7,200 | 1 | `[ ]` |
| `hasan2023banglawar` | BanglaBERT (86%) | Bangla sentiment, 10,861 | 41 | `[ ]` |
| `mitra2025muril` | **MuRIL** (92%) — beats both | Bangla emotion | 0 | `[ ]` |
| `hassin2026banglablend` | **XLM-R** (94%) > BanglaBERT (93.4%) | **BanglaBlend, 7,350** | 0 | `[ ]` |
| `mazumder2025banglaforms` | **IndicBERTv2** (95.44%) > XLM-R > BanglaBERT | **BanglaBlend — same data** | 0 | `[ ]` |
| `mukherjee2023blp` | XLM-R > BanglaBERT | BLP-2023 shared task | 0 | `[ ]` |

⚠️ `mukherjee2023blp` ranked **19th of 30** in that shared task. It is evidence
that the ordering is unstable across teams, **not** evidence that XLM-R is
better, and it is never to be cited as the latter.

`hasan2025banglaemotion` additionally supplies the **methodological precedent**
for our decision rule: it settles the same comparison in the same language with
a **paired bootstrap test**.

---

## Tier 6 — Clusterability and post-clustering inference (added 2026-08-10)

> **Why this tier exists.** Everything above defends *how* we clustered. Nothing
> defended the prior question — **whether this data clusters at all** — and G1's
> own diagnostics (silhouette 0.053, monotone gap statistic, HDBSCAN 100% noise)
> had been answering "no" since 2026-08-03 without a literature to read it
> against. These four entries supply it, and they closed STATUS decision 12.
>
> **Source disclosure:** found via alphaXiv and Scite on 2026-08-10, **not
> Consensus** — the Consensus quota was exhausted (0 searches until 1 September).
> The standing instruction prefers Consensus; it was unavailable, this is
> recorded rather than glossed, and the searches were re-run across two indices
> to compensate for using neither the preferred one nor a single one.

| Key | Source | Read | Defends / forces |
|---|---|---|---|
| `pinto2026drawinglines` | Pinto, Marques & Lopez 2026, arXiv 2605.06989 | `[x]` abstract + full body via PDF query | 🔴 **LOAD-BEARING — this is the paper that retired both *persona* and *cluster*.** k-means on simulated data with no latent groups, and on 8,360 real psychometric respondents. Empirical result: **k = 2, silhouette ≈ 0.31, ARI 0.999 ± 0.001, sizes 50.6/49.4** — numerically almost our region B (49.4/50.6, silhouette 0.039, bootstrap ARI 0.962). Their reading of it: *"geometric stratifications of a latent psychological continuum rather than evidence for discrete subtypes"*, and **"Stability, therefore, is not equivalent to validity."** On correlated Gaussian data: ARI = 1.00, SD 0.00, described as *"an artificial partition of a continuous, anisotropic distribution."* **Our PS ≥ 0.80 rule passing a contentless cut in region B is this phenomenon, not a quirk of our pipeline.** |
| `cornelissen2026contour` | Cornelissen, Zuidema, Burgoyne & Honing 2026, arXiv 2604.13119 | `[x]` full body via PDF query | **Precedent that a negative clusterability result is publishable**, across three musical traditions, using dist-dip after UMAP. Also the sharpest cautionary case in either paper: with no clustering present, k-means places centroids near the leading principal axes, reproducing a previously *published* four-type typology *"for entirely mathematical, not musical reasons."* Conclusion: treat the character as **continuous**. Direct model for how our Ch.4 should report the K = 2 cut. |
| `chen2023selectiveinference` | Chen & Witten 2023, *JMLR* 24 | `[ ]` — cited via `pinto2026drawinglines`; **must be read before Ch.4 is written** | 🔴 **Forces a Ch.5 limitation (deviation of 2026-08-10).** Classical post-hoc tests on cluster-derived groups inflate Type I error, because the same data defines and tests the groups — and large between-group differences appear **even when no population categories exist**. S2e/S2f's φ = 0.3981, χ² = 300.7 and surface AUCs are all post-clustering inference on the defining rows. **They are demoted to descriptive profiling; no p-value from them is evidence.** RQ1-H is untouched — held-out items, annotators blind to the partition. |
| `adolfsson2019clusterability` | Adolfsson, Ackerman & Brownstein 2019, *Pattern Recognition* 88 | `[ ]` | Survey of clusterability methods — the question G1 asked informally and answered with three ad-hoc indicators. Provides the vocabulary (*clusterability*) and the formal tests. |
| `vonluxburg2010stability` | von Luxburg 2010, arXiv 1007.1075 | `[ ]` | **The foundational critique of stability-based K selection — i.e. of our own PS ≥ 0.80 rule.** RQ1-G rediscovered its central warning independently (region B: PS 0.818 on a cut correlating with nothing). Citing it converts an odd finding into a confirmed known failure mode. |
| `kalogeratos2012distdip` | Kalogeratos & Likas 2012 | `[ ]` | The dist-dip multimodality test, via `cornelissen2026contour`. **Candidate addition to Ch.4** — a direct clusterability test we never ran; cheaper than anything in G1 and it answers the question G1 only circled. |

⚠️ **Two of these are not yet read in full** (`chen2023selectiveinference`,
`vonluxburg2010stability`) and both are load-bearing. They carry the same
warning as Tier 5: listed because `protocol.md` now rests on them, and an
unread load-bearing citation is a debt, not an asset.

## Tier 7 — Verifier gaming and evaluator independence (added 2026-08-11)

> **Why this tier exists.** RQ5 rests on two assumptions that had never been
> checked against the literature: that **Verifier-A and Verifier-B are
> independent enough** for their gap to mean something, and — proposed on
> 2026-08-11 — that a **symbolic scorer resists gaming**. The first is weaker
> than decision 16 claimed. The second is false. Both were settled *before*
> anything was written, which is the standing instruction working.
>
> **Source disclosure:** alphaXiv, **not Consensus** (quota exhausted until
> 2026-09-01).

| Key | Source | Read | Defends / forces |
|---|---|---|---|
| `mahmoud2026rubric` | Mahmoud et al. 2026, arXiv 2605.12474 (Scale AI) | `[x]` **full body** | 🔴 **Cited twice, for opposite purposes.** (1) It is decision 16's basis for cross-family evaluation. (2) **It refutes the RQ3 gaming-shield reframing before it was written.** Rule-based rewards *are* hacked: under a strong verifier, rubric judges preferred the checkpoint on **85.8%** of prompts while rubric-free judges preferred the **base** on **78.4%**; gains concentrated in **presence-based** criteria (+1.07 completeness) with losses in conciseness (−2.91), relevance (−1.10), factual correctness (−0.85). Mechanism: *"hacking the rubric, not the verifier."* **Our §3.5 features are presence/count-based and our Reflector names the failing rule to the Writer** — strictly easier to game than their setting. ⬛ Their `self-internalization gap` diagnostic is **not usable here**: it needs a training trajectory, and we never fine-tune (rule 10). |
| `kuai2026entanglement` | Kuai et al. 2026, arXiv 2604.07650 (Texas A&M) | `[x]` **full body** | 🔴 **Amends decision 16.** 18 LLMs × 6 families: entanglement is widespread **intra- and cross-family**, so "different family" does not establish independence. *"Apparent agreement may reflect a consensus of correlated errors rather than independent verification."* Tracks judge over-endorsement (Spearman **0.64**, p<0.001). **Plain correlation fails to detect it** — the signal is in the joint **failure** manifold (BEI, CIG), weighted toward co-failures on easy items. Supplies the dev-slice entanglement audit now pre-registered for RQ5. |

## Tier 8 — Sentence specificity: the construct has prior art (added 2026-08-11)

> **The most consequential thing this tier does is remove an invention.** RQ1's
> construct was treated throughout as something the project defined. It is a
> **named task with a fifteen-year literature**, and one of its papers evaluates
> on **movie reviews**. That changes Ch.2: the construct is *adopted*, not coined.

| Key | Source | Read | Defends / forces |
|---|---|---|---|
| `ko2019specificity` | Ko, Durrett & Li, AAAI 2019 | `[x]` **full body** | 🔴 **The S3.5 feature pool comes from here, replacing the pipeline's presence-based list.** Validated families: normalised punctuation/digits, mean word length, discourse connectives, sentiment-bearing fraction, and — decisively — **min/max/mean IDF**, the one family that cannot be satisfied vacuously. Evaluates on **movie reviews**: Spearman **0.702** vs a **length baseline of 0.581**, which independently reproduces our `length_auc` **0.6764**. ⚠️ Also reframes G-300 attempt 1: their α of 0.68–0.70 needed **9 raters plus exclusion of raters below 0.3**. We had **2** and no exclusion rule — a second cause of α 0.4970 beside scale collapse. |
| `kapur2026length` | Kapur, Hawkins & Kreiss 2026, arXiv 2601.04609 (Stanford/UCLA) | `[x]` **full body** | Independent support for **RQ1-H's length-matched design** — with length held constant, humans reliably prefer the more specific option. 🔴 **Forces the hybrid-weight relocation:** in *human* text longer means more specific; in **machine-generated text the relation is flat or reversed**, so a weight calibrated on real reviews will not transfer to generated ones. Their contrast-set specificity measure is also robust to fabricated detail (rank 17.05 → 30.91) — a **candidate for §5.4's realism test, not yet adopted**. |

**The honest asymmetry, recorded because it is the argument for both rows:**
these papers study policies trained by RL against a reward. **We never train a
generator** (rule 10) — our loop reruns a *prompted* model up to three times.
So the optimisation pressure is far weaker than theirs, and their effect sizes
are an **upper bound** on what our loop could produce, not a prediction. That
cuts both ways: it makes gaming less likely *and* makes a null RQ5 result less
informative. Both halves go in Ch.5.

---

## Tier 9 — Not tuning, and not assuming calibration (added 2026-08-11)

> **Both entries were found by a search run *before* the decision they inform,
> and both changed something.** One fixed a hyperparameter rule; the other
> deleted a sentence from `protocol.md` that had been written from memory the
> previous day. ⚠️ **Index used: alphaXiv, not Consensus** — the Consensus quota
> is exhausted until 1 September 2026. Recorded rather than glossed over,
> because "searched a different index" and "did not search" must not look alike
> in a bibliography.

| Key | Source | Read | Defends / forces |
|---|---|---|---|
| `schneider2025overtuning` | Schneider, Bischl & Feurer, **AutoML 2025** (LMU Munich) | `[x]` **full body** | 🔴 **Fixes Verifier-B's learning rate at the spec default, unselected** (protocol.md §S3.3 decision 1). Reanalysis of seven HPO benchmark suites: in **~10% of runs the validation-optimal configuration generalises *worse* than the default**, and their mixed models name the aggravating conditions as **small data, holdout rather than CV, binary classification, accuracy-type metric** — all four describe Verifier-B (888 rows, 82-row holdout, 2 classes, macro-F1). Their own recommendation is repeated CV; **not tuning at all was available and is strictly stronger**, so it was taken. Also the standing citation for why the 82-row dev slice is a *reporting* surface and never a selection surface. |
| `zhang2026tabpfn` | Zhang et al. 2026, arXiv 2607.11007 (USC) | `[x]` **full body** | 🔴 **Withdraws the "natively calibrated" defence of Verifier-A and makes §3.4 temperature scaling mandatory for it.** Across **22,820 episodes**, 14 datasets and 11 encoders, a logistic head on a frozen encoder takes the **best mean rank on accuracy** and ranks **below kNN and every in-context head on both ECE and NLL** (Top-1 ECE **0.069** vs 0.037 / 0.031). Their sentence, which is the one that matters: *"strong accuracy does not inherently guarantee well-calibrated probabilities."* ✅ **What survives:** their practical guidance keeps logistic regression appropriate for *"high dimensions, or near-ceiling tasks"* — ours is 768-d LaBSE at 0.9866 — so **the artifact is confirmed and one sentence of its justification is not.** ⚠️ **Bounded:** their canonical grid is 10-class and the calibration gap narrows at C=2; our task is binary, so the recorded correction is *"the claim had no support"*, not *"Verifier-A is miscalibrated"*. |

**Why this tier is one line longer than it needs to be.** `zhang2026tabpfn` is
the **fourth** entry in CLAUDE.md's table of decisions made without searching
first, and the cheapest to have caught — the claim was one day old and no code
depended on it. The three earlier entries each cost a rebuilt instrument, a
rewritten decision rule, or a withdrawn recommendation. **The table is kept
because the pattern is the argument for the rule, not because the failures are
interesting individually.**

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
