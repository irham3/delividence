"""Preference lintas-deal milik freelancer.

Ini bukan fakta klien dan bukan baseline. Ia hanya menyiapkan policy candidate
untuk deal baru, yang nanti tetap dapat dikalahkan oleh pernyataan eksplisit
klien dan hanya menjadi AGREED lewat approval baseline biasa.
"""

import hashlib
import json
import os
from datetime import datetime, timezone

from app import config


def _now():
    return datetime.now(timezone.utc).isoformat()


def _doc_id(owner_id):
    return hashlib.sha256(owner_id.encode("utf-8")).hexdigest()


def _local_path(owner_id):
    directory = os.path.join(config.LOCAL_DATA_DIR, "preferences")
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, _doc_id(owner_id) + ".json")


def get(owner_id):
    if config.LOCAL:
        try:
            with open(_local_path(owner_id), encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    from app import store

    snapshot = store._client().collection("owner_preferences").document(_doc_id(owner_id)).get()
    return snapshot.to_dict() if snapshot.exists else None


def confirm_revision_rounds(owner_id, rounds):
    """Simpan satu preference yang eksplisit dikonfirmasi oleh owner."""
    record = {
        "owner_id_hash": _doc_id(owner_id),
        "revision_rounds": rounds,
        "status": "CONFIRMED",
        "confirmed_at": _now(),
        "updated_at": _now(),
    }
    if config.LOCAL:
        with open(_local_path(owner_id), "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
    else:
        from app import store

        store._client().collection("owner_preferences").document(_doc_id(owner_id)).set(record)
    return record


def candidate_for_new_run(owner_id):
    """Bentuk minimum yang aman untuk disimpan pada run baru."""
    preference = get(owner_id)
    if not preference or preference.get("status") != "CONFIRMED":
        return None
    return {
        "revision_rounds": preference["revision_rounds"],
        "confirmed_at": preference["confirmed_at"],
    }
