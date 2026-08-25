"""Audit event log — satu pemilik untuk alokasi seq (09-DOMAIN-RULES §7, §10 butir 3).

Seluruh sistem memakai satu collection append-only: deals/{deal_id}/audit/{event_id}.
seq dialokasikan dari deals/{deal_id}.audit_seq dalam transaksi yang sama dengan
penulisan event — bukan dari created_at. Modul lain MUST NOT menulis ke
collection audit langsung atau mengimplementasikan alokasi seq sendiri; panggil
append_event() di sini.
"""

import json
import os
import uuid
from datetime import datetime, timezone

from app import config
from app.domain.enums import ACTORS, AUDIT_EVENT_TYPES, DISABLED_EVENT_TYPES, DomainError


def _now():
    return datetime.now(timezone.utc).isoformat()


def _new_event_id():
    return "evt_" + uuid.uuid4().hex


def _validate(event_type, actor, baseline_version):
    # G-6: setiap keputusan mencatat baseline_version + actor + seq. seq kami
    # alokasikan sendiri; dua lainnya wajib dari pemanggil dan ditolak di sini
    # kalau tidak ada.
    if event_type not in AUDIT_EVENT_TYPES:
        raise DomainError("tipe event tidak dikenal: %r" % (event_type,))
    if event_type in DISABLED_EVENT_TYPES:
        raise DomainError("tipe event dinonaktifkan pada profil ini: %r" % (event_type,))
    if actor not in ACTORS:
        raise DomainError("actor tidak dikenal: %r" % (actor,))
    if baseline_version is None:
        raise DomainError("baseline_version wajib diisi (G-6)")


# --- Firestore ---------------------------------------------------------------

_db = None


def _client():
    global _db
    if _db is None:
        from google.cloud import firestore

        _db = firestore.Client(project=config.PROJECT_ID)
    return _db


def _append_event_firestore(deal_id, envelope_base):
    from google.cloud import firestore

    client = _client()
    deal_ref = client.collection("deals").document(deal_id)
    event_ref = deal_ref.collection("audit").document(envelope_base["event_id"])

    @firestore.transactional
    def _txn(transaction):
        snap = deal_ref.get(transaction=transaction)
        seq = (snap.get("audit_seq") if snap.exists else 0) + 1
        envelope = dict(envelope_base, seq=seq)
        transaction.set(deal_ref, {"audit_seq": seq, "updated_at": _now()}, merge=True)
        transaction.set(event_ref, envelope)
        return envelope

    return _txn(client.transaction())


def _list_events_firestore(deal_id):
    client = _client()
    docs = (
        client.collection("deals")
        .document(deal_id)
        .collection("audit")
        .order_by("seq")
        .stream()
    )
    return [d.to_dict() for d in docs]


# --- Lokal ---------------------------------------------------------------

_local_lock = None


def _lock():
    global _local_lock
    if _local_lock is None:
        import threading

        _local_lock = threading.Lock()
    return _local_lock


def _deal_path(deal_id):
    d = os.path.join(config.LOCAL_DATA_DIR, "deals")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, deal_id + ".json")


def _audit_dir(deal_id):
    d = os.path.join(config.LOCAL_DATA_DIR, "deals", deal_id, "audit")
    os.makedirs(d, exist_ok=True)
    return d


def _read_deal_local(deal_id):
    try:
        with open(_deal_path(deal_id), encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def _append_event_local(deal_id, envelope_base):
    # Satu proses lokal (dev/test) — kunci in-process cukup untuk mencegah dua
    # request bersamaan membaca audit_seq yang sama sebelum salah satunya
    # menulis kembali.
    with _lock():
        deal = _read_deal_local(deal_id) or {"deal_id": deal_id, "audit_seq": 0}
        seq = deal["audit_seq"] + 1
        deal["audit_seq"] = seq
        deal["updated_at"] = _now()
        with open(_deal_path(deal_id), "w", encoding="utf-8") as f:
            json.dump(deal, f, ensure_ascii=False, indent=2)

        envelope = dict(envelope_base, seq=seq)
        event_path = os.path.join(_audit_dir(deal_id), envelope["event_id"] + ".json")
        with open(event_path, "w", encoding="utf-8") as f:
            json.dump(envelope, f, ensure_ascii=False, indent=2)
        return envelope


def _list_events_local(deal_id):
    d = os.path.join(config.LOCAL_DATA_DIR, "deals", deal_id, "audit")
    if not os.path.isdir(d):
        return []
    events = []
    for name in sorted(os.listdir(d)):
        if name.endswith(".json"):
            with open(os.path.join(d, name), encoding="utf-8") as f:
                events.append(json.load(f))
    return sorted(events, key=lambda e: e["seq"])


# --- API -----------------------------------------------------------------


def append_event(deal_id, event_type, actor, baseline_version, payload, actor_ref=None):
    """Menulis satu event dan mengembalikan envelope lengkap (§7.1), seq terisi.

    payload MUST JSON-serializable; envelope tidak pernah di-update atau
    dihapus setelah ditulis (G-2).
    """
    _validate(event_type, actor, baseline_version)

    envelope_base = {
        "event_id": _new_event_id(),
        "type": event_type,
        "actor": actor,
        "actor_ref": actor_ref,
        "baseline_version": baseline_version,
        "created_at": _now(),
        "payload": payload,
    }

    if config.LOCAL:
        return _append_event_local(deal_id, envelope_base)
    return _append_event_firestore(deal_id, envelope_base)


def list_events(deal_id):
    """Semua event untuk satu deal, terurut seq asc — urutan yang sama dipakai
    semua modul (09-DOMAIN-RULES §6: "Semua modul membaca seq yang sama")."""
    if config.LOCAL:
        return _list_events_local(deal_id)
    return _list_events_firestore(deal_id)
