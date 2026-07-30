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

## Open decisions (resolve before they are needed)

| # | Decision | Blocks | Due |
|---|---|---|---|
| 1 | Final `usable_n` after near-dup removal | Split freeze | S2 pilot |
| 2 | Near-dup threshold (0.90 / 0.95 / 0.98) — from the sensitivity curve | Split freeze | S2 pilot |
| 3 | Whether personas survive the ARI trap-check, or reframe as engagement tiers | RQ1 claim | S2 pilot |
| 4 | Correct the S0 table in `research_pipeline_en.md` (deferred until 1–2 settle) | — | after S2 |
