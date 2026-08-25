"""Terapkan jawaban langsung klien ke ledger (01 §4.1: klien mengoreksi
critical-field summary lewat portal, bukan lewat ekstraksi model).

State selalu CLIENT_STATED -- ini input langsung dari klien lewat form, bukan
klaim model yang butuh validate_quote terhadap artifact (beda dari
app/domain/extraction.py, yang memproyeksikan kandidat model).
"""

from app.domain.enums import CLIENT_STATED


def apply_client_answer(ledger, field_path, value):
    """Set satu field ledger (path bertitik, mis. "timeline.final_deadline")
    ke `value`, state CLIENT_STATED. Mengubah `ledger` in-place dan
    mengembalikannya, supaya pemanggil bisa memanggil berkali-kali sebelum
    menyimpan hasil akhirnya."""
    *parents, leaf = field_path.split(".")
    node = ledger
    for part in parents:
        node = node.setdefault(part, {})
    node[leaf] = {"value": value, "state": CLIENT_STATED}
    return ledger
