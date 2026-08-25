"""Test evidence + delivery review — 01-PRD §5 langkah 9-10, 09-DOMAIN-RULES
Modul A (effective_status/can_record_decision lewat endpoint sungguhan).
"""

from fastapi.testclient import TestClient

from app import audit
from app.api import app as api_app

api = TestClient(api_app)

_READY_ANSWERS = [
    {"field": "deliverables", "value": [{"id": "d1", "title": "Landing page"}]},
    {
        "field": "acceptance_criteria",
        "value": [
            {"deliverable_id": "d1", "criterion_key": "mobile-breakpoints", "text": "Renders at 375px."}
        ],
    },
    {"field": "out_of_scope", "value": ["No paid ads."]},
    {"field": "timeline.final_deadline", "value": "2026-08-31"},
    {"field": "revision_policy.rounds_total", "value": 2},
]


def _run_with_active_baseline(published):
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    clar_token = api.post("/runs/%s/client-links" % run_id).json()["token"]
    api.post("/client/%s/answers" % clar_token, json={"answers": _READY_ANSWERS})
    current_hash = api.get("/client/%s" % clar_token).json()["payload_hash"]
    api.post("/client/%s/confirm" % clar_token, json={"payload_hash": current_hash})
    return run_id


def _review_link(run_id):
    return api.post("/runs/%s/client-links" % run_id, json={"purpose": "DELIVERY_REVIEW"}).json()["token"]


def test_evidence_ditolak_tanpa_baseline_aktif(published):
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    r = api.post(
        "/runs/%s/evidence" % run_id,
        json={"criterion_key": "mobile-breakpoints", "type": "url", "uri": "https://example.com"},
    )
    assert r.status_code == 409


def test_evidence_criterion_key_tidak_dikenal_404(published):
    run_id = _run_with_active_baseline(published)
    r = api.post(
        "/runs/%s/evidence" % run_id,
        json={"criterion_key": "tidak-ada", "type": "url", "uri": "https://example.com"},
    )
    assert r.status_code == 404


def test_tambah_evidence_sukses_dan_menulis_audit_event(published):
    run_id = _run_with_active_baseline(published)
    r = api.post(
        "/runs/%s/evidence" % run_id,
        json={"criterion_key": "mobile-breakpoints", "type": "url", "uri": "https://example.com/shot.png"},
    )
    assert r.status_code == 201
    assert r.json()["criterion_key"] == "mobile-breakpoints"

    events = [e["type"] for e in audit.list_events(run_id)]
    assert "EVIDENCE_ADDED" in events


def test_delivery_review_link_purpose_benar(published):
    run_id = _run_with_active_baseline(published)
    r = api.post("/runs/%s/client-links" % run_id, json={"purpose": "DELIVERY_REVIEW"})
    assert r.status_code == 201
    assert r.json()["purpose"] == "DELIVERY_REVIEW"


def test_view_review_menampilkan_criterion_pending_dan_evidence(published):
    run_id = _run_with_active_baseline(published)
    api.post(
        "/runs/%s/evidence" % run_id,
        json={"criterion_key": "mobile-breakpoints", "type": "text", "uri": "Tested manually, passes."},
    )
    token = _review_link(run_id)

    r = api.get("/client/%s/review" % token)
    assert r.status_code == 200
    body = r.json()
    assert body["baseline_version"] == 1
    crit = body["criteria"][0]
    assert crit["criterion_key"] == "mobile-breakpoints"
    assert crit["status"] == "PENDING"
    assert len(crit["evidence"]) == 1


def test_clarification_token_tidak_bisa_dipakai_untuk_review(published):
    run_id = _run_with_active_baseline(published)
    clar_token = api.post("/runs/%s/client-links" % run_id).json()["token"]
    assert api.get("/client/%s/review" % clar_token).status_code == 403


def test_submit_review_accepted_mengubah_status_dan_menulis_dua_jenis_event(published):
    run_id = _run_with_active_baseline(published)
    token = _review_link(run_id)

    r = api.post(
        "/client/%s/review" % token,
        json={"decisions": [{"criterion_key": "mobile-breakpoints", "decision": "ACCEPTED"}]},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["review_session_id"]
    assert body["decisions"][0]["decision"] == "ACCEPTED"

    events = [e["type"] for e in audit.list_events(run_id)]
    assert events[-2:] == ["REVIEW_SESSION_OPENED", "CRITERION_DECISION"]

    # Link DELIVERY_REVIEW sengaja tidak ditandai completed setelah submit --
    # klien boleh mengirim ronde review lagi untuk criterion lain nantinya.
    view = api.get("/client/%s/review" % token).json()
    assert view["criteria"][0]["status"] == "ACCEPTED"


def test_submit_review_changes_requested_tanpa_reason_ditolak(published):
    run_id = _run_with_active_baseline(published)
    token = _review_link(run_id)

    r = api.post(
        "/client/%s/review" % token,
        json={"decisions": [{"criterion_key": "mobile-breakpoints", "decision": "CHANGES_REQUESTED"}]},
    )
    assert r.status_code == 422


def test_submit_review_changes_requested_dengan_reason_sukses(published):
    run_id = _run_with_active_baseline(published)
    token = _review_link(run_id)

    r = api.post(
        "/client/%s/review" % token,
        json={
            "decisions": [
                {
                    "criterion_key": "mobile-breakpoints",
                    "decision": "CHANGES_REQUESTED",
                    "reason": "Breaks at 375px, overlapping text.",
                }
            ]
        },
    )
    assert r.status_code == 200


def test_criterion_key_tidak_dikenal_di_submit_review_404(published):
    run_id = _run_with_active_baseline(published)
    token = _review_link(run_id)

    r = api.post(
        "/client/%s/review" % token,
        json={"decisions": [{"criterion_key": "tidak-ada", "decision": "ACCEPTED"}]},
    )
    assert r.status_code == 404


def test_ubah_keputusan_atas_criterion_yang_sudah_accepted_ditolak_a9(published):
    """09-DOMAIN-RULES A-9: ACCEPTED final untuk criterion_key + text_hash;
    permintaan perubahan berikutnya MUST ditolak di sini (arahnya Guardrail,
    belum dibangun), bukan menimpa jadi CHANGES_REQUESTED baru."""
    run_id = _run_with_active_baseline(published)
    token = _review_link(run_id)

    api.post(
        "/client/%s/review" % token,
        json={"decisions": [{"criterion_key": "mobile-breakpoints", "decision": "ACCEPTED"}]},
    )
    r = api.post(
        "/client/%s/review" % token,
        json={
            "decisions": [
                {"criterion_key": "mobile-breakpoints", "decision": "CHANGES_REQUESTED", "reason": "x"}
            ]
        },
    )
    assert r.status_code == 409


def test_review_ditolak_kalau_belum_ada_baseline_aktif(published):
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    token = _review_link(run_id)
    assert api.get("/client/%s/review" % token).status_code == 409
