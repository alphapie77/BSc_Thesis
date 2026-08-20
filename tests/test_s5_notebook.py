import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _nb():
    return json.loads((ROOT / "notebooks/s5_main_bn_kaggle.ipynb").read_text(encoding="utf-8"))


def test_notebook_is_runner_only_and_pins_a_full_commit():
    nb = _nb()
    code = "\n".join(
        "".join(cell.get("source", []))
        for cell in nb["cells"] if cell["cell_type"] == "code"
    )
    match = re.search(r"RUNNER_COMMIT = '([0-9a-f]{40})'", code)
    assert match
    assert "subprocess.run" in code and "check=True" in code
    assert "Verifier-B" not in code and "verifier_b" not in code.lower()


def test_notebook_defaults_to_smoke_only_and_exports_all_resume_archives():
    nb = _nb()
    code = "\n".join("".join(c.get("source", [])) for c in nb["cells"])
    assert "RUN_SMOKE = True" in code
    assert "RUN_CHUNK = False" in code
    assert "'--limit','1'" in code
    for name in (
        "s5_main_bn_calls.jsonl", "s5_main_bn_gemini_calls.jsonl",
        "s5_main_bn_cases.jsonl", "s5_checkpoint.zip",
    ):
        assert name in code
