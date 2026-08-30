from fastapi.testclient import TestClient
from datetime import datetime, timezone

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


def test_session_cookie_hanya_dibuat_dari_login_baru(monkeypatch):
    api_app.dependency_overrides.pop(auth.require_owner, None)
    now = int(datetime.now(timezone.utc).timestamp())

    class FakeFirebaseAuth:
        @staticmethod
        def verify_id_token(token, app):
            assert token == "fresh-id-token"
            return {"uid": "owner-a", "auth_time": now}

        @staticmethod
        def create_session_cookie(token, expires_in, app):
            assert token == "fresh-id-token"
            assert int(expires_in.total_seconds()) > 0
            return "signed-session-cookie"

    monkeypatch.setattr(auth, "_app", lambda: object())
    monkeypatch.setattr(auth, "_firebase_auth_module", lambda: FakeFirebaseAuth)

    response = api.post(
        "/auth/session", headers={"Authorization": "Bearer fresh-id-token"}
    )
    assert response.status_code == 200
    assert response.json()["session_cookie"] == "signed-session-cookie"


def test_session_cookie_menolak_token_dengan_auth_time_lama(monkeypatch):
    api_app.dependency_overrides.pop(auth.require_owner, None)
    old = int(datetime.now(timezone.utc).timestamp()) - 600

    class FakeFirebaseAuth:
        @staticmethod
        def verify_id_token(token, app):
            return {"uid": "owner-a", "auth_time": old}

    monkeypatch.setattr(auth, "_app", lambda: object())
    monkeypatch.setattr(auth, "_firebase_auth_module", lambda: FakeFirebaseAuth)

    response = api.post(
        "/auth/session", headers={"Authorization": "Bearer stale-id-token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "A recent sign-in is required"
