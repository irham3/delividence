"""Penyimpanan client link (02-ARCHITECTURE §8, model data §6 client_links/{token_hash}).

Token mentah tidak pernah disimpan -- hanya sha256 hash-nya, di collection
diberi nama persis oleh hash itu (bukan id acak terpisah), supaya lookup saat
resolve() adalah get-by-id, bukan query. Raw token hanya pernah keluar sekali,
dari issue(), dan MUST NOT ditaruh di log/audit event (02 §8) -- pemanggil
yang butuh menyebut link di audit event MUST pakai potongan hash lewat
actor_ref_for(), bukan token mentah.

Dual mode LOCAL/Firestore sama seperti app/store.py dan app/audit.py.
"""

import json
import os
import secrets
from datetime import datetime, timedelta, timezone

from app import config
from app.domain.canonical import sha256_hex
from app.domain.client_link import PURPOSES
from app.domain.enums import DomainError

# "Expiry pendek" (02 §8) tanpa angka pasti didokumentasikan -- 7 hari dipilih
# supaya cukup untuk klien yang tidak segera membuka email/chat, tapi masih
# pendek dibanding umur project.
DEFAULT_TTL_SECONDS = 7 * 24 * 3600

TOKEN_ENTROPY_BYTES = 16  # 128 bit, syarat minimum 02 §8


def _now():
    return datetime.now(timezone.utc)


def _hash(raw_token):
    return sha256_hex(raw_token.encode("utf-8"))


def actor_ref_for(raw_token):
    """actor_ref buat audit event (09 §7.1 contoh: "client_link:9c1f...") --
    potongan hash, bukan token mentah."""
    return "client_link:" + _hash(raw_token)[:8]


def _local_path(token_hash):
    d = os.path.join(config.LOCAL_DATA_DIR, "client_links")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, token_hash + ".json")


_db = None


def _client():
    global _db
    if _db is None:
        from google.cloud import firestore

        _db = firestore.Client(project=config.PROJECT_ID)
    return _db


def _read(token_hash):
    if config.LOCAL:
        try:
            with open(_local_path(token_hash), encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    snap = _client().collection("client_links").document(token_hash).get()
    return snap.to_dict() if snap.exists else None


def _write(token_hash, record):
    if config.LOCAL:
        with open(_local_path(token_hash), "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        return
    _client().collection("client_links").document(token_hash).set(record)


def _parse_dates(record):
    record = dict(record)
    record["expires_at"] = datetime.fromisoformat(record["expires_at"])
    for field in ("revoked_at", "completed_at"):
        record[field] = datetime.fromisoformat(record[field]) if record[field] else None
    return record


def issue(deal_id, purpose, allowed_actions, ttl_seconds=DEFAULT_TTL_SECONDS):
    """Buat link baru, kembalikan RAW token. Ini satu-satunya tempat raw
    token keluar dari sistem -- simpan hanya hash-nya."""
    if purpose not in PURPOSES:
        raise DomainError("purpose tidak dikenal: %r" % (purpose,))

    raw_token = secrets.token_urlsafe(TOKEN_ENTROPY_BYTES)
    record = {
        "deal_id": deal_id,
        "purpose": purpose,
        "allowed_actions": list(allowed_actions),
        "expires_at": (_now() + timedelta(seconds=ttl_seconds)).isoformat(),
        "revoked_at": None,
        "completed_at": None,
        "created_at": _now().isoformat(),
    }
    _write(_hash(raw_token), record)
    return raw_token


def resolve(raw_token):
    """RAW token -> record siap pakai app.domain.client_link.check (tanggal
    sudah jadi datetime aware), atau None kalau token tidak dikenal."""
    record = _read(_hash(raw_token))
    return _parse_dates(record) if record is not None else None


def revoke(raw_token):
    token_hash = _hash(raw_token)
    record = _read(token_hash)
    if record is None:
        return None
    record["revoked_at"] = _now().isoformat()
    _write(token_hash, record)
    return _parse_dates(record)


def mark_completed(raw_token):
    """Tandai purpose link ini selesai (02 §8: "berhenti valid setelah
    workflow purpose selesai"). Tidak menghapus record -- link yang sudah
    dipakai tetap tersimpan sebagai riwayat."""
    token_hash = _hash(raw_token)
    record = _read(token_hash)
    if record is None:
        return None
    record["completed_at"] = _now().isoformat()
    _write(token_hash, record)
    return _parse_dates(record)
