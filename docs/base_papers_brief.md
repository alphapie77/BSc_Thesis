# Base papers — reading brief for the six Tier-1 sources

**Written 2026-08-01 by Claude, for Sabbir to verify against the originals.**

This is a *companion* to `related_work.md`, not a replacement. `related_work.md`
stays the register of record (one entry per paper, BibTeX key must match
`references.bib`). This file is the thing to read on a phone before a
supervision meeting.

---

## ⚠️ Read this box first — it is the honest part

**Sabbir has not read any of these papers. Claude has, to the depths stated
below.** The reading depth is *not* uniform, and every claim in this file is
tagged so you know what to trust:

| Tag | Means |
|---|---|
| 📗 **full text** | The paper body was read; section and table numbers are given and are checkable |
| 📙 **abstract + record** | Only the abstract and the bibliographic record were read. Claims are the authors' own summary of their work — accurate as far as it goes, but **no numbers beyond what the abstract states**, and no view of the method's fine print |

| Paper | Depth | Why that depth |
|---|---|---|
| Huang et al. 2024 | 📗 full text | It is the theoretical anchor and it changed our ablation design |
| Kamoi et al. 2024 | 📙 abstract + record | Survey; the abstract states its three findings numerically |
| Sands et al. 2026 | 📙 abstract + record | Unusually detailed abstract; full text is open access |
| Mixture-of-Personas 2025 | 📙 abstract + record | **Needs full-text reading before the comparison table is built** |
| Self-Correction Illusion 2026 | 📙 abstract + record | **Needs full-text reading — it proposes a free baseline that competes with ours** |
| Cobbe et al. 2021 | 📙 abstract + record | No HTML on arXiv (2021); PDF only |

**Three of these need full-text reading before they can carry weight in Ch.2.**
Marked ⬛ below. An examiner asking "what did they actually do?" about MoP or the
Illusion paper will not be satisfied by an abstract, and neither should you be.

**Everything here is verifiable.** Every paper is open access; links are given.
Downloading the six and checking this file against them is an afternoon, and it
is the afternoon that converts this from *Claude's notes* into *your knowledge*.

---

## 1. Huang et al., ICLR 2024 📗

