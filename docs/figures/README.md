# Thesis figure source register

This directory contains editable vector figures for the thesis. Schematics do
not introduce computed results; numeric labels reproduce frozen values from the
listed sources.

| Figure | File | Source contract | Numeric standing |
|---|---|---|---|
| 4.1 | `dual_verifier_isolation.svg` | `data/splits/split_map_v1.json`, `results/g300_agreement.md`, Chapters 3--4, frozen verifier/RAG manifests | G=300 and 598/600 Attempt-1 ratings, α=0.497; R1=2,162, R2=2,163; dev-200 is within R1; A train=804, B train=888, RAG=886 |
| 5.1 | `multi_agent_state_graph.svg` | implemented agent graph and Chapter 5 | maximum three Writer attempts; schematic routing only |
| 5.2 | `s4_loop_dynamics.svg` | `results/s4_tau_frontier.json`, `results/s4_loop_dynamics.json` | development-only tau=0.4384071 and 60-case dynamics |

Verifier-B's placement outside Figures 4.1 and 5.1 is a scientific isolation
constraint, not a visual simplification. Figure 5.1 depicts bounded autonomy:
the controller may route retries and revise retrieval after failed diagnostics,
but it may not change frozen thresholds, data partitions or attempt ceilings.
