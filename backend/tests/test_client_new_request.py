"""Test portal "New Request" untuk klien -- 01-PRD §5 langkah 7: "klien
dapat mengirim request baru melalui portal yang sama". Purpose `NEW_REQUEST`
sudah lama dicadangkan di app.domain.client_link.PURPOSES tapi baru
tersambung ke endpoint di sini.
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


def _new_request_token(run_id):
    return api.post(
        "/runs/%s/client-links" % run_id, json={"purpose": "NEW_REQUEST"}
    ).json()["token"]


def test_view_new_request_link_tanpa_baseline_409(published):
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    token = _new_request_token(run_id)
    # view sendiri tidak butuh baseline (link-nya sah), tapi ini menegaskan
    # link view tidak ikut 409 -- cuma submit yang butuh baseline aktif.
    r = api.get("/client/%s/new-request" % token)
    assert r.status_code == 200
    assert r.json()["brief"] == "Need a landing page."


def test_klien_submit_request_baru_menulis_audit_event_actor_client(published):
    run_id = _run_with_active_baseline(published)
    token = _new_request_token(run_id)

    r = api.post("/client/%s/new-request" % token, json={"raw_text": "Bisa tambah 3 visual TikTok?"})
    assert r.status_code == 201
    body = r.json()
    assert body["raw_text"] == "Bisa tambah 3 visual TikTok?"
    assert body["submitted_by"] == "client"

    events = [e for e in audit.list_events(run_id) if e["type"] == "REQUEST_SUBMITTED"]
    assert len(events) == 1
    assert events[0]["actor"] == "client"
    assert events[0]["actor_ref"].startswith("client_link:")


def test_klien_bisa_submit_lebih_dari_sekali_lewat_link_yang_sama(published):
    run_id = _run_with_active_baseline(published)
    token = _new_request_token(run_id)

    api.post("/client/%s/new-request" % token, json={"raw_text": "Request pertama"})
    r2 = api.post("/client/%s/new-request" % token, json={"raw_text": "Request kedua"})
    assert r2.status_code == 201

    items = api.get("/runs/%s/requests" % run_id).json()
    assert len(items) == 2


def test_submit_tanpa_baseline_aktif_409(published):
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    token = _new_request_token(run_id)
    r = api.post("/client/%s/new-request" % token, json={"raw_text": "x"})
    assert r.status_code == 409


def test_new_request_link_tidak_bisa_dipakai_untuk_purpose_lain(published):
    """Token NEW_REQUEST ditolak di endpoint CLARIFICATION, dan sebaliknya --
    purpose match, bukan cuma validitas token, yang menentukan."""
    run_id = _run_with_active_baseline(published)
    new_request_token = _new_request_token(run_id)
    assert api.get("/client/%s" % new_request_token).status_code == 403

    clar_token = api.post("/runs/%s/client-links" % run_id).json()["token"]
    assert api.get("/client/%s/new-request" % clar_token).status_code == 403
