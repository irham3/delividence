import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field, ValidationError, field_validator

from app import audit, auth, baselines, client_links, config, evidence, queue, scope_requests, store
from app.domain import client_link, criteria, guardrail, proof, readiness, schemas
from app.domain.baseline import build_canonical_payload
from app.domain.canonical import payload_hash as compute_payload_hash
from app.domain.enums import ACCEPTED, CHANGES_REQUESTED, FREELANCER_POLICY
from app.domain.ledger import apply_client_answer

# Action yang diizinkan tiap purpose client link -- portal new-request lewat
# client link belum dibangun (submit request lewat client link, bukan cuma
# lewat freelancer), lihat CATATAN-LANJUTAN.md.
_ACTIONS_BY_PURPOSE = {
    "CLARIFICATION": ["view", "answer", "confirm"],
    "DELIVERY_REVIEW": ["view", "submit_review"],
}

app = FastAPI(title="Delividence API")

# Frontend berjalan di origin lain (Next.js), jadi CORS wajib. Daftarnya dibatasi
# lewat env supaya produksi tidak terbuka untuk semua origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


def _owned_run_or_404(run_id: str, owner_id: str):
    """Run yang dimiliki `owner_id`, atau 404 -- juga kalau run ada tapi
    milik owner lain (02 §8: owner A tidak boleh tahu deal B ada)."""
    run = store.get_run(run_id)
    if run is None or run.get("owner_id") != owner_id:
        raise HTTPException(status_code=404, detail="run not found")
    return run


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
def create_run(req: CreateRunRequest, owner_id: str = Depends(auth.require_owner)):
    # deal_id == run_id (satu-satu, lihat CATATAN-LANJUTAN.md): satu brief
    # yang disubmit menciptakan tepat satu deal, jadi id run pemrosesannya
    # dipakai ulang sebagai deal_id untuk audit log 09-DOMAIN-RULES §7.
    run_id = uuid.uuid4().hex
    store.create_run(run_id, owner_id, req.brief, req.output_language)
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
def get_run(run_id: str, owner_id: str = Depends(auth.require_owner)):
    return _owned_run_or_404(run_id, owner_id)


class CreateClientLinkRequest(BaseModel):
    purpose: str = "CLARIFICATION"

    @field_validator("purpose")
    @classmethod
    def _known_purpose(cls, v):
        if v not in _ACTIONS_BY_PURPOSE:
            raise ValueError("purpose must be one of %s" % (", ".join(_ACTIONS_BY_PURPOSE),))
        return v


@app.post("/runs/{run_id}/client-links", status_code=201)
def create_client_link(
    run_id: str,
    req: CreateClientLinkRequest = CreateClientLinkRequest(),
    owner_id: str = Depends(auth.require_owner),
):
    """Freelancer menerbitkan client link (02 §8). Token mentah HANYA muncul
    di response ini -- pemanggil bertanggung jawab mengirimkannya ke klien
    lewat kanal apa pun (chat/email), sistem tidak menyimpannya lagi setelah
    ini."""
    _owned_run_or_404(run_id, owner_id)

    token = client_links.issue(run_id, req.purpose, _ACTIONS_BY_PURPOSE[req.purpose])
    return {"token": token, "purpose": req.purpose}


def _resolve_client_link(token: str, purpose: str, action: str):
    record = client_links.resolve(token)
    ok, reason = client_link.check(record, datetime.now(timezone.utc), purpose, action)
    if not ok:
        raise HTTPException(status_code=403, detail=reason)
    return record


def _next_baseline_preview(deal_id, ledger):
    """(next_version, canonical_payload, payload_hash) untuk ledger saat ini.

    Deterministik dari ledger yang sama (test_baseline.py) -- dipakai GET
    /client/{token} untuk menunjukkan payload_hash yang harus di-echo balik
    ke POST .../confirm sebagai precondition (02 §5: approval basi -> 409)."""
    active_version = baselines.get_active_version(deal_id)
    next_version = active_version + 1
    previous = baselines.get(deal_id, active_version) if active_version else None
    previous_criteria = previous["canonical_payload"]["criteria"] if previous else None
    canonical_payload = build_canonical_payload(ledger, next_version, previous_criteria)
    return next_version, canonical_payload, compute_payload_hash(canonical_payload)


@app.get("/client/{token}")
def view_client_link(token: str):
    record = _resolve_client_link(token, "CLARIFICATION", "view")
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
    record = _resolve_client_link(token, "CLARIFICATION", "answer")
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
    record = _resolve_client_link(token, "CLARIFICATION", "confirm")
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


