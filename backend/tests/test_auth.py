from fastapi.testclient import TestClient

from app import auth
from app.api import app as api_app

api = TestClient(api_app)


def test_create_run_tanpa_token_401():
    api_app.dependency_overrides.pop(auth.require_owner, None)
    r = api.post("/runs", json={"brief": "x"})
    assert r.status_code == 401


def test_get_run_tanpa_token_401():
    api_app.dependency_overrides.pop(auth.require_owner, None)
    r = api.get("/runs/tidak-ada")
    assert r.status_code == 401


def test_header_bukan_bearer_401():
    api_app.dependency_overrides.pop(auth.require_owner, None)
    r = api.post("/runs", json={"brief": "x"}, headers={"Authorization": "Basic abc"})
    assert r.status_code == 401


def test_owner_lain_tidak_bisa_baca_run(published):
    """02 §8: owner A tidak dapat membaca deal owner B -- 404, bukan 403,
    supaya keberadaan deal tidak bocor ke owner yang salah."""
    api_app.dependency_overrides[auth.require_owner] = lambda: "owner-a"
    run_id = api.post("/runs", json={"brief": "punya owner-a"}).json()["run_id"]

    api_app.dependency_overrides[auth.require_owner] = lambda: "owner-b"
    assert api.get(f"/runs/{run_id}").status_code == 404
    assert api.post(f"/runs/{run_id}/client-links", json={"purpose": "CLARIFICATION"}).status_code == 404
    assert (
        api.post(
            f"/runs/{run_id}/evidence",
            json={"criterion_key": "k", "type": "url", "uri": "https://x.test"},
        ).status_code
        == 404
    )
    assert api.get(f"/runs/{run_id}/proof").status_code == 404
    assert api.post(f"/runs/{run_id}/requests", json={"raw_text": "x"}).status_code == 404
    assert api.get(f"/runs/{run_id}/requests").status_code == 404


def test_owner_sendiri_tetap_bisa_baca_run(published):
    api_app.dependency_overrides[auth.require_owner] = lambda: "owner-a"
    run_id = api.post("/runs", json={"brief": "punya owner-a"}).json()["run_id"]

    assert api.get(f"/runs/{run_id}").status_code == 200
