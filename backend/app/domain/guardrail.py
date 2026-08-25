"""Klasifikasi request baru terhadap baseline aktif -- Guardrail
(02-ARCHITECTURE §4.5, 01-PRD §5 langkah 7).

Fungsi murni: tidak memanggil Gemini, tidak menyentuh Firestore. Model boleh
mengusulkan classification + citation (nanti, lewat app/agent.py -- belum
di-wire, lihat CATATAN-LANJUTAN.md); fungsi di sini memvalidasi tiap citation
tanpa syarat, sama seperti app/domain/extraction.py, dan tidak pernah
mempercayai classification usulan begitu saja.

02 §4.5: "Jika tidak ada citation yang relevan, hasil otomatis AMBIGUOUS;
jangan mengizinkan model menyimpulkan IN_SCOPE/CHANGE_REQUEST tanpa dasar."
"""

from app.domain.canonical import validate_quote
from app.domain.enums import DomainError

CLASSIFICATIONS = frozenset({"IN_SCOPE", "AMBIGUOUS", "CHANGE_REQUEST"})


def citable_text(baseline):
    """{ref: teks} dari baseline aktif -- semua yang boleh dikutip untuk
    mendukung classification. ref criterion pakai criterion_key apa adanya
    (bisa langsung disambungkan ke effective_status); ref lain pakai
    "field[index]" supaya tetap stabil per baseline yang sama."""
    payload = baseline["canonical_payload"]
    text_by_ref = {key: c["text"] for key, c in payload["criteria"].items()}
    for i, item in enumerate(payload.get("out_of_scope") or []):
        text_by_ref["out_of_scope[%d]" % i] = item
    for i, item in enumerate(payload.get("deliverables") or []):
        if isinstance(item, dict):
            text_by_ref["deliverables[%d]" % i] = item.get("title", "")
    return text_by_ref


def classify(proposed_classification, citations, baseline_text_by_ref):
    """(classification_final, valid_citations).

    `citations`: list {"ref": str, "quote": str}. `baseline_text_by_ref`:
    hasil citable_text(baseline). Citation yang ref-nya tidak dikenal atau
    quote-nya tidak lolos validate_quote dibuang dari valid_citations --
    bukan error, supaya satu kutipan buruk tidak menggagalkan seluruh
    request; tapi kalau SEMUA kutipan gugur, IN_SCOPE/CHANGE_REQUEST turun
    jadi AMBIGUOUS (G-4 spirit: tidak ada kesimpulan tanpa dasar).
    """
    if proposed_classification not in CLASSIFICATIONS:
        raise DomainError("classification tidak dikenal: %r" % (proposed_classification,))

    valid = [
        c for c in citations
        if validate_quote(c.get("quote"), baseline_text_by_ref.get(c.get("ref")))
    ]

    if proposed_classification in ("IN_SCOPE", "CHANGE_REQUEST") and not valid:
        return "AMBIGUOUS", valid
    return proposed_classification, valid
