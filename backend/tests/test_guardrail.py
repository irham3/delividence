"""Test klasifikasi Guardrail — 02-ARCHITECTURE §4.5."""

import pytest

from app.domain import guardrail
from app.domain.enums import DomainError

BASELINE = {
    "canonical_payload": {
        "criteria": {"mobile-breakpoints": {"text": "Renders at 375px, 768px, and 1440px."}},
        "out_of_scope": ["No paid ads.", "No video assets."],
        "deliverables": [{"id": "d1", "title": "Landing page"}],
    }
}


def test_citable_text_menggabungkan_criteria_out_of_scope_dan_deliverables():
    text_by_ref = guardrail.citable_text(BASELINE)
    assert text_by_ref["mobile-breakpoints"] == "Renders at 375px, 768px, and 1440px."
    assert text_by_ref["out_of_scope[0]"] == "No paid ads."
    assert text_by_ref["out_of_scope[1]"] == "No video assets."
    assert text_by_ref["deliverables[0]"] == "Landing page"


def test_in_scope_dengan_kutipan_valid_dipertahankan():
    text_by_ref = guardrail.citable_text(BASELINE)
    result, valid = guardrail.classify(
        "IN_SCOPE",
        [{"ref": "mobile-breakpoints", "quote": "Renders at 375px"}],
        text_by_ref,
    )
    assert result == "IN_SCOPE"
    assert len(valid) == 1


def test_in_scope_tanpa_kutipan_valid_turun_ke_ambiguous():
    text_by_ref = guardrail.citable_text(BASELINE)
    result, valid = guardrail.classify(
        "IN_SCOPE",
        [{"ref": "mobile-breakpoints", "quote": "kutipan karangan"}],
        text_by_ref,
    )
    assert result == "AMBIGUOUS"
    assert valid == []


def test_change_request_tanpa_kutipan_sama_sekali_turun_ke_ambiguous():
    result, valid = guardrail.classify("CHANGE_REQUEST", [], guardrail.citable_text(BASELINE))
    assert result == "AMBIGUOUS"
    assert valid == []


def test_change_request_mengutip_out_of_scope_dipertahankan():
    text_by_ref = guardrail.citable_text(BASELINE)
    result, valid = guardrail.classify(
        "CHANGE_REQUEST", [{"ref": "out_of_scope[0]", "quote": "No paid ads."}], text_by_ref
    )
    assert result == "CHANGE_REQUEST"
    assert len(valid) == 1


def test_ambiguous_tidak_butuh_kutipan():
    result, valid = guardrail.classify("AMBIGUOUS", [], guardrail.citable_text(BASELINE))
    assert result == "AMBIGUOUS"
    assert valid == []


def test_ref_tidak_dikenal_dibuang_bukan_error():
    text_by_ref = guardrail.citable_text(BASELINE)
    result, valid = guardrail.classify(
        "IN_SCOPE", [{"ref": "tidak-ada", "quote": "apa saja"}], text_by_ref
    )
    assert result == "AMBIGUOUS"
    assert valid == []


def test_satu_kutipan_buruk_tidak_menggagalkan_kutipan_lain_yang_valid():
    text_by_ref = guardrail.citable_text(BASELINE)
    result, valid = guardrail.classify(
        "IN_SCOPE",
        [
            {"ref": "mobile-breakpoints", "quote": "karangan"},
            {"ref": "mobile-breakpoints", "quote": "Renders at 375px"},
        ],
        text_by_ref,
    )
    assert result == "IN_SCOPE"
    assert len(valid) == 1


def test_classification_tidak_dikenal_ditolak():
    with pytest.raises(DomainError):
        guardrail.classify("MAYBE", [], guardrail.citable_text(BASELINE))
