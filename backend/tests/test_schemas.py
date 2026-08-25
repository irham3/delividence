"""Test skema ledger/baseline/audit event — 09-DOMAIN-RULES §10 butir 1.

Skema hanya memvalidasi BENTUK. Aturan domain (effective_status, readiness)
tetap diuji di test_domain.py; di sini kita cek bahwa bentuk yang sama yang
sudah dipakai test_domain.py dan app.audit benar-benar tervalidasi, dan
bentuk yang salah/typo benar-benar ditolak.
"""

import pytest
from pydantic import ValidationError

from app import audit
from app.domain import canonical, schemas
from app.domain.enums import ACCEPTED, AGREED, CLIENT_STATED, NOT_SET

TEKS = "Layout renders correctly at 375px, 768px, and 1440px widths."


# --- LedgerField -------------------------------------------------------------


def test_ledger_field_minimal_tanpa_provenance():
    f = schemas.LedgerField(state=CLIENT_STATED, value="2026-09-01")
    assert f.state == CLIENT_STATED
    assert f.source_quote is None


def test_ledger_field_state_tidak_dikenal_ditolak():
    with pytest.raises(ValidationError):
        schemas.LedgerField(state="NOT_A_STATE", value=1)


def test_ledger_field_typo_field_ditolak():
    with pytest.raises(ValidationError):
        schemas.LedgerField(state=CLIENT_STATED, value=1, sorce_quote="typo")


# --- DealLedger, termasuk fixture yang dipakai test_domain.py --------------


def ledger_lengkap():
    return {
        "deliverables": {
            "state": CLIENT_STATED,
            "value": [{"id": "d1", "title": "Instagram edits"}],
        },
        "acceptance_criteria": {
            "state": AGREED,
            "value": [{"deliverable_id": "d1", "criterion_key": "k1", "text": TEKS}],
        },
        "out_of_scope": {"state": AGREED, "value": ["Thumbnail design"]},
        "timeline": {"final_deadline": {"state": CLIENT_STATED, "value": "2026-09-01"}},
        "revision_policy": {"rounds_total": {"state": AGREED, "value": 2}},
    }


def test_ledger_lengkap_dari_test_domain_tervalidasi():
    ledger = schemas.DealLedger.model_validate(ledger_lengkap())
    assert ledger.deliverables.value[0].id == "d1"
    assert ledger.acceptance_criteria.value[0].criterion_key == "k1"
    assert ledger.timeline.final_deadline.value == "2026-09-01"
    assert ledger.revision_policy.rounds_total.value == 2


def test_ledger_kosong_tervalidasi():
    assert schemas.DealLedger.model_validate({}) is not None


def test_not_set_sentinel_diterima_untuk_rounds_total():
    l = ledger_lengkap()
    l["revision_policy"]["rounds_total"]["value"] = NOT_SET
    ledger = schemas.DealLedger.model_validate(l)
    assert ledger.revision_policy.rounds_total.value == NOT_SET


def test_deliverable_tanpa_id_ditolak():
    l = ledger_lengkap()
    del l["deliverables"]["value"][0]["id"]
    with pytest.raises(ValidationError):
        schemas.DealLedger.model_validate(l)


# --- Baseline & criteria, contoh persis dari 09-DOMAIN-RULES §2.3 ---------


def test_baseline_dari_contoh_dokumen_tervalidasi():
    baseline = schemas.Baseline.model_validate(
        {
            "version": 2,
            "status": "ACTIVE",
            "canonical_payload": {
                "deliverables": ["..."],
                "in_scope": ["..."],
                "out_of_scope": ["..."],
                "timeline": {"final_deadline": "2026-08-28"},
                "revision_policy": {"rounds_total": 2},
                "criteria": {
                    "mobile-breakpoints": {
                        "text": TEKS,
                        "text_hash": canonical.text_hash(TEKS),
                        "introduced_in_version": 1,
                    },
                },
            },
            "payload_hash": "sha256:7d13",
            "approved_by": "client",
            "approved_at": "2026-08-26T04:10:00Z",
            "activated_seq": 41,
        }
    )
    assert baseline.canonical_payload.criteria["mobile-breakpoints"].text_hash.startswith(
        "sha256:"
    )


def test_criterion_key_format_ditolak_di_canonical_payload():
    with pytest.raises(ValidationError):
        schemas.CanonicalPayload.model_validate(
            {"criteria": {"Mobile-Breakpoints": {"text": TEKS, "text_hash": "sha256:x"}}}
        )


# --- CriterionDecision, bentuk yang dipakai app.domain.criteria ------------


def test_criterion_decision_dari_bentuk_test_domain():
    d = schemas.CriterionDecision.model_validate(
        {
            "criterion_key": "k1",
            "decision": ACCEPTED,
            "baseline_version": 1,
            "criterion_text_hash": canonical.text_hash(TEKS),
            "seq": 10,
        }
    )
    assert d.decision == ACCEPTED


def test_criterion_decision_nilai_tidak_dikenal_ditolak():
    with pytest.raises(ValidationError):
        schemas.CriterionDecision.model_validate(
            {
                "criterion_key": "k1",
                "decision": "MAYBE",
                "baseline_version": 1,
                "criterion_text_hash": "sha256:x",
                "seq": 10,
            }
        )


# --- AuditEventEnvelope, langsung dari output app.audit --------------------


def test_envelope_dari_audit_append_event_tervalidasi():
    """Cross-check: apa yang benar-benar ditulis app.audit MUST lolos skema ini."""
    e = audit.append_event(
        "deal-1", "CRITERION_DECISION", "client", 1, {"decision": ACCEPTED}
    )
    envelope = schemas.AuditEventEnvelope.model_validate(e)
    assert envelope.seq == 1
    assert envelope.type == "CRITERION_DECISION"


def test_envelope_tipe_tidak_dikenal_ditolak():
    with pytest.raises(ValidationError):
        schemas.AuditEventEnvelope.model_validate(
            {
                "event_id": "evt_x",
                "seq": 1,
                "type": "NOT_A_TYPE",
                "actor": "system",
                "baseline_version": 0,
                "created_at": "2026-08-25T00:00:00Z",
                "payload": {},
            }
        )
