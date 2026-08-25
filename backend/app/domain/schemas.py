"""Skema ledger, baseline, dan audit event — satu source of truth (09-DOMAIN-RULES
§10 butir 1).

Bentuk-bentuk ini sebelumnya tersebar sebagai dict ad-hoc di test dan prosa
dokumen. Modul lain (ekstraksi, service ledger, API) MUST membangun payload
lewat model di sini, bukan menuliskan dict sendiri yang menafsirkan ulang
bentuknya — supaya perbedaan tipis (field hilang, nama beda) gagal saat
divalidasi, bukan diam-diam menghasilkan data yang salah bentuk.

Model di sini hanya mendeskripsikan BENTUK data. Aturan (effective_status,
gate readiness, alokasi seq) tetap di app/domain/{criteria,readiness}.py dan
app/audit.py — sengaja tidak diduplikasi di sini.
"""

from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.criteria import CRITERION_KEY_MAX_LENGTH, CRITERION_KEY_PATTERN
from app.domain.enums import (
    ACTORS,
    AUDIT_EVENT_TYPES,
    CRITERION_DECISIONS,
    FIELD_STATES,
    NOT_SET,
)


class _Strict(BaseModel):
    # extra="forbid": field yang salah nama atau typo gagal saat validasi,
    # bukan diam-diam terbuang atau diam-diam diterima.
    model_config = ConfigDict(extra="forbid")


# --- Ledger field (01 §4.1) -------------------------------------------------


class LedgerField(_Strict):
    """Satu field ledger: value + state + provenance opsional.

    source_artifact/source_quote/confidence/version opsional karena state
    seperti MISSING tidak punya provenance untuk dilekatkan.
    """

    value: Any = None
    state: str
    source_artifact: Optional[str] = None
    source_quote: Optional[str] = None
    confidence: Optional[float] = None
    version: Optional[int] = None

    @field_validator("state")
    @classmethod
    def _state_dikenal(cls, v):
        if v not in FIELD_STATES:
            raise ValueError("state tidak dikenal: %r" % (v,))
        return v


# --- Deliverable & acceptance criteria (09 §9.4, readiness.py) -------------


class Deliverable(_Strict):
    id: str
    title: str


class AcceptanceCriterionRef(_Strict):
    """Baris di dalam value acceptance_criteria ledger — referensi ke
    criterion, bukan criterion baseline itu sendiri (lihat Criterion di
    bawah, yang punya text_hash dan menjadi rujukan effective_status)."""

    deliverable_id: str
    criterion_key: str
    text: str


class DeliverablesField(LedgerField):
    value: Optional[list[Deliverable]] = None


class OutOfScopeField(LedgerField):
    value: Optional[list[str]] = None


class AcceptanceCriteriaField(LedgerField):
    value: Optional[list[AcceptanceCriterionRef]] = None


class FinalDeadlineField(LedgerField):
    value: Optional[str] = None


class RoundsTotalField(LedgerField):
    # NOT_SET adalah sentinel value (§5.7), bukan state ketujuh — boleh
    # muncul di sini walau state-nya AGREED.
    value: Optional[Union[int, Literal[NOT_SET]]] = None


class TimelineSection(_Strict):
    final_deadline: Optional[FinalDeadlineField] = None


class RevisionPolicySection(_Strict):
    rounds_total: Optional[RoundsTotalField] = None


class DealLedger(_Strict):
    """Ledger minimum, 01 §4.1. Field kritis: lihat enums.CRITICAL_FIELDS."""

    deliverables: Optional[DeliverablesField] = None
    in_scope: Optional[LedgerField] = None
    out_of_scope: Optional[OutOfScopeField] = None
    acceptance_criteria: Optional[AcceptanceCriteriaField] = None
    timeline: Optional[TimelineSection] = None
    revision_policy: Optional[RevisionPolicySection] = None
    dependencies: Optional[LedgerField] = None
    assumptions: Optional[LedgerField] = None
    unresolved_questions: Optional[LedgerField] = None


# --- Baseline & criteria (09 §2.3) ------------------------------------------


class Criterion(_Strict):
    text: str
    text_hash: str
    introduced_in_version: Optional[int] = None


class CanonicalPayload(_Strict):
    deliverables: list = Field(default_factory=list)
    in_scope: list = Field(default_factory=list)
    out_of_scope: list = Field(default_factory=list)
    timeline: dict = Field(default_factory=dict)
    revision_policy: dict = Field(default_factory=dict)
    criteria: dict[str, Criterion] = Field(default_factory=dict)

    @field_validator("criteria")
    @classmethod
    def _key_format(cls, v):
        for key in v:
            if not CRITERION_KEY_PATTERN.match(key) or len(key) > CRITERION_KEY_MAX_LENGTH:
                raise ValueError("criterion_key tidak sesuai format: %r" % (key,))
        return v


class Baseline(_Strict):
    version: int
    status: Literal["DRAFT", "ACTIVE"] = "DRAFT"
    canonical_payload: CanonicalPayload
    payload_hash: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    activated_seq: Optional[int] = None


# --- Keputusan criterion terproyeksi (dipakai app.domain.criteria) ---------


class CriterionDecision(_Strict):
    """Satu baris `decisions` yang dikonsumsi criteria.effective_status —
    hasil proyeksi dari event CRITERION_DECISION, bukan event itu sendiri."""

    criterion_key: str
    decision: str
    baseline_version: int
    criterion_text_hash: str
    seq: int

    @field_validator("decision")
    @classmethod
    def _decision_dikenal(cls, v):
        if v not in CRITERION_DECISIONS:
            raise ValueError("decision tidak dikenal: %r" % (v,))
        return v


# --- Audit event envelope (09 §7.1, ditulis oleh app.audit) ----------------


class AuditEventEnvelope(_Strict):
    event_id: str
    seq: int
    type: str
    actor: str
    actor_ref: Optional[str] = None
    baseline_version: Optional[int] = None
    created_at: str
    payload: dict = Field(default_factory=dict)

    @field_validator("type")
    @classmethod
    def _type_dikenal(cls, v):
        if v not in AUDIT_EVENT_TYPES:
            raise ValueError("tipe event tidak dikenal: %r" % (v,))
        return v

    @field_validator("actor")
    @classmethod
    def _actor_dikenal(cls, v):
        if v not in ACTORS:
            raise ValueError("actor tidak dikenal: %r" % (v,))
        return v
