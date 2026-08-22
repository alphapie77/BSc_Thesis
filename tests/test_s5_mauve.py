from src.eval.analyze_s5_mauve_bn import choose_reference


def test_reference_subsample_is_level_seeded_deterministic_and_without_replacement():
    source = [f"t{i}" for i in range(300)]
    selected = choose_reference(source, 270, 0)
    assert selected == choose_reference(source, 270, 0)
    assert len(selected) == len(set(selected)) == 270
    assert selected != choose_reference(source, 270, 1)
