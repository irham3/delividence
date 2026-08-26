"""Test penyimpanan baseline — app/baselines.py.

Mode lokal saja (conftest.isolated_local_state). Firestore diverifikasi
lewat bentuk kode, sama seperti app/audit.py dan app/client_links.py.
"""

from app import baselines


def test_get_active_version_nol_kalau_belum_ada_baseline():
    assert baselines.get_active_version("deal-1") == 0


def test_create_lalu_get_active_version_naik():
    baselines.create(
        "deal-1", 1, {"deliverables": []}, "sha256:x", "client", "2026-08-26T00:00:00Z", 5
    )
    assert baselines.get_active_version("deal-1") == 1


def test_create_versi_lebih_tinggi_menang_di_get_active_version():
    baselines.create("deal-1", 1, {}, "sha256:a", "client", "t1", 1)
    baselines.create("deal-1", 2, {}, "sha256:b", "client", "t2", 9)
    assert baselines.get_active_version("deal-1") == 2


def test_get_mengembalikan_record_yang_disimpan():
    baselines.create(
        "deal-1", 1, {"deliverables": ["x"]}, "sha256:x", "client", "2026-08-26T00:00:00Z", 5
    )
    record = baselines.get("deal-1", 1)
    assert record["canonical_payload"] == {"deliverables": ["x"]}
    assert record["payload_hash"] == "sha256:x"
    assert record["approved_by"] == "client"
    assert record["activated_seq"] == 5
    assert record["status"] == "ACTIVE"


def test_get_versi_tidak_ada_none():
    assert baselines.get("deal-1", 1) is None


def test_deal_terpisah_tidak_saling_pengaruh():
    baselines.create("deal-a", 1, {}, "sha256:a", "client", "t", 1)
    assert baselines.get_active_version("deal-b") == 0


def test_get_all_up_to_mengembalikan_semua_versi_sampai_batas():
    baselines.create("deal-1", 1, {"v": 1}, "sha256:a", "client", "t1", 1)
    baselines.create("deal-1", 2, {"v": 2}, "sha256:b", "client", "t2", 9)
    all_versions = baselines.get_all_up_to("deal-1", 2)
    assert set(all_versions) == {1, 2}
    assert all_versions[1]["canonical_payload"] == {"v": 1}
    assert all_versions[2]["canonical_payload"] == {"v": 2}
