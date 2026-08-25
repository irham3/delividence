"""Enum tertutup — 09-DOMAIN-RULES §10 butir 4.

Satu file konstanta. Di-import, tidak pernah diketik ulang di tempat lain.
Menambah anggota di sini adalah perubahan kontrak, bukan detail implementasi.
"""


class DomainError(Exception):
    """Pelanggaran aturan domain. Bukan error teknis."""


# --- State field ledger (01 §4.1) -----------------------------------------

CLIENT_STATED = "CLIENT_STATED"
FREELANCER_POLICY = "FREELANCER_POLICY"
PROPOSED = "PROPOSED"
AGREED = "AGREED"
MISSING = "MISSING"
CONFLICTING = "CONFLICTING"

FIELD_STATES = frozenset(
    {CLIENT_STATED, FREELANCER_POLICY, PROPOSED, AGREED, MISSING, CONFLICTING}
)

# State yang memenuhi syarat field kritis (§5.7). PROPOSED tidak termasuk:
# usulan belum dikonfirmasi manusia, jadi masih memblokir.
SATISFYING_STATES = frozenset({CLIENT_STATED, FREELANCER_POLICY, AGREED})

# Sentinel VALUE, bukan state ketujuh (§5.7). Artinya kedua pihak sepakat
# batas itu memang tidak ditetapkan — berbeda dari MISSING yang berarti
# informasinya belum ada.
NOT_SET = "NOT_SET"


# --- Field kritis (§5.7, himpunan tertutup) -------------------------------

CRITICAL_FIELDS = (
    "deliverables",
    "acceptance_criteria",
    "out_of_scope",
    "timeline.final_deadline",
    "revision_policy.rounds_total",
)


# --- Status turunan criterion (§2.2) --------------------------------------

PENDING = "PENDING"
ACCEPTED = "ACCEPTED"
CHANGES_REQUESTED = "CHANGES_REQUESTED"
SUPERSEDED = "SUPERSEDED"
WITHDRAWN = "WITHDRAWN"

CRITERION_EFFECTIVE_STATUSES = frozenset(
    {PENDING, ACCEPTED, CHANGES_REQUESTED, SUPERSEDED, WITHDRAWN}
)

# Keputusan yang boleh ditulis klien pada satu criterion.
CRITERION_DECISIONS = frozenset({ACCEPTED, CHANGES_REQUESTED})


# --- Actor (§7.1) ---------------------------------------------------------

ACTOR_FREELANCER = "freelancer"
ACTOR_CLIENT = "client"
ACTOR_SYSTEM = "system"
ACTOR_MODEL = "model"

ACTORS = frozenset({ACTOR_FREELANCER, ACTOR_CLIENT, ACTOR_SYSTEM, ACTOR_MODEL})


# --- Tipe audit event (§7.3, himpunan tertutup) ---------------------------

AUDIT_EVENT_TYPES = frozenset(
    {
        "DEAL_CREATED",
        "ARTIFACT_ADDED",
        "LEDGER_DRAFT_SAVED",
        "QUESTIONS_SAVED",
        "CLIENT_ANSWERED",
        "CONFLICT_RESOLVED",
        "BASELINE_PROPOSED",
        "BASELINE_APPROVED",
        "BASELINE_ACTIVATED",
        "REQUEST_SUBMITTED",
        "SCOPE_ANALYSIS_PROPOSED",
        "SCOPE_CLASSIFICATION_DECIDED",
        "CHANGE_PROPOSED",
        "CHANGE_APPROVED",
        "EVIDENCE_ADDED",
        "REVIEW_SESSION_OPENED",
        "CRITERION_DECISION",
        "REVISION_ROUND_CONSUMED",
        "REVISION_ROUND_GRANTED",
        "PREFERENCE_CANDIDATE_SAVED",
        "PREFERENCE_CONFIRMED",
    }
)

# Modul B dan C dilepas pada profil submission ini (10 §4b). Tipe event-nya
# sengaja tetap ada di himpunan supaya kontrak log tidak berubah kalau modul
# itu dihidupkan lagi, tetapi tidak ada kode yang menulisnya.
DISABLED_EVENT_TYPES = frozenset(
    {"REVISION_ROUND_CONSUMED", "REVISION_ROUND_GRANTED", "CONFLICT_RESOLVED"}
)

MAX_CLARIFICATION_QUESTIONS = 3
