"""Penyimpanan evidence item (02-ARCHITECTURE §6:
deals/{deal_id}/evidence/{evidence_id}, "Evidence item" §5).

Scope MVP ini sengaja dipersempit ke `type` "url" dan "text" -- screenshot/
file upload butuh Cloud Storage, blocker yang sama dengan billing GCP (lihat
CATATAN-LANJUTAN.md). checksum/file metadata belum relevan tanpa file
sungguhan.

Dual mode LOCAL/Firestore sama seperti app/audit.py, app/baselines.py.
"""

import json
import os
import uuid
from datetime import datetime, timezone

from app import config
from app.domain.enums import DomainError

EVIDENCE_TYPES = frozenset({"url", "text"})


def _now():
    return datetime.now(timezone.utc).isoformat()


def _dir(deal_id):
    d = os.path.join(config.LOCAL_DATA_DIR, "deals", deal_id, "evidence")
    os.makedirs(d, exist_ok=True)
    return d


_db = None


def _client():
    global _db
    if _db is None:
        from google.cloud import firestore

        _db = firestore.Client(project=config.PROJECT_ID)
    return _db


def add(deal_id, criterion_key, type_, uri, caption=None, uploader_role="freelancer"):
    if type_ not in EVIDENCE_TYPES:
        raise DomainError("tipe evidence tidak dikenal: %r" % (type_,))

    record = {
        "evidence_id": "ev_" + uuid.uuid4().hex,
        "criterion_key": criterion_key,
        "type": type_,
        "uri": uri,
        "caption": caption,
        "uploader_role": uploader_role,
        "created_at": _now(),
    }
    if config.LOCAL:
        path = os.path.join(_dir(deal_id), record["evidence_id"] + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
    else:
        _client().collection("deals").document(deal_id).collection("evidence").document(
            record["evidence_id"]
        ).set(record)
    return record


def list_for_deal(deal_id):
    """Semua evidence untuk satu deal, terurut created_at asc."""
    if config.LOCAL:
        d = _dir(deal_id)
        if not os.path.isdir(d):
            return []
        items = []
        for name in os.listdir(d):
            if name.endswith(".json"):
                with open(os.path.join(d, name), encoding="utf-8") as f:
                    items.append(json.load(f))
        return sorted(items, key=lambda r: r["created_at"])
    docs = (
        _client().collection("deals").document(deal_id).collection("evidence").stream()
    )
    return sorted((d.to_dict() for d in docs), key=lambda r: r["created_at"])


def list_for_criterion(deal_id, criterion_key):
    return [e for e in list_for_deal(deal_id) if e["criterion_key"] == criterion_key]
