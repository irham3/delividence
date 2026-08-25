"""Test service penulis audit event — 09-DOMAIN-RULES §7, §10 butir 3.

Mode lokal saja (lihat conftest.isolated_local_state); jalur Firestore
diverifikasi lewat bentuk transaksi, bukan dites di sini.
"""

import pytest

from app import audit
from app.domain.enums import DomainError


def test_seq_dimulai_dari_1_dan_naik_per_deal():
    e1 = audit.append_event("deal-1", "DEAL_CREATED", "system", 0, {})
    e2 = audit.append_event("deal-1", "ARTIFACT_ADDED", "freelancer", 0, {})
    assert e1["seq"] == 1
    assert e2["seq"] == 2


def test_seq_terpisah_per_deal():
    a = audit.append_event("deal-a", "DEAL_CREATED", "system", 0, {})
    b = audit.append_event("deal-b", "DEAL_CREATED", "system", 0, {})
    assert a["seq"] == 1
    assert b["seq"] == 1


def test_envelope_memuat_field_wajib():
    e = audit.append_event(
        "deal-1", "CRITERION_DECISION", "client", 1, {"decision": "ACCEPTED"},
        actor_ref="client_link:abc",
    )
    assert e["event_id"].startswith("evt_")
    assert e["type"] == "CRITERION_DECISION"
    assert e["actor"] == "client"
    assert e["actor_ref"] == "client_link:abc"
    assert e["baseline_version"] == 1
    assert e["payload"] == {"decision": "ACCEPTED"}
    assert e["seq"] == 1
    assert "created_at" in e


def test_tipe_event_tidak_dikenal_ditolak():
    with pytest.raises(DomainError):
        audit.append_event("deal-1", "NOT_A_REAL_TYPE", "system", 0, {})


def test_tipe_event_yang_dinonaktifkan_ditolak():
    """Modul B/C dilepas pada profil ini (10 §4b) — event-nya tidak boleh ditulis."""
    with pytest.raises(DomainError):
        audit.append_event("deal-1", "REVISION_ROUND_CONSUMED", "system", 1, {})


def test_actor_tidak_dikenal_ditolak():
    with pytest.raises(DomainError):
        audit.append_event("deal-1", "DEAL_CREATED", "nobody", 0, {})


def test_baseline_version_wajib_g6():
    with pytest.raises(DomainError):
        audit.append_event("deal-1", "DEAL_CREATED", "system", None, {})


def test_list_events_terurut_seq_asc():
    audit.append_event("deal-1", "DEAL_CREATED", "system", 0, {"n": 1})
    audit.append_event("deal-1", "ARTIFACT_ADDED", "freelancer", 0, {"n": 2})
    audit.append_event("deal-1", "LEDGER_DRAFT_SAVED", "model", 0, {"n": 3})

    events = audit.list_events("deal-1")
    assert [e["payload"]["n"] for e in events] == [1, 2, 3]
    assert [e["seq"] for e in events] == [1, 2, 3]


def test_list_events_deal_kosong():
    assert audit.list_events("deal-tidak-ada") == []


def test_event_tidak_pernah_ditimpa_g2():
    """Append-only: dua event beruntun tidak saling menimpa file satu sama lain."""
    audit.append_event("deal-1", "DEAL_CREATED", "system", 0, {"n": 1})
    audit.append_event("deal-1", "ARTIFACT_ADDED", "freelancer", 0, {"n": 2})
    events = audit.list_events("deal-1")
    assert len(events) == 2
    assert events[0]["event_id"] != events[1]["event_id"]
