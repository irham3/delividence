"""Test "propose change" -> baseline v2 -- 01-PRD §5 langkah 8,
09-DOMAIN-RULES §2.6 A-7/A-8 (naik versi tidak sendirinya mengubah status
criterion; criterion tak berubah mempertahankan introduced_in_version).
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


def _run_with_active_baseline(published):
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    clar_token = api.post("/runs/%s/client-links" % run_id).json()["token"]
    api.post("/client/%s/answers" % clar_token, json={"answers": _READY_ANSWERS})
    current_hash = api.get("/client/%s" % clar_token).json()["payload_hash"]
    api.post("/client/%s/confirm" % clar_token, json={"payload_hash": current_hash})
    return run_id


def test_propose_change_tanpa_baseline_aktif_409(published):
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    r = api.post(
        "/runs/%s/change-proposal" % run_id,
        json={"answers": [{"field": "out_of_scope", "value": []}]},
    )
    assert r.status_code == 409


def test_propose_change_menulis_ledger_dan_audit_event(published):
    run_id = _run_with_active_baseline(published)

    r = api.post(
        "/runs/%s/change-proposal" % run_id,
        json={
            "answers": [
                {
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
                            "text": "Hero section includes an autoplaying video.",
                        },
                    ],
                }
            ]
        },
    )
    assert r.status_code == 200
    values = [c["criterion_key"] for c in r.json()["ledger"]["acceptance_criteria"]["value"]]
    assert values == ["mobile-breakpoints", "hero-video"]
    assert r.json()["ledger"]["acceptance_criteria"]["state"] == "FREELANCER_POLICY"

    events = [e["type"] for e in audit.list_events(run_id)]
    assert events[-1] == "CHANGE_PROPOSED"


def test_v2_criterion_lama_pertahankan_introduced_in_version_dan_acceptance(published):
    run_id = _run_with_active_baseline(published)
    review_token = api.post(
        "/runs/%s/client-links" % run_id, json={"purpose": "DELIVERY_REVIEW"}
    ).json()["token"]
    api.post(
        "/client/%s/review" % review_token,
        json={"decisions": [{"criterion_key": "mobile-breakpoints", "decision": "ACCEPTED"}]},
    )

    api.post(
        "/runs/%s/change-proposal" % run_id,
        json={
            "answers": [
                {
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
                            "text": "Hero section includes an autoplaying video.",
                        },
                    ],
                }
            ]
        },
    )

    clar_token_2 = api.post("/runs/%s/client-links" % run_id).json()["token"]
    current_hash = api.get("/client/%s" % clar_token_2).json()["payload_hash"]
    r = api.post("/client/%s/confirm" % clar_token_2, json={"payload_hash": current_hash})
    assert r.status_code == 200
    assert r.json()["version"] == 2

    baseline_v2 = baselines.get(run_id, 2)
    criteria = baseline_v2["canonical_payload"]["criteria"]
    assert criteria["mobile-breakpoints"]["introduced_in_version"] == 1
    assert criteria["hero-video"]["introduced_in_version"] == 2

    run = api.get("/runs/%s" % run_id).json()
    assert run["active_baseline_version"] == 2

    review_token_2 = api.post(
        "/runs/%s/client-links" % run_id, json={"purpose": "DELIVERY_REVIEW"}
    ).json()["token"]
    view = api.get("/client/%s/review" % review_token_2).json()
    statuses = {c["criterion_key"]: c["status"] for c in view["criteria"]}
    assert statuses["mobile-breakpoints"] == "ACCEPTED"
    assert statuses["hero-video"] == "PENDING"


def test_v2_criterion_yang_teksnya_berubah_jadi_superseded(published):
    """05-SUBMISSION-CHECKLIST.md §3: "Baseline version baru mempertahankan
    acceptance untuk criterion dengan hash identik dan menandai criterion
    yang berubah sebagai SUPERSEDED" -- kebalikan dari test di atas (yang
    teksnya TIDAK berubah)."""
    run_id = _run_with_active_baseline(published)
    review_token = api.post(
        "/runs/%s/client-links" % run_id, json={"purpose": "DELIVERY_REVIEW"}
    ).json()["token"]
    api.post(
        "/client/%s/review" % review_token,
        json={"decisions": [{"criterion_key": "mobile-breakpoints", "decision": "ACCEPTED"}]},
    )

    api.post(
        "/runs/%s/change-proposal" % run_id,
        json={
            "answers": [
                {
                    "field": "acceptance_criteria",
                    "value": [
                        {
                            "deliverable_id": "d1",
                            "criterion_key": "mobile-breakpoints",
                            "text": "Renders at 375px, 768px, and 1440px widths.",
                        }
                    ],
                }
            ]
        },
    )

    clar_token_2 = api.post("/runs/%s/client-links" % run_id).json()["token"]
    current_hash = api.get("/client/%s" % clar_token_2).json()["payload_hash"]
    api.post("/client/%s/confirm" % clar_token_2, json={"payload_hash": current_hash})

    baseline_v2 = baselines.get(run_id, 2)
    assert baseline_v2["canonical_payload"]["criteria"]["mobile-breakpoints"]["introduced_in_version"] == 2

    review_token_2 = api.post(
        "/runs/%s/client-links" % run_id, json={"purpose": "DELIVERY_REVIEW"}
    ).json()["token"]
    view = api.get("/client/%s/review" % review_token_2).json()
    assert view["criteria"][0]["status"] == "SUPERSEDED"
