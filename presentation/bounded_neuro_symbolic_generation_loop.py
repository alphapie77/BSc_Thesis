"""Focused presentation view copied directly from methodology Phase 4."""

from src.common.seed import set_seed

set_seed()

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

plt.rcParams["figure.dpi"] = 300
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 14

fig, ax = plt.subplots(figsize=(16, 9))
ax.set_xlim(0.55, 18.25)
ax.set_ylim(1.25, 8.25)
ax.axis("off")

c3, c4, c5 = "#E8F5E9", "#F3E5F5", "#FFF9C4"

# Direct copy of the Phase 4 boundary and component coordinates.
p3 = FancyBboxPatch((0.8, 1.5), 17.2, 6.50, boxstyle="round,pad=0.15",
                    edgecolor="#2E7D32", facecolor=c3, linewidth=2.5)
ax.add_patch(p3)

inp = FancyBboxPatch((1.5, 6.4), 2.2, 1.0, boxstyle="round,pad=0.1",
                     edgecolor="#2E7D32", facecolor="white", linewidth=2)
ax.add_patch(inp)
ax.text(2.6, 7.1, "INPUT", ha="center", fontsize=15, fontweight="bold")
ax.text(2.6, 6.8, "Movie Plot", ha="center", fontsize=13.5)
ax.text(2.6, 6.53, "Requested Level", ha="center", fontsize=13.5)

a1 = FancyBboxPatch((5.0, 6.4), 2.0, 1.0, boxstyle="round,pad=0.1",
                    edgecolor="#1976D2", facecolor="#BBDEFB", linewidth=2)
ax.add_patch(a1)
ax.text(6.0, 7.1, "AGENT 1", ha="center", fontsize=14, fontweight="bold")
ax.text(6.0, 6.8, "Researcher", ha="center", fontsize=13.5)
ax.text(6.0, 6.53, "R1 Retrieval Query", ha="center", fontsize=12, style="italic")

a2 = FancyBboxPatch((5.0, 4.9), 2.0, 1.0, boxstyle="round,pad=0.1",
                    edgecolor="#388E3C", facecolor="#C8E6C9", linewidth=2)
ax.add_patch(a2)
ax.text(6.0, 5.6, "AGENT 2", ha="center", fontsize=14, fontweight="bold")
ax.text(6.0, 5.3, "Writer", ha="center", fontsize=13.5)
ax.text(6.0, 5.03, "Generate Candidate", ha="center", fontsize=12, style="italic")

a3 = FancyBboxPatch((5.0, 3.4), 2.0, 1.0, boxstyle="round,pad=0.1",
                    edgecolor="#F57C00", facecolor="#FFE0B2", linewidth=2)
ax.add_patch(a3)
ax.text(6.0, 4.1, "AGENT 3", ha="center", fontsize=14, fontweight="bold")
ax.text(6.0, 3.8, "Critic", ha="center", fontsize=13.5)
ax.text(6.0, 3.53, "Evaluate Candidate", ha="center", fontsize=12, style="italic")

a4 = FancyBboxPatch((5.0, 1.9), 2.0, 1.0, boxstyle="round,pad=0.1",
                    edgecolor="#C62828", facecolor="#FFCDD2", linewidth=2)
ax.add_patch(a4)
ax.text(6.0, 2.6, "AGENT 4", ha="center", fontsize=14, fontweight="bold")
ax.text(6.0, 2.3, "Reflector", ha="center", fontsize=13.5)
ax.text(6.0, 2.03, "Revision Feedback", ha="center", fontsize=12, style="italic")

rag = FancyBboxPatch((8.5, 6.1), 2.5, 1.6, boxstyle="round,pad=0.1",
                     edgecolor="#6A1B9A", facecolor=c4, linewidth=2)
