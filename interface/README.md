# Audience Response Lab interface

This is the presentation wrapper for the thesis pipeline. It deliberately
contains no batch simulator and never regenerates the frozen 5,400 S5 cases.

Current state:

- implemented: Bangla plot input, fixed two-level output contract, transparent
  R1 → Writer → Verifier-A → symbolic-feedback loop display, isolation badges,
  and a read-only ten-condition table copied from the audited S5 master table;
- implemented locally: live generation through the server-side Gemini secret,
  frozen R1-only retrieval, Verifier-A and symbolic feedback;
- implemented as a separate operational check: source-bounded structured plot
  support triage (`SUPPORTED` / `REVIEW` / `UNSUPPORTED`) using Gemma-4-31B;
  this is visible evidence for the user, not a human-validated thesis metric;
- product split: `/` is the focused simulator; `/research` contains method,
  isolation, model disclosures and the frozen ten-condition table;
- forbidden: Verifier-B in the live loop, Gold-300/R2 retrieval, fabricated
  demo outputs, and a hallucination-free claim before the separate audit.

`results/s5_main_bn_master_table.csv` remains the canonical numerical source;
`app/experiment-data.ts` is a display-only copy.

## Run locally on Windows

From the repository root, double-click `start_demo.cmd`. It checks the API key
and local environments, installs only a missing first-run dependency, starts
both services, and opens `http://localhost:3000`. Keep the launcher window open;
press Ctrl+C there to stop both services.