@app.post("/runs/{run_id}/change-proposal")
def propose_change(
    run_id: str, req: SubmitAnswersRequest, owner_id: str = Depends(auth.require_owner)
):
    """Freelancer mengusulkan perubahan ledger setelah request diklasifikasi
    CHANGE_REQUEST (01-PRD §5 langkah 8: "sistem membuat diff ...; perubahan
    hanya aktif setelah approval"). Mengedit ledger yang sama dengan
    `/client/{token}/answers` -- bedanya state jadi FREELANCER_POLICY (bukan
    CLIENT_STATED) dan MUST sudah ada baseline aktif (endpoint ini untuk
    mengubah kesepakatan yang sudah berjalan, bukan setup awal). Belum
    mengaktifkan apa pun -- freelancer masih perlu menerbitkan client link
    CLARIFICATION baru supaya klien meninjau lalu "Confirm project plan" (
    endpoint yang sama dengan v1, version-agnostic: next_version = active + 1
    ) sebelum ini jadi baseline v2."""
    run = _owned_run_or_404(run_id, owner_id)
    active_version, _ = _active_baseline_or_409(run_id, run)

    ledger = run.get("ledger", {})
    for answer in req.answers:
        apply_client_answer(ledger, answer.field, answer.value, state=FREELANCER_POLICY)

    try:
        schemas.DealLedger.model_validate(ledger)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    for answer in req.answers:
        audit.append_event(
            run_id, "CHANGE_PROPOSED", "freelancer", active_version,
            {"field": answer.field, "value": answer.value},
        )

    store.update_run(run_id, ledger=ledger)
    ready, blockers = readiness.evaluate(ledger)
    return {"ledger": ledger, "readiness": {"ready": ready, "blockers": blockers}}


class AddEvidenceRequest(BaseModel):
    criterion_key: str = Field(min_length=1)
    type: str
    uri: str = Field(min_length=1)
    caption: str | None = None

    @field_validator("type")
    @classmethod
    def _known_type(cls, v):
        if v not in evidence.EVIDENCE_TYPES:
            raise ValueError("type must be one of %s" % (", ".join(sorted(evidence.EVIDENCE_TYPES)),))
        return v


def _active_baseline_or_409(run_id, run):
    active_version = run.get("active_baseline_version")
    if not active_version:
        raise HTTPException(status_code=409, detail="No active baseline yet.")
    return active_version, baselines.get(run_id, active_version)


@app.post("/runs/{run_id}/evidence", status_code=201)
def add_evidence(run_id: str, req: AddEvidenceRequest, owner_id: str = Depends(auth.require_owner)):
    """Freelancer melampirkan evidence ke satu acceptance criterion (01-PRD
    §5 langkah 9). criterion_key MUST ada di baseline aktif."""
    run = _owned_run_or_404(run_id, owner_id)

    active_version, baseline = _active_baseline_or_409(run_id, run)
    if req.criterion_key not in baseline["canonical_payload"]["criteria"]:
        raise HTTPException(status_code=404, detail="criterion_key not found in active baseline")

    record = evidence.add(run_id, req.criterion_key, req.type, req.uri, req.caption)
    audit.append_event(
        run_id, "EVIDENCE_ADDED", "freelancer", active_version,
        {"evidence_id": record["evidence_id"], "criterion_key": req.criterion_key, "type": req.type},
    )
    return record


def _decisions_for(deal_id):
    """Proyeksi event CRITERION_DECISION -> bentuk `decisions` yang
    dikonsumsi app.domain.criteria.effective_status/can_record_decision.

    Field ekstra (actor/reason/created_at) ikut disertakan -- criteria.py
    hanya membaca lima key intinya dan mengabaikan sisanya, jadi aman
    dipakai ulang oleh proof manifest (build_proof_manifest) tanpa proyeksi
    kedua."""
    out = []
    for e in audit.list_events(deal_id):
        if e["type"] != "CRITERION_DECISION":
            continue
        p = e["payload"]
        out.append({
            "criterion_key": p["criterion_key"],
            "decision": p["decision"],
            "baseline_version": e["baseline_version"],
            "criterion_text_hash": p["criterion_text_hash"],
            "seq": e["seq"],
            "actor": e["actor"],
            "reason": p.get("reason"),
            "created_at": e["created_at"],
        })
    return out


