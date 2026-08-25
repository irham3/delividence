# 05 — Checklist Submission & Naskah Video

Dikerjakan Hari 7 (Minggu, 30 Agustus). Jangan menunggu Hari 8.

---

## 1. Checklist deliverable Devpost

### Wajib

- [ ] **Kategori dipilih:** The Collaborative Partner
- [ ] **URL project yang di-host** — URL Cloud Run frontend. Kalau tidak sempat,
      boleh dikosongkan; aturan panitia menyebut project tidak wajib live
- [ ] **Deskripsi teks** — lihat kerangka di bagian 3
- [ ] **Repo kode** — GitHub di akun Rifqi sendiri
- [ ] Kalau repo **private**: undang `testing@devpost.com` dan
      `cloudhackathons@google.com` sebagai kolaborator
- [ ] **README.md** dengan setup reproducible — lihat bagian 4
- [ ] **Diagram arsitektur** (PNG) — ekspor dari `02-ARCHITECTURE.md` bagian 1
- [ ] **Video demo ~4 menit** — naskah di bagian 2

### Bonus (hanya kalau yang wajib sudah aman)

- [ ] Post LinkedIn — paling murah, dan Rifqi memang aktif di sana
- [ ] Blog post di Medium
- [ ] Integrasi model Google lain (Gemma / Veo / Lyria) — **lewati**, tidak
      sepadan dengan sisa waktu

### Pemeriksaan terakhir sebelum menekan submit

- [ ] Repo bisa dibuka dari jendela penyamaran (incognito), atau kolaborator
      sudah diundang
- [ ] Branch default repo memuat kode final — **bukan branch kerja**
- [ ] Tidak ada API key, `.env`, atau kredensial ikut ter-commit
- [ ] README memuat perintah yang benar-benar sudah dijalankan, bukan yang
      diasumsikan jalan
- [ ] Video bisa diputar oleh orang lain (setelan berbagi benar, bukan "private")
- [ ] Durasi video ≤ 4 menit
- [ ] Bukti deploy Google Cloud **terlihat di layar** dalam video
- [ ] Git history menunjukkan commit pertama di dalam periode 3–31 Agustus 2026

---

## 2. Naskah video 4 menit

Alokasi ketat. Juri menonton banyak video; 30 detik pertama menentukan.

### Segmen 1 — Masalah (0:00–0:40)

Tunjukkan brief WhatsApp asli di layar:

> "Bro bisa bantu edit video buat konten IG kita? Ada beberapa video, deadline
> minggu depan ya. Budget 2 juta. Nanti dirapihin aja yang bagus."

Narasi (inti, jangan dibaca kaku):

> Brief ini terlihat lengkap — ada budget, ada deadline. Tapi tidak ada jumlah
> video, tidak ada batas revisi, tidak ada siapa yang menyetujui, dan "dirapihin
> yang bagus" itu tidak punya batas. Freelancer tetap menyanggupi harganya, lalu
> proyeknya melar tanpa tambahan bayaran. Masalahnya bukan mereka tidak tahu
> harus bertanya — masalahnya menyusun pertanyaan yang benar untuk setiap calon
> klien itu melelahkan, dan sebagian besar calon klien tidak jadi.

### Segmen 2 — Value proposition (0:40–1:10)

> DealReady menerima brief itu sekali. Agent-nya bekerja sendiri di background:
> membaca, menilai celahnya dengan aturan deterministik, memutuskan pertanyaan
> mana yang benar-benar menentukan risiko, dan menyiapkan pesan siap kirim.
> Freelancer cuma melakukan dua hal: forward brief, lalu approve.

Tampilkan diagram arsitektur ~5 detik di sini.

### Segmen 3 — Demo langsung (1:10–3:00) — **porsi terbesar**

Urutan yang harus terlihat, jangan diubah:

1. Tempel brief, klik submit. **Tunjukkan responsnya instan** dan katakan agent
   berjalan di background — lalu **tutup tabnya**. Ini bukti asinkron.
2. Buka lagi. Run sudah maju sendiri.
3. Tampilkan bukti terekstrak, dan **sorot kutipan verbatim**-nya:
   > Setiap fakta yang diklaim ada di brief membawa kutipan aslinya. Kalau model
   > mengarang kutipan, kode menolaknya.
4. Tampilkan pertanyaan yang disusun agent + draft pesan bahasa Indonesia.
5. **Buka panel reasoning trace.** Ini momen terkuat:
   > Ini yang dikerjakan agent, langkah per langkah. Perhatikan: penilaian dan
   > angkanya keluar dari fungsi deterministik, bukan dari model bahasa. Model
   > mengekstrak dan menyusun kalimat; kode yang menghitung. Karena itu hasilnya
   > bisa diulang dan bisa diaudit.
