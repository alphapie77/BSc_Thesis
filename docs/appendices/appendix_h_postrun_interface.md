# Appendix H — Post-run diagnostic interface

## H.1 Standing

The Audience Response Lab is a local, post-run software demonstration. It did
not generate, select, score or alter any of the frozen 5,400 Phase-5 cases and
is not evidence for any research question. It uses a different live Writer
path and must not be presented as a deployment of the experimental generator.

## H.2 User-facing workflow

The user supplies a Bangla plot synopsis and requests Level 0 or Level 1. The
service performs frozen R1-only retrieval, calls a live Writer, applies
Verifier-A and symbolic diagnostics, and may request bounded correction. It
returns the generated response, target-level diagnostics, attempt trace,
retrieved-example identifiers and a source-bounded plot-support triage.

The interface also exposes the frozen ten-condition result table read-only. It
contains no batch simulator and cannot rerun the experiment.

## H.3 Model and data differences from the experiment

| Component | Frozen experiment | Local interface |
|---|---|---|
| Writer | local `google/gemma-3-12b-it`, NF4 | Gemini API `gemma-4-26b-a4b-it` |
| Faithfulness check | no registered human-validated metric | operational Gemma-4-31B source-bounded triage |
| Retrieval | frozen Region-A R1 index, top 10 | same frozen R1-only index, top 10 |
| In-loop gate | Verifier-A, τ=0.4384071 | same artifact and threshold |
| Outcome Verifier-B | post-generation scoring only | prohibited from the live loop |
| Persistence | sealed cases and manifests | user plots and live calls are not persisted |

The interface's `SUPPORTED`, `REVIEW`, and `UNSUPPORTED` faithfulness labels are
operational aids, not human-validated thesis metrics. Repeated live calls may
vary and do not reproduce a Phase-5 condition.

The Plot Judge runs only after the bounded generation loop and does not trigger
retrieval or rewriting. On failed attempts, the registered loop itself returns
to R1-only retrieval with feedback-anchored query terms; the expert trace shows
the retrieved identifiers for each attempt.

## H.4 Reproducible local entry points

The interface configuration is `configs/demo.yaml`; the backend is under
`src/demo/`; the presentation client is under `interface/`; and the Windows
launcher is `start_demo.cmd`. `tests/test_demo.py` checks the principal data and
privilege boundaries. API secrets remain server-side and are not written to the
repository or browser bundle.
The launcher uses the repository-local frontend runner when dependencies are
present and waits for a full artifact-readiness endpoint before opening the UI.
