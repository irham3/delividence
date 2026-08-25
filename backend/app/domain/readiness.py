"""Gate readiness deterministik (01 §7, field kritis 09-DOMAIN-RULES §5.7).

Readiness bukan angka yang dikarang model. Fungsi ini tidak pernah memanggil
LLM. Agent boleh menjelaskan gate yang gagal; ia tidak boleh mengubah hasilnya —
dijamin karena tidak ada tool yang menulis ke sini.
"""

from app.domain.enums import (
    CONFLICTING,
    CRITICAL_FIELDS,
    MISSING,
    PROPOSED,
    SATISFYING_STATES,
)


def _get_field(ledger, path):
    """Ambil field ledger dengan path bertitik, mis. `timeline.final_deadline`."""
    node = ledger
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def _blocker(field, reason):
    return {"field": field, "reason": reason}


def evaluate(ledger):
    """Kembalikan (ready, blockers).

    `ledger` memetakan nama field ke {"state": ..., "value": ...}. Field kritis
    yang tidak ada diperlakukan sama dengan MISSING — tidak ada bedanya bagi
    klien, dan membedakannya hanya menambah cara gagal.
    """
    blockers = []

    for path in CRITICAL_FIELDS:
        field = _get_field(ledger, path)

        if not isinstance(field, dict) or "state" not in field:
            blockers.append(_blocker(path, "No information yet."))
            continue

        state = field["state"]
        if state == CONFLICTING:
            # Modul D dilepas pada profil ini, jadi konflik hanya memblokir dan
            # ditampilkan apa adanya. Tidak ada resolusi otomatis (G-4).
            blockers.append(
                _blocker(path, "Two sources disagree. The client needs to settle this.")
            )
        elif state == MISSING:
            blockers.append(_blocker(path, "No information yet."))
        elif state == PROPOSED:
            blockers.append(
                _blocker(path, "Suggested but not confirmed by a person yet.")
            )
        elif state not in SATISFYING_STATES:
            blockers.append(_blocker(path, "Unrecognised state: %s" % state))

    blockers.extend(_deliverable_blockers(ledger))
    return (not blockers), blockers


def _deliverable_blockers(ledger):
    """Minimal satu deliverable, dan tiap deliverable punya minimal satu criterion."""
    out = []

    deliverables_field = _get_field(ledger, "deliverables")
    deliverables = (deliverables_field or {}).get("value") or []
    if not isinstance(deliverables, list) or not deliverables:
        out.append(_blocker("deliverables", "At least one deliverable is required."))
        return out

    criteria_field = _get_field(ledger, "acceptance_criteria")
    criteria = (criteria_field or {}).get("value") or []
    covered = {
        c.get("deliverable_id") for c in criteria if isinstance(c, dict)
    }

    for item in deliverables:
        if not isinstance(item, dict):
            continue
        if item.get("id") not in covered:
            out.append(
                _blocker(
                    "acceptance_criteria",
                    'Deliverable "%s" has no acceptance criterion yet.'
                    % item.get("title", item.get("id")),
                )
            )
    return out
