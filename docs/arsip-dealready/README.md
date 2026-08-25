# DealReady — Paket Dokumen Project

Paket dokumen perencanaan untuk **project baru** yang akan diikutkan ke
**All Things Agentic Hackathon (Google × Devpost)**.

Folder ini **self-contained**. Boleh di-zip dan dikirim ke partner, atau ditaruh
di komputer lain apa adanya. Tidak ada dependensi ke file lain di luar folder ini.

---

## PENTING — hubungan dengan Baseline

Project ini **bukan** kelanjutan, bukan fork, dan bukan modifikasi dari
`baseline-app`.

| | |
|---|---|
| **Baseline** (`C:\Users\ASUS\Projects\baseline-app`) | Project lain milik Rifqi & partner, kontes terpisah, tayang di platform Emergent. **Read-only. Tidak boleh diubah, tidak boleh dipakai sebagai basis kode.** |
| **DealReady** (folder ini) | Project baru dari nol. Meminjam *cara berpikir* Baseline — bukti sebelum keyakinan, AI mengekstrak & kode yang menghitung — tapi kodenya ditulis ulang sepenuhnya. |

Kenapa dipisah tegas:
1. Aturan hackathon menuntut project **dibuat baru selama periode submission**.
   Project yang lahir 24 Agustus 2026 jelas memenuhi itu tanpa perlu berdebat.
2. Menghindari benturan dengan kontes lain yang sudah diikuti Baseline.
3. Repo Baseline bukan milik akun Rifqi (`github.com/irham3/baseline`), jadi
   memakainya sebagai basis submission menimbulkan pertanyaan kepemilikan.

**Aturan kerja: boleh membaca Baseline untuk inspirasi konsep. Dilarang
menyalin-tempel kode dari sana, dan dilarang mengubah apa pun di sana.**

---

## Status paket

| Item | Nilai |
|---|---|
| Nama | **DealReady** — **final** per 25 Agu 2026 |
| Disusun | 24 Agustus 2026 |
| Deadline submission | **31 Agustus 2026, 17:00 PT** = 1 September 2026, 07:00 WIB |
| Sisa waktu | ~6 hari (~32 jam kerja realistis — lihat [`09`](09-KEPUTUSAN-DAN-VERIFIKASI.md) §4) |
| Kategori | **The Collaborative Partner** |
| Repo | <https://github.com/rifqiahmadpratama/dealready> — private, commit pertama 25 Agu 2026 |
| Status kode | **Nol baris.** Belum ada apa pun yang dibangun |

> Dokumen ini rencana, bukan laporan. Belum ada kode, belum ada deploy, belum ada
> verifikasi. Klaim yang belum diuji ditandai `[verifikasi]`.

---

## Urutan baca

Partner yang baru masuk: baca berurutan, sekitar 25 menit.

| # | File | Isi | Untuk |
|---|---|---|---|
| 00 | [`00-BRIEF.md`](00-BRIEF.md) | Aturan hackathon: deadline, syarat wajib, kriteria juri, hadiah | Semua |
| 01 | [`01-PRD.md`](01-PRD.md) | Produk apa, untuk siapa, scope MVP, user story, kriteria terima | Semua |
| 02 | [`02-ARCHITECTURE.md`](02-ARCHITECTURE.md) | Arsitektur, diagram, desain agent, model data, keputusan teknis | Engineer |
| 03 | [`03-BUILD-BREAKDOWN.md`](03-BUILD-BREAKDOWN.md) | Rincian yang harus dibangun, per komponen, dengan perkiraan waktu | Engineer |
| 04 | [`04-PLAN-7-DAYS.md`](04-PLAN-7-DAYS.md) | Rencana harian: langkah → cara verifikasi | Semua |
| 05 | [`05-SUBMISSION-CHECKLIST.md`](05-SUBMISSION-CHECKLIST.md) | Checklist Devpost + kerangka video 4 menit | Semua |
| 06 | [`06-SETUP.md`](06-SETUP.md) | Menyiapkan dan menjalankan dari nol di komputer mana pun | Engineer |
| 07 | [`07-RISKS-DECISIONS.md`](07-RISKS-DECISIONS.md) | Risiko + keputusan yang **masih menunggu Rifqi/partner** | Semua |
| 08 | `08-CRITIQUE-AND-REVISED-PLAN.md` | Kritik & rencana revisi dari partner — **belum ada di folder ini**, masih di mesin partner | Semua |
| 09 | [`09-KEPUTUSAN-DAN-VERIFIKASI.md`](09-KEPUTUSAN-DAN-VERIFIKASI.md) | **Baca ini setelah 00.** Keputusan terkunci, fakta aturan yang sudah diverifikasi, rekonsiliasi scope | Semua |

---

## Ringkasan satu paragraf

Freelancer menerima brief klien yang ambigu lewat WhatsApp, lalu menyanggupi
harga sebelum tahu berapa putaran revisi, siapa yang menyetujui, dan apa batas
perubahannya — dan proyeknya melar tanpa tambahan bayaran. **DealReady** adalah
agent yang menerima brief itu sekali, lalu bekerja sendiri di background:
mengekstrak bukti dari teks, menilai celah dengan aturan deterministik, memutuskan
pertanyaan mana yang benar-benar penting, menyiapkan draft pesan siap kirim,
menunggu jawaban klien, mengevaluasi ulang, dan berhenti hanya ketika brief aman
untuk di-quote — sambil mengingat koreksi user supaya putaran berikutnya lebih
kalibrasi. Prinsip yang dipegang: **AI mengekstrak dan mengorkestrasi, kode
deterministik yang menghitung.**

---

## Yang masih harus diputuskan sebelum menulis kode

Blocker, bukan detail. Status terbaru di
[`09-KEPUTUSAN-DAN-VERIFIKASI.md`](09-KEPUTUSAN-DAN-VERIFIKASI.md) §1 & §5.

1. ~~**Nama project & repo baru.**~~ **Selesai** — DealReady,
   `github.com/rifqiahmadpratama/dealready`.
2. **Akun Google Cloud + billing.** Belum ada. Paling mendesak: klaim $150 credit
   punya cutoff **28 Agustus 12:00 PT**, dan verifikasi billing di luar kendali kita.
3. **Solo atau berdua partner?** Menentukan pembagian kerja. Catatan: alasan
   hadiah Individual/Hobbyist **sudah gugur** — aturan menyebut tim juga eligible.
4. **Konfirmasi tidak ada benturan aturan** dengan kontes yang sedang diikuti
   Baseline, mengingat domain masalahnya mirip. Selama ini belum dicek, repo
   ditahan private.
5. **Cara menutup selisih jam.** Kebutuhan jauh di atas ~32 jam yang tersedia.
