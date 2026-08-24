# 07 — Risiko & Keputusan Terbuka

Dua bagian: **keputusan yang menunggu Rifqi/partner** (blocker), dan **risiko
yang sudah diketahui** beserta mitigasinya.

---

# Bagian A — Keputusan yang masih menunggu

Kelimanya harus diputuskan **Hari 1**, sebelum menulis kode. Kalau tidak, ada
pekerjaan yang harus diulang.

## D-1 — Nama project & repo

**Status: belum diputuskan.**

"DealReady" adalah nama kerja yang saya pakai supaya dokumen ini bisa ditulis —
bukan pilihan final. Yang penting bukan namanya, tapi ini:

- Repo dibuat di **akun GitHub Rifqi sendiri**, bukan akun orang lain. Repo
  Baseline ada di `github.com/irham3/baseline`; memakai pola yang sama untuk
  submission akan menimbulkan pertanyaan kepemilikan di mata panitia.
- Nama jangan memakai kata "Baseline", supaya tidak tampak sebagai turunan dari
  project yang sedang diikutkan kontes lain.

**Butuh dari Rifqi:** nama final + repo dibuat.

## D-2 — Solo atau berdua partner

**Status: belum diputuskan.** Ini keputusan paling berdampak.

| | Solo | Berdua |
|---|---|---|
| Jam tersedia | ~35 jam | ~55–65 jam |
| Berhak hadiah Individual/Hobbyist ($10K, 2 pemenang) | Ya | `[verifikasi]` aturan panitia soal ini untuk tim |
| Biaya koordinasi | Nol | Nyata — kontrak data harus disepakati di awal |
| Risiko | Selisih ~15 jam harus ditutup dengan pemangkasan | Rendah, kalau pembagiannya jelas |

Kalau berdua, pakai pembagian di [`06-SETUP.md`](06-SETUP.md) bagian 10 dan
sepakati bentuk dokumen Firestore di Hari 1.

**Butuh dari Rifqi:** keputusan, dan kalau berdua — konfirmasi partner benar-benar
punya waktu di 29–30 Agustus.

## D-3 — Akun Google Cloud & billing

**Status: belum ada.**

Ini blocker paling keras karena **waktunya di luar kendali kita**. Verifikasi
billing kadang selesai dalam menit, kadang butuh berjam-jam.

**Butuh dari Rifqi:** kerjakan malam ini juga, sebelum apa pun yang lain.
Panitia menyediakan $150 credit — klaim sekalian.

## D-4 — Konfirmasi tidak ada benturan aturan

**Status: belum dicek.** `[verifikasi]`

Baseline sedang diikutkan kontes lain (platform Emergent) dan domain masalahnya
mirip dengan DealReady. Perlu dipastikan:

1. Aturan kontes Emergent tidak melarang peserta mengerjakan project lain di
   domain serupa.
2. DealReady benar-benar tidak memakai kode Baseline — sehingga tidak ada yang
   perlu didisclose ke Devpost dan tidak ada klaim kepemilikan yang tumpang
   tindih.

Poin 2 sudah ditegakkan lewat aturan "jangan salin kode" di seluruh paket
dokumen ini. Poin 1 butuh Rifqi membaca aturan kontes Emergent.

**Kalau ternyata ada benturan:** ganti domain masalahnya. Struktur agent,
arsitektur, dan rencana 7 hari di paket ini bisa dipakai ulang untuk domain lain
— misalnya kesiapan dokumen audit — tanpa mengubah desain teknisnya.

## D-5 — Menutup selisih 15 jam

**Status: belum diputuskan.**

Kebutuhan ~50 jam, tersedia ~35 jam. Pilihannya ada di
[`04-PLAN-7-DAYS.md`](04-PLAN-7-DAYS.md): ambil cuti, bagi kerja dengan partner,
atau pangkas sejak awal. Rencana harian saat ini ditulis dengan asumsi
**pangkas sejak awal** — paling konservatif.

**Butuh dari Rifqi:** pilih satu. Kalau memilih cuti atau partner, item SHOULD di
PRD bisa dikembalikan.

---

# Bagian B — Risiko

Diurutkan dari yang paling mungkin merusak submission.

## R-1 — Kurva belajar ADK memakan waktu terlalu banyak
**Kemungkinan: sedang. Dampak: fatal.**

ADK belum pernah dipakai Rifqi, dan dokumentasi framework agent berubah cepat.
Kalau ini baru ketahuan Hari 5, submission tidak akan jadi.

