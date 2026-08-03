# ══════════════════════════════════════════════════════════════════════════
#  S2e on Kaggle — paste this as ONE cell in a Kaggle notebook and run it.
#
#  Why a standalone cell instead of re-running s2_pilot_kaggle.ipynb:
#  S2e does NOT need G1 re-run. It reads results/s2d_ktable_regionA.csv, which
#  is committed to the repo, and re-embeds only region A (1,897 short reviews).
#  Re-running the whole notebook would redo the full-corpus S2 and the entire
#  K-table for nothing.
#
#  Before you run:
#    • Internet must be ON            (LaBSE weights download from HuggingFace)
#    • bn_clean.csv must be attached  (right panel → "+ Add Input")
#    • GPU is optional               (1,897 short texts; CPU is a minute or two)
#
#  ⚠️ Check the commit hash the clone prints. If it is not d2fb159 or later,
#     the push has not landed and this will fail on a missing config — which is
#     the correct behaviour, not a bug to work around.
#
#  Read docs/protocol.md (RQ1-D) BEFORE reading the output. The bands were
#  fixed before the script was written.
# ══════════════════════════════════════════════════════════════════════════

# Step out of the clone directory BEFORE deleting it, or the shell loses its
# own working directory and every later command fails with a getcwd error.
%cd /kaggle/working
!rm -rf /kaggle/working/thesis
!git clone --depth 1 https://github.com/alphapie77/BSc_Thesis.git /kaggle/working/thesis
%cd /kaggle/working/thesis
!git log --oneline -1

!pip install -q sentence-transformers pyyaml

import shutil
from pathlib import Path

hits = sorted(Path("/kaggle/input").rglob("bn_clean.csv"))
if not hits:
    visible = [str(p) for p in Path("/kaggle/input").rglob("*") if p.is_file()][:20]
    raise FileNotFoundError(
        "bn_clean.csv is not under /kaggle/input. Attach the private dataset "
        f"with '+ Add Input' in the right-hand panel. Visible now: {visible or 'NOTHING'}"
    )
Path("data/cleaned").mkdir(parents=True, exist_ok=True)
shutil.copy(hits[0], "data/cleaned/bn_clean.csv")
print("input:", hits[0])

# Tests first. These need no sklearn and no GPU, and if they fail the report
# that follows is not worth reading.
!python tests/test_s2e_profile.py

!python -m src.cluster.s2e_profile --config configs/s2e_profile.yaml

# Package the four outputs for download, so they can be committed with their
# lab-notebook entry. The embedding cache is deliberately excluded: it is large
# and fully reproducible from bn_clean.csv.
import zipfile
OUT = Path("/kaggle/working/s2e_outputs.zip")
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for f in ("results/s2e_regionA_k2_profile.md",
              "results/s2e_regionA_k2_assignments.csv",
              "results/s2e_regionA_k2_features.csv",
              "results/s2e_regionA_k2_logodds.csv"):
        p = Path(f)
        print(("added   " if p.exists() else "MISSING ") + f)
        if p.exists():
            z.write(p, f)
print("wrote", OUT)

from IPython.display import Markdown, display
display(Markdown(Path("results/s2e_regionA_k2_profile.md").read_text(encoding="utf-8")))