6. Tempel jawaban klien → agent jalan lagi → readiness naik → agent **berhenti
   sendiri**.
   > Agent memutuskan sendiri kapan cukup. Ada batas putaran, dan kalau jawaban
   > klien tidak menambah informasi, ia berhenti dan mengatakannya — tidak
   > bertanya berulang-ulang.

### Segmen 4 — Bukti Google Cloud + penutup (3:00–4:00)

Rekam layar console GCP:

- Cloud Run: tiga service berjalan (`web`, `api`, `worker`)
- Pub/Sub: topic dan subscription
- Firestore: dokumen run yang tadi dibuat, terlihat nyata
- Sebutkan: Gemini 3.5+, Google ADK, Firebase Auth, Secret Manager

Penutup:

> Dibangun dengan Google ADK dan Gemini di atas Cloud Run, Pub/Sub, dan
> Firestore. Semua kode dan instruksi setup ada di repo.

### Aturan produksi

- **Rekam suara terpisah dari layar**, lalu gabungkan. Merekam keduanya sekaligus
  sambil gugup adalah cara tercepat menghabiskan 3 jam.
- Latihan sekali, rekam maksimal dua kali. Jangan mengejar sempurna.
- **SALAH — sudah dikoreksi, lihat [`09`](09-KEPUTUSAN-DAN-VERIFIKASI.md) V-1.**
  ~~UI dan draft pesan boleh tetap bahasa Indonesia.~~ Aturan resmi: *"The
  Application must, at a minimum, support English language use."* **UI dan
  seluruh alur kerja wajib bisa dipakai dalam bahasa Inggris.** Lokalisasi
  Indonesia ditampilkan sebagai selector bahasa output, bukan sebagai
  satu-satunya mode.
- Narasi bahasa Inggris, dan **video wajib punya subtitle English** meski
  narasinya sudah English (V-4).
- **Video wajib publik di YouTube atau Vimeo** (V-3), dan wajib menampilkan
  eksekusi **live yang tidak diedit** (V-5) — potong waktu mati di sekeliling,
  tapi pertahankan alur inti sebagai satu take utuh.
- **Jangan tampilkan percakapan WhatsApp pribadi yang asli.** Pakai data sintetis
  atau yang sudah diredaksi, dan hindari logo pihak ketiga.
- Zoom teks kecil. Trace yang tidak terbaca sama saja tidak ditampilkan.

---

## 3. Kerangka deskripsi Devpost

**Inspiration**
Brief klien di WhatsApp terlihat lengkap padahal menyembunyikan hal yang
menentukan untung-rugi. Freelancer tahu harus bertanya, tapi friksinya terlalu
besar untuk dilakukan setiap kali.

**What it does**
Terima brief sekali; agent menjalankan siklus klarifikasi otonom di background
sampai brief aman di-quote, lalu menyiapkan pesan siap kirim.

**How we built it**
Google ADK + Gemini 3.5+ untuk ekstraksi dan orkestrasi. Aturan deal
deterministik dan seluruh perhitungan di Python. Cloud Run (tiga service),
Pub/Sub untuk eksekusi asinkron, Firestore untuk state dan Memory Bank lintas
sesi, Firebase Auth, Secret Manager.

**Challenges we ran into**
Diisi jujur dari yang benar-benar terjadi. Kandidat: IAM push subscription
Pub/Sub, menegakkan idempotensi worker, memaksa model tidak mengarang kutipan.

**Accomplishments that we're proud of**
Pemisahan tegas: model mengekstrak dan menyusun bahasa, kode yang menilai dan
menghitung — sehingga hasilnya reproducible dan bisa diaudit. Trace yang
membuktikannya, terbuka untuk user.

**What we learned**
Diisi jujur.

**What's next**
Integrasi WhatsApp/Gmail supaya brief masuk tanpa disalin manual.

> Jangan mengklaim apa pun yang tidak ada di video atau repo. Klaim yang tidak
> terbukti lebih merugikan daripada fitur yang tidak ada.

---

## 4. Yang harus ada di README repo

Dinilai eksplisit di kriteria *Demo & Production Readiness* (30%).

- [ ] Satu paragraf: produk ini apa
- [ ] Diagram arsitektur (gambar tertanam)
- [ ] **Setup dari nol** — persis isi [`06-SETUP.md`](06-SETUP.md)
- [ ] Tabel environment variable
- [ ] Cara menjalankan test + hasil sebenarnya
- [ ] Perintah deploy ke Google Cloud
- [ ] Bagian **"Google Cloud services used"** — memudahkan juri memverifikasi
- [ ] Batasan yang diketahui, ditulis jujur

Perlakukan README sebagai barang yang dinilai, bukan formalitas. Juri mungkin
tidak menjalankan kodenya, tapi mereka pasti membaca README-nya.
