"""Test GET /runs/{run_id}/proof — 01-PRD §5 langkah 12."""

from fastapi.testclient import TestClient

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
    token = api.post("/runs/%s/client-links" % run_id).json()["token"]
    api.post("/client/%s/answers" % token, json={"answers": _READY_ANSWERS})
    current_hash = api.get("/client/%s" % token).json()["payload_hash"]
    api.post("/client/%s/confirm" % token, json={"payload_hash": current_hash})
    return run_id


def test_proof_ditolak_tanpa_baseline_aktif(published):
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    assert api.get("/runs/%s/proof" % run_id).status_code == 409


def test_proof_run_tidak_ada_404():
    assert api.get("/runs/tidak-ada/proof").status_code == 404


def test_proof_format_tidak_dikenal_422(published):
    run_id = _run_with_active_baseline(published)
    assert api.get("/runs/%s/proof?format=pdf" % run_id).status_code == 422


def test_proof_json_default_memuat_baseline_dan_criteria(published):
    run_id = _run_with_active_baseline(published)
    r = api.get("/runs/%s/proof" % run_id)
    assert r.status_code == 200
    body = r.json()
    assert body["deal_id"] == run_id
    assert body["baseline"]["version"] == 1
    assert body["criteria"][0]["criterion_key"] == "mobile-breakpoints"
    assert body["criteria"][0]["agreement_source"]["status"] == "PENDING"
    assert body["criteria"][0]["client_decision"] is None


def test_proof_json_mencerminkan_evidence_dan_keputusan_terbaru(published):
    run_id = _run_with_active_baseline(published)
    api.post(
        "/runs/%s/evidence" % run_id,
        json={"criterion_key": "mobile-breakpoints", "type": "url", "uri": "https://example.com/shot.png"},
    )
    review_token = api.post(
        "/runs/%s/client-links" % run_id, json={"purpose": "DELIVERY_REVIEW"}
    ).json()["token"]
    api.post(
        "/client/%s/review" % review_token,
        json={"decisions": [{"criterion_key": "mobile-breakpoints", "decision": "ACCEPTED"}]},
    )

    body = api.get("/runs/%s/proof" % run_id).json()
    crit = body["criteria"][0]
    assert crit["agreement_source"]["status"] == "ACCEPTED"
    assert crit["evidence"][0]["uri"] == "https://example.com/shot.png"
    assert crit["client_decision"]["decision"] == "ACCEPTED"
    assert crit["client_decision"]["actor"] == "client"


def test_proof_markdown(published):
    run_id = _run_with_active_baseline(published)
    r = api.get("/runs/%s/proof?format=md" % run_id)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/markdown")
    assert "# Acceptance Record" in r.text
    assert "mobile-breakpoints" in r.text
