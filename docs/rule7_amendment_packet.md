# Amendment request — Inviolable Rule 7

**Student:** Sabbir Hossain (21701082) · **Prepared:** 2026-08-11
**Rule to amend:** `CLAUDE.md`, inviolable rule 7
**Decision required from:** supervisor **and** Sabbir, jointly
**Status until signed:** `enable_f1: false`. The guard stays in the code.

---

## 0. What you are being asked to decide, in one paragraph

Rule 7 forbids TF-IDF in the main pipeline. It was written to protect the
contextual encoders from mangled input, and for that purpose it is correct and
should be kept. But as worded it also forbids something different — computing a
corpus-frequency **statistic as a feature**, with the text left untouched — and
that prohibition costs the symbolic scorer a **measured ~18 macro-F1 points**
and pushes it toward exactly the feature families the 2026 literature identifies
as the ones that get gamed. **The request is to split rule 7 into two rules that
say separately what it currently says jointly**, not to weaken it.

---

## 1. The rule as it stands

> **7. No stemming, no stopword removal, no TF-IDF in the main pipeline.** LaBSE
> and BanglaBERT are contextual encoders and need natural text. (TF-IDF is
> allowed *only* as an explicitly-labelled cheap proxy in a pilot, never in a
> result.)

Note the structure: a prohibition, then **one stated rationale** — *"contextual
encoders need natural text"*.

---

## 2. The rule prohibits two different things, and its rationale supports only one

| | Operation | Does the text reaching LaBSE/BanglaBERT change? | Does the stated rationale apply? |
|---|---|---|---|
| **(a)** | stemming, stopword removal | **Yes** — the encoder sees mutilated Bangla | ✅ **Yes.** Rule 7 is right |
| **(b)** | IDF as a scalar feature | **No** — the encoder sees the original review, unchanged | ❌ **No.** Nothing is fed anything unnatural |

Our disputed feature family, **F1**, is (b): three scalar summaries (min, max,
mean IDF) of a review's own tokens. **No document-term matrix. No encoder
replaced. No text altered before LaBSE or BanglaBERT.** It is a number computed
*beside* the encoder, not a representation fed *into* it.

**The rule's own justification therefore does not reach F1.** That is the entire
technical claim in this document.

> ⚠️ **This reading was available in August and was deliberately NOT acted on.**
> Reinterpreting a rule whose preamble says *"breaking any of these invalidates
> the thesis"* is not a decision the student or the assistant may take alone.
> That is why this is a signature request and not a config change.

---

## 3. What it costs — measured, not argued

From `results/pilot_s35_idf.*` (explicitly banner-marked **NOT A RESULT**, run
under the pilot clause rule 7 itself provides).

| Quantity | Without F1 | With F1 |
|---|---|---|
| Stratified 5-fold CV macro-F1 | **0.5150 ± 0.0713** | **0.6949 ± 0.0532** |
| Majority-class baseline | 0.3926 | 0.3926 |

- **Leave-one-out delta for F1: +0.1798** — 2.5× the CV standard deviation, and
  an order of magnitude above every other family.
- **The mean rises while the variance falls.** That is not the signature of
  overfitting, which was the reason for caution.
- ⚠️ **Recorded because it was wrong:** the prediction before the run was that
  14 features on 82 rows would *lower* CV. It did the opposite.

**An effect nobody anticipated — F1 repairs F2.** Without IDF, *removing* the
length feature **improves** CV by 0.1082: length is actively harmful. With IDF
present, length's contribution moves to +0.0033. Length was a poor proxy for
what IDF measures directly, and was injecting noise in its absence.

### 3.1 The part that matters for the thesis, not just the accuracy

| Family | LOO delta | Gameable? |
|---|---|---|
| **F1 IDF** | **+0.1798** | **No** |
| **F6 lexical richness** | **+0.0213** | **No** |
| F4 connective presence | −0.0191 | **Yes** |
| F5 sentiment presence | −0.0350 | **Yes** |

**With F1 enabled, the two non-gameable families are the top contributors.
Without it, the scorer's remaining signal sits in presence-based rules that
contribute negatively.**

So rule 7 as applied does not merely cost accuracy. **It pushes the symbolic
scorer toward the gameable families** — and our §4.2 Reflector *tells the
generator which symbolic rule failed*. Under that loop, a pool of presence rules
is closer to a gaming instruction than to a scorer.

---

## 4. What the literature says — including the paper that argues against us

Searched 2026-08-11. ⚠️ **Consensus quota was exhausted until 2026-09-01, so
this used alphaXiv and scite.** "Searched a different index" and "did not
search" are different facts and are recorded as such.

**(i) The premise of rule 7 points the wrong way.**
`clavie2026latentterms` (arXiv 2605.29384) show that dense retrievers **already
contain** sparse, IDF-ready structure their scoring interface never exposes.
Sparse autoencoder features taken from a *frozen* retriever have **quasi-Zipfian
collection statistics**, so BM25 — which is IDF at its core — works on them
unmodified. Their own qualitative audit finds **about one third of the extracted
features are purely lexical**. IDF is not foreign to a contextual encoder; the
encoder has internalised it. Rule 7 forbids computing explicitly what LaBSE is
already using implicitly.

