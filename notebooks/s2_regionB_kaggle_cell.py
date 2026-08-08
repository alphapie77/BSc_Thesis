# ══════════════════════════════════════════════════════════════════════════
#  RQ1-G — REPLICATION RUN ON REGION B. Paste as ONE cell and run.
#
#  Region A selected K = 2. The strongest thing that could be said about that
#  split is that it appears in a SECOND corpus, with a different register and
#  different provenance. This points the IDENTICAL instrument at region B.
#
#  Interpretation is pre-registered in docs/protocol.md, "RQ1-G pre-commitment",
#  written before this ran -- including the matching rule and all four outcomes.
#  READ IT BEFORE READING THE OUTPUT.
#
#  Why this matters more than it did last week: G-300 round 1 came back
#  inconclusive (alpha 0.497 -- the scale collapsed, not the raters), and there
#  is no annotator time for a round 2. This run needs NO PEOPLE, and it is now
#  the only remaining external evidence that the K = 2 split is not an artefact
#  of one corpus. It is NOT a substitute for human validation and must never be
#  reported as one.
#
#  Before you run:
#    • Internet ON, bn_clean.csv attached (+ Add Input)
#    • GPU strongly preferred -- region B is ~2,700 rows and the K-table is the
#      slow part (20 split-pairs x 7 K, plus 100 bootstrap runs x 7)
#    • Expect 15-25 minutes. The four steps run in order and each needs the one
#      before it.
# ══════════════════════════════════════════════════════════════════════════

%cd /kaggle/working
!rm -rf /kaggle/working/thesis
!git clone --depth 1 https://github.com/alphapie77/BSc_Thesis.git /kaggle/working/thesis
%cd /kaggle/working/thesis
!git log --oneline -1

!pip install -q sentence-transformers pyyaml hdbscan

import shutil
from pathlib import Path

hits = sorted(Path("/kaggle/input").rglob("bn_clean.csv"))
if not hits:
    visible = [str(p) for p in Path("/kaggle/input").rglob("*") if p.is_file()][:20]
    raise FileNotFoundError(
        "bn_clean.csv is not under /kaggle/input. Attach the private dataset "
        f"with '+ Add Input'. Visible now: {visible or 'NOTHING'}"
    )
Path("data/cleaned").mkdir(parents=True, exist_ok=True)
shutil.copy(hits[0], "data/cleaned/bn_clean.csv")
print("input:", hits[0])

# Tests first. The one that matters here is
# test_the_region_B_replication_uses_an_IDENTICAL_instrument -- if the two
# configs have drifted apart, whatever this run produces is not a replication.
!python tests/test_s2e_profile.py
!python tests/test_s2f_residual.py

print("\n" + "=" * 70 + "\n1/4  S2-B: near-duplicate removal + trap-check on region B\n")
!python -m src.cluster.s2_pilot --config configs/s2_pilot_regionB.yaml

print("\n" + "=" * 70 + "\n2/4  GATE G1 on region B -- the slow one. Does B also select K = 2?\n")
!python -m src.cluster.s2d_ktable --config configs/s2d_ktable_regionB.yaml

# ⚠️ If G1 selects something other than 2 here, STOP AND READ RQ1-G.
# Steps 3 and 4 are hard-coded to k: 2 and would then be profiling a partition
# the K-table did not select. That is outcome 3 in the pre-registration
# ("B selects a different K") and it is a reportable result, not a failure --
# but it is not something to paper over by running the next two cells anyway.

print("\n" + "=" * 70 + "\n3/4  S2e: what is B's K=2 partition made of?\n"
      "     THE NUMBER TO FIND: types_at_budget per cluster. RQ1-G's matching\n"
      "     rule reads it, and it was fixed before any of this ran.\n")
!python -m src.cluster.s2e_profile --config configs/s2e_profile_regionB.yaml

print("\n" + "=" * 70 + "\n4/4  S2f: is B's cut just valence and verbosity either?\n")
!python -m src.cluster.s2f_residual --config configs/s2f_residual_regionB.yaml

import zipfile
OUT = Path("/kaggle/working/s2_regionB_outputs.zip")
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for f in ("results/s2b2_regionB_trapcheck.md",
              "results/s2b2_regionB_cluster_assignments.csv",
              "results/s2d_ktable_regionB.md",
              "results/s2d_ktable_regionB.csv",
              "results/s2e_regionB_k2_profile.md",
              "results/s2e_regionB_k2_assignments.csv",
              "results/s2e_regionB_k2_features.csv",
              "results/s2e_regionB_k2_logodds.csv",
              "results/s2f_regionB_k2_residual.md",
              "results/s2f_regionB_k2_cells.csv"):
        p = Path(f)
        print(("added   " if p.exists() else "MISSING ") + f)
        if p.exists():
            z.write(p, f)
print("wrote", OUT)

# Fill expected_n in the region-B configs from the counts printed above, so a
# later stale input is caught. They ran unguarded on purpose and said so.
from IPython.display import Markdown, display
display(Markdown(Path("results/s2d_ktable_regionB.md").read_text(encoding="utf-8")))
