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

Sudah dijalankan sungguhan lewat Gemini Developer API (lihat
CATATAN-LANJUTAN.md) -- kutipan verbatim + provenance terbukti benar. Bentuk
`value` tiap field dijabarkan eksplisit di _INSTRUCTION di bawah karena model
awalnya menulis deliverables/acceptance_criteria sebagai satu string paragraf,
bukan list of object sesuai app.domain.schemas -- jangan hapus penjelasan
bentuk itu, itu bukan hiasan.
"""

from typing import Any, Literal, Optional

from google.adk.agents import LlmAgent
from google.adk.tools.tool_context import ToolContext
from pydantic import BaseModel

from app import config
from app.domain import extraction, guardrail
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

Field ledger minimum, dan BENTUK value yang WAJIB kamu pakai untuk tiap field
(field lain di luar daftar ini ditolak sistem -- jangan mengarang field baru):

- deliverables: list of {{"id": "d1", "title": "..."}} -- id pendek unik per
  deliverable, kamu yang membuatnya (d1, d2, ...), BUKAN kalimat.
- acceptance_criteria: list of {{"deliverable_id": "d1", "criterion_key": "...",
  "text": "..."}} -- criterion_key: huruf kecil, angka, tanda hubung saja
  (mis. "mobile-breakpoints"), deliverable_id MUST cocok salah satu id di atas.
- out_of_scope, in_scope, assumptions, unresolved_questions: list of string,
  satu klaim per string -- JANGAN gabung banyak klaim jadi satu paragraf.
- timeline.final_deadline: satu string tanggal/keterangan (mis. "2026-08-28"
  atau "Jumat" kalau brief tidak menyebut tanggal pasti).
- revision_policy.rounds_total: integer, atau JANGAN diajukan sama sekali
  kalau tidak disebut sebagai angka eksplisit (lihat aturan di bawah).

Setiap field di atas adalah SATU kandidat field-level (satu source_quote
mewakili satu list utuh atau satu deliverable/criterion) -- lihat field kritis
di bawah, kirim value dengan bentuk persis seperti dijelaskan.

Field kritis (paling menentukan readiness): {critical_fields}.

Aturan wajib:
- Setiap klaim MUST menyertakan source_artifact dan source_quote verbatim dari
  artifact itu -- jangan parafrase kutipannya.
- asserted_by MUST "client" kalau klaim berasal dari klien, atau "freelancer"
  kalau berasal dari kebijakan/pernyataan freelancer.
- JANGAN menebak nilai yang tidak disebutkan eksplisit. "beberapa revisi"
  BUKAN angka -- itu MISSING (jangan diajukan sama sekali), bukan diisi 2 atau 3.
- JANGAN pernah mengusulkan state AGREED. Kamu tidak berwenang menyetujui
  apa pun; itu hanya terjadi lewat aksi klien yang tervalidasi.
- Panggil save_ledger_draft tepat sekali di akhir, dengan seluruh kandidat
  field yang kamu temukan sekaligus.
""".format(critical_fields=", ".join(CRITICAL_FIELDS))


def extraction_agent_for(model: str):
    return LlmAgent(
        name="extraction_agent",
        description="Mengekstrak Deal Ledger terstruktur dari brief freelance dengan provenance per field.",
        model=model,
        instruction=_INSTRUCTION,
        tools=[validate_quote_candidate, save_ledger_draft],
    )


extraction_agent = extraction_agent_for(config.GEMINI_MODEL)


class CitationCandidate(BaseModel):
    ref: str
    quote: str


def propose_classification(
    classification: str, citations: list[CitationCandidate], tool_context: ToolContext
) -> dict:
    """Simpan usulan classification + citation untuk satu scope request
    (Guardrail, 02 §4.5).

    Divalidasi tanpa syarat lewat app.domain.guardrail.classify sebelum
    ditulis -- persis pola save_ledger_draft. Usulan ini TIDAK OTORITATIF:
    09-DOMAIN-RULES §8 mewajibkan hanya freelancer yang berwenang
    mengonfirmasi klasifikasi lewat POST .../classify, yang memvalidasi
    ulang dari nol dan tidak pernah membaca tool_context.state di sini
    secara langsung.
    """
    text_by_ref = tool_context.state.get("citable_text", {})
    final_classification, valid_citations = guardrail.classify(
        classification, [c.model_dump() for c in citations], text_by_ref
    )
    proposal = {"classification": final_classification, "citations": valid_citations}
    tool_context.state["classification_proposal"] = proposal
    return proposal


_GUARDRAIL_INSTRUCTION = """\
Kamu menilai satu permintaan baru dari klien terhadap baseline (rencana
proyek) yang sudah disepakati untuk sebuah proyek freelance.

Pesan berikutnya berisi permintaan klien yang harus dinilai, dan daftar teks
yang boleh dikutip (ref -> teks) dari baseline aktif.

Klasifikasi yang tersedia:
- IN_SCOPE: permintaan ini sudah tercakup oleh salah satu teks yang boleh
  dikutip di atas.
- CHANGE_REQUEST: permintaan ini di LUAR apa yang sudah disepakati -- scope
  tambahan, bukan sekadar klarifikasi dari yang sudah ada.
- AMBIGUOUS: kamu tidak yakin ada dasar kutipan yang kuat untuk salah satu
  di atas.

Aturan wajib:
- IN_SCOPE dan CHANGE_REQUEST WAJIB disertai minimal satu citation verbatim
  (ref dan quote PERSIS seperti tertulis di teks yang boleh dikutip) yang
  benar-benar mendukung kesimpulanmu. JANGAN memaksakan kutipan yang tidak
  relevan hanya supaya tidak AMBIGUOUS -- kalau ragu, pilih AMBIGUOUS tanpa
  citation.
- JANGAN mengarang ref yang tidak ada di daftar yang diberikan.
- Panggil propose_classification tepat sekali, dengan classification final
  dan seluruh citation pendukungnya (list kosong kalau AMBIGUOUS).
- Usulanmu bukan keputusan akhir -- freelancer tetap yang mengonfirmasi.
"""

def guardrail_agent_for(model: str):
    return LlmAgent(
        name="guardrail_agent",
        description=(
            "Mengusulkan classification (IN_SCOPE/AMBIGUOUS/CHANGE_REQUEST) + citation "
            "untuk satu scope request baru, terhadap baseline aktif."
        ),
        model=model,
        instruction=_GUARDRAIL_INSTRUCTION,
        tools=[propose_classification],
    )


guardrail_agent = guardrail_agent_for(config.GEMINI_MODEL)
