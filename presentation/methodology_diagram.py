"""
Professional Methodology Diagram - FINAL VERSION
Proper L-shaped arrows with correct routing
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.lines as mlines

from src.common.seed import set_seed

set_seed()

plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 14

fig, ax = plt.subplots(figsize=(19, 13.9))
ax.set_xlim(0, 19)
ax.set_ylim(-1.9, 12)
ax.axis('off')

c1, c2, c3, c4, c5 = '#E3F2FD', '#FFF3E0', '#E8F5E9', '#F3E5F5', '#FFF9C4'

# PHASE 1
p1 = FancyBboxPatch((0.8, 9.65), 5.2, 1.65, boxstyle="round,pad=0.1",
                    edgecolor='#1565C0', facecolor=c1, linewidth=2.5)
ax.add_patch(p1)
ax.text(3.4, 11.08, 'PHASE 1: DATA AUDIT & SPLIT FREEZE',
        ha='center', va='top', fontsize=14.5, fontweight='bold')
ax.text(3.4, 10.55, '5,000 → 4,625 Reviews', ha='center', fontsize=14)
ax.text(3.4, 10.18, 'G: 300  ·  R1: 2,162  ·  R2: 2,163',
        ha='center', fontsize=13.5)
ax.text(3.4, 9.82, 'Plots: Dev 30  ·  Eval 90', ha='center', fontsize=13.5)

# PHASE 2
p2 = FancyBboxPatch((6.8, 9.65), 5.2, 1.65, boxstyle="round,pad=0.1", 
                    edgecolor='#E65100', facecolor=c2, linewidth=2.5)
ax.add_patch(p2)
ax.text(9.4, 11.08, 'PHASE 2: CONSTRUCT DEVELOPMENT',
        ha='center', va='top', fontsize=14.5, fontweight='bold')
ax.text(9.4, 10.55, 'Two-Level Engagement-Specificity Continuum',
        ha='center', fontsize=13)
ax.text(9.4, 10.18, 'Human Recovery: 0.78 / 0.84 vs 0.25 Chance',
        ha='center', fontsize=13, fontweight='bold')
ax.text(9.4, 9.82, 'Length-Matched Comparative Judgement', ha='center', fontsize=13)

# PHASE 3
p3_top = FancyBboxPatch((12.8, 9.65), 5.2, 1.65, boxstyle="round,pad=0.1",
                        edgecolor='#6A1B9A', facecolor='#F3E5F5', linewidth=2.5)
ax.add_patch(p3_top)
ax.text(15.4, 11.08, 'PHASE 3: DUAL-VERIFIER DESIGN',
        ha='center', va='top', fontsize=14.5, fontweight='bold')
ax.text(15.4, 10.55, 'A · LaBSE + Logistic · R1: 804 · In-Loop',
        ha='center', fontsize=12.5)
ax.text(15.4, 10.18, r'B · $\mathbf{BanglaBERT}$ · R2: 888 · Outcome-Only',
        ha='center', fontsize=12.5)
ax.text(15.4, 9.82, 'Disjoint Data + Model Families', ha='center', fontsize=13,
        fontweight='bold')

# PHASE 4
p3 = FancyBboxPatch((0.8, 1.5), 17.2, 7.15, boxstyle="round,pad=0.15", 
                    edgecolor='#2E7D32', facecolor=c3, linewidth=2.5)
ax.add_patch(p3)
ax.text(1.15, 8.38, 'PHASE 4: Bounded Multi-Agent Generation',
        ha='left', va='top', fontsize=17, fontweight='bold')


# Components
inp = FancyBboxPatch((1.5, 6.4), 2.2, 1.0, boxstyle="round,pad=0.1", 
                     edgecolor='#2E7D32', facecolor='white', linewidth=2)
ax.add_patch(inp)
ax.text(2.6, 7.1, 'INPUT', ha='center', fontsize=15, fontweight='bold')
ax.text(2.6, 6.8, 'Movie Plot', ha='center', fontsize=13.5)
ax.text(2.6, 6.53, 'Requested Level', ha='center', fontsize=13.5)

a1 = FancyBboxPatch((5.0, 6.4), 2.0, 1.0, boxstyle="round,pad=0.1", 
                    edgecolor='#1976D2', facecolor='#BBDEFB', linewidth=2)
ax.add_patch(a1)
ax.text(6.0, 7.1, 'AGENT 1', ha='center', fontsize=14, fontweight='bold')
ax.text(6.0, 6.8, 'Researcher', ha='center', fontsize=13.5)
ax.text(6.0, 6.53, 'R1 Retrieval Query', ha='center', fontsize=12, style='italic')

a2 = FancyBboxPatch((5.0, 4.9), 2.0, 1.0, boxstyle="round,pad=0.1", 
                    edgecolor='#388E3C', facecolor='#C8E6C9', linewidth=2)
ax.add_patch(a2)
ax.text(6.0, 5.6, 'AGENT 2', ha='center', fontsize=14, fontweight='bold')
ax.text(6.0, 5.3, 'Writer', ha='center', fontsize=13.5)
ax.text(6.0, 5.03, 'Generate Candidate', ha='center', fontsize=12, style='italic')

a3 = FancyBboxPatch((5.0, 3.4), 2.0, 1.0, boxstyle="round,pad=0.1", 
                    edgecolor='#F57C00', facecolor='#FFE0B2', linewidth=2)
ax.add_patch(a3)
ax.text(6.0, 4.1, 'AGENT 3', ha='center', fontsize=14, fontweight='bold')
ax.text(6.0, 3.8, 'Critic', ha='center', fontsize=13.5)
ax.text(6.0, 3.53, 'Evaluate Candidate', ha='center', fontsize=12, style='italic')

a4 = FancyBboxPatch((5.0, 1.9), 2.0, 1.0, boxstyle="round,pad=0.1", 
                    edgecolor='#C62828', facecolor='#FFCDD2', linewidth=2)
ax.add_patch(a4)
ax.text(6.0, 2.6, 'AGENT 4', ha='center', fontsize=14, fontweight='bold')
ax.text(6.0, 2.3, 'Reflector', ha='center', fontsize=13.5)
ax.text(6.0, 2.03, 'Revision Feedback', ha='center', fontsize=12, style='italic')

rag = FancyBboxPatch((8.5, 6.1), 2.5, 1.6, boxstyle="round,pad=0.1", 
                     edgecolor='#6A1B9A', facecolor=c4, linewidth=2)
ax.add_patch(rag)
ax.text(9.75, 7.45, 'R1-ONLY RETRIEVAL', ha='center', fontsize=14, fontweight='bold')
ax.text(9.75, 7.1, 'LaBSE Index', ha='center', fontsize=13)
ax.text(9.75, 6.8, '886 Reviews', ha='center', fontsize=13)
ax.text(9.75, 6.5, 'Same-Level Search', ha='center', fontsize=13)
ax.text(9.75, 6.2, 'Top-10 Examples', ha='center', fontsize=12, fontweight='bold')

val = FancyBboxPatch((11.5, 6.1), 2.5, 1.6, boxstyle="round,pad=0.1", 
                     edgecolor='#F57F17', facecolor=c5, linewidth=2)
ax.add_patch(val)
ax.text(12.75, 7.45, 'VERIFIER-A', ha='center', fontsize=15, fontweight='bold')
ax.text(12.75, 7.1, 'Frozen LaBSE Probe', ha='center', fontsize=13)
ax.text(12.75, 6.8, 'Neural Acceptance Score', ha='center', fontsize=12)
ax.text(12.75, 6.5, 'Registered Threshold', ha='center', fontsize=13)
ax.text(12.75, 6.2, 'IN-LOOP · NO VERIFIER-B', ha='center', fontsize=10.5,
        fontweight='bold')

hyb = FancyBboxPatch((8.5, 3.1), 3.5, 1.2, boxstyle="round,pad=0.1", 
                     edgecolor='#6A1B9A', facecolor=c4, linewidth=2)
ax.add_patch(hyb)
ax.text(10.25, 4.05, 'DECISION & DIAGNOSTICS', ha='center', fontsize=13, fontweight='bold')
ax.text(10.25, 3.7, 'Critic Output: Gate + Rules', ha='center', fontsize=12.5)
ax.text(10.25, 3.35, 'Registered Threshold Decides', ha='center', fontsize=11.5,
        style='italic')

out = FancyBboxPatch((14.8, 2.2), 2.8, 1.8, boxstyle="round,pad=0.1",
                     edgecolor='#C62828', facecolor='#FFEBEE', linewidth=2.5)
ax.add_patch(out)
ax.text(16.2, 3.72, 'SEALED OUTPUT', ha='center', fontsize=16, fontweight='bold')
ax.text(16.2, 3.32, 'Final Bangla Response', ha='center', fontsize=14)
ax.text(16.2, 2.92, 'Attempt-Level Trace', ha='center', fontsize=13)
ax.text(16.2, 2.52, 'Accepted or Gave Up', ha='center', fontsize=13, fontweight='bold')

# ARROWS
ax.add_patch(FancyArrowPatch((6.12, 10.52), (6.68, 10.52), arrowstyle='simple',
                             mutation_scale=15, linewidth=1.2,
                             edgecolor='black', facecolor='black'))
ax.add_patch(FancyArrowPatch((12.12, 10.52), (12.68, 10.52), arrowstyle='simple',
                             mutation_scale=15, linewidth=1.2,
                             edgecolor='black', facecolor='black'))
ax.add_patch(FancyArrowPatch((15.4, 9.52), (15.4, 8.73), arrowstyle='->',
                             mutation_scale=25, linewidth=3, color='black'))

# Agent flow
ax.add_patch(FancyArrowPatch((3.78, 6.9), (4.92, 6.9), arrowstyle='->',
                             mutation_scale=20, linewidth=2.5, color='black'))
ax.add_patch(FancyArrowPatch((6.0, 6.32), (6.0, 5.98), arrowstyle='->',
                             mutation_scale=20, linewidth=2.5, color='black'))
ax.add_patch(FancyArrowPatch((6.0, 4.82), (6.0, 4.48), arrowstyle='->',
                             mutation_scale=20, linewidth=2.5, color='black'))

# RAG
ax.add_patch(FancyArrowPatch((8.42, 6.9), (7.08, 6.9), arrowstyle='->',
                             mutation_scale=20, linewidth=2, color='#6A1B9A', linestyle='--'))
ax.text(7.75, 7.2, 'Retrieve', ha='center', fontsize=13.5, color='#6A1B9A', fontweight='bold')

# Validator -> Hybrid
ax.plot([12.75, 12.75], [6.1, 4.9], color='#F57F17', linewidth=2, linestyle='--')
ax.plot([12.75, 11.0], [4.9, 4.9], color='#F57F17', linewidth=2, linestyle='--')
ax.plot([11.0, 11.0], [4.9, 4.3], color='#F57F17', linewidth=2, linestyle='--')
ax.add_patch(FancyArrowPatch((11.0, 4.46), (11.0, 4.38), arrowstyle='->',
                             mutation_scale=20, linewidth=2, color='#F57F17'))
ax.text(12.0, 5.4, 'Score', ha='center', fontsize=13.5, color='#F57F17', fontweight='bold')

# Critic to Hybrid
ax.add_patch(FancyArrowPatch((7.08, 3.9), (8.42, 3.9), arrowstyle='->',
                             mutation_scale=20, linewidth=2.5, color='black'))

# Decision to Sealed Output: either a pass or exhaustion at the retry ceiling
ax.add_patch(FancyArrowPatch((12.08, 3.7), (14.72, 3.7), arrowstyle='simple',
                             mutation_scale=18, linewidth=1.5,
                             edgecolor='#37474F', facecolor='#37474F'))
ax.text(13.4, 3.52, 'PASS OR\nLIMIT REACHED', ha='center', va='top', fontsize=13,
        fontweight='bold', color='#37474F', linespacing=0.9)

# Hybrid -> Agent 4 (FAIL)
ax.plot([9.5, 9.5], [3.1, 2.4], color='red', linewidth=2, linestyle='--')
ax.plot([9.5, 7.5], [2.4, 2.4], color='red', linewidth=2, linestyle='--')
ax.add_patch(FancyArrowPatch((7.5, 2.4), (7.08, 2.4), arrowstyle='->',
                             mutation_scale=20, linewidth=2, color='red'))
ax.text(8.2, 2.7, 'FAIL', ha='center', fontsize=13, fontweight='bold', color='red',
        bbox=dict(boxstyle='round', facecolor='white', edgecolor='red', linewidth=1.5))

# Agent 4 -> Agent 1 (retry re-retrieves before the next Writer attempt)
ax.plot([5.0, 4.2], [2.4, 2.4], color='red', linewidth=2, linestyle='--')
ax.plot([4.2, 4.2], [2.4, 6.62], color='red', linewidth=2, linestyle='--')
ax.add_patch(FancyArrowPatch((4.2, 6.62), (4.92, 6.62), arrowstyle='->',
                             mutation_scale=20, linewidth=2, color='red'))
ax.text(3.48, 4.35, 'RETRY VIA', ha='center', va='center', rotation=90,
        fontsize=11.5, color='red', fontweight='bold')
ax.text(3.72, 4.35, 'RESEARCHER', ha='center', va='center', rotation=90,
        fontsize=11.5, color='red', fontweight='bold')
ax.text(3.96, 4.35, 'MAX 3 WRITER ATTEMPTS', ha='center', va='center', rotation=90,
        fontsize=11.5, color='red', fontweight='bold')

# Legend
leg = [
    mpatches.Patch(facecolor=c1, edgecolor='#1565C0', linewidth=2,
                   label='Phase 1: Data Audit & Frozen Partitioning'),
    mpatches.Patch(facecolor=c2, edgecolor='#E65100', linewidth=2, label='Phase 2: Validator Training'),
    mpatches.Patch(facecolor=c3, edgecolor='#2E7D32', linewidth=2, label='Phase 3: Multi-Agent (Core AI)'),
    mpatches.Patch(facecolor='#F3E5F5', edgecolor='#7B1FA2', linewidth=2, alpha=0.3, label='Phase 4: UI Wrapper'),
    mpatches.Patch(facecolor='#FFF3E0', edgecolor='#FF6F00', linewidth=2, label='Phase 5: Explainability'),
    mpatches.Patch(facecolor='#E0F2F1', edgecolor='#00897B', linewidth=2, label='Phase 6: Evaluation'),
    mlines.Line2D([], [], color='green', linewidth=3, label='Success Path'),
    mlines.Line2D([], [], color='red', linewidth=2, linestyle='--', label='Self-Correction Loop')
]

# Attempt trace box
p5 = FancyBboxPatch((14.8, 6.1), 2.8, 1.6, boxstyle="round,pad=0.1", 
                    edgecolor='#FF6F00', facecolor='#FFF3E0', linewidth=2)
ax.add_patch(p5)
ax.text(16.2, 7.45, 'TRACE RECORD', ha='center', fontsize=14, fontweight='bold')
ax.text(16.2, 7.1, 'Retrieved IDs', ha='center', fontsize=12.5)
ax.text(16.2, 6.8, 'Scores & Decision', ha='center', fontsize=12.5)
ax.text(16.2, 6.5, 'Feedback & Cost', ha='center', fontsize=12.5)
ax.text(16.2, 6.2, 'Append Each Attempt', ha='center', fontsize=12,
        fontweight='bold')

# Every completed attempt is appended before the controller advances.
ax.plot([12.08, 14.45], [4.24, 4.24], color='#D66A00', linewidth=2,
        linestyle=(0, (3, 3)))
ax.plot([14.45, 14.45], [4.24, 6.9], color='#D66A00', linewidth=2,
        linestyle=(0, (3, 3)))
ax.add_patch(FancyArrowPatch((14.45, 6.9), (14.72, 6.9), arrowstyle='->',
                             mutation_scale=16, linewidth=2, color='#D66A00'))

# Trace is an audit sidecar associated with the sealed output, not a control-flow node.
ax.add_patch(FancyArrowPatch((16.2, 4.08), (16.2, 6.02), arrowstyle='<->',
                             mutation_scale=16, linewidth=2,
                             color='#FF6F00', linestyle=(0, (3, 3))))
ax.text(16.42, 5.05, 'AUDIT\nLINK', va='center', ha='left', linespacing=1.0,
        fontsize=13.5, color='#FF6F00', fontweight='bold')

# PHASE 5 — frozen comparison surface.
p5_eval = FancyBboxPatch((0.8, -1.15), 5.2, 1.65, boxstyle="round,pad=0.10",
                         edgecolor='#1565C0', facecolor='#E3F2FD', linewidth=2.5)
ax.add_patch(p5_eval)
ax.text(3.4, 0.23, 'PHASE 5: FROZEN EXPERIMENT',
        ha='center', fontsize=16, fontweight='bold')
ax.text(3.4, -0.22, '10 Conditions · 90 Plots · 2 Levels',
        ha='center', fontsize=14)
ax.text(3.4, -0.57, 'Paired Seeds: 42, 43, 44',
        ha='center', fontsize=14)
ax.text(3.4, -0.95, '5,400 Bangla Cases',
        ha='center', fontsize=14, fontweight='bold', color='#0D47A1')

# PHASE 6 — independent outcome evaluation.
p6_eval = FancyBboxPatch((6.9, -1.15), 5.2, 1.65, boxstyle="round,pad=0.10",
                         edgecolor='#6A1B9A', facecolor='#F3E5F5', linewidth=2.5)
ax.add_patch(p6_eval)
ax.text(9.5, 0.23, 'PHASE 6: OUTCOME EVALUATION',
        ha='center', fontsize=16, fontweight='bold')
ax.text(9.5, -0.22, r'Verifier-B ($\mathbf{BanglaBERT}$) · Outcome-Only',
        ha='center', fontsize=14)
ax.text(9.5, -0.57, 'Paired Bootstrap · McNemar · BH',
        ha='center', fontsize=13.2)
ax.text(9.5, -0.95, '100 Outputs · 300 Blinded Judgements',
        ha='center', fontsize=13.5, fontweight='bold')

# Separate dashed branch for the non-evidential local interface.
demo_box = FancyBboxPatch((12.8, -1.15), 5.2, 1.65, boxstyle="round,pad=0.10",
                          edgecolor='#00897B', facecolor='#E0F2F1', linewidth=2.5,
                          linestyle=(0, (6, 4)))
ax.add_patch(demo_box)
ax.text(15.4, 0.23, 'LIVE DEMONSTRATION INTERFACE',
        ha='center', fontsize=15, fontweight='bold', color='black')
ax.text(15.4, -0.22, 'Same Core Workflow',
        ha='center', fontsize=14)
ax.text(15.4, -0.57, 'Different Live Writer',
        ha='center', fontsize=14)
ax.text(15.4, -0.95, 'Not Experimental Evidence',
        ha='center', fontsize=14, fontweight='bold', color='#00796B')

# Solid research path: Phase 4 → Phase 5 → Phase 6.
ax.add_patch(FancyArrowPatch((3.4, 1.38), (3.4, 0.62), arrowstyle='->',
                             mutation_scale=22, linewidth=2.5, color='black'))
ax.add_patch(FancyArrowPatch((6.12, -0.33), (6.78, -0.33), arrowstyle='simple',
                             mutation_scale=15, linewidth=1.2,
                             edgecolor='black', facecolor='black'))

# Dashed demonstration branch: it exposes the workflow but contributes no evidence.
ax.plot([15.4, 15.4], [1.38, 0.87], color='#00897B', linewidth=2.2,
        linestyle=(0, (5, 3)))
ax.add_patch(FancyArrowPatch((15.4, 0.87), (15.4, 0.62), arrowstyle='->',
                             mutation_scale=20, linewidth=2.2, color='#00897B',
                             linestyle=(0, (5, 3))))

plt.tight_layout()
plt.savefig('E:/Research/Thesis/thesis/presentation/images/methodology_diagram.png',
            dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('E:/Research/Thesis/thesis/presentation/images/methodology_diagram.pdf',
            bbox_inches='tight', facecolor='white')
print("[SUCCESS] Saved final methodology diagram PNG and PDF.")
