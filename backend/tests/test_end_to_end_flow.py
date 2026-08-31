"""Satu journey integrasi lengkap, termasuk kedua batas AI.

Model diganti stub deterministik, tetapi wiring worker/API, persistence, domain
gates, client portal, versioning, evidence, review, dan proof memakai kode
produksi yang sama. Kontrak tool AI sendiri tetap diuji di test_agent.py.
"""

import base64
import json

from fastapi.testclient import TestClient

from app.api import app as api_app
from app.domain.ledger import apply_client_answer
from app.worker import app as worker_app

api = TestClient(api_app)
worker = TestClient(worker_app)


def _envelope(payload):
    data = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
    return {"message": {"data": data, "messageId": "journey-1"}}


def test_complete_owner_ai_client_delivery_change_journey(published, monkeypatch):
    from app import api as api_module
    from app import worker as worker_module

    async def extracted_ledger(run_id, brief):
        ledger = {}
        for field, value in [
            ("deliverables", [{"id": "d1", "title": "Landing page"}]),
            (
                "acceptance_criteria",
                [{
                    "deliverable_id": "d1",
                    "criterion_key": "mobile-breakpoints",
                    "text": "Renders at 375px.",
                }],
            ),
            ("out_of_scope", ["No paid ads."]),
            ("timeline.final_deadline", "2026-09-30"),
            ("revision_policy.rounds_total", 2),
        ]:
            apply_client_answer(ledger, field, value)
        return ledger

    async def guardrail_proposal(raw_text, text_by_ref):
        assert text_by_ref["mobile-breakpoints"] == "Renders at 375px."
        return {
            "classification": "CHANGE_REQUEST",
            "citations": [{"ref": "mobile-breakpoints", "quote": "Renders at 375px."}],
        }

    monkeypatch.setattr(worker_module, "run_extraction", extracted_ledger)
    monkeypatch.setattr(api_module, "propose_scope_classification", guardrail_proposal)

    created = api.post(
        "/runs", json={"brief": "Build a responsive landing page.", "output_language": "en"}
    )
    assert created.status_code == 202
    run_id = created.json()["run_id"]
    assert worker.post("/pubsub/push", json=_envelope({"run_id": run_id, "round": 1})).status_code == 204
    assert api.get(f"/runs/{run_id}").json()["status"] == "done"

    clarification = api.post(f"/runs/{run_id}/client-links").json()["token"]
    client_view = api.get(f"/client/{clarification}").json()
    assert client_view["readiness"]["ready"] is True
    baseline_v1 = api.post(
        f"/client/{clarification}/confirm",
        json={"payload_hash": client_view["payload_hash"]},
    )
    assert baseline_v1.status_code == 200
    assert baseline_v1.json()["version"] == 1

    evidence = api.post(
        f"/runs/{run_id}/evidence",
        json={
            "criterion_key": "mobile-breakpoints",
            "type": "url",
            "uri": "https://example.test/mobile-proof.png",
            "caption": "375px browser capture",
        },
    )
    assert evidence.status_code == 201

    review_link = api.post(
        f"/runs/{run_id}/client-links", json={"purpose": "DELIVERY_REVIEW"}
    ).json()["token"]
    review = api.post(
        f"/client/{review_link}/review",
        json={"decisions": [{"criterion_key": "mobile-breakpoints", "decision": "ACCEPTED"}]},
    )
    assert review.status_code == 200

    request_link = api.post(
        f"/runs/{run_id}/client-links", json={"purpose": "NEW_REQUEST"}
    ).json()["token"]
    request = api.post(
        f"/client/{request_link}/new-request",
        json={"raw_text": "Please add a hero video."},
    )
    assert request.status_code == 201
    assert request.json()["proposed_classification"] == "CHANGE_REQUEST"
    request_id = request.json()["request_id"]

    classification = api.post(
        f"/runs/{run_id}/requests/{request_id}/classify",
        json={
            "classification": "CHANGE_REQUEST",
            "citations": [{"ref": "mobile-breakpoints", "quote": "Renders at 375px."}],
        },
    )
    assert classification.status_code == 200
    assert classification.json()["confirmed_classification"] == "CHANGE_REQUEST"

    proposed = api.post(
        f"/runs/{run_id}/change-proposal",
        json={
            "answers": [{
                "field": "acceptance_criteria",
                "value": [
                    {
                        "deliverable_id": "d1",
                        "criterion_key": "mobile-breakpoints",
                        "text": "Renders at 375px.",
                    },
                    {
                        "deliverable_id": "d1",
                        "criterion_key": "hero-video",
                        "text": "Hero video autoplays muted.",
                    },
                ],
            }],
        },
    )
    assert proposed.status_code == 200

    clarification_v2 = api.post(f"/runs/{run_id}/client-links").json()["token"]
    v2_view = api.get(f"/client/{clarification_v2}").json()
    baseline_v2 = api.post(
        f"/client/{clarification_v2}/confirm",
        json={"payload_hash": v2_view["payload_hash"]},
    )
    assert baseline_v2.status_code == 200
    assert baseline_v2.json()["version"] == 2

    proof = api.get(f"/runs/{run_id}/proof").json()
    assert proof["baseline"]["version"] == 2
    criteria = {item["criterion_key"]: item for item in proof["criteria"]}
    assert criteria["mobile-breakpoints"]["agreement_source"]["status"] == "ACCEPTED"
    assert criteria["hero-video"]["agreement_source"]["status"] == "PENDING"
    assert len(criteria["mobile-breakpoints"]["evidence"]) == 1