ax.add_patch(rag)
ax.text(9.75, 7.34, "R1-ONLY RETRIEVAL", ha="center", fontsize=12.8, fontweight="bold")
ax.text(9.75, 6.87, "Same-Level R1 Search", ha="center", fontsize=12.2)
ax.text(9.75, 6.40, "Top-10 Examples", ha="center", fontsize=12.2, fontweight="bold")

val = FancyBboxPatch((11.5, 6.1), 2.5, 1.6, boxstyle="round,pad=0.1",
                     edgecolor="#F57F17", facecolor=c5, linewidth=2)
ax.add_patch(val)
ax.text(12.75, 7.34, "VERIFIER-A", ha="center", fontsize=14, fontweight="bold")
ax.text(12.75, 6.87, "Neural Acceptance Score", ha="center", fontsize=11.2)
ax.text(12.75, 6.40, "Registered Threshold", ha="center", fontsize=12.2,
        fontweight="bold")

hyb = FancyBboxPatch((8.5, 3.1), 3.5, 1.2, boxstyle="round,pad=0.1",
                     edgecolor="#6A1B9A", facecolor=c4, linewidth=2)
ax.add_patch(hyb)
ax.text(10.25, 4.05, "DECISION & DIAGNOSTICS", ha="center", fontsize=13,
        fontweight="bold")
ax.text(10.25, 3.68, "Verifier-A Gate + Deterministic Rules", ha="center", fontsize=10.7)
ax.text(10.25, 3.34, "Registered Threshold Decides", ha="center", fontsize=10.8,
        style="italic")

out = FancyBboxPatch((14.8, 2.2), 2.8, 1.8, boxstyle="round,pad=0.1",
                     edgecolor="#C62828", facecolor="#FFEBEE", linewidth=2.5)
ax.add_patch(out)
ax.text(16.2, 3.72, "SEALED OUTPUT", ha="center", fontsize=16, fontweight="bold")
ax.text(16.2, 3.32, "Final Bangla Response", ha="center", fontsize=14)
ax.text(16.2, 2.92, "Attempt-Level Trace", ha="center", fontsize=13)
ax.text(16.2, 2.52, "Accepted or Gave Up", ha="center", fontsize=13,
        fontweight="bold")

trace = FancyBboxPatch((14.8, 6.1), 2.8, 1.6, boxstyle="round,pad=0.1",
                       edgecolor="#FF6F00", facecolor="#FFF3E0", linewidth=2)
ax.add_patch(trace)
ax.text(16.2, 7.34, "TRACE RECORD", ha="center", fontsize=13.2, fontweight="bold")
ax.text(16.2, 6.96, "Retrieved IDs · Scores · Decision", ha="center", fontsize=10.1)
ax.text(16.2, 6.60, "Feedback · Cost · Attempt", ha="center", fontsize=10.5)
ax.text(16.2, 6.25, "Append Every Attempt", ha="center", fontsize=10.8,
        fontweight="bold")

# Direct copy of the Phase 4 arrow routing.
ax.add_patch(FancyArrowPatch((3.78, 6.9), (4.92, 6.9), arrowstyle="->",
                             mutation_scale=20, linewidth=2.5, color="black"))
ax.add_patch(FancyArrowPatch((6.0, 6.32), (6.0, 5.98), arrowstyle="->",
                             mutation_scale=20, linewidth=2.5, color="black"))
ax.add_patch(FancyArrowPatch((6.0, 4.82), (6.0, 4.48), arrowstyle="->",
                             mutation_scale=20, linewidth=2.5, color="black"))

ax.add_patch(FancyArrowPatch((8.42, 6.9), (7.08, 6.9), arrowstyle="->",
                             mutation_scale=20, linewidth=2, color="#6A1B9A",
                             linestyle="--"))
ax.text(7.75, 7.2, "Retrieve", ha="center", fontsize=13.5,
        color="#6A1B9A", fontweight="bold")

