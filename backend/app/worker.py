import base64
import json
import logging

from fastapi import FastAPI, Request, Response

from app import config, store

log = logging.getLogger("dealready.worker")

app = FastAPI(title="DealReady Worker")


@app.get("/health")
def health():
    return {"status": "ok", "role": "worker", "local": config.LOCAL}


def _decode(envelope):
    """Ambil payload dari envelope push Pub/Sub. None kalau tidak bisa dipakai."""
    try:
        raw = envelope["message"]["data"]
        msg = json.loads(base64.b64decode(raw).decode("utf-8"))
        run_id = msg["run_id"]
        round_no = int(msg["round"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None
    if not run_id or round_no < 1:
        return None
    return run_id, round_no


@app.post("/pubsub/push")
async def push(request: Request):
    envelope = await request.json()
    parsed = _decode(envelope)

    # Pesan rusak permanen: di-ack supaya tidak diulang selamanya. Yang layak
    # diulang adalah kegagalan sementara, dan itu urusan retry + dead-letter.
    if parsed is None:
        log.warning("envelope tidak bisa didekode, di-drop: %s", envelope)
        return Response(status_code=204)

    run_id, round_no = parsed

    if not store.claim_job(run_id, round_no):
        log.info("pengiriman ganda untuk %s round %s, dilewati", run_id, round_no)
        return Response(status_code=204)

    run = store.get_run(run_id)
    if run is None:
        log.warning("run %s tidak ada, di-drop", run_id)
        return Response(status_code=204)

    store.update_run(run_id, status="processing", round=round_no)
    store.append_audit_step(
        run_id,
        "vertical_slice",
        "Pekerjaan diterima dari antrean dan diproses di luar request. "
        "Belum ada logika produk di tahap ini.",
    )
    store.update_run(run_id, status="done")
    return Response(status_code=204)
