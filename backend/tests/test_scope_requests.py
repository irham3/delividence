"""Test penyimpanan request Guardrail — app/scope_requests.py."""

from app import scope_requests


def test_submit_mengembalikan_record_belum_terklasifikasi():
    record = scope_requests.submit("deal-1", "Bisa tambah ikon sosial di footer?", "freelancer")
    assert record["request_id"].startswith("req_")
    assert record["raw_text"] == "Bisa tambah ikon sosial di footer?"
    assert record["confirmed_classification"] is None
    assert record["citations"] == []


def test_get_mengembalikan_record_yang_disimpan():
    submitted = scope_requests.submit("deal-1", "teks", "client")
    fetched = scope_requests.get("deal-1", submitted["request_id"])
    assert fetched == submitted


def test_get_request_tidak_ada_none():
    assert scope_requests.get("deal-1", "req_tidak-ada") is None


def test_mark_classified_mengisi_classification_dan_citations():
    submitted = scope_requests.submit("deal-1", "teks", "freelancer")
    updated = scope_requests.mark_classified(
        "deal-1", submitted["request_id"], "IN_SCOPE", [{"ref": "k1", "quote": "x"}]
    )
    assert updated["confirmed_classification"] == "IN_SCOPE"
    assert updated["citations"] == [{"ref": "k1", "quote": "x"}]
    assert updated["decided_at"] is not None


def test_mark_classified_request_tidak_ada_none():
    assert scope_requests.mark_classified("deal-1", "req_tidak-ada", "IN_SCOPE", []) is None


def test_list_for_deal_terurut_dan_terfilter_per_deal():
    scope_requests.submit("deal-1", "a", "freelancer")
    scope_requests.submit("deal-1", "b", "client")
    scope_requests.submit("deal-2", "c", "freelancer")
    items = scope_requests.list_for_deal("deal-1")
    assert len(items) == 2
    # created_at bisa seri (dua submit dalam microsecond yang sama) -- cek
    # isinya, bukan urutan tie-break-nya. list_for_criterion di evidence.py
    # punya keterbatasan display-order yang sama, sengaja tidak diperketat.
    assert {i["raw_text"] for i in items} == {"a", "b"}
    assert items[0]["created_at"] <= items[1]["created_at"]


def test_list_for_deal_kosong():
    assert scope_requests.list_for_deal("deal-tidak-ada") == []
