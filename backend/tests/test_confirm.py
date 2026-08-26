"""Test "Confirm project plan" -- POST /client/{token}/confirm.

01-PRD §5 langkah 5, 09-DOMAIN-RULES §7.3 (BASELINE_APPROVED lalu
BASELINE_ACTIVATED), 02-ARCHITECTURE §5 (precondition payload_hash, request
basi -> 409).
"""

from fastapi.testclient import TestClient

from app import audit, baselines
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


def _run_with_link(published):
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    token = api.post("/runs/%s/client-links" % run_id).json()["token"]
    return run_id, token


def _make_ready(token):
    return api.post("/client/%s/answers" % token, json={"answers": _READY_ANSWERS})


def test_confirm_sebelum_ready_ditolak_422(published):
    _run_id, token = _run_with_link(published)
    r = api.post("/client/%s/confirm" % token, json={"payload_hash": "sha256:apapun"})
    assert r.status_code == 422


def test_confirm_dengan_hash_basi_ditolak_409(published):
    _run_id, token = _run_with_link(published)
    _make_ready(token)

    r = api.post("/client/%s/confirm" % token, json={"payload_hash": "sha256:bukan-yang-sekarang"})
    assert r.status_code == 409


def test_confirm_sukses_menulis_baseline_v1_dan_dua_audit_event(published):
    run_id, token = _run_with_link(published)
    _make_ready(token)
    current_hash = api.get("/client/%s" % token).json()["payload_hash"]

    r = api.post("/client/%s/confirm" % token, json={"payload_hash": current_hash})
    assert r.status_code == 200
    body = r.json()
    assert body["version"] == 1
    assert body["payload_hash"] == current_hash

    baseline = baselines.get(run_id, 1)
    assert baseline["status"] == "ACTIVE"
    assert baseline["approved_by"] == "client"
    assert baseline["canonical_payload"]["criteria"]["mobile-breakpoints"]["text_hash"]

    events = [e["type"] for e in audit.list_events(run_id)]
    assert events[-2:] == ["BASELINE_APPROVED", "BASELINE_ACTIVATED"]


def test_link_selesai_setelah_confirm_tidak_bisa_dipakai_lagi(published):
    _run_id, token = _run_with_link(published)
    _make_ready(token)
    current_hash = api.get("/client/%s" % token).json()["payload_hash"]
    api.post("/client/%s/confirm" % token, json={"payload_hash": current_hash})

    assert api.get("/client/%s" % token).status_code == 403
    assert api.post(
        "/client/%s/answers" % token,
        json={"answers": [{"field": "out_of_scope", "value": []}]},
    ).status_code == 403


def test_active_baseline_version_tersimpan_di_run(published):
    run_id, token = _run_with_link(published)
    _make_ready(token)
    current_hash = api.get("/client/%s" % token).json()["payload_hash"]
    api.post("/client/%s/confirm" % token, json={"payload_hash": current_hash})

    run = api.get("/runs/%s" % run_id).json()
    assert run["active_baseline_version"] == 1
