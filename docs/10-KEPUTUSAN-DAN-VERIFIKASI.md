# 09 — Keputusan Terkunci & Hasil Verifikasi

Ditulis **25 Agustus 2026**, setelah review partner (dua kritik) dan pengecekan
langsung ke halaman aturan resmi + dokumentasi model Google.

> **Struktur dokumen per 25 Agustus 2026.** Paket revisi dari partner sudah
> masuk dan menjadi rencana kerja resmi: `00`-`07` + `09-DOMAIN-RULES.md`.
> Paket DealReady yang lama dipindahkan ke [`arsip-dealready/`](arsip-dealready/)
> sebagai riwayat, bukan rujukan. Dokumen ini (`10`) memuat keputusan terkunci
> dan fakta aturan yang sudah diverifikasi ke sumber resmi.

---

## 1. Keputusan yang sudah TERKUNCI

| Kode | Keputusan | Nilai |
|---|---|---|
| **D-1** | Nama produk | **Delividence** — final (sempat DealReady, lalu ScopeHandshake di paket revisi) |
| **D-1** | Repo submission | `github.com/irham3/delividence`, **public**, milik partner |
| — | Repo cadangan | `github.com/rifqiahmadpratama/dealready`, private, mirror milik Rifqi |
| — | Commit pertama | 25 Agustus 2026 — di dalam periode submission (3–31 Agustus) |
| **R-4** | Model | `gemini-3.7-flash` (lihat §3) |
| — | Rencana kerja | Paket revisi partner diadopsi; profil **Modul A saja** (§4b) |
| — | Stack | Next.js 16 + TypeScript + Tailwind 4 (web); Python 3.11 + FastAPI (API & worker) |

**Repo submission ada di akun partner, bukan akun Rifqi.** Itu sah untuk
submission tim — tetapi hanya kalau **keduanya benar-benar terdaftar sebagai tim
di Devpost dan undangannya sudah diterima**. Kalau tidak, submission berjalan atas
nama akun yang bukan milik Rifqi. Masuk checklist `05` sebagai item yang wajib
diverifikasi sebelum submit.

Repo sudah public, jadi syarat akses juri (V-7) terpenuhi tanpa perlu berbagi ke
`testing@devpost.com`.

## 2. Fakta yang sudah DIVERIFIKASI ke aturan resmi

Diambil 25 Agustus 2026 dari <https://allthingsagentichackathon.devpost.com/rules>.
Kutipan verbatim, bukan parafrase.

| # | Fakta | Kutipan |
|---|---|---|
| V-1 | **Aplikasi wajib mendukung English** | *"The Application must, at a minimum, support English language use. All Submission materials must be in English or, if not in English, the Entrant must provide an English translation."* |
| V-2 | Video ≤ 4 menit | *"It should not be longer than 4 minutes. If it is longer than 4 minutes, only the first 4 minutes may be evaluated."* |
| V-3 | Video wajib publik di YouTube/Vimeo | *"Submission must be uploaded to and made publicly visible on YouTube or Vimeo"* |
| V-4 | Video wajib English / subtitle English | *"It must be in English or include English subtitles."* |
| V-5 | Video wajib menunjukkan eksekusi **live, tidak diedit** + backend di Google Cloud | Rules menuntut *unedited, live execution of the agent* |
| V-6 | Cutoff klaim credit | *"August 28th at 12:00 pm PT or while supplies last"* |
| V-7 | **Project wajib bisa diakses juri, gratis, tanpa restriksi, sampai judging selesai** | *"The Entrant must make the Project available free of charge and without any restriction, for testing, evaluation and use by the Sponsor, Administrator and Judges until the Judging Period ends."* |
| V-8 | Syarat teknis | *"Gemini 3.5 or newer accessed through Gemini API or Vertex AI"*; framework: *"Google ADK, GenAI SDK, Antigravity SDK or GenKit"*; *"at least one Google Cloud infrastructure service"* |
| V-9 | Project wajib baru + disclosure | *"Projects must be newly created during the Submission Period. Participants may use standard development tools... but must disclose any other pre-existing code or work incorporated into the Project."* |
| V-10 | **Individual/Hobbyist terbuka untuk tim** | *"All eligible individuals and/or team participants"* — 2 pemenang |

### Dampak yang mengubah rencana

**V-1 — blocker eligibility.** Rencana lama (`05` baris 114) mengizinkan UI dan
output draft berbahasa Indonesia saja. Itu melanggar. UI dan seluruh alur kerja
**wajib bisa dipakai dalam bahasa Inggris**; lokalisasi Indonesia jadi opsi
tambahan, bukan default satu-satunya.

