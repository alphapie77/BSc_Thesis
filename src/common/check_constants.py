#!/usr/bin/env python3
"""Every decision constant must carry a reason. This checks that it does.

Standing rule from Sabbir, 2026-08-11: *"hate likha thakle hbe na. karon
thakte hobe."* -- a hand-written number is not acceptable; there must be a
reason.

The rule was prompted by the Critic's `0.6 x VerifierA + 0.4 x symbolic`
weight, which appears in the pipeline spec with no derivation behind it. The
audit that followed found the problem was not confined to that one number:
`independent_at_or_above`, `explained_at_or_above` and `strong_at_or_above`
decide verdicts and appear **zero times** in `protocol.md`.

🔴 BLIND SPOT, STATED BECAUSE IT IS THE IMPORTANT ONE
-----------------------------------------------------
This scans `configs/*.yaml` ONLY. It does not read prose.

So on 2026-08-11 it reported a clean pass while `0.6 x VerifierA + 0.4 x
symbolic` -- **the number that caused this checker to be written** -- sat
unjustified in `research_pipeline_en.md` §4.2, because Phase 4 has no config
yet and the constant lives in a sentence.

The audit cleaned up everything except its own reason for existing. Anyone
reading a green exit code should know that is what green can mean here: the
worst constants are the ones for steps not yet built, and those live in prose.
When `configs/s4_*.yaml` is written, `w` must arrive with its derivation or
this check will finally be able to see it.

WHAT THIS DOES NOT DO
---------------------
It cannot check that a reason is *good*. It checks that one was written down.
That is a low bar on purpose: the failure mode being prevented is not bad
reasoning, it is *absent* reasoning that nobody notices because a bare number
in a YAML file looks exactly as authoritative as a derived one.

TIERS
-----
Not every number is a decision. Three tiers, and only the first is enforced:

  DECISION   a number that changes a verdict, a claim, or what gets reported.
             Thresholds, cutoffs, weights, alpha levels. MUST have a reason.

  KNOB       an engineering default with no bearing on any claim -- batch
             size, n_init, worker counts. Warned about, never enforced.

  ASSERTION  a value the config checks the data against rather than choosing:
             `expected_n`, `train_n`, the S0 claimed counts. These are the
             opposite of hand-set -- they exist to fail loudly if the data
             moves. Skipped entirely.

WHAT COUNTS AS A REASON
-----------------------
Any one of:
  * an inline comment on the same line
  * a comment in the 4 lines above
  * the key appearing in `docs/protocol.md` (i.e. pre-registered there)
  * an explicit `# ref: <where>` pointer within 4 lines

The last two matter most, and the fourth was added on 2026-08-11 after the
first run produced a **false alarm that is worth recording**. It reported 29
constants as having "no reason anywhere". That was wrong for most of them:
`strong_at_or_above: 0.45` is pre-registered in protocol.md with a power
calculation behind it (*"at n = 50, detecting 0.45 against 0.25"*), and
`dominated_at_or_above: 0.75` sits in a full pre-committed outcome table.
The reasons existed; the **key names** did not appear in the prose, so a
key-name search could not see them.

The defect was therefore linkage, not absence — but linkage is still a real
defect, because a reader holding the config cannot get from the number to the
argument, and neither could this checker. `# ref:` fixes that in the one
place the reader is actually looking.

Usage:  python src/common/check_constants.py [--strict]
        --strict also fails on KNOB tier (not recommended; noisy)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO / "configs"
PROTOCOL = REPO / "docs" / "protocol.md"

# Substrings that mark a key as a DECISION -- it gates a verdict.
DECISION_MARKERS = (
    "threshold", "_at_or_above", "_below", "_above", "cutoff", "alpha",
    "weight", "chance", "ci", "fraction", "headline", "tolerance",
    "min_", "max_score", "_rate",
)

# Keys that are assertions about the data, not choices. Skipped.
ASSERTION_MARKERS = (
    "expected_", "_n:", "train_n", "dev_n", "gold", "boundary_row",
    "exact_duplicates", "normalized_duplicates", "null_rows", "usable_n",
    "median_words", "max_words", "emoji_rows", "url_or_mention_rows",
    "short_reviews", "sheet", "seed", "random_state",
)

# Pure engineering knobs.
KNOB_MARKERS = (
    "batch_size", "n_init", "n_jobs", "workers", "timeout", "retries",
    "checkpoint_every", "max_seq_length", "epochs", "n_resamples",
    "bootstrap", "permutations", "n_runs", "n_reference", "pca_components",
    "cv_folds", "n_splits", "request_delay", "category_depth", "top_n",
    "prior_strength", "max_pages", "n_quantiles", "n_bins",
    # Added 2026-08-11 after the first run misfiled these as DECISION. None
    # of them changes a verdict: they cap display length, set a display
    # count, or set a numerical tolerance.
    "max_chars", "min_count", "min_samples", "n_representative",
    "n_boundary", "subsample_frac", "min_budget", "tolerance",
    "length_bands",
)

NUM_LINE = re.compile(r"^(\s*)([a-z_0-9]+):\s*(-?[0-9][0-9.eE+-]*)\s*(#.*)?$")


def classify(key: str) -> str:
    k = key.lower()
    if any(m.strip(":") in k for m in ASSERTION_MARKERS):
        return "ASSERTION"
    if any(m in k for m in KNOB_MARKERS):
        return "KNOB"
    if any(m in k for m in DECISION_MARKERS):
        return "DECISION"
    # Unclassified numbers are treated as DECISION. Deliberate: the safe
    # default when we do not know what a number does is to demand a reason
    # for it, not to wave it through.
    return "DECISION"


# A comment that ANNOUNCES the absence of a reason must not be counted as one.
# Second instance of the same loophole in one hour: the first was the audit note
# in the deviations log, this one is an inline "no reason yet" marker. Both read
# as prose about the constant, and a substring check cannot tell prose about a
# reason from a reason. These are surfaced under their own OPEN heading so that
# flagging a gap can never be the thing that hides it.
OPEN_MARKERS = ("no recorded reason", "no reason", "awaiting sabbir", "todo")


def has_reason(lines: list[str], idx: int, key: str, protocol_text: str) -> str | None:
    """Return the kind of reason found, or None."""
    m = NUM_LINE.match(lines[idx])
    if m and m.group(4):
        return "inline comment"
    for j in range(max(0, idx - 4), idx + 1):
        stripped = lines[j].strip()
        if "# ref:" in stripped.lower():
            return "explicit ref pointer"
    for j in range(max(0, idx - 4), idx):
        if lines[j].strip().startswith("#"):
            return "comment block above"
    if key in protocol_text:
        return "pre-registered in protocol.md"
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true",
                    help="also fail on KNOB tier")
    args = ap.parse_args()

    if not CONFIG_DIR.is_dir():
        print(f"no configs/ at {CONFIG_DIR}", file=sys.stderr)
        return 2

    protocol_text = PROTOCOL.read_text(encoding="utf-8") if PROTOCOL.exists() else ""
    # 🔴 The Deviations log is CUT OUT before searching.
    #
    # Found 2026-08-11, immediately after this checker's first run. The audit
    # note written into the deviations table names the offending keys --
    # `independent_at_or_above`, `explained_at_or_above`, `strong_at_or_above`
    # -- in order to report that they lacked justification. On the next run
    # the checker found those key names in protocol.md and passed them.
    #
    # **Writing about the gap closed the check.** A log entry saying "this
    # constant has no reason" is the opposite of a reason, and a checker that
    # cannot tell those apart certifies the exact defect it exists to catch.
    # Pre-registration means the key was registered BEFORE the run, in a
    # pre-commitment section -- not mentioned afterwards in an audit note.
    _dev = protocol_text.find("## Deviations log")
    if _dev != -1:
        protocol_text = protocol_text[:_dev]
    if not protocol_text:
        print("WARNING: docs/protocol.md not readable; "
              "pre-registration cannot count as a reason this run.")

    failures: list[tuple[str, int, str, str]] = []
    warnings: list[tuple[str, int, str, str]] = []
    open_items: list[tuple[str, int, str, str]] = []
    ok = 0

    for path in sorted(CONFIG_DIR.glob("*.yaml")):
        lines = path.read_text(encoding="utf-8").split("\n")
        for i, line in enumerate(lines):
            m = NUM_LINE.match(line)
            if not m:
                continue
            key, val = m.group(2), m.group(3)
            tier = classify(key)
            if tier == "ASSERTION":
                continue
            ctx = " ".join(lines[max(0, i - 6):i + 1]).lower()
            if any(mk in ctx for mk in OPEN_MARKERS):
                open_items.append((path.relative_to(REPO).as_posix(),
                                   i + 1, key, val))
                continue
            reason = has_reason(lines, i, key, protocol_text)
            if reason:
                ok += 1
                continue
            rel = path.relative_to(REPO).as_posix()
            if tier == "DECISION":
                failures.append((rel, i + 1, key, val))
            else:
                warnings.append((rel, i + 1, key, val))

    if open_items:
        print(f"\n{len(open_items)} constants EXPLICITLY FLAGGED as having no "
              f"reason yet (open, not silent):")
        for rel, n, key, val in open_items:
            print(f"  {rel}:{n}  {key} = {val}")

    if warnings:
        print(f"\n{len(warnings)} KNOB-tier constants with no stated reason "
              f"(not enforced):")
        for rel, n, key, val in warnings:
            print(f"  {rel}:{n}  {key} = {val}")

    if failures:
        print(f"\n{len(failures)} DECISION-tier constants with NO reason "
              f"anywhere -- these gate a verdict:")
        for rel, n, key, val in failures:
            print(f"  {rel}:{n}  {key} = {val}")
        print("\nFix by ONE of:")
        print("  * a comment saying where the number came from")
        print("  * pre-registering it in docs/protocol.md")
        print("  * deriving it and citing the result file")
        print("\nA number that decides something and cannot say why it has "
              "that value\nis a hand-written number, and those are not "
              "allowed (Sabbir, 2026-08-11).")

    n_bad = len(failures) + (len(warnings) if args.strict else 0)
    print(f"\n{ok} constants carry a reason. "
          f"{len(failures)} DECISION-tier do not. "
          f"{len(warnings)} KNOB-tier do not. "
          f"{len(open_items)} are openly flagged as unresolved.")
    if open_items and not failures:
        print("\nExit 0: nothing is SILENTLY unjustified. The open items above "
              "are\nawaiting an answer and say so, which is the intended state "
              "-- not a pass.")
    return 1 if n_bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