**Large Language Models Cannot Self-Correct Reasoning Yet**
Huang, Chen, Mishra, Zheng, Yu, Song, Zhou · [arXiv:2310.01798](https://arxiv.org/abs/2310.01798) (v2) · CC BY 4.0
**Key:** `huang2024selfcorrect` · **Role:** theoretical anchor for RQ2

### The claim, exactly

They define **intrinsic self-correction** (§2) as self-correction *"without any
external or human feedback"*, and say all unqualified uses of "self-correction"
in the paper mean that. Finding: LLMs *"struggle to self-correct their responses
without external feedback, and at times, their performance even degrades."*

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

Every intrinsic number is at or below its baseline. Only the oracle row improves,
and §3.2 argues oracle results *"can only be regarded as indicative of an
oracle's performance"* — if you hold the ground truth, why run the model.

### Why it degrades (§3.3)

GPT-3.5 keeps its first answer 74.7% of the time on GSM8K; among the rest it is
**more likely to change a correct answer to an incorrect one** than the reverse.
Their diagnosis: *"LLMs cannot properly judge the correctness of their
reasoning."* **That is a claim about the judge, not the generator** — which is
precisely why we externalise the judge.

### The boundary — what it does NOT cover

Reasoning benchmarks only. **No generation task, no persona control, no
low-resource language.** External feedback is explicitly endorsed, not refuted.
The title's *"Yet"* is load-bearing.

### It endorses our approach by name (§6)

*"when valid external feedback is available, it is beneficial to leverage it
properly"* — citing **Cobbe et al. 2021**, Lightman et al. 2023, Wang et al.
2023b for *"train a verifier or a critique model … to verify or refine LLM
outputs"*. **This paper is not an obstacle we route around; it names our
direction as the promising one.**

### 🔧 Two results that bite on our §5.1 ablation

- **§4:** multi-agent debate at 9 calls scores **83.0**; self-consistency at the
  same 9 calls scores **88.2**. What looks like "critique" is selection.
- **§5:** a reported Self-Refine gain vanished once the requirement was moved
  into the *initial* prompt — standard **81.8** vs self-corrected **75.1**.
- **§6** asks for comparison against baselines of **comparable inference cost**.

→ **Open decisions 9 and 10.** Our rows 1–3 are single-call, rows 4–8 loop, and
we have no self-consistency baseline and no cost column.

---

## 2. Kamoi et al., TACL 2024 📙

**When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of
Self-Correction of LLMs**
Kamoi, Zhang, Zhang, Han, Zhang · TACL 12: 1417–1440 · [arXiv:2406.01297](https://arxiv.org/abs/2406.01297) (v3) · CC BY 4.0
**Key:** `kamoi2024when` · **Role:** supplies our framing vocabulary

### The three findings, in their own words

1. *"no prior work demonstrates successful self-correction with feedback from
   prompted LLMs, except for studies in tasks that are exceptionally suited for
   self-correction"*
2. **"self-correction works well in tasks that can use reliable external
   feedback"**
3. *"large-scale fine-tuning enables self-correction"*

### Why finding (2) is the sentence our thesis rests on

Huang et al. show intrinsic correction failing. Kamoi et al. survey the whole
literature and conclude that correction **works when the feedback is reliable
and external**. Our trained verifier is exactly that. Together the two papers
give us: *the problem is the judge* (Huang) and *externalising the judge is the
known fix* (Kamoi).

Finding (1) also kills a cheaper alternative for us: an LLM prompted to critique
— our ablation row 7 — is the thing they say has **never** been shown to work.
That makes row 7 the right headline baseline and predicts it will lose.

### Also useful: they provide a checklist

They report that prior work *"involve[s] impractical frameworks or unfair
evaluations that over-evaluate self-correction"* and offer *"a checklist for
designing appropriate experiments."*

⬛ **Get that checklist and run §5.1 against it before S6.** It is the closest
thing to a referee's rubric for exactly our experiment, and it is free.

---

## 3. Sands et al., NCAA 2026 📙

**An evaluation of LLMs for generating movie reviews: GPT-4o, Gemini-2.0 and
DeepSeek-V3**
Brendan Sands, Yining Wang, Chenhao Xu, Yuxuan Zhou, Lai Wei, … Rohitash Chandra
Neural Computing and Applications **38**, article 556 (2026) · published 27 June 2026
[doi:10.1007/s00521-026-12247-0](https://doi.org/10.1007/s00521-026-12247-0) · **Open access**
**Key:** `sands2026` · **Role:** closest work to our S6; **their gaps are our motivation**

### What they did

Generated movie reviews with **GPT-4o, DeepSeek-V3, Gemini-2.0**, using **movie
subtitles and screenplays** as input, and compared the output to **IMDb user
reviews** on vocabulary, sentiment polarity, similarity and thematic
consistency. Then a **survey-based human study** where participants tried to
tell LLM reviews from IMDb reviews.

### What they found

- LLMs produce *"syntactically fluent and structurally complete"* reviews.
- **But: *"a noticeable gap in emotional richness and stylistic coherence"***
  against real IMDb reviews.
- Humans found LLM reviews *"generally difficult to distinguish"* from real ones.
- DeepSeek-V3 most balanced; **GPT-4o overemphasised positive emotions**;
  Gemini-2.0 caught negative emotion better but with *"excessive emotional
  intensity."*

### Why this is the most useful paper in the list for us

Their stated gap — **emotional richness and stylistic coherence** — is what a
verifier-in-the-loop is *for*. And their per-model bias finding (GPT-4o skews
positive) is a direct warning for our generator choice and for our persona-mix
sanity check.

**Four gaps that are our contribution:**

| They | We |
|---|---|
| English, IMDb | **Bangla**, low-resource |
| No persona conditioning | 3 personas, verifier-enforced |
| No verifier, no loop | trained verifier in a generate–verify–refine loop |
| Input = subtitles + screenplays | input = **plot synopses only** (pre-release realistic) |

That last row matters and is easy to miss: subtitles and screenplays are only
available **after** a film is made. Our setting is *pre-release*, so a synopsis
is all there is. It makes our task harder and our framing more honest.

---

## 4. Mixture-of-Personas (MoP), 2025 📙 ⬛

**Mixture-of-Personas Language Models for Population Simulation**
Bui, Nguyen, Kumar, Theodore, Qiu, Nguyen, Ying · [arXiv:2504.05019](https://arxiv.org/abs/2504.05019) (v1, 7 Apr 2025) · CC BY 4.0
**Key:** `mop2025` · **Role:** **closest competitor**; borrow their formalism

### What it is

A *probabilistic prompting* method to align LLM output with a target
population. **A contextual mixture model**: each component is an LM agent
characterised by **a persona and an exemplar** representing a subpopulation.
Persona and exemplar are drawn according to **learned mixing weights**. No
finetuning; transferable across base models. They report beating competing
methods on *"alignment and diversity metrics."*

### What we take from it

The formalism — population **P**, **K** groups, persona **g_k** — and the idea
that a persona should come **with an exemplar**, not as a bare label. Our RAG
retrieval over R1 is arguably the same move; saying so explicitly would
strengthen Ch.2.

### ⚠️ Two things the pipeline asserts that the record does NOT confirm

1. **The pipeline calls it "Findings of ACL 2025".** The arXiv record shows
   **no journal reference and no venue comment** — v1 only, submitted 7 Apr
   2025. Cite it as arXiv unless a published version is found. **Do not put
   "Findings of ACL 2025" in the bibliography on our say-so.**
2. **The pipeline says it "uses IMDB/SST-2".** The abstract says only *"synthetic
   data generation"* and names no dataset. Plausible, unverified.

### ⬛ Read the full text before the comparison table

The entry in `related_work.md` asks the key question — **how do they validate
their personas?** If they do not human-validate, that gap is our contribution ①,
and it is the single most important thing we need from this paper. **The
abstract does not answer it.** Also needed: their K-selection method, and
whether they report MAUVE (our §C mandates `mauve-text` specifically so the
numbers are comparable).

---

## 5. The Self-Correction Illusion, 2026 📙 ⬛

**The Self-Correction Illusion: LLMs Correct Others but Not Themselves**
Kuan-Yen Chen, Fang-Yi Su, Jung-Hsien Chiang · [arXiv:2606.05976](https://arxiv.org/abs/2606.05976) (v1, 4 Jun 2026)
**Key:** `selfcorrectionillusion2026` · **Role:** why external-role feedback works

### The claim, and it is a striking one

They hold the erroneous claim **byte-identical** across conditions (SHA-256
verified) and vary only the **chat-template role** carrying it: the agent's own
`<thought>`, a `user` message, a `tool` response, or a `system <memory>` block.

**Relabelling the claim from `<thought>` to an external role lifts the
explicit-correction rate by 23 to 93 percentage points**, across 13
model–domain cells, seven model families, three domains, n=30 paired tasks per
cell; 10 of 13 cells at p<0.001.

Their conclusion: *"The failure to self-correct is not a cognitive deficit; it
is a chat-template artifact."* They then build a **prompt-structure-only
intervention — no training, no model modification** — whose best role label is
domain-dependent (`<memory>` for math, plain `user` for logical deduction).

### 🔴 Why this is the most dangerous paper in the list for us

It supports our framing — *external* presentation of feedback is what unlocks
correction, and our verifier is external — **but it also proposes a free
competitor.** If simply relabelling self-critique as coming from an external
role captures most of the benefit, then a trained verifier has to justify its
cost against a prompt-formatting trick.

**That is not a reason to hide it. It is a reason to run it as a baseline.**

### ⬛ Proposed new ablation condition (Sabbir's call)

> **Row 7b — self-critique presented under an external role label.** Identical
> critique text to row 7, wrapped as a `user`/`tool` message rather than the
> model's own turn.

- If **7b ≈ 6**, our trained verifier is not earning its keep, and *that is a
  publishable negative result* we would far rather find ourselves.
- If **6 > 7b**, our contribution is much stronger than row 7 alone could show:
  it survives the cheapest known alternative.

Logged as **open decision 11**. Note this is a 2026 paper on a 2026 thesis —
being this close to the frontier is an asset, provided we engage with it rather
than cite it in passing.

---

## 6. Cobbe et al., 2021 📙

**Training Verifiers to Solve Math Word Problems**
Cobbe, Kosaraju, Bavarian, Chen, Jun, Kaiser, Plappert, Tworek, Hilton, Nakano,
Hesse, Schulman · [arXiv:2110.14168](https://arxiv.org/abs/2110.14168) (v2)
**Key:** `cobbe2021verifiers` · **Role:** origin of the trained-verifier line

### What it established

Introduced **GSM8K** (8.5K grade-school math word problems) and proposed
**training verifiers to judge the correctness of model completions**. At test
time: generate many candidate solutions, **select the one the verifier ranks
highest**. They report that verification *"significantly improves performance"*
and — the part that matters for us — *"provide strong empirical evidence that
verification scales more effectively with increased data than a finetuning
baseline."*

### Why it is load-bearing rather than background

Huang et al. §6 point at **this paper** as the alternative to intrinsic
self-correction. Our whole design is a descendant of it. The scaling claim also
pre-empts an obvious objection to us: *"why not just fine-tune the generator?"*
— Cobbe et al. answer that verification uses data better.

### One difference to state honestly

**Their verifier ranks; ours gates.** They generate N candidates and pick the
best (best-of-N). We generate, verify against a threshold, and **refine in a
loop**. Different mechanisms with a shared ancestor — and best-of-N is exactly
the cost-matched baseline Huang et al. §6 demands (open decision 9). Cobbe et
al. is where that baseline comes from.

---

## What reading these six actually changed

Not one of these papers left our design untouched. That is the argument for
doing this before S6 rather than while writing Ch.2:

| Source | Change |
|---|---|
| Huang §4/§5/§6 | Open decisions **9** (cost-matched + self-consistency baseline) and **10** (prompt parity) |
| Illusion 2026 | Open decision **11** (row 7b: external-role self-critique) |
| Kamoi | Their experiment-design checklist should be run against §5.1 before S6 |
| Sands | Their stated gap — emotional richness, stylistic coherence — is our target; GPT-4o's positivity skew is a generator warning |
| Cobbe | Best-of-N is the ancestor of decision 9's baseline |
| MoP | Two pipeline claims about it are **unverified** (venue, datasets) |

**Three ablation conditions may be missing from a pre-registered table.**
Finding that now costs a config edit; finding it after 2,160 generations costs
the experiment.

---

## Your afternoon, if you want this to be yours

1. Download all six. All open access; links above.
2. Check this file against them — especially the numbers in §1, which are the
   ones we would quote.
3. Read **full text** for MoP (does it human-validate its personas?) and the
   **Illusion** paper (how big is the free intervention, really?). Those two
   ⬛ marks are where an examiner will push hardest, and where our own design
   decisions are still open.
4. Tell me what you find. If I have overstated anything, it gets corrected in
   `related_work.md` with the correction visible, not silently.

> One thing I nearly got wrong and want on the record: I first read Sands et al.
> as "Chandra et al." because the bibliographic metadata lists the corresponding
> author last, and I was one keystroke from "correcting" a citation that was
> already right. The author list on the article page settled it. Check me the
> same way.
