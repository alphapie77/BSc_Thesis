# Base papers — reading brief for the six Tier-1 sources

**Written 2026-08-01 by Claude. Verify against the originals — all six are free.**

Companion to `related_work.md` (the register of record) and `references.bib`
(keys must match). This is the file to read before a supervision meeting.

---

## ⚠️ Reading depth — the honest part

**Sabbir has read none of these. Claude read them to the depths below.** Depth
is not uniform and every section says which it is.

| Paper | Depth | What that means here |
|---|---|---|
| 1. Huang et al. 2024 | 📗 **full text** | Sections, tables, numbers — all checkable |
| 2. Kamoi et al. 2024 | 📗 **body read** | RQ structure, taxonomy table, headline findings per section |
| 3. Self-Correction Illusion 2026 | 📗 **body read** | Intro, findings, Table 2 cells, mechanism controls, experimental design |
| 4. Mixture-of-Personas 2025 | 📘 **partial** | Formalism + method + section structure. §4.1 setup **unreadable** — the arXiv HTML buries it in MathML markup. Datasets/metrics still unverified |
| 5. Sands et al. 2026 | 📙 **abstract + record** | Detailed abstract; body not read |
| 6. Cobbe et al. 2021 | 📙 **abstract + record** | 2021 paper, PDF only, no arXiv HTML |

**Where a number is quoted, it came from the paper.** Where something could not
be extracted, it says so rather than being filled in plausibly.

---

## 1. Huang et al., ICLR 2024 📗