@app.get("/client/{token}/review")
def view_delivery_review(token: str):
    record = _resolve_client_link(token, "DELIVERY_REVIEW", "view")
    deal_id = record["deal_id"]
    run = store.get_run(deal_id)
    if run is None:
        raise HTTPException(status_code=404, detail="deal not found")

    active_version, active_baseline = _active_baseline_or_409(deal_id, run)
    all_baselines = baselines.get_all_up_to(deal_id, active_version)
    decisions = _decisions_for(deal_id)

    criteria_view = [
        {
            "criterion_key": key,
            "text": crit["text"],
            "status": criteria.effective_status(key, active_version, all_baselines, decisions),
            "evidence": evidence.list_for_criterion(deal_id, key),
        }
        for key, crit in active_baseline["canonical_payload"]["criteria"].items()
    ]
    return {"baseline_version": active_version, "criteria": criteria_view}


class CriterionDecisionItem(BaseModel):
    criterion_key: str = Field(min_length=1)
    decision: str
    reason: str | None = None

    @field_validator("decision")
    @classmethod
    def _known_decision(cls, v):
        if v not in (ACCEPTED, CHANGES_REQUESTED):
            raise ValueError("decision must be ACCEPTED or CHANGES_REQUESTED")
        return v


class SubmitReviewRequest(BaseModel):
    decisions: list[CriterionDecisionItem] = Field(min_length=1)


@app.post("/client/{token}/review")
def submit_delivery_review(token: str, req: SubmitReviewRequest):
    """Klien mengirim Accept/Request changes untuk sekumpulan criterion dalam
    SATU aksi submit (01-PRD §5 langkah 10) -- satu review_session_id untuk
    seluruh keputusan di request ini. Semua item divalidasi dulu sebelum satu
    pun event ditulis, supaya tidak ada submission yang setengah tersimpan."""
    record = _resolve_client_link(token, "DELIVERY_REVIEW", "submit_review")
    deal_id = record["deal_id"]
    run = store.get_run(deal_id)
    if run is None:
        raise HTTPException(status_code=404, detail="deal not found")

    active_version, active_baseline = _active_baseline_or_409(deal_id, run)
    active_criteria = active_baseline["canonical_payload"]["criteria"]
    all_baselines = baselines.get_all_up_to(deal_id, active_version)
    decisions_so_far = _decisions_for(deal_id)

    prepared = []
    for item in req.decisions:
        if item.decision == CHANGES_REQUESTED and not (item.reason or "").strip():
            raise HTTPException(
                status_code=422,
                detail="reason is required when requesting changes for %r" % item.criterion_key,
            )
        if item.criterion_key not in active_criteria:
            raise HTTPException(
                status_code=404, detail="criterion_key not found: %r" % item.criterion_key
            )
        allowed, why = criteria.can_record_decision(
            item.criterion_key, active_version, all_baselines, decisions_so_far, item.decision
        )
        if not allowed:
            raise HTTPException(status_code=409, detail=why)
        prepared.append((item, active_criteria[item.criterion_key]["text_hash"]))

    review_session_id = uuid.uuid4().hex
    actor_ref = client_links.actor_ref_for(token)
    audit.append_event(
        deal_id, "REVIEW_SESSION_OPENED", "client", active_version,
        {"review_session_id": review_session_id}, actor_ref=actor_ref,
    )
    for item, text_hash in prepared:
        audit.append_event(
            deal_id, "CRITERION_DECISION", "client", active_version,
            {
                "criterion_key": item.criterion_key,
                "decision": item.decision,
                "criterion_text_hash": text_hash,
                "reason": item.reason,
                "review_session_id": review_session_id,
            },
            actor_ref=actor_ref,
        )

    return {
        "review_session_id": review_session_id,
        "decisions": [item.model_dump() for item, _ in prepared],
    }


