"""Test penyimpanan evidence item — app/evidence.py, 02-ARCHITECTURE §6/§5."""

import pytest

from app import evidence
from app.domain.enums import DomainError


def test_add_mengembalikan_record_dengan_id_dan_tipe():
    record = evidence.add("deal-1", "mobile-breakpoints", "url", "https://example.com/screenshot.png")
    assert record["evidence_id"].startswith("ev_")
    assert record["criterion_key"] == "mobile-breakpoints"
    assert record["type"] == "url"
    assert record["uri"] == "https://example.com/screenshot.png"


def test_tipe_tidak_dikenal_ditolak():
    with pytest.raises(DomainError):
        evidence.add("deal-1", "k1", "video", "https://example.com/x.mp4")


def test_list_for_deal_terurut_created_at():
    evidence.add("deal-1", "k1", "text", "Test passed.")
    evidence.add("deal-1", "k2", "url", "https://example.com")
    items = evidence.list_for_deal("deal-1")
    assert len(items) == 2
    assert items[0]["created_at"] <= items[1]["created_at"]


def test_list_for_deal_kosong():
    assert evidence.list_for_deal("deal-tidak-ada") == []


def test_list_for_criterion_memfilter_per_key():
    evidence.add("deal-1", "k1", "text", "a")
    evidence.add("deal-1", "k2", "text", "b")
    evidence.add("deal-1", "k1", "text", "c")
    items = evidence.list_for_criterion("deal-1", "k1")
    assert len(items) == 2
    assert all(e["criterion_key"] == "k1" for e in items)


def test_deal_terpisah_tidak_saling_pengaruh():
    evidence.add("deal-a", "k1", "text", "a")
    assert evidence.list_for_deal("deal-b") == []
