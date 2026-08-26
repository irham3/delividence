"""Penyimpanan request baru -- Guardrail (02-ARCHITECTURE §6:
deals/{deal_id}/requests/{request_id}).

Nama modul sengaja `scope_requests`, bukan `requests` -- itu nama paket HTTP
yang sangat umum, tabrakan nama akan membingungkan siapa pun yang membaca
import.

`change_draft_id` dari bentuk data 02 §6 sengaja tidak ada di sini --
CHANGE_REQUEST yang menghasilkan baseline versi baru (v2) belum dibangun,
lihat catatan `introduced_in_version` di app/domain/baseline.py.

Dual mode LOCAL/Firestore sama seperti app/evidence.py, app/baselines.py.
"""

import json
import os
import uuid
from datetime import datetime, timezone

from app import config


def _now():
    return datetime.now(timezone.utc).isoformat()


def _dir(deal_id):
    d = os.path.join(config.LOCAL_DATA_DIR, "deals", deal_id, "requests")
    os.makedirs(d, exist_ok=True)
    return d


_db = None


def _client():
    global _db
    if _db is None:
        from google.cloud import firestore

        _db = firestore.Client(project=config.PROJECT_ID)
    return _db


def _write(deal_id, record):
    if config.LOCAL:
        path = os.path.join(_dir(deal_id), record["request_id"] + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
    else:
        _client().collection("deals").document(deal_id).collection("requests").document(
            record["request_id"]
        ).set(record)
    return record


def submit(deal_id, raw_text, submitted_by):
    record = {
        "request_id": "req_" + uuid.uuid4().hex,
        "raw_text": raw_text,
        "submitted_by": submitted_by,
        "confirmed_classification": None,
        "citations": [],
        "created_at": _now(),
        "decided_at": None,
    }
    return _write(deal_id, record)


def get(deal_id, request_id):
    if config.LOCAL:
        path = os.path.join(_dir(deal_id), request_id + ".json")
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    snap = (
        _client()
        .collection("deals")
        .document(deal_id)
        .collection("requests")
        .document(request_id)
        .get()
    )
    return snap.to_dict() if snap.exists else None


def mark_classified(deal_id, request_id, classification, citations):
    record = get(deal_id, request_id)
    if record is None:
        return None
    record["confirmed_classification"] = classification
    record["citations"] = citations
    record["decided_at"] = _now()
    return _write(deal_id, record)


def list_for_deal(deal_id):
    """Semua request untuk satu deal, terurut created_at asc."""
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
        _client().collection("deals").document(deal_id).collection("requests").stream()
    )
    return sorted((d.to_dict() for d in docs), key=lambda r: r["created_at"])
