# 03 — Rincian yang Harus Dibangun

Semua dari nol. Dipakai sebagai sumber daftar kerja di
[`04-PLAN-7-DAYS.md`](04-PLAN-7-DAYS.md).

Perkiraan waktu mengasumsikan **satu orang bekerja dengan bantuan AI coding**,
dengan kecepatan yang terbukti: Baseline dibangun dari nol dalam ~6 hari
(92 commit, 18–23 Agustus 2026). Kalau dikerjakan berdua partner, waktu total
tidak otomatis terbagi dua — koordinasi punya biaya sendiri.

---

## 1. Infrastruktur Google Cloud

| # | Item | Perkiraan | Catatan |
|---|---|---|---|
| I1 | Akun GCP + billing aktif + klaim $150 credit | 1–3 jam | **Di luar kendali kita.** Verifikasi billing bisa lama. Kerjakan paling awal |
| I2 | Aktifkan API: Cloud Run, Pub/Sub, Firestore, Secret Manager, Artifact Registry | 30 menit | |
| I3 | Firestore mode Native + aturan keamanan | 1 jam | |
| I4 | Firebase Auth + Google Sign-In | 1 jam | |
| I5 | Topic + push subscription Pub/Sub dengan OIDC | 1–2 jam | Sering gagal di percobaan pertama karena IAM |
| I6 | Secret Manager + service account beserta role | 1 jam | Prinsip least privilege |
| I7 | Artifact Registry + pipeline deploy pertama | 2–3 jam | Deploy pertama selalu paling lama |

**Total: ~1 hari.** Jangan diremehkan. Ini bagian yang paling sering meleset
karena kegagalannya bersifat konfigurasi, bukan logika.

## 2. Agent (inti nilai)

| # | Item | Perkiraan | Catatan |
|---|---|---|---|
| A1 | ADK "hello world" — agent minimal jalan lokal, satu tool dummy | 2–3 jam | **Kerjakan sebelum menyentuh domain.** Kurva belajar diselesaikan di awal |
| A2 | `ExtractorAgent` — brief → bukti terstruktur + kutipan verbatim | 3–4 jam | Termasuk validasi kutipan setelah respons LLM |
| A3 | Aturan deal deterministik (10–12 aturan) | 3–4 jam | Kode murni, tanpa LLM. Paling mudah di-test |
| A4 | `compute_readiness()` | 1–2 jam | Memetakan bobot issue ke 3 state |
| A5 | `estimate_effort_range()` | 2–3 jam | Menolak menghitung kalau data kurang |
| A6 | `DealReadyAgent` root + orkestrasi tool | 4–5 jam | Bagian tersulit |
| A7 | Loop multi-putaran + seluruh pengaman | 3–4 jam | `MAX_ROUNDS`, deteksi readiness tidak naik, batas waktu |
| A8 | `DrafterAgent` — pertanyaan → pesan bahasa Indonesia | 2–3 jam | Kualitas bahasa penting untuk demo |
| A9 | Penulisan reasoning trace | 2 jam | Hook di setiap tool call & keputusan |

**Total: ~2 hari.** Ini yang dinilai 40%. Jangan dikorbankan demi UI.

## 3. Backend API

| # | Item | Perkiraan |
|---|---|---|
| B1 | Skeleton FastAPI + config + health check | 1 jam |
| B2 | Verifikasi ID token Firebase + dependency auth | 2 jam |
| B3 | `POST /runs` — buat run, publish ke Pub/Sub, balas 202 | 2 jam |
| B4 | `GET /runs`, `GET /runs/{id}`, `GET /runs/{id}/trace` | 2 jam |
| B5 | `POST /runs/{id}/client-reply` — masukkan jawaban klien, picu putaran baru | 2 jam |
| B6 | `POST /memory/corrections` — simpan koreksi user | 1 jam |
| B7 | Rate limit per user | 1 jam |
| B8 | Endpoint worker: push handler + idempotensi + verifikasi OIDC | 3 jam |

**Total: ~1 hari.**

## 4. Frontend

Sengaja tipis. Empat layar, tidak lebih.

