# Lab Notebook — dated decisions and their reasoning

> Why this file exists: `results/` stores **numbers**; this file stores **why**.
> Thesis Chapter 3 (Methodology) and the Limitations chapter are written from
> here, not from the JSON logs. Every entry names the thesis section it feeds.
>
> Rule: an entry is written the day the decision is made, never reconstructed.

---

## 2026-07-27 — Phase 0 / Step 1: repository and reproducibility contract
**Feeds:** Ch.3 §Experimental Setup; Appendix (environment)

Repo created to the pipeline §0.1 layout. Global seed=42 enforced through
`src/common/seed.py`; every result carries a UTC timestamp and git commit hash
via `src/common/provenance.py`.

**Decision — unpinned install, pinned record.** `requirements.in` is unpinned so
installs resolve to current releases; `src/common/env_snapshot.py` then freezes
the resolved set into `requirements.lock.txt`, which is committed. Rationale:
hand-pinned versions go stale and cost research time, but the pipeline §C
requires exact versions in the appendix and a reviewer must be able to reproduce
a number months later. This satisfies both.

**Decision — `data/splits/*.json` is force-included in `.gitignore`.** All other
derived data is ignored. The split map is the one derived artifact that cannot be
regenerated without invalidating every downstream result (pipeline §A).

---

## 2026-07-27 — Step 2: S0 verification (read-only)
**Feeds:** Ch.3 §Dataset; Ch.4 §Data Quality; dataset card

The pipeline's S0 table was treated as a set of **claims to be tested**, not
facts. `src/preprocess/s0_xray.py` recomputes each independently. Verification
was deliberately separated from cleaning so that a disagreement can only have one
cause (the data) rather than two (the data or a bug in the cleaning code).

**Result: 8 of 11 claims reproduce. Three do not.**

| Quantity | Claimed | Observed | Nature of the defect |
|---|---|---|---|
| `null_rows` | 1 | **2** | Under-reporting |
| `normalized_duplicates` | 205 | **206** | Off-by-one; original definition unrecoverable |
| `usable_n` | 4,722 | **4,730** | Arithmetic error (see below) |

**Finding — `null_rows` is 2, and they are different kinds of null.** Row 849 has
missing review text with a valid label; row 897 has valid text with a missing
`Sentiment`. Only the first was counted originally. Both must be dropped: a
review with no label is unusable for weak supervision.

**Finding — 4,722 is a double-counting artifact, not a rounding.** It is
reproduced exactly by `5000 − (2 + 72 + 204) = 4722`, i.e. by subtracting the
three drop counts as if the sets were disjoint. They are not: |SHORT ∩ DUP| = 10.
The true union is 268 (exact dups) or 270 (normalized), giving 4,732 / 4,730.
Note the subtraction uses **2** nulls — the observed count — so the S0 table is
internally inconsistent with its own `usable_n`, and the defect lies in how
`null_rows` was reported rather than in the arithmetic's null handling.

**Consequence:** every split size in the pipeline derives from `usable_n`, so
this correction propagates to R1/R2 sizes. Logged in `protocol.md` deviations.

