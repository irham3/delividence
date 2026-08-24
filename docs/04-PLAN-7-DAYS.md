# 04 — Rencana 7 Hari

Format tiap langkah: **apa yang dikerjakan → cara memverifikasi bahwa itu
benar-benar selesai.** Sebuah langkah tidak dianggap selesai karena "sudah
ditulis", tapi karena verifikasinya lulus.

---

## Realita waktu — baca ini dulu

| | |
|---|---|
| Deadline | 31 Agustus 2026, 17:00 PT = **1 September 2026, 07:00 WIB** |
| Hari ini | Senin, 24 Agustus 2026 |
| Target submit | **Minggu, 30 Agustus** — bukan hari terakhir |

**Kendala yang tidak boleh diabaikan:** Rifqi bekerja penuh waktu sebagai
Internal Auditor. Hari Senin–Jumat realistis hanya ~3 jam per malam. Sabtu dan
Minggu bisa penuh.

| | Jam tersedia |
|---|---|
| 5 malam kerja (Sen–Jum) × 3 jam | ~15 jam |
| Sabtu 29 + Minggu 30 penuh | ~20 jam |
| **Total realistis** | **~35 jam** |
| Perkiraan kebutuhan di [`03-BUILD-BREAKDOWN.md`](03-BUILD-BREAKDOWN.md) | **~50 jam** |

**Ada selisih ~15 jam.** Ini harus diselesaikan sekarang, bukan ditemukan hari
Jumat. Tiga pilihan:

1. **Ambil cuti 1–2 hari** di Kamis/Jumat. Menutup selisih paling bersih.
2. **Kerjakan berdua partner** dengan pembagian tegas: satu di agent + backend,
   satu di frontend + video. Perlu kesepakatan di Hari 1.
3. **Pangkas dari sekarang**, jalankan daftar pemangkasan di
   [`03-BUILD-BREAKDOWN.md`](03-BUILD-BREAKDOWN.md) bagian 7 sejak awal — bukan
   sebagai penyelamat darurat.

Rencana di bawah ditulis dengan asumsi **pilihan 3** (paling konservatif). Kalau
pilihan 1 atau 2 diambil, tambahkan kembali item SHOULD dari PRD.

---

## Hari 1 — Senin 24 Agustus (~3 jam)
**Tema: buka semua pintu yang butuh menunggu orang lain.**

| Langkah | Verifikasi |
|---|---|
| Buat akun Google Cloud, aktifkan billing, klaim $150 credit | `gcloud auth list` menampilkan akun; project muncul di console dengan billing **Active** |
| Aktifkan API: Cloud Run, Pub/Sub, Firestore, Secret Manager, Artifact Registry | `gcloud services list --enabled` memuat kelima API |
| Buat repo GitHub baru **di akun Rifqi sendiri**, commit folder `docs/` ini | Repo ada, commit pertama tercatat 24 Agustus 2026 |
| Putuskan: solo atau berdua; kalau berdua, sepakati pembagian kerja | Tertulis di [`07-RISKS-DECISIONS.md`](07-RISKS-DECISIONS.md), bukan cuma diobrolkan |
| `[verifikasi]` Cek ID model Gemini 3.5+ yang tersedia, catat di README | ID model tercatat dari dokumentasi resmi, bukan tebakan |

**Kriteria selesai Hari 1:** billing aktif dan repo hidup. Kalau billing belum
beres malam ini, **itu masalah paling mendesak** — semua langkah berikutnya
menunggu di belakangnya.

---

## Hari 2 — Selasa 25 Agustus (~3 jam)
**Tema: selesaikan kurva belajar ADK sebelum ia menabrak hari terakhir.**

| Langkah | Verifikasi |
|---|---|
| ADK "hello world": satu agent, satu tool dummy, jalan lokal | Perintah lokal memanggil agent, tool benar-benar terpanggil, output tercetak |
| Skeleton FastAPI + health check + struktur folder | `GET /health` mengembalikan 200 di lokal |
| Sambungkan ADK ke Gemini 3.5+ dengan API key dari Secret Manager | Satu prompt nyata mendapat balasan nyata dari model yang benar |

**Kriteria selesai Hari 2:** ADK terbukti jalan di mesin Rifqi. Kalau macet di
sini, **berhenti dan pertimbangkan GenAI SDK** sebagai ganti ADK — keduanya sah
menurut aturan panitia, dan lebih baik ganti sekarang daripada Hari 5.

---

## Hari 3 — Rabu 26 Agustus (~3 jam)
**Tema: bangun otak deterministik. Tidak butuh cloud, tidak butuh LLM.**

| Langkah | Verifikasi |
|---|---|
| Tulis 10–12 aturan deal (`rules.py`) | Setiap aturan punya minimal 1 test; semua hijau |
| `compute_readiness()` — memetakan bobot issue ke 3 state | Test: brief kosong → `not_ready`; brief lengkap → `ready_to_quote` |
| `estimate_effort_range()` | Test: data kurang → **menolak menghitung**, bukan mengarang |

**Kriteria selesai Hari 3:** `pytest` hijau, dan semua ini berjalan **tanpa
memanggil LLM sama sekali**. Ini bukti hidup prinsip "kode yang menghitung".

Bagian ini sengaja ditaruh di malam kerja: paling tidak butuh internet, paling
mudah dikerjakan dalam potongan waktu pendek.

---

## Hari 4 — Kamis 27 Agustus (~3 jam)
**Tema: LLM mulai masuk, tapi dikurung.**

