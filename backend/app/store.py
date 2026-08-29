"""State run + klaim job.

Idempotensi ditegakkan lewat pembuatan dokumen job yang create-only dan berkunci
`{run_id}:{round}` — bukan lewat field `idempotency_key` yang tidak menegakkan
apa pun. Pub/Sub menjamin at-least-once, jadi pengiriman ganda pasti terjadi.
"""

import json
import os
from datetime import datetime, timezone

from app import config


def _now():
    return datetime.now(timezone.utc).isoformat()


# --- Firestore -------------------------------------------------------------

_db = None


def _client():
    global _db
    if _db is None:
        from google.cloud import firestore

        _db = firestore.Client(project=config.PROJECT_ID)
    return _db


# --- Lokal -----------------------------------------------------------------


def _local_path(kind, name):
    d = os.path.join(config.LOCAL_DATA_DIR, kind)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, name + ".json")


def _local_write(kind, name, doc):
    with open(_local_path(kind, name), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)


def _local_read(kind, name):
    try:
        with open(_local_path(kind, name), encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


# --- API ------------------------------------------------------------------


def create_run(run_id, owner_id, brief, output_language, preference_candidate=None):
    doc = {
        "run_id": run_id,
        "owner_id": owner_id,
        "status": "queued",
        "output_language": output_language,
        "brief": brief,
        "round": 0,
        "audit_trail": [],
        # deal_id == run_id (lihat api.py) -- ledger draft hidup di sini
        # sampai ada alasan nyata untuk memisahkannya ke collection sendiri.
        "ledger": {},
        "preference_candidate": preference_candidate,
        "created_at": _now(),
        "updated_at": _now(),
    }
    if config.LOCAL:
        _local_write("runs", run_id, doc)
    else:
        _client().collection("runs").document(run_id).set(doc)
    return doc


def get_run(run_id):
    if config.LOCAL:
        return _local_read("runs", run_id)
    snap = _client().collection("runs").document(run_id).get()
    return snap.to_dict() if snap.exists else None


def list_runs(owner_id):
    """Semua deal milik satu freelancer, terbaru lebih dulu.

    Ini adalah read model untuk workspace/records. Ia sengaja hanya membaca
    dokumen run yang sudah dimiliki owner yang terautentikasi; route API tetap
    menyembunyikan keberadaan run milik owner lain.
    """
    if config.LOCAL:
        directory = os.path.join(config.LOCAL_DATA_DIR, "runs")
        if not os.path.isdir(directory):
            return []
        items = []
        for name in os.listdir(directory):
            if not name.endswith(".json"):
                continue
            with open(os.path.join(directory, name), encoding="utf-8") as f:
                record = json.load(f)
            if record.get("owner_id") == owner_id:
                items.append(record)
        return sorted(items, key=lambda item: item.get("updated_at", ""), reverse=True)

    # Urutannya sengaja dikerjakan di Python, bukan lewat .order_by() Firestore:
    # equality filter di `owner_id` + order_by field lain (`updated_at`) menuntut
    # composite index yang harus dibuat lebih dulu, dan query-nya gagal total
    # (FailedPrecondition 400) selama index itu belum ada. Deployment baru --
    # termasuk juri yang men-deploy ke project sendiri -- tidak akan punya index
    # itu, jadi ketergantungannya dihapus. Satu freelancer hanya punya sedikit
    # deal, sehingga sort in-memory di sini setara dan tidak butuh infra apa pun.
    # Cabang LOCAL di atas sudah memakai kunci sort yang sama.
    docs = _client().collection("runs").where("owner_id", "==", owner_id).stream()
    items = [doc.to_dict() for doc in docs]
    return sorted(items, key=lambda item: item.get("updated_at") or "", reverse=True)


def update_run(run_id, **fields):
    fields["updated_at"] = _now()
    if config.LOCAL:
        doc = _local_read("runs", run_id)
        if doc is None:
            return None
        doc.update(fields)
        _local_write("runs", run_id, doc)
        return doc
    ref = _client().collection("runs").document(run_id)
    ref.update(fields)
    return ref.get().to_dict()


def append_audit_step(run_id, step, detail):
    """Satu langkah di jejak audit. Isinya keputusan & hasil tool, bukan prompt."""
    entry = {"at": _now(), "step": step, "detail": detail}
    if config.LOCAL:
        doc = _local_read("runs", run_id)
        if doc is None:
            return None
        doc.setdefault("audit_trail", []).append(entry)
        doc["updated_at"] = _now()
        _local_write("runs", run_id, doc)
        return entry
    from google.cloud import firestore

    self_ref = _client().collection("runs").document(run_id)
    self_ref.update(
        {"audit_trail": firestore.ArrayUnion([entry]), "updated_at": _now()}
    )
    return entry


def claim_job(run_id, round_no):
    """True kalau pengiriman ini yang berhak memproses; False kalau duplikat.

    Kunci menyertakan `round` supaya putaran berikutnya dari jawaban klien tidak
    ikut tertekan sebagai duplikat.
    """
    job_id = "%s__%s" % (run_id, round_no)
    doc = {"run_id": run_id, "round": round_no, "claimed_at": _now()}

    if config.LOCAL:
        path = _local_path("jobs", job_id)
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return False
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        return True

    from google.api_core.exceptions import AlreadyExists

    try:
        _client().collection("jobs").document(job_id).create(doc)
        return True
    except AlreadyExists:
        return False
