import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError, field_validator

from app import audit, baselines, client_links, config, queue, store
from app.domain import client_link, readiness, schemas
from app.domain.baseline import build_canonical_payload
from app.domain.canonical import payload_hash as compute_payload_hash
from app.domain.ledger import apply_client_answer

# Purpose tunggal yang didukung endpoint klien untuk saat ini -- lihat
# CATATAN-LANJUTAN.md, portal klien penuh (approval/delivery review/new
# request) belum dibangun.
_CLARIFICATION_ACTIONS = ["view", "answer", "confirm"]

app = FastAPI(title="Delividence API")

# Frontend berjalan di origin lain (Next.js), jadi CORS wajib. Daftarnya dibatasi
# lewat env supaya produksi tidak terbuka untuk semua origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class CreateRunRequest(BaseModel):
    brief: str = Field(min_length=1, max_length=config.MAX_BRIEF_CHARS)
    # English adalah default. Aturan hackathon mewajibkan aplikasi mendukung
    # bahasa Inggris minimal; Bahasa Indonesia adalah pilihan tambahan.
    output_language: str = "en"

    @field_validator("output_language")
    @classmethod
    def _supported(cls, v):
        v = v.strip().lower()
        if v not in config.SUPPORTED_OUTPUT_LANGUAGES:
            raise ValueError(
                "output_language must be one of %s"
                % (", ".join(config.SUPPORTED_OUTPUT_LANGUAGES),)
            )
        return v


@app.get("/health")
def health():
    return {"status": "ok", "role": "api", "local": config.LOCAL}


@app.post("/runs", status_code=202)
def create_run(req: CreateRunRequest):
    # deal_id == run_id (satu-satu, lihat CATATAN-LANJUTAN.md): satu brief
    # yang disubmit menciptakan tepat satu deal, jadi id run pemrosesannya
    # dipakai ulang sebagai deal_id untuk audit log 09-DOMAIN-RULES §7.
    run_id = uuid.uuid4().hex
    store.create_run(run_id, req.brief, req.output_language)
    audit.append_event(
        run_id, "DEAL_CREATED", "freelancer", 0,
        {"output_language": req.output_language},
    )
    audit.append_event(
        run_id, "ARTIFACT_ADDED", "freelancer", 0,
        {"artifact_ref": "artifact:brief-1", "type": "text", "chars": len(req.brief)},
    )
    queue.publish({"run_id": run_id, "round": 1})
    return {"run_id": run_id, "status": "queued"}


@app.get("/runs/{run_id}")
def get_run(run_id: str):
    run = store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return run


@app.post("/runs/{run_id}/client-links", status_code=201)
def create_client_link(run_id: str):
    """Freelancer menerbitkan client link untuk klarifikasi (02 §8). Token
    mentah HANYA muncul di response ini -- pemanggil bertanggung jawab
    mengirimkannya ke klien lewat kanal apa pun (chat/email), sistem tidak
    menyimpannya lagi setelah ini."""
    if store.get_run(run_id) is None:
        raise HTTPException(status_code=404, detail="run not found")

    token = client_links.issue(run_id, "CLARIFICATION", _CLARIFICATION_ACTIONS)
    return {"token": token, "purpose": "CLARIFICATION"}


def _resolve_client_link(token: str, action: str):
    record = client_links.resolve(token)
    ok, reason = client_link.check(record, datetime.now(timezone.utc), "CLARIFICATION", action)
    if not ok:
        raise HTTPException(status_code=403, detail=reason)
    return record


def _next_baseline_preview(deal_id, ledger):
    """(next_version, canonical_payload, payload_hash) untuk ledger saat ini.

    Deterministik dari ledger yang sama (test_baseline.py) -- dipakai GET
    /client/{token} untuk menunjukkan payload_hash yang harus di-echo balik
    ke POST .../confirm sebagai precondition (02 §5: approval basi -> 409)."""
    next_version = baselines.get_active_version(deal_id) + 1
    canonical_payload = build_canonical_payload(ledger, next_version)
    return next_version, canonical_payload, compute_payload_hash(canonical_payload)


@app.get("/client/{token}")
def view_client_link(token: str):
    record = _resolve_client_link(token, "view")
    deal_id = record["deal_id"]
    run = store.get_run(deal_id)
    if run is None:
        raise HTTPException(status_code=404, detail="deal not found")

    ledger = run.get("ledger", {})
    ready, blockers = readiness.evaluate(ledger)
    _, _, hash_ = _next_baseline_preview(deal_id, ledger)
    return {
        "brief": run["brief"],
        "output_language": run["output_language"],
        "ledger": ledger,
        "readiness": {"ready": ready, "blockers": blockers},
        "payload_hash": hash_,
    }


