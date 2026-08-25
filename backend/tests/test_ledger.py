"""Test apply_client_answer — 01-PRD §4.1."""

from app.domain.enums import CLIENT_STATED
from app.domain.ledger import apply_client_answer


def test_field_top_level_diset_client_stated():
    ledger = apply_client_answer({}, "out_of_scope", ["No paid ads."])
    assert ledger == {"out_of_scope": {"value": ["No paid ads."], "state": CLIENT_STATED}}


def test_field_nested_membuat_parent_kalau_belum_ada():
    ledger = apply_client_answer({}, "timeline.final_deadline", "2026-08-31")
    assert ledger["timeline"]["final_deadline"] == {
        "value": "2026-08-31",
        "state": CLIENT_STATED,
    }


def test_field_nested_tidak_menimpa_sibling_yang_sudah_ada():
    ledger = {"timeline": {"kickoff": {"value": "2026-08-20", "state": CLIENT_STATED}}}
    apply_client_answer(ledger, "timeline.final_deadline", "2026-08-31")
    assert ledger["timeline"]["kickoff"]["value"] == "2026-08-20"
    assert ledger["timeline"]["final_deadline"]["value"] == "2026-08-31"


def test_menimpa_nilai_lama_di_field_yang_sama():
    ledger = apply_client_answer({}, "revision_policy.rounds_total", 2)
    apply_client_answer(ledger, "revision_policy.rounds_total", 3)
    assert ledger["revision_policy"]["rounds_total"]["value"] == 3


def test_mengembalikan_objek_ledger_yang_sama_in_place():
    ledger = {}
    result = apply_client_answer(ledger, "out_of_scope", [])
    assert result is ledger
