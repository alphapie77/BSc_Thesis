"""Tests for the explicit single-coder S4.6 deviation path."""
import pytest

from src.eval.finalize_s4_failure_taxonomy import finalize


AUDIT = {
    "coder_a_identity": "Codex under authorization",
    "user_reviewed_coder_a_before_endorsement": True,
    "independent_coder_b": False,
    "agreement_available": False,
    "finalization_status": "single_coder_user_endorsed_protocol_deviation",
}


def _row(case_id="p:L0", **updates):
    row = {
        "case_id": case_id, "target_level": "0", "emitted_attempt": "2",
        "wrong_sentiment": "0", "too_short": "0", "off_topic": "0",
        "template_repeat": "0", "register_or_honorific": "0", "other": "0",
        "other_label": "", "coder_notes": "none visible",
    }
    row.update(updates)
    return row


def test_single_coder_result_never_manufactures_agreement():
    result = finalize([_row()], AUDIT, 1)
    assert result["agreement"] is None
    assert not result["independent_coder_b"]
    assert result["uncategorized_no_observable_registered_error"] == 1


def test_other_requires_a_post_hoc_label():
    with pytest.raises(ValueError, match="requires other_label"):
        finalize([_row(other="1")], AUDIT, 1)


def test_category_counts_and_other_labels_are_auditable():
    rows = [
        _row("a:L0", off_topic="1"),
        _row("b:L1", other="1", other_label="axis mismatch"),
    ]
    result = finalize(rows, AUDIT, 2)
    assert result["category_counts"]["off_topic"] == 1
    assert result["category_counts"]["other"] == 1
    assert result["other_label_counts_post_hoc"] == {"axis mismatch": 1}
