"""Bangun canonical_payload baseline dari ledger draft (09-DOMAIN-RULES §2.3,
"Approved snapshot" 02-ARCHITECTURE §5).

Fungsi murni: tidak menghitung hash sendiri (itu app.domain.canonical), tidak
menyentuh waktu/Firestore. Hanya membentuk struktur. Readiness gate
(app.domain.readiness) MUST sudah dicek lolos oleh pemanggil sebelum baseline
dibangun -- fungsi ini tidak mengecek ulang, supaya tidak ada dua tempat yang
bisa berbeda pendapat soal readiness.
"""

from app.domain.canonical import text_hash


def _value_of(field):
    return field.get("value") if isinstance(field, dict) else None


def build_canonical_payload(ledger, version):
    """`ledger`: dict field ledger (bentuk {field: {value, state}, ...},
    lihat app.domain.schemas.DealLedger). `version`: nomor baseline yang
    sedang dibuat.

    Dipakai sebagai introduced_in_version tiap criterion. Ini benar untuk
    baseline pertama (semua criterion memang "lahir" di v1). Kalau nanti
    change-request/re-approval (v2+) dibangun, fungsi ini MUST diperbarui
    supaya criterion yang sudah ada di v(n-1) mempertahankan
    introduced_in_version aslinya, bukan ditimpa jadi versi baru -- lihat 09
    §2.6 A-7. Belum ada jalur kode yang membuat v2, jadi belum ditangani di
    sini.
    """
    timeline = ledger.get("timeline") or {}
    revision_policy = ledger.get("revision_policy") or {}

    criteria = {}
    for item in _value_of(ledger.get("acceptance_criteria")) or []:
        text = item["text"]
        criteria[item["criterion_key"]] = {
            "text": text,
            "text_hash": text_hash(text),
            "introduced_in_version": version,
        }

    return {
        "deliverables": _value_of(ledger.get("deliverables")) or [],
        "in_scope": _value_of(ledger.get("in_scope")) or [],
        "out_of_scope": _value_of(ledger.get("out_of_scope")) or [],
        "timeline": {"final_deadline": _value_of(timeline.get("final_deadline"))},
        "revision_policy": {"rounds_total": _value_of(revision_policy.get("rounds_total"))},
        "criteria": criteria,
    }
