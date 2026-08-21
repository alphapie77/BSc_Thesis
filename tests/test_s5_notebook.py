import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _nb():
    return json.loads((ROOT / "notebooks/s5_main_bn_kaggle.ipynb").read_text(encoding="utf-8"))


def test_notebook_is_runner_only_and_pins_a_full_commit():
    nb = _nb()
    for index, cell in enumerate(nb["cells"]):
        if cell["cell_type"] == "code":
            compile("".join(cell.get("source", [])), f"cell-{index}", "exec")
    code = "\n".join(
        "".join(cell.get("source", []))
        for cell in nb["cells"] if cell["cell_type"] == "code"
    )
    match = re.search(r"RUNNER_COMMIT = '([0-9a-f]{40})'", code)
    assert match
    assert "subprocess.run" in code and "check=True" in code
    assert "Verifier-B" not in code and "verifier_b" not in code.lower()
    assert code.index("preflight_s5_kaggle.py") < code.index("build_index.py")
    assert code.index("preflight_s5_kaggle.py") < code.index("run_s5_main_bn.py")
    assert "'--index-only'" in code


def test_notebook_resumes_the_verified_smoke_with_chunk_zero_and_exports_audit_artifacts():
    nb = _nb()
    code = "\n".join("".join(c.get("source", [])) for c in nb["cells"])
    assert "RUN_SMOKE = False" in code
    assert "RUN_CHUNK = True" in code
    assert "REPLICATE_SEED = 42" in code
    assert "START_CASE = 20" in code
    assert "N_CASES = 40" in code
    assert "'--limit','1'" in code
    for name in (
        "s5_main_bn_calls.jsonl", "s5_main_bn_gemini_calls.jsonl",
        "s5_main_bn_cases.jsonl", "s5_main_bn_preflight.json",
        "s5_checkpoint.zip",
    ):
        assert name in code


def test_kaggle_work_cells_are_restart_safe_and_model_input_is_unambiguous():
    nb = _nb()
    work_cells = [
        "".join(cell.get("source", []))
        for cell in nb["cells"]
        if cell["cell_type"] == "code"
        and any(marker in "".join(cell.get("source", [])) for marker in (
            "bn_clean.csv", "restore = {", "preflight_s5_kaggle.py",
            "RUN_SMOKE = False", "RUN_CHUNK = True", "snapshot =",
        ))
    ]
    assert len(work_cells) == 6
    assert all("REPO = Path('/kaggle/working/s5_repo_2e91989')" in cell for cell in work_cells)
    assert all("os.chdir(REPO)" in cell for cell in work_cells)
    setup = next(cell for cell in work_cells if "bn_clean.csv" in cell)
    assert "assert len(clean) == 1" in setup
    for cell in work_cells:
        if "MODEL_PATH" in cell:
            assert "assert len(gemma) == 1" in cell
