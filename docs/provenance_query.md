# Provenance query — where did rows 2000–5000 come from?

**Raised:** 2026-07-30 · **Status:** 🔴 **OPEN — blocks the RQ1 claim**
**Evidence:** `results/s2c_region_split.md` (exploratory)
**Addressee:** the person who collected the dataset

---

> ## ⚠️ Round 1 asked the wrong question — read this first
>
> This document originally asked about the **class-2 (neutral)** rows. The
> collector answered on 2026-07-30 that they were **collected the same way as
> the others**.
>
> That answer prompted a look at the raw `.xlsx` itself, and the question turns
> out to have been mis-aimed. The pattern does not follow the *label*, it
> follows **position in the file**:
>
> | rows | label | দাঁড়ি | first-person | word types / 1k |
> |---|---|---|---|---|
> | 499–896 | **0** | 32.4% | 9.0% | 399 |
> | 3665–4330 | **0** | **99.8%** | **0.0%** | **240** |
>
> **Both blocks are negative reviews.** They do not look like the same kind of
> writing. So the neutral class was never the issue — it just happens to sit
> entirely inside the second half of the file.
>
> Aggregated: **rows 0–1998** (1,999 rows: 38.7% দাঁড়ি, 13.5% first-person, 255
> types/1k) versus **rows 1999–4999** (3,001 rows: **99.2%, 0.8%, 128**). The
> change is a step over about 50 rows, not a gradual drift. That is **60% of the
> corpus**.
>
> The revised question is in §"The questions (round 2)" below. The original
> round-1 material is kept underneath it, unedited, because a superseded
> question that disappears is one nobody can audit.

---

## Why this is being asked

This is **not** an accusation that anything was done wrong. Balancing a corpus
by writing or generating neutral examples is a normal and often sensible thing
to do — it only becomes a problem when it is not *recorded*, because downstream
analysis then cannot tell it apart from organic data.

The measurements below cannot distinguish a legitimate collection choice from an
undocumented one. Only the collector can. Whatever the answer is, it gets
written into `docs/dataset_card.md` and reported in the thesis — including "yes,
those were written to fill the quota", which is a perfectly reportable fact.

## What was measured

`Sentiment == 2` (n = 1,618 after cleaning; 1,670 raw) differs from classes 0
and 1 on features that **cannot encode an opinion about a film** — punctuation,
length, pronouns. If class 2 were the same kind of text with a different
opinion, these would match. They do not:

| Feature | class 0 | class 1 | **class 2** | Expected in class 2 if same population | Observed |
|---|---|---|---|---|---|
| contains দাঁড়ি (।) | 58.0% | 66.0% | **100.0%** | 1,005 of 1,618 | **1,618** |
| first-person pronoun (আমি/আমার/…) | — | — | **0.0%** | 149 | **0** |
| exclamation mark | — | — | **0.0%** | 38 | **0** |
| comma run (`,,,`) | — | — | **0.0%** | 33 | **0** |
| unique word types per 12,000 tokens | 3,577 | 3,303 | **1,772** | ~3,400 | **1,772** |

Four separate structural absolutes, plus a vocabulary about **half the size** at
identical text length. Under the assumption that class 2 was drawn from the same
population as the other two, the দাঁড়ি result alone has probability ≈ 10⁻³³⁴.

Reading a sample of class 2 rows, none of the eight drawn mentioned a film, an
actor, or a personal experience. Classes 0 and 1 routinely do — শাকিব, শাবনূর,
বুবলি, "কেউ দেখবেন না", "পুরাই লস প্রজেক্ট".

## Why it matters for the thesis

The S2 clustering separates class 2 from the rest almost perfectly — **12 of
1,572 class-2 items** fall in cluster 0, against 1,802 items from the other two
classes. Refolded as *cluster 0 vs rest* × *class 2 vs rest*, the association
(φ = 0.565) is **stronger than the clustering's association with sentiment as a
whole** (V = 0.410).