| Langkah | Verifikasi |
|---|---|
| `ExtractorAgent`: brief → bukti terstruktur + kutipan verbatim | Brief contoh menghasilkan `stated`/`inferred`/`missing` yang benar |
| Validasi kutipan **di kode** setelah LLM merespons | Test: LLM mengarang kutipan yang tidak ada di brief → ditolak sistem |
| Test prompt injection pertama | Brief berisi "abaikan instruksi sebelumnya" tidak mengubah perilaku agent |

**Kriteria selesai Hari 4:** ekstraksi jalan, dan **tidak dipercaya begitu saja**
— setiap kutipan diverifikasi kode.

---

## Hari 5 — Jumat 28 Agustus (~3 jam)
**Tema: jadikan ia agent, bukan pemanggil fungsi.**

| Langkah | Verifikasi |
|---|---|
| `DealReadyAgent` root + orkestrasi tool | Satu run lokal memanggil extractor lalu tool deterministik, berurutan |
| Loop multi-putaran + seluruh pengaman | Test: `MAX_ROUNDS` ditegakkan; readiness stagnan → `STALLED`, bukan berputar |
| Penulisan reasoning trace | Satu run menghasilkan daftar langkah lengkap dengan alasan tiap langkah |
| `DrafterAgent` → pertanyaan jadi pesan bahasa Indonesia | Draft terbaca wajar, maksimal 5 pertanyaan, semuanya berasal dari celah nyata |

**Kriteria selesai Hari 5:** satu run penuh berjalan **lokal**, dari brief sampai
draft pesan, dengan trace lengkap. Belum di cloud — itu besok.

---

## Hari 6 — Sabtu 29 Agustus (~10 jam)
**Tema: pindahkan ke Google Cloud. Hari terberat.**

| Langkah | Verifikasi |
|---|---|
| Firestore: koleksi + aturan keamanan | Tulis/baca dari lokal berhasil; akses lintas-user ditolak |
| Firebase Auth + verifikasi ID token di FastAPI | Sign-in menghasilkan token; endpoint menolak token palsu |
| Endpoint API: `POST /runs`, `GET /runs/{id}`, trace, client-reply | Test API hijau di lokal |
| Pub/Sub topic + push subscription + OIDC | Publish manual memicu worker; permintaan tanpa OIDC ditolak |
| Idempotensi worker | Test: pesan yang sama dikirim dua kali diproses **sekali** |
| **Deploy pertama ke Cloud Run** (api + worker) | URL Cloud Run hidup; run end-to-end selesai di cloud |
| Memory Bank: simpan koreksi, dibaca run berikutnya | Test: koreksi user terlihat pengaruhnya di run kedua |
| **Test isolasi per-user** | Test: user A tidak bisa membaca run/memory/trace user B |

**Kriteria selesai Hari 6:** satu brief dikirim ke URL Cloud Run yang nyata, agent
memprosesnya di background, hasilnya terbaca. **Ini titik tidak-bisa-mundur.**
Kalau Sabtu malam ini belum tercapai, jalankan daftar pemangkasan besok pagi
tanpa berdebat.

---

## Hari 7 — Minggu 30 Agustus (~10 jam)
**Tema: bikin bisa dilihat orang, lalu submit. Hari ini submit, bukan besok.**

Pagi (~4 jam):

| Langkah | Verifikasi |
|---|---|
| Frontend: sign-in, submit brief, daftar run, detail run | Alur penuh jalan di browser terhadap backend Cloud Run |
| Panel trace | Trace terbaca dari UI, bukan cuma dari log |
| Form jawaban klien → memicu putaran berikutnya | Putaran kedua benar-benar jalan dari UI |
| Deploy frontend ke Cloud Run | URL publik bisa dibuka dari perangkat lain |

Siang (~3 jam):

| Langkah | Verifikasi |
|---|---|
| README dengan setup reproducible | **Orang lain** mengikuti README dari nol dan berhasil jalan |
| Ekspor diagram arsitektur jadi PNG | File gambar ada, terbaca jelas |
| Rapikan `pytest`, pastikan semua hijau | Output test disalin ke README |

Sore (~3 jam):

| Langkah | Verifikasi |
|---|---|
| **Rekam video 4 menit** (kerangka di [`05-SUBMISSION-CHECKLIST.md`](05-SUBMISSION-CHECKLIST.md)) | Durasi ≤ 4 menit; bukti deploy GCP terlihat di layar |
| Tulis deskripsi Devpost | Semua field terisi |
| **SUBMIT** | Halaman submission Devpost menunjukkan status terkirim |
| Kalau repo private, share ke `testing@devpost.com` dan `cloudhackathons@google.com` | Undangan kolaborator terkirim |

**Kriteria selesai Hari 7: sudah tersubmit.** Bukan "hampir", bukan "tinggal
video".

---

## Hari 8 — Senin 31 Agustus (cadangan)

Hanya untuk perbaikan darurat. Deadline sesungguhnya **1 September 07:00 WIB**,
jadi Senin malam masih ada — tapi **jangan direncanakan sebagai hari kerja.**
Devpost mengizinkan pembaruan submission sebelum deadline, jadi submit lebih awal
tidak menutup pintu perbaikan.

---

## Aturan harian

1. **Setiap hari berakhir dengan `pytest` hijau.** Tidak ada pengecualian.
2. **Setiap hari berakhir dengan commit dan push.** Riwayat git adalah bukti
   "newly created during the Submission Period" — dan bukti itu hanya berlaku
   kalau tanggalnya benar-benar tercatat.
3. **Kalau satu hari meleset, jangan tambah jam besok — pangkas scope.**
   Menambah jam pada orang yang bekerja penuh waktu berujung ke Hari 7 yang
   berantakan.
4. **Jangan pernah memangkas: loop agent, test security, deploy nyata, video.**
   Empat ini adalah submission-nya. Sisanya bisa dinegosiasikan.
