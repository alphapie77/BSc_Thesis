# Audience Response Lab interface

This is the presentation wrapper for the thesis pipeline. It deliberately
contains no batch simulator and never regenerates the frozen 5,400 S5 cases.

Current state:

- implemented: Bangla plot input, fixed two-level output contract, transparent
  R1 → Writer → Verifier-A → symbolic-feedback loop display, isolation badges,
  and a read-only ten-condition table copied from the audited S5 master table;
- intentionally disconnected: live generation, until a server-side Gemini API
  secret and the R1/Verifier-A backend are configured;
- forbidden: Verifier-B in the live loop, Gold-300/R2 retrieval, fabricated
  demo outputs, and a hallucination-free claim before the separate audit.

`results/s5_main_bn_master_table.csv` remains the canonical numerical source;
`app/experiment-data.ts` is a display-only copy.