class ClientAnswer(BaseModel):
    field: str = Field(min_length=1)
    value: Any = None


class SubmitAnswersRequest(BaseModel):
    answers: list[ClientAnswer] = Field(min_length=1)


@app.post("/client/{token}/answers")
def submit_client_answers(token: str, req: SubmitAnswersRequest):
    """Klien mengoreksi/melengkapi field ledger langsung (01 §4.1). Link
    SENGAJA tidak ditandai selesai di sini -- klien boleh mengirim beberapa
    ronde koreksi sebelum "Confirm project plan" (baseline approval, belum
    dibangun; lihat CATATAN-LANJUTAN.md) menutup link ini."""
    record = _resolve_client_link(token, "answer")
    deal_id = record["deal_id"]
    run = store.get_run(deal_id)
    if run is None:
        raise HTTPException(status_code=404, detail="deal not found")

    ledger = run.get("ledger", {})
    for answer in req.answers:
        apply_client_answer(ledger, answer.field, answer.value)

    # Skema jadi gate bentuk (09 §10 butir 1): field top-level yang tidak
    # dikenal atau bentuk value yang salah ditolak di sini, sebelum satu pun
    # audit event ditulis -- supaya tidak ada koreksi setengah tersimpan.
    try:
        schemas.DealLedger.model_validate(ledger)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    actor_ref = client_links.actor_ref_for(token)
    for answer in req.answers:
        audit.append_event(
            deal_id, "CLIENT_ANSWERED", "client", 0,
            {"field": answer.field, "value": answer.value},
            actor_ref=actor_ref,
        )

    store.update_run(deal_id, ledger=ledger)
    ready, blockers = readiness.evaluate(ledger)
    return {"ledger": ledger, "readiness": {"ready": ready, "blockers": blockers}}


class ConfirmProjectPlanRequest(BaseModel):
    # Precondition (02 §5): MUST persis payload_hash yang terakhir dilihat
    # klien lewat GET /client/{token}. Kalau ledger berubah sejak itu (mis.
    # tab lain, ronde koreksi lain), hash tidak cocok -> 409, bukan approval
    # diam-diam atas versi yang sudah basi.
    payload_hash: str = Field(min_length=1)


@app.post("/client/{token}/confirm")
def confirm_project_plan(token: str, req: ConfirmProjectPlanRequest):
    """"Confirm project plan" (01-PRD §5 langkah 5) -- membekukan ledger jadi
    baseline versi baru. Readiness gate MUST lolos; endpoint ini tidak bisa
    melewatinya (readiness.evaluate adalah satu-satunya sumber kebenaran,
    sama seperti di view_client_link/submit_client_answers)."""
    record = _resolve_client_link(token, "confirm")
    deal_id = record["deal_id"]
    run = store.get_run(deal_id)
    if run is None:
        raise HTTPException(status_code=404, detail="deal not found")

    ledger = run.get("ledger", {})
    ready, blockers = readiness.evaluate(ledger)
    if not ready:
        raise HTTPException(status_code=422, detail={"blockers": blockers})

    next_version, canonical_payload, hash_ = _next_baseline_preview(deal_id, ledger)
    if req.payload_hash != hash_:
        raise HTTPException(
            status_code=409,
            detail="The plan changed since you last viewed it. Please review again before confirming.",
        )

    actor_ref = client_links.actor_ref_for(token)
    approved_event = audit.append_event(
        deal_id, "BASELINE_APPROVED", "client", next_version,
        {"payload_hash": hash_}, actor_ref=actor_ref,
    )
    # BASELINE_APPROVED dan BASELINE_ACTIVATED sengaja dua event terpisah (09
    # §7.3): approval adalah aksi klien, aktivasi adalah transisi domain
    # service yang tervalidasi -- MVP ini tidak punya jalur approval yang
    # kedaluwarsa sebelum aktivasi, jadi keduanya ditulis berurutan di sini.
    activated_event = audit.append_event(deal_id, "BASELINE_ACTIVATED", "system", next_version, {})

    baseline = baselines.create(
        deal_id, next_version, canonical_payload, hash_,
        approved_by="client", approved_at=approved_event["created_at"],
        activated_seq=activated_event["seq"],
    )
    store.update_run(deal_id, active_baseline_version=next_version)
    # CLARIFICATION selesai tugasnya di sini -- ini "workflow purpose selesai"
    # yang dimaksud 02 §8, beda dari /answers yang sengaja tidak menutup link.
    client_links.mark_completed(token)

    return {"version": next_version, "payload_hash": hash_, "baseline": baseline}
