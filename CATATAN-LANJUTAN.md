# Catatan Lanjutan — Delividence

Ditulis **25 Agustus 2026, sore**. Baca file ini dulu sebelum menyentuh apa pun.

---

## Di mana kita sekarang

| | |
|---|---|
| Deadline | **1 September 2026, 07:00 WIB** (31 Agu 17:00 PT) |
| Target submit internal | 31 Agustus, 18:00 WIB |
| Sisa waktu kerja realistis | **~26–29 jam** |
| Repo submission | <https://github.com/irham3/delividence> (public, akun partner, remote `delividence`) |
| Repo cadangan | <https://github.com/rifqiahmadpratama/dealready> (private, remote `origin`) |
| Folder lokal | `C:\Users\ASUS\Projects\dealready` (nama folder sengaja dibiarkan lama) |
| Test | **64 hijau** (`cd backend; ..\.venv\Scripts\python.exe -m pytest -q`) |

Tidak ada proses yang ditinggal jalan. Aman dimatikan.

---

## Yang sudah jadi

**Vertical slice async** — `POST /runs` → antrean → worker → store, dua service
dari satu image lewat `ROLE=api|worker`. Sudah diverifikasi lewat browser: status
berubah `queued → done` sendiri tanpa request kedua.

**Frontend** — Next.js 16 + TypeScript + Tailwind 4 di `web/`. English-first
dengan selector bahasa output.

**Inti domain** (`backend/app/domain/`) — ini yang dikerjakan terakhir:

| File | Isi | Rujukan |
|---|---|---|
| `enums.py` | Semua enum tertutup: state field, status criterion, actor, 21 tipe audit event, `CRITICAL_FIELDS` | §10 butir 4 |
| `canonical.py` | `normalize_criterion_text`, `canonical_json`, `payload_hash`, `text_hash`, `validate_quote` | §10 butir 2 |
| `criteria.py` | Modul A: `effective_status`, `can_record_decision`, validasi `criterion_key` | §2 |
| `readiness.py` | Gate readiness deterministik | 01 §7 + §5.7 |

Golden vector hash sudah dipaku sebagai literal di `tests/test_domain.py`.
Kalau nilainya berubah, artinya klaim integritas berubah arti — jangan
"perbaiki" test-nya, cari tahu kenapa hash bergeser.

Test Modul A menutup A-T1 sampai A-T11 dari §2.8.

---

## Yang dikerjakan berikutnya

1. ~~**Alokasi `seq`** (§7.2) + service penulis audit event.~~ **Selesai** —
   `backend/app/audit.py`: `append_event()` (validasi type/actor/baseline_version
   G-6, alokasi seq dalam transaksi Firestore / lock in-process lokal, envelope
   §7.1) dan `list_events()` (urut seq asc, dipakai semua modul §6). Belum ada
   pemanggil lain; ini fondasi, bukan fitur yang terlihat. 10 test baru di
   `tests/test_audit.py`.
2. ~~**Skema ledger** (§10 butir 1).~~ **Selesai** — `backend/app/domain/schemas.py`:
   model Pydantic `LedgerField`, `DealLedger`, `Criterion`/`CanonicalPayload`/
   `Baseline`, `CriterionDecision`, `AuditEventEnvelope`. Sengaja **bukan** di
   folder root `shared/schemas/` seperti tertulis di 06 §1 — sudah dicek ke
   Rifqi, keputusannya taruh di dalam backend karena satu-satunya konsumen
   saat ini Python backend (web/ belum menyentuh bentuk ledger). Hanya
   mendeskripsikan bentuk; tidak menyentuh/mengubah `criteria.py`/`readiness.py`
   yang sudah ada. 13 test baru di `tests/test_schemas.py`, termasuk cross-check
   langsung ke output `app.audit.append_event()`.
3. **Ekstraksi brief → ledger** lewat Gemini, dengan `validate_quote`
   dijalankan tanpa syarat atas setiap field sebelum draft ditulis. Sekarang
   ada `schemas.DealLedger`/`schemas.Baseline` untuk memvalidasi hasil ekstraksi
   sebelum ditulis — pakai itu, jangan bikin dict manual lagi.
4. **Ranking tiga pertanyaan** prioritas.
5. Baru setelah itu: portal klien, baseline approval, Guardrail, Proof.

---

## Blocker yang tidak bisa diselesaikan dari sisi kode

1. **Billing Google Cloud belum aktif.** Cutoff klaim $150 credit:
   **28 Agustus, 12:00 PT**. Semua langkah cloud menunggu di belakang ini.
2. **`gcloud` belum terpasang** (tidak ada `winget` di mesin ini):
   `curl.exe -o "$env:TEMP\gcloud.exe" https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe; & "$env:TEMP\gcloud.exe"`
   lalu `gcloud auth login` dan `gcloud auth application-default login`.
3. **Status tim di Devpost belum dipastikan.** Repo submission ada di akun
   partner. Itu sah untuk tim — tetapi hanya kalau keduanya terdaftar sebagai
   tim di Devpost dan undangannya sudah diterima.
4. **Aturan kontes Emergent** (D-4) belum dicek soal benturan.

Begitu billing aktif: `.\deploy\01-setup-gcp.ps1 -ProjectId <id>` lalu
`.\deploy\02-deploy.ps1 -ProjectId <id>`. Keduanya belum pernah dijalankan.

---

## Keputusan yang sudah dikunci — jangan dibuka ulang tanpa alasan baru

- Nama **Delividence** (sempat DealReady, lalu ScopeHandshake).
- Model **`gemini-3.7-flash`**. Paket revisi menulis `gemini-3.5-flash`; itu
  sudah dikoreksi karena Google kini menyebutnya *legacy Flash model*.
- **Profil Modul A saja.** Modul C (drift ledger), B (revision rounds), dan D
  (conflict resolution) dilepas berikut fixture konflik Friday/Monday. Alasan
  lengkap di `docs/10-KEPUTUSAN-DAN-VERIFIKASI.md` §4b.
- Backend Python, bukan Express — ADK Python-first.

Rujukan utama: `docs/10-KEPUTUSAN-DAN-VERIFIKASI.md` (keputusan + fakta aturan
terverifikasi) dan `docs/09-DOMAIN-RULES.md` (aturan normatif).
`docs/arsip-dealready/` adalah riwayat, bukan rujukan.
