import json
from pathlib import Path

from src.annotate.s5_human_eval_build import interface_html, select_items
from src.eval.s5_contract import CONDITIONS


ROOT = Path(__file__).resolve().parents[1]


def test_balanced_deterministic_sample_from_frozen_archive():
    rows = [json.loads(x) for x in (ROOT / "results/s5_main_bn_cases.jsonl").read_text(
        encoding="utf-8").splitlines() if x.strip()]
    a = select_items(rows, seed=42, per_cell=5)
    b = select_items(rows, seed=42, per_cell=5)
    assert [x["key"] for x in a] == [x["key"] for x in b]
    assert len(a) == len({x["key"] for x in a}) == 100
    counts = {(c, level): 0 for c in CONDITIONS for level in (0, 1)}
    for row in a:
        counts[(row["condition"], int(row["target_level"]))] += 1
    assert set(counts.values()) == {5}
    # With 100 items over 90 plots, the allocator achieves the theoretical
    # minimum of ten repeated plot exposures and avoids duplicate output text.
    assert len({x["plot_id"] for x in a}) == 90
    from src.annotate.s5_human_eval_build import emitted_text
    assert len({emitted_text(x) for x in a}) == 100
    for condition in CONDITIONS:
        for level in (0, 1):
            seeds = [x["replicate_seed"] for x in a if x["condition"] == condition
                     and int(x["target_level"]) == level]
            assert sorted(seeds.count(s) for s in (42, 43, 44)) == [1, 2, 2]


def test_interface_is_blinded_and_forced_binary():
    secret = "S5BN|s42|BN002|L0|zero_shot"
    page = interface_html([{"item_id": "H001", "plot": "একটি প্লট",
                            "review": "একটি মন্তব্য", "key": secret}],
                          annotator="A", provenance={"timestamp_utc": "t", "git_commit": "g"})
    assert secret not in page
    assert "zero_shot" not in page
    assert "verifier" not in page.lower()
    assert 'value="U"' not in page
    assert "সব item-এর উত্তর দিন" in page
