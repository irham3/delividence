"""Test ranking clarification questions — 02-ARCHITECTURE §4.4.

Modul D (forced-slot untuk CONFLICTING) dilepas pada profil ini -- lihat
docstring app/domain/questions.py. Test di sini hanya menutup ranking umum.
"""

from app.domain import questions


def q(text, scope=0, acceptance=0, schedule=0, conflict=0):
    return {
        "text": text,
        "scope_impact": scope,
        "acceptance_impact": acceptance,
        "schedule_impact": schedule,
        "conflict_severity": conflict,
    }


def test_top_tiga_dari_lebih_banyak_kandidat():
    candidates = [
        q("a", scope=1),
        q("b", scope=3),
        q("c", scope=2),
        q("d", scope=0),
    ]
    ranked = questions.rank_questions(candidates)
    assert [c["text"] for c in ranked] == ["b", "c", "a"]


def test_priority_adalah_jumlah_empat_komponen():
    candidates = [
        q("tinggi", scope=1, acceptance=1, schedule=1, conflict=1),
        q("rendah", scope=1),
    ]
    ranked = questions.rank_questions(candidates)
    assert [c["text"] for c in ranked] == ["tinggi", "rendah"]


def test_skor_sama_mempertahankan_urutan_kemunculan():
    candidates = [q("pertama", scope=1), q("kedua", scope=1), q("ketiga", scope=1)]
    ranked = questions.rank_questions(candidates)
    assert [c["text"] for c in ranked] == ["pertama", "kedua", "ketiga"]


def test_kurang_dari_tiga_kandidat_mengembalikan_semua():
    candidates = [q("satu-satunya")]
    assert questions.rank_questions(candidates) == candidates


def test_kandidat_kosong():
    assert questions.rank_questions([]) == []


def test_field_impact_hilang_dianggap_nol():
    candidates = [{"text": "tanpa skor"}, q("berskor", scope=1)]
    ranked = questions.rank_questions(candidates)
    assert [c["text"] for c in ranked] == ["berskor", "tanpa skor"]


def test_maksimal_tiga_walau_ada_sepuluh_kandidat():
    candidates = [q(str(i), scope=i) for i in range(10)]
    ranked = questions.rank_questions(candidates)
    assert len(ranked) == 3
    assert [c["text"] for c in ranked] == ["9", "8", "7"]
