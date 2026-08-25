"""Test aturan domain — 09-DOMAIN-RULES §2.8 dan §10.

Tidak ada cloud, tidak ada LLM, tidak ada I/O. Kalau test di file ini butuh
salah satunya, aturannya yang salah tempat.
"""

import pytest

from app.domain import canonical, criteria, readiness
from app.domain.enums import (
    ACCEPTED,
    AGREED,
    CHANGES_REQUESTED,
    CLIENT_STATED,
    CONFLICTING,
    MISSING,
    NOT_SET,
    PENDING,
    PROPOSED,
    SUPERSEDED,
    WITHDRAWN,
    DomainError,
)

TEKS = "Layout renders correctly at 375px, 768px, and 1440px widths."


# --- §10 butir 2: normalisasi, canonical JSON, hash ------------------------


def test_normalisasi_menyeragamkan_semua_whitespace():
    kotor = "  Layout\trenders\ncorrectly at 375px.  "
    assert canonical.normalize_criterion_text(kotor) == "Layout renders correctly at 375px."


def test_normalisasi_tidak_lowercase_dan_tidak_membuang_tanda_baca():
    assert canonical.normalize_criterion_text("Layout, 375px.") == "Layout, 375px."


def test_golden_vector_text_hash():
    """Input tetap -> string hash persis. Kalau ini berubah, seluruh klaim
    integritas berubah artinya, jadi nilainya sengaja dipaku di sini."""
    assert canonical.text_hash(TEKS) == (
        "sha256:8fe2a6a3a09f15c2765ef6dc581b66549d81dfa97b7c97417eb732cc9051d1bc"
    )


def test_golden_vector_payload_hash():
    assert canonical.payload_hash({"b": 1, "a": [1, 2], "c": "nilai unicode ü"}) == (
        "sha256:15ed80fe5288c3be50867dac9cc84d518ac860e469d63abbf02f722d8ef646e5"
    )


def test_perubahan_editorial_tidak_mengubah_hash():
    assert canonical.text_hash(TEKS) == canonical.text_hash(
        "Layout renders  correctly at 375px,\n768px, and 1440px widths."
    )


def test_perubahan_satu_karakter_mengubah_hash():
    assert canonical.text_hash(TEKS) != canonical.text_hash(TEKS.replace("375", "376"))


def test_canonical_json_stabil_terhadap_urutan_key():
    assert canonical.canonical_json({"b": 1, "a": 2}) == canonical.canonical_json(
        {"a": 2, "b": 1}
    )


def test_canonical_json_menolak_nan():
    with pytest.raises(ValueError):
        canonical.canonical_json({"x": float("nan")})


# --- §10: validasi kutipan verbatim ---------------------------------------


def test_kutipan_yang_benar_benar_ada_lolos():
    artifact = "Bro, deadline minggu depan ya. Budget 2 juta."
    assert canonical.validate_quote("deadline minggu depan", artifact) is True


def test_kutipan_karangan_ditolak():
    artifact = "Bro, deadline minggu depan ya."
    assert canonical.validate_quote("deadline bulan depan", artifact) is False


def test_kutipan_dibandingkan_setelah_normalisasi_whitespace():
    artifact = "Bro,\tdeadline   minggu\ndepan ya."
    assert canonical.validate_quote("deadline minggu depan", artifact) is True


# --- MODUL A §2.8 ---------------------------------------------------------


def baseline(criteria_map):
    return {"canonical_payload": {"criteria": criteria_map}}


def crit(text):
    return {"text": text, "text_hash": canonical.text_hash(text)}


def keputusan(decision, version, text, seq, key="k1"):
    return {
        "criterion_key": key,
        "decision": decision,
        "baseline_version": version,
        "criterion_text_hash": canonical.text_hash(text),
        "seq": seq,
    }


def status(key, active, baselines, decisions):
    return criteria.effective_status(key, active, baselines, decisions)


def test_a_t1_diterima_pada_versi_aktif():
    b = {1: baseline({"k1": crit(TEKS)})}
    assert status("k1", 1, b, [keputusan(ACCEPTED, 1, TEKS, 10)]) == ACCEPTED


def test_a_t2_naik_versi_dengan_teks_identik_tetap_diterima():
    b = {1: baseline({"k1": crit(TEKS)}), 2: baseline({"k1": crit(TEKS)})}
    assert status("k1", 2, b, [keputusan(ACCEPTED, 1, TEKS, 10)]) == ACCEPTED


def test_a_t3_teks_berubah_membatalkan_acceptance():
    lain = TEKS.replace("1440px", "1920px")
    b = {1: baseline({"k1": crit(TEKS)}), 2: baseline({"k1": crit(lain)})}
    assert status("k1", 2, b, [keputusan(ACCEPTED, 1, TEKS, 10)]) == SUPERSEDED


def test_a_t4_perubahan_spasi_saja_tidak_membatalkan():
    b = {
        1: baseline({"k1": crit(TEKS)}),
        2: baseline({"k1": crit("Layout renders  correctly at 375px, 768px, and 1440px widths.")}),
    }
    assert status("k1", 2, b, [keputusan(ACCEPTED, 1, TEKS, 10)]) == ACCEPTED


def test_a_t5_criterion_hilang_di_versi_baru_jadi_withdrawn():
    b = {1: baseline({"k1": crit(TEKS)}), 2: baseline({})}
    assert status("k1", 2, b, [keputusan(ACCEPTED, 1, TEKS, 10)]) == WITHDRAWN


