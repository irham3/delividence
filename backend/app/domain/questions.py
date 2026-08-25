"""Ranking clarification questions — 02-ARCHITECTURE §4.4, 01-PRD §6 & §7.

Model mengusulkan kandidat pertanyaan dengan skor dampak; fungsi di sini
satu-satunya yang membentuk himpunan final maksimal tiga pertanyaan aktif,
deterministik. `save_questions` (kalau/ketika dibangun) hanya menyimpan
kandidat mentah -- tidak menegakkan limit sendiri (02 §4.4), supaya tidak ada
enforcement ganda yang bisa menghasilkan lebih dari tiga pertanyaan aktif.

Sengaja TIDAK mengimplementasikan forced-slot untuk field kritis CONFLICTING
(09-DOMAIN-RULES §5.6, bagian Modul D). Modul D dilepas pada profil ini
(10-KEPUTUSAN-DAN-VERIFIKASI.md §4b) bersama seluruh deteksi multi-candidate-
nya -- app/domain/extraction.py tidak punya jalur yang menghasilkan
CONFLICTING sama sekali. Membangun override untuk state yang tidak pernah
muncul adalah kode mati yang tidak bisa diuji jujur. Kalau Modul D dihidupkan
lagi, override itu MUST ditambahkan di sini sebelum ranking dipakai lagi.
"""

from app.domain.enums import MAX_CLARIFICATION_QUESTIONS


def _priority(candidate):
    return (
        candidate.get("scope_impact", 0)
        + candidate.get("acceptance_impact", 0)
        + candidate.get("schedule_impact", 0)
        + candidate.get("conflict_severity", 0)
    )


def rank_questions(candidates):
    """Kandidat model -> maksimal MAX_CLARIFICATION_QUESTIONS pertanyaan.

    Urut priority menurun; skor sama mempertahankan urutan kemunculan asli di
    `candidates` (stable sort, tidak ada tie-break tersembunyi berbasis waktu
    atau field -- supaya hasil dapat direproduksi dari input yang sama).
    """
    indexed = list(enumerate(candidates))
    indexed.sort(key=lambda pair: (-_priority(pair[1]), pair[0]))
    return [c for _, c in indexed[:MAX_CLARIFICATION_QUESTIONS]]
