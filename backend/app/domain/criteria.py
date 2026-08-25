"""MODUL A — identitas criterion & versioning baseline (09-DOMAIN-RULES §2).

Fungsi murni, wajib deterministik. Tidak menyentuh Firestore, tidak menyentuh
waktu, tidak menyentuh model. Semua masukan berupa dict biasa supaya aturan ini
bisa diuji tanpa cloud sama sekali.

Kesalahan yang paling merusak dan paling mudah dibuat: menganggap naik versi
berarti semua acceptance hangus. Aturan di bawah sengaja dirancang supaya
acceptance hanya batal kalau teks criterion itu sendiri berubah.
"""

import re

from app.domain.enums import (
    ACCEPTED,
    CHANGES_REQUESTED,
    CRITERION_DECISIONS,
    PENDING,
    SUPERSEDED,
    WITHDRAWN,
    DomainError,
)

CRITERION_KEY_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CRITERION_KEY_MAX_LENGTH = 48


def validate_criterion_key(key):
    """§2.3. Boleh diusulkan model, tapi formatnya divalidasi service."""
    if not isinstance(key, str) or not CRITERION_KEY_PATTERN.match(key):
        raise DomainError("criterion_key tidak sesuai format: %r" % (key,))
    if len(key) > CRITERION_KEY_MAX_LENGTH:
        raise DomainError("criterion_key melebihi %d karakter" % CRITERION_KEY_MAX_LENGTH)
    return key


def _criteria_of(baselines, version):
    try:
        return baselines[version]["canonical_payload"]["criteria"]
    except KeyError:
        raise DomainError("baseline versi %r tidak ada" % (version,))


def effective_status(criterion_key, active_version, baselines, decisions):
    """§2.5. Status criterion selalu dihitung, tidak pernah disimpan.

    `baselines`: {version: {"canonical_payload": {"criteria": {key: {...}}}}}
    `decisions`: daftar event CRITERION_DECISION untuk deal ini. Setiap item
    memuat criterion_key, baseline_version, criterion_text_hash, decision, seq.
    """
    active = _criteria_of(baselines, active_version)

    if criterion_key not in active:
        # Pernah ada di versi sebelumnya berarti dicabut, bukan tidak dikenal.
        if any(
            criterion_key in _criteria_of(baselines, v)
            for v in baselines
            if v < active_version
        ):
            return WITHDRAWN
        raise DomainError("criterion_key tidak dikenal: %r" % (criterion_key,))

    current_hash = active[criterion_key]["text_hash"]

    relevant = sorted(
        (d for d in decisions if d["criterion_key"] == criterion_key),
        key=lambda d: d["seq"],
    )
    if not relevant:
        return PENDING

    last = relevant[-1]

    # Aturan jeda: kalau criterion pernah hilang setelah keputusan itu diambil,
    # keputusannya tidak hidup lagi. Keluar dari kesepakatan lalu kembali adalah
    # putus makna, bukan kelanjutan.
    for v in range(last["baseline_version"] + 1, active_version + 1):
        if v in baselines and criterion_key not in _criteria_of(baselines, v):
            return SUPERSEDED

    if last["criterion_text_hash"] != current_hash:
        return SUPERSEDED

    return last["decision"]


def can_record_decision(criterion_key, active_version, baselines, decisions, decision):
    """Gate tulis untuk invariant A-9.

    `ACCEPTED` bersifat final untuk pasangan `criterion_key + criterion_text_hash`.
    Permintaan perubahan berikutnya atas pasangan yang sama harus masuk Guardrail,
    bukan menimpa keputusan yang sudah ada.

    Mengembalikan (boleh, alasan). Alasan memakai bahasa netral (G-7): tidak ada
    pihak yang disalahkan.
    """
    if decision not in CRITERION_DECISIONS:
        raise DomainError("keputusan tidak dikenal: %r" % (decision,))

    status = effective_status(criterion_key, active_version, baselines, decisions)

    if status == ACCEPTED and decision == CHANGES_REQUESTED:
        return False, (
            "This criterion is already accepted for its current text. "
            "The request goes to scope review instead of replacing that decision."
        )
    if status == WITHDRAWN:
        return False, "This criterion is not part of the active baseline."
    return True, ""
