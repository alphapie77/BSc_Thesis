"""Every code cell in every runner notebook must at least compile.

This exists because it did not. `s2_pilot_kaggle.ipynb` has been edited five
times by programmatic string surgery on its JSON, and one of those edits sliced
the final line off a cell -- leaving a `print(` with no closing paren. Nothing
caught it here; it surfaced as a `SyntaxError` on Kaggle, after a fifteen-minute
GPU run, in the cell that packages the results.

A compile check is cheap and would have caught it before the notebook was ever
pushed. It does not verify that the cells *work* -- only that they are not
syntactically broken, which is the failure mode string editing actually
produces.

Run:  python -m pytest tests/test_notebooks.py -q
      python tests/test_notebooks.py          (no pytest needed)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted((ROOT / "notebooks").glob("*.ipynb"))

#: Cells that are shell or IPython magic, not Python. `compile()` would reject
#: `!pip install` and `%cd`, which are legitimate in a notebook.
def is_magic(src: str) -> bool:
    stripped = src.lstrip()
    return (stripped.startswith(("!", "%"))
            or "\n!" in src or "\n%" in src)


def test_notebooks_exist():
    assert NOTEBOOKS, "no notebooks found -- has the directory moved?"


def test_every_notebook_is_valid_json():
    for nb_path in NOTEBOOKS:
        try:
            nb = json.loads(nb_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise AssertionError(f"{nb_path.name} is not valid JSON: {e}")
        assert "cells" in nb, f"{nb_path.name} has no cells"
        assert nb.get("nbformat") == 4, f"{nb_path.name} is not nbformat 4"


def test_every_code_cell_compiles():
    problems = []
    for nb_path in NOTEBOOKS:
        nb = json.loads(nb_path.read_text(encoding="utf-8"))
        code = [c for c in nb["cells"] if c["cell_type"] == "code"]
        for i, cell in enumerate(code):
            src = "".join(cell["source"])
            if not src.strip() or is_magic(src):
                continue
            try:
                compile(src, f"{nb_path.name}[cell {i}]", "exec")
            except SyntaxError as e:
                problems.append(
                    f"{nb_path.name} cell {i}: line {e.lineno}: {e.msg}"
                )
    assert not problems, "\n  " + "\n  ".join(problems)


def test_no_cell_ends_mid_statement():
    """Catch the specific mutilation: a source list truncated by a bad slice.

    A cell whose last non-empty line has unbalanced brackets is the signature of
    programmatic editing that dropped a line, and it is worth naming separately
    from a generic SyntaxError because the cause is different.
    """
    problems = []
    for nb_path in NOTEBOOKS:
        nb = json.loads(nb_path.read_text(encoding="utf-8"))
        for i, cell in enumerate(c for c in nb["cells"]
                                 if c["cell_type"] == "code"):
            src = "".join(cell["source"])
            if not src.strip() or is_magic(src):
                continue
            depth = 0
            in_str = None
            prev = ""
            for ch in src:
                if in_str:
                    if ch == in_str and prev != "\\":
                        in_str = None
                elif ch in "\"'":
                    in_str = ch
                elif ch in "([{":
                    depth += 1
                elif ch in ")]}":
                    depth -= 1
                prev = ch
            if depth != 0:
                problems.append(
                    f"{nb_path.name} cell {i}: {depth:+d} unbalanced bracket(s) "
                    "-- a line was probably dropped by an edit"
                )
    assert not problems, "\n  " + "\n  ".join(problems)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed "
          f"({len(NOTEBOOKS)} notebook(s) checked)")
    raise SystemExit(1 if failed else 0)
