"""Normalisasi, canonical JSON, hash, dan validasi kutipan.

09-DOMAIN-RULES §10 butir 2: satu fungsi, satu pemilik, satu file. Dua
implementasi yang berbeda tipis menghasilkan hash berbeda, dan seluruh klaim
integritas mati tanpa memunculkan error apa pun. Jangan menyalin logika di sini
ke tempat lain, dan jangan "memperbaiki" toleransinya.
"""

import hashlib
import json
import re
import unicodedata

# Semua whitespace yang harus diseragamkan jadi U+0020, termasuk NBSP.
_WHITESPACE = re.compile("[\t\n\r\f\v\x20\u00a0]+")


def normalize_criterion_text(s):
    """§2.4. NFC, seragamkan whitespace, rapatkan, trim.

    Sengaja TIDAK lowercase dan TIDAK membuang tanda baca: sistem ini memilih
    bertanya ulang daripada diam-diam menganggap dua teks berbeda itu sama.
    Perubahan editorial murni tidak membatalkan acceptance; perubahan karakter
    yang terlihat, membatalkan.
    """
    s = unicodedata.normalize("NFC", s)
    s = _WHITESPACE.sub(" ", s)
    return s.strip()


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def text_hash(text):
    """Hash teks criterion, sudah dinormalisasi lebih dulu."""
    return "sha256:" + sha256_hex(normalize_criterion_text(text).encode("utf-8"))


def canonical_json(payload):
    """§10 butir 2. Satu bentuk serialisasi, supaya hash tidak pernah berbeda.

    Key diurutkan, tanpa spasi, unicode apa adanya (bukan escape \\uXXXX), dan
    NaN/Infinity ditolak karena bukan JSON yang sah dan tidak stabil antar bahasa.
    """
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def payload_hash(payload):
    return "sha256:" + sha256_hex(canonical_json(payload).encode("utf-8"))


def validate_quote(source_quote, artifact_text):
    """§10. Kutipan harus benar-benar ada di artifact, dibandingkan setelah
    normalisasi whitespace di kedua sisi.

    Offset karakter dari model tidak dipakai: mudah meleset, dan merusak klaim
    provenance persis di titik kepercayaan dibutuhkan.

    Gate ini dijalankan tanpa syarat oleh API/worker atas setiap field dari
    setiap structured output. Model tidak bisa melewatinya dengan tidak
    memanggil tool apa pun. Kalau hasilnya False, field turun ke PROPOSED atau
    MISSING dan tidak boleh diatribusikan ke klien.
    """
    if not source_quote or not artifact_text:
        return False
    return normalize_criterion_text(source_quote) in normalize_criterion_text(
        artifact_text
    )
