import base64
import json

from fastapi.testclient import TestClient

from app import store
from app.api import app as api_app
from app.worker import app as worker_app

api = TestClient(api_app)
worker = TestClient(worker_app)


def envelope(payload):
    data = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
    return {"message": {"data": data, "messageId": "m-1"}, "subscription": "s"}


def test_health_membedakan_role():
    assert api.get("/health").json()["role"] == "api"
    assert worker.get("/health").json()["role"] == "worker"


def test_create_run_mengantre_dan_belum_diproses(published):
    r = api.post("/runs", json={"brief": "Need an edit for our IG content."})
    assert r.status_code == 202
    run_id = r.json()["run_id"]

    run = store.get_run(run_id)
    assert run["status"] == "queued"
    assert run["audit_trail"] == []
    assert published == [{"run_id": run_id, "round": 1}]


def test_output_language_default_english(published):
    r = api.post("/runs", json={"brief": "halo, butuh edit video"})
    assert store.get_run(r.json()["run_id"])["output_language"] == "en"


def test_output_language_tidak_didukung_ditolak(published):
    r = api.post("/runs", json={"brief": "x", "output_language": "fr"})
    assert r.status_code == 422


def test_worker_memproses_sampai_selesai(published):
    run_id = api.post("/runs", json={"brief": "brief apa adanya"}).json()["run_id"]

    assert worker.post("/pubsub/push", json=envelope({"run_id": run_id, "round": 1})).status_code == 204

    run = store.get_run(run_id)
    assert run["status"] == "done"
    assert run["round"] == 1
    assert len(run["audit_trail"]) == 1


def test_pengiriman_ganda_hanya_diproses_sekali(published):
    """Pub/Sub menjamin at-least-once, jadi pesan yang sama pasti datang dua kali."""
    run_id = api.post("/runs", json={"brief": "brief apa adanya"}).json()["run_id"]
    env = envelope({"run_id": run_id, "round": 1})

    assert worker.post("/pubsub/push", json=env).status_code == 204
    assert worker.post("/pubsub/push", json=env).status_code == 204

    assert len(store.get_run(run_id)["audit_trail"]) == 1


def test_putaran_berikutnya_tidak_ikut_tertekan(published):
    """Kunci klaim menyertakan round, supaya jawaban klien tetap bisa diproses."""
    run_id = api.post("/runs", json={"brief": "brief apa adanya"}).json()["run_id"]

    worker.post("/pubsub/push", json=envelope({"run_id": run_id, "round": 1}))
    worker.post("/pubsub/push", json=envelope({"run_id": run_id, "round": 2}))

    run = store.get_run(run_id)
    assert run["round"] == 2
    assert len(run["audit_trail"]) == 2


def test_envelope_rusak_di_ack_bukan_diulang_selamanya():
    r = worker.post("/pubsub/push", json={"message": {"data": "bukan-base64-json"}})
    assert r.status_code == 204


def test_run_tidak_dikenal_di_drop():
    r = worker.post("/pubsub/push", json=envelope({"run_id": "tidak-ada", "round": 1}))
    assert r.status_code == 204


def test_get_run_tidak_ada_404():
    assert api.get("/runs/tidak-ada").status_code == 404