So the dominant structure the encoder found may be **how the text was produced**,
not who the audience is. `docs/protocol.md` RQ1 Band 3 pre-registered exactly
this confound; `docs/STATUS.md` recorded it as *untestable in principle* because
venue was never retained. That was wrong in one specific way — venue was not
retained, but **writing style survives in the text**, and it is measurable.

**Until this is answered, no persona claim resting on the three-class structure
can be defended.**

---

## The questions (round 2) — ask these

Position in the file is what matters, so the questions are about **blocks of
rows**, not about labels.

1. **Was the dataset built in one sitting, or assembled from more than one
   batch?** The label column runs in ten long blocks (499 rows of one label,
   then 398 of another, and so on), which is what pasting batches together
   looks like.

2. **Do you remember adding a second batch of roughly 3,000 rows**, after an
   initial batch of roughly 2,000? The writing changes character sharply at
   about row 2,000.

3. **For that second batch — was any of it written or generated rather than
   copied from comments?** Not just the neutral ones: the negative and positive
   rows in that region look the same way. A tool, a template, a paraphraser, or
   writing them by hand would all produce this.

4. **Or did the second batch come from a different kind of source** — a review
   blog, a news site, an existing dataset, a friend's file?

5. **Did you build this dataset yourself, or receive it (in whole or in part)
   from someone else** before publishing to Mendeley? If part of it came from
   elsewhere, that alone explains everything above and is entirely normal.

6. **Is any file, sheet, chat, or download folder left from that period?** Even
   a partial record beats none.

Everything in round 1 below still applies, in particular that **no answer here
is a problem** — only an unrecorded one is.

---

## The questions (round 1 — superseded, kept for the record)

Please answer as precisely as memory allows, and say plainly where you are
unsure — "I don't remember" is a usable answer and a guess is not.

1. **Were the class-2 (neutral) reviews collected the same way as classes 0 and
   1** — scrolling Bangla movie-related Facebook groups and YouTube channels and
   copying real user comments?

2. **If not, how were they produced?** Specifically:
   - written by hand (by you or by someone else), to fill the neutral quota?
   - generated with a tool (ChatGPT, Gemini, a template, a paraphraser)?
   - taken from a different kind of source — a blog, a review site, a news
     article, an existing dataset?

3. **Was the neutral class harder to fill than the other two?** Neutral comments
   are rare on social media; if the quota was hard to reach, that would explain
   the pattern and is worth stating in the thesis on its own.

4. **Were classes 0 and 1 fully organic**, or were some of those written or
   generated too? (Class 0 and 1 contain some short generic lines like
   "সিনেমার ভিজ্যুয়াল এস্থেটিকস খুব সাধারণ।" that read differently from the
   rest.)

5. **Is any list, spreadsheet, chat log, or browser history left** that would
   show which rows came from where — even partially, even for a subset? A
   partial record is far better than none.

6. **Roughly when was each class collected?** If the neutral rows were added in
   one later session, that alone would corroborate the pattern.

7. **Was the dataset published to Mendeley by you**, or obtained from someone
   else and re-published? If obtained, from whom, and did they document
   collection?

---

## What happens with each answer

| Answer | Consequence |
|---|---|
| Organic, same method as 0 and 1 | The measurements contradict this and must be reported as an **unexplained** data-quality finding, with the absent collection log as the limiting factor. |
| Written by hand / generated | Recorded as a **verified fact** in the dataset card. RQ1 must be re-scoped — most likely to the two organic classes, or with the synthetic/organic split as the object of study rather than a nuisance. |
| Different venue | Same consequence: the clusters track provenance. The confound becomes reportable and testable instead of hypothetical. |
| Don't remember | The probe result stands as the best available evidence and is reported as exploratory, with the risk stated openly in the limitations. |

**Every one of these is publishable.** The one thing that is not survivable is
presenting a persona claim while this question sits unanswered in the file.
