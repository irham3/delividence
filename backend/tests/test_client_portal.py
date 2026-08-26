"""Test endpoint klien -- freelancer menerbitkan client link, klien membuka
dan menjawab (02-ARCHITECTURE §8, 01-PRD §5 langkah 4-5).
"""

from fastapi.testclient import TestClient

from app import audit, client_links
from app.api import app as api_app

api = TestClient(api_app)


def _new_run(published):
    return api.post("/runs", json={"brief": "Need an edit for our IG content."}).json()["run_id"]


def test_freelancer_menerbitkan_client_link(published):
    run_id = _new_run(published)
    r = api.post("/runs/%s/client-links" % run_id)
    assert r.status_code == 201
    body = r.json()
    assert body["purpose"] == "CLARIFICATION"
    assert len(body["token"]) >= 20


def test_menerbitkan_link_untuk_run_tidak_ada_404():
    assert api.post("/runs/tidak-ada/client-links").status_code == 404


def test_klien_membuka_link_valid(published):
    run_id = _new_run(published)
    token = api.post("/runs/%s/client-links" % run_id).json()["token"]

    r = api.get("/client/%s" % token)
    assert r.status_code == 200
    body = r.json()
    assert body["brief"] == "Need an edit for our IG content."
    assert body["ledger"] == {}
    assert body["readiness"]["ready"] is False


def test_klien_membuka_token_tidak_dikenal_403():
    assert api.get("/client/token-yang-tidak-pernah-diterbitkan").status_code == 403


def test_klien_membuka_link_yang_sudah_direvoke_403(published):
    run_id = _new_run(published)
    token = api.post("/runs/%s/client-links" % run_id).json()["token"]
    client_links.revoke(token)

    r = api.get("/client/%s" % token)
    assert r.status_code == 403
    assert "revoked" in r.json()["detail"]


def test_freelancer_revoke_lewat_endpoint_bikin_link_403(published):
    run_id = _new_run(published)
    token = api.post("/runs/%s/client-links" % run_id).json()["token"]

    r = api.post("/runs/%s/client-links/%s/revoke" % (run_id, token))
    assert r.status_code == 200
    assert r.json() == {"revoked": True}

    assert api.get("/client/%s" % token).status_code == 403


def test_revoke_token_tidak_dikenal_404(published):
    run_id = _new_run(published)
    r = api.post("/runs/%s/client-links/token-yang-tidak-pernah-diterbitkan/revoke" % run_id)
    assert r.status_code == 404


def test_revoke_token_milik_run_lain_404(published):
    run_a = _new_run(published)
    run_b = _new_run(published)
    token_a = api.post("/runs/%s/client-links" % run_a).json()["token"]

    r = api.post("/runs/%s/client-links/%s/revoke" % (run_b, token_a))
    assert r.status_code == 404
    assert api.get("/client/%s" % token_a).status_code == 200  # tetap valid, tidak ikut ke-revoke


def test_klien_menjawab_mengubah_ledger_dan_menulis_audit_event(published):
    run_id = _new_run(published)
    token = api.post("/runs/%s/client-links" % run_id).json()["token"]

    r = api.post(
        "/client/%s/answers" % token,
        json={"answers": [{"field": "timeline.final_deadline", "value": "2026-08-31"}]},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ledger"]["timeline"]["final_deadline"]["value"] == "2026-08-31"
    assert body["ledger"]["timeline"]["final_deadline"]["state"] == "CLIENT_STATED"

    events = audit.list_events(run_id)
    client_answered = [e for e in events if e["type"] == "CLIENT_ANSWERED"]
    assert len(client_answered) == 1
    assert client_answered[0]["payload"]["field"] == "timeline.final_deadline"
    assert client_answered[0]["actor_ref"] == client_links.actor_ref_for(token)


def test_link_tetap_valid_setelah_dipakai_menjawab_sekali(published):
    """Klien boleh mengirim beberapa ronde koreksi sebelum confirm -- link
    tidak otomatis selesai setelah satu jawaban (lihat test_confirm.py)."""
    run_id = _new_run(published)
    token = api.post("/runs/%s/client-links" % run_id).json()["token"]

    first = api.post(
        "/client/%s/answers" % token,
        json={"answers": [{"field": "out_of_scope", "value": ["No paid ads."]}]},
    )
    second = api.post(
        "/client/%s/answers" % token,
        json={"answers": [{"field": "timeline.final_deadline", "value": "2026-08-31"}]},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["ledger"]["out_of_scope"]["value"] == ["No paid ads."]
    assert second.json()["ledger"]["timeline"]["final_deadline"]["value"] == "2026-08-31"


def test_field_tidak_dikenal_ditolak_dan_tidak_menulis_apa_pun(published):
    run_id = _new_run(published)
    token = api.post("/runs/%s/client-links" % run_id).json()["token"]

    r = api.post(
        "/client/%s/answers" % token,
        json={"answers": [{"field": "field_yang_tidak_ada", "value": "x"}]},
    )
    assert r.status_code == 422

    assert audit.list_events(run_id)[-1]["type"] == "ARTIFACT_ADDED"
    assert api.get("/client/%s" % token).json()["ledger"] == {}


def test_menjawab_dengan_link_yang_direvoke_403(published):
    run_id = _new_run(published)
    token = api.post("/runs/%s/client-links" % run_id).json()["token"]
    client_links.revoke(token)

    r = api.post(
        "/client/%s/answers" % token,
        json={"answers": [{"field": "out_of_scope", "value": []}]},
    )
    assert r.status_code == 403