**Mitigasi:** Hari 2 dikhususkan untuk "hello world" ADK sebelum menyentuh
domain sama sekali. **Titik keputusan:** kalau Hari 2 berakhir tanpa agent
minimal yang jalan, ganti ke **Google GenAI SDK** — sama-sama sah menurut syarat
panitia dan lebih sederhana. Ganti di Hari 2 masih murah; di Hari 5 sudah tidak.

## R-2 — Deploy pertama ke Cloud Run + Pub/Sub gagal berjam-jam
**Kemungkinan: tinggi. Dampak: besar.**

Push subscription dengan OIDC hampir tidak pernah mulus di percobaan pertama;
kegagalannya biasanya IAM, dan pesan errornya tidak membantu.

**Mitigasi:** dijadwalkan Sabtu (Hari 6) yang punya waktu penuh, bukan malam
kerja. Kalau macet lebih dari 3 jam, **jatuhkan ke Cloud Tasks** atau — paling
buruk — worker yang mem-polling Firestore. Yang penting eksekusinya tetap asinkron
dan terpisah dari request; mekanisme antreannya bisa dinegosiasikan.

## R-3 — Video tidak sempat dibuat dengan layak
**Kemungkinan: tinggi. Dampak: besar — 30% bobot.**

Ini kegagalan paling umum di hackathon: kode jalan, tapi videonya direkam
terburu-buru satu jam sebelum deadline dan tidak menunjukkan apa pun.

**Mitigasi:** video dijadwalkan Hari 7 sore dengan alokasi 3 jam, naskahnya sudah
ditulis lengkap di [`05-SUBMISSION-CHECKLIST.md`](05-SUBMISSION-CHECKLIST.md).
**Aturan keras:** kalau Hari 7 siang produk belum siap direkam, rekam apa yang
sudah ada. Video dari produk yang belum lengkap jauh lebih baik daripada tidak
ada video.

## R-4 — ID model Gemini 3.5+ salah
**Kemungkinan: sedang. Dampak: fatal — gugur syarat wajib.**

Nama model tidak boleh ditebak, dan tidak boleh disalin dari dokumen mana pun di
paket ini.

**Mitigasi:** Hari 1 cek langsung ke dokumentasi resmi, catat di README, dan
tampilkan di video sebagai bukti.

## R-5 — Selisih waktu 15 jam tidak ditutup
**Kemungkinan: tinggi kalau D-5 tidak diputuskan. Dampak: besar.**

**Mitigasi:** daftar pemangkasan di [`03-BUILD-BREAKDOWN.md`](03-BUILD-BREAKDOWN.md)
bagian 7, dijalankan **sejak awal**, bukan sebagai penyelamat darurat di Hari 6.

## R-6 — Agent terlihat seperti chatbot biasa di mata juri
**Kemungkinan: sedang. Dampak: besar — menyerang bobot 40%.**

Kalau demonya cuma "paste teks, dapat jawaban", tidak ada bedanya dengan ratusan
submission lain.

**Mitigasi:** tiga hal ini **wajib** terlihat di video: (1) tab ditutup dan agent
tetap jalan, (2) reasoning trace yang menunjukkan tool deterministik dipanggil,
(3) agent berhenti sendiri dan mengatakan alasannya. Ketiganya adalah bukti
otonomi, bukan klaim otonomi.

## R-7 — Biaya Google Cloud membengkak
**Kemungkinan: rendah. Dampak: sedang.**

$150 credit sangat cukup untuk skala ini, tapi loop agent yang lepas kendali bisa
membakar kuota dengan cepat.

**Mitigasi:** `MAX_ROUNDS`, `MAX_TOOL_CALLS_PER_ROUND`, batas waktu run, dan rate
limit per user — semuanya sudah masuk desain di
[`02-ARCHITECTURE.md`](02-ARCHITECTURE.md) 3.3. Pasang juga budget alert di GCP
sejak Hari 1.

## R-8 — Kredensial ikut ter-commit
**Kemungkinan: rendah. Dampak: fatal untuk reputasi.**

Repo akan dibaca juri. API key yang bocor di repo publik adalah hal pertama yang
terlihat.

**Mitigasi:** `.gitignore` disiapkan **sebelum** commit pertama, secret hanya di
Secret Manager, dan jangan pernah men-download service account key ke laptop.

---

## Ringkasan: yang dibutuhkan dari Rifqi hari ini

1. **Buat akun Google Cloud + aktifkan billing + klaim $150 credit** — paling
   mendesak, karena waktunya di luar kendali kita
2. Putuskan **solo atau berdua partner** (D-2)
3. Putuskan **nama final + buat repo di akun sendiri** (D-1)
4. Cek **aturan kontes Emergent** soal benturan (D-4)
5. Putuskan **cara menutup selisih 15 jam** (D-5)
