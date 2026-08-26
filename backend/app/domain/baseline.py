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


def build_canonical_payload(ledger, version, previous_criteria=None):
    """`ledger`: dict field ledger (bentuk {field: {value, state}, ...},
    lihat app.domain.schemas.DealLedger). `version`: nomor baseline yang
    sedang dibuat. `previous_criteria`: `canonical_payload["criteria"]` dari
    baseline v(n-1), atau None untuk v1.

    09 §2.6 A-7: criterion yang teksnya identik (text_hash sama) dengan
    versi sebelumnya MEMPERTAHANKAN introduced_in_version aslinya -- ia
    tidak "lahir ulang" hanya karena baseline naik versi. Criterion baru
    atau yang teksnya berubah (text_hash beda) dicap `version` sekarang;
    effective_status (app/domain/criteria.py) yang menentukan kalau teks
    berubah, acceptance lama jadi SUPERSEDED -- itu logika terpisah, bukan
    urusan introduced_in_version.
    """
    timeline = ledger.get("timeline") or {}
    revision_policy = ledger.get("revision_policy") or {}
    previous_criteria = previous_criteria or {}

    criteria = {}
    for item in _value_of(ledger.get("acceptance_criteria")) or []:
        text = item["text"]
        hash_ = text_hash(text)
        prev = previous_criteria.get(item["criterion_key"])
        introduced_in_version = (
            prev["introduced_in_version"] if prev and prev["text_hash"] == hash_ else version
        )
        criteria[item["criterion_key"]] = {
            "text": text,
            "text_hash": hash_,
            "introduced_in_version": introduced_in_version,
        }

    return {
        "deliverables": _value_of(ledger.get("deliverables")) or [],
        "in_scope": _value_of(ledger.get("in_scope")) or [],
        "out_of_scope": _value_of(ledger.get("out_of_scope")) or [],
        "timeline": {"final_deadline": _value_of(timeline.get("final_deadline"))},
        "revision_policy": {"rounds_total": _value_of(revision_policy.get("rounds_total"))},
        "criteria": criteria,
    }
