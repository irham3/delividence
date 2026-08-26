"""Test endpoint Guardrail — 01-PRD §5 langkah 7, 02-ARCHITECTURE §4.5.

09-DOMAIN-RULES §8: hanya freelancer yang berwenang memutuskan klasifikasi
scope -- endpoint classify di sini tidak mengecek actor (belum ada auth di
codebase ini sama sekali, konsisten dengan endpoint lain), tapi audit event
selalu menulis actor "freelancer" untuk keputusan ini.
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
    token = api.post("/runs/%s/client-links" % run_id).json()["token"]
    api.post("/client/%s/answers" % token, json={"answers": _READY_ANSWERS})
    current_hash = api.get("/client/%s" % token).json()["payload_hash"]
    api.post("/client/%s/confirm" % token, json={"payload_hash": current_hash})
    return run_id


def test_submit_request_ditolak_tanpa_baseline_aktif(published):
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    r = api.post("/runs/%s/requests" % run_id, json={"raw_text": "Bisa tambah fitur X?"})
    assert r.status_code == 409


def test_submit_request_sukses_dan_menulis_audit_event(published):
    run_id = _run_with_active_baseline(published)
    r = api.post(
        "/runs/%s/requests" % run_id,
        json={"raw_text": "Bisa export 3 visual TikTok?", "submitted_by": "client"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["raw_text"] == "Bisa export 3 visual TikTok?"
    assert body["confirmed_classification"] is None

    events = [e["type"] for e in audit.list_events(run_id)]
    assert "REQUEST_SUBMITTED" in events


def test_submit_request_menyimpan_usulan_guardrail_dan_menulis_audit_event(published, monkeypatch):
    """propose_scope_classification di-stub autouse (conftest) supaya test
    lain tidak memanggil Gemini -- di sini di-override sekali untuk
    memverifikasi hasilnya benar-benar tersambung ke record + audit trail,
    tanpa memanggil Gemini sungguhan sama sekali."""
    import app.api as api_module

    async def _fake_proposal(raw_text, text_by_ref):
        return {
            "classification": "IN_SCOPE",
            "citations": [{"ref": "mobile-breakpoints", "quote": "Renders at 375px."}],
        }

    monkeypatch.setattr(api_module, "propose_scope_classification", _fake_proposal)

    run_id = _run_with_active_baseline(published)
    r = api.post(
        "/runs/%s/requests" % run_id, json={"raw_text": "Perlu breakpoint mobile juga?"}
    )
    assert r.status_code == 201
    body = r.json()
    assert body["proposed_classification"] == "IN_SCOPE"
    assert body["proposed_citations"] == [{"ref": "mobile-breakpoints", "quote": "Renders at 375px."}]
    # Freelancer belum mengonfirmasi apa pun -- usulan model tidak boleh
    # otomatis dianggap keputusan final (09-DOMAIN-RULES §8).
    assert body["confirmed_classification"] is None

    events = [e["type"] for e in audit.list_events(run_id)]
    assert "SCOPE_ANALYSIS_PROPOSED" in events


def test_submit_request_kegagalan_guardrail_agent_tidak_menggagalkan_pencatatan(published, monkeypatch):
    import app.api as api_module

    async def _boom(raw_text, text_by_ref):
        raise RuntimeError("Gemini gagal")

    monkeypatch.setattr(api_module, "propose_scope_classification", _boom)

    run_id = _run_with_active_baseline(published)
    r = api.post("/runs/%s/requests" % run_id, json={"raw_text": "x"})

    assert r.status_code == 201
    body = r.json()
    assert body["proposed_classification"] is None

    events = [e["type"] for e in audit.list_events(run_id)]
    assert "SCOPE_ANALYSIS_PROPOSED" not in events


def test_list_requests(published):
    run_id = _run_with_active_baseline(published)
    api.post("/runs/%s/requests" % run_id, json={"raw_text": "a"})
    api.post("/runs/%s/requests" % run_id, json={"raw_text": "b"})
    items = api.get("/runs/%s/requests" % run_id).json()
    assert len(items) == 2


def test_classify_dengan_kutipan_valid_in_scope(published):
    run_id = _run_with_active_baseline(published)
    request_id = api.post(
        "/runs/%s/requests" % run_id, json={"raw_text": "Perlu breakpoint mobile juga?"}
    ).json()["request_id"]

    r = api.post(
        "/runs/%s/requests/%s/classify" % (run_id, request_id),
        json={
            "classification": "IN_SCOPE",
            "citations": [{"ref": "mobile-breakpoints", "quote": "Renders at 375px"}],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["confirmed_classification"] == "IN_SCOPE"
    assert len(body["citations"]) == 1

    events = [e["type"] for e in audit.list_events(run_id)]
    assert "SCOPE_CLASSIFICATION_DECIDED" in events


def test_classify_in_scope_tanpa_kutipan_valid_turun_ambiguous(published):
    run_id = _run_with_active_baseline(published)
    request_id = api.post(
        "/runs/%s/requests" % run_id, json={"raw_text": "Klaim scope tanpa dasar"}
    ).json()["request_id"]

    r = api.post(
        "/runs/%s/requests/%s/classify" % (run_id, request_id),
        json={"classification": "IN_SCOPE", "citations": [{"ref": "mobile-breakpoints", "quote": "karangan"}]},
    )
    assert r.status_code == 200
    assert r.json()["confirmed_classification"] == "AMBIGUOUS"


def test_classify_request_tidak_dikenal_404(published):
    run_id = _run_with_active_baseline(published)
    r = api.post(
        "/runs/%s/requests/req_tidak-ada/classify" % run_id,
        json={"classification": "AMBIGUOUS", "citations": []},
    )
    assert r.status_code == 404


def test_classify_tanpa_baseline_aktif_409(published):
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    r = api.post(
        "/runs/%s/requests/req_tidak-ada/classify" % run_id,
        json={"classification": "AMBIGUOUS", "citations": []},
    )
    assert r.status_code == 409


def test_classification_tidak_dikenal_422(published):
    run_id = _run_with_active_baseline(published)
    request_id = api.post("/runs/%s/requests" % run_id, json={"raw_text": "x"}).json()["request_id"]
    r = api.post(
        "/runs/%s/requests/%s/classify" % (run_id, request_id),
        json={"classification": "MAYBE", "citations": []},
    )
    assert r.status_code == 422


def test_citable_refs_meliputi_criterion_dan_out_of_scope(published):
    """UI Guardrail (GuardrailPanel) menampilkan ini sebagai hint ref+teks
    sebelum freelancer mengisi citation -- harus mencakup SEMUA yang
    divalidasi `classify()`, bukan cuma criterion_key."""
    run_id = _run_with_active_baseline(published)
    refs = api.get("/runs/%s/citable-refs" % run_id).json()
    assert refs["mobile-breakpoints"] == "Renders at 375px."
    assert refs["out_of_scope[0]"] == "No paid ads."
    assert refs["deliverables[0]"] == "Landing page"


def test_citable_refs_tanpa_baseline_aktif_409(published):
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    assert api.get("/runs/%s/citable-refs" % run_id).status_code == 409