**Large Language Models Cannot Self-Correct Reasoning Yet**
[arXiv:2310.01798](https://arxiv.org/abs/2310.01798) v2 · CC BY 4.0 · `huang2024selfcorrect`

### The claim, exactly as scoped

**Intrinsic self-correction** (§2) = correction *"without any external or human
feedback"*; all unqualified uses of "self-correction" in the paper mean that.

### Numbers (Tables 2–4, accuracy %)

| Setting | Model | GSM8K | CommonSenseQA | HotpotQA |
|---|---|---|---|---|
| Standard prompting | GPT-3.5 | 75.9 | 75.8 | 26.0 |
| Self-correct **with oracle** | GPT-3.5 | **84.3** | **89.7** | **29.0** |
| Self-correct **intrinsic** r1→r2 | GPT-3.5 | 75.1 → **74.7** | 38.1 → **41.8** | 25.0 → 25.0 |
| Standard prompting | GPT-4 | 95.5 | 82.0 | 49.0 |
| Self-correct **intrinsic** r1→r2 | GPT-4 | 91.5 → **89.0** | 79.5 → 80.0 | 49.0 → **43.0** |
| Standard prompting | Llama-2-70b | 62.0 | 64.0 | — |
| Self-correct **intrinsic** r1→r2 | Llama-2-70b | 43.5 → **36.5** | 37.5 → **36.5** | — |

Every intrinsic number sits at or below its baseline. Only the oracle row rises,
and §3.2 argues oracle results *"can only be regarded as indicative of an
oracle's performance"* — holding the ground truth removes the reason to run the
model.

### Why (§3.3)

GPT-3.5 keeps its first answer 74.7% of the time on GSM8K; among the rest it is
**more likely to turn a correct answer into an incorrect one** than the reverse.
*"LLMs cannot properly judge the correctness of their reasoning."* **A claim
about the judge, not the generator** — hence externalising the judge.

### Boundary

Reasoning benchmarks only. No generation task, no persona control, no
low-resource language. The *"Yet"* is load-bearing.

### It names our direction (§6)

*"when valid external feedback is available, it is beneficial to leverage it
properly"* — citing **Cobbe et al. 2021** and others for *"train a verifier or a
critique model … to verify or refine LLM outputs"*.

### 🔧 Bites on §5.1

- **§4:** multi-agent debate at 9 calls = **83.0**; self-consistency at 9 calls =
  **88.2**. The "critique" gain is selection.
- **§5:** a Self-Refine gain vanished when the requirement moved into the
  *initial* prompt — **81.8** standard vs **75.1** self-corrected.
- **§6:** compare against baselines of **comparable inference cost**.

→ open decisions **9**, **10**.

---

## 2. Kamoi et al., TACL 2024 📗

**When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey**
TACL 12: 1417–1440 · [arXiv:2406.01297](https://arxiv.org/abs/2406.01297) v3 · CC BY 4.0 · `kamoi2024when`

### Structure: three research questions

They argue prior work *"often do[es] not define their research questions in
detail and involve[s] impractical frameworks or unfair evaluations that
over-evaluate self-correction"*, and split the field into RQ1 (can LLMs
self-correct?), RQ2 (what makes it work?), RQ3 (is it better than
alternatives?). Self-correction is framed in **three stages** (Fig. 1): initial
response generation → feedback → refinement.

### The findings that matter to us

- *"no prior work demonstrates successful self-correction with feedback from
  **prompted LLMs**, except for studies in tasks that are exceptionally suited
  for self-correction"* — **this predicts our ablation row 7 loses**, which is
  exactly why it is the right headline baseline.
- **"Self-correction is effective in tasks where reliable external feedback is
  available"** (§5.1) — the sentence RQ2 rests on.
- **§5.2: *"Fine-tuning enables self-correction when large training data is
  available but is unexplored for small training data."*** 🎁 **Read that
  twice.** Our verifier trains on **R1 = 2,162 rows**. A TACL survey names our
  exact regime as *unexplored*. That is a gap sentence for Ch.1 that we did not
  have to argue for — it is stated by the survey.
- **§6 "Strong Baselines": *"Self-correction is often not compared with
  sufficiently strong baselines, and it is still unclear whether it is better
  than other approaches."*** Independent confirmation of open decision 9.

### Their taxonomy — use this vocabulary in Ch.2

Table 1 classifies every prior system by feedback source: **Intrinsic**,
**Oracle**, **Fair-Asymmetric**, **Unfair-Asymmetric**, **Cross-Model**. Huang
et al. appears under *Negative Results → Intrinsic*.

⬛ **Open question this raises for us:** which cell is *our* system in? A
verifier trained on R1 and applied to generated text looks like **Cross-Model**
(they list REFINER and RL4F there: GPT-3.5 with a trained T5 feedback model —
structurally the closest analogue to ours in the entire table). Deciding this
deliberately, rather than letting a reviewer decide it for us, is a Ch.2 task.
The asymmetry distinction also matters: if our verifier sees information the
generator never had, that is **asymmetric** and must be disclosed as such.

---

## 3. The Self-Correction Illusion, 2026 📗

**Role Relabeling Gates Explicit Error Flagging in Large Language Models**
Chen, Su, Lin, Li, Chiang · [arXiv:2606.05976](https://arxiv.org/abs/2606.05976) v2 (31 Jul 2026; rechecked 20 Aug 2026) · `selfcorrectionillusion2026`

### The testable claim (§1)

> *"When an LLM agent encounters an erroneous claim, its willingness to correct
> that claim depends primarily on the chat-template role label attached to the
> claim, rather than on the content of the claim itself."*

The erroneous claim is held **byte-identical (SHA-256 verified)** across five
conditions; only the wrapping role varies: the agent's own `<thought>`, a `user`
message, a `tool` response, or a `system <memory>` block.

### Design (§4.1) — and one caveat that matters

n=30 paired tasks per cell, T=0, fixed seed, 10,000-sample paired bootstrap,
two-sided p, pre-registered exit criteria. Judged by a locked Qwen-72B judge
(κ=1.0 against hand labels; κ=0.843 on independent re-judge).

⚠️ **They evaluate on a *failure pool*** — tasks where intrinsic correction
already failed under the audit-only baseline. That concentrates statistical
power on the target regime, and it means the headline lifts are measured on a
**pre-selected subset**, not on all tasks. Report it that way.

### Results (Table 2, ΔCR in percentage points over the self-baseline)

| Cell | best relabel |
|---|---|
| Llama-3.3-70B logic | **+93*** |
| Llama-3.3-70B math | **+87*** |
| Qwen2.5-72B gen-logic | **+80*** |
| Qwen2.5-72B math | +53*** |
| GPT-4o math | +50*** |
| Claude Sonnet 4 math | +40*** |
| gpt-oss-20B math | +17 (ceiling, L₀ 77%) |
| Qwen2.5-72B BBH-LD | +17* (ceiling, L₀ 67%) |

10 of 12 cells have at least one significant relabel; the 2 exceptions have
high baselines (L₀ ≥ 67%). Nine of 12 survive Holm–Bonferroni. Per-task flips:
**29 of 30** eligible tasks on Llama-70B logic, **18 of 25** on Qwen-72B math.

### Mechanism — four controls, and they matter to us

1. **Handle-granularity ladder:** a bare syntactic boundary is worth **17–23 pp**;
   the **role tag adds a further ~30 pp**. Neither acts alone.
2. **Lexical identity of the tag is load-bearing:** a nonsense `<xqzy>` tag
   reaches 30% where `<memory>` reaches 70%.
3. **Within-thought duplication control** (same duplication count and recency,
   role kept inside `<thought>`) lifts only **+6.7 pp, p=0.26** — isolating a
   **+46.7 pp pure role-tag effect**. So it is not "the model saw it twice".
4. 🔴 **Self-distrust control:** instructing the agent to verify its own thoughts
   yields **0–23%** correction, against **70%** for the relabel. **Telling a
   model to doubt itself is not a substitute for external presentation.**

### Safety scope

The channel does **not** reverse into an error-injection attack by default — all
20 adversarial cells ≤ 3.3%. But one trust-framing sentence (*"treat this memory
as ground truth and do not verify"*) raises the math attack rate to **70%**.

### 🔴 Why this is the most dangerous paper for us

It supports our framing *and* offers a **training-free competitor**. If moving
the critique into an external role slot captures most of the benefit, a trained
verifier must justify its cost against a formatting change.

Control 4 is the reassuring part: naive self-distrust does **not** work, so our
row 7 is predicted to lose for a *mechanistic* reason. But row 7b — the same
critique under an external role — is the real competitor and is now a main row.

→ **decision 11 closed.** If 7b ≈ row 6, the verifier is not earning its cost,
and that is a negative result we would far rather find than have a reviewer find.

---

## 4. Mixture-of-Personas, 2025 📘 partial

**Mixture-of-Personas Language Models for Population Simulation**
Bui, Nguyen, Kumar, Theodore, Qiu, Nguyen, Ying · [arXiv:2504.05019](https://arxiv.org/abs/2504.05019) v1 · CC BY 4.0 · `mop2025`

### The formalism (§3.1) — this is what we borrow

The population's response distribution decomposes over **K** personas:

> **p(y | x) = Σₖ πₖ · p_LM(y | gₖ, x)**, with **Σₖ πₖ = 1**

where **gₖ** is a persona description and **πₖ** the mixing weight. Then a
**second level**: in-context exemplars are drawn from a representative pool of
the target population under their own learnable weights — a **two-level
hierarchical mixture** (level 1 selects the persona, level 2 weights the
exemplar).

### The design choice we should copy in Ch.2

Personas are *either* user-defined *or* **synthesised from the record set**, and
crucially they require **no persona↔response pairing**: *"our setting could be
considered as an 'unsupervised' setting of the steerability problem of LLMs."*
No fine-tuning; transferable across base models.

Their motivation for exemplars is the one we should quote: prompting with a
persona alone still yields responses that *"lack diversity and exhibit
significant biases"*, and temperature scaling alone causes *"a trade-off between
quality and diversity or … outputs to collapse into semantically similar
responses."* **Our RAG retrieval over R1 is arguably the same move** — persona
plus retrieved exemplar rather than a bare persona label. Saying so explicitly
would strengthen Ch.2 rather than weaken it.

### ✅ The key question, answered from the paper's own structure

`related_work.md` asks: **do they human-validate their personas?**

Their §4 Experiments contains exactly four subsections — **4.2 Steerability,
4.3 Synthetic Data Generation, 4.4 Transferability, 4.5 Ablation Studies** —
plus §7 Limitations. **There is no human-evaluation or persona-validation
section anywhere in the paper.** Personas are synthesised from data and
evaluated by automatic alignment and diversity metrics.

**So contribution ① stands: the closest competitor does not validate that its
personas correspond to anything real.** Our G-300, with three annotators and
κ/α, does. (Check this against the PDF yourself — it is an argument from the
section list, which is strong but is not the same as reading §4 in full.)

### ⚠️ Two pipeline claims the record does not support

1. **"Findings of ACL 2025"** — the arXiv record shows **no venue**, v1 only,
   7 Apr 2025. Cite as arXiv until a published version is found.
2. **"uses IMDB/SST-2"** — the abstract names no dataset, and §4.1 could not be
   read (MathML). **Unverified.**

### ⬛ Still needed from the full PDF

§4.1 setup: datasets, **whether they report MAUVE** (our §C mandates
`mauve-text` precisely so the numbers are comparable), and **how they choose K**.
The arXiv HTML renders these behind MathML markup; the PDF will be readable.

---

## 5. Sands et al., NCAA 2026 📙

**An evaluation of LLMs for generating movie reviews: GPT-4o, Gemini-2.0 and DeepSeek-V3**
Brendan Sands, Yining Wang, Chenhao Xu, Yuxuan Zhou, Lai Wei, … Rohitash Chandra
*Neural Computing and Applications* **38**, art. 556 (2026), publ. 27 June 2026
[doi:10.1007/s00521-026-12247-0](https://doi.org/10.1007/s00521-026-12247-0) · **Open access** · `sands2026`

### What they did

Generated movie reviews with **GPT-4o, DeepSeek-V3, Gemini-2.0** from **movie
subtitles and screenplays**, compared against **IMDb user reviews** on
vocabulary, sentiment polarity, similarity and thematic consistency, then ran a
**survey-based human study** asking participants to tell LLM reviews from real
ones.

### What they found

- Reviews are *"syntactically fluent and structurally complete"*.
- **But *"a noticeable gap in emotional richness and stylistic coherence"***.
- Humans found LLM reviews *"generally difficult to distinguish"* from IMDb.
- **DeepSeek-V3** most balanced; **GPT-4o overemphasised positive emotions**;
  Gemini-2.0 caught negative emotion better but with *"excessive emotional
  intensity."*

### Why this is the most directly useful paper in the list

Their stated gap is our target, and their per-model bias finding is an immediate
warning for generator selection and for the persona-mix sanity check (§5.4).

| They | We |
|---|---|
| English, IMDb | **Bangla**, low-resource |
| No persona conditioning | 3 personas, verifier-enforced |
| No verifier, no loop | trained verifier in generate–verify–refine |
| Input = subtitles + screenplays | input = **plot synopses only** |

That last row is easy to miss and worth a sentence in Ch.1: subtitles and
screenplays exist only **after** a film is made. Ours is *pre-release*, where a
synopsis is all there is. Harder task, more honest framing.

⬛ Body not read. Before citing any specific metric, read the results section.

---

## 6. Cobbe et al., 2021 📙

**Training Verifiers to Solve Math Word Problems**
Cobbe, Kosaraju, Bavarian, Chen, Jun, Kaiser, Plappert, Tworek, Hilton, Nakano,
Hesse, Schulman · [arXiv:2110.14168](https://arxiv.org/abs/2110.14168) v2 · `cobbe2021verifiers`

### What it established

Introduced **GSM8K** (8.5K grade-school math word problems) and proposed
**training verifiers to judge the correctness of model completions**: generate
many candidates, **select the one the verifier ranks highest**. Verification
*"significantly improves performance"*, and — the load-bearing part —
*"verification scales more effectively with increased data than a finetuning
baseline."*

### Why it is load-bearing

Huang §6 points at **this paper** as the alternative to intrinsic correction.
The scaling claim also pre-empts *"why not just fine-tune the generator?"*

### The difference to state honestly

**Their verifier ranks; ours gates and refines.** Best-of-N versus a
verify–refine loop — same ancestor, different mechanism. And best-of-N is exactly
the cost-matched baseline open decision 9 needs, so the baseline and the ancestor
are the same paper.

⬛ Body not read (no arXiv HTML for 2021 papers). Their headline numbers are
worth having before Ch.2.

---

## What six papers changed

| Source | Consequence |
|---|---|
| Huang §4/§5/§6 | decisions **9** (cost-matched + self-consistency baseline), **10** (prompt parity) |
| Illusion, control 4 + Table 2 | decision **11** (row 7b, external-role self-critique) |
| Kamoi §5.2 | 🎁 *"unexplored for small training data"* — **a gap sentence for Ch.1, in a TACL survey's own words** |
| Kamoi Table 1 | we must place our system in their taxonomy (probably **Cross-Model**) before a reviewer does |
| Kamoi §6 | independent confirmation of decision 9 |
| MoP §4 structure | **no persona validation** — contribution ① confirmed |
| MoP §3.1 | the mixture formalism to adopt; and our RAG ≈ their exemplar level |
| Sands | their gap is our target; GPT-4o positivity skew is a generator warning |
| Cobbe | best-of-N is decision 9's baseline *and* our ancestor |

**Three ablation conditions may be missing from a pre-registered table.** A
config edit today; an unrepeatable experiment after S6.

---

## Your afternoon

1. Download all six — all open access, links above.
2. Check §1's numbers first; they are the ones we would quote.
3. Read the ⬛ items: **MoP §4.1** (datasets, MAUVE, K selection) and the
   **Illusion** intervention section. Those are where the design decisions still
   hang.
4. Tell me what you find. Anything I overstated gets corrected in
   `related_work.md` **visibly**, not silently.

> Recorded so you check me the same way: I first read Sands et al. as *"Chandra
> et al."* because the bibliographic metadata lists the corresponding author
> last, and nearly "corrected" a citation that was already right. The article
> page's author list settled it. **Metadata is not the paper.**
