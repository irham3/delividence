"""Freelancer preference memory: reusable, but never client-owned truth."""

import base64
import json

from fastapi.testclient import TestClient

from app import store
from app.api import app as api_app
from app.worker import app as worker_app

api = TestClient(api_app)
worker = TestClient(worker_app)


def _envelope(run_id, round_no=1):
    raw = base64.b64encode(json.dumps({"run_id": run_id, "round": round_no}).encode()).decode()
    return {"message": {"data": raw, "messageId": "preference"}, "subscription": "test"}


def test_confirmed_preference_is_staged_on_next_deal_as_freelancer_policy(published):
    saved = api.post("/preferences", json={"revision_rounds": 2})
    assert saved.status_code == 200
    assert saved.json()["status"] == "CONFIRMED"

    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    assert worker.post("/pubsub/push", json=_envelope(run_id)).status_code == 204

    rounds = store.get_run(run_id)["ledger"]["revision_policy"]["rounds_total"]
    assert rounds["value"] == 2
    assert rounds["state"] == "FREELANCER_POLICY"
    assert rounds["source_artifact"] == "artifact:policy-1"


def test_client_statement_can_replace_staged_preference_but_not_auto_agree(published):
    api.post("/preferences", json={"revision_rounds": 2})
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    worker.post("/pubsub/push", json=_envelope(run_id))
    token = api.post(f"/runs/{run_id}/client-links").json()["token"]

    response = api.post(
        f"/client/{token}/answers",
        json={"answers": [{"field": "revision_policy.rounds_total", "value": 3}]},
    )
    assert response.status_code == 200
    rounds = response.json()["ledger"]["revision_policy"]["rounds_total"]
    assert rounds["value"] == 3
    assert rounds["state"] == "CLIENT_STATED"