def test_a_t6_keluar_lalu_kembali_tetap_superseded():
    """Keluar dari kesepakatan lalu kembali adalah putus makna, bukan lanjutan."""
    b = {
        1: baseline({"k1": crit(TEKS)}),
        2: baseline({}),
        3: baseline({"k1": crit(TEKS)}),
    }
    assert status("k1", 3, b, [keputusan(ACCEPTED, 1, TEKS, 10)]) == SUPERSEDED


def test_a_t7_criterion_baru_mulai_dari_pending():
    b = {1: baseline({"k1": crit(TEKS)}), 2: baseline({"k1": crit(TEKS), "k9": crit("Something else.")})}
    assert status("k9", 2, b, []) == PENDING


def test_a_t8_changes_requested_bertahan_selama_teks_sama():
    b = {1: baseline({"k1": crit(TEKS)})}
    assert status("k1", 1, b, [keputusan(CHANGES_REQUESTED, 1, TEKS, 10)]) == CHANGES_REQUESTED


def test_a_t9_keputusan_dengan_seq_terbesar_yang_menang():
    b = {1: baseline({"k1": crit(TEKS)})}
    decisions = [keputusan(ACCEPTED, 1, TEKS, 20), keputusan(CHANGES_REQUESTED, 1, TEKS, 10)]
    assert status("k1", 1, b, decisions) == ACCEPTED


def test_a_t10_key_yang_tidak_pernah_ada_adalah_domain_error():
    b = {1: baseline({"k1": crit(TEKS)})}
    with pytest.raises(DomainError):
        status("k404", 1, b, [])


def test_a_t11_acceptance_final_diarahkan_ke_guardrail():
    """A-9: jangan menimpa ACCEPTED dengan CHANGES_REQUESTED atas teks yang sama."""
    b = {1: baseline({"k1": crit(TEKS)})}
    decisions = [keputusan(ACCEPTED, 1, TEKS, 10)]

    boleh, alasan = criteria.can_record_decision("k1", 1, b, decisions, CHANGES_REQUESTED)
    assert boleh is False
    assert "scope review" in alasan
    assert status("k1", 1, b, decisions) == ACCEPTED


def test_naik_versi_saja_tidak_mengubah_status_apa_pun():
    """A-8. Kalau v2 hanya mengubah timeline, semua acceptance tetap berlaku."""
    b = {1: baseline({"k1": crit(TEKS)}), 2: baseline({"k1": crit(TEKS)})}
    b[2]["canonical_payload"]["timeline"] = {"final_deadline": "2026-09-30"}
    assert status("k1", 2, b, [keputusan(ACCEPTED, 1, TEKS, 10)]) == ACCEPTED


def test_criterion_key_divalidasi_formatnya():
    assert criteria.validate_criterion_key("mobile-breakpoints")
    for buruk in ["Mobile-Breakpoints", "mobile_breakpoints", "-mobile", "mobile--x", "a" * 49]:
        with pytest.raises(DomainError):
            criteria.validate_criterion_key(buruk)


# --- Gate readiness (01 §7, §5.7) -----------------------------------------


def ledger_lengkap():
    return {
        "deliverables": {
            "state": CLIENT_STATED,
            "value": [{"id": "d1", "title": "Instagram edits"}],
        },
        "acceptance_criteria": {
            "state": AGREED,
            "value": [{"deliverable_id": "d1", "criterion_key": "k1", "text": TEKS}],
        },
        "out_of_scope": {"state": AGREED, "value": ["Thumbnail design"]},
        "timeline": {"final_deadline": {"state": CLIENT_STATED, "value": "2026-09-01"}},
        "revision_policy": {"rounds_total": {"state": AGREED, "value": 2}},
    }


def test_ledger_lengkap_lolos_gate():
    ready, blockers = readiness.evaluate(ledger_lengkap())
    assert ready is True
    assert blockers == []


def test_field_kritis_missing_memblokir():
    l = ledger_lengkap()
    l["out_of_scope"] = {"state": MISSING, "value": None}
    ready, blockers = readiness.evaluate(l)
    assert ready is False
    assert [b["field"] for b in blockers] == ["out_of_scope"]


def test_field_kritis_conflicting_memblokir():
    l = ledger_lengkap()
    l["timeline"]["final_deadline"] = {"state": CONFLICTING, "value": None}
    ready, blockers = readiness.evaluate(l)
    assert ready is False
    assert "client" in blockers[0]["reason"]


def test_usulan_model_belum_dikonfirmasi_memblokir():
    """PROPOSED bukan kesepakatan. Model tidak bisa meloloskan gate sendiri."""
    l = ledger_lengkap()
    l["revision_policy"]["rounds_total"] = {"state": PROPOSED, "value": 2}
    ready, blockers = readiness.evaluate(l)
    assert ready is False
    assert "confirmed" in blockers[0]["reason"]


def test_not_set_adalah_nilai_yang_sah_bukan_penghalang():
    """§5.7: NOT_SET berarti kedua pihak sepakat batas itu tidak ditetapkan."""
    l = ledger_lengkap()
    l["revision_policy"]["rounds_total"] = {"state": AGREED, "value": NOT_SET}
    ready, _ = readiness.evaluate(l)
    assert ready is True


def test_deliverable_tanpa_criterion_memblokir():
    l = ledger_lengkap()
    l["deliverables"]["value"].append({"id": "d2", "title": "TikTok cutdowns"})
    ready, blockers = readiness.evaluate(l)
    assert ready is False
    assert "TikTok cutdowns" in blockers[0]["reason"]


def test_ledger_kosong_memblokir_semua_field_kritis():
    ready, blockers = readiness.evaluate({})
    assert ready is False
    assert len(blockers) == 6  # lima field kritis + syarat minimal satu deliverable