**Finding — the "Raw" file is partially pre-cleaned (evidence #1).** An initial
emoji regex flagged 6 rows. On inspection all 6 contained a bare U+FE0F
(VARIATION SELECTOR-16) orphaned directly after a Bangla letter — a modifier with
no emoji base, i.e. residue left behind when the publisher stripped emoji. The
regex was corrected (VS-16 excluded, so `emoji_rows = 0` stands) and the orphan
count is reported as context. **Methodological note for the thesis:** a regex
result was inspected rather than trusted; this is the reason the emoji
preprocessing tables in the pre-defence report do not describe this file.

---

## 2026-07-27 — Step 3: rule-based cleaning → `bn_clean.csv` (n = 4,730)
**Feeds:** Ch.3 §Preprocessing; Ch.4 §Data Quality; Limitations (construct validity)

**Decision — normalized duplicates (206), not exact (204).** Normalized is a
superset of exact. A pair differing only in whitespace or Unicode normalization
form is the *same review*; keeping both allows one review to appear in R1 and its
twin in R2, contaminating the Verifier-A / Verifier-B separation on which RQ5
depends. `configs/s1_clean.yaml` already sequenced both steps, so this is a
clarification, not a new choice.

**Decision — no stemming, no stopword removal, no TF-IDF** (pipeline §1.1.3).
LaBSE and BanglaBERT are contextual encoders requiring natural text. TF-IDF is
permitted only as an explicitly labelled cheap proxy in a pilot, never in a
reported result. This corrects the earlier pipeline.

**Finding — step order is load-bearing.** `drop_exact_duplicates` removes 205,
not the 204 found on raw text, because `normalize_whitespace` runs first and
collapses one whitespace-differing pair into an exact match; the NFC key then
catches 1 more. The *total* (206) is order-invariant but the split between the
two steps is not. The order is therefore part of the protocol, not an
implementation detail, and is logged per-step in `results/s1_cleaning_log.json`.

**Decision — `review_id` format `bn_0042`.** IDs derive from the 0-based **raw**
row index assigned before any drop, so `bn_4999` still points at raw row 4999 and
re-running cleaning cannot change an ID. Two reasons for the prefix: (a) a bare
zero-padded numeric string is coerced to int by pandas/Excel on read, destroying
the padding and silently breaking the frozen split map — and these IDs reach
annotators via Label Studio CSV export; (b) the English arm will use `en_xxxx`,
and under the §1.2 "mirror, never merge" rule an accidental namespace collision
must be immediately visible rather than silent.

**Finding — the curated balance does not survive cleaning (evidence #2).**

| Sentiment | Raw | Post-clean | Dropped |
|---|---|---|---|
| 0 | 1,665 | 1,513 | 152 |
| 1 | 1,664 | 1,599 | 65 |
| 2 | 1,670 | 1,618 | 52 |
| Total labelled | 4,999 | 4,730 | 269 |
| Unlabelled | 1 | 0 | 1 |

152 of 270 drops fall in class 0 — not random attrition. Perfect balance
(1665/1664/1670) in a scraped corpus is already implausible; that the negative
class carries a disproportionate share of *duplicates and sub-3-word items*
suggests the balance was achieved by padding class 0 with repeats and very short
reviews. This is the second independent piece of evidence that the file is
curated rather than raw, and belongs in the dataset card as evidence, not as a
complaint.

**Consequences:** (a) the resulting imbalance is mild (ratio 1.07) so no
re-balancing is applied; (b) **R1/R2 must be sentiment-stratified**, else the two
verifiers see different class priors and the Goodhart comparison is confounded;
(c) the case for reporting Gwet's AC1 alongside κ (§2.5) is strengthened.

---

## 2026-07-27 — Ordering change: near-duplicate removal moved BEFORE split freeze
**Feeds:** Ch.3 §Data Splits; Ch.5 §Threats to Validity — **defence-relevant**

`configs/s1_clean.yaml` deferred LaBSE near-duplicate removal (cosine > 0.95) to
S2, while the week plan froze the R1/R2 split before it. This ordering is a
leakage path: if a near-duplicate pair is split across R1 and R2, Verifier-B is
effectively evaluated on Verifier-A's training content, and the A/B wall that the
entire RQ5 Goodhart test rests on is compromised.

**Old:** clean → freeze split → embed → near-dup
**New:** clean → embed → near-dup → **then** freeze split

Cost is ~zero (the LaBSE pass was required anyway). Recorded here because the v1
verifier (`shksabbir7/bengali-movie-review-classifier`) was discarded for exactly
this class of defect — a leaked split — and repeating it would be
indefensible. **This entry is the answer to the expected defence question about
train/test contamination.**

---

## 2026-07-27 — S2 pilot instrumentation (written, not yet run)
**Feeds:** Ch.3 §Persona Discovery; Ch.4 §Trap-check

Beyond the ARI trap-check the pilot reports: (a) the off-diagonal cosine
**distribution** (p50/90/95/99/99.9, max) because a 0.95 cutoff inherited from
long-document dedup literature may be either far too aggressive or nearly inert
on ~8-word texts, where anisotropy and hubness compress similarities into a
narrow high band — the same high-dimensional pathology §2.1 already concedes for
silhouette; (b) cluster sizes, the 3×3 cluster×Sentiment crosstab, χ² and
Cramér's V, with a DEGENERATE flag (<5% or >70% in any cluster), because a
degenerate partition scores *low* ARI by failing to partition at all and must not
be misread as evidence that personas are independent of sentiment; (c) ARI both
before and after dedup, pre-empting the reviewer question of whether dedup itself
moved the cluster structure.

**Status:** logic tested against brute force on synthetic embeddings; the
embedding path is unexercised. The first Kaggle run is also the first end-to-end
test.

---

## 2026-07-28 — Provenance v2: what the labels are, and what the sample is not
**Feeds:** Ch.3 §Dataset; Ch.5 §Threats to Validity; dataset card

The dataset's provenance was obtained **verbally from the data collector on
2026-07-28**. **There is no written collection log**, and this is the single
fact that sets the confidence on everything below to `recall-based (medium)`.
Not the manner in which the account was obtained — the absence of a record.

**On the revision during supervision.** The account was revised **once**: an
initial description of the labels as a harvest-pass indicator was corrected to
**single-coded per-item human annotation**. A second apparent change was
**an input error, not a substantive revision** — confirmed as such by the
collector. It is recorded here so that a reader comparing drafts does not infer
two revisions where one occurred. A single correction under questioning is
ordinary and is not itself grounds to discount the account; the discount comes
from the missing log.

**The distinction that now organizes the threats.** These are two different
problems and conflating them would misdirect every mitigation:

| | Status | Why |
|---|---|---|
| **Label validity** | **Adequate in kind, but single-coded and unquantified** | Labels are genuine per-item human judgments — not heuristics. But one annotator with no overlapping items means **no IAA is computable** and systematic bias is unmeasurable. |
| **Sample validity** | **Compromised** | Quota stopping at ~1,665/class **destroys the natural class prior**; venue/thread/timestamp were not retained, so the sampling frame cannot be reconstructed. |

The consequences differ. Label validity is *repairable after the fact*: the
retrospective reliability study (200 items, 2 blind annotators, registered in
STATUS parallel tracks) converts "no IAA exists" into an estimated figure.
**Sample validity is not repairable** — no prevalence claim may ever be made
from this corpus, and the unretained venue leaves a permanently untestable
alternative explanation if clusters turn out to track sentiment (protocol.md,
RQ1 Band 3).

**Decision — the raw file needs verification, not backup.** The `.xlsx` is the
root of every `review_id` (IDs derive from its raw row order), so a silently
different copy would invalidate all of them with no error anywhere. But it is
**re-downloadable from Mendeley**, so the risk is *substitution*, not *loss* —
and the control for substitution is a checksum, not a second copy. SHA-256
recorded in STATUS (Confidence: `verified`) and in the README reproducibility
contract. `bn_clean.csv` needs neither: it is deterministically regenerable from
the `.xlsx` by `s1_clean.py`, which asserts n = 4,730.

**Pre-registration written today, before any ARI exists.** The RQ1 ARI bands
were rewritten (DEGENERATE / <0.20 / 0.20–0.60 / >0.60) and the log-odds probe
registered as a REQUIRED falsification test of the no-keyword-search claim. The
S2 pilot has still never been run, which is what makes this pre-registration
rather than rationalization — the commit timestamp is the evidence.

---

## 2026-07-30 — Infrastructure: LF normalization, S2 numeric tests, Kaggle runner

**Feeds:** Ch.3 (Reproducibility), Appendix (environment) · **Artifacts:**
`.gitattributes`, `tests/test_s2_numeric.py`, `notebooks/s2_pilot_kaggle.ipynb`
· **No result numbers changed by this entry.**

### What prompted it

`git status` showed `results/env_snapshot.json`, `results/s0_data_xray.md` and
`results/s1_cleaning_log.json` as modified, uncommitted, since 2026-07-28.
Before running S2 on top of them they had to be explained, because a new result
resting on unexplained modifications to earlier results is not defensible.

### Finding — the diff was pure line-ending churn, not a content change

`git diff --ignore-cr-at-eol -- results/` is **empty**. All three files were
byte-identical to `HEAD` apart from CRLF-vs-LF: 24, 121 and 134 converted lines
respectively. **No number, no table, no verdict changed.** Verified by comparing
the md5 of each worktree file against `git show HEAD:<file>` after converting
back to LF — all three match exactly. Nothing in the STATUS "Verified facts"
table is affected.

**Cause.** Python's text mode writes `os.linesep`, so `Path.write_text()` emits
CRLF on Windows and LF on Linux — the same script on the same data produces
different bytes on the two hosts this pipeline runs on by design (Windows
locally, Kaggle remotely). `core.autocrlf` is **unset** in this checkout, so git
records those CR bytes as real changes.

**A stale claim was found and corrected.** The previous `.gitattributes` header
asserted "This checkout has `core.autocrlf=true`". It is not, and there is no
evidence it ever was; `git config core.autocrlf` returns empty. The comment was
an assumption written as a fact, which is precisely how the phantom diff went
unexplained for two days.

### Why this was worth fixing rather than committing

A 279-line diff with zero content change is not cosmetic — it is camouflage. The
next real change to `s0_data_xray.md` would arrive inside a wall of identical
noise, and the reviewer-facing claim that a result is reproducible across hosts
is false if the same inputs yield different bytes. Byte-identical output across
Windows and Kaggle is part of the reproducibility contract.

### Decisions made (and why)

- **Two-layer fix, not one.** Source layer: `provenance.write_text_lf()` and
  `provenance.NEWLINE`, used by every writer of a text artifact
  (`s0_xray`, `s1_clean`, `s2_pilot`, `step_close`, `env_snapshot`); pandas
  `to_csv` calls now pass `lineterminator="\n"`. Git layer: `.gitattributes`
  pins `eol=lf` for all text types. The writer keeps new files correct; the
  attributes catch anything written by hand or by a tool that bypasses it.
  Either alone would leave a hole.
- **`*.xlsx binary` added explicitly.** Git's auto-detection would almost
  certainly have handled it, but the raw `.xlsx` is pinned by SHA-256 and every
  `review_id` derives from its row order. A line-ending conversion applied to it
  would break the hash and invalidate all IDs with no error raised anywhere. Not
  worth leaving to heuristics (inviolable rule 1).
- **The three files were renormalized to LF rather than committed as CRLF.**
  They are now byte-identical to `HEAD`, so `results/` carries no diff at all
  and this commit touches no result file. That is the honest outcome: nothing
  about the S0/S1 numbers was re-derived today, so nothing in `results/` should
  appear to have changed.
- **`requirements.lock.txt` renormalized to LF — this is not a hand-edit.**
  CLAUDE.md forbids hand-editing the lock file, so the distinction matters: all
  **166 pins are byte-identical** (verified by comparing the sorted pin sets
  before and after, and by `diff` against `HEAD` with CRs stripped). Only the
  166 line terminators changed. It had to be done in this commit rather than
  left: the new `*.txt text eol=lf` rule would otherwise make the file appear
  modified on the next `git add` by anyone, for no visible reason — exactly the
  confusion this whole entry is about.
- **A trailing newline is now written for result JSONs.** `env_snapshot.json`
  previously ended without one, which shows as "\\ No newline at end of file" in
  every diff and makes appending a line look like editing the last one. Applies
  to files written from now on; the existing file was left byte-identical to
  `HEAD` on purpose.
- **`env_snapshot.py` gained `--out`, and refuses to target the lock file.**
  Run with no arguments it overwrites `requirements.lock.txt` — which, executed
  on Kaggle, would silently replace the record of the local environment with a
  Linux freeze and leave every earlier result pointing at a machine it never ran
  on. `--out` writes a snapshot *alongside* the lock instead. The old
  `notebooks/README.md` would have led straight into this trap.
- **Kaggle environment policy — host-native, recorded (Sabbir's decision,
  2026-07-30).** S2 will run against Kaggle's preinstalled torch/CUDA with only
  `sentence-transformers` and `pyyaml` installed on top, rather than applying
  `requirements.lock.txt` (Windows-frozen, would drag in a full torch build and
  conflict with Kaggle's CUDA image). **Consequence to report:** S2's numbers are
  attributable to `results/env_snapshot_s2_kaggle.json`, *not* to
  `requirements.lock.txt`. The thesis must describe two environments and state
  which produced which result. This is a disclosure obligation, not a caveat to
  bury.

### Findings (things we did not expect)

- **The S2 numeric core had no tests at all.** `test_s2_verdict.py` pinned the
  *interpretation* of ARI but nothing checked the *computation* underneath it —
  the blocked matmul in `all_near_dup_pairs` and the greedy pass in
  `greedy_keep_first`, which together decide which rows exist for the rest of the
  thesis. A pair missed at a 512-row block boundary would survive into the frozen
  split, and the split is never regenerated (rule 3), so the error would be
  **permanent and invisible**. Added `tests/test_s2_numeric.py`: 15 differential
  tests against brute-force O(n²) references, `n = 1100` chosen to straddle the
  block size with a short final block. **All 15 pass, all 8 existing verdict
  tests still pass.** The dedup logic is correct as written — including the
  transitive-chain guard (a~b, b~c, a≁c leaves the far end alive) and the
  strongest-anchor tie-break.
- **Float32 cosine can exceed 1.0.** Two L2-normalized identical vectors dot to
  `1.0000001192092896`, not `1.0`. Harmless at the swept thresholds (0.90–0.98)
  and no removal decision depends on it, but the `maximum` row of the report's
  cosine-distribution table will print a value slightly above one and a reviewer
  may ask. Noted here so the answer exists before the question.
- **`notebooks/README.md` pointed at a script that does not exist**
  (`src/cluster/pilot_trapcheck.py`; the real file is `src/cluster/s2_pilot.py`).
  Following it would have failed on Kaggle after the clone. Corrected.
- **`bn_clean.csv` re-verified end-to-end today** through `load_clean`: 4,730
  rows, class balance 1,513 / 1,599 / 1,618, word count median 8 / max 84 /
  min 3, zero nulls, `review_id` running `bn_0000`…`bn_4999`. Every figure
  matches the STATUS "Verified facts" table. No drift.

### Consequences for downstream steps

- S2 can now be launched without a broken-runner or clobbered-lock failure mode.
  The runner runs both test suites *before* the experiment and pre-flights
  `load_clean` *before* LaBSE downloads weights, so a mismatch costs seconds
  rather than a session.
- The appendix must carry **two** environment records and say which result came
  from which host. Do not present `requirements.lock.txt` as the environment for
  S2.
- No deviation logged in `protocol.md`: nothing here changes a method, a
  threshold, or a pre-registered band. The pre-registration is untouched, and the
  S2 pilot has still never been run.

### Citations needed

- None. No new method was introduced — this entry is tooling and test
  infrastructure only.

---

## 2026-07-30 — S2 pilot: the trap-check ran, and found something else

**Feeds:** Ch.4 §Persona discovery, Ch.4 §Data quality, Ch.5 §Threats
**Artifacts:** `results/s2_pilot_ari_trapcheck.md`,
`results/env_snapshot_s2_kaggle.json`, `results/s2b_register_probe.md`,
`docs/provenance_query.md`
**Ran on:** Kaggle, Tesla T4, commit `e3d8e43`

### Numbers

- ARI(cluster, Sentiment) at the primary threshold 0.95: **0.1793** → Band 1,
  `NOT_SENTIMENT_ALIGNED`
- Cramér's V 0.4104 · χ² 1558.05 (df 4) · surviving n **4,625**
- Cluster shares 39.2 / 30.9 / 29.9 — **not degenerate**, so the ARI is
  interpretable
- Sensitivity: no-dedup 0.1792 (Band 1) · **0.90 → 0.2181 (Band 2)** ·
  0.95 → 0.1793 (Band 1) · 0.98 → 0.1784 (Band 1)
- Off-diagonal cosine: median 0.3511, p99.9 **0.7561**, max 0.999758

### Reading it in the pre-registered order

**Distribution first.** p99.9 = 0.7561 sits below every swept threshold, so none
of them cut into the bulk of the distribution — they trim a genuine duplicate
tail (449 pairs out of 11,184,085, i.e. 0.004%). The pre-registered worry that a
threshold might be removing merely *similar* short reviews did not trigger. The
median of 0.3511 is itself worth reporting: with 8-word reviews, unrelated texts
already sit at high cosine.

**Degeneracy second.** All three clusters inside the 5–70% band at every swept
threshold, so Band 0 does not apply and the ARI means something.

**Then the number.** Band 1 at the pre-registered primary threshold.

### Findings (things we did not expect)

**(1) The sensitivity curve is not constant.** At t = 0.90 the verdict crosses
into Band 2 (`PARTIAL_OVERLAP` + `RESIDUAL_TEST_REQUIRED`); at 0.95 and 0.98 it
is Band 1. ΔARI vs no-dedup is +0.0388 at 0.90 but +0.0001 at 0.95 — so the
low threshold is doing real work on the headline number, not housekeeping. The
primary threshold was fixed in `configs/s2_pilot.yaml` on 2026-07-28, two days
before the run, so the headline stays Band 1 and the 0.90 result is a
**mandatory disclosure**, not a reason to switch. Moving to 0.90 now would be
threshold-shopping.

**(2) A low ARI beside a moderate V is not a clean result.** The report's own
text warned this combination is a caveat rather than a pass, and the crosstab
shows why. Per class, the distribution across clusters is:

| Sentiment | Cluster 0 | Cluster 1 | Cluster 2 |
|---|---|---|---|
| 0 | 55.5% | 27.8% | 16.8% |
| 1 | 62.4% | 20.3% | 17.3% |
| 2 | **0.8%** | 44.3% | 54.9% |

Classes 0 and 1 are distributed **almost identically** — the clustering cannot
separate them at all. Class 2 is almost entirely absent from cluster 0 (12 of
1,572) and then split across the other two. So the recovered structure is
effectively **binary**: class 2 versus the rest. ARI is low because a three-way
partition that merges two classes and splits the third scores poorly even when
strong structure exists. Recomputing ARI and V independently from the crosstab
reproduced the report exactly (0.1793 / 0.4104), so the report's arithmetic is
sound.

**(3) — the important one. Class 2 appears not to be the same kind of text.**
Refolding the crosstab as *cluster 0 vs rest* × *class 2 vs rest* gives
**φ = 0.565**, a stronger association than the clustering has with sentiment as
a whole. That prompted the register probe (`results/s2b_register_probe.md`,
**exploratory**), which measured only features that cannot encode an opinion
about a film:

| | class 0 | class 1 | **class 2** |
|---|---|---|---|
| contains দাঁড়ি | 58.0% | 66.0% | **100.0%** |
| first-person pronoun | — | — | **0.0%** (expected 149) |
| exclamation mark | — | — | **0.0%** (expected 38) |
| comma run `,,,` | — | — | **0.0%** (expected 33) |
| word types per 12,000 tokens | 3,577 | 3,303 | **1,772** |

Four structural absolutes and roughly half the vocabulary at identical length.
Near-duplicate endpoints are 50.1% class 2 against a 34.2% corpus share, and
51.8% in the contested 0.90–0.95 band — which is also why the threshold question
and this question are the same question.

**This is the confound RQ1 Band 3 pre-registered** ("clusters recovering the
source rather than any persona"), and which `STATUS.md` recorded as *untestable
in principle* because venue was never retained. **That record was wrong in one
specific way: venue was not retained, but writing style survives in the text.**
Three explanations fit equally well — generated to fill the quota, collected
from a different venue, or hand-written as neutral examples — and all three
break provenance fact (c) and all three mean the clusters track provenance.
Statistics cannot choose between them; only the collector can.
`docs/provenance_query.md` puts the question in answerable form.

**(4) `git_hash()` was calling every run dirty.** The stamp on the S2 report
reads `e3d8e434…-dirty`, but the run came from a **fresh `--depth 1` clone**,
where no tracked file can have been modified. The suffix came from bare
`git status --porcelain`, which also lists untracked files — and every run
creates untracked outputs. A flag that is always on is not a flag. Fixed to use
`-uno`; untracked files are now counted separately in `stamp()`. Verified in a
clean-room clone: untracked files alone leave the hash clean, editing a tracked
file restores `-dirty`.

**(5) Two gaps in the tooling.** `s2_pilot.py` never persists cluster
assignments, so every follow-up question about the clustering has to be
reconstructed from the printed crosstab or answered by re-running the whole
embedding. And the Kaggle environment diverges from `requirements.lock.txt` more
than expected — **scikit-learn 1.6.1 computed the KMeans and the ARI**, not
1.9.0; numpy 2.0.2 not 2.4.6; transformers 5.0.0 not 5.14.1.

### Decisions made (and why)

- **Threshold left at the pre-registered 0.95**, with the 0.90 divergence
  reported as a sensitivity caveat. The audit sheet for revisiting it
  (`results/s2_threshold_audit_sheet.csv`, blinded, 30 contested + 8 control
  pairs) is generated and **parked** — 52% of the contested band is class 2, so
  the threshold question is downstream of the provenance question and answering
  it first would settle nothing.
- **RQ1's persona claim is suspended**, not withdrawn, pending the provenance
  answer.
- **Register probe registered as exploratory** in `protocol.md`, not slipped in
  as a planned analysis. Nothing is trained in it, so inviolable rule 10 stands.
- **The split stays unfrozen.** Open decisions 1 and 2 cannot close while the
  composition of the corpus is in question.

### Consequences for downstream steps

- Gold-300 stratification was to be drawn from the S2 clusters. If those clusters
  are tracking provenance, the annotation scheme needs rethinking **before** 300
  items are annotated — this is the cheapest possible moment to find out.
- The appendix must report two environments and say which produced S2.
- `docs/STATUS.md` fact (c) and the "untestable in principle" note both need
  correcting.

### Citations needed

- **None for method.** Everything in the probe is textbook: rank AUC
  (Mann–Whitney U), Wilson score intervals, type–token ratio at a fixed token
  budget. No published technique was adopted, so attaching a citation would
  misrepresent where the analysis came from.
- **Open, and Sabbir's to decide:** whether the finding is *framed* in the
  stylometry / authorship-attribution literature or the
  machine-generated-text-detection literature when it reaches Ch.4. That choice
  shapes the related-work section and is a writing decision, not a method one.
  Logged in `STATUS.md` open decisions rather than guessed at here.

---

## 2026-07-30 (later) — I asked the wrong question. It is not the class, it is the file.

**Feeds:** Ch.4 §Data quality, Ch.5 §Threats · **Artifact:**
`results/s2c_region_split.md` · **Supersedes:** the framing of
`results/s2b_register_probe.md`

### What happened

The collector was asked where the class-2 rows came from and answered that they
were **collected the same way as the others**. Rather than treat that as
settling it or as contradicting it, the raw `.xlsx` was examined directly —
`review_id` derives from its row order, so the file's assembly is recoverable.

The label sequence has only **10 runs across 5,000 rows**: the file was pasted
together in blocks. Then, per block, the register features:

| rows | label | দাঁড়ি | first-person | exclaim | types/1k |
|---|---|---|---|---|---|
| 0–498 | 1 | 36.3% | 20.2% | 1.2% | 298 |
| 499–896 | 0 | 32.4% | 9.0% | 3.0% | 399 |
| 999–1498 | 1 | 54.4% | 14.6% | 6.0% | 359 |
| 1499–1998 | 0 | 32.0% | 9.6% | 2.8% | 443 |
| **1999–2999** | **2** | **100.0%** | **0.0%** | **0.0%** | **184** |
| **3000–3664** | **1** | **96.5%** | **3.5%** | **1.2%** | **240** |
| **3665–4330** | **0** | **99.8%** | **0.0%** | **0.0%** | **240** |
| **4331–4999** | **2** | **100.0%** | **0.0%** | **0.0%** | **144** |

**The split is by position in the file, not by label.** Rows 3665–4330 are
labelled **0** and look nothing like rows 499–896, which are also labelled 0.

Aggregated: rows 0–1998 (n = 1,999) at 38.7% দাঁড়ি / 13.5% first-person / 255
types per 1k; rows 1999–4999 (n = 3,001) at **99.2% / 0.8% / 128**. The rolling
দাঁড়ি rate steps from ~30% to 100% over roughly 50 rows around row 2000 — a step,
not a drift.

Reading samples confirms it independently. Region A, label 0: *"কি বাজে মুভি!
কিভাবে বানায় এগুলা!"* Region B, label 0: *"সিনেমার গল্প একঘেয়ে।"* Region A,
label 1 carries a typo (*থিবীর* for *পৃথিবীর*) and names actors; region B, label
1 is multi-sentence, generic, and names nobody.

### Findings

- **`s2b`'s measurements were right and its interpretation was wrong.** Class 2
  is not a different kind of text *because it is neutral*; it is a different kind
  of text because **all 1,670 neutral rows sit inside region B**, and region B is
  a different corpus. The neutral class is perfectly nested in the second file.
  Corrected in STATUS as fact (split), with (reg) struck through rather than
  deleted — a superseded claim that vanishes is a claim nobody can audit.
- **This is 60% of the corpus**, not 34%. Region B holds 3,001 of 5,000 raw rows
  and 2,820 of 4,730 cleaned rows, across **all three labels**.
- **The cluster correspondence is suggestive but not established.** S2's cluster
  0 holds 1,814 items (823/979/12); cleaned region A holds 1,910 (948/962/0).
  Close — but `ARI(cluster, region)` cannot be computed, because `s2_pilot.py`
  never persisted the assignments. That is the decisive number and it is
  outstanding.
- **The collector's recollection is inconsistent with the file's own layout.**
  That is a finding about the record, not about the person: fact (a) already
  established there is no written collection log, the recollection is old, and a
  second source merged at assembly time is an easy thing to forget. `protocol.md`
  pre-committed that a computed test supersedes the recall-based table where they
  disagree — that pre-commitment is now doing exactly the work it was written for.

### Decisions made (and why)

- **The question to the collector is being re-asked**, against the region rather
  than the class. "Where did the neutral reviews come from?" was answerable with
  "same way" in good faith; "rows 2000 onward look like a different corpus,
  including the negative ones — where did that block come from?" is a question
  the answer can actually engage with.
- **Nothing is deleted or re-run to make this go away.** The S2 result stands as
  computed; it is now reported *with* the confound rather than instead of it.
- **`s2b` is kept, not withdrawn.** Its numbers are correct and its framing error
  is instructive — it is exactly the mistake of reading a file-layout artifact as
  a semantic property.

### Consequences for downstream steps

- Every result over the full corpus is confounded, **including the S2 trap-check
  itself**. The ARI of 0.1793 was computed across two corpora.
- Region A survives as **1,910 cleaned rows, organic register, two classes**
  (948 negative / 962 positive). Smaller and binary, but real — a viable corpus
  if the thesis narrows to it.
- The three-persona design assumed three classes. Region A has two.
- Gold-300 stratification must not be drawn until decision 0b is settled.

### Citations needed

- None yet. If the thesis reports the split as a dataset-integrity finding, the
  framing decision (open decision 5) covers it.

---

## 2026-07-30 (later still) — instrumenting the decisive test, before running it

**Feeds:** Ch.4 §Persona discovery · **Artifacts:** `configs/s2_pilot.yaml`
(region scoring), `configs/s2_pilot_regionA.yaml`, `tests/test_s2_region.py`,
`docs/protocol.md` RQ1-A · **Nothing was run.**

### Numbers

None from a model. This entry exists precisely because **no result exists yet** —
the interpretation is being fixed while the outcome is still unknown.

Feasibility was computed first, because if region A could not carry the thesis
none of the rest was worth building:

- cleaned region A: **1,910** rows (948 negative / 962 positive), median 9 words
- near-duplicate burden: of the 449 pairs, **387 are internal to region B**, 61
  internal to A, and exactly **1 crosses** the boundary
- after dedup at 0.95: **~1,897**
- budget: G-300 eval-only + R1 ≈ 798 (RAG index) + R2 ≈ 799 (verifier training)

~800 examples to fine-tune a binary BanglaBERT verifier is small but workable;
~800 for a RAG index is thin but usable. Region A is a real fallback, not a
consolation prize.

### Findings (things we did not expect)

- **The near-duplicate asymmetry was not looked for and is the strongest
  evidence yet.** If the two regions were really one corpus, near-duplicate
  pairs would cross the boundary at some rate. **Exactly one of 449 does.** This
  owes nothing to the register features, so it is independent confirmation.

### Decisions made (and why)

- **`s2_pilot.py` now persists cluster assignments.** Their absence is why
  `ARI(cluster, region)` could not be computed from the first run — a
  one-column file would have saved a whole Kaggle session. Region derives from
  `review_id` (`bn_<raw row>`), so no extra input is needed.
- **The clustering is now scored against `region` as well as `Sentiment`, in the
  same table.** Deliberately not in a separate document: quoting either number
  alone misrepresents the result.
- **Region A gets its own config, not a modified one.** Seed, encoder, K,
  thresholds and all four bands identical — `tests/test_s2_region.py` asserts
  it — so the subset run is the same instrument pointed at less data. Output
  paths differ so the full-corpus result cannot be overwritten, and the
  embedding cache is forced off for restricted runs because it is keyed to the
  full corpus by row count.
- **K stays at 3 for region A although region A has two classes, and the
  weakness that creates is stated in the pre-registration rather than discovered
  afterwards:** ARI between a 3-way partition and a 2-class labelling is
  structurally capped below 1, so a low ARI there is *weaker* evidence than the
  same number on the full corpus. K = 2 registered as secondary.
- **Interpretation pre-registered before the run** (`protocol.md`, RQ1-A). The
  *decision* to analyse a subset came from seeing S2c and is exploratory in
  origin — said plainly there. What is fixed in advance is what each outcome
  will be taken to mean, which is the part that otherwise drifts to fit the
  number.

### Consequences for downstream steps

- The next Kaggle run produces both numbers at once; the notebook runs both
  configs and zips both sets of outputs.
- If `ARI(cluster, region)` exceeds `ARI(cluster, Sentiment)`, the full corpus is
  finished as a basis for persona claims and open decision 0b resolves itself.

### Citations needed

- None. Same K-Means and ARI, scored against a second grouping.

---

## 2026-07-30 — Scope settled: the full corpus, with region as a controlled factor

**Feeds:** Ch.1 §Scope, Ch.3 §Design, Ch.5 §Limitations · **Artifact:**
`docs/protocol.md` §"Scope decision" + RQ1-B · **Sabbir's decision.**

### The decision

Region A alone (1,910 rows, two classes) was the conservative option and was
declined. **The thesis runs on the full corpus.** Recorded as his call, with the
reasoning that follows written as conditions rather than attributed to him.

### Why this is defensible, and what makes it so

The full corpus is not the reckless choice — it is the *harder* choice, and it
buys three real things: n = 4,730 instead of 1,910; three sentiment classes
instead of two, so the three-persona design survives; and a cross-region
comparison that region A alone could not produce.

What makes it defensible is one rule: **region is carried explicitly through the
design, not hidden.** A confound that is measured, stratified on, and reported
is no longer a confound — it is a covariate. Pre-committed in `protocol.md`:
split stratified on `Sentiment × region` (6 strata), every headline metric
reported full / A / B in the *main* table, G-300 stratified on region with IAA
computed per region, and no claim allowed to survive that does not survive
within-region.

### Findings

- **A structure visible only across the full corpus, and absent inside both
  regions separately, would be made of the seam.** That is the specific failure
  mode the within-region rule exists to catch, and it is cheap to check once
  cluster assignments are persisted.
- **The cross-region generalisation test (RQ1-B) converts the problem into a
  measurement.** Train Verifier-A on one region, test on the other, both
  directions, against within-region baselines. Pre-registered with three
  outcomes at >15 / 5–15 / <5 point drops. All three are publishable and the
  largest drop is the most interesting — it would establish that the two corpora
  are not interchangeable for modelling, which nobody has reported for this
  dataset.

### The cost, stated plainly

Three things cannot be claimed on the full corpus regardless of any future
number, and they are listed in `protocol.md` so they cannot quietly lapse:

1. The corpus does **not** represent organic Bangla audience opinion — 60% has
   unknown provenance and a register no comment thread produces.
2. No prevalence or distribution claim (already excluded by fact (c)).
3. **If region B is machine-written — unresolved, open decision 0 — then a
   system generating audience reviews, trained and scored against it, is partly
   machine imitating machine.** This goes in Limitations *whatever* open
   decision 0 returns, because the thesis cannot currently rule it out.

Point 3 is the real price of the larger n. It is payable, but only in the open.

### Consequences for downstream steps

- The split map must stratify on `Sentiment × region`; it cannot be written
  until the S2 re-run persists cluster assignments (G-300 is cluster-stratified
  by the pipeline's own spec).
- Region A is retained as a **robustness check**, not the main line —
  `configs/s2_pilot_regionA.yaml` stays.
- New open decision 7: the design posits three personas, region A has two
  sentiment classes and region B three. The pipeline's G1 gate settles K from the
  master K-table rather than the label count, but the mismatch has to be faced
  before S3.

### Citations needed

- None yet. If RQ1-B becomes a headline result, the framing decision (open
  decision 5) covers where it is situated.

---

## 2026-07-30 — Provenance question closed: unresolvable, and that is the answer

**Feeds:** Ch.4 §Data quality, Ch.5 §Limitations · **Artifact:** STATUS facts
(collector-2) and (split) · **Nothing was computed.**

### What was asked and what came back

The collector was asked twice. First about the class-2 rows — answered "collected
the same way". Then, after the file's layout showed the pattern follows *row
position* rather than label, about rows 1999–4999. The answer:

> gathered from **many different places**, all organic user comments, none
> written or machine-generated, and **which rows came from where is not
> remembered — no metadata was kept**.

### Findings

- **"I don't remember" is the most useful answer available**, and it was
  pre-committed as a valid outcome in `provenance_query.md` before it was
  received. A guess would have entered the record and been falsifiable later; a
  refusal to guess leaves the record clean.
- **The account does not reconcile with the measurement, and is not forced to.**
  Many mixed sources would interleave registers throughout the file. The observed
  change is a step at one row: before it, 61% of rows carry no দাঁড়ি; after it,
  0.8% do. Sampling from many places does not produce that.
- **The likeliest reconciliation is collection in two sittings** — an initial
  batch, then more added later when the count fell short, months apart, with no
  log. That fits both the testimony and the file. But it is **inference, not
  testimony**, and is labelled as such in STATUS rather than folded into the
  collector's account.
- **Recall reliability is now itself evidence.** The same recollection stated
  "collected the same way" for a block the file shows was assembled separately.
  Fact (collector-2) is therefore recorded at **low** confidence — not as a
  judgement of the person, but because it has now been checked once against an
  artifact and did not match.

### Decisions made (and why)

- **The question is closed and will not be re-asked.** There is no venue, thread
  or timestamp column (fact (c)) and no collection log (fact (a)). A third round
  would produce recollection under pressure to supply an answer, which is worse
  evidence than none.
- **Both records are kept, unreconciled.** Fact (collector-2) states the
  collector's account in his words; fact (split) states what is measured. The
  thesis reports both and does not adjudicate. Deleting either would be the only
  dishonest move available here.
- **Nothing downstream stays blocked on it.** Waiting for an answer that cannot
  arrive is how a thesis stalls. The scope decision is made, the code is written,
  and the register split is handled as a controlled factor whatever its cause.

### Consequences for downstream steps

- Limitations must state that ~60% of the corpus has an **unrecoverable**
  provenance, and that the register split is measured but unexplained. That is a
  disclosable limitation, not a defect — many published corpora have worse and
  say less.
- The `machine-imitating-machine` risk (protocol.md, "what may NOT be claimed",
  point 3) **remains conditional and stays in Limitations**, because it cannot be
  ruled out. The collector denies it; the denial is recorded; neither settles it.

### Citations needed

- Possibly one on dataset documentation practice (datasheets / data statements)
  when Limitations is written — it would let the absent collection log be framed
  against an established standard rather than as an ad-hoc complaint. Sabbir's
  call at writing time; logged as open decision 5's neighbour, not decided here.

---

## 2026-07-30 — Plots: scraped, not hand-written (and that is the better method)

**Feeds:** Ch.3 §Data, Ch.5 §Limitations · **Artifacts:**
`src/preprocess/plots_scrape.py`, `configs/plots_scrape.yaml`,
`data/plots/README.md`, dataset-card §Plot synopses · **Sabbir's request.**

### The request, and why I stopped arguing for hand-collection

Sabbir asked for the 130 plots to be scraped. I had built the manual workflow an
hour earlier. On thinking it through, **the manual version was the worse method**
and not only the slower one:

- **Hand-written summaries put the experimenter's register into the inputs.**
  The thesis generates Bangla audience reviews *from these plots*, so the plot
  text is part of the experimental apparatus. 130 summaries in one person's voice
  is an uncontrolled variable at the top of every generation — and after spending
  the day proving that register differences dominate this corpus, seeding a new
  one deliberately would have been indefensible.
- **Hand-collection selects the films you think of**, which are the famous ones
  with the longest articles. Harvest-then-sample has no opinion about which films
  matter.
- **A paraphrase is checkable against nothing.** `source_url` + `revision_id`
  lets a reviewer fetch the exact text used.

So this is not a concession to speed. The earlier design was wrong.

### Decisions made (and why)

- **Harvest and sample are separate commands.** Harvest everything that passes
  the gate, then draw 130 blind with seed 42. Choosing which harvested films to
  keep, by eye, would reintroduce exactly the bias the scraping removes. The
  sampler refuses to run if the harvest is short, with a message saying to widen
  the categories rather than hand-pick the remainder.
- **Verbatim extraction, not paraphrase.** bn.wikipedia is CC BY-SA 4.0:
  reusable with attribution and share-alike. A paraphrase is a derivative work
  either way and loses the ability to point at a revision. Verbatim + revision id
  is both the more honest and the more citable choice.
- **Quality gate at 3–12 sentences, ≥120 chars, must contain Bangla.** Most
  bn.wikipedia film articles are stubs; harvesting unfiltered would yield a
  corpus of one-line plots nothing could be generated from. Over-length plots are
  **truncated at a sentence boundary rather than dropped** — a good long plot is
  not a bad plot.
- **Rate-limited to 1 req/s with a contactable User-Agent.** It is someone
  else's free server.
- **Categories deliberately broader than Bangladeshi cinema alone.** A set built
  only from recent hits would make the evaluation easier than the claim implies.

### Findings

- **Nine heading spellings are needed.** bn.wikipedia is inconsistent —
  কাহিনী / কাহিনি / কাহিনীসংক্ষেপ / পটভূমি / গল্প all occur. Matching is on the
  space-stripped heading. Verified against fixtures: all nine match, and
  সঙ্গীত / অভিনয়ে correctly do not.
- **A licence obligation now exists that did not before.** CC BY-SA attribution
  and share-alike are conditions of use. Recorded in the dataset card as a
  pre-publication checklist with three specific items, not a vague note.
- **The plot corpus will have better provenance than the review corpus** —
  complete, per-row, checkable against a revision. Worth stating in the thesis:
  it is the difference between a corpus assembled with a record and one
  assembled without, and today produced a live example of the cost of the latter.

### What is NOT verified

**The network path has never run.** The sandbox blocks bn.wikipedia, so
`discover()` and `harvest()` are untested against the real API — the first real
run is their first test. Tested offline against fixtures: section splitting,
heading matching across all nine spellings, sentence counting, boundary
truncation, and every quality-gate rejection reason.

Expected first-run failure modes: category names not matching bn.wikipedia's
exact strings, and `formatversion=2` response shapes differing from what the
parser assumes.

### Consequences for downstream steps

- The 26-working-day manual track is gone; the plot corpus stops being the
  critical path (STATUS parallel track downgraded 🔴 → 🟡).
- **A human read of the sampled 130 is still required.** The gate counts
  characters; it cannot tell a plot summary from a production-history paragraph
  that sat under a matching heading. Rejects are deleted from the harvest and the
  sample **redrawn**, never patched by hand — patching is hand-selection wearing
  a different hat.
- `plots_check.py` is kept: it validates the sampled output and owns
  `--assign-split`.

### Citations needed

- Wikipedia as a plot-summary source has precedent in the summarisation
  literature (e.g. the MPST-adjacent work already in the English arm). Worth a
  citation in Ch.3 when the data section is written — **Sabbir to confirm which**,
  since it should be a paper he has actually read.

---

## 2026-07-30 — First plot harvest: 67 of 130, and the shortfall was my fault

**Feeds:** Ch.3 §Data · **Artifact:** `results/plots_harvest_report.md`
**Ran on:** Sabbir's machine (the sandbox cannot reach bn.wikipedia)

### Numbers

| | |
|---|---|
| candidate articles discovered | **1,225** |
| passed the quality gate | **67** |
| rejected: no plot section | **1,148** |
| rejected: under 3 sentences | 5 |
| rejected: under 120 chars | 5 |

67 against a target of 130.

### Findings

- **1,148 rejections for "no plot section" is 94%, and that is not a corpus of
  stubs — it is a fault in my heading list.** bn.wikipedia's section wording
  varies far more than the nine exact strings I guessed: কাহিনী সংক্ষেপ,
  সংক্ষিপ্ত কাহিনী, কাহিনীর সারাংশ, গল্প সংক্ষেপ, প্লট are all in use. Exact
  matching against a list I invented was the wrong mechanism.
- **Two network faults surfaced before this, both mine.** A read timeout on a
  batch of 20 full extracts killed a run that had already fetched 1,225 articles,
  because nothing was checkpointed — the timeout was the trigger, the missing
  checkpoint was the defect. And `urllib` on Windows verified TLS against the
  system certificate store, which carries an expired root, while a current
  `certifi` bundle sat unused in the venv.
- **1,225 candidates is comfortably enough** for 130 if the extraction rate
  improves at all. The discovery step is not the constraint.

### Decisions made (and why)

- **Stem matching, with an exclusion list.** Exact headings are still tried
  first; failing that, a heading containing কাহিন / গল্প / সার / পটভূমি / প্লট /
  বিষয়বস্তু counts. Stems alone would over-match — নির্মাণ কাহিনী is a making-of,
  কাহিনী সূত্র is a source credit — so a heading also carrying a production or
  metadata term is vetoed. **Precision over recall on purpose:** a making-of
  paragraph passed off as a plot is a silently corrupted evaluation input,
  whereas a missed article costs one row out of 1,225.
- **The harvest now tallies the headings of everything it rejected**, top 25 into
  the report. If this still falls short, the next fix comes from the corpus
  rather than from me imagining more Bangla section titles. Guessing twice would
  have been the same mistake twice.
- **`--reset` added.** Processed titles are skipped on resume, so a heading-config
  change would otherwise have no effect — the run would cheerfully re-report 67.
- **Discovery widened**: depth 1 → 2 (most films sit in by-decade and by-genre
  subcategories, not the parent), cap 400 → 900, and the category that returned
  **+0 articles** replaced — its name was simply wrong. A category contributing
  nothing is printed per category, which is how that was visible at all.
- **TLS verification stays on.** Disabling it would have "fixed" the certificate
  error. This text becomes evaluation data; over an unverified connection the
  per-row `revision_id` — the entire reason for recording provenance — guarantees
  nothing.

### Consequences for downstream steps

- Re-run needed with `--reset`. If the yield still lands under 130, the report's
  heading tally names the next stems to add; failing that, widen the categories
  further. **Not** to be closed by hand-writing the remainder — that reinstates
  the two biases scraping was chosen to remove.
- The quality gate itself is barely rejecting anything (10 of 1,225), so it is
  not the constraint and should not be relaxed to make the number.

### Citations needed

- None. No method here, only extraction plumbing.

---

## 2026-07-31 — Second harvest: 110 of 130, and the tally earns its keep

**Feeds:** Ch.3 §Data · **Artifact:** `results/plots_harvest_report.md`

### Numbers

| | first harvest | **second** |
|---|---|---|
| candidates discovered | 1,225 | **2,820** |
| usable | 67 | **110** |
| rejected: no plot section | 1,148 | **2,690** |

Stem matching plus depth-2 discovery took the yield from 67 to 110. Still 20
short of 130.

### Findings

- **The 900-page cap was binding, and had been all along.** The three working
  categories returned **912 / 957 / 951** — all sitting on the cap rather than
  exhausting the category. Both harvests were silently discarding candidates.
  Raised to 6,000. A round number appearing three times should have been noticed
  the first time; it was in the output of run 1 and I read past it.
- **The heading tally paid for itself immediately.** The rejected articles are
  dominated by তথ্যসূত্র (221) and বহিঃসংযোগ (182) — stubs carrying nothing but
  references — plus কর্মজীবন, ব্যক্তিগত জীবন, চলচ্চিত্রের তালিকা, which are
  **person articles, not films**: actors and directors swept in by the film
  categories. So the misses are mostly genuine absence of plot sections, **and
  adding more heading stems would not have helped.** That is worth knowing from
  the corpus instead of from a third round of guessing.
- **`কাহিনী সংক্ষেপ` appears 8 times among the *rejected*.** Those articles have
  the heading but yielded no body — most likely level-3 subsections underneath it
  taking the text. Small (8 of 2,690) and not worth chasing yet, but recorded so
  it is not rediscovered later as a mystery.
- **Two category names in a row were ones I invented**, both returning +0. That
  is what `--find-categories` now exists for: it searches the Category namespace
  and prints each candidate's page count, so the config gets real names rather
  than plausible ones.

### Decisions made (and why)

- **Cap raised to 6,000 and `--find-categories` added, before deciding anything
  about the target.** The shortfall may simply be an artefact of the cap; there
  is no point debating whether 130 is reachable while the harvester is still
  throwing candidates away.
- **The quality gate is not being relaxed.** It rejected 20 of 2,820 — it is not
  the constraint, and loosening it to manufacture a number would trade real
  quality for an arbitrary target.
- **Not hand-writing the remainder**, even at 110 of 130. That reinstates both
  biases scraping was chosen to remove, and it would do so for the last 20 rows
  only — a corpus where 15% of items came from a different process, which is
  precisely the defect being documented in the review corpus this week.

### Consequences for downstream steps

- Re-run with `--reset`. If the raised cap does not close the gap, the remaining
  options are more categories (from `--find-categories`, not invention) or a
  **logged, deliberate reduction of the target** — the 30 dev / 100 eval split is
  a design choice from the pipeline, not a statistical requirement, and changing
  it is legitimate provided it is a recorded decision rather than a quiet
  accommodation.

### Citations needed

- None.

---

## 2026-07-31 — Third harvest: 132, and two of them are people

**Feeds:** Ch.3 §Data · **Artifact:** `results/plots_harvest_report.md`

### Numbers

| harvest | candidates | usable |
|---|---|---|
| 1 | 1,225 | 67 |
| 2 | 2,820 | 110 |
| **3** | **2,995** | **132** |

Rejects at harvest 3: 2,848 no plot section, 8 under 3 sentences, 6 under 120
chars, 1 over 2,000 chars.

### Findings

- **Raising the binding cap was the fix**: 110 → 132, over the target of 130.
- **Quality is good, and that was checked rather than assumed.** `পটভূমি` is the
  single most common heading (38 of 132) and could plausibly have meant
  "historical background of a real event" rather than the film's story. Six
  drawn at random — পালাবি কোথায়, ভটভটি, বাপি বাড়ি যা, মায়া, মন মানে না,
  এখানে রাজনৈতিক আলাপ জরুরি — are all genuine plot summaries. The heading is
  safe.
- **Two rows are biographies of people, not films.** `জীবনকাহিনী` pulled
  **অপর্ণা সেন** and `প্রারম্ভিক জীবন এবং পটভূমি` pulled **অনুস্মৃতি সরকার** —
  a director and an actress, swept in because bn.wikipedia's film categories
  contain people. Both passed every mechanical gate: Bangla, 3–12 sentences,
  over 120 characters. **Nothing except reading them would have caught this**,
  which is exactly why the README insists the sampled set is read.
- **132 − 2 = 130 exactly.** Zero slack, and the set has not been read yet.

### Decisions made (and why)

- **Whole-article veto for person articles**, not another heading exclusion. If
  an article carries কর্মজীবন / ব্যক্তিগত জীবন / চলচ্চিত্রের তালিকা anywhere,
  it is a person and is rejected outright. Stronger than vetoing one heading at
  a time: a biography is never a film plot regardless of what the section
  containing it is called, and the next such article will use a section name
  nobody has thought of. `জীবন` also added to the heading exclusions as a
  cheaper second line.
- **More harvest before sampling, not straight to `--sample 130`.** Landing on
  exactly 130 with zero margin means the first genuine reject during reading
  puts the set back under target, and the "blind sample of 130 from 132" is
  barely a sample at all. `--find-categories` first — the one category still
  returning **+0** has a name I invented, and fixing it is free candidates.

### Consequences for downstream steps

- Reading the sampled set remains mandatory and is now demonstrably not a
  formality: the mechanical gate passed two biographies.

### Citations needed

- None.

---

## 2026-07-31 — Fourth harvest: 124, and the number going *down* is the good news

**Feeds:** Ch.3 §Data, Ch.5 §Limitations · **Artifact:**
`results/plots_harvest_report.md`, `docs/protocol.md` (Deviations)

### Numbers

| harvest | candidates | usable |
|---|---|---|
| 1 | 1,225 | 67 |
| 2 | 2,820 | 110 |
| 3 | 2,995 | 132 |
| **4** | **3,135** | **124** |

Harvest 4 rejects: 2,925 no plot section, 15 under 3 sentences, 6 under 120
chars, **65 person articles**.

### Findings

- **132 was never really 132.** The person-article veto rejected 65 articles, and
  **8 of them had been counted as usable** in harvest 3. Reading headings by eye,
  I had found only 2 (অপর্ণা সেন, অনুস্মৃতি সরকার) — the other 6 were
  biographies hiding under `পটভূমি` or `কাহিনী`, indistinguishable from a film
  plot by heading alone. So the count went 132 → 124 because it got **more
  honest**, not worse.
- **The eyeball check caught 25% of the problem.** That is the argument for the
  structural veto over inspection, and worth remembering the next time a
  spot-check feels sufficient.
- **`বাংলাদেশের স্বাধীনতা যুদ্ধের চলচ্চিত্র` contributed +0** — not a wrong name
  this time: its 84 films were already reached through the other categories.
  `+0` means "no *new* articles", which is different from "does not exist", and
  the two look identical in the output. Worth distinguishing if this is ever
  extended.
- **bn.wikipedia does not contain 130 Bangla films with usable plot sections.**
  Four harvests establish that; it is a property of the source, not of the
  harvester.

### Decisions made (and why)

- **Target follows the data: 30 dev + ~94 eval, floor of 80.** Logged as a
  deviation in `protocol.md` **before** the number is used. `N_DEV` stays at 30
  because the dev slice tunes the loop threshold; eval takes the remainder.
- **Both routes to 130 were available and both were refused.** Relaxing the
  quality gate would have admitted two-sentence plots — but the gate rejected
  only ~20 of 3,135, so it is not the constraint, and thin plots are poor
  generation inputs. Adding the by-year categories would have overshot 130
  easily — but they are language-neutral, and Tamil or Hindi films described in
  Bangla would have **passed every check in this harvester** while making the
  plot corpus stop being Bangla cinema. Nothing downstream would have noticed.
- **`plots_check` now refuses to split below 80 eval**, with a message naming
  both shortcuts so a future run cannot take them absent-mindedly.

### Consequences for downstream steps

- S6 runs on ~94 eval plots rather than 100. Bootstrap CIs absorb that; the
  Limitations section states it.
- The set still has to be **read** before the split is frozen. The veto is
  structural and will not catch a production-history paragraph that happens to
  sit under `কাহিনী`.

### Citations needed

- None.

---

## 2026-07-31 — Plot corpus FROZEN: 120 = 30 dev + 90 eval

**Feeds:** Ch.3 §Data · **Artifacts:** `data/plots/plots_bn.csv` (committed,
frozen), `data/plots/rejected_by_review.csv`

### Numbers

| | |
|---|---|
| harvested | 124 |
| rejected on human review | **4** |
| **frozen set** | **120** — 30 dev / 90 eval, seed 42 |
| sentences | min 3, median 9, max 12 |
| provenance | 120/120 carry `revision_id`; licence CC BY-SA 4.0 throughout |

### The four rejections, and who caught what

| id | film | reason | found by |
|---|---|---|---|
| BN024 | আদম সুরত | production history — funding, cinematographer changes, how the director met his wife. No plot at all, and it is a documentary. | both |
| BN042 | কাগজের ফুল | the director's fatal road accident and a prime-ministerial statement. The film was never finished. | screen |
| BN068 | দহন (১৯৮৫) | commentary *about* the story's themes, not the story. Says what it is about, never what happens. | screen |
| BN113 | শঙ্খবেলা | a 3-sentence fragment that sets up and stops — passed the minimum exactly | **Sabbir** |

### Findings

- **The two review methods caught different things, and neither was
  sufficient.** My keyword screen flagged 9 candidates, of which 5 were false
  positives — BN087 বাঁশি trips on "নির্মাণ" because *the protagonist's dream is
  to make a film*, which is the plot. It found the three that are structurally
  not plots. It could not have found BN113, which is a real plot that simply
  stops; only reading it does that. Sabbir's read caught BN113 and BN024.
- **BN113 is the argument for human review in one row.** It passed every
  mechanical gate — Bangla, exactly 3 sentences, over 120 characters, no
  biography section — and it is unusable, because nothing happens in it.
- **The 3-sentence floor is doing less work than it appears.** BN113 sat exactly
  on it. Not changing the gate after the fact, but worth knowing that "3
  sentences" and "a usable plot" are not the same predicate.

### Decisions made (and why)

- **BN072 দ্য নেমসেক kept — Sabbir's decision.** It is a complete, well-written
  plot summary, but the film is Mira Nair's English-language American
  production, in bn.wikipedia because its subject is a Bengali immigrant family.
  I recommended dropping it as outside "Bangla cinema"; Sabbir chose to keep it,
  which settles the scope question in favour of the broader reading. **Recorded
  as his call, and my dissent recorded as fact rather than argued further** — but
  it means the plot corpus contains one non-Bangla-language film, and that
  should be stated if the corpus is described as Bangla cinema without
  qualification.
- **Rejections removed from the HARVEST, not from the sample**, then re-sampled.
  Deleting from `plots_bn.csv` would have left the harvest holding items already
  judged unusable, ready to be drawn again.
- **Logged to `rejected_by_review.csv`** rather than vanishing: what a reviewer
  saw and refused is part of how this corpus was built.
- **Split frozen at 30 dev / 90 eval, seed 42.** `plots_check` now refuses to
  reassign it.

### Consequences for downstream steps

- S6 runs on **90 eval plots** against the spec's 100. Deviation logged
  2026-07-31; bootstrap CIs absorb it; Limitations states it.
- **The plot corpus has complete per-row provenance** — URL, revision id,
  timestamp, licence — which the review corpus does not. Worth the contrast in
  Ch.3: one corpus assembled with a record, one without, in the same thesis.
- **CC BY-SA attribution is now an outstanding obligation**, not a future one:
  the dataset card carries a three-item checklist that must be discharged before
  submission.

### Citations needed

- Still open (decision 5's neighbour): whether Wikipedia-as-plot-source gets a
  citation in Ch.3. Sabbir to pick a paper he has read.

---

## 2026-07-31 — The decisive run: the clusters are a corpus detector

**Feeds:** Ch.4 §Persona discovery, Ch.5 §Threats · **Artifacts:**
`results/s2_pilot_ari_trapcheck.md`, `results/s2a_regionA_trapcheck.md`,
`results/s2_cluster_assignments.csv` · **Ran on:** Kaggle T4

### Numbers — full corpus, primary threshold 0.95, n = 4,625

| Scored against | ARI |
|---|---|
| `Sentiment` | 0.1793 |
| **`region`** | **0.4813** |

Cluster × region:

| Cluster | A_organic | B_uniform |
|---|---|---|
| 0 | **1,700** | 114 |
| 1 | 119 | **1,308** |
| 2 | 78 | **1,306** |

Cramér's V = **0.8610**. Region is binary while K = 3, so the three-way ARI is
structurally capped; merging the two region-B clusters gives the undistorted
comparison: **ARI = 0.7487, φ = 0.8607, and the clustering identifies which
corpus a review came from with 93.3% accuracy.**

Consistent across every threshold: ARI(region) 0.5943 / 0.4813 / 0.4799 at
0.90 / 0.95 / 0.98, against ARI(Sentiment) 0.2181 / 0.1793 / 0.1784.

### The pre-registered outcome fires

`protocol.md` RQ1-A, Test 1, written on 2026-07-30 before this run existed:

> `ARI(cluster, region)` > `ARI(cluster, Sentiment)` → the encoder recovers
> **which file a review came from** more strongly than what it says. **No
> persona claim may rest on the full-corpus clustering.**

0.4813 > 0.1793, by a factor of 2.7, at every threshold. **The condition is met
and there is nothing to negotiate** — which is the entire reason it was written
down in advance.

So the three clusters found on 2026-07-30, and read then as candidate audience
personas, are **not personas**. They are the seam in the file. LaBSE was
separating two corpora with 93.3% accuracy while appearing to do persona
discovery.

### Region A alone — n = 1,897, not degenerate

Cluster shares 29.5 / 38.9 / 31.6, comfortably inside the 5–70% band, so the
number is interpretable. **ARI = 0.1804 → Band 1, NOT_SENTIMENT_ALIGNED**,
constant across all four threshold rows.

But the crosstab has to be read alongside it:

| Cluster | Sentiment 0 | Sentiment 1 | |
|---|---|---|---|
| 0 | 64 | 496 | 89% positive |
| 1 | 396 | 342 | **54 / 46 — mixed** |
| 2 | 484 | 115 | 81% negative |

Cramér's V = **0.5455**, *higher* than the full corpus's 0.4104. The clusters
are strongly sentiment-ordered — negative-leaning, mixed, positive-leaning —
and ARI is low largely because **a three-way partition cannot align with a
two-class label**. That structural cap was written into the RQ1-A
pre-registration precisely so it could not be discovered now and used as a
convenient explanation.

**So Band 1 here is a weaker result than Band 1 on the full corpus was.** The
pre-registered claim ("the persona programme may proceed on region A") holds,
but only in its literal form: the clusters are not a *rediscovery* of the
sentiment partition. They are visibly sentiment-*correlated*, and whether
cluster 1 — the mixed one — is an audience persona or simply the ambivalent
reviews is exactly what G-300 has to settle. It cannot be settled from here.

### Findings

- **The 2026-07-30 reading of S2 was wrong, and the instrument that corrected it
  was built the same day.** Persisting cluster assignments cost one CSV column
  and turned an unanswerable question into a two-minute one.
- **93.3% corpus-detection accuracy is itself a reportable finding.** No
  published work on this dataset reports that its two halves are separable at
  all, let alone by an off-the-shelf multilingual encoder with no supervision.
- **V rose when the confound was removed** (0.4104 → 0.5455). The register split
  was *suppressing* the sentiment signal on the full corpus by dominating the
  first axis.

### Decisions made (and why)

- **Persona discovery moves inside region A.** The full corpus stays — Sabbir's
  scope decision — but the pre-committed rule that no claim survives unless it
  survives within-region is now load-bearing rather than precautionary.
- **Nothing is re-run to look better.** The full-corpus trap-check stands as
  computed and is reported as confounded, with the region table beside it.
- **K remains an open question, not a settled one.** Region A has two sentiment
  classes and the K-Means K = 3 was inherited from the persona design. The
  pipeline's own G1 gate settles K from the master K-table; that gate has not
  run yet, and this result makes it more important, not less.

### Consequences for downstream steps

- **Gold-300 stratification must be drawn from the region-A clustering**, not the
  full-corpus one. Had the annotation been done a week earlier, 300 items would
  have been stratified on a corpus detector.
- The split freeze can now proceed: cluster assignments exist for both.
- Ch.4 gains a result it did not have: an encoder recovering dataset provenance
  from text alone.

### Citations needed

- The corpus-detection result may want a pointer to the dataset-artefact /
  shortcut-learning literature when written up. **Sabbir's call** — open
  decision 5 covers the framing.

---

## 2026-08-01 — Consistency sweep: Sabbir was right, the docs had drifted

**Feeds:** all chapters (these are the normative documents) · **Artifacts:**
`docs/research_pipeline_en.md`, `docs/dataset_card.md`, `docs/protocol.md`,
`results/s2b_register_probe.md`, artifact index in `STATUS.md`
**Prompted by:** Sabbir — *"onk kichui updated nai folder gulo te maybe"*

### Numbers

No new computation. Four documents were carrying refuted figures.

### Findings — four defects, all mine

- **`results/s2b_register_probe.md` had no forward pointer.** Read alone, it says
  class 2 is a different kind of text *because it is class 2*. That is the exact
  mistake `s2c` corrected: every class-2 row sits in the second corpus, and rows
  3665–4330 are labelled **0** with the same signature. Anyone opening that file
  first — a supervisor, an examiner — would have taken away the wrong finding.
- **`docs/research_pipeline_en.md`, the normative spec, still said `usable ≈
  4,722` and `130 plots / 30 + 100`, and contained ZERO mentions of the region
  split.** The largest finding of the week was absent from the document that
  defines the design. `CLAUDE.md` says the pipeline wins on method — so a
  pipeline that does not know the corpus is two corpora is a live trap, not a
  stale note.
- **`docs/dataset_card.md`** still described the plot corpus as n = 130,
  30 dev / 100 eval.
- **`docs/protocol.md` RQ2 still specified 100 eval-plots** — a *live* spec line,
  not a historical record — and the plot deviation quoted the pre-review estimate
  (~124 / ~94) rather than the frozen 120 / 90.

- **Three result files were orphaned**: on disk, referenced from nothing. One was
  `s2a_regionA_cluster_assignments.csv` — **the file G-300 stratification must be
  drawn from.** A result nobody can find is a result nobody can check.

### Decisions made (and why)

- **The s2b banner went into the report TEMPLATE, not the file.** Editing the
  generated markdown by hand would have been undone by the next re-run — which is
  how a warning quietly disappears. The report was regenerated to prove it
  survives.
- **Strikethrough, not deletion, in the pipeline spec.** `~~4,722~~ 4,730` with
  the reason attached, so the original claim and its refutation are both
  readable. A number that silently changes cannot be audited, and the corrections
  themselves are a finding.
- **Historical numbers in this notebook and in the deviations log left
  untouched.** Recording what was believed at the time is what those files are
  *for*; "fixing" them would destroy the record of how the understanding moved.
  The rule applied: correct the **normative** documents, preserve the
  **historical** ones.
- **Artifact index added to STATUS**, covering all 14 files in `results/` with
  their standing — current, superseded, or parked.

### Findings (about process, not data)

- **The drift was invisible from inside the work.** Six days of appending to
  STATUS and the notebook, and neither I nor the pre-commit hook noticed the
  spec had gone stale — the hook checks that reasoning accompanies results, not
  that the design document still matches reality. Sabbir noticed by looking at
  the folder. Worth repeating this sweep at each phase boundary rather than
  waiting to be asked.

### Consequences for downstream steps

- The spec now carries the region split, so S2/S3 instructions inside it
  (persona discovery on region A, G-300 stratified on the region-A clustering)
  are correct where someone would actually read them.
- S6's scale drops from 2,400 to **2,160 generations per language** (90 eval
  plots, not 100), corrected in both the spec and the protocol.

### Citations needed

- None.

---

## 2026-08-01 — Split FROZEN. Phase 1 is closed.

**Feeds:** everything downstream · **Artifact:**
`data/splits/split_map_v1.json` (committed, frozen)

### Numbers

| Part | n | region A / B | Sentiment 0 / 1 / 2 |
|---|---|---|---|
| **G** (gold, eval-only) | **300** | 123 / 177 | 96 / 102 / 102 |
| **R1** (Verifier-A + RAG) | **2,162** | 886 / 1,276 | 694 / 733 / 735 |
| **R2** (Verifier-B) | **2,163** | 888 / 1,275 | 694 / 734 / 735 |
| dev (⊂ R1) | 200 | 82 / 118 | 64 / 68 / 68 |

Built over the **4,625** rows surviving near-duplicate removal at t = 0.95 —
**not** over `bn_clean.csv`'s 4,730. A split defined on the pre-dedup set could
put a near-duplicate pair on opposite sides of the R1/R2 wall, which is a leak
that looks like nothing.

Verified independently of the writing script: every part matches the corpus on
both region and sentiment to **within 0.1 percentage points**, zero overlap
between any two parts, union covers the input exactly, dev ⊆ R1.

### Decisions made (and why)

- **Stratified on `Sentiment × region`, not on cluster** — a departure from
  pipeline §A, logged in `protocol.md`. The cluster instruction predates the
  finding that the full-corpus clustering is a **corpus detector**; stratifying
  the gold set on it would stratify on a file seam. And Gate G1 has not run, so
  a cluster-stratification would go stale the moment K changes.
- **The 300 gold ids are fixed now, even though the persona scheme is not.**
  Which items are held out, and what they will eventually be annotated *for*,
  are separate questions. Fixing the ids now is what makes "G never enters
  training" true from this moment rather than from whenever the scheme settles.
- **The script refuses to overwrite the map.** The override flag is
  deliberately unwieldy (`--i-am-recreating-the-split-and-i-know-why`) and
  stores the stated reason inside the new map.
- **The map carries its own contract** — `_contract` and `_provenance`
  (including the SHA-256 of the input) live inside the JSON, so a reader who
  opens only that file still learns that G is eval-only and why R2 exists.
- **`tests/test_split_map.py` pins the invariants permanently**, not just at
  creation. Verified by corrupting a copy: leaking 5 R1 ids into R2 fails with
  the reason named.

### Findings

- **Nothing else in this repo would notice a broken split.** The verifier would
  train, the loop would run, the numbers would look plausible. That is why the
  invariants live in a test rather than only in the script that ran once.
- **The Open-decisions table below had lost its header row** to one of my
  earlier edits — the rows were orphaned under a `### Citations needed`
  heading. Repaired here. Small, but it is the second formatting casualty of
  editing these files programmatically, after the notebook cell.

### Consequences for downstream steps

- **Phase 1 is complete.** Data prepared, corpus characterised, plot corpus
  frozen, split frozen.
- S4 can begin: R1 → Verifier-A, R2 → Verifier-B, dev for the τ sweep.
- G-300 annotation still waits on the persona scheme (Gate G1), but the
  **identity** of the held-out 300 is settled and unarguable.

### Citations needed

- None.

---

## 2026-08-01 — Repo tidy: what was dead, and what only looked dead

**Feeds:** repo hygiene · **Prompted by:** Sabbir — *"oproyojonio gulo jeno batil hoy"*

### Removed

- **5 redundant `.gitkeep` files** — `data/plots/`, `data/raw/`, `data/splits/`,
  `notebooks/`, `results/` all hold real tracked files now, so the placeholders
  were doing nothing. `data/cleaned/.gitkeep` **kept**: that directory is
  gitignored by design (derived data), so without it the directory does not
  exist in a fresh clone and every script that writes there fails.
- **`data/plots/plots_bn_template.csv`** — dead since the corpus became scraped
  rather than hand-entered. Its only remaining reference was an error message in
  `plots_check.py` telling the user to copy it, which was actively wrong advice:
  `plots_bn.csv` is now **frozen and committed**, so a missing copy must be
  recovered from git history, not regenerated. A re-harvest would produce a
  different set and silently invalidate the frozen split. Message rewritten to
  say so.

### Kept, deliberately

- **`src/agents/`, `src/eval/`, `src/verifier/`** — `__init__.py` only. They are
  Phases 3–5 of the declared layout, not clutter. Marked as empty in the README
  so nobody goes looking for code that was never written.
- **`results/s2_threshold_audit_{sheet,key}.csv`** — generated, never annotated.
  Parked rather than deleted: the 0.90-vs-0.95 question is still live in
  principle, and the sheet is blinded and reproducible. Marked ⏸ in the STATUS
  artifact index so its standing is explicit.
- **`results/s2b_register_probe.md`** — superseded framing, correct
  measurements. Kept with a banner, because a superseded claim that disappears
  is one nobody can audit.
- **`docs/legacy/`** — the pre-defence report and conference draft. Source
  material; they are what the pipeline was built from.

### Also corrected

- **`README.md` still said "Phase 0 — setup. No experimental results yet."**
  Six days and the entire S2 result later. Now states Phase 1 complete, points
  at STATUS as the source of truth, and leads with the corpus-detector finding —
  because anyone opening this repo needs that before they read anything else.
- **The README repeated the `core.autocrlf=true` claim** that `.gitattributes`
  had already been corrected for. Both now say it is unset, and why that
  mattered.
- **Hook mode verified `100755`** in the index — the README warns that a plain
  `git add` can silently drop the executable bit and disable the check without
  any warning. It has not.

### Findings

- **Two of the three stale documents were the ones a newcomer reads first**
  (`README.md`, and the pipeline spec earlier today). The files that get updated
  are the ones being worked in; the entry points rot precisely because nobody
  working on the project needs to read them.

### Consequences

- 80 tracked files → 74. Nothing that had a reader was removed.
- All 40 tests pass and all 13 modules import after the cleanup.

---

## 2026-08-01 — Base paper 1/5 read: Huang et al. bites on our ablation table

**Feeds:** Ch.1 §1.1(2), Ch.2, RQ2 motivation, **§5.1 ablation design**
**Artifacts:** `docs/related_work.md` (entry filled), `docs/references.bib`
**Read by:** Claude. **Not by Sabbir** — recorded on the entry itself.

### What the paper actually claims

**Intrinsic** self-correction — *"without any external or human feedback"* (§2)
— fails on reasoning benchmarks and often degrades performance. Every intrinsic
number in Tables 3–4 is at or below its standard-prompting baseline. Llama-2-70b
on GSM8K: **62.0 → 43.5 → 36.5** over two rounds. GPT-4 on GSM8K:
**95.5 → 91.5 → 89.0**. The oracle-label rows do improve (GPT-3.5 GSM8K
75.9 → 84.3), and §3.2 argues those *"can only be regarded as indicative of an
oracle's performance"* — if you hold the ground truth, why run the model.

Their diagnosis (§3.3): the model keeps its first answer 74.7% of the time on
GSM8K, and among the rest is **more likely to turn a correct answer into an
incorrect one** than the reverse, because *"LLMs cannot properly judge the
correctness of their reasoning."*

### Findings

- **The paper endorses our approach by name.** §6 "Leveraging external feedback"
  says that when valid external feedback exists it should be used, and cites
  **Cobbe et al. 2021**, Lightman et al. 2023 and Wang et al. 2023b for
  *"train a verifier or a critique model … to verify or refine LLM outputs"*.
  That is this thesis. **Huang et al. is not an obstacle to route around — it is
  the paper that names our direction as the promising one.** The pipeline called
  it a "theoretical anchor", which undersells it.
- **It does not test our setting.** Reasoning benchmarks only; no generation
  task, no persona control, no low-resource language. Writing "Huang et al.
  proved LLMs cannot self-correct, therefore we use an external verifier" would
  be an overstatement an examiner who has read it will catch. Safe wording is in
  the entry.
- **§4 and §5 bite on our ablation table, and this is the real return on
  reading it.**
  - §4: multi-agent debate at 9 calls scores **83.0** against self-consistency's
    **88.2**. What looks like "critique" is selection across generations.
  - §5: a reported Self-Refine gain came from stating the requirement *only* in
    the feedback prompt. Move it into the initial prompt and standard prompting
    wins: **81.8 vs 75.1**.
  - §6 asks that self-correction be compared against baselines **of comparable
    inference cost**.

  Our §5.1 table has rows 1–3 single-call and rows 4–8 looping, no
  self-consistency baseline at all, and no cost column. **"Row 6 beats row 1"
  is currently open to exactly the objection this paper makes.** Raised as
  open decisions 9 and 10 rather than acted on — §5.1 is pre-registered and
  changing it is Sabbir's call.

### Decisions made (and why)

- **The entry records who read it.** The file's own rule is *"filled when read,
  never from an abstract alone"*. The content rule is satisfied — full text, v2,
  with section and table numbers throughout — but the *reader* is not the person
  who will be examined on it. Marking that is the honest move; quietly filing it
  as read would leave a landmine in the viva.
- **Section and table numbers are attached to every claim**, so the whole entry
  is checkable in under an hour rather than taken on trust.
- **Three follow-up papers logged**: Wang et al. 2022 (self-consistency, needed
  for the baseline in decision 9), Madaan et al. 2023 (Self-Refine — the closest
  thing to our loop *without* a trained verifier), and Cobbe et al. 2021 moves
  from "background" to load-bearing.

### Consequences for downstream steps

- Open decisions **9** and **10** must close before S6 runs. Both concern the
  headline comparison; discovering them after 2,160 generations would be
  expensive.
- `references.bib` existed but was **empty** — first entry added.

### Citations needed

- Done for this paper: `huang2024selfcorrect` in `references.bib`, key matching
  the `related_work.md` heading as the file requires.

---

## 2026-08-01 — All six base papers briefed. Three of them change the design.

**Feeds:** Ch.1, Ch.2, **§5.1 ablation** · **Artifacts:**
`docs/base_papers_brief.md`, `docs/references.bib` (6 entries)
**Read by:** Claude. Sabbir has read none — stated at the top of the brief.

### Depth, stated honestly

One paper read in full (Huang et al. — section and table numbers throughout).
Five read at **abstract + bibliographic record** only. Every claim in the brief
is tagged 📗 or 📙 so a reader knows which is which, and three papers are marked
⬛ *"needs full text before it can carry weight in Ch.2"*.

That is not ideal and the brief says so. But an abstract-level brief that is
**labelled** as abstract-level is honest and useful; an abstract-level brief
presented as a reading is the thing that gets someone destroyed in a viva.

### Findings — each of these changes something

- **Kamoi et al. is the other half of Huang.** Huang shows intrinsic correction
  failing; Kamoi's survey concludes that *"self-correction works well in tasks
  that can use reliable external feedback"*. Together: **the problem is the
  judge, and externalising it is the known fix.** Their finding (1) — no prior
  work shows successful correction from *prompted-LLM* feedback — also predicts
  our ablation row 7 will lose, which makes it the right headline baseline.
  They also publish an **experiment-design checklist** for exactly this kind of
  study; it should be run against §5.1 before S6.
- **The Self-Correction Illusion (2026) is the most dangerous paper in the
  list.** Holding a claim byte-identical (SHA-256 verified) and changing only
  the chat-template role that carries it lifts correction rates by **23–93
  percentage points**. Their conclusion: the failure to self-correct *"is not a
  cognitive deficit; it is a chat-template artifact"*, and they build a
  **training-free** intervention on it. It supports our framing — external
  presentation is what unlocks correction — **and simultaneously offers a free
  competitor to our trained verifier.** → open decision 11 proposes row 7b:
  self-critique wrapped in an external role. If 7b ≈ row 6, the verifier is not
  earning its cost, and **that is a negative result we would much rather find
  ourselves than have a reviewer find.**
- **Sands et al. is the closest existing work to our S6**, and their stated
  gap — *"a noticeable gap in emotional richness and stylistic coherence"* —
  is precisely what a verifier-in-the-loop targets. Their finding that **GPT-4o
  overemphasises positive emotions** is a direct warning for generator choice
  and for our persona-mix sanity check. Also worth noting: they feed the model
  **subtitles and screenplays**, which exist only *after* a film is made. Ours
  is a **pre-release** setting where a synopsis is all there is — harder, and a
  more honest framing.
- **Two pipeline claims about MoP are unverified.** It is cited as *"Findings of
  ACL 2025"*; the arXiv record shows **no venue at all** (v1, 7 Apr 2025). And
  the pipeline says it *"uses IMDB/SST-2"*; the abstract names no dataset.
  Recorded in `references.bib` as a comment above the entry, and cited as arXiv
  until a published version is confirmed.
- **Cobbe et al. is load-bearing, not background.** Huang §6 points at *this
  paper* as the alternative to intrinsic correction. One honest difference to
  state: **their verifier ranks (best-of-N); ours gates and refines in a loop.**
  Best-of-N is also exactly the cost-matched baseline open decision 9 needs — so
  the baseline and the ancestor are the same paper.

### A near-miss worth recording

I first read Sands et al. as **"Chandra et al."**, because the bibliographic
metadata lists the corresponding author last and that was the name in
`citation_author`. I was one step from "correcting" a citation in the pipeline
that was **already right**. The article page's author list settled it: Brendan
Sands is first, Chandra is last. Recorded in the brief so Sabbir checks me the
same way — metadata is not the paper.

### Decisions made (and why)

- **A separate `base_papers_brief.md` rather than six long `related_work.md`
  entries.** `related_work.md` stays the register of record, structured for
  assembling Ch.2. The brief is the thing you read on a phone before a
  supervision meeting. Different jobs, different files.
- **Depth tagged per paper, and the three that need full text marked.** The
  temptation is to write six entries of uniform confidence; the honest version
  is uneven and says where it is thin.
- **`references.bib` now has all six**, with `note` fields recording reading
  depth and the MoP venue caveat carried as a comment in the file itself.

### Consequences for downstream steps

- **Three open decisions (9, 10, 11) now sit against a pre-registered ablation
  table**, all from six papers' worth of reading. Each is a config edit today
  and an unrepeatable experiment after S6.
- Ch.2's gap sentence is now writable: no prior work does persona-controlled
  review generation with an external trained verifier in a low-resource
  language, and the closest work (Sands) names the exact weakness we target.

### Citations needed

- All six are in `references.bib`. Keys match the `related_work.md` headings, as
  that file requires.

---

## 2026-08-01 (later) — Deeper reads. Kamoi hands us a gap sentence.

**Feeds:** Ch.1, Ch.2, §5.1 · **Artifact:** `docs/base_papers_brief.md` (rewritten)
**Depth now:** Huang 📗, Kamoi 📗, Illusion 📗, MoP 📘 partial, Sands 📙, Cobbe 📙

### Findings

- 🎁 **Kamoi §5.2 states our gap for us:** *"Fine-tuning enables self-correction
  when large training data is available but is **unexplored for small training
  data**."* Our verifier trains on **R1 = 2,162 rows**. A TACL survey naming our
  exact regime as unexplored is a stronger Ch.1 sentence than anything we could
  have argued ourselves — and we would not have found it from the abstract.
- **Kamoi's Table 1 gives us a placement problem worth solving deliberately.**
  Their taxonomy is Intrinsic / Oracle / Fair-Asymmetric / Unfair-Asymmetric /
  **Cross-Model**, and REFINER and RL4F — a large LM paired with a trained T5
  feedback model — sit under Cross-Model as the closest structural analogue to
  ours. We should classify ourselves in Ch.2 before a reviewer does it for us.
  The asymmetry axis matters too: if our verifier sees information the generator
  never had, that is *asymmetric* and must be disclosed.
- **The Illusion paper's fourth control is the one that matters to us.** Their
  **self-distrust control** — instructing the agent to verify its own thoughts —
  yields **0–23%** correction against **70%** for the role relabel. So naive
  self-distrust is not a substitute for external presentation, and our row 7 is
  predicted to lose for a *mechanistic* reason rather than an empirical accident.
  Their **within-thought duplication control** (+6.7 pp, p=0.26) further isolates
  a **+46.7 pp pure role-tag effect** — it is not "the model saw it twice".
- ⚠️ **But their lifts are measured on a *failure pool*** — tasks pre-selected
  for having already failed intrinsic correction. That concentrates power on the
  target regime and it means the 23–93 pp figures are on a selected subset. Must
  be stated that way whenever we cite them.
- ✅ **MoP does not validate its personas — confirmed from the paper's own
  section list.** §4 contains only Steerability, Synthetic Data Generation,
  Transferability and Ablations, plus §7 Limitations. **No human-evaluation
  section exists anywhere.** Contribution ① stands. Their formalism is
  p(y|x) = Σₖ πₖ·p_LM(y|gₖ,x), with a second level weighting in-context
  exemplars — and **our RAG over R1 is arguably that same exemplar level**,
  which is worth saying in Ch.2 rather than leaving a reviewer to notice.

### What could not be read, and why

**MoP §4.1** — datasets, whether they report MAUVE, and how they choose K. The
arXiv HTML renders that section behind MathML markup that costs more to parse
than the content is worth; the PDF will be readable. Marked ⬛ rather than
guessed. This also leaves the pipeline's *"uses IMDB/SST-2"* claim unverified,
alongside its unverified *"Findings of ACL 2025"* venue.

**Sands and Cobbe** remain 📙 abstract + record. Sands is open access and its
abstract is unusually specific; Cobbe has no arXiv HTML.

### Decisions made (and why)

- **Depth tagged per paper in the brief, with three ⬛ marks for what still needs
  the PDF.** The temptation with six papers is to write six sections of uniform
  confidence. The honest version is uneven and says where it is thin.
- **`related_work.md` entries updated to `[~]` with the substantive findings**,
  and the brief carries the numbers. Two files, two jobs: the register stays
  structured for assembling Ch.2, the brief is readable in one sitting.
- **MoP's heading now carries "⚠️ venue unverified"** in the register itself, so
  the wrong venue cannot be copied into a bibliography from this file.

### Consequences for downstream steps

- Ch.1's gap paragraph now has a citable sentence (Kamoi §5.2) rather than an
  argument we have to construct.
- Ch.2 owes a taxonomy placement (Kamoi Table 1) and an explicit comparison of
  our RAG layer to MoP's exemplar layer.
- Open decisions 9, 10, 11 stand; nothing in the deeper reading weakened them,
  and the Illusion controls strengthened 11.

### Citations needed

- All six in `references.bib`, keys matching the register headings.

---

## 2026-08-01 — MoP entry closed from the PDF. It hands us contribution ②.

**Feeds:** Ch.2, **Gate G1 design** · **Artifact:** `docs/related_work.md`
(`mop2025` now `[x]`)

### Why this one section was read before starting G1

Of the three outstanding reading gaps, only MoP's **K-selection method** touches
the next code step. If the closest competitor had a principled way of choosing
K, we would want to know it before running our own K-table rather than after.
The arXiv HTML buried §4.1 in MathML; **the PDF is clean** and answered
everything in one section.

### Findings

- **🔑 MoP does not select K. It is fixed at 100 by hand.** §4.1: *"we choose the
  number of personas to be 100 … We then run K-Means and the persona synthesizer
  to extract 100 persona descriptions."* No K-table, no stability analysis, no
  criterion, no sensitivity check. **Our Gate G1 — seven criteria, bootstrap ARI,
  prediction strength — is therefore contribution ②**, sitting beside human
  validation as contribution ①.
- **And the granularity differs conceptually, which Ch.2 must say plainly.** They
  model a population as **100 micro-personas**; we model **3 audience types**.
  These are not the same object at different K. Pretending otherwise would
  invite a reviewer to point it out.
- **🔑 Their ablation predicts something about ours.** Removing exemplars is far
  more damaging than removing the persona synthesiser: MAUVE 0.871 → **0.552**
  versus → 0.807. **The exemplars carry most of the benefit, not the persona
  descriptions.** Our RAG layer is structurally their exemplar layer, so this
  predicts row 3 (RAG only) may beat rows 1–2 (persona prompting) by more than
  we assumed — and it validates keeping them as separate ablation rows.
- **⚠️ They never measure persona-conditioning accuracy.** Alignment is
  distributional (FID / MAUVE / KL Cosine) plus downstream F1. **There is no
  per-persona controllability number anywhere in the paper** — which is precisely
  the axis RQ2 measures. A third gap.
- **✅ Both unverified pipeline claims resolved.** Datasets *are* AGNews + Yelp +
  **SST-2 + IMDB**. MAUVE *is* reported, as the primary alignment metric. §C's
  mandate to use `mauve-text` is justified: the numbers will be comparable.
  Encoder `all-mpnet-base-v2`; Llama3-8B-Instruct as base for MoP *and* every
  baseline; 5,000 synthetic responses per method.
- **Venue still unverified** — arXiv shows none. "Findings of ACL 2025" stays
  flagged.

### Numbers now in the register

MoP AGNews FID 0.951 / MAUVE 0.871 / KL 0.069, with +13.6% to +41.3% MAUVE over
the best baseline across four datasets; downstream F1 within 0.01–0.07 of golden
data. Transfers to Gemma2-9B (MAUVE 0.957) and Mistral-7B (0.869) without
retraining.

### Decisions made (and why)

- **Read this one section rather than finishing all three gaps.** Sands's and
  Cobbe's numbers feed Ch.2 and §5.x, which are weeks away; MoP's K-selection
  feeds the step being built today. Sequencing by what blocks what, not by
  tidiness.
- **`mop2025` marked `[x]` — the first entry besides Huang to be complete.**
  Every register field is filled from the PDF.

### Consequences for downstream steps

- **G1 can proceed** knowing the closest competitor offers no K-selection
  precedent to follow or beat — which raises the value of doing it properly.
- Ch.2 gains three distinct gaps against MoP: no persona validation, no K
  selection, no persona-conditioning accuracy.

### Citations needed

- None new; `mop2025` already in `references.bib`.

---

## 2026-08-01 — Gate G1 built and pre-registered. Not run.

**Feeds:** Ch.4 §Persona discovery, **open decision 7** · **Artifacts:**
`configs/s2d_ktable.yaml`, `src/cluster/s2d_ktable.py`,
`tests/test_s2d_ktable.py`, `docs/protocol.md` RQ1-C · **Nothing was run.**

### Numbers

None. That is the point: the interpretation was fixed while the outcome is
still unknown.

### Decisions made (and why)

- **The decision rule was not invented here.** Pipeline §2.2 already fixes it —
  *the largest K with prediction strength ≥ 0.80* (Tibshirani & Walther's own
  cutoff), with **stability beating compactness** where criteria disagree. The
  code applies that rule mechanically; it does not choose.
- **Prediction strength takes the MINIMUM over clusters, not the mean.** One
  unreproducible cluster should sink a K. A mean would let two good clusters
  hide a bad one — and that is precisely how a K=3 that is really K=2-plus-noise
  would survive. There is a test for exactly this.
- **The gap statistic runs in PCA space (~50 components).** Its uniform
  reference is drawn over the data's bounding box, and in 768 dimensions a
  bounding box is almost entirely empty, so the reference would be meaningless.
- **The trap-check runs at every K, not only the selected one.** Stability and
  validity are different properties: a K can be perfectly stable and still be a
  rediscovery of the sentiment split. Both columns sit in the same table so
  neither can be quoted alone.
- **RQ1-C pre-commits every outcome, including the one that costs us the title.**
  If K=2 wins, the three-persona design gives way and the thesis runs two
  personas, with K=3 retained as the theory-motivated secondary. If no K reaches
  0.80, the verdict is `NO_STABLE_K` and the scheme must become theory-driven
  (the pipeline's own Gate G2 fallback) or RQ1 becomes a negative result.
  **Both are publishable; lowering the cutoff is not an option**, and a test
  asserts the threshold is still 0.80 so it cannot drift quietly.
- **Region A only.** Running a K-table on the full corpus would be choosing how
  many ways to split a file seam.

### Findings

- **I shipped a test suite that reported `8/8 passed` while five of its tests had
  not run.** scikit-learn is absent from the authoring sandbox, and the skip
  path printed a message and returned — which the runner counted as a pass.
  Fixed: skips now raise a `Skipped` sentinel and the summary reads
  `3 passed, 5 SKIPPED, 0 failed`, with a warning naming what did not execute.
  **A suite that reports green for tests it never ran is worse than no suite,
  because it is trusted** — and this is the second false-green I have caught in
  my own work this week, after the notebook cell.
- The five skipped tests are the ones that actually validate the statistics
  (prediction strength peaking at the true K, the minimum-over-clusters rule,
  bootstrap ARI separating structure from noise). **They run for the first time
  on Kaggle**, which is why the runner now prints their skip count separately.

### Consequences for downstream steps

- G1 runs on Kaggle in the same notebook, after both S2 configs, reusing their
  region-A row set. HDBSCAN needs `pip install hdbscan`.
- Open decision 7 (three personas or two) closes when this runs.
- **G-300 stratification depends on the outcome**, so no annotation can start
  until the K question is settled.

### Citations needed

- **Tibshirani & Walther (2005)**, prediction strength — the 0.80 cutoff is
  theirs and the thesis must attribute it.
- **Tibshirani, Walther & Hastie (2001)**, gap statistic.
- Both need entries in `related_work.md` (Tier 2) and `references.bib` before
  Ch.4 is written. **Not added yet — I have not read either paper**, and adding
  a citation for a method I took from the pipeline's summary would be exactly
  the shortcut this file exists to prevent.

---

## 2026-08-03 — Gate G1 ran. K = 2, and the corpus has no cluster structure.

**Feeds:** Ch.4 §Persona discovery, **Ch.5 §Threats**, open decision 7
**Artifacts:** `results/s2d_ktable_regionA.md`, `results/s2d_ktable_regionA.csv`
**Ran on:** Kaggle T4 · n = 1,897 (region A, post-dedup)

### Numbers

| K | **PS** | bootstrap ARI | silhouette | gap | GMM-BIC | ARI vs Sentiment | shares |
|---|---|---|---|---|---|---|---|
| **2** | **0.860** ✅ | **0.940 ± 0.029** | **0.053** | 0.9498 | −6.125e6 | 0.152 | 39.7 / 60.3 |
| 3 | 0.669 | 0.909 ± 0.045 | 0.015 | 0.9700 | −6.152e6 | 0.180 | 29.5–38.9 |
| 4 | 0.415 | 0.531 ± 0.178 | 0.011 | 0.9857 | −6.168e6 | 0.127 | 18.8–34.1 |
| 5 | 0.375 | 0.647 ± 0.213 | 0.018 | 0.9986 | −6.183e6 | 0.115 | 12.5–25.8 |
| 6 | 0.364 | 0.671 ± 0.162 | 0.012 | 1.0122 | −6.198e6 | 0.085 | 11.1–24.1 |
| 7 | 0.354 | 0.755 ± 0.097 | 0.017 | 1.0224 | −6.201e6 | 0.084 | 9.2–19.5 |
| 8 | 0.315 | 0.642 ± 0.098 | 0.010 | 1.0323 | −6.210e6 | 0.073 | 8.6–15.8 |

**HDBSCAN: K = 0, noise = 100.0%.**

### The verdict, by the rule fixed on 2026-08-01

**Only K = 2 clears the pre-registered PS ≥ 0.80** (0.860). K=3 reaches **0.669**
— not marginal, not "close enough". RQ1-C's K=2 branch therefore applies:

> **The three-persona design gives way.** The thesis runs two personas; K=3 is
> retained as the theory-motivated secondary (pipeline §2.2).

**Open decision 7 is closed: two personas.**

### The worry that K=2 raised is dispelled

Region A has two sentiment classes, so the obvious fear was that a 2-way
clustering just *is* the sentiment split. **ARI(cluster, Sentiment) = 0.152 →
Band 1, NOT_SENTIMENT_ALIGNED.** It is not. Cluster shares 39.7 / 60.3 —
comfortably non-degenerate. Bootstrap ARI 0.940 ± 0.029 is the tightest in the
table.

### 🔴 The finding that matters more than K

**The criteria do not merely disagree — they disagree in a patterned way, and
the pattern says there are no clusters here at all.**

- Agreeing on K=2: prediction strength, bootstrap ARI, **silhouette**,
  Calinski-Harabasz.
- Pointing at K=8 (the largest tested): **Davies-Bouldin**, **GMM-BIC**.
- **Gap statistic: the rule `gap(k) ≥ gap(k+1) − s(k+1)` is satisfied at NO K.**
  Gap rises monotonically 0.9498 → 1.0323 across the whole range. A gap curve
  that never turns over is the textbook signature of a dataset with **no cluster
  structure** — it would keep climbing past K=8.
- **HDBSCAN classified 100% of points as noise.** An algorithm free to find its
  own K, and to say "nothing here", said exactly that.
- **Silhouette peaks at 0.053.** Zero means points sit on cluster boundaries.
  0.05 is not weak structure; it is the absence of structure.

**Synthesis, and this is what goes in the thesis:** region A contains a
**highly reproducible bisection** (PS 0.86, bootstrap ARI 0.94) of a space that
contains **no separated groups**. Those are compatible. A dominant continuous
axis gets cut in the same place every time — that is what stability measures —
without there being two things to find. K-Means always returns K parts;
HDBSCAN and the gap statistic are the two instruments here allowed to answer
"none", and both did.

**Stability is reproducibility of a cut, not evidence of groups.** The
pre-registration warned that stability ≠ validity; this table is that warning
made concrete.

### Decisions made (and why)

- **K = 2 stands as the selected K.** The rule was fixed in advance and it was
  followed. Reading the disagreement as licence to reinstate K=3 would be
  exactly the manoeuvre the pre-registration exists to block — and K=3's own PS
  is worse, so there is no reading under which K=3 wins.
- **No deviation logged.** Nothing departed from the protocol; the rule produced
  an uncomfortable answer, which is what rules are for.
- **The full table goes in the thesis, disagreement included** (pipeline §2.2:
  no cherry-picking). Reporting only PS and bootstrap ARI would hide the fact
  that half the criteria point elsewhere and two say "no clusters".
- **The persona language must be qualified from here on.** Writing "we
  discovered two audience personas" would overclaim. What was found is a stable
  2-way partition whose status as *personas* is undetermined — and that is
  precisely G-300's question, not a statistic's.

### Consequences for downstream steps

- **G-300 is now decisive rather than confirmatory.** If three annotators can
  reliably tell the two halves apart, the partition means something and the
  persona framing survives (probably as a *tier* or *axis* rather than
  categorical types). If they cannot, RQ1 becomes a negative result — which
  RQ1-C already recorded as publishable.
- **Ch.5 §Threats gains a concrete entry:** three independent indicators
  (silhouette ≈ 0, monotone gap, 100% HDBSCAN noise) agree that LaBSE space over
  8-word Bangla reviews has no cluster structure. That is a limitation of the
  data and encoder, and it should be stated plainly rather than buried.
- **Title and framing need revisiting** — "three personas" appears throughout
  the pipeline and the pre-defence material. Sabbir's call; logged as open
  decision 12.

### Citations needed

- **Tibshirani & Walther (2005)** — prediction strength, and the 0.80 cutoff.
- **Tibshirani, Walther & Hastie (2001)** — gap statistic; the monotone-gap
  reading needs their own framing to be stated correctly.
- **Campello, Moulavi & Sander (2013)** — HDBSCAN.
- Still **not added** to `references.bib`: I have not read any of the three. A
  method citation taken from a summary is the shortcut this file exists to stop.

---

---

## 2026-08-03 -- S2e-f: K=2 profile and the residual test
**Feeds:** Ch.4 RQ1
**Commit:** `730de20136ae8e572f8340701c405477258a64e9-dirty`
**Artifacts:** `results/s2e_regionA_k2_profile.md`, `results/s2f_regionA_k2_residual.md`

### Numbers

**S2e — what the K=2 cut is made of** (n = 1,897; clusters 1,143 / 754 =
60.3% / 39.7%). Guard passed: silhouette 0.053404 and ARI 0.152152 reproduced
G1's published values to <1e-6, so these are G1's own labels.

- **`length_auc` (n_words) = 0.6764 → `LENGTH_CONFOUNDED`** (band [0.65, 0.75)).
- Strongest surface feature `n_chars` **0.6810** — below the 0.80 headline
  threshold, so no regular-expression finding was declared.
- All other features ≤ 0.574. `has_latin` 0.5004: region A has essentially no
  code-mixing (1 review in 1,897).
- Lexical richness at 4,000 tokens: cluster 0 **1,623** types, cluster 1
  **1,913** — the shorter half is the richer one.
- Margin: median 0.0644; **15.2%** of reviews within 0.02 of the boundary.

**S2f — the residual test** (voluntary; see Decisions).

| Test | Result | Verdict |
|---|---|---|
| A — length within a sentiment class | min AUC **0.6115** (S0 0.6115, S1 0.6567) | independent (threshold 0.60) |
| B — sentiment within a length band | min \|φ\| **0.3133** (worst band 3–6 words) | independent (threshold 0.20) |
| **C — what is left over** | lift **+9.80 pp** (70.06% vs 60.25%) | **`RESIDUAL_SURVIVES`** (threshold 10.0) |
| D — richness inversion under length control | holds in **all 4 bands**, budget 1,100 tokens | inversion survives |

Decomposition of Test C, same estimator, three cell definitions:

| Conditioning on | Accuracy | Lift |
|---|---|---|
| nothing (marginal) | 60.25% | — |
| Sentiment only | 69.53% | +9.28 pp |
| length band only | 65.47% | +5.22 pp |
| both (8 cells) | 70.06% | +9.80 pp |

Computed by hand off S2e's crosstab, and the reason S2f was run at all:
φ(cluster, Sentiment) = **0.3981**, χ² = 300.7, cluster→sentiment accuracy
**69.5%** vs a 50.2% baseline — against the **ARI of 0.1522** that the
pre-registration reads.

### Decisions made (and why)

- **Ran the residual test although the pre-registration did not require it.**
  RQ1 Band 2 triggers it at ARI ≥ 0.20; we are at 0.1522, so nothing was owed.
  The alternative was to stop at S2e and let Band 1 stand. Rejected because ARI
  is the wrong instrument for this association and **this project has already
  been misled by exactly this gap once** — `s2b_register_probe.md` recorded
  φ 0.565 against V 0.410. Every one of the 12 reviews nearest cluster 0's
  centre is positive and every one of the 12 nearest cluster 1's is negative;
  the log-odds lists separate praise terms from complaint terms. A reviewer
  would demand this test and the data was already on disk. Pre-registered as
  RQ1-E before the script existed. **It does not move the corpus into Band 2 and
  revises no band assignment** — recorded as voluntary and additional.
- **Chose a resubstitution estimator for Test C, knowing it overstates.** The
  alternative was a held-out or cross-validated estimate. Rejected because the
  bias direction matters more than the bias size here: resubstitution makes
  "sentiment and length explain the cut" *easier* to conclude, which is the
  verdict that kills the persona claim. A **low** lift under an optimistic
  estimator is therefore strong evidence, whereas a low lift under a
  conservative one would prove little. The caveat is printed everywhere the
  number is.
- **Derived the quartile band edges rather than choosing them.** Hand-picked cut
  points after seeing the table is how a residual test gets tuned into
  agreement. Edges are in the output; `n_quantiles: 4` is pinned by a test
  because the verdict is 0.2 pp from its threshold and re-binning could flip it.
- **Reported the near-threshold verdict as weak rather than as a result.** 9.80
  against a cutoff of 10.0 is 0.2 pp. The script emits a boundary warning box
  automatically whenever the lift lands within 2 pp of a cutoff, so this cannot
  depend on my remembering to mention it.
- **Did not normalise the Bangla text**, despite finding that it would change
  the log-odds table (see Findings). Inviolable rule: preserve the script
  exactly. Reported instead of fixed. **Whether the vocabulary table should
  additionally be shown in an NFC-collapsed form is Sabbir's call — not made
  here.**

### Findings (things we did not expect)

- **The richness inversion, and that it survives a length control.** Cluster 1
  is 33% shorter yet draws ~18% more word types at an equal budget — and this
  holds in **all four** length bands, not just in aggregate. Pure length
  predicts the opposite. Reading the representative reviews explains it: cluster
  0 is formulaic praise ("অসাধারণ সুন্দর একটা মুভি" with small variations),
  cluster 1 is short but **specific** complaint (কাহিনী, অভিনয়, নায়ক named
  individually). **This is the strongest pre-G-300 evidence that the halves
  differ in kind rather than in size**, and it was not anticipated.
- **Length is nearly redundant with sentiment at the level of prediction.**
  Sentiment alone buys +9.28 pp; adding length buys **+0.53 pp more**. S2e's
  `length_auc` of 0.6764 measures *correlation* and is real, but the
  `LENGTH_CONFOUNDED` verdict overstates length's independent contribution —
  long reviews in this corpus are mostly positive ones. This nuance is absent
  from `s2e_regionA_k2_profile.md` and is recorded here rather than silently
  correcting that file.
- **10.44% of all tokens sit in a group where the same word exists in two
  Unicode encodings.** Found while checking why নায়ক and নায়িকা each appear
  **twice** in S2e's log-odds table. 267 groups collapse under NFC; e.g. অভিনয়
  as `U+09DF` (188×) versus `U+09AF U+09BC` (152×). Two consequences: counts in
  the log-odds table are split and therefore understated for the affected words,
  and **LaBSE's tokenizer also sees the two forms as different**, so the
  distinction is inside the embedding, not only in the diagnostic.
- **The encoding form is itself a provenance signal.** φ(region, encoding form)
  = **−0.3245** over the 2,780 reviews using exactly one form: region A is 69.1%
  precomposed, region B is 64.0% decomposed. Different input methods, therefore
  different sources — an *independent* corroboration of fact (split), obtained
  from orthography rather than from punctuation or pronouns.
- **Region A has almost no code-mixing.** `has_latin` fires on 1 review in
  1,897. Worth knowing before any claim about Bangla-English mixing in the
  thesis.

### Consequences for downstream steps

- **G-300 proceeds, and it is now the decisive step, not a confirmatory one.**
  Test C eliminated the two cheapest explanations, so no cheaper instrument
  remains that could pre-empt the annotators.
- **The G-300 annotation guideline must be written so that annotators cannot
  succeed by reading length alone** — a condition fixed in RQ1-D before the
  number was known, and still binding at `LENGTH_CONFOUNDED`.
- **G-300 stratification uses `s2e_regionA_k2_assignments.csv`**, not the K=3
  file. G1 never persisted its labels; this is where they now live.
- **Every persona claim in the thesis carries both controls** — sentiment and
  length — in the main text, with the decomposition above, not in a footnote.
- **The persona language stays qualified.** Nothing here shows the halves *are*
  personas; it shows valence and verbosity do not account for them. The
  distinction goes in Ch.4 in those words.
- **`s2e_regionA_k2_profile.md` is not wrong but is incomplete**: its
  `LENGTH_CONFOUNDED` verdict stands as computed, while the +0.53 pp
  decomposition above is the sharper statement. Both are cited together
  wherever the length confound is discussed.
- **Open decision 13 opened** (Unicode encoding variants) — see STATUS.

### Citations needed

- **Monroe, Colaresi & Quinn (2008)** — log-odds with an informative Dirichlet
  prior. **Added** to `related_work.md` (Tier 2) and `references.bib`, with an
  explicit ⚠️ that the paper has not been read in full and its fields come from
  the record, not the article.
- Still **not added**, still unread, unchanged from the G1 entry: Tibshirani &
  Walther (2005), Tibshirani/Walther/Hastie (2001), Campello et al. (2013).
- **Nothing new is owed for S2f.** φ, AUC and majority-rule accuracy are
  textbook; the type-token-at-fixed-budget comparison reuses the S2b method
  already recorded there.

---

---

## 2026-08-08 -- S5k: G-300 round 1: the scale collapsed
**Feeds:** Ch.4 RQ1, Ch.5 Limitations
**Commit:** `43e6d877b40b9251623747079df0ec180e1f8a6b-dirty`
**Artifacts:** `results/g300_agreement.md`, `results/g300_ratings.csv`

### Numbers

Two independent annotators, all 300 items; B left 2 blank (G055, G060), so
**n = 298** rated by both.

| Statistic | Value |
|---|---|
| **Krippendorff α (ordinal)** | **0.4970** → `UNRELIABLE` (< 0.667) |
| Krippendorff α (nominal) | 0.4324 |
| Cohen's κ (linear weights) | 0.4456 |
| **Exact agreement** | **75.5%** |
| **Within 1 point** | **98.7%** |
| **Gwet's AC1 (linear)** | **0.8705** ⚠️ see the correction below |

Rating distribution — this is the whole story:

| Rating | A | B |
|---|---|---|
| 0 | 0.7% | 0.0% |
| 1 | 8.1% | 3.7% |
| **2** | **67.8%** | **76.2%** |
| 3 | 23.5% | 20.1% |

Rescue attempt, reported because it failed: binary recast at the only boundary
with real spread (3 vs ≤2) → observed agreement 83.9%, **κ = 0.5285**, still
below 0.667. Mean-rating spread: SD 0.442, **60.7% of items sit on the modal
value**.

**Gate 2 was not computed.** RQ1-F fixed that in advance for α < 0.667.

> ### ⚠️ Correction, 2026-08-08 — AC1 was over-read, and it was mine to catch
>
> Found while verifying `gwet2008ac1` for the bibliography, under the new
> standing instruction to search Consensus before defending a method.
>
> **Vach & Gerke (2023), MethodsX** — *"Gwet's AC1 is not a substitute for
> Cohen's kappa"* — show that for a **fixed** agreement rate, AC1 **increases**
> as the prevalence of one category departs from 0.5, while κ decreases. They
> also show AC1 can be non-zero under no association at all, and state that
> Landis & Koch's verbal bands must **not** be applied to it.
>
> **That is exactly our situation.** 68–76% of ratings were the single value
> "2". So **AC1 = 0.871 is partly a mechanical consequence of the skew**, not
> independent evidence that the annotators agreed. Reporting it as "the raters
> agreed strongly, AC1 0.871" made the skew look like corroboration when it is
> the same fact twice.
>
> **What survives unchanged:** exact agreement **75.5%** and within-1 **98.7%**
> are raw counts, not chance-corrected, and they do not depend on any of this.
> The instrument-failure reading rests on those plus the distribution table, and
> it stands. **What changes:** AC1 is reported *with* this caveat and is never
> the load-bearing number, and `vach2023ac1` is cited beside `gwet2008ac1`
> everywhere the paradox is discussed.
>
> The general lesson is the same one that produced the standing instruction:
> `gwet2008ac1` had been sitting in `related_work.md` for weeks as "the kappa-
> paradox guard", **listed but never read**, and the 2023 critique of it was one
> search away.

### Decisions made (and why)

- **Reported as INCONCLUSIVE (instrument failure), not as a negative result.**
  The pre-registered verdict (`UNRELIABLE`) stands and is not revised — what
  changes is only what it is taken to *mean*. "Negative" would assert that
  people do not make this distinction. **The data shows the opposite about the
  people**: 75.5% exact, 98.7% within one, AC1 0.871. What failed is the scale.
  Both readings are written down side by side so a reader can disagree with the
  framing while seeing the same numbers.
- **Attempted a post-hoc rescue, and reported that it failed.** Collapsing to
  binary at 3-vs-≤2 was the most favourable recoding available and it reaches
  only κ 0.53. Recorded because "we did not try" and "we tried and it did not
  work" are different states, and only the second supports an instrument-failure
  claim.
- **No round 2 — closed by circumstance, not by judgement.** A repaired rubric
  was the recommended path; Sabbir has no further annotator time. Written down
  explicitly so the absence of a second round is never read as a decision that
  round 1 sufficed.
- **RQ2–RQ5 decoupled from RQ1's outcome** (deviations log, 2026-08-05). The
  generation experiments condition on `cluster_k2` as a controlled label. RQ2
  asks whether an external verifier improves adherence to a **target label**;
  that needs the label to be well-defined and reproducible (PS 0.860, bootstrap
  ARI 0.940), not validated as an audience type.
- **Open decision 12 closed by force.** The word *persona* may no longer describe
  the K=2 halves anywhere, including the title. **The wording is Sabbir's; the
  constraint is not.**

### Findings (things we did not expect)

- **High agreement and low α at the same time.** The textbook kappa paradox, met
  in the wild. `gwet2008ac1` was already sitting in `related_work.md` Tier 2
  labelled as the guard for exactly this, entered weeks ago for a different
  reason (class-0 imbalance) — and it is what diagnosed this.
- **The calibration intervention caused the failure, and it was mine.** Round-1
  calibration showed annotator A compressed onto "1" (12 of 20). The advice given
  was *"if the review names an aspect, at least 2"*. **Nearly every review names
  something**, so both annotators moved almost everything to 2, and the 2-vs-3
  boundary — where the real discrimination had to live — was never sharpened.
  One problem was traded for a worse one. Calibration α was 0.744; after the fix
  it fell to 0.497. **The intervention made it worse, measurably.**
- **The lesson is transferable and belongs in the thesis, not in a footnote.**
  A rubric whose lower boundary is easy to satisfy will collapse upward. On
  ~8-word reviews there is not enough text to support four distinguishable
  levels of specificity; two or three would have been the honest design, or a
  forced-choice pairwise task, which cannot collapse at all.

### Consequences for downstream steps

- **RQ1 is reported as inconclusive on human validation.** RQ1-C's negative-result
  branch is *not* invoked, because this is not that outcome.
- **`cluster_k2` remains usable** as a controlled label for RQ2–RQ5. Nothing
  downstream is blocked.
- **Every use of "persona" in the pipeline spec, the pre-defence report and the
  conference draft needs a pass.** The title included.
- **RQ1-G (region-B replication) rises in value.** It needs no annotator time and
  is now the only remaining external evidence that the split is not an artefact
  of one corpus. It is **not** a substitute for human validation and is not
  reported as one.
- The G-300 items are **spent**: both annotators have seen them, so they cannot
  serve as a clean gold set for any future round.

### Citations needed

- **Gwet (2008), AC1** — `gwet2008ac1`, already in `related_work.md` Tier 2. It
  now has a concrete use and must be cited where the paradox is discussed.
  ⚠️ Still unread; the entry needs filling before the number is defended.
- **Krippendorff (2019)** — `krippendorff2019`, already listed for the ordinal α
  and the 0.667/0.80 bands. Same status: listed, unread.
- Nothing new is owed. Cohen's κ and the binary recast are textbook.

---

---

## 2026-08-08 -- S5m: RQ1-H: the split IS humanly perceptible
**Feeds:** Ch.4 RQ1 — the headline result
**Commit:** `75688957a9197a18f40982a619151f299cdf13e3`
**Artifacts:** `results/intrusion_agreement.md`, `results/intrusion_responses.csv`, `results/s2d_ktable_regionB.md`

### Numbers

**RQ1-H, Gate A — intrusion.** 50 length-matched sets, chance = 0.25.

| Annotator | Correct | Accuracy | Exact one-sided binomial p |
|---|---|---|---|
| A | 39/50 | **0.780** | < 1e-15 |
| B | 42/50 | **0.840** | < 1e-15 |
| pooled | 81/100 | **0.810** | < 1e-15 |

→ **`HUMANLY_PERCEPTIBLE`** (pre-registered threshold 0.45).

**Gate B — pairwise specificity.** 40 length-matched pairs, chance = 0.50.
Both annotators 34/40 = **0.850**, p < 1e-8. → the construct **is** specificity.

Inter-annotator: same option on **70.0%** of sets, **75.0%** of pairs.

**Verification, run before believing any of it:**

| Check | Result |
|---|---|
| Accuracy recomputed by an independent path | 39/50 and 42/50 — identical |
| Answer-position spread | A 13 · B 15 · C 8 · D 14 — no positional cue |
| Word span within a set | max **2**, mean **1.62** — matching held |
| **Length heuristic** (pick the most length-deviant option) | **8/50 = 0.16 — *below* chance.** Length is not merely neutralised, it is useless |
| Agreement vs. that expected under independent errors | 0.700 observed, 0.667 expected — no lockstep |
| Both wrong *and* identical | 2 sets of 50 |

**RQ1-G, region B replication** (`s2d_ktable_regionB.md`): n = 2,728. K = 2
selected, PS **0.818**, bootstrap ARI **0.962 ± 0.036**, shares 49.4/50.6.
But: silhouette **0.039**, HDBSCAN noise **96.7%**, ARI vs Sentiment **0.011**,
every surface-feature AUC in 0.50–0.58, `length_auc` **0.550 → NOT_LENGTH**,
richness inversion holds in **1 of 4** bands. S2f: Test A ENTANGLED, Test B fails
in band (6,8], Test C +7.2 pp.

### Decisions made (and why)

- **Gate A is read as a win, and Gate B is therefore interpreted.** Both were
  fixed in RQ1-H before any item was answered; nothing here is a judgement call.
- **Reported the annotators' own reported difficulty alongside the result.**
  They both said the items looked alike — and then scored 0.78 and 0.84. That
  contrast is not an embarrassment to be dropped; it is evidence about the
  *kind* of distinction this is (see Findings).
- **RQ1-G is read as outcome 2 — NO REPLICATION.** The rule required K *and*
  signature to match. K matched; the signature did not (`length_auc` 0.676 vs
  0.550, different bands; inversion 4/4 vs 1/4). Applied as written.
- **Did not withdraw or soften the region-A result because region B failed to
  replicate.** They are different corpora and the pre-registration anticipated
  exactly this outcome.

### Findings (things we did not expect)

- **The annotators could do it but could not say how.** Both independently
  reported that the items looked alike, and both then performed far above
  chance. **That is the signature of an implicit stylistic distinction** — real,
  perceptible, and not articulable on demand. It also explains attempt 1
  retrospectively: asking them to *rate* a property they cannot name is a much
  harder task than asking them to *spot the odd one out*, which is precisely
  what Kiritchenko & Mohammad (2017) predict and what Chang et al. (2009)
  designed around. **Attempt 1's failure was a failure of the question, not of
  the annotators or of the data.**
- **The length heuristic scores 0.16 — below chance.** Length matching did not
  merely neutralise the cue; on these sets, following length actively misleads.
  So Gate A's 0.81 was obtained with the strongest known confound not just
  controlled but inverted.
- **Region B's K = 2 split correlates with nothing measurable, and still passes
  the pre-registered stability rule** (PS 0.818, bootstrap ARI 0.962) at a
  near-perfect 49.4/50.6 bisection. **Region B is effectively a negative control
  showing that PS ≥ 0.80 is attainable by a contentless cut** in this regime.
  That is a methodological finding in its own right and it should be reported as
  one: prediction strength, our own decision rule, is weak evidence on short-text
  embeddings.
- Read together, the two runs say something sharper than either alone: **region
  A's cut has content (sentiment φ 0.398, length AUC 0.676, a consistent richness
  inversion, and now human recognition at 0.81); region B's has none.** The
  contrast is the argument.

### Consequences for downstream steps

- **RQ1 is answered, positively, and the answer is stronger than required** —
  obtained with length removed and with no construct named to the annotators.
- **Decision 12 needs revisiting again.** It was closed by force on 2026-08-05,
  banning the word *persona*, on the basis that human validation was
  inconclusive. **It is no longer inconclusive.** Whether "persona" is now
  permitted is Sabbir's call; what the evidence supports is *a humanly
  recognisable two-way distinction in engagement specificity*. It does **not**
  support "two audience types", because G1 showed no cluster structure — the
  object is a cut through a continuum that people can see.
- **Verifier-A's target label now has human backing**, which Phase 3 could not
  claim on 2026-08-05. The Phase-3 deviation (label reproduction only) stands
  for the *verifier's* accuracy, but the **label itself** is no longer merely a
  weak label.
- **Region B may not be pooled with region A** for persona-controlled work. Its
  split is a different object.
- G-300 attempt 1 remains reported in full. Two attempts, one instrument
  failure, one success — and the contrast between them is a methods contribution.

### Citations needed

- **Chang et al. (2009)**, intrusion task — now load-bearing, needs a `references.bib`
  entry and a `related_work.md` entry. ⚠️ not yet added.
- **Kiritchenko & Mohammad (2017)**, comparative vs rating scales — explains both
  the attempt-1 failure and the attempt-2 design. ⚠️ not yet added.
- **Eklund et al. (2025), CIPHE** — the document-vs-keyword intrusion distinction
  that puts this design on the supported side of the critique. ⚠️ not yet added.
- Miller et al. (2024), Nasution et al. (2024), El Assadi et al. (2025) — needed
  only if the LLM supplement is run.

---

## 2026-08-08 -- S3.2-prereg: Phase 3 opened: S3.2/S3.4 pre-registered, ablation code written, nothing run
**Feeds:** Ch.3 methods, RQ2
**Commit:** `ca88aa8fcd769882574d733e8c6bcd3a90c74444-dirty`
**Artifacts:** `docs/protocol.md` §"S3.2 pre-commitment" + §"S3.4 pre-commitment";
`configs/s3_backbone.yaml`; `src/verifier/{split_access,compare,backends,s3_backbone_ablation}.py`;
`tests/test_s3_backbone.py`; `notebooks/s3_backbone_kaggle.ipynb`.
**No file in `results/` — nothing has been run.** The dry-run artifacts were
generated, checked, and deleted; a stub's output does not belong in `results/`.

### Numbers

Four counts were computed directly against the frozen split and the region-A
K=2 assignments, and **all four match what `STATUS.md` recorded on 2026-08-08**,
which is the first independent confirmation of them:

| Quantity | Value |
|---|---|
| Verifier-A train (R1 ∖ dev, labelled) | **804** — 481 / 323 |
| dev (⊂ R1, labelled) | **82** — 53 / 29 |
| Verifier-B train (R2, labelled) | **888** — 531 / 357 |
| G-300 rows carrying a `cluster_k2` label | **123** — 78 / 45 |
| R1 rows labelled at all | 886 of 2,162 (**41.0%**) — the rest are region B |

Ablation size: 7 arms × 2 learning rates × 5 seeds = **70 fine-tuning runs**.
Test suite for this step: **20 tests, all passing**. The dry run completes in
~29 s on CPU, of which nearly all is the 21 × 10,000 bootstrap resamples.

### Decisions made (and why)

- **The S3.2 winner is decided by a paired bootstrap, not by the best
  mean ± SD across seeds — reversing what this notebook committed to one day
  earlier.** Alternative considered and used until today: "mean ± SD over ≥ 3
  seeds", logged in the 2026-08-08 Phase-3 deviation. Bethard (2022) surveys 85
  ACL Anthology papers and classifies *varying only the seed to build score
  distributions for performance comparison* as a **risky** use of seeds, while
  listing sensitivity measurement as safe. Our rule was the risky one, almost
  verbatim. Seeds go to 5 (Gundersen et al. 2023 on small effect sizes), variance
  is reported as sensitivity, and the decision moves to a paired bootstrap with
  BH correction over the 21 pairs. Reasoning is Claude's; the literature search
  that produced it was Sabbir's standing instruction.
- **Three arms added: IndicBERTv2, SetFit (LaBSE body), BERT-NLI.** Approved by
  Sabbir, 2026-08-08. Alternative was the pipeline's four arms unchanged, which
  needs no deviation. Claude's argument for the change: the four specified arms
  are all full fine-tuning, which is the weakest regime at n = 804, and they do
  not span the candidate space the recent literature names. ⬛ **Sabbir's own
  reasoning for approving is not recorded here, because he was not asked for it
  — it was a delegated choice presented with a recommendation. Recorded as
  delegated, not as his argument.**
- **Blocked 3×2 cross-validation (Xue et al. 2023) considered and rejected.**
  Sabbir's call, 2026-08-08. It has the better signal-to-noise property and
  would relieve the n = 82 dev bottleneck, but re-draws the train/dev boundary
  inside R1. **The reason, as confirmed by Sabbir on 2026-08-08:** *the frozen
  split map is the thesis's strongest reproducibility claim — committed to git,
  pinned by `tests/test_split_map.py`, and never regenerated — and it is not
  worth disturbing for a statistical improvement.*
  ⚠️ **Provenance of that sentence, stated so it is not mistaken for
  spontaneous testimony:** Claude drafted the wording and asked whether it
  matched his thinking; Sabbir confirmed it. It is his position, in Claude's
  words, endorsed rather than authored. That distinction matters if he is ever
  asked to defend it in his own terms.
- **Calibration (S3.4) demoted from "hidden contribution" to descriptive.**
  Claude's, uncontested. At 82 dev rows a 10-bin reliability diagram holds ~8
  samples per bin. Alternative was to keep the pipeline's framing and defend it;
  that defence does not exist. Temperature scaling is **kept and deliberately
  not upgraded**, which is the literature's own recommendation at this n
  (Balanya et al. 2022), not a concession.
- **`TIE` pre-registered as the most likely S3.2 outcome, and as publishable.**
  This is a decision, not a hedge: it fixes in advance that a tie is reported as
  the result and broken on stated non-performance grounds, so that a tie cannot
  later be quietly resolved by picking whichever arm read best.
- **The R1/R2/G wall was moved from convention into code.** `split_access.py`
  takes a *role*, not a partition name, so no caller can request R2 for the
  in-loop verifier. Alternative was to keep relying on everyone remembering
  inviolable rules 4 and 6. The rules have held so far; they had no enforcement.

### Findings (things we did not expect)

- 🎁 **The Bangla literature does not agree on a backbone winner, and two papers
  disagree on the *same dataset*.** `hassin2026banglablend` reports XLM-R 94% >
  BanglaBERT 93.4% on BanglaBlend; `mazumder2025banglaforms` reports IndicBERTv2
  95.44% > XLM-R > BanglaBERT on BanglaBlend. `mitra2025muril` has MuRIL beating
  both. **Pipeline §3.2 framed the ablation as confirming an expected BanglaBERT
  win; it is not confirmatory, and "BanglaBERT because it is Bangla-native"
  cannot be defended by citation at all.** This makes the ablation load-bearing
  and makes its outcome genuinely unknown, which is the condition under which
  pre-registering was worth the effort.
- 🔴 **We wrote a protocol rule on 2026-08-07 that the methodology literature
  had already classified as bad practice.** Found by searching, one day later,
  before anything ran — but it is the second time the standing Consensus
  instruction has caught something after the fact rather than before (the first
  was the G-300 rating scale). The instruction works; the habit of searching
  *before* writing the rule still does not.
- ⚠️ **The dry run was not reproducible on its first attempt.** The stub used
  the builtin `hash()`, which Python randomises per process; `set_seed()`'s
  `PYTHONHASHSEED` assignment cannot fix that, because the interpreter reads
  that variable at startup. Fixed with `zlib.crc32`. Nothing scientific
  depended on it — but the same trap would apply to any future use of `hash()`
  for a deterministic choice anywhere in this repo, and it was invisible until
  the dry run was executed **twice**. Running it once would have shown a clean
  result.

### Consequences for downstream steps

- **S3.2 may not be run until this is committed**, since the pre-registration
  is only a pre-registration if it precedes the run in the history.
- **§3.3's dual-accuracy table stays impossible** (deviation of 2026-08-08).
  The S3.2 winner is selected on **label reproduction, not validity**, and the
  generated report says so on its own face rather than only in the thesis.
- **τ in §4.5 now inherits a weakened calibration.** τ becomes a sensitivity
  curve rather than a point, and §4.2's Verifier-B sanity-check on the final τ
  is promoted from advisory to mandatory.
- **Pipeline §3.2 and §3.4 are both now wrong as written** (four arms; ten-bin
  ECE as a contribution). Deviations are logged; the spec text itself is still
  unedited, consistent with the existing policy of not editing
  `research_pipeline_en.md` piecemeal.
- **`protocol.md` §S3.2 and §S3.4 are frozen from the moment S3.2 runs.**
  Neither may be edited afterwards.
- Kaggle budget risk: 70 fine-tuning runs against a 12 h session cap. If split,
  split **by arm, never by seed** — splitting by seed would put an arm's seeds
  in two environments and make its SD a mixture of two things.

### Citations needed

17 entries added to `references.bib` and `related_work.md` §Tier 5 on
2026-08-08. ⚠️ **All 17 are Consensus index records; none has been read in
full, none carries a DOI or eprint ID, and author lists are truncated to the
first author.** Nothing was reconstructed from memory. Read-status is `[ ]` for
every one of them.

Three are **load-bearing** and must be read before the S3.2 result is written up,
because each is the sole support for a design decision:

- `bethard2022seeds` — why the decision rule is not mean ± SD.
- `laurer2023bertnli` — why the BERT-NLI arm was added; the +10.7–18.3 pp figure
  is quoted from an abstract and must be checked.
- `beliveau2024smalldata` — why SetFit is registered as an expected loser.

⚠️ Four of the six Bangla backbone papers have **0 citations** and are 2025–26
conference papers. They are adequate to show that *the field disagrees* and are
used for nothing else; `mukherjee2023blp` in particular ranked 19th of 30 and is
explicitly not evidence that XLM-R is better.

⬛ Still outstanding from the 2026-08-08 RQ1-H entry above: Chang et al. (2009),
Kiritchenko & Mohammad (2017), Eklund et al. (2025) — **not yet added**.

---

## 2026-08-10 -- S3.2: Backbone ablation: seven arms, verdict TIE under both aggregation rules
**Feeds:** Ch.3 methods, Ch.4 results, RQ2
**Commit:** `e3afa71f627fbbae441b53582621cf94ff42610f-dirty`
**Artifacts:** `results/s3_backbone_ablation.json`, `results/s3_backbone_ablation.md`, `results/s3_backbone_per_seed.csv`

### Numbers
- `results/s3_backbone_ablation.json`
  - `dry_run` = False
  - `verdict` = TIE
  - `n_train` = 804
  - `n_dev` = 82
  - `train_class_counts` = {'0': 481, '1': 323}
  - `dev_class_counts` = {'0': 53, '1': 29}
  - `gold_ids_touched` = 0
  - `visible_gpus` = 1
  - `env` = {'python': '3.12.13', 'transformers': '4.57.6', 'torch': '2.10.0+cu128', 'gpu': 'Tesla T4', 'n_gpu': 1}
  - `resume_status` = verified
  - `resumed_from_unverified_checkpoint` = False
  - `verdict_pooled_lr` = TIE
  - `verdict_agrees_across_lr_rules` = True
  - `mean_macro_f1_pooled_lr` = {'banglabert': 0.960792, 'setfit_labse': 0.958966, 'indicbertv2': 0.955991, 'muril': 0.941799, 'mbert': 0.934917, 'bert_nli': 0.926205, 'xlmr': 0.91385}
  - `mean_macro_f1` = {'banglabert': 0.964668, 'setfit_labse': 0.958966, 'indicbertv2': 0.956018, 'muril': 0.942118, 'mbert': 0.940246, 'xlmr': 0.935954, 'bert_nli': 0.929828}
  - `seed_sd` = {'banglabert': 0.020898, 'xlmr': 0.02185, 'muril': 0.039095, 'mbert': 0.012509, 'indicbertv2': 0.015585, 'bert_nli': 0.016548, 'setfit_labse': 0.0}
  - `selected_lr` = {'banglabert': 3e-05, 'xlmr': 3e-05, 'muril': 3e-05, 'mbert': 2e-05, 'indicbertv2': 3e-05, 'bert_nli': 3e-05, 'setfit_labse': 2e-05}
  - `lr_selected_on_eval_set` = True
- `results/s3_backbone_ablation.md`
  - (see file; 3238 bytes)
- `results/s3_backbone_per_seed.csv`
  - (see file; 1897 bytes)

### Decisions made (and why)

- **The winner is BanglaBERT by the pre-registered TIE-BREAK, not by performance.**
  Alternative: read the ranking and call BanglaBERT the winner at 0.9647. Rejected
  because all **21** pairwise comparisons are non-significant after BH and the
  smallest p is **0.096** — there is no winner to read. The tie-break
  `[smallest_params, banglabert]` was fixed on 2026-08-08, before any number
  existed, and selects BanglaBERT on parameter count (110M, smallest of seven).
  **Every defence of the backbone choice must state that the data did not
  determine it.**
- **Inner k-fold tuning is NOT run, and the argument for that is now empirical.**
  On 2026-08-09 we could not settle whether selecting the learning rate on dev
  manufactures a winner (winner's curse). Rather than spend ~30% more GPU on
  nested tuning, the verdict was computed under **two aggregation rules from the
  same runs** — best-LR per arm, and a selection-free majority vote over all ten
  runs. **Both return `TIE`.** The pre-registered trigger for the expensive
  design was disagreement; it did not fire.
- **The setfit arm is reported as ONE configuration and is NOT re-run.**
  Alternative: re-run it correctly for ~2h15m. Rejected because the fixed arm
  cannot change a verdict already agreed by both aggregation rules, while the
  honest single-configuration report is available at no cost. The code is fixed
  so the arm is correct if ever re-run, and a test now reads the source for the
  learning-rate arguments.
- **No ranking below the top place is quoted anywhere.** The two aggregation
  rules disagree on the order (XLM-R 6th under the headline rule, 7th under
  pooling), which is itself the argument: in a tie, order is a property of the
  aggregation, not of the models.

### Findings (things we did not expect)

- 🎁 **The variation inside one arm exceeds the variation between all seven.**
  MuRIL's seed-to-seed SD is **0.0391**; the entire between-arm spread is
  **0.0348** (0.9298–0.9647). Together with Coakley et al. (2022), who measured
  **>6 pp** of accuracy variation from hardware/software environment alone
  across 780 runs, this makes the tie a **statement about measurement
  resolution**, not an absence of effort: *the differences we set out to resolve
  are smaller than the noise of the apparatus.* This is the sentence Ch.4 should
  carry, and it was not anticipated.
- 🔴 **The setfit arm ran one computation ten times, and the log proves it.**
  Across all ten runs the schedule peaked at the same 1.98e-5 under **both**
  nominal learning rates, `grad_norm` matched to sixteen decimals
  (2.8027944564819336), and `train_loss` was **0.016336093562370195** every
  time. Identical gradients cannot come from different initialisations, so the
  seed was inert as well. The checkpoint agrees independently: **1 distinct
  prediction vector out of 10**, against 8/10 for MuRIL and IndicBERTv2. Cause:
  `setfit_predict` never passed `lr` to SetFit. **Its SD of 0.0000 is an
  artefact and must never be read as stability** — which is exactly how it would
  have read in a results table.
- ⚠️ **SetFit placed second, having been pre-registered as an expected loser.**
  Beliveau et al. (2024) found BERT-like > SetFit in the closest published
  setting; here it sits above five of seven arms. In a tie the ordering carries
  little, and it ran on one configuration, so **this does not overturn
  Beliveau** — but the expected loser did not visibly underperform, and that is
  reported rather than passed over.
- ⚠️ **bert_nli placed last (0.9298).** It was added on the strength of Laurer
  et al. (2023), who report +10.7–18.3 pp at 100–2,500 training texts and
  especially on imbalanced data. **That advantage did not appear.** The arm was
  added on the literature's authority and the result went the other way; that is
  the honest outcome of adding it.
- 🎁 **MuRIL and SetFit produced byte-identical predictions** on the 82 dev rows
  (the zero-width confidence interval in the pairwise table is what exposed it).
  Six distinct prediction vectors across seven arms. At 82 items and ~95%
  accuracy, convergence is plausible rather than alarming — but it is another
  sign that the dev set is small enough for arms to collide.
- 🎁 **Reproducibility held across sessions.** Five arms returned identical
  macro-F1 in two separate sessions on different GPU allocations before the
  environment was pinned, which is what justified resuming rather than
  re-running them.

### Consequences for downstream steps

- **Verifier-A uses BanglaBERT** — 110M, and the smallest arm, which also makes
  it the cheapest to run inside the Phase 4 loop. The choice is defensible on
  cost; it is **not** defensible on measured accuracy, and must not be presented
  that way.
- **§3.3's framing is unchanged and now has a number attached**: 0.93–0.96 is
  **label reproduction**, not validity. No human-validated verifier accuracy
  exists (deviation of 2026-08-08).
- **Ch.4 gains a methodological result it did not plan for**: within-arm seed
  variance exceeding between-arm spread. This belongs beside the ablation table,
  not in a footnote.
- **Ch.5 Limitations gains three entries**: the setfit single-configuration
  defect; the cross-model-class caveat for comparisons spanning fine-tuning,
  SetFit and NLI transfer (Teodorescu et al. 2025); and the levels being
  selection-biased because the learning rate was chosen on the same dev set.
- **S3.4 (calibration) is next**, and its pre-registration already demotes it to
  descriptive at n = 82.

### Citations needed

No new methods were used in this step. Every citation the run rests on is
already in `references.bib` and `related_work.md` §Tier 5:
`bethard2022seeds` (why the decision rule is a bootstrap), `coakley2022implementation`
⬛ **not yet added — the environment-variation figure is now load-bearing in two
deviations and in Ch.4, and it still has no bib entry**, `laurer2023bertnli`
(why bert_nli was added; the result contradicts it), `beliveau2024smalldata`
(why setfit was an expected loser), `tunstall2022setfit`, and
`teodorescu2025kfold` ⬛ **also not yet added** for the cross-model-class caveat.

⚠️ Read-status is still `[ ]` for all of them.

---

## 2026-08-10 -- S3.2b: Baselines: a frozen LaBSE probe beats every fine-tuned arm
**Feeds:** Ch.3 methods, Ch.4 results, Ch.5 limitations, RQ5
**Commit:** `1a37be13a011e2d3ee68e0b2c68cd12a04ee9fbc-dirty`
**Artifacts:** `results/s3b_baselines.json`, `results/s3b_baselines.md`

### Numbers
- `results/s3b_baselines.json`
  - `verdict` = CIRCULARITY_CONFIRMED
  - `n_train` = 804
  - `n_dev` = 82
  - `one_dev_item_in_macro_f1` = 0.012195
  - `baselines` = {'majority': 0.392593, 'length_rule': 0.619666, 'labse_probe': 0.986555}
  - `best_arm` = banglabert
  - `best_arm_macro_f1` = 0.964668
  - `gap_best_arm_minus_labse_probe` = -0.021887
  - `gap_in_dev_items` = -1.79
  - `arm_means_for_reference` = {'banglabert': 0.964668, 'setfit_labse': 0.958966, 'indicbertv2': 0.956018, 'muril': 0.942118, 'mbert': 0.940246, 'xlmr': 0.935954, 'bert_nli': 0.929828}
- `results/s3b_baselines.md`
  - (see file; 1361 bytes)

### Decisions made (and why)

- **The frozen-probe baseline was added at all.** Alternative: proceed to Phase 4
  on the seven-arm table as it stood. Rejected because the table could not
  answer *0.96 against what?*, and the specific worry — that `cluster_k2` came
  from k-means **on LaBSE embeddings**, so a linear probe on those embeddings is
  the label's own geometry reproducing itself — was cheap to test and expensive
  to discover later. Sabbir asked whether Phase 3 was satisfactory before
  Phase 4; this is the answer to that question.
- **Bands were fixed before the number existed**, in units of one dev item
  (1/82 = 0.0122), because that is the resolution 82 items have. Band (i) fired,
  and past its own threshold.
- **The result was verified before it was believed**, which the pre-registration
  demanded only for the `NOT_CIRCULAR` outcome — done here anyway because a
  result this strong is exactly when a bug is most likely to be mistaken for a
  finding. Train and dev are disjoint, so nothing leaked into the logistic fit;
  the reported macro-F1 reconstructs exactly at **one error in 82**; and the
  artifact carries a real provenance stamp (`1a37be1`, genuine UTC timestamp).
- **Verifier-A is NOT reassigned here.** The probe is now the strongest and
  cheapest candidate, but making both A and B probes would collapse RQ5, so the
  choice is opened as decision 16 rather than taken. Registering it before
  Verifier-A is trained is the point.

### Findings (things we did not expect)

- 🔴 **The frozen probe does not merely match the fine-tuned arms — it beats all
  seven.** 0.9866 against BanglaBERT's 0.9647: **1.8 dev items ahead**, one error
  on 82 items, from a logistic regression that fits in seconds. Roughly 4.5
  GPU-hours of fine-tuning produced something slightly *worse* than a linear head
  on frozen embeddings.
- 🔴 **So the seven-arm ablation measured the label's construction, not the
  backbones.** `cluster_k2` is close to a linear boundary in LaBSE space by
  construction, and every arm was recovering it. **The table may support no claim
  about which backbone is better**, and the `TIE` is re-explained: the arms are
  indistinguishable because the task is near-saturated, not because backbones are
  interchangeable in general.
- ⚠️ **Fine-tuning cost accuracy rather than adding it.** This is what Buckmann
  et al. (2024) predict for the tens-of-shot regime and what Beliveau et al.
  (2024) imply for small non-English data. Both were already in the
  bibliography; neither was applied to our own setup until now.
- 🎁 **The trivial baselines are reassuring and were also unknown.** Majority
  **0.3926**, best length rule fitted on train (n_words ≤ 7) **0.6197**. The task
  is not the class prior or the length confound wearing a transformer — which
  matters, because S2e had measured `length_auc` at 0.6764 and left the worry open.
- ⚠️ **A consequence the pre-registered bands did not anticipate, and it is the
  most serious one.** If Verifier-A becomes the probe and Verifier-B is also a
  probe, the two are near-identical functions on one embedding space, they agree
  by construction, and **RQ5's Goodhart test — the wall that inviolable rule 6
  exists to protect — becomes unmeasurable.** Opened as decision 16.
- 🎁 **A sharper way to state the risk, which may become the more interesting
  paper.** A verifier that is a linear function of LaBSE may be *trivially
  gameable* by a generator whose output is scored in that same space. That is
  precisely the failure mode RQ5 was written to detect, and S3.2b has made it a
  live hypothesis rather than a formality.

### Consequences for downstream steps

- **Ch.4 rewrites the ablation section.** It becomes: seven backbones are
  indistinguishable, a frozen linear probe beats all of them, and the reason is
  that the label is linear in its generating encoder. That is a more honest
  section and a more interesting one than "BanglaBERT wins".
- **RQ1 and RQ2 are unaffected.** RQ1-H showed humans perceive the distinction
  (0.78/0.84 against 0.25 chance), so the label is real — it is simply linear in
  LaBSE space. RQ2 needs a well-defined reproducible label and has one.
- **Verifier-A is blocked on decision 16.** It must not be trained before that is
  registered.
- **S3.4 may get easier**: logistic regression yields calibrated probabilities
  natively, which is a better starting point at n=82 than a fine-tuned
  transformer's logits. Whether that survives depends on decision 16.
- **Ch.5 Limitations gains the central one**: a cluster-derived label evaluated
  by models with access to the clustering encoder cannot measure much, and any
  accuracy reported against it must be read as reproduction of a geometric
  partition.

### Citations needed

- `buckmann2024logistic` — already in `references.bib` §Tier 5b as a supporting
  entry. **Promote it: it is now load-bearing**, since it predicted this result
  in advance and we did not apply it.
- `beliveau2024smalldata` — already load-bearing for SetFit; its BERT-like >
  SetFit ordering is unchanged, but its broader point about small non-English
  data now applies to the whole ablation.
- ⬛ No new method was used. Logistic regression on frozen sentence embeddings
  needs no citation beyond Buckmann; the k-means provenance of the label is
  already documented in S2d/S2e.

⚠️ Read-status remains `[ ]` for both.

---

## 2026-08-10 -- S6: protocol.md sealed for Phases 1-3; decision 12 closed as the engagement-specificity axis
**Feeds:** Ch.3 Methods; Ch.4 Results framing; Ch.5 Limitations
**Commit:** `fee944c9850129a95fb4d50232cb9703205c818c-dirty`
**Artifacts:** `docs/protocol.md` (1,123 lines, 37 deviation rows), `docs/supervisor_seal_packet.md`, `docs/related_work.md` Tier 6, `docs/references.bib` (+6 keys)

### Numbers
- `protocol.md`: 1,049 -> **1,123** lines; deviation rows 33 -> **37**.
- Body corrections against STATUS's verified facts: **5**.
  - clustering n: `4,422` -> **4,625**
  - annotators: `3` -> **2**
  - RQ2 design: `3 personas` -> **2 axis levels** (stale since 2026-08-03)
  - the venue-confound paragraph's *"untestable in principle"* -> corrected
  - header: `FROZEN PRE-ANALYSIS PLAN` -> **APPEND-ONLY PRE-ANALYSIS RECORD**
- Superseded-section banners added: **2** (RQ1-B table, S3.2 premise).
- Missing deviation rows added: **4** (RQ1-G, RQ1-H, terminology, selective inference).
- `references.bib`: 39 -> **45** entries.
- Cross-check: every quantity in the seal packet matches `STATUS.md`;
  `step_close.py --check` exits 0.

### Decisions made (and why)

- **Decision 12 closed as the engagement-specificity AXIS; both *persona* and
  *cluster* retired.** ⚠️ **Provenance: Sabbir delegated the call ("you can make
  the best decision"). The choice and the reasoning are Claude's -- endorsed, not
  authored.** Three options were live: keep the 2026-08-05 ban and say *cluster*;
  re-permit *persona* on RQ1-H's warrant; or a third term. The literature moved
  the answer past all three as posed. `pinto2026drawinglines` obtains k=2,
  silhouette ~0.31, ARI 0.999+/-0.001, sizes **50.6/49.4** on 8,360 psychometric
  respondents -- numerically almost our region B (49.4/50.6) -- and reads it as
  *"geometric stratifications of a latent continuum rather than evidence for
  discrete subtypes"*. `cornelissen2026contour` publishes a negative
  clusterability result and shows a prior four-type typology was an artefact of
  k-means placing centroids on principal axes. **So *cluster* fails for the same
  reason *persona* did**: both assert structure that silhouette 0.053, a monotone
  gap statistic and 100% HDBSCAN noise say is absent. `cluster_k2` survives as a
  frozen *variable name* only -- renaming would break the split map (rule 3).
  ⬛ **Rejected: re-permitting *persona* on RQ1-H.** Perceptibility of a
  distinction is not evidence of discrete groups, and separating those two claims
  is exactly what this literature does.

- **The seal is an append-only record, not a freeze event.** Sabbir chose this
  form from three offered. The old header promised one freeze after Step 5; Step
  5 ran 2026-07-30 and 30+ amendments followed, so the promise was already false.
  Replaced with four properties that `git log` can check: every section dated, no
  section edited after the run it governs, superseded text struck not deleted,
  every departure logged. ⬛ **Rejected: filling in a single freeze date** -- 
  easier to sign, impossible to defend against the document's own history.

- **Pre-registered section bodies were NOT edited.** S3.2 states "nothing in this
  section may be edited after the first run", and its premise did not survive
  S3.2b. Resolved with a dated pointer banner rather than a rewrite, following
  the pattern already in the file at the superseded RQ1 ARI bands. Editing the
  premise would have destroyed the evidence that it was fixed in advance.

- **Phases 4-6 seal separately.** RQ2-RQ5 are 3-8 lines each and nothing in them
  has run; sealing them now would attach a signature to text with no evidence
  behind it.

### Findings (things we did not expect)

- 🎁 **`pinto2026drawinglines` is our region B in another field.** k=2,
  ARI 0.999, sizes 50.6/49.4, and on correlated Gaussian data ARI = 1.00 SD 0.00
  described as *"an artificial partition of a continuous, anisotropic
  distribution."* RQ1-G's negative control was not a quirk of this pipeline; it
  is the documented behaviour of stability-based K selection, and
  `vonluxburg2010stability` had said so in 2010. **We rediscovered a known
  failure mode and did not know it was known.**

- 🔴 **S2e/S2f are post-clustering inference and nobody had noticed.**
  `chen2023selectiveinference` shows post-hoc tests on cluster-derived groups
  inflate Type I error, producing large between-group differences *even when no
  population categories exist*. phi = 0.3981 and chi2 = 300.7 are computed on the
  rows that defined the partition. S2f Test C already self-flagged as a
  resubstitution bound -- the instinct was right and simply was never generalised
  to the neighbouring statistics.

- 🔴 **RQ1-G and RQ1-H had full pre-commitment sections and NO deviation rows.**
  Five and two days respectively. RQ1-H is the largest departure in the document
  -- a second human-validation instrument after the first failed -- and its
  defence sat in a section body rather than in the log where a reviewer checks.
  Recorded as a process failure rather than backdated.

- **`protocol.md` was still asserting an error that its own deviations log
  quotes as an error.** The *"untestable in principle"* correction was applied to
  `STATUS.md` on 2026-07-30 and to this file only on 2026-08-10. A correction
  applied to one of two files is a correction that has not been made.

### Consequences for downstream steps

- **No p-value from S2e/S2f may be quoted as evidence** that the halves differ.
  They are descriptive profiling. Ch.4 must say so where the numbers appear.
  RQ1-H does not inherit this -- held-out items, blind annotators -- which is why
  the human validation, not the profiling, carries RQ1.
- **PS >= 0.80 is demoted to necessary-but-not-sufficient** everywhere it appears.
- **Ch.1, the title, and the conference draft** must follow the axis constraint.
  ⚠️ The title still says "Audience Simulation" and now contradicts the sealed
  document. **Sabbir's wording; the constraint is not optional.**
- **`related_work.md` Tier 3 needs a re-read.** It was assembled to ground three
  personas; `cuadrado1999` is a 3-cluster cinema segmentation and no longer
  mirrors any claim we make.
- **Two unread load-bearing citations** (`chen2023selectiveinference`,
  `vonluxburg2010stability`) are debts, flagged as such, and must be read before
  Ch.4 is written.

### Citations needed

Added as **Tier 6** in `related_work.md` and to `references.bib`:
`pinto2026drawinglines` `[x]`, `cornelissen2026contour` `[x]`,
`chen2023selectiveinference` `[ ]`, `adolfsson2019clusterability` `[ ]`,
`vonluxburg2010stability` `[ ]`, `kalogeratos2012distdip` `[ ]`.

⚠️ **Source disclosure: found via alphaXiv and Scite, NOT Consensus** -- the
Consensus quota was exhausted (0 searches until 2026-09-01). The standing
instruction prefers Consensus; it was unavailable, and searching two replacement
indices does not fully substitute for it. Recorded rather than glossed.

---

## 2026-08-11 -- S6b: pipeline cross-check -- 10 deviations, and a reframing the search killed
**Feeds:** Ch.3 Methods; Ch.5 Limitations; Phase 4 planning
**Artifacts:** `docs/protocol.md` (47 deviation rows), `docs/related_work.md` Tier 7, `docs/references.bib` (+1, +1 upgraded), `docs/STATUS.md` Phase-3 real state

### Numbers
- Deviation rows **37 -> 47**.
- Pipeline sect. 3 deliverables: **1 of 5** exist.
- `grep -rl symbolic src/ configs/` -> **0 files**. `src/agents/`, `src/eval/` -> empty stubs.
- English arm artifacts (`imdb`, `mpst`, `distilroberta`) in repo -> **0**.
- sect. 5.1 generation count **2,160 -> 1,440** per language (stale 8 days).
- Dev-slice decision count: **5** decisions on 82 rows (2 now moved to dev-plots).

### Decisions made (and why)

- **RQ3 is NOT reframed. The gaming-shield idea was proposed, searched, and
  rejected before a word of it was written.** Claude proposed reframing RQ3 from
  "does hybrid raise accuracy" to "does symbolic prevent gaming", because S3.2b
  left the accuracy question unanswerable (Verifier-A at 0.9866 = 1 error in 82).
  `mahmoud2026rubric` refutes it directly: under a **strong** verifier, rubric
  judges preferred the RL checkpoint on **85.8%** of prompts while rubric-free
  judges preferred the **base** on **78.4%**, with gains in **presence-based**
  criteria (+1.07) and losses in conciseness (-2.91), relevance (-1.10), factual
  correctness (-0.85). **Our sect. 3.5 features are almost all presence/count-based,
  and sect. 4.2's Reflector names the failing rule to the Writer** -- our setting is
  strictly easier to game than theirs. ⬛ **The paper was already in our
  bibliography, cited from its abstract for decision 16.** Writing the reframing
  from memory would have produced a claim refuted by our own reference list.

- **Symbolic is retained on honest grounds:** sect. 3.5 mandates it, sect. 4.2's Critic
  cannot exist without it, and it is the only component that can say *which*
  rule failed -- which the Reflector requires and a LaBSE probe cannot do.
  Registered as an **instrument for detecting** gaming (presence-scores rising
  while Verifier-B stays flat is Mahmoud's signature), never as a shield.

- **Hybrid weight moves off the 82 rows onto the 30 dev-plots.** At 1 error in
  82 the weight sweep is degenerate -- every weight in sect. 5.1b's 0.5-0.8 grid
  returns the same answer, and the "<2 points" rule would need to resolve ~1.6
  dev items. The weight is a generation-time parameter, so it is fit where the
  Critic operates. Reported as a sensitivity curve, never a point (as for tau).

- **Decision 16 amended, not overturned.** `kuai2026entanglement`: entanglement
  is widespread intra- AND cross-family, and **plain correlation cannot detect
  it**. A dev-slice failure-manifold audit (BEI/CIG) is pre-registered before any
  RQ5 gap is interpreted. Cross-family stays **necessary, not sufficient**.

- ⛔ **CORRECTED SAME DAY -- English arm is SCHEDULED, not reduced.** The first
  version of this entry said the charter's *"cut to fertility + zero-shot only"*
  clause had been invoked. **That was Claude exercising a scope decision that
  belongs to Sabbir**, on the basis of him saying *"pore kori"* -- which is a
  statement about **order**, not **scope**. Corrected on his instruction:
  *"english thakbe. cross lingual hobe"*, plus the standing rule *"amader lokkho
  research pipeline onujayi kaj kora."* **The full sect. 1.2 charter runs and RQ4
  stays live in its strong form**; the cut clause remains unexercised and
  available to him. **Lesson, recorded because it generalises: a pipeline escape
  clause is not mine to invoke.** Ambiguity about scope goes back to Sabbir; it
  does not get resolved by picking the cheaper reading.

- **Verifier-B disambiguated: the S3.2 *recipe* retrained on R2, never the S3.2
  checkpoints.** Sabbir's earlier question about pipeline conformance is what
  surfaced it.

### Findings (things we did not expect)

- 🔴 **The seal of 2026-08-10 claimed "every departure is logged" without ever
  opening the document departures are measured against.** `CLAUDE.md` names
  `research_pipeline_en.md` as normative in its second line. The audit compared
  `protocol.md` to `STATUS.md` and to itself. **Logged against ourselves;** the
  seal stands on its four checkable properties, the completeness claim did not.

- 🔴 **Pipeline sect. 2.1 instructs writing a sentence our own results falsify** --
  *"low silhouette ... not absence of structure; hence we rely on stability"*.
  Region B cleared PS 0.818 on a contentless cut. The thesis would have asserted
  in Methods the exact inference its Results disprove. Withdrawn.

- 🔴 **Verifier-B was one training run from voiding rule 6.** "The fine-tuned
  BanglaBERT from S3.2" -- and S3.2 ran `role: A`, i.e. on R1. Everyone read the
  sentence correctly, which is why it survived. **Code does not read intent.**

- **Phase 3 is ~20% done and nothing said so.** Progress was tracked against
  `protocol.md`, which is Bangla-only and silent on sect. 3.5, so two whole
  workstreams were invisible rather than late.

- **sect. 5.4's mandatory Limitations sentence was broken by yesterday's own fix** --
  it reads "persona-conditioned", retired 2026-08-10. The sentence defending
  "Simulation" in the title was collateral damage of the terminology change.

### Consequences for downstream steps

- **Phase 4 is blocked on sect. 3.5**, not on verifier training. No symbolic scorer
  -> no Critic -> no loop. This is now the top item in STATUS.
- **RQ4 reduces** to fertility covariate + zero-shot English reference.
- **RQ5 gains a precondition**: the entanglement audit runs before any A-B gap
  is interpreted; a small gap under high entanglement is not evidence of safety.
- **sect. 5.1 is one third smaller** than the spec says (1,440, not 2,160) -- affects
  cost, runtime, and every bootstrap CI in sect. 5.6.
- **Ch.5 carries one combined dev-reuse limitation**, not three footnotes.

### Citations needed

**Tier 7** added to `related_work.md`: `mahmoud2026rubric` upgraded `[ ] -> [x]`
(read in full; the abstract-only reading missed the half that matters), and
`kuai2026entanglement` added `[x]`.

⚠️ **Found via alphaXiv, NOT Consensus** (quota exhausted until 2026-09-01).
⚠️ **Recorded because it bounds both citations:** these papers study policies
**RL-trained** against a reward. We never train a generator (rule 10) -- the loop
reruns a *prompted* model at most three times. Their effect sizes are an **upper
bound** on what our loop can produce, not a prediction. That makes gaming less
likely *and* a null RQ5 less informative. Both halves belong in Ch.5.

---

## 2026-08-11 -- S3.5-prereg: symbolic feature pool pre-registered; IDF replaces the presence rules
**Feeds:** Ch.3 Methods sect. 3.5; Phase 4 Critic
**Artifacts:** `docs/protocol.md` sect."S3.5 pre-commitment", `docs/related_work.md` Tier 8, `docs/references.bib` (+2)

### Numbers
- Feature families fixed: **6** (F1 IDF, F2 length/shape, F3 normalised orthography,
  F4 discourse connectives, F5 sentiment fraction, F6 length-corrected richness).
- Families registered **gameable in advance**: **4 of 6** (F2-F5).
- `ko2019specificity` on movie reviews: Spearman **0.702** vs length baseline **0.581**.
- Our `length_auc`: **0.6764** -- independently in the same regime.
- Deviation rows **48 -> 50**; bib **46 -> 48**.
- Dev-slice decision load **5 -> 3** (hybrid weight and tau moved to dev-plots).

### Decisions made (and why)

- **The pipeline's sect. 3.5 feature pool is replaced before any code was written.**
  Its list is almost entirely presence-based, and `mahmoud2026rubric` shows that
  is the category that gets hacked. **Our sect. 4.2 Reflector names the failing rule
  to the Writer**, so presence rules under this loop function closer to a gaming
  instruction than a scorer.

- **IDF (F1) is the load-bearing addition, and the argument is specific:**
  raising it requires using genuinely rarer, more specific words, which *is* the
  construct. It cannot be satisfied vacuously -- the exact property Mahmoud et
  al. find presence criteria lack. Computable from R1 alone; no external
  resource; rule 7 intact (whitespace tokens, no stemming).

- **Presence rules retained as F2-F5 rather than deleted**, because sect. 3.5
  mandates them and the Reflector needs human-readable rules to name.
  **Each is labelled gameable in advance and its weight reported individually**,
  so a gain arriving only through them is visible as such -- pre-committed as a
  negative result about the hybrid design.

- **Hybrid weight moved off the 82 rows onto the 30 dev-plots' generations.**
  Two reasons: at 1 error in 82 the 0.5-0.8 grid is degenerate; and
  `kapur2026length` show the length-specificity relation is flat or reversed in
  machine-generated text, so a weight calibrated on real reviews is calibrated
  on the wrong distribution.

- **Excluded with stated reasons** rather than silently: imageability/familiarity
  norms (none exist for Bangla), stop-word fraction (no resource; rule 7
  territory), emoji (zero in corpus), standalone name-mention rule (subsumed by
  IDF, since names are naturally high-IDF).

### Findings (things we did not expect)

- 🎁 **The construct was never ours to invent.** RQ1 has been treating
  "engagement specificity" as a project coinage. **Sentence specificity is a
  named task** with prior art to Louis & Nenkova (2011), and
  `ko2019specificity` evaluates it **on movie reviews**. Ch.2 can now cite a
  literature instead of defending a coinage, and **RQ1-H's Gate B becomes
  corroboration of an existing construct rather than the definition of a new
  one** -- a materially stronger position.

- **Their length baseline is 0.581 Spearman against a full system at 0.702.**
  Length being a strong-but-incomplete predictor of specificity is the
  *expected* state of this construct, not a flaw in our data. `length_auc`
  0.6764 sits in the same regime and can be reported as such.

- ⚠️ **An uncomfortable correction to the G-300 post-mortem.**
  `ko2019specificity` reached Cronbach alpha 0.68-0.70 **with nine raters and an
  exclusion rule below 0.3**. Attempt 1 ran **two** raters with no exclusion
  rule. The 2026-08-05 diagnosis blamed scale collapse and Claude's calibration
  advice -- **both stand, but they were not the whole cause.** Specificity
  rating is known to need many raters and we ran the minimum possible. Recorded
  because a post-mortem that names only the causes we already knew is not a
  post-mortem.

### Consequences for downstream steps

- **Ch.2 gains a construct section** citing the specificity literature; RQ1's
  framing shifts from coinage to adoption.
- **The Reflector's rule vocabulary is fixed by F2-F5** -- it can only name what
  the scorer measures, and the gameable families are precisely the nameable ones.
  That tension is registered, not resolved.
- **RQ5 gains a third signal**: per-family symbolic scores logged per attempt;
  presence-family scores rising while Verifier-B stays flat is Mahmoud's
  signature.
- `kapur2026length`'s contrast-set specificity measure is a **candidate for
  sect. 5.4's realism test** -- noted, not adopted, and not to be adopted without
  its own pre-registration.

### Citations needed

**Tier 8** added: `ko2019specificity` `[x]`, `kapur2026length` `[x]` -- both read
in full. ⚠️ Found via **alphaXiv + Scite, NOT Consensus** (quota exhausted until
2026-09-01).

---

## 2026-08-11 -- S3.5: symbolic scorer fitted -- length HURTS, richness helps, F1 held on a rule-7 question
**Feeds:** Ch.3 sect. 3.5; Phase 4 Critic; RQ3
**Artifacts:** `results/s35_symbolic.{json,md}`, `src/symbolic/`, `configs/s35_symbolic.yaml`, `tests/test_symbolic.py`

### Numbers
- Fitted on **82** dev rows, **11** features -> **7.45 rows per feature**.
- Resubstitution macro-F1 **0.6570** (optimistic, labelled as such everywhere).
- **Stratified 5-fold CV 0.5150 +/- 0.0713** -- the honest number.
- Majority baseline **0.3926**. Verifier-A (frozen LaBSE probe) **0.9866**.
- Leave-one-family-out (CV delta when the family is REMOVED):

| Family | CV without | Delta | Gameable? |
|---|---|---|---|
| F3_ortho | 0.4503 | **+0.0647** | yes |
| F6_richness | 0.4764 | **+0.0386** | no |
| F5_sentiment | 0.5338 | -0.0188 | yes |
| F4_connective | 0.5339 | -0.0189 | yes |
| F2_length | 0.6232 | **-0.1082** | yes |

- Tests: **22** new, **150** pass overall.

### Decisions made (and why)

- **F1 (IDF) built but DISABLED, and the run reported without it.** Inviolable
  rule 7 forbids TF-IDF "in the main pipeline ... never in a result". F1 is IDF
  only -- three scalar summaries, no document-term matrix, no encoder replaced
  -- but "never in a result" is unambiguous and F1 would be in one. **Flagged to
  Sabbir rather than decided here**, per CLAUDE.md. `enable_f1` defaults False
  and a test pins that default, so the compliant setting cannot drift on.

- **Cross-validated estimate reported beside resubstitution, not instead of it.**
  The 14-point gap (0.6570 vs 0.5150) at 7.45 rows per feature IS the finding
  about this slice, and hiding either number would hide it.

- **Leave-one-family-out computed on CV only.** Resubstitution deltas at n=82
  measure fitting capacity, not contribution.

- **IDF table would be built from TRAIN rows only** (804), never dev. Building
  it on the fitting slice would leak the fitting distribution into a feature --
  the same shape of error S3.2b found in the label itself.

### Findings (things we did not expect)

- 🔴 **Length HURTS the symbolic scorer.** Removing F2 raises CV from 0.5150 to
  **0.6232**. This is the only delta that exceeds the CV SD (0.0713), so it is
  the one result here worth believing. **The pipeline's own feature list
  includes "length bucket", and at n=82 it is actively harmful** -- almost
  certainly overfitting, since `length_auc` on the full region-A data is 0.6764
  and length is genuinely predictive there. Small-n behaviour, not a
  contradiction of S2e.

- **The two positive contributors are F3_ortho (+0.0647, gameable) and
  F6_richness (+0.0386, NOT gameable).** F6 earning its place is the one piece
  of good news for the hybrid design: the non-gameable family contributes.

- 🎁 **The pipeline's presence-based families contribute NEGATIVELY.** F4
  (connectives) and F5 (sentiment lexemes) both show negative deltas -- removing
  them *helps*. That is the sect. 3.5 list as written, and it corroborates the
  2026-08-11 pre-registration's scepticism about presence rules from a direction
  the search did not supply.

- ⚠️ **Do not over-read any of this.** CV SD is **0.0713** and every delta except
  F2's is smaller than it. Four of the five family effects are inside noise, and
  they are reported as such rather than ranked.

### Consequences for downstream steps

- **RQ3's pre-committed "softened" branch is now the likely one.** Symbolic
  alone is **0.5150** against Verifier-A's **0.9866**; there is no room for a
  2-point hybrid gain on real reviews. The pre-commitment holds and fires.
- **Symbolic's retained purpose is interpretability**, exactly as pre-registered
  -- sect. 4.2's Reflector cannot name a failing rule without it.
- ⚠️ **The Reflector's nameable rules are F3/F4/F5 -- and F4/F5 are the families
  that contribute negatively while being the most gameable.** The component the
  loop can talk about is the component that works least. Registered as a tension,
  not resolved.
- The hybrid weight is unaffected: it is fit on dev-plot generations, not here.

### Rule-7 pilot (added same day, after the ruling question was raised)

**Decision: F1 stays OFF in the result; run once as an explicitly-labelled
pilot, which rule 7 itself permits.** ⚠️ Sabbir delegated ("jeta valo hoy
koro"); the choice and reasoning are Claude's. Reinterpreting an inviolable rule
is not a delegated-decision-sized act -- "breaking any of these invalidates the
thesis" -- so it goes to Sabbir AND the supervisor, dated and signed.

**Enforced structurally, not remembered:** `s35_scorer.py` refuses to run with
`enable_f1: true` unless the config sets `pilot: true` AND the output filename
contains `pilot`. Verified by running it against a copied non-pilot config,
which refused.

| | CV macro-F1 | rows/feature |
|---|---|---|
| F1 off (committed result) | 0.5150 +/- 0.0713 | 7.45 |
| F1 on (**pilot, unquotable**) | **0.6949 +/- 0.0532** | 5.86 |

- 🔴 **F1 leave-one-out delta +0.1798** -- 2.5x the CV SD, an order of magnitude
  above every other family. **Mean rises AND variance falls**, which is not the
  signature of overfitting.
- ⚠️ **Claude predicted the opposite and was wrong.** The stated reason for
  running F1 cautiously was that 14 features on 82 rows (5.86 rows/feature)
  would likely *lower* CV. It produced the largest effect in the study.
  Recorded rather than dropped.
- 🎁 **F1 repairs F2.** Without IDF, removing length *improves* CV by 0.1082 --
  length is actively harmful. With IDF present, length's delta is **+0.0033**.
  Length was a poor proxy for what IDF measures directly.
- 🔑 **The design consequence, which matters more than the accuracy one:** with
  F1, the top two contributors are the two **non-gameable** families
  (F1 +0.1798, F6 +0.0213), while the gameable presence families stay negative
  (F4 -0.0191, F5 -0.0350). **Rule 7 as applied pushes the scorer toward exactly
  the families `mahmoud2026rubric` identifies as the hacked category.** That is
  the substantive argument for an amendment, and it is recorded as evidence for
  a decision, not as one.
- Ruling request added to `docs/supervisor_seal_packet.md` section 6, to travel with
  the signature. **Until a ruling is in `protocol.md`, `enable_f1` stays false.**

### Citations needed

None new. `ko2019specificity` (feature families) and `mahmoud2026rubric`
(gameability annotation) were added 2026-08-11 in Tiers 7-8.

---

## 2026-08-11 -- S3.3: Verifier-A and Verifier-B: built, pre-registered, and not yet run
**Feeds:** Ch.3 Verifier design; Ch.5 RQ5
**Commit:** `65c9a28605d79f72a90db147fa2b47eaff759890-dirty`
**Artifacts:** `configs/s3c_verifier_a.yaml`, `configs/s3d_verifier_b.yaml`,
`src/verifier/train_verifier_a.py`, `src/verifier/train_verifier_b.py`,
`src/verifier/calibration.py`, `tests/test_s3_verifiers.py`,
`notebooks/s3d_verifier_b_kaggle.ipynb`, `docs/protocol.md` §S3.3.
⚠️ **Nothing in `results/`** — see "Numbers" below.

### Numbers

**None yet, and that is the honest state of this entry.** The code, the configs,
the tests and the pre-registration exist; neither verifier has been trained.
Only these are established:

- Data contracts, verified by computation, not assumed: Verifier-A draws
  **804** R1 rows (481/323), Verifier-B draws **888** R2 rows (531/357), both
  evaluated on the same **82** dev rows (53/29). `train ∩ dev = ∅` for both
  roles, `A_train ∩ B_train = ∅`, and G-300 reaches neither.
- **171 tests pass** (150 existing + **21 new**), including the wall assertions.
- The `--dry-run` path executes end to end on CPU: contracts, walls, provenance
  stamp and markdown renderer, with no model and no download.

**Why not run:** Verifier-B needs a GPU. Verifier-A does not, but its own
reproduction check compares against S3.2b's **0.9866**, which was measured on
Kaggle — and `coakley2022implementation` put environment-only variation at
**>6 pp**, while half a dev item is **0.6 pp**. Fitting Verifier-A in a third
environment would risk a spurious "the data moved" stop that means nothing but
"different host". Both therefore run from
`notebooks/s3d_verifier_b_kaggle.ipynb`, and `results/env_snapshot_s3d_kaggle.json`
is mandatory per fact (env).

### Decisions made (and why)

- **Verifier-B's learning rate is fixed at 2e-5 and never selected** — the
  pipeline §3.1 default, 5 seeds at one lr rather than S3.2's two.
  ⚠️ **Sabbir's call, 2026-08-11**, taken from three options presented with
  their costs; the search that produced the options is Claude's.
  `schneider2025overtuning` re-analyse seven HPO benchmark suites and find
  **~10% of runs select a configuration that generalises worse than the
  default**, with the aggravating conditions named as small data, holdout
  rather than CV, binary classification, accuracy-type metric — **all four
  describe this run.** Their recommendation is repeated CV; not tuning at all
  was available and is stronger, so it was taken. Cost accepted: B may be
  slightly weaker than a tuned B would be.
- **Both verifiers are evaluated on the same dev-82.** ⚠️ **Sabbir's call.**
  The alternative was carving B its own slice out of R2, which is closer to the
  split map's literal wording but drops B's training n below 888 and, more
  seriously, measures A and B on different items — after which RQ5's A−B gap
  confounds model difference with item difference and nothing downstream can
  separate them again. Leakage-free either way: `dev ⊂ R1` is held out of A's
  804, and `dev ∩ R2 = ∅` by the frozen split's own contract.
- **The persisted Verifier-B is the seed-42 model, declared before any score
  exists.** Claude's call, recorded as such. Not best-of-five, which would be
  selection on the reporting slice. An **ensemble of all five was considered
  and rejected**: Verifier-A is a single model, and an ensembled B would make
  part of the RQ5 gap a gap between "one model" and "five" — symmetry is worth
  more here than the ensemble's calibration gain. The other four seeds are
  reported as a sensitivity band.
- **`--dry-run` writes to `results/_dryrun/`, never to `results/`.** Claude's
  call, and it is a correction rather than a design: the first dry run wrote
  four files into `results/` containing scores from a random number generator.
  They were deleted within the minute and nothing cited them, but by this
  project's own artifact index a file in `results/` is something a reader may
  check, and "it was obviously a dry run" is not a property the filename
  carried.

### Findings (things we did not expect)

- 🔴 **`split_access.load_training_rows` returned `dev = None` for role B, so
  Verifier-B had no registered evaluation slice at all.** Not a bug in any
  result — no verifier existed — but the gap had survived since the file was
  written, and `tests/test_s3_backbone.py` was actively *pinning* it with
  `assert dev is None`. **A test can protect a gap as effectively as it
  protects a rule**, and this one read as a wall while being an omission. The
  test is amended, not deleted, with the reason in its docstring.
- 🔴 **`protocol.md` claimed Verifier-A was "natively calibrated". It has no
  support.** `zhang2026tabpfn` evaluate nine heads on frozen encoders across
  **22,820 episodes**: a logistic head takes the **best mean rank on accuracy**
  and ranks **below kNN and every in-context head on both ECE and NLL** (Top-1
  ECE 0.069 vs 0.037 / 0.031). The clause is withdrawn and §3.4 temperature
  scaling becomes **mandatory** for Verifier-A. ✅ The **choice** of Verifier-A
  survives — the same paper keeps logistic regression appropriate at high
  dimension and near-ceiling accuracy, which is exactly our regime. ⚠️ Bounded:
  their grid is 10-class and the gap narrows at C=2, so what is recorded is
  *"the claim had no support"*, not *"Verifier-A is miscalibrated"*.
- This is the **fourth** entry in CLAUDE.md's search-first table and the
  cheapest to have caught: the sentence was one day old and no code depended on
  it yet. The three earlier entries each cost a rebuilt instrument, a rewritten
  decision rule, or a withdrawn recommendation.
- ⚠️ **Search index: alphaXiv, not Consensus** (quota exhausted until
  2026-09-01). Recorded in `protocol.md`, `related_work.md` and the `.bib`
  notes, because "searched a different index" and "did not search" are
  different facts that look identical in a bibliography.

### Consequences for downstream steps

- **Phase 3 is Bangla-complete on paper and not on disk.** Pipeline §3.1 asks
  for four verifiers (A/B × bn/en); this delivers **two**, and the English pair
  is scheduled rather than cut (STATUS, 2026-08-11). Phase 3 must be described
  that way and not as "done".
- **Phase 4 unblocks only after the Kaggle run.** §4.2's Critic is
  `0.6×VerifierA + 0.4×symbolic`; the symbolic half was built 2026-08-11, and
  Verifier-A is the remaining input.
- **§3.4's calibration figure now has a pre-committed null that can fire.**
  `test_calibration_reports_the_null_when_there_is_nothing_to_fix` exists
  specifically because RQ1-F's Gate 2 had to be rewritten mid-protocol when its
  null verdict turned out to be nearly unreachable by construction. The same
  failure mode is tested for here rather than discovered later.
- **§3.3's dual-accuracy table remains not producible** (logged 2026-08-08) and
  nothing here changes that.

### Citations needed

Two new, both added 2026-08-11 to `related_work.md` **Tier 9** and
`references.bib`, both read in full:

- `schneider2025overtuning` — Schneider, Bischl & Feurer, AutoML 2025. Cited in
  Ch.3 beside Verifier-B's learning-rate rule.
- `zhang2026tabpfn` — Zhang et al. 2026, arXiv 2607.11007. Cited in Ch.3 beside
  the calibration stage, and in Ch.5 Limitations for the C=2 caveat.

---

## 2026-08-11 -- S3.3: Verifier A/B fitted on Kaggle: A reproduces S3.2b, calibration null fires for B
**Feeds:** Ch.3 §3.3-3.4; Ch.4 §4.2 Critic
**Commit:** `d8b1f5deeb54499e43775a985dd60e054898aa70`
**Artifacts:** `results/s3c_verifier_a.json`, `results/s3d_verifier_b.json`, `results/s3c_verifier_a.md`, `results/s3d_verifier_b.md`

### Numbers
- `results/s3c_verifier_a.json`
  - `role` = A
  - `model` = frozen sentence-transformers/LaBSE + L2 logistic
  - `n_train` = 804
  - `train_class_counts` = {'0': 481, '1': 323}
  - `n_dev` = 82
  - `dev_class_counts` = {'0': 53, '1': 29}
  - `dev_macro_f1` = 0.986555
  - `dev_errors` = 1
  - `one_dev_item_in_macro_f1` = 0.012195
  - `s3b_reference_macro_f1` = 0.9866
  - `reproduces_s3b` = True
  - `artifact` = artifacts/verifier_a.joblib
  - `hyperparameters_selected` = none -- C, penalty and max_iter are library defaults fixed in the config, per protocol.md S3.3 decision 1
- `results/s3d_verifier_b.json`
  - `role` = B
  - `verdict` = COMPETENT_EVALUATOR
  - `dry_run` = False
  - `model` = csebuetnlp/banglabert
  - `n_train` = 888
  - `train_class_counts` = {'0': 531, '1': 357}
  - `n_dev` = 82
  - `dev_class_counts` = {'0': 53, '1': 29}
  - `learning_rate` = 2e-05
  - `hyperparameters_selected` = none — one lr, taken from pipeline §3.1
  - `artifact_seed` = 42
  - `artifact_selection_rule` = global_seed, pre-declared; NOT best-of-five
  - `dev_macro_f1_artifact` = 0.959666
  - `dev_macro_f1_mean_over_seeds` = 0.967442
  - `dev_macro_f1_sd_over_seeds` = 0.015839
  - `one_dev_item_in_macro_f1` = 0.012195
  - `s3_banglabert_on_R1_for_context` = 0.9647
  - `artifact` = artifacts/verifier_b.joblib
- `results/s3c_verifier_a.md`
  - (see file; 2017 bytes)
- `results/s3d_verifier_b.md`
  - (see file; 2095 bytes)

**Calibration (§3.4), both verifiers, n = 82, 5 bins, temperature fitted in-sample:**

| | Verifier-A (frozen LaBSE + L2 logistic) | Verifier-B (BanglaBERT, fine-tuned) |
|---|---|---|
| Temperature | **0.10918** (T < 1 -> sharpens) | **1.09949** (T > 1 -> softens) |
| ECE before | **0.11836** | **0.01644** |
| ECE after | 0.00537 | 0.00996 |
| ΔECE | +0.11299 | +0.00649 |
| ΔECE 95% CI | **[+0.07431, +0.13489]** | **[-0.00661, +0.00705]** |
| Brier before -> after | 0.03056 -> 0.00934 | 0.02777 -> 0.02733 |
| NLL before -> after | 0.15154 -> 0.02823 | (see file) |
| Verdict | **CALIBRATION_IMPROVED** | **CALIBRATION_NOT_ESTABLISHED** |

Verifier-A reliability bins, before: `[0.4,0.6)` n=5 conf 0.543 acc 0.800;
`[0.6,0.8)` n=7 conf 0.721 acc 1.000; `[0.8,1.0)` n=70 conf 0.908 acc 1.000.
After: `[0.6,0.8)` n=3 conf 0.750 acc 0.667; `[0.8,1.0)` n=79 conf 0.998 acc 1.000.

Verifier-B per-seed macro-F1 (lr 2e-05): 42 -> 0.959666 (3 errors), 43 -> 0.972884 (2),
44 -> 0.973325 (2), 45 -> 0.944781 (4), 46 -> 0.986555 (1).

### Decisions made (and why)
- **None -- mechanical execution of the S3.3 build committed in `d8b1f5d`.** Every
  choice that governs this run (Verifier-A's C/penalty/max_iter as config-fixed
  library defaults; Verifier-B's single lr from pipeline §3.1 with no tuning;
  seed 42 pre-declared as the shipped artifact rather than best-of-five) was made
  and justified in the preceding entry. Recorded here explicitly because a run
  that decides nothing is a different object from a run whose decisions went
  unwritten, and the two look identical in a diff.
- The one thing worth naming as *held*, not decided: `artifact_selection_rule` =
  `global_seed, pre-declared; NOT best-of-five`. Seed 46 reached 0.986555 -- equal
  to Verifier-A -- and was not shipped. That is the rule costing us the better
  number, which is the only circumstance under which the rule is evidence of
  anything.

### Findings (things we did not expect)
- 🔴 **Verifier-A was badly miscalibrated: ECE 0.11836, the largest miscalibration
  quantity in Phase 3.** The withdrawal of protocol.md's "natively calibrated"
  clause one day earlier was therefore not a documentation tidy-up -- it removed a
  claim that the very next run refuted by ~12 points. `zhang2026tabpfn` predicted
  the direction of this from 22,820 episodes, and the search that surfaced it ran
  *before* the code existed. Fourth entry in CLAUDE.md's search-first table, and
  the first one where the search's payoff can be quantified.
- 🔴 **The miscalibration is UNDER-confidence, not over-confidence.** T = 0.109
  multiplies the logits by ~9.2. The bins say it plainly: 70 of 82 items sat at
  mean confidence 0.908 while being 100% correct. Cause is not mysterious --
  L2 shrinkage at C=1.0 over 768-d normalised embeddings compresses the logits,
  while the underlying decision is right 81 times in 82. **This matters for how
  Ch.3 is written:** `guo2017calibration`'s entire framing is that modern networks
  are over-confident (T > 1). Ours is the opposite, and citing that paper for the
  *method* while implying its *finding* would misreport it.
- ✅ **The A/B asymmetry is the cleanest result in this step, and it runs in the
  textbook direction.** Verifier-B -- fine-tuned -- had ECE 0.01644 and needed
  T = 1.099, i.e. it was mildly *over*-confident in the classic sense and already
  near-calibrated. The frozen probe was the badly-calibrated one. That is exactly
  `zhang2026tabpfn`'s ranking of logistic heads against fine-tuned alternatives,
  reproduced on our own data without being aimed at.
- ✅ **The pre-committed calibration null fired, on B.** ΔECE CI
  [-0.00661, +0.00705] straddles zero -> `CALIBRATION_NOT_ESTABLISHED`, and
  Brier barely moved (0.02777 -> 0.02733), independently agreeing. This is the
  outcome `test_calibration_reports_the_null_when_there_is_nothing_to_fix` was
  written for after RQ1-F's Gate 2 had to be rewritten mid-protocol for having a
  null that was nearly unreachable by construction. **This null was reachable and
  it was reached.** A null that can fire and does is worth more than the positive
  result beside it.
- ⚠️ **The bootstrap CI does not propagate uncertainty in T.** It resamples the 82
  dev items while holding T fixed at the value fitted on all 82. So
  [+0.07431, +0.13489] is an interval on ΔECE *given this temperature*, not given
  the procedure -- and +0.11299 is an **upper bound** on what a held-out T would
  deliver. `calibration.py` already records that T is in-sample; this specific
  consequence for the interval was not stated and must be, in Ch.3 and Ch.5.
- ⚠️ **T = 0.10918 is a ~9x logit multiplier fitted on 82 rows containing one
  error.** The NLL objective sharpens as far as the near-absence of errors lets
  it. If the true error rate is even 3-4%, this temperature will be over-confident
  out of sample. 82 rows cannot do better; the honest report is the number plus
  this sentence, not the number alone.
- ✅ Verifier-A reproduced S3.2b **exactly** (0.986555 vs 0.9866 reference,
  `reproduces_s3b` = True), so the reproduction gate passes and the artifact is
  the same object S3.2b measured.

### Consequences for downstream steps
- 🔴 **New open decision for §4.5: does the τ sweep run on calibrated or
  uncalibrated Verifier-A scores?** This is no longer hypothetical -- the
  post-scaling bins show **79 of 82 items at mean confidence 0.998**. Calibrated
  Verifier-A output is very nearly binary, so a threshold sweep over it has almost
  no resolution left to sweep. §3.4 was demoted to descriptive on 2026-08-08, but
  the same amendment said τ "rests on this confidence", so the two halves now
  pull in opposite directions. **Registered in STATUS as open; to be settled by a
  literature search before Phase 4 begins, not in passing.**
- **Phase 4's Critic (§4.2, `0.6xVerifierA + 0.4xsymbolic`) is unblocked.** Both
  inputs now exist on disk: the symbolic half from 2026-08-11 and Verifier-A here.
  The open decision above governs *which* Verifier-A score it consumes.
- **Verifier-B's wall holds and is now load-bearing.** B scores S6 only and never
  enters the loop (CLAUDE.md rule 6). Its calibration null is a property of the
  scorer, so it must be reported in Ch.5 beside the Goodhart test rather than
  folded into the Ch.3 calibration figure.
- **Phase 3 remains Bangla-only.** This delivers the two Bangla verifiers; the
  English pair (§3.1's A/B x bn/en) is still scheduled, not cut. Nothing here
  changes that, and Phase 3 must not be described as "done".
- **§3.3's dual-accuracy table remains not producible** (logged 2026-08-08).

### Citations needed
- `guo2017calibration` -- already in `references.bib`. **Its Ch.3 annotation needs
  amending**: cite it for temperature scaling as a *method*, with an explicit note
  that our observed direction (T < 1, under-confidence) is opposite to its
  reported finding. Cited as-is it would misdescribe our own result.
- `zhang2026tabpfn` -- already added 2026-08-11 (Tier 9). Its Ch.3 placement beside
  the calibration stage is now supported by a measured number rather than an
  anticipated one; update the annotation to say so.
- ⚠️ **No new search was run for this entry** -- it executes an already-searched
  design. The §4.5 τ decision above *does* require one and has not had it.

---

## 2026-08-11 -- S4: Phase 4 pre-registration: the loop, w, tau scoping, the generator pilot
**Feeds:** Ch.3 Methods (SS4.1-4.2), Ch.4 SS4.5
**Commit:** `d84efd392225385095e51310730f75b2af2cae60-dirty`
**Artifacts:** `docs/protocol.md` §"S4 pre-commitment" (new section + 5 deviation
rows); `docs/research_pipeline_en.md` (second maintenance pass); `docs/STATUS.md`
(self-contradiction corrected, step 12 added); `docs/related_work.md` Tier 10;
`docs/references.bib` (6 entries). **No code, no config, no result files** — that
is the point of the entry.

### Numbers
- **No new measured number exists**, and none may. Phase 4 has produced no
  generation, so `w`, τ, τ\*, `quality(τ)`, α_lo and α_hi are all undefined.
- Numbers *carried in* and verified on disk rather than read from STATUS:
  Verifier-A dev macro-F1 **0.9866** (T = 0.1092, `CALIBRATION_IMPROVED`),
  Verifier-B **0.9597** at seed 42 (`COMPETENT_EVALUATOR`,
  `CALIBRATION_NOT_ESTABLISHED`), both committed in `0d2578d`.
- `check_constants.py` after this pass: **115 constants carry a reason, 0
  DECISION-tier do not, 0 openly flagged unresolved** (41 KNOB-tier unstated,
  never enforced). Exit 0.
- ⚠️ **`pytest` is not installed in this session's sandbox, so the 171-test
  suite was NOT run.** This commit touches only Markdown and BibTeX, so no test
  outcome could have changed — but "not run" is recorded rather than implied.

### Decisions made (and why)
- **τ scoping — hierarchical partial pooling across the two axis levels**, not
  one global τ and not two independent ones. Alternatives were exactly those
  two, and both were put to Sabbir. ⚠️ **Provenance: Sabbir delegated —
  *"research kore dekho konta vlo hoy"* — so the choice and reasoning are
  Claude's, endorsed not authored,** as for decisions 12, 14, 16 and 19. Reason:
  `2605.14260` says a single pooled threshold hides cross-group heterogeneity,
  while its own title says group-conditional thresholds cost calibration sample
  — and `2607.24562`'s estimator resolves the conflict by degrading to whichever
  end the data supports. The shrinkage is **estimated from the within/between
  variance ratio, not chosen**, which is what keeps it clear of the standing
  hand-written-constant rule.
- **The 20-generation pilot gets a decision rule, with `TIE` pre-committed** and
  a declared non-performance tie-break. Alternative was §4.4 as written — a
  budget with no criterion, i.e. the same defect as `0.6/0.4`. Reason: S3.2
  returned `TIE` over seven arms and five seeds with a between-arm spread
  smaller than one arm's seed SD; expecting 20 generations to separate two
  models is not defensible, so the rule is fixed before any output is seen.
- **The pilot is not scored by Verifier-A.** Alternative was to reuse the
  in-loop judge for convenience. Reason: pre-selecting the generator against
  the judge that will grade it is a soft form of the evaluator–policy
  co-adaptation `wang2026hacking` name, and rule 6 exists to prevent it.
- **Rule 6 restated as a code-level constraint** (no Verifier-B import under
  `src/agents/`, enforced by a test) rather than as prose. Reason: the
  2026-08-11 Verifier-B data-definition row records this wall coming one
  training run from collapsing through *ambiguity*, not disagreement.
- **`w` is left with no value and three pre-committed outcomes**, including
  `SYMBOLIC_INERT` as a publishable negative result. Nothing was decided about
  its magnitude and nothing could be.

### Findings (things we did not expect)
- 🔴 **`docs/STATUS.md` contradicted itself about whether Phase 3 had run**, and
  a fresh session read the stale half, believed it, and reported Phase 4 as
  blocked. Sabbir corrected it from memory — *"verifier A to ache maybe.
  artifacts e. check koro to."* **Fourth instance of the pattern the file
  already names**, and the worst of the four, because the two halves disagreed
  on whether the next phase could begin at all.
- 🔴 **The struck `0.6/0.4` and the struck *"first-pass 60–70%"* were still live
  in FOUR places in the normative pipeline** — checklist steps 16 and 17, the S5
  stage-contract Gate G4, and the §4.5 bullet list four lines below the box that
  strikes them. Step 17 additionally still cited **closed** decision 17 *and its
  refuted premise*. **Both strikes had been applied to the argument and not to
  the instructions.**
- 🔑 **The general shape, now three-for-three** (`0.6/0.4`, line 8's Bangla
  mirror, these four): corrected and uncorrected text living in the same file
  with only one copy edited. Striking a number means grepping the file for it,
  not editing the paragraph where the argument happens to live — a reader
  scanning a checklist or a gate table never reaches the prose box.
- ⚠️ **The search overturned Claude's own recommendation, again.** A global τ had
  already been recommended to Sabbir as the conservative option before the
  search ran on it. It is not conservative. Fifth entry in CLAUDE.md's
  search-first table.
- 🎁 **The previous entry (S3.3) closed itself with *"the §4.5 τ decision above
  does require [a search] and has not had it."*** That gap is now closed by this
  entry — a small demonstration that the notebook's own flagged debts get paid.

### Consequences for downstream steps
- **Step 16 (build the loop) may now proceed**, against §S4 rather than against
  §4.2 alone. `configs/s4_loop.yaml` and `configs/s4_pilot.yaml` must carry a
  `# ref:` to §S4 on every decision constant.
- **`requirements.in`'s Phase-4 block must be uncommented** (`langgraph`,
  `chromadb`, `groq`, `google-generativeai`) and `requirements.lock.txt`
  regenerated by `env_snapshot.py` — never hand-edited.
- **§4.6's failure taxonomy is under-specified.** Its four categories (*wrong
  sentiment / too short / off-topic / template repeat*) have **no register or
  honorific category**, and `2605.22487` documents exactly that failure mode in
  Bangla generation. Flagged now; the taxonomy is hand-coded over 50 three-time
  failures, so the category list must be fixed before coding starts.
- **Decision 10 (prompt parity) is promoted from "blocks Phase 5" to "due before
  the τ sweep is interpreted"** — §5.1 row 1 *is* α_lo, so an under-specified
  row-1 prompt inflates the loop's apparent gain, which is precisely the
  artefact Huang et al. §5 document.
- **`axiv2607_24562_hierarchicalcrc` must be read in full before the τ sweep
  runs.** Its estimator is being *adopted*, not merely cited, and the entry rests
  on an abstract.

### Citations needed
- Six new entries added to `docs/references.bib` and `docs/related_work.md`
  **Tier 10**: `axiv2607_24562_hierarchicalcrc`, `axiv2605_14260_fairnessburden`,
  `axiv2605_05562_socioconformal`, `axiv2606_29403_selforganizedcp`,
  `axiv2605_10405_bestmodelid`, `axiv2605_31483_benhallueval`,
  `axiv2605_22487_banglahonorific`.
- ⚠️ **Index used: alphaXiv**, not Consensus (quota exhausted to 2026-09-01).
- 🔴 **Reading depth is ABSTRACT ONLY for all of them**, and 🔴 **author lists are
  UNRESOLVED** — the alphaXiv discovery call returns title, ID, URL and date but
  no authors, so the `author` field is an explicit placeholder rather than an
  inference. Both gaps are flagged in the `.bib` header and in Tier 10, and both
  must be closed before the bibliography enters the thesis. Guessing an author
  list from memory is the defect CLAUDE.md's do-not-invent rule names, and it
  would look identical to a correct one.

---

## 2026-08-11 -- S4.1: the R1-only RAG index: built, tested, NOT yet run
**Feeds:** Ch.3 Methods SS4.2 (Researcher)
**Commit:** `ffe34444fa98f6b4d39f86244796f8982cb5f1ad-dirty`
**Artifacts:** `src/agents/build_index.py`, `configs/s4_index.yaml`,
`tests/test_s4_index.py`, `requirements.in` (Phase-4 block enabled).
🔴 **No result files.** `results/s4_index_manifest.{json,md}` will exist only
after the build runs in an environment that has `chromadb` and
`sentence-transformers`; this session's sandbox has neither.


### Numbers
- ✅ **RUN 2026-08-11 on Sabbir's host** (Windows-11, Python 3.13.3), commit
  `14d3170`. `results/s4_index_manifest.{json,md}` exist.
- **886 rows indexed**, partition **R1**, axis levels **534 / 352**, encoder
  `sentence-transformers/LaBSE`, cosine, collection `r1_regionA_k2`.
- **`r2_ids_present` = 0, `gold_ids_present` = 0.**
- Row-set digest (SHA-256 over sorted ids):
  `85fc2d7d7ad3281b9dd99a7a0a01f8221a5e7ab762d1c69a0924bbc4468b45bb`
  — **byte-identical to the pre-run dry-run's digest**, so the build indexed
  exactly the rows the contract check had already cleared. That equality is the
  point of computing the digest in both places.
- ⬛ superseded: ~~Dry-run only. **The index has NOT been built** — `chromadb`
  and `sentence-transformers` are absent from this session's sandbox.~~ True
  when written; the build ran within the hour.
- What the dry-run resolves, which is the part that matters for the wall:
  **886 R1 region-A rows**, axis levels **534 / 352**, row-set digest
  `85fc2d7d7ad3281b...`, **0 R2 ids, 0 Gold-300 ids**.
- 886 = **804** (Verifier-A's training rows) + **82** (dev). See the decision
  below — that is deliberate, not an off-by-something.
- `tests/test_s4_index.py`: **6/6 pass.** Full suite could not be run:
  `pytest` is not installed here, and `test_s3_backbone`, `test_s3_verifiers`
  and `test_symbolic` require it. Of the tests that run standalone, all pass.

### Decisions made (and why)
- **The dev-82 reviews ARE in the RAG index** (`hold_out_dev=False`). Alternative
  was to hold them out, costing 82 of 886 exemplars. Reason: the index is not a
  fitted object — nothing is estimated from those rows — and the τ sweep operates
  on **dev-plots** (Bangla film synopses), not dev reviews, so no threshold is
  tuned on anything the index supplies. ⚠️ **The residue is real and is
  disclosed, not buried:** a dev review can appear as a Writer exemplar while
  also being in the slice Verifier-A's temperature was fitted on. Logged as a
  sixth use of the 82 rows under the dev-reuse deviation. Reversible in one
  config line if that disclosure is judged insufficient.
- **Rules 4 and 5 are enforced twice, by two different mechanisms.**
  `split_access` takes a **role**, so no config can name R2; then
  `assert_rag_contract` re-checks resolved ids against the split map directly.
  Alternative was to trust `split_access` alone. Reason: the frozen split is a
  *promise* (inviolable rule 3) and the second check is a *mechanism*, and they
  fail differently — if the map is ever edited, only the second one notices.
- **Rule 6 is enforced by an AST scan, not a substring search.** Alternative was
  a grep. Reason: a grep passes a file containing `# never import verifier_b`
  and fails one that mentions it in a docstring — wrong in both directions. The
  precedent is `check_constants.py`'s two loopholes from earlier today, where
  **writing about the gap closed the check**.
- **The import guard has a twin test proving it can fail.** Reason: RQ1-F's
  Gate 2 was rewritten mid-protocol when its null verdict turned out unreachable
  by construction. A guard whose failure branch cannot fire certifies nothing.
- **Building and querying are separated into different modules.** Reason: so
  that *"the index contains the wrong rows"* and *"the query is wrong"* can never
  be the same bug.

### Findings (things we did not expect)
- 🔴 **The RAG index §4.2 assumes did not exist in any form** — no index, no
  config, no script. §4.2 reads *"queries ChromaDB, top-10, within same persona
  label, R1 index only"*, which is written as a description of an existing
  system, and that is why nobody noticed. **Step 16's real prerequisite, found
  only when the Researcher was about to be written.**
- 🔑 **The general form, recorded because it may hide elsewhere in §4:
  a contract that names a resource does not create it.** §4.2 also names
  prompt templates, an exemplar-overlap log and a feedback renderer in the same
  register. Each should be checked for existence before it is assumed.

### Consequences for downstream steps
- **The Researcher cannot be written until the index is actually built**, and
  the build needs `chromadb` + `sentence-transformers` in a real environment.
  This is now the top of the Phase 4 queue.
- **`requirements.in`'s Phase-4 block is uncommented** (`langgraph`, `chromadb`,
  `groq`, `google-generativeai`). ⚠️ **`requirements.lock.txt` is NOT
  regenerated** — it must be produced by `env_snapshot.py` in Sabbir's own
  environment, because a lock written from this sandbox would pin the wrong
  machine. Fact (env) already requires two environments to be disclosed in the
  appendix; this would have quietly added a third.
- **This step is deliberately recorded as "built, NOT run"**, and `STATUS.md`
  says so in the same words. The S3.3 row said exactly that, was completed, and
  then told a fresh session Phase 4 was blocked — **the correction earlier today
  is the reason this entry is explicit about which half is true.**

### 🔴 Post-run addendum — two provenance problems the lock file exposed

Neither is the index's fault; both surfaced because `env_snapshot.py` printed
the local versions, and both bind on the **Critic**, not on this step.

1. **`results/env_snapshot_s3d_kaggle.json` does not exist.** STATUS's own
   next-action item called it *mandatory (fact (env))*. Both verifiers were
   trained on Kaggle and **no environment snapshot was captured for that run** —
   `results/s3c_verifier_a.json` records only `Linux-6.12.90+`, Python 3.12.13.
   Fact (env) obliges us to state which environment produced which result; for
   S3.3 we currently cannot. **Not recoverable without re-running**, and the
   artifacts are committed, so what is available is the disclosure.
2. **The loop will run in a materially different environment from the one its
   in-loop judge was measured in.** Here: Windows-11, Python 3.13.3,
   **transformers 5.14.1**, sentence-transformers 5.6.1, sklearn 1.9.0, numpy
   2.4.6. There: Linux, Python 3.12.13 — and S3.2 was *deliberately* pinned to
   **transformers < 5** after 5.x broke an arm. **Coakley et al. put
   environment-only variation above 6 pp; Verifier-A's reproduction gate is
   0.6 pp.** An order of magnitude apart.
   ⚠️ Noted while checking: `requirements.lock.txt` has recorded transformers
   **5.14.1 since 2026-07-30** and is unchanged by today's install — so the
   committed lock has never described the environment that produced the S3
   numbers. Consistent with fact (env)'s two-environment disclosure, but worth
   saying plainly rather than leaving implied.

**`src/agents/preflight.py` answers (2) by measurement rather than argument**,
and is **read-only by construction**: it loads the committed artifact and the
committed per-item predictions and diffs them against predictions recomputed
here. It never refits and never writes to `artifacts/` or `results/s3c_*`.
🔑 **That restraint is the whole design** — re-running `train_verifier_a.py`
locally would overwrite the Kaggle artifacts with locally-fitted ones and then
agree with itself, **which would look exactly like success**. Verdict is
pre-committed and two-outcome (`HOST_INVARIANT` / `HOST_DEPENDENT`), reported in
**items** (1 item = 0.0122 macro-F1). `HOST_DEPENDENT` is not automatically a
defect, but it makes the loop's scores attributable to this host rather than to
`s3c_verifier_a.json`, and the two may not be averaged.

⚠️ **`data/rag/` is gitignored.** The 4.7 MB Chroma SQLite is a build artifact
fully regenerable from `data/cleaned` + the frozen split + the config. What is
committed is the **manifest and its digest** — strictly better evidence than the
blob, because a digest is readable and a binary is not.

### Citations needed
- None new. This step implements already-registered contracts (inviolable rules
  4, 5, 6; pipeline §4.2; `protocol.md` §S4). **No search was run for it, and
  none was needed** — recorded rather than omitted, since a silent absence and a
  considered one look identical.
- `coakley2022environment` — already cited for S3.2's environment argument; the
  addendum above is its second load-bearing use, now about the *inference* host
  rather than the training host. Its `related_work.md` annotation should say so.

---

## 2026-08-11 -- S3.5b: persist the symbolic scorer; and the S3.5 numbers reproduce across a THIRD environment
**Feeds:** Ch.3 SS3.5, Ch.4 SS4.2 Critic
**Commit:** `e6b8ce1559c613123e81723cfaa32f03be36298f-dirty`
**Artifacts:** `artifacts/symbolic_scorer.joblib`, `results/s35_symbolic.json` (re-run, numbers identical), `src/symbolic/s35_scorer.py`, `configs/s35_symbolic*.yaml`, `.gitignore`


### Numbers
- **Every headline number is IDENTICAL** to the 2026-08-10 run: resubstitution
  **0.657028550645572**, CV **0.5150303030303031 ± 0.07125600481805267**,
  majority **0.3925925925925926**, 11 features, `enable_f1 = False`. The whole
  `leave_one_family_out` table compares equal as a dict.
- **max |Δ coefficient| = 1.932e-14** — float noise, ~11 orders of magnitude
  below the 1e-3 at which any coefficient would be read differently.
- New artifact: `artifacts/symbolic_scorer.joblib`.

### Decisions made (and why)
- **Persist the fitted pipeline as a joblib artifact**, keyed alongside the
  feature names in fitted order. Alternative was to rebuild the scorer from the
  11 coefficients in `results/s35_symbolic.json`. **That alternative does not
  work**: the estimator is `StandardScaler + LogisticRegression`, and the JSON
  has no intercept and no scaler mean/scale. The fitted object was not
  recoverable from anything committed.
- **Feature names travel inside the artifact.** Reason: the Critic must rebuild
  the feature vector in exactly the fitted order, and a mismatch must raise
  rather than score a permuted vector — which would look like a working Critic.
- **Rule 7's guard extended to the artifact path.** Reason: the existing guard
  covered the *result* path only. A result file is read by a human; an artifact
  is loaded silently and its contents never appear on screen, so an IDF-enabled
  scorer at the default artifact path would put rule-7 features into every
  generation's score with nothing visible to show it. `enable_f1` is also
  recorded *inside* the artifact, and the Critic will refuse an artifact
  carrying `True`.
- **`artifacts/pilot_*` is gitignored.** Reason: a committed pilot artifact is a
  file a future session can load by path without ever seeing the banner that
  explains what it is.

### Findings (things we did not expect)
- 🔴 **S3.5's original numbers were produced in a THIRD environment, and it was
  never disclosed.** The superseded provenance block reads
  **`Linux-6.8.0-124-generic`, Python 3.10.12** — which is neither Kaggle
  (Python 3.12.13, where both verifiers were fitted) nor Sabbir's thesis machine
  (Windows-11, Python 3.13.3). It is the assistant's own sandbox. **Fact (env)
  commits us to reporting *two* environments and stating which produced which
  result; there have been at least three.**
- 🎁 **And the same run is the reassurance.** Re-fitted on Windows / Python
  3.13.3 / sklearn 1.9.0, every reported metric reproduces **exactly** and the
  coefficients move by 1.9e-14. So the symbolic scorer is **host-invariant at
  the precision anything is read at** — unlike Verifier-A, whose probabilities
  moved by 1.07e-06 across hosts. The difference is expected (11 hand-computed
  text features vs a 768-d neural encoder) but it is now measured rather than
  assumed, on both halves of the Critic.
- ⚠️ The re-run **overwrote** `results/s35_symbolic.json`. No number changed, so
  nothing is lost — but the pre-commit hook caught the staged `results/` diff
  and forced this entry, which is the second time today the hook has been the
  thing that noticed.

### Consequences for downstream steps
- **The Critic is now buildable**: both halves have loadable artifacts.
- **`docs/dataset_card.md` / Ch.5's environment disclosure must name three
  environments, not two**, and say which produced which result: Kaggle
  (verifiers, backbone ablation), the assistant sandbox (S3.5's original fit —
  now superseded by the Windows re-fit), and the thesis machine (RAG index,
  S3.5 as committed, and the whole Phase 4 loop). Fact (env) as written is
  already violated by the file it governs.
- **A rule to carry forward:** every remaining Phase 4 artifact should be
  produced on the machine that will run the loop, and the reason is now
  measured rather than argued.

### Citations needed
- None new. `coakley2022environment` gains a third use — its >6 pp
  environment-only variation is the reason these two host comparisons were run
  at all, and both came back far below it.

---

## 2026-08-11 -- S4.5: generator preflight, secrets, the Researcher and the one prompt renderer
**Feeds:** Ch.3 Methods SS4.2, appendix (prompt templates verbatim)
**Commit:** `933e719ceff947ecb8f4f4f32dd2b42c50e23815-dirty`
**Artifacts:** `src/agents/{researcher,prompts,groq_preflight}.py`, `src/common/secrets.py`, `tests/test_s4_{researcher,prompts}.py`, `tests/test_secrets.py`, `.env.example`, `results/s4_groq_preflight.json`


### Numbers
- **Groq auth OK; 15 models served to this account.** All three registered IDs
  present: `llama-3.3-70b-versatile` (arm A), `openai/gpt-oss-20b` (arm B),
  `llama-3.1-8b-instant` (fallback).
- ⚠️ **No rate-limit headers on `/models`** — so **the account tier is still
  unknown**, and the whole runtime plan (6,000 TPM free vs 250K TPM developer,
  ~40×) rests on it. Resolved by the first generation call, not before.
- Prompt size, measured on real data: synopsis **695** chars mean, ten exemplars
  **~640**, definition **1,079** → **~2,416 chars**. Tokens **not** computed:
  Bangla fertility is an unmeasured covariate of our own (§1.2).
- Tests: `test_s4_researcher` 6/6, `test_s4_prompts` 10/10, `test_secrets` 6/6,
  `test_s4_index` 6/6, `test_s4_state` 7/7.
- 🔴 `pytest` is absent from the assistant sandbox, so `test_s3_backbone`,
  `test_s3_verifiers` and `test_symbolic` were **not** run.

### Decisions made (and why)
- **Secrets in `.env` with a ten-line reader, not `python-dotenv`.** Sabbir's
  call on location; the reader is mine. Adding a dependency would edit
  `requirements.in`, force a reinstall, and regenerate `requirements.lock.txt`
  — a provenance artifact that appears in the appendix. Not worth it for this.
- **`redact()` runs on everything written.** The JSONL trace is *designed* to
  record everything, which is exactly what makes it the likeliest place for a
  key to reach git — and a committed key is not removed by deleting it later.
- **The Researcher embeds the whole synopsis** rather than key-phrases. Forced:
  TF-IDF extraction is rule 7, an LLM call would break its own contract and add
  an uncounted call to E[calls]. Deviation logged.
- **One prompt renderer.** Row 1 is `render(exemplars=(), feedback=None)`, so
  decision 10 is a property of the code rather than a thing to remember.
- **The target-level line goes AFTER the definition.** Naming the target first
  would have the model read the two-level contrast already knowing its side,
  turning the other level's description into a list of things to avoid — the
  negative constraint `2601.08070` warns about, arriving by ordering instead of
  by wording.

### Findings (things we did not expect)
- 🔴 **Two prompt bugs, both found by PRINTING the rendered prompt and reading
  it — neither by the eight tests that were already passing.**
  (i) `target_level` was validated and then **discarded**; the prompt never said
  which level to write, while the definition describes both. Every generation
  would have looked well-formed, the Critic would have scored it against a level
  nobody asked for, and **the axis-control result would have been noise with no
  visible cause.**
  (ii) The target line used an ASCII digit — *"স্তর 1"* — while the definition's
  own headings use Bengali digits, *"স্তর ১"*. **The prompt pointed at a section
  by a name that section does not have.**
  🔑 **The lesson is about the method, not the bugs: tests check the properties
  you thought of. Reading the artifact catches the ones you did not.** The
  rendered prompt is now printed and inspected before any generation runs, and
  both bugs have tests so they cannot return.
- 🎁 **My own test caught my own bug in the Researcher** — `build_query(["", " "])`
  appended a trailing space, because an all-whitespace list is still truthy.
  That query differs from attempt 1's by whitespace alone, which is enough to
  change the embedding and make *"re-retrieval changed the exemplars"* true for
  no reason.
- **The search summary about Groq deprecations was wrong** and the authoritative
  docs disagreed with it — logged in `protocol.md`; §S4 decision 3's *"never from
  memory"* now reads *"never from a search summary either"*.

### Consequences for downstream steps
- **The tier question blocks any firm runtime plan** and is answered by the
  first generation call. Until then the ~30-hour estimate for Phase 5 stands as
  a free-tier worst case.
- **Bangla tokenizer fertility (§1.2) is now on the critical path** for the same
  reason — it converts a chars→tokens range into a number.
- **The Writer is the next component** and must carry 429 backoff plus
  per-generation JSONL append. S3.2 attempt 1 lost ~4 GPU-hours at arm 6 of 7
  because a long run could not resume; a ~30-hour API run has the same shape.
- **`enable_f1` remains false**; the Critic must refuse a symbolic artifact
  carrying `enable_f1=True`, which is not yet written.

### Citations needed
- No new references. The prompt design cites already-recorded work:
  `2601.08070` (ordering of the target line), `2502.15603` / `2402.10588` /
  `2606.08994` / `2606.19668` (the two language arms), `huang2024selfcorrect`
  (§5, why parity is structural). **No search was run for this step and none was
  needed** — it implements already-searched decisions, recorded rather than
  omitted so that a silent absence and a considered one do not look alike.

---

## 2026-08-17 -- S4.dev: attempt-1 dev-plot generations, free length
**Feeds:** Ch.4 Phase 4; §4.5 (w, tau); §5.4 realism
**Commit:** `07ef398881083d41f9e1b545c4adb8b4407387eb-dirty`
**Artifacts:** `results/s4_devplot_generations.md`, `results/s4_devplot_generations.json`

### Numbers
- `results/s4_devplot_generations.md`
  - (see file; 1648 bytes)
- `results/s4_devplot_generations.json`
  - `NOT_A_RESULT` = True
  - `banner` = Attempt-1 dev-plot generations. The substrate `w` and τ are fitted on. No Critic ran; no quality claim is made here.
  - `n_generations` = 120
  - `level_length_gap_words` = {'bn': -24.766666666666666, 'en': -33.96666666666666}
  - `corpus_level_gap_words` = 4.27
  - `length_diagnostic` = {'bn': 'GAP_BELOW_CORPUS', 'en': 'GAP_BELOW_CORPUS'}

### Decisions made (and why)
- **Ran attempt 1 only, with no Critic and no Reflector.** The Critic requires
  `w` and tau, and both are estimated *from these generations* (S4 decisions 1,
  2, 19). Running the loop first would mean choosing a `w` in order to fit `w`.
  The alternative -- fitting `w` on the 82 human dev rows -- was already
  rejected on 2026-08-11: `kapur2026length` show the length/specificity relation
  is flat or reversed in machine text, and this run confirms it on our own data.
- **A length-controlled second condition is registered rather than replacing
  this one.** Sabbir delegated the choice; the reasoning and the 20-word cap are
  Claude's. The free-length archive is retained because it is the measurement of
  what the generator does unconstrained. Alternative considered and closed by
  arithmetic, not preference: a report-side length-matched analysis, which
  cannot be done at all (see Findings).

### Findings (things we did not expect)
- 🔴 **The pre-registered length diagnostic PASSED while the confound it exists
  to catch was at its strongest.** It asks whether level-1 output came out
  *shorter* than level-0 by roughly the corpus gap (4.27 mean words). Observed:
  level 1 is **longer** -- bn 13.5 -> 38.3, en 6.3 -> 40.3 -- so the rule
  returned `GAP_BELOW_CORPUS`. The rule fixed a **direction** as well as a
  magnitude, and the generator inverted the direction. Verdict re-reported as
  **UNINFORMATIVE**, never as a pass.
- 🔴 **Length alone recovers the target level: AUC 0.9894 (bn), 1.0000 (en).**
  Computed here, labelled exploratory. In the en arm the ranges do not overlap
  at all -- longest level-0 = 15 words, shortest level-1 = 25.
- 🔴 **No length-matched slice exists.** Under `2607.18508`'s criterion
  (|l0-l1| < 0.15*max, same plot) there are **0 matched pairs in both arms**.
  This is what closed the report-only option: the subset a length-neutral claim
  would be made on is empty, so this was never a choice between controlling at
  generation time and controlling at reporting time.
- ⚠️ Truncation is 5 of 120, **all at level 1** (2 bn, 3 en), which biases the
  level-1 mean *downward* -- the true separation is if anything larger.
- 🎁 **Verbatim exemplar copying: 0 of 120.** Worth counting: the Groq pilot
  emitted `bn_0230` exactly. Retrieval is not being echoed here.
- 🎁 **Generated text does not reproduce the corpus's length signature.** The
  corpus's level 1 is *shorter and richer* (8.85 vs 13.12 mean words, ~18%
  richer per 1k tokens); the generator renders "specific" as "long", at 37-40
  words against a corpus median of 8. A §5.4 realism result, not a defect.
- 🎁 **Non-Bangla script leakage is concentrated at level 1 and under English
  prompts**: bn-L0 0/30, bn-L1 3/30, en-L0 1/30, en-L1 6/30, one generation
  carrying Tamil script. Same direction as the pilot's 1/20 vs 4/20 at larger n
  -- the second data point for the §3e prompt-language factor.

### Consequences for downstream steps
- **No axis-control claim may rest on these 120 generations.** They remain valid
  as the `w` / tau substrate and as §5.1 row-1 (alpha_lo) evidence, because
  neither depends on the level contrast being length-neutral.
- **`length_confound` (AUC-based, direction-free) supersedes
  `length_diagnostic`** for any axis-control claim, and both the AUC and the
  matched-pair count are now printed beside every axis-level cell.
- **The length-controlled condition must run before `w` is interpreted per
  level.** Pre-committed: if its AUC stays >= 0.90 and its matched slice stays
  empty, the control FAILED and is reported as failed -- `2601.01768` finds LLMs
  track their own output length poorly, so that outcome is live.
- **Ch.5 gains a limitation and §5.4 gains a result** from the same observation:
  the inversion of the corpus length/specificity relation.
- Four deviations logged in `protocol.md` under 2026-08-16, including the
  pre-registration's own directionality defect.

### Citations needed
- `2607.18508` (Style over Substance) -- content-blind probe, length-matched
  slice, and the recommendation that generation-time and reporting-time controls
  are both required. **Supplied the remedy; the matched-pair count taken from
  its §3 criterion is what closed the report-only option.**
- `2601.01768` -- LLMs track their own output length poorly; the reason the
  length clause is measured rather than assumed to work.
- `kapur2026length` -- already in the bibliography, and the paper that
  **predicted this exact outcome** while the diagnostic was written to miss it.
  Recorded that way in `protocol.md` deliberately.
- Index searched: **alphaXiv** (Consensus quota exhausted to 2026-09-01).