ax.plot([12.75, 12.75], [6.1, 4.9], color="#F57F17", linewidth=2, linestyle="--")
ax.plot([12.75, 11.0], [4.9, 4.9], color="#F57F17", linewidth=2, linestyle="--")
ax.plot([11.0, 11.0], [4.9, 4.3], color="#F57F17", linewidth=2, linestyle="--")
ax.add_patch(FancyArrowPatch((11.0, 4.46), (11.0, 4.38), arrowstyle="->",
                             mutation_scale=20, linewidth=2, color="#F57F17"))
ax.text(12.0, 5.4, "Score", ha="center", fontsize=13.5,
        color="#F57F17", fontweight="bold")

ax.add_patch(FancyArrowPatch((7.08, 3.9), (8.42, 3.9), arrowstyle="->",
                             mutation_scale=20, linewidth=2.5, color="black"))

ax.add_patch(FancyArrowPatch((12.08, 3.7), (14.72, 3.7), arrowstyle="simple",
                             mutation_scale=18, linewidth=1.5,
                             edgecolor="#37474F", facecolor="#37474F"))
ax.text(13.4, 3.52, "PASS OR\nLIMIT REACHED", ha="center", va="top",
        fontsize=12.5, fontweight="bold", color="#37474F", linespacing=0.9)

# FAIL begins at Decision & Diagnostics, not at Agent 3.
ax.plot([9.5, 9.5], [3.1, 2.4], color="red", linewidth=2, linestyle="--")
ax.plot([9.5, 7.5], [2.4, 2.4], color="red", linewidth=2, linestyle="--")
ax.add_patch(FancyArrowPatch((7.5, 2.4), (7.08, 2.4), arrowstyle="->",
                             mutation_scale=20, linewidth=2, color="red"))
ax.text(8.2, 2.7, "FAIL", ha="center", fontsize=13, fontweight="bold", color="red",
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="red", linewidth=1.5))

# Reflector feedback re-enters at Agent 1; there is no Agent 3 -> Agent 4 arrow.
ax.plot([5.0, 4.2], [2.4, 2.4], color="red", linewidth=2, linestyle="--")
ax.plot([4.2, 4.2], [2.4, 6.62], color="red", linewidth=2, linestyle="--")
ax.add_patch(FancyArrowPatch((4.2, 6.62), (4.92, 6.62), arrowstyle="->",
                             mutation_scale=20, linewidth=2, color="red"))
ax.text(3.48, 4.35, "RETRY VIA", ha="center", va="center", rotation=90,
        fontsize=11.5, color="red", fontweight="bold")
ax.text(3.72, 4.35, "RESEARCHER", ha="center", va="center", rotation=90,
        fontsize=11.5, color="red", fontweight="bold")
ax.text(3.96, 4.35, "MAX 3 WRITER ATTEMPTS", ha="center", va="center", rotation=90,
        fontsize=11.5, color="red", fontweight="bold")

ax.plot([12.08, 14.45], [4.24, 4.24], color="#D66A00", linewidth=2,
        linestyle=(0, (3, 3)))
ax.plot([14.45, 14.45], [4.24, 6.9], color="#D66A00", linewidth=2,
        linestyle=(0, (3, 3)))
ax.add_patch(FancyArrowPatch((14.45, 6.9), (14.72, 6.9), arrowstyle="->",
                             mutation_scale=16, linewidth=2, color="#D66A00"))

ax.add_patch(FancyArrowPatch((16.2, 4.08), (16.2, 6.02), arrowstyle="<->",
                             mutation_scale=16, linewidth=2, color="#FF6F00",
                             linestyle=(0, (3, 3))))
ax.text(16.42, 5.05, "AUDIT\nLINK", va="center", ha="left", linespacing=1.0,
        fontsize=13, color="#FF6F00", fontweight="bold")

plt.tight_layout(pad=0.20)
plt.savefig(
    "E:/Research/Thesis/thesis/presentation/images/bounded_neuro_symbolic_generation_loop.png",
    dpi=300, bbox_inches="tight", facecolor="white"
)
print("[SUCCESS] Saved direct Phase 4 presentation view.")