**V-7 — bertabrakan dengan Google Sign-In.** Kalau aplikasi dikunci di balik
login Google, juri harus tetap bisa masuk. Siapkan **akun testing + kredensial
yang ditulis di form submission**, atau mode demo tanpa login. Ini belum ada di
dokumen mana pun.

**V-10 — mematahkan alasan solo.** `07 D-2` menyebut hadiah Individual/Hobbyist
sebagai keunggulan bekerja solo. Itu **salah**: aturan menyebut tim juga
eligible. Jadi solo-vs-berdua murni soal jam kerja, bukan soal hadiah.

**V-5 vs tips penyelenggara.** Aturan menuntut eksekusi live tak diedit; tips
penyelenggara menyarankan jump cut. Kompromi yang aman: potong waktu mati di
sekeliling, **pertahankan alur inti sebagai satu take utuh**, jangan pernah
memalsukan hasil.

## 3. ID model — koreksi atas kritik partner

Dicek 25 Agustus 2026 ke <https://ai.google.dev/gemini-api/docs/models>.

Kritik partner menyebut `gemini-3.5-flash` sebagai "the exact stable model code".
Benar bahwa model itu ada dan berstatus GA — tetapi Google kini mendeskripsikannya
sebagai ***"our legacy Flash model, providing baseline speed"***. Roster Flash
stabil saat ini:

| Model | Status | Deskripsi resmi Google |
|---|---|---|
| **`gemini-3.7-flash`** | Stabil (GA) | *"Our latest and most capable Flash model, built for complex coding"* |
| `gemini-3.6-flash` | Stabil (GA) | *"Our previous-generation Flash model, balancing speed and multimodal capabilities"* |
| `gemini-3.5-flash` | Stabil (GA) | *"Our legacy Flash model, providing baseline speed"* |

**Keputusan:** default **`gemini-3.7-flash`**. Ketiganya memenuhi syarat "3.5 or
newer", jadi memakai 3.5 berarti sengaja memilih yang paling tua tanpa alasan.
Kalau jalur multimodal (§4) diambil, evaluasi `gemini-3.6-flash` — deskripsi
resminya secara eksplisit menyebut kemampuan multimodal.

`[verifikasi]` masih harus dibuktikan dengan panggilan API nyata; catat metadata
respons sebagai bukti, dan pastikan ketersediaan model di region yang dipilih
kalau memakai Vertex AI (`06 §3` mem-pin `asia-southeast2`).

## 4. Rekonsiliasi scope — dua kritik, satu anggaran jam

Kedua kritik benar bahwa jam kerja defisit berat. Tapi keduanya juga **menambah**
scope. Karena itu penyesuaian dijalankan sebagai **trade**: setiap item masuk,
ada yang keluar.

Anggaran nyata per 25 Agustus: Sel–Jum malam ~12 jam + Sabtu–Minggu ~20 jam =
**~32 jam**. Senin 31 Agustus malam hanya buffer tipis (deadline 1 September
07:00 WIB).

### Masuk

| Item | Alasan |
|---|---|
| **Vertical slice cloud didahulukan** — `POST → Pub/Sub → worker → Firestore` di Cloud Run sebelum logika produk apa pun (~3j) | Membunuh R-2 di hari pertama, bukan Sabtu malam. Sekaligus bukti "jalan di Google Cloud" sejak awal |
| **UI English-first + selector bahasa output** | V-1, blocker eligibility. Murah dari commit pertama, mahal kalau di-retrofit Hari 6 |
| **Idempotensi nyata**: dokumen create-only berkunci `{run_id}:{round}` dalam transaksi Firestore, + dead-letter topic + batas retry (~45 mnt) | Field `idempotency_key` saja tidak menegakkan apa pun. Menyerang bobot 30% |
| **Vertex AI + ADC jadi default** (bukan stretch goal) | Menghapus langkah API key di Secret Manager; log Vertex diterima sebagai bukti backend di Google Cloud. **Cek ketersediaan model di region dulu** |
| **Primitives ADK** — `LoopAgent(max_iterations=N)` + `exit_loop`, guardrail & audit trail lewat `before_tool_callback`/`after_tool_callback` | Lebih sedikit kode ditulis tangan, cerita arsitektur jauh lebih kuat |
| **Rename "Memory Bank"** → "cross-session memory (Firestore)" | Memory Bank produk Google sungguhan (Vertex AI Agent Engine). Memakai namanya terbaca sebagai klaim palsu |
| **Koreksi klaim "2 aksi"** di `01 §8` | Alur nyata ~7 aksi manual. Klaim yang tidak tahan cek merusak kepercayaan juri lebih besar daripada nilai klaimnya |
| **Output jadi Scope Ledger ter-versi** | Bukan fitur baru — reframing output yang sudah dirancang (evidence, issues, readiness) menjadi artefak yang bermutasi. Biayanya di UI, bukan di mesin |
| **Kredensial testing untuk juri** | V-7. Belum ada di dokumen mana pun |
| **Draft submission Devpost Hari 5** + video cadangan Sabtu malam | Jangan pernah membuka form itu pertama kali di hari terakhir |

