"""Test penyimpanan client link — app/client_links.py, 02-ARCHITECTURE §8.

Mode lokal saja (conftest.isolated_local_state). Firestore diverifikasi lewat
bentuk kode, bukan dites di sini -- sama seperti app/audit.py.
"""

import os

import pytest

from app import client_links, config
from app.domain.client_link import check
from app.domain.enums import DomainError


def test_issue_mengembalikan_token_beda_tiap_kali():
    a = client_links.issue("deal-1", "CLARIFICATION", ["answer_question"])
    b = client_links.issue("deal-1", "CLARIFICATION", ["answer_question"])
    assert a != b
    assert len(a) >= 20  # 128 bit base64url tanpa padding -> ~22 karakter


def test_purpose_tidak_dikenal_ditolak():
    with pytest.raises(DomainError):
        client_links.issue("deal-1", "NOT_A_PURPOSE", ["answer_question"])


def test_resolve_mengembalikan_record_yang_sesuai():
    token = client_links.issue("deal-1", "CLARIFICATION", ["answer_question"], ttl_seconds=3600)
    record = client_links.resolve(token)
    assert record["deal_id"] == "deal-1"
    assert record["purpose"] == "CLARIFICATION"
    assert record["allowed_actions"] == ["answer_question"]
    assert record["revoked_at"] is None
    assert record["completed_at"] is None


def test_resolve_token_tidak_dikenal_none():
    assert client_links.resolve("token-yang-tidak-pernah-diterbitkan") is None


def test_raw_token_tidak_pernah_ditulis_ke_penyimpanan():
    """02 §8: hanya hash yang disimpan. Baca file mentahnya langsung -- raw
    token MUST NOT muncul di dalamnya sama sekali."""
    token = client_links.issue("deal-1", "CLARIFICATION", ["answer_question"])

    d = os.path.join(config.LOCAL_DATA_DIR, "client_links")
    contents = []
    for name in os.listdir(d):
        with open(os.path.join(d, name), encoding="utf-8") as f:
            contents.append(f.read())

    assert len(contents) == 1
    assert token not in contents[0]


def test_revoke_membuat_link_tidak_lagi_valid():
    token = client_links.issue("deal-1", "CLARIFICATION", ["answer_question"])
    client_links.revoke(token)

    record = client_links.resolve(token)
    assert record["revoked_at"] is not None

    import datetime

    ok, _ = check(record, datetime.datetime.now(datetime.timezone.utc), "CLARIFICATION", "answer_question")
    assert ok is False


def test_mark_completed_membuat_link_tidak_lagi_valid():
    token = client_links.issue("deal-1", "CLARIFICATION", ["answer_question"])
    client_links.mark_completed(token)

    record = client_links.resolve(token)
    assert record["completed_at"] is not None


def test_revoke_token_tidak_dikenal_none():
    assert client_links.revoke("tidak-pernah-ada") is None


def test_actor_ref_for_tidak_memuat_raw_token():
    token = client_links.issue("deal-1", "CLARIFICATION", ["answer_question"])
    ref = client_links.actor_ref_for(token)
    assert ref.startswith("client_link:")
    assert token not in ref


def test_actor_ref_for_deterministik_untuk_token_yang_sama():
    token = client_links.issue("deal-1", "CLARIFICATION", ["answer_question"])
    assert client_links.actor_ref_for(token) == client_links.actor_ref_for(token)
