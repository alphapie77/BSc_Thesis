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

## Open decisions (resolve before they are needed)

| # | Decision | Blocks | Status |
|---|---|---|---|
| ~~1~~ | ~~Final `usable_n` after near-dup removal~~ | — | ✅ **4,625** at t = 0.95 |
| ~~2~~ | ~~Near-dup threshold from the sensitivity curve~~ | — | ✅ held at the pre-registered **0.95**; 0.90 disclosed as a sensitivity caveat |
| ~~3~~ | ~~Do personas survive the trap-check?~~ | — | ✅ **answered**: on the full corpus the clusters are a corpus detector (93.3%); in region A they are Band 1 but sentiment-ordered. G-300 decides. |
| ~~4~~ | ~~Correct the S0 table in `research_pipeline_en.md`~~ | — | ✅ corrected 2026-08-01, with strikethrough |
| 5 | Frame the register finding in **stylometry/authorship** or **machine-generated-text detection** literature? | Ch.2, Ch.4 | 🔵 Sabbir's, at writing time |
| 6 | Should `s2_pilot.py` persist UMAP coordinates too, for the Ch.4 figure? | Ch.4 figures | 🔵 open |
| 7 | **Three personas or two?** The design posits three; region A has two sentiment classes. Gate G1's master K-table settles K, not the label count | S2 → S3 | 🔴 **next** |
| 8 | If the provenance question ever reopens, does region B get **excluded**, **kept as a labelled condition**, or become **the contribution**? | Ch.1 framing | ⏸ dormant (decision 0 closed unresolvable) |
