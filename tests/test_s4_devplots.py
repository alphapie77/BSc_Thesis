"""S4.dev — the dev-plot generation runner's invariants.

These test the things that would be silent if wrong: the danda exclusion (which
already produced one 18-vs-1 error), the absence of a Critic in this step, and
the config's agreement with the frozen plots split.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agents.run_devplots import foreign_script_chars  # noqa: E402

CFG = yaml.safe_load((ROOT / "configs" / "s4_devplots.yaml").read_text(encoding="utf-8"))
SRC = (ROOT / "src" / "agents" / "run_devplots.py").read_text(encoding="utf-8")


def test_danda_is_not_foreign_script():
    """U+0964 sits in the Devanagari block and Bangla uses it.

    Counting it as foreign made 18 of 20 pilot generations look script-confused
    when the real leak rate was 1 in 20. The bug is cheap to reintroduce because
    a naive Devanagari range check looks obviously correct.
    """
    assert foreign_script_chars("ভালো সিনেমা।") == {}
    assert foreign_script_chars("ভালো।। খুব ভালো।") == {}


def test_real_foreign_script_is_still_caught():
    """The guard above must not become a blanket exemption."""
    assert foreign_script_chars("सलमान শাহ") == {"devanagari": 5}
    assert foreign_script_chars("অভিনয় actors") == {"latin": 6}
    assert foreign_script_chars("সিনেমা കണ്ട")["malayalam"] > 0


def test_no_critic_and_no_reflector_in_this_step():
    """`w` and τ do not exist yet; fitting them from a loop that used them
    would be circular. Enforced against the import graph, not the docstring."""
    tree = ast.parse(SRC)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
    assert not any("critic" in m or "reflector" in m or "graph" in m
                   for m in imported), sorted(imported)


def test_verifier_b_is_unreachable(  ):
    """Inviolable rule 6 restated at the file level."""
    assert "verifier_b" not in SRC
    assert "train_verifier_b" not in SRC


def test_config_matches_the_frozen_dev_split():
    import csv
    rows = [r for r in csv.DictReader(
        open(ROOT / "data" / "plots" / "plots_bn.csv", encoding="utf-8"))
        if r["split"] == "dev"]
    assert CFG["sample"]["n_plots"] == len(rows) == 30
    assert CFG["sample"]["levels"] == [0, 1]


def test_generation_settings_match_the_pilot():
    """A mid-experiment change to any of these confounds the change with
    whatever else moved. Batch size in particular is provenance, not a knob."""
    pilot = yaml.safe_load(
        (ROOT / "configs" / "s4_pilot_local.yaml").read_text(encoding="utf-8"))
    for k in ("batch_size", "quantization", "max_new_tokens", "seed", "provider"):
        assert CFG[k] == pilot[k], k


def test_single_generator_arm_is_explicit():
    """The second arm collapsed (TigerLLM weights = gemma). One arm is a
    registered decision, not an omission — so the config must state one model,
    and the file must carry the reason."""
    assert list(CFG["models"]) == ["arm_a"]
    assert "2604.04532" in (ROOT / "configs" / "s4_devplots.yaml").read_text(
        encoding="utf-8"), "the single-backbone limitation must cite its source"


def test_outputs_do_not_collide_with_the_pilot_archive():
    """Two archives from different steps may never be merged by accident."""
    pilot = yaml.safe_load(
        (ROOT / "configs" / "s4_pilot_local.yaml").read_text(encoding="utf-8"))
    assert set(CFG["outputs"].values()).isdisjoint(set(pilot["outputs"].values()))


def test_the_length_diagnostic_is_reported():
    """Pre-registered in axis_definition.md §3c before any generation existed."""
    assert CFG["report"]["length_by_level"] is True
    assert "LENGTH_MAY_EXPLAIN_LEVEL" in SRC
    assert "13.12" in SRC and "8.85" in SRC


def test_retrieval_encoder_is_pinned_to_cpu():
    """LaBSE and a 12B generator must not share 16 GB of VRAM.

    Retrieval happens once, up front, and the encoder is released before the
    generator loads. Regression guard for the 2026-08-15 OOM.
    """
    assert 'device="cpu"' in SRC
    assert SRC.index("del researcher") < SRC.index("LocalWriter")


def test_requested_quantisation_is_verified_after_load():
    """An ignored `quantization_config` still 'loads' — in fp16, at 3.4x the
    memory — and the only symptom is a crash somewhere else. The guard turns
    that into a named failure at the point of cause."""
    lw = (ROOT / "src" / "agents" / "local_writer.py").read_text(encoding="utf-8")
    assert "is_loaded_in_4bit" in lw
    assert "quantisation was requested" in lw


def test_report_writers_are_called_with_the_right_signature():
    """`write_text_lf(path, text)` — path FIRST. The reversed call cost a full
    120-generation run its report on 2026-08-15: every generation was safely on
    disk, but the step still exited non-zero at the last line.

    Checked by binding the real signature rather than by reading the call, so a
    future rename fails here instead of at the end of a 40-minute run.
    """
    import inspect

    from src.common.provenance import write_text_lf
    params = list(inspect.signature(write_text_lf).parameters)
    assert params[:2] == ["path", "text"]
    assert "config_path" not in params
    assert 'write_text_lf(out["report_md"]' in SRC