| # | Layar | Perkiraan |
|---|---|---|
| F1 | Sign-in Google | 1–2 jam |
| F2 | Submit brief (satu textarea + tombol) | 1 jam |
| F3 | Daftar run beserta status | 2 jam |
| F4 | Detail run: bukti, issue, pertanyaan, draft pesan, tombol salin | 3–4 jam |
| F5 | Panel reasoning trace (bisa dilipat) | 2–3 jam |
| F6 | Form jawaban klien untuk memicu putaran berikutnya | 1–2 jam |

**Total: ~1 hari.** Rapi lebih penting daripada mewah. Yang dinilai adalah agent
dan arsitekturnya; UI cukup jelas dan tidak memalukan di video.

## 5. Test

| # | Item | Perkiraan | Kenapa |
|---|---|---|---|
| T1 | Unit test aturan deal (10–12 aturan) | 2 jam | Paling murah, paling meyakinkan |
| T2 | Test readiness & effort | 1 jam | |
| T3 | **Test isolasi per-user** | 1 jam | Cacat security di depan juri = fatal |
| T4 | **Test prompt injection** (US-6) | 1–2 jam | Pembeda; jarang dipunya peserta lain |
| T5 | Test pengaman loop (`MAX_ROUNDS`, readiness stagnan) | 1–2 jam | Bukti agent terkendali |
| T6 | Test idempotensi worker | 1 jam | Pub/Sub at-least-once |
| T7 | Test validasi kutipan verbatim | 1 jam | Bukti anti-halusinasi |

**Total: ~0,5–1 hari.** Target realistis 40–60 test bermakna. Jangan mengejar
angka; kejar yang benar-benar membuktikan sesuatu.

## 6. Deliverable submission

| # | Item | Perkiraan | Catatan |
|---|---|---|---|
| S1 | README dengan setup reproducible | 2–3 jam | Dinilai eksplisit oleh juri |
| S2 | Diagram arsitektur diekspor jadi PNG | 1 jam | Sumbernya sudah ada di `02-ARCHITECTURE.md` |
| S3 | Naskah + rekaman + edit video 4 menit | **4–6 jam** | **Paling sering diremehkan.** Bukan 1 jam |
| S4 | Teks deskripsi Devpost | 1–2 jam | |
| S5 | Isi form submission + share akses repo | 1 jam | |
| S6 | Bonus: post LinkedIn / blog | 1–2 jam | Hanya kalau MUST sudah aman |

**Total: ~1,5 hari.**

## 7. Rekap

| Kelompok | Perkiraan |
|---|---|
| Infrastruktur GCP | ~1 hari |
| Agent | ~2 hari |
| Backend API | ~1 hari |
| Frontend | ~1 hari |
| Test | ~0,5–1 hari |
| Deliverable submission | ~1,5 hari |
| **Subtotal** | **~7–7,5 hari** |
| Waktu tersedia | **7 hari** |

**Tidak ada buffer.** Ini harus dinyatakan terang-terangan, bukan disembunyikan
di balik optimisme.

Konsekuensinya, tiga hal ini wajib:

1. **Daftar WON'T di [`01-PRD.md`](01-PRD.md) 6.3 dipatuhi tanpa kompromi.**
   Setiap fitur tambahan memakan waktu yang tidak ada.
2. **Frontend adalah katup pelepas tekanan.** Kalau terlambat, potong F5 jadi
   JSON mentah dan F3 jadi daftar sederhana. Jangan pernah memotong agent atau
   test.
3. **Video dijadwalkan Hari 6, bukan Hari 7.** Kalau menunggu semuanya sempurna,
   videonya tidak akan pernah dibuat.

### Rencana pemangkasan kalau tertinggal

Urutan yang dikorbankan, dari yang pertama:

1. S6 (bonus post) — hilangkan tanpa ragu
2. F5 (panel trace cantik) — ganti tampilan JSON mentah
3. S2 (Vertex AI) — tetap di Gemini API
4. A5 (`estimate_effort_range`) — cukup sampai readiness saja, tanpa angka effort
5. F3 (daftar run) — cukup halaman detail per run

**Tidak pernah dikorbankan:** A6, A7 (loop agent), T3, T4 (test security),
I7 (deploy nyata), S3 (video).
