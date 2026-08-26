"""Terapkan jawaban langsung ke ledger -- klien mengoreksi critical-field
summary lewat portal (01 §4.1), atau freelancer mengusulkan perubahan scope
setelah CHANGE_REQUEST dikonfirmasi Guardrail (01 §5 langkah 8).

State CLIENT_STATED atau FREELANCER_POLICY -- ini input langsung lewat
form, bukan klaim model yang butuh validate_quote terhadap artifact (beda
dari app/domain/extraction.py, yang memproyeksikan kandidat model).
"""

from app.domain.enums import CLIENT_STATED


def apply_client_answer(ledger, field_path, value, state=CLIENT_STATED):
    """Set satu field ledger (path bertitik, mis. "timeline.final_deadline")
    ke `value`. Mengubah `ledger` in-place dan mengembalikannya, supaya
    pemanggil bisa memanggil berkali-kali sebelum menyimpan hasil akhirnya."""
    *parents, leaf = field_path.split(".")
    node = ledger
    for part in parents:
        node = node.setdefault(part, {})
    node[leaf] = {"value": value, "state": state}
    return ledger
