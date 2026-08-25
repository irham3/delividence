"""Penyimpanan baseline -- append-only (02-ARCHITECTURE §6:
deals/{deal_id}/baselines/{version_id}, 09-DOMAIN-RULES A-3: "Baseline
immutable setelah BASELINE_ACTIVATED. Perubahan apa pun MUST lewat versi
baru.").

create() tidak pernah menimpa versi yang sudah ada -- pemanggil MUST
menghitung nomor versi baru lewat get_active_version() + 1 sebelum memanggil
ini. Dual mode LOCAL/Firestore sama seperti app/audit.py dan
app/client_links.py.
"""

import json
import os
from datetime import datetime, timezone

from app import config


def _now():
    return datetime.now(timezone.utc).isoformat()


def _dir(deal_id):
    d = os.path.join(config.LOCAL_DATA_DIR, "deals", deal_id, "baselines")
    os.makedirs(d, exist_ok=True)
    return d


_db = None


def _client():
    global _db
    if _db is None:
        from google.cloud import firestore

        _db = firestore.Client(project=config.PROJECT_ID)
    return _db


def get_active_version(deal_id):
    """Nomor versi baseline aktif untuk deal, atau 0 kalau belum pernah ada
    baseline sama sekali (dipakai buat menghitung nomor versi berikutnya:
    get_active_version(deal_id) + 1)."""
    if config.LOCAL:
        d = _dir(deal_id)
        versions = [int(name[:-5]) for name in os.listdir(d) if name.endswith(".json")]
        return max(versions, default=0)
    docs = (
        _client().collection("deals").document(deal_id).collection("baselines").stream()
    )
    versions = [int(doc.id) for doc in docs]
    return max(versions, default=0)


def create(deal_id, version, canonical_payload, payload_hash, approved_by, approved_at, activated_seq):
    record = {
        "version": version,
        "status": "ACTIVE",
        "canonical_payload": canonical_payload,
        "payload_hash": payload_hash,
        "approved_by": approved_by,
        "approved_at": approved_at,
        "activated_seq": activated_seq,
        "created_at": _now(),
    }
    if config.LOCAL:
        path = os.path.join(_dir(deal_id), "%d.json" % version)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
    else:
        ref = (
            _client()
            .collection("deals")
            .document(deal_id)
            .collection("baselines")
            .document(str(version))
        )
        ref.set(record)
    return record


def get(deal_id, version):
    if config.LOCAL:
        path = os.path.join(_dir(deal_id), "%d.json" % version)
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    snap = (
        _client()
        .collection("deals")
        .document(deal_id)
        .collection("baselines")
        .document(str(version))
        .get()
    )
    return snap.to_dict() if snap.exists else None