### Keluar

| Item | Alasan |
|---|---|
| `estimate_effort_range()` | Dibuang total, hemat 2–3j. Sudah #4 di cut-list sendiri, dan menambah liabilitas kalibrasi |
| Model Armor | +1 service tapi bukan pembeda; guardrail sendiri sudah cukup |
| Pertanyaan 5 → **3** | Lebih mudah dijawab klien, lebih baik di demo 4 menit |
| Eval dataset 12 brief → **8** | Tetap mencakup: ambigu, lengkap, kontradiktif, injection, multi-putaran |
| Polish daftar run, analytics, visualisasi trace mewah, rate-limit canggih | Tidak menyentuh kriteria penilaian mana pun |
| Target 40–60 test → **15–25 test bernilai tinggi** | Jumlah test bukan kriteria penilaian |

### Stretch — hanya kalau Hari 6 sudah aman

| Item | Catatan |
|---|---|
| **Cloud Scheduler nudge** | ~1.5j. Satu-satunya perbaikan murah untuk klaim otonomi (bobot 40%) — run idle bangun sendiri dan menyusun follow-up. Prioritaskan di atas multimodal |
| **Multimodal** (screenshot & voice note brief) | Best Multimodal UX punya 2 pemenang, dan brief WhatsApp asli memang datang sebagai screenshot. ~2j. **Komitmen hanya setelah alur inti hijau** |

## 4b. Profil modul — diputuskan di depan, bukan saat kepepet

Paket revisi mengestimasi **46–50 jam** (expected) sampai **60–70 jam**
(pesimistis), dengan anggaran 35 jam yang sudah basi: blok "Selasa 25, 3 jam"
adalah hari ini dan sebagian besar sudah lewat. Realistis tersisa **~29–32 jam**.

Paket itu juga memuat satu kontradiksi yang harus dicatat supaya tidak menyesatkan
saat panik: `04 §1` menyebut yang dipotong lebih dulu adalah polish, PDF, email,
memory UI, dan evidence adapter — sementara `03 §5` menyatakan hal-hal itu
**sudah** berada di SHOULD/WON'T dan "bukan slack dari MUST dan tidak dihitung
sebagai cut". Artinya cadangan pemotongan yang dijanjikan `04` sebenarnya tidak ada.

**Keputusan: jalankan tangga degradasi `03 §5` sejak sekarang.**

| Modul | Status | Yang wajib ikut dihapus |
|---|---|---|
| **A** — criterion identity & baseline versioning | **DIBANGUN** | — |
| **C** — drift ledger | **DILEPAS** | panel drift disembunyikan; beat drift dihapus dari naskah video |
| **B** — revision rounds | **DILEPAS** | revision counter & exhausted-round routing disembunyikan |
| **D** — conflict resolution | **DILEPAS** | fixture konflik Friday/Monday ikut dilepas — mempertahankannya tanpa D membuat golden path deadlock |

Yang dihemat: seluruh WP-2b (4.5 jam), sebagian besar matriks 45 test, dan potongan
besar WP-5/WP-6 — tanpa menyentuh pembeda utama: portal klien tanpa akun, Pub/Sub
resume, provenance, deterministic readiness, baseline tak tertimpa, cited
comparison, evidence-to-criterion acceptance, dan deployment.

Setiap degradasi wajib masuk known limitations, dan **semua klaim, test, serta beat
video terkait ikut dihapus** — bukan dibiarkan mengklaim fitur yang tidak ada.

## 5. Yang MASIH terbuka

| Kode | Keputusan | Catatan |
|---|---|---|
| **D-2** | Solo atau berdua partner | Alasan hadiah sudah gugur (V-10). Murni soal jam: ~32j solo vs ~55j berdua |
| **D-4** | Benturan aturan kontes Emergent | Belum dicek. Selama belum, repo ditahan private |
| **D-5** | Cara menutup selisih jam | Rencana saat ini mengasumsikan "pangkas sejak awal" (§4) |

## 6. Hari 1 yang belum dikerjakan — jamnya di luar kendali kita

- [ ] Aktifkan billing Google Cloud + **klaim $150 credit sebelum 28 Agustus 12:00 PT** (V-6)
- [ ] Daftar & join hackathon di Devpost; kalau berdua, partner **accept undangan tim**
- [ ] Pasang Google Cloud SDK (`gcloud` belum ada di mesin ini)
- [ ] Aktifkan API: Cloud Run, Pub/Sub, Firestore, Secret Manager, Artifact Registry, Cloud Build
- [ ] Pasang budget alert (R-7)
