"""Test build_canonical_payload — 09-DOMAIN-RULES §2.3."""

from app.domain.baseline import build_canonical_payload
from app.domain.canonical import text_hash
from app.domain.enums import AGREED, CLIENT_STATED

TEKS = "Layout renders correctly at 375px, 768px, and 1440px widths."


def ledger_lengkap():
    return {
        "deliverables": {
            "state": CLIENT_STATED,
            "value": [{"id": "d1", "title": "Instagram edits"}],
        },
        "acceptance_criteria": {
            "state": AGREED,
            "value": [{"deliverable_id": "d1", "criterion_key": "mobile-breakpoints", "text": TEKS}],
        },
        "out_of_scope": {"state": AGREED, "value": ["Thumbnail design"]},
        "timeline": {"final_deadline": {"state": CLIENT_STATED, "value": "2026-09-01"}},
        "revision_policy": {"rounds_total": {"state": AGREED, "value": 2}},
    }


def test_ekstrak_value_mentah_dari_tiap_field():
    payload = build_canonical_payload(ledger_lengkap(), version=1)
    assert payload["deliverables"] == [{"id": "d1", "title": "Instagram edits"}]
    assert payload["out_of_scope"] == ["Thumbnail design"]
    assert payload["timeline"]["final_deadline"] == "2026-09-01"
    assert payload["revision_policy"]["rounds_total"] == 2


def test_criteria_dapat_text_hash_dan_introduced_in_version():
    payload = build_canonical_payload(ledger_lengkap(), version=1)
    crit = payload["criteria"]["mobile-breakpoints"]
    assert crit["text"] == TEKS
    assert crit["text_hash"] == text_hash(TEKS)
    assert crit["introduced_in_version"] == 1


def test_ledger_kosong_menghasilkan_payload_dengan_default_kosong():
    payload = build_canonical_payload({}, version=1)
    assert payload["deliverables"] == []
    assert payload["criteria"] == {}
    assert payload["timeline"]["final_deadline"] is None
    assert payload["revision_policy"]["rounds_total"] is None


def test_dua_ledger_yang_setara_menghasilkan_payload_yang_sama_persis():
    """Payload deterministik -- prasyarat supaya payload_hash bisa dipakai
    sebagai precondition di endpoint confirm."""
    a = build_canonical_payload(ledger_lengkap(), version=1)
    b = build_canonical_payload(ledger_lengkap(), version=1)
    assert a == b
