import base64
import json
import logging

from fastapi import FastAPI, Request, Response

from app import agent, audit, config, store

log = logging.getLogger("delividence.worker")

app = FastAPI(title="Delividence Worker")


def _merge_staged_preference(run, ledger_draft):
    """Tambahkan policy owner hanya saat sumber klien tidak sudah menjawabnya."""
    staged = run.get("preference_candidate")
    if not staged or "revision_policy" in ledger_draft:
        return ledger_draft, False
    merged = dict(ledger_draft)
    rounds = staged["revision_rounds"]
    merged["revision_policy"] = {
        "rounds_total": {
            "value": rounds,
            "state": "FREELANCER_POLICY",
            "source_artifact": "artifact:policy-1",
            "source_quote": "%d revision rounds are included." % rounds,
            "confidence": None,
        }
    }
    return merged, True


async def run_extraction(run_id, brief):
    """Jalankan agent.extraction_agent lewat Gemini sungguhan atas satu
    artifact brief (artifact:brief-1). Mengembalikan ledger draft (dict)
    dari tool_context.state["ledger_draft"] setelah run selesai, atau None
    kalau agent tidak pernah memanggil save_ledger_draft.

    Fungsi terpisah (bukan inline di push()) supaya test bisa
    memonkeypatch-nya -- lihat conftest.stub_extraction (autouse): semua
    test lewat push handler TIDAK memanggil Gemini sungguhan, supaya test
    suite cepat, deterministik, dan tidak butuh GEMINI_API_KEY. Wiring ini
    diverifikasi manual lewat uvicorn (CATATAN-LANJUTAN.md), bukan di sini.
    """
    from google.adk.runners import InMemoryRunner
    from google.genai import types as genai_types

    runner = InMemoryRunner(agent=agent.extraction_agent, app_name="delividence")
    await runner.session_service.create_session(
        app_name="delividence",
        user_id="worker",
        session_id=run_id,
        state={"artifacts": {"artifact:brief-1": brief}},
    )
    # tool_context.state (diisi di atas) HANYA terlihat dari dalam tool
    # (validate_quote_candidate/save_ledger_draft) -- model sendiri tidak
    # bisa "melihat" state, jadi teks brief MUST disertakan langsung di
    # prompt di sini juga. Tanpa ini model menjawab tidak ada konten sama
    # sekali untuk dikutip, walau state sudah terisi (bug yang sempat
    # lolos: run pertama selalu menghasilkan ledger kosong).
    message = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=(
            'Extract the deal ledger from this artifact. source_artifact for every '
            'candidate MUST be exactly "artifact:brief-1" (with the "artifact:" prefix).\n\n'
            "--- artifact:brief-1 ---\n" + brief
        ))],
    )
    async for _ in runner.run_async(user_id="worker", session_id=run_id, new_message=message):
        pass

    session = await runner.session_service.get_session(
        app_name="delividence", user_id="worker", session_id=run_id
    )
    return session.state.get("ledger_draft")


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

    # Kegagalan Gemini (mis. 503 model sedang overload) TIDAK BOLEH
    # menjatuhkan seluruh worker -- round ini sudah diklaim (claim_job di
    # atas), jadi Pub/Sub redelivery tidak akan mengulang kerja ini (lihat
    # CATATAN-LANJUTAN.md: belum ada retry level-job untuk kegagalan Gemini
    # transient, gap yang diketahui). Status tetap ditulis jujur sebagai
    # gagal, bukan diam-diam dianggap "0 field ditemukan".
    try:
        ledger_draft = await run_extraction(run_id, run["brief"])
    except Exception:
        log.exception("ekstraksi Gemini gagal untuk run %s", run_id)
        ledger_draft = None
        final_status = "failed"
        detail = "Gemini extraction failed (see worker logs); the ledger stays empty."
    else:
        final_status = "done"
        ledger_draft, applied_preference = _merge_staged_preference(run, ledger_draft or {})
        if ledger_draft:
            store.update_run(run_id, ledger=ledger_draft)
            audit.append_event(
                run_id, "LEDGER_DRAFT_SAVED", "model", 0,
                {"fields": sorted(ledger_draft.keys())},
            )
            if applied_preference:
                audit.append_event(
                    run_id, "PREFERENCE_CONFIRMED", "system", 0,
                    {"field": "revision_policy.rounds_total", "state": "FREELANCER_POLICY"},
                )
            detail = "Brief extracted with Gemini -- %d ledger field(s) filled." % len(ledger_draft)
        else:
            detail = "Gemini returned no ledger field for this brief."
    store.append_audit_step(run_id, "extraction", detail)

    store.update_run(run_id, status=final_status)
    return Response(status_code=204)
