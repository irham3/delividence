"""Read-model endpoints used by the non-workspace owner pages.

The pages must read the same owner-isolated facts as the main workspace; they
cannot silently infer a record from browser state or expose another owner’s
run just because it exists in the store.
"""

from fastapi.testclient import TestClient

from app import store
from app.api import app as api_app

api = TestClient(api_app)


def test_run_index_is_owner_scoped_and_activity_is_per_run(published):
    mine = api.post("/runs", json={"brief": "My client material."}).json()["run_id"]
    store.create_run("foreign-run", "another-owner", "Private material.", "en")

    listing = api.get("/runs")
    assert listing.status_code == 200
    assert [item["run_id"] for item in listing.json()["items"]] == [mine]

    activity = api.get(f"/runs/{mine}/activity")
    assert activity.status_code == 200
    assert [event["type"] for event in activity.json()["items"]] == [
        "DEAL_CREATED",
        "ARTIFACT_ADDED",
    ]


def test_active_baseline_read_model_returns_confirmed_version(published):
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    token = api.post(f"/runs/{run_id}/client-links").json()["token"]
    answers = [
        {"field": "deliverables", "value": [{"id": "d1", "title": "Landing page"}]},
        {"field": "acceptance_criteria", "value": [{"deliverable_id": "d1", "criterion_key": "mobile", "text": "Renders at 375px."}]},
        {"field": "out_of_scope", "value": ["No paid ads."]},
        {"field": "timeline.final_deadline", "value": "2026-08-31"},
        {"field": "revision_policy.rounds_total", "value": 2},
    ]
    api.post(f"/client/{token}/answers", json={"answers": answers})
    payload_hash = api.get(f"/client/{token}").json()["payload_hash"]
    assert api.post(f"/client/{token}/confirm", json={"payload_hash": payload_hash}).status_code == 200

    response = api.get(f"/runs/{run_id}/baseline")
    assert response.status_code == 200
    body = response.json()
    assert body["active_version"] == 1
    assert body["baseline"]["canonical_payload"]["criteria"]["mobile"]["text"] == "Renders at 375px."
