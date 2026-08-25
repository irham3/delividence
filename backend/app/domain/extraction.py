"""Proyeksi kandidat field dari model menjadi ledger field tervalidasi.

02-ARCHITECTURE §4.3: "Setelah structured output selesai, API/worker SELALU
memvalidasi setiap source_quote terhadap artifact sebelum draft ditulis,
terlepas dari apakah model memanggil validate_quote_candidate." Gate ini
karena itu tidak bersyarat di sini — dipanggil untuk setiap kandidat, bukan
hanya kandidat yang model minta divalidasi.

Fungsi murni: tidak memanggil Gemini, tidak menyentuh Firestore, tidak
menyentuh waktu. app/agent.py memanggil modul ini dari dalam tool ADK; modul
ini sendiri tidak tahu apa-apa soal ADK.
"""

from app.domain.canonical import validate_quote
from app.domain.enums import (
    AGREED,
    CLIENT_STATED,
    FREELANCER_POLICY,
    MISSING,
    PROPOSED,
    DomainError,
)

# §5.4: hanya dua pihak yang bisa jadi sumber candidate. asserted_by lain
# (termasuk "model") tidak berhak atas CLIENT_STATED/FREELANCER_POLICY --
# turun ke PROPOSED lewat .get() default di project_field_candidate.
_ASSERTED_BY_STATE = {
    "client": CLIENT_STATED,
    "freelancer": FREELANCER_POLICY,
}

_EMPTY_VALUES = (None, "", [], {})


def project_field_candidate(candidate, artifacts):
    """Satu kandidat model -> satu ledger field {value, state, source_artifact,
    source_quote, confidence}.

    `candidate`: dict dari model -- value, source_artifact, source_quote,
    confidence, asserted_by ("client" | "freelancer"). `state` usulan model
    diabaikan; state akhir selalu dihitung ulang di sini, tidak pernah
    dipercaya dari model (G-1).

    `artifacts`: {artifact_ref: text_lengkap}, dipakai validate_quote.
    """
    if candidate.get("state") == AGREED:
        # G-1: model tidak pernah menghasilkan state kesepakatan. Ini
        # pelanggaran kontrak tool, bukan degradasi kualitas biasa.
        raise DomainError("model tidak boleh mengusulkan state AGREED")

    value = candidate.get("value")
    if value in _EMPTY_VALUES:
        return {
            "value": None,
            "state": MISSING,
            "source_artifact": None,
            "source_quote": None,
            "confidence": None,
        }

    quote = candidate.get("source_quote")
    artifact_ref = candidate.get("source_artifact")
    artifact_text = artifacts.get(artifact_ref) if artifact_ref else None
    quote_valid = bool(quote) and bool(artifact_text) and validate_quote(quote, artifact_text)

    if not quote_valid:
        # Ada nilai, tapi kutipannya tidak lolos -- tidak boleh diatribusikan
        # sebagai CLIENT_STATED/FREELANCER_POLICY (02 §4.3).
        return {
            "value": value,
            "state": PROPOSED,
            "source_artifact": artifact_ref,
            "source_quote": quote,
            "confidence": candidate.get("confidence"),
        }

    state = _ASSERTED_BY_STATE.get(candidate.get("asserted_by"), PROPOSED)
    return {
        "value": value,
        "state": state,
        "source_artifact": artifact_ref,
        "source_quote": quote,
        "confidence": candidate.get("confidence"),
    }


def assemble_ledger_draft(candidates, artifacts):
    """Banyak kandidat model -> dict ledger {field_path: LedgerField-shaped dict}.

    `candidates`: list dict, tiap item punya "field" (path bertitik, mis.
    "timeline.final_deadline") plus bentuk candidate di project_field_candidate.

    Path bertitik dipetakan ke struktur nested (mis. "timeline.final_deadline"
    -> {"timeline": {"final_deadline": {...}}}), sesuai bentuk yang dipakai
    app.domain.readiness dan app.domain.schemas.DealLedger.
    """
    draft = {}
    for candidate in candidates:
        path = candidate["field"]
        field = project_field_candidate(candidate, artifacts)

        *parents, leaf = path.split(".")
        node = draft
        for part in parents:
            node = node.setdefault(part, {})
        node[leaf] = field
    return draft
