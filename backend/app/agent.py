"""Agent ADK — ekstraksi brief menjadi ledger draft (02-ARCHITECTURE §4.2, §4.3).

Tool di sini sengaja tipis: seluruh aturan (validate_quote tanpa syarat, G-1
model tidak boleh menulis AGREED) hidup di app/domain/extraction.py dan
dipanggil dari sini, bukan ditulis ulang.

Sengaja BELUM termasuk `load_deal_context`/`read_artifact` dari tool allowlist
penuh (§4.2) -- itu butuh model data `deals/{deal_id}/artifacts/` yang belum
ada (lihat CATATAN-LANJUTAN.md). Pemanggil agent ini untuk saat ini
bertanggung jawab mengisi `tool_context.state["artifacts"]` (dict
artifact_ref -> teks lengkap) sebelum run dimulai. `save_ledger_draft` dan
`validate_quote_candidate` membaca dari situ.

Belum pernah dijalankan sungguhan (billing GCP belum aktif, lihat
CATATAN-LANJUTAN.md) -- konstruksi Agent ini diuji (importable, tool
callable), pemanggilan Gemini yang sesungguhnya belum.
"""

from typing import Any, Literal, Optional

from google.adk.agents import LlmAgent
from google.adk.tools.tool_context import ToolContext
from pydantic import BaseModel

from app import config
from app.domain import extraction
from app.domain.canonical import validate_quote
from app.domain.enums import CRITICAL_FIELDS


class FieldCandidate(BaseModel):
    """Bentuk satu kandidat yang MUST dikirim model ke save_ledger_draft.

    `state` diterima tapi diabaikan -- app.domain.extraction menghitung
    ulang state akhir dari hasil validasi kutipan (G-1), tidak pernah
    mempercayai usulan model.
    """

    field: str
    value: Any = None
    source_artifact: Optional[str] = None
    source_quote: Optional[str] = None
    confidence: Optional[float] = None
    asserted_by: Optional[Literal["client", "freelancer"]] = None
    state: Optional[str] = None


def validate_quote_candidate(source_quote: str, source_artifact: str, tool_context: ToolContext) -> dict:
    """Cek apakah source_quote benar-benar ada (verbatim, setelah normalisasi
    whitespace) di dalam artifact source_artifact.

    Self-check saja. Hasilnya TIDAK OTORITATIF -- save_ledger_draft tetap
    memvalidasi ulang setiap kandidat tanpa syarat sebelum ditulis (09
    §10, 02 §4.3), terlepas dari apakah tool ini dipanggil.
    """
    artifacts = tool_context.state.get("artifacts", {})
    artifact_text = artifacts.get(source_artifact)
    valid = bool(artifact_text) and validate_quote(source_quote, artifact_text)
    return {"valid": valid}


def save_ledger_draft(candidates: list[FieldCandidate], tool_context: ToolContext) -> dict:
    """Simpan hasil ekstraksi sebagai ledger draft.

    Setiap kandidat divalidasi tanpa syarat lewat
    app.domain.extraction.project_field_candidate sebelum ditulis ke
    tool_context.state["ledger_draft"]. Tool ini MUST NOT dan tidak bisa
    menghasilkan state AGREED -- itu ditolak sebagai DomainError.
    """
    artifacts = tool_context.state.get("artifacts", {})
    draft = extraction.assemble_ledger_draft(
        [c.model_dump() for c in candidates], artifacts
    )
    tool_context.state["ledger_draft"] = draft
    return draft


_INSTRUCTION = """\
Kamu mengekstrak Deal Ledger terstruktur dari brief freelance (teks, dan opsional
satu screenshot chat). Setiap sumber tersedia sebagai satu artifact_ref di
konteks yang diberikan.

Field ledger minimum: deliverables, in_scope, out_of_scope, acceptance_criteria,
timeline.final_deadline, revision_policy.rounds_total, dependencies,
assumptions, unresolved_questions.

Field kritis (paling menentukan readiness): {critical_fields}.

Aturan wajib:
- Setiap klaim MUST menyertakan source_artifact dan source_quote verbatim dari
  artifact itu -- jangan parafrase kutipannya.
- asserted_by MUST "client" kalau klaim berasal dari klien, atau "freelancer"
  kalau berasal dari kebijakan/pernyataan freelancer.
- JANGAN menebak nilai yang tidak disebutkan eksplisit. "beberapa revisi"
  BUKAN angka -- itu MISSING, bukan diisi 2 atau 3.
- JANGAN pernah mengusulkan state AGREED. Kamu tidak berwenang menyetujui
  apa pun; itu hanya terjadi lewat aksi klien yang tervalidasi.
- criterion_key (kalau mengusulkan acceptance criterion baru): huruf kecil,
  angka, dan tanda hubung saja, mis. "mobile-breakpoints".
- Panggil save_ledger_draft tepat sekali di akhir, dengan seluruh kandidat
  field yang kamu temukan sekaligus.
""".format(critical_fields=", ".join(CRITICAL_FIELDS))


extraction_agent = LlmAgent(
    name="extraction_agent",
    description="Mengekstrak Deal Ledger terstruktur dari brief freelance dengan provenance per field.",
    model=config.GEMINI_MODEL,
    instruction=_INSTRUCTION,
    tools=[validate_quote_candidate, save_ledger_draft],
)
