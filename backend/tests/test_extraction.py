"""Test proyeksi kandidat model -> ledger field — 02-ARCHITECTURE §4.3.

Tidak ada Gemini, tidak ada ADK, tidak ada I/O di sini. Kalau test ini butuh
salah satunya, logikanya salah tempat (lihat app/domain/extraction.py).
"""

import pytest

from app.domain import extraction
from app.domain.enums import (
    AGREED,
    CLIENT_STATED,
    FREELANCER_POLICY,
    MISSING,
    PROPOSED,
    DomainError,
)

ARTIFACT = "Bro, deadline minggu depan ya. Dua ronde revisi termasuk."
ARTIFACTS = {"artifact:brief-1": ARTIFACT}


def test_kutipan_valid_dari_klien_jadi_client_stated():
    field = extraction.project_field_candidate(
        {
            "value": "minggu depan",
            "source_artifact": "artifact:brief-1",
            "source_quote": "deadline minggu depan",
            "asserted_by": "client",
            "confidence": 0.9,
        },
        ARTIFACTS,
    )
    assert field == {
        "value": "minggu depan",
        "state": CLIENT_STATED,
        "source_artifact": "artifact:brief-1",
        "source_quote": "deadline minggu depan",
        "confidence": 0.9,
    }


def test_kutipan_valid_dari_freelancer_jadi_freelancer_policy():
    field = extraction.project_field_candidate(
        {
            "value": 2,
            "source_artifact": "artifact:brief-1",
            "source_quote": "Dua ronde revisi termasuk",
            "asserted_by": "freelancer",
        },
        ARTIFACTS,
    )
    assert field["state"] == FREELANCER_POLICY


def test_kutipan_karangan_turun_ke_proposed_bukan_client_stated():
    """02 §4.3: gagal validasi -> PROPOSED/MISSING, tidak pernah CLIENT_STATED."""
    field = extraction.project_field_candidate(
        {
            "value": "bulan depan",
            "source_artifact": "artifact:brief-1",
            "source_quote": "deadline bulan depan",
            "asserted_by": "client",
        },
        ARTIFACTS,
    )
    assert field["state"] == PROPOSED
    assert field["value"] == "bulan depan"


def test_tanpa_kutipan_sama_sekali_turun_ke_proposed():
    field = extraction.project_field_candidate(
        {"value": "minggu depan", "asserted_by": "client"}, ARTIFACTS
    )
    assert field["state"] == PROPOSED


def test_tanpa_nilai_jadi_missing():
    field = extraction.project_field_candidate({"asserted_by": "client"}, ARTIFACTS)
    assert field == {
        "value": None,
        "state": MISSING,
        "source_artifact": None,
        "source_quote": None,
        "confidence": None,
    }


def test_referensi_artifact_yang_tidak_ada_turun_ke_proposed():
    field = extraction.project_field_candidate(
        {
            "value": "minggu depan",
            "source_artifact": "artifact:tidak-ada",
            "source_quote": "deadline minggu depan",
            "asserted_by": "client",
        },
        ARTIFACTS,
    )
    assert field["state"] == PROPOSED


def test_asserted_by_tidak_dikenal_turun_ke_proposed_walau_kutipan_valid():
    field = extraction.project_field_candidate(
        {
            "value": "minggu depan",
            "source_artifact": "artifact:brief-1",
            "source_quote": "deadline minggu depan",
            "asserted_by": "model",
        },
        ARTIFACTS,
    )
    assert field["state"] == PROPOSED


def test_model_mengusulkan_agreed_ditolak_g1():
    with pytest.raises(DomainError):
        extraction.project_field_candidate(
            {"value": "minggu depan", "state": AGREED, "asserted_by": "client"},
            ARTIFACTS,
        )


# --- assemble_ledger_draft --------------------------------------------------


def test_assemble_memetakan_path_bertitik_ke_nested_dict():
    draft = extraction.assemble_ledger_draft(
        [
            {
                "field": "timeline.final_deadline",
                "value": "minggu depan",
                "source_artifact": "artifact:brief-1",
                "source_quote": "deadline minggu depan",
                "asserted_by": "client",
            },
            {
                "field": "out_of_scope",
                "value": ["Thumbnail design"],
                "source_artifact": "artifact:brief-1",
                "source_quote": "Dua ronde revisi termasuk",
                "asserted_by": "freelancer",
            },
        ],
        ARTIFACTS,
    )
    assert draft["timeline"]["final_deadline"]["state"] == CLIENT_STATED
    assert draft["out_of_scope"]["state"] == FREELANCER_POLICY
    assert draft["out_of_scope"]["value"] == ["Thumbnail design"]


def test_assemble_ledger_kosong_untuk_daftar_kandidat_kosong():
    assert extraction.assemble_ledger_draft([], ARTIFACTS) == {}