@app.get("/runs/{run_id}/proof")
def get_proof(run_id: str, format: str = "json", owner_id: str = Depends(auth.require_owner)):
    """Proof Manifest / Acceptance Record (01-PRD §5 langkah 12) -- rangkuman
    baseline + status tiap criterion + evidence + keputusan klien, siap
    diekspor. `format=json` (default) atau `format=md`."""
    if format not in ("json", "md"):
        raise HTTPException(status_code=422, detail="format must be 'json' or 'md'")

    run = _owned_run_or_404(run_id, owner_id)

    active_version, active_baseline = _active_baseline_or_409(run_id, run)
    all_baselines = baselines.get_all_up_to(run_id, active_version)
    decisions = _decisions_for(run_id)

    criteria_keys = active_baseline["canonical_payload"]["criteria"]
    criteria_status = {
        key: criteria.effective_status(key, active_version, all_baselines, decisions)
        for key in criteria_keys
    }
    evidence_by_criterion = {
        key: evidence.list_for_criterion(run_id, key) for key in criteria_keys
    }
    # Keputusan terakhir per criterion (seq terbesar) -- sama seperti aturan
    # "last" di app.domain.criteria.effective_status, bukan tie-break baru.
    latest_decision_by_criterion = {}
    for d in sorted(decisions, key=lambda d: d["seq"]):
        latest_decision_by_criterion[d["criterion_key"]] = d

    manifest = proof.build_manifest(
        run_id, run["brief"], run["output_language"], active_baseline,
        criteria_status, evidence_by_criterion, latest_decision_by_criterion,
    )

    if format == "md":
        return PlainTextResponse(proof.to_markdown(manifest), media_type="text/markdown")
    return manifest


class SubmitScopeRequestRequest(BaseModel):
    raw_text: str = Field(min_length=1)
    submitted_by: str = "freelancer"

    @field_validator("submitted_by")
    @classmethod
    def _known_submitter(cls, v):
        if v not in ("freelancer", "client"):
            raise ValueError("submitted_by must be 'freelancer' or 'client'")
        return v


@app.post("/runs/{run_id}/requests", status_code=201)
def submit_scope_request(
    run_id: str, req: SubmitScopeRequestRequest, owner_id: str = Depends(auth.require_owner)
):
    """Freelancer mencatat request baru dari kanal lain, atau klien
    mengirimkannya (01-PRD §5 langkah 7). Guardrail baru bermakna kalau
    sudah ada baseline untuk dibandingkan."""
    run = _owned_run_or_404(run_id, owner_id)
    active_version, _ = _active_baseline_or_409(run_id, run)

    record = scope_requests.submit(run_id, req.raw_text, req.submitted_by)
    audit.append_event(
        run_id, "REQUEST_SUBMITTED", req.submitted_by, active_version,
        {"request_id": record["request_id"], "raw_text": req.raw_text},
    )
    return record


@app.get("/runs/{run_id}/requests")
def list_scope_requests(run_id: str, owner_id: str = Depends(auth.require_owner)):
    _owned_run_or_404(run_id, owner_id)
    return scope_requests.list_for_deal(run_id)


class CitationItem(BaseModel):
    ref: str = Field(min_length=1)
    quote: str = Field(min_length=1)


class ClassifyScopeRequestRequest(BaseModel):
    classification: str
    citations: list[CitationItem] = Field(default_factory=list)

    @field_validator("classification")
    @classmethod
    def _known_classification(cls, v):
        if v not in guardrail.CLASSIFICATIONS:
            raise ValueError(
                "classification must be one of %s" % (", ".join(sorted(guardrail.CLASSIFICATIONS)),)
            )
        return v


@app.post("/runs/{run_id}/requests/{request_id}/classify")
def classify_scope_request(
    run_id: str,
    request_id: str,
    req: ClassifyScopeRequestRequest,
    owner_id: str = Depends(auth.require_owner),
):
    """Freelancer mengonfirmasi klasifikasi (09-DOMAIN-RULES §8: hanya
    freelancer yang berwenang memutuskan klasifikasi scope -- bukan klien,
    bukan model). Setiap citation divalidasi tanpa syarat lewat
    app.domain.guardrail; IN_SCOPE/CHANGE_REQUEST tanpa kutipan valid
    otomatis turun ke AMBIGUOUS (02 §4.5), classification yang dikirim
    tidak pernah dipercaya langsung."""
    run = _owned_run_or_404(run_id, owner_id)
    active_version, active_baseline = _active_baseline_or_409(run_id, run)

    if scope_requests.get(run_id, request_id) is None:
        raise HTTPException(status_code=404, detail="request not found")

    text_by_ref = guardrail.citable_text(active_baseline)
    final_classification, valid_citations = guardrail.classify(
        req.classification, [c.model_dump() for c in req.citations], text_by_ref
    )

    updated = scope_requests.mark_classified(run_id, request_id, final_classification, valid_citations)
    audit.append_event(
        run_id, "SCOPE_CLASSIFICATION_DECIDED", "freelancer", active_version,
        {
            "request_id": request_id,
            "classification": final_classification,
            "proposed_classification": req.classification,
            "citations": valid_citations,
        },
    )
    return updated
