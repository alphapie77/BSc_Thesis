from pathlib import Path

import pandas as pd
import pytest

from src.eval.plot_s5_realism_bn import CONDITIONS, RealismFigureError, build_figure


def _frames():
    base = [{"condition": c, "target_level": level} for c in CONDITIONS for level in (0, 1)]
    lengths = pd.DataFrame([{**row, "js_length_exact_word_count": .2} for row in base])
    diversity = pd.DataFrame([{**row, "rate_texts_under_4_words": .1} for row in base])
    mauve = pd.DataFrame([{**row, "labse_feature_mauve": .03} for row in base])
    return lengths, diversity, mauve


def test_realism_figure_renders_exact_registered_cells(tmp_path: Path):
    out = tmp_path / "realism.png"
    build_figure(*_frames(), out, provenance={"git_commit": "test-clean"})
    assert out.read_bytes().startswith(b"\x89PNG")
    assert out.stat().st_size > 10_000


def test_realism_figure_rejects_missing_cell(tmp_path: Path):
    lengths, diversity, mauve = _frames()
    with pytest.raises(RealismFigureError, match="exact 20"):
        build_figure(lengths.iloc[:-1], diversity, mauve, tmp_path / "bad.png",
                     provenance={"git_commit": "test-clean"})
