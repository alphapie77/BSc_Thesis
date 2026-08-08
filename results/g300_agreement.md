# G-300 — human validation of the K = 2 partition

> **Both gates were pre-registered in `docs/protocol.md` (RQ1-F) before a single
> item was annotated.** Read that section first.
>
> ### Two constraints, recorded rather than worked around
>
> **Only 123 of the
> frozen G-300 are in region A** and therefore carry a K = 2 label. The split map
> is frozen (inviolable rule 3) and was **not** regenerated. All 300 are
> annotated; Gate 2 runs on the region-A subset and its reduced power is stated
> as a number.
>
> **Two annotators, not the three RQ1 states** — logged as a deviation. With two
> there is no majority, so the adjudication rule was fixed in advance:
> **disagreements are not resolved.** The gold value is the mean of the two
> ratings and the disagreement rate is reported below. Adjudicating after seeing
> the data is how an IAA figure gets laundered.

- **Config:** `configs/g300.yaml` · **Generated (UTC):** 2026-08-08T05:53:13.420950+00:00
- **Commit:** `43e6d877b40b9251623747079df0ec180e1f8a6b` · **Seed:** 42
- Ratings filled: A 300, B 298 · items
  rated by **all** annotators: **298**
- **Nothing is trained.** α, κ and AUC are agreement/rank statistics.

## Gate 1 — can humans agree at all?

**UNRELIABLE** — α = 0.4970 <
0.667.

**The construct is not reliably annotatable by humans, and Gate 2 was not
computed.** Pre-registered in RQ1-F: a rating nobody agrees on cannot validate
anything. RQ1 is reported as a **negative result** — publishable under RQ1-C —
and the failure is attributed to the construct, not to the annotators.

| Statistic | Value |
|---|---|
| Krippendorff's α (**ordinal**) | **0.4970** |
| Krippendorff's α (nominal, for reference) | 0.4324 |
| Cohen's κ (linear weights) | 0.4456 |
| Exact agreement | 75.5% |
| Agreement within 1 point | 98.7% |

Ordinal α is the pre-registered figure. The nominal value is shown only because
the gap between them is informative: it is the part of the agreement that comes
from **near misses on an ordered scale** rather than from exact matches.

### Rating distribution per annotator

|   rating |   A |   B |
|---------:|----:|----:|
|        0 |   2 |   0 |
|        1 |  24 |  11 |
|        2 | 202 | 227 |
|        3 |  70 |  60 |

A distribution concentrated in one or two categories caps α mechanically —
there is little variance for agreement to be measured against — and is reported
here so that a low α is not misread as disagreement when it is actually
degeneracy.

## Gate 2 — does the human rating recover the machine's split?

_Not computed — see Gate 1._

## What this settles, and what it does not

- **This is the arbiter for RQ1.** S2f eliminated valence and verbosity, so no
  cheaper instrument remained.
- **It does not establish that region A contains cluster structure.** It cannot:
  G1 already showed there is none (silhouette 0.053, monotone gap, HDBSCAN 100%
  noise). At best this shows a **reproducible, humanly-recognisable cut through
  a continuum** — which is a real finding, and is not the same sentence as
  "we discovered two audience personas".
- **It says nothing about region B**, which carries no K = 2 label at all.
