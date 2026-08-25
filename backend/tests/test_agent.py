"""Test agent.py -- konstruksi Agent ADK dan tool-nya.

Tidak memanggil Gemini (belum bisa, billing GCP belum aktif -- lihat
CATATAN-LANJUTAN.md). Yang diuji: agent bisa dikonstruksi, dan tool
yang dipanggilnya langsung (bypass LLM) menghasilkan bentuk yang benar --
sama seperti test_extraction.py, hanya lewat pembungkus ADK-nya.
"""

from app import agent, config
from app.domain.enums import CLIENT_STATED, CRITICAL_FIELDS, MISSING


class _FakeToolContext:
    """Duck-type ToolContext ADK -- tool di agent.py hanya menyentuh .state."""

    def __init__(self, artifacts=None):
        self.state = {"artifacts": artifacts or {}}


def test_agent_konstruksi_dengan_model_dan_dua_tool():
    assert agent.extraction_agent.model == config.GEMINI_MODEL
    assert len(agent.extraction_agent.tools) == 2
    assert agent.validate_quote_candidate in agent.extraction_agent.tools
    assert agent.save_ledger_draft in agent.extraction_agent.tools


def test_instruksi_menyebut_semua_field_kritis():
    for field in CRITICAL_FIELDS:
        assert field in agent.extraction_agent.instruction


def test_validate_quote_candidate_kutipan_valid():
    ctx = _FakeToolContext({"artifact:brief-1": "Deadline minggu depan ya."})
    result = agent.validate_quote_candidate("Deadline minggu depan", "artifact:brief-1", ctx)
    assert result == {"valid": True}


def test_validate_quote_candidate_artifact_tidak_ada():
    ctx = _FakeToolContext({})
    result = agent.validate_quote_candidate("apa saja", "artifact:tidak-ada", ctx)
    assert result == {"valid": False}


def test_save_ledger_draft_menulis_ke_state_dan_memvalidasi_ulang():
    ctx = _FakeToolContext({"artifact:brief-1": "Deadline minggu depan ya."})
    candidates = [
        agent.FieldCandidate(
            field="timeline.final_deadline",
            value="minggu depan",
            source_artifact="artifact:brief-1",
            source_quote="Deadline minggu depan",
            asserted_by="client",
        ),
        agent.FieldCandidate(field="out_of_scope"),  # tanpa value -> MISSING
    ]

    result = agent.save_ledger_draft(candidates, ctx)

    assert result is ctx.state["ledger_draft"]
    assert result["timeline"]["final_deadline"]["state"] == CLIENT_STATED
    assert result["out_of_scope"]["state"] == MISSING


def test_save_ledger_draft_kutipan_karangan_tidak_lolos_walau_model_mengklaim():
    """Model tidak bisa melewati gate hanya dengan tidak memanggil
    validate_quote_candidate -- save_ledger_draft memvalidasi ulang sendiri."""
    ctx = _FakeToolContext({"artifact:brief-1": "Deadline minggu depan ya."})
    candidates = [
        agent.FieldCandidate(
            field="timeline.final_deadline",
            value="bulan depan",
            source_artifact="artifact:brief-1",
            source_quote="deadline bulan depan",
            asserted_by="client",
        )
    ]

    result = agent.save_ledger_draft(candidates, ctx)

    assert result["timeline"]["final_deadline"]["state"] != CLIENT_STATED
