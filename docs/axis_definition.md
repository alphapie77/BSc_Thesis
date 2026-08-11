# The engagement-specificity axis — operational definition

> **Status: DRAFT by Claude, 2026-08-11. NOT APPROVED.** §4.2 requires the
> Writer's prompt to carry the axis-level operational definition *"verbatim from
> Phase 2"*, and no such text existed as an artifact — only as description
> inside the pipeline spec. This file is that artifact.
>
> 🔴 **Sabbir's approval is required before a single generation is produced.**
> What level 0 and level 1 *mean* is a claim the thesis makes, not a convenience
> for the code. The evidence below is Claude's reading of S2e and RQ1-H; the
> ruling is not Claude's to take.
>
> **Why it is a file and not a string in `writer.py`:** the same block feeds the
> §5.1 row-1 prompt and every loop prompt (decision 5 — parity by construction).
> One source means the two cannot drift; a copy-pasted docstring means they can.

---

## 1. What the evidence supports

**The construct is specificity, and that is measured, not assumed.** RQ1-H Gate B:
two annotators each scored **34/40 = 0.850** against a chance rate of 0.50,
p < 0.0001, on whether the distinction is specificity. Gate A had already shown
the halves are humanly separable at **0.780 / 0.840** against 0.25 chance, with
**length matched to within 2 words** and a length heuristic scoring **0.16 —
below chance**.

**What the two halves look like** (S2e, region A, n = 1,897 — ⚠️ *descriptive
profiling, not hypothesis tests*: this is post-clustering inference on the rows
that defined the cut, per the 2026-08-10 deviation):

| | level 0 (n = 1,143) | level 1 (n = 754) |
|---|---|---|
| Length | **longer** — 13.1 words, 73.9 chars | **shorter** — 8.9 words, 49.2 chars |
| First person | 17.3% | 8.8% |
| Danda | 44.6% | 32.4% |
| **Types at equal 4,000-token budget** | **1,623** | **1,913** |

🔑 **The inversion is the finding.** Level 1 is **33% shorter yet ~18% richer in
word types at an equal token budget.** Longer text with a *smaller* vocabulary
is the signature of formulaic writing; shorter text with a *larger* one is the
signature of saying something particular.

## 2. Three things this definition must NOT say

1. **Not sentiment.** Level 0 is 66% positive and level 1 is 74% negative, so a
   definition mentioning valence would be learned as "level 1 = complain".
   S2f's residual test found valence and verbosity do **not** account for the
   cut (lift **+9.80 pp**) — but it cleared its cutoff by **0.2 pp** and is
   **reported as weak**. Weak evidence is a reason for caution in both
   directions, not a licence in one.
2. **Not length.** `length_auc` **0.6764 → `LENGTH_CONFOUNDED`**. A definition
   that says "write shorter" hands the Writer the confound instead of the
   construct — and RQ1-H's own length heuristic scored **below chance**, so
   length is not even a good proxy for what humans perceived.
3. **Not "persona", "cluster", "audience type".** Retired 2026-08-10. Permitted:
   *axis, gradient, the cut, level*.

## 3. The definition — verbatim block

Everything between the markers is what the prompt renders. Bangla, because the
Writer generates Bangla and a translated definition is a different instrument.
The wording deliberately reuses the G-300 guideline's validated 0–3 language
(levels 0–1 → axis level 0; levels 2–3 → axis level 1), because that instrument
is what RQ1-H validated and inventing fresh wording would discard the validation.

<!-- AXIS_DEFINITION_BEGIN -->
### স্তর ০ — রায়, কিন্তু নির্দিষ্ট কিছু নয়

লেখক ছবিটি ভালো বা খারাপ বলছেন, এবং সেই রায়ের উপরেই থেমে আছেন। আবেগ থাকতে
পারে — বারবার বলা, তীব্র শব্দ, নিজের অনুভূতির কথা — কিন্তু **ছবির কোনো একটি
নির্দিষ্ট অংশের নাম আসে না**। গল্প, অভিনয়, গান, পরিচালনা, কোনো চরিত্র বা কোনো
দৃশ্য — এর কোনোটিই আলাদা করে ধরা হয় না।

এই স্তরের ভাষা প্রায়ই চেনা ছাঁচে চলে: একই ধরনের প্রশংসা বা নিন্দা, যা প্রায়
যেকোনো ছবির সম্পর্কেই লেখা যেত।

### স্তর ১ — নির্দিষ্ট কিছুর কথা

লেখক ছবির **কোনো একটি অংশ ধরে** কথা বলছেন — গল্প, অভিনয়, গান, নায়ক-নায়িকা,
পরিচালনা, শেষটা, একটি দৃশ্য, বা কারও নাম। সেই নির্দিষ্ট জিনিসটির সাথে তাঁর
প্রতিক্রিয়া যুক্ত — কেন এমন মনে হলো, কীসের সাথে তুলনা, কী আশা করেছিলেন, বা
দেখার পর ঠিক কী ঘটল।

এই স্তরের মন্তব্য **এই ছবিটি সম্পর্কেই**; অন্য ছবির গায়ে বসিয়ে দিলে আর খাটে না।

### দুই স্তরের মধ্যে পার্থক্য কোথায় নয়

- **মতামতের দিক নয়।** দুই স্তরেই প্রশংসা ও নিন্দা দুটোই থাকে।
- **দৈর্ঘ্য নয়।** ছোট মন্তব্যও নির্দিষ্ট হতে পারে; লম্বা মন্তব্যও ছাঁচে বাঁধা
  হতে পারে।
- **ভালো বাংলা কি না, তা নয়।** বানান বা গঠন এখানে বিচার্য নয়।
<!-- AXIS_DEFINITION_END -->

## 4. Open questions for Sabbir

1. ~~**Is the direction right?**~~ ✅ **CHECKED against the data on 2026-08-11,
   not against the S2e table.** Which half k-means labels 0 is an artefact of
   initialisation — S2e reports every AUC directionless for exactly that reason
   — so this had to be recomputed from `results/s2e_regionA_k2_assignments.csv`
   joined to `data/cleaned/bn_clean.csv` rather than read off a report:

   | `cluster_k2` | n | mean words | median | types / 1k tokens |
   |---|---|---|---|---|
   | **0** | 1,143 | 13.12 | 11 | **269** |
   | **1** | 754 | 8.85 | 7 | **414** |

   **Level 1 is 33% shorter and carries 54% more word types per thousand
   tokens.** The direction in §3 is correct as written: level 0 is the
   longer, lower-variety half; level 1 the shorter, higher-variety one.
   ⚠️ Note the richness gap is *larger* here (269 vs 414) than S2e's
   equal-budget figure (1,623 vs 1,913) — expected, because this is a raw
   type-token ratio over unequal corpora and TTR falls as tokens grow, which is
   precisely the artefact S2e's fixed 4,000-token budget removes. **S2e's
   numbers are the reportable ones; these confirm only the direction.**
2. **Naming.** The levels are currently just 0 and 1. If they get names in the
   thesis, that is open decision 12 and yours.
3. **The §2.3 theory grounding** (`abercrombie1998`, `cuadrado1999`, …) was
   written for three audience types and is flagged for re-reading under the axis
   framing. It is not cited here, because nothing above rests on it.
