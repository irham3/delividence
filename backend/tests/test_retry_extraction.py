"""Test POST /runs/{run_id}/retry-extraction -- coba ulang ekstraksi Gemini
setelah kegagalan transient. Gap yang dicatat di CATATAN-LANJUTAN.md:
`claim_job` mengklaim round SEBELUM ekstraksi dicoba, jadi redelivery
Pub/Sub tidak pernah mengulang round yang sama -- endpoint ini memberi
freelancer jalan eksplisit lewat round baru.
"""

import base64
import json

from fastapi.testclient import TestClient

from app import store
from app.api import app as api_app
from app.worker import app as worker_app

api = TestClient(api_app)
worker = TestClient(worker_app)


def _envelope(run_id, round_no):
    payload = {"run_id": run_id, "round": round_no}
    data = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
    return {"message": {"data": data, "messageId": "m-%s-%s" % (run_id, round_no)}, "subscription": "s"}

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


def test_retry_menaikkan_round_dan_republish(published):
    """Urutan realistis: freelancer baru mencoba retry SETELAH melihat round
    1 selesai diproses (gagal) -- di situlah `run["round"]` benar-benar
    menjadi 1 (worker yang menulisnya, bukan `POST /runs`)."""
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    worker.post("/pubsub/push", json=_envelope(run_id, 1))

    r = api.post("/runs/%s/retry-extraction" % run_id)
    assert r.status_code == 202
    body = r.json()
    assert body["round"] == 2
    assert body["status"] == "queued"
    assert published[-1] == {"run_id": run_id, "round": 2}

    run = store.get_run(run_id)
    assert run["status"] == "queued"


def test_round_baru_bisa_diklaim_walau_round_lama_sudah_diklaim(published):
    """Inti dari fix ini: klaim round 1 (oleh worker yang memproses ekstraksi
    gagal) tidak menghalangi round 2 diklaim ulang -- itulah yang membuat
    redelivery Pub/Sub untuk round LAMA tetap di-drop sebagai duplikat
    (perilaku asli, sengaja dipertahankan) sementara retry lewat round BARU
    tetap bisa diproses dari awal."""
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    worker.post("/pubsub/push", json=_envelope(run_id, 1))
    assert store.claim_job(run_id, 1) is False  # round lama tetap terkunci, seperti semula

    api.post("/runs/%s/retry-extraction" % run_id)
    assert store.claim_job(run_id, 2) is True


def test_retry_ditolak_kalau_sudah_ada_baseline_409(published):
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    clar_token = api.post("/runs/%s/client-links" % run_id).json()["token"]
    api.post("/client/%s/answers" % clar_token, json={"answers": _READY_ANSWERS})
    current_hash = api.get("/client/%s" % clar_token).json()["payload_hash"]
    api.post("/client/%s/confirm" % clar_token, json={"payload_hash": current_hash})

    r = api.post("/runs/%s/retry-extraction" % run_id)
    assert r.status_code == 409


def test_retry_run_tidak_dikenal_404():
    assert api.post("/runs/tidak-ada/retry-extraction").status_code == 404
