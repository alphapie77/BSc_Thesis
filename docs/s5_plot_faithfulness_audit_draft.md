# S5 Bangla plot-faithfulness audit — draft, not pre-registered

This audit addresses a measurement gap that Verifier-A, the symbolic scorer,
Verifier-B and the current binary human evaluation do not cover: whether a
generated audience-style comment introduces plot-specific content unsupported
by, or contradictory to, the input synopsis.

## Scientific boundary

- The frozen 5,400 generations are read-only inputs. No generation rerun is
  authorised.
- This is a separate post-run analysis, not an amendment to the three frozen
  human-evaluation instruments now in progress.
- A subjective reaction (for example, “the ending felt weak”) is not itself a
  hallucination. A new named actor, character, relationship, event or scene not
  licensed by the synopsis is an unsupported detail.
- Retrieved R1 reviews are style exemplars, not factual evidence about the new
  plot. Apparent transfer of their named entities or events is recorded as
  `retrieved_exemplar_leakage` when supported by the trace.

## Annotation labels

| Label | Meaning |
|---|---|
| `SUPPORTED` | Every plot-specific assertion is supported by the synopsis. |
| `CONTRADICTED` | At least one assertion conflicts with the synopsis. |
| `UNSUPPORTED_DETAIL` | At least one plot-specific detail is invented or not licensed by the synopsis. |
| `UNDECIDABLE` | The synopsis does not permit a defensible decision. |

Annotators localize the shortest offending span and select a suspected error
source. Condition, model identity, Verifier-A/B scores, loop verdict and
`gave_up` remain hidden.

## What remains open before freezing

The sample size and adjudication rule are intentionally unset. They must be
chosen from an explicit precision or power target before any case is sampled.
The builder must refuse `n_cases: null`, verify the sealed case hash, sample
uniformly within condition × level without consulting outcomes, and produce a
separate immutable interface version. Until human validation is complete, any
automatic warning in the public demo is labelled heuristic and no
“hallucination-free” claim is permitted.

Recent work motivates separate completeness, hallucination and irrelevance
measurement rather than treating generic quality as factuality
[@zhu2024rageval]. A 2025 review likewise emphasizes that automated factuality
metrics remain limited and require validated evidence
[@rahman2025hallucination].