**(ii) The 2026 preprocessing literature has not tested rule 7's premise.**
`magsarjav2026preprocessing` is a 2026 systematic study of preprocessing order —
and states plainly that it *"will primarily focus on word-based sentiment
analysis"* rather than BERT-class models. The studies it reviews report stopword
removal and stemming as *"not so important"* — **low impact, not harmful**. So
part (a) of rule 7 is under-evidenced, but it is also nearly free to keep, which
is why this request keeps it.

**(iii) 🔴 The paper that cuts against enabling F1, reported because it does.**
`barata2026hybrid` (arXiv 2608.02112) asks whether a cheap extra component adds
value to an already-strong hybrid. Across five datasets, 14,500 queries and
exhaustive scoring, the cheap component received **zero weight in all 50
cross-validated fold selections**, and **forcing it in reduced effectiveness**.
Their conclusion is the one we must apply to ourselves:

> *"standalone benchmark performance is insufficient to establish marginal value
> in hybrid retrieval."*

**Our +18 points is a standalone number.** Whether IDF-enhanced symbolic adds
anything *to the Critic* has not been measured. And the component they rejected
was, like ours, the weaker one standalone.

---

## 5. 🔴 A risk this search created, which was not previously on record

If `clavie2026latentterms` are right that IDF signal already lives inside LaBSE,
then **adding IDF to symbolic may make symbolic more correlated with Verifier-A,
not less**.

The hybrid Critic exists to combine **two independent signals**. This is the
same failure `kuai2026entanglement` describe, where *"apparent agreement may
reflect a consensus of correlated errors rather than independent verification"*.

**So enabling F1 may buy accuracy at the cost of independence — and independence
is what RQ5 measures.** This argues for the conditional amendment in §6, not for
a straight enable.

---

## 6. The amendment requested

**Replace rule 7 with two rules.**

> **7a. No text transformation before any encoder — unchanged, and strengthened
> by being stated alone.**
> No stemming, no stopword removal, no character normalisation beyond
> whitespace. LaBSE and BanglaBERT always receive the original Bangla, exactly
> as collected. This remains inviolable, and nothing in this request touches it.

> **7b. Corpus-frequency statistics may enter as explicit scalar features of the
> symbolic scorer only.**
> Permitted: IDF summaries of a review's own tokens, as features.
> **Forbidden, as before:** any document-term matrix or TF-IDF vector used as a
> *representation*; any such transformation applied to encoder input; TF-IDF
> replacing or preprocessing for LaBSE or BanglaBERT.
> **F1 remains disabled until it passes the test in §7.**

---

## 7. The conditions under which F1 turns on

Enabling on the strength of §3 alone would repeat the error `barata2026hybrid`
warn about. F1 turns on **only if all four hold**, each pre-registered before the
run:

1. **Marginal, not standalone.** Inclusion is selected on **training folds only**
   and evaluated **held out** — the contribution to the *Critic*, not the
   symbolic scorer's own CV.
2. **Paired inference.** Bootstrap CI plus multiplicity correction, as in
   `barata2026hybrid`. A CI straddling zero means **not established**, and F1
   stays off.
3. **The forced-inclusion check.** Does forcing the symbolic term in *reduce*
   held-out performance? That is what rejected the cheap component in all 50 of
   their folds, and it must be run against us too.
4. **The entanglement check (§5).** If IDF-enhanced symbolic is measurably more
   entangled with Verifier-A, that is reported beside any RQ5 gap, and a small
   A−B gap **may not be read as absence of gaming**.

**All four outcomes are publishable, including "F1 adds nothing."** That result
would be strictly better than the present situation, in which the symbolic
term's weight was hand-written and never tested at all.

---

## 8. What happens if the amendment is refused

Stated plainly, because refusal must be a real option and its cost should be
visible.

- The symbolic scorer stays at **0.5150** against a majority baseline of 0.3926.
- The Critic remains **0.6 × a circular scorer + 0.4 × a barely-better-than-
  majority one**. (Verifier-A's 0.9866 is `CIRCULARITY_CONFIRMED` — a linear
  probe on the encoder that generated the label.)
- The symbolic scorer's remaining signal stays concentrated in **presence-based
  rules**, which `mahmoud2026rubric` identify as the category that gets hacked —
  under a loop that names the failing rule to the generator.
- **RQ3 stays close to unanswerable**: the *"symbolic adds < 2 points"* rule
  would need to resolve **1.6 dev items** at n = 82.

This is a defensible position. It is not a free one, and the thesis would have
to say so in Limitations rather than leave it unstated.

---

## 9. Signature

**Amendment to inviolable rule 7 — split into 7a (unchanged) and 7b
(conditional), with F1 gated on the four tests in §7.**

- [ ] Approved as written
- [ ] Approved with changes: ______________________________________________
- [ ] Refused — rule 7 stands unchanged, and §8 goes into Limitations

Supervisor: ____________________________ Date: __________

Sabbir Hossain: ________________________ Date: __________

> Until one of these boxes is ticked and dated, `enable_f1` stays `false` and
> `s35_scorer.py` continues to refuse any non-pilot run that sets it. The
> constraint is enforced in code, not by anyone remembering this document.
