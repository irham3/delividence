"""Test aturan client link — 02-ARCHITECTURE §8.

Murni: `now` selalu parameter eksplisit, tidak ada mocking waktu.
"""

from datetime import datetime, timedelta, timezone

from app.domain import client_link

NOW = datetime(2026, 8, 26, 0, 0, 0, tzinfo=timezone.utc)


def link(**overrides):
    base = {
        "deal_id": "deal-1",
        "purpose": "CLARIFICATION",
        "allowed_actions": ["answer_question", "edit_ledger"],
        "expires_at": NOW + timedelta(days=7),
        "revoked_at": None,
        "completed_at": None,
    }
    base.update(overrides)
    return base


def test_link_valid_untuk_purpose_dan_action_yang_cocok():
    ok, reason = client_link.check(link(), NOW, "CLARIFICATION", "answer_question")
    assert ok is True
    assert reason == ""


def test_link_tidak_ada_ditolak():
    ok, reason = client_link.check(None, NOW, "CLARIFICATION", "answer_question")
    assert ok is False


def test_link_revoked_ditolak():
    ok, reason = client_link.check(
        link(revoked_at=NOW - timedelta(hours=1)), NOW, "CLARIFICATION", "answer_question"
    )
    assert ok is False
    assert "revoked" in reason


def test_link_sudah_selesai_ditolak():
    ok, reason = client_link.check(
        link(completed_at=NOW - timedelta(hours=1)), NOW, "CLARIFICATION", "answer_question"
    )
    assert ok is False
    assert "already been used" in reason


def test_link_kedaluwarsa_ditolak():
    ok, reason = client_link.check(
        link(expires_at=NOW - timedelta(seconds=1)), NOW, "CLARIFICATION", "answer_question"
    )
    assert ok is False
    assert "expired" in reason


def test_link_tepat_di_batas_expiry_dianggap_kedaluwarsa():
    """>= supaya tidak ada celah 'masih boleh' persis di detik expiry."""
    ok, _ = client_link.check(link(expires_at=NOW), NOW, "CLARIFICATION", "answer_question")
    assert ok is False


def test_purpose_salah_ditolak():
    ok, reason = client_link.check(link(), NOW, "APPROVAL", "answer_question")
    assert ok is False
    assert "not valid for this action" in reason


def test_action_tidak_diizinkan_ditolak():
    ok, reason = client_link.check(link(), NOW, "CLARIFICATION", "approve_baseline")
    assert ok is False
    assert "does not allow this action" in reason
