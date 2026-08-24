# 00 — Brief Hackathon

Ringkasan aturan **All Things Agentic Hackathon: Ready, Set, Agent!** supaya tim
tidak perlu membaca ulang seluruh halaman Devpost.

Sumber: <https://allthingsagentichackathon.devpost.com/> dan halaman `/rules`,
diambil 24 Agustus 2026. **Kalau ada perbedaan, halaman resmi yang menang.**

---

## 1. Identitas

| | |
|---|---|
| Nama | All Things Agentic Hackathon: Ready, Set, Agent! |
| Penyelenggara | Google (platform: Devpost) |
| Format | Online, global |
| Tema | AI agent yang bekerja otonom di background, memproses data besar, mengotomasi workflow kompleks secara **asinkron** |
| Total hadiah | $180.000 |
| Peserta terdaftar | ~7.482 (per 24 Agustus 2026) |

## 2. Timeline

| | |
|---|---|
| Submission period | 3 Agustus 2026, 09:00 PT sampai **31 Agustus 2026, 17:00 PT** |
| Deadline dalam WIB | **1 September 2026, 07:00 WIB** |
| Target internal | Submit **30 Agustus**, sisakan 1 hari buffer |

## 3. Syarat teknis — WAJIB ketiganya

1. **Gemini 3.5 atau lebih baru** — via Gemini API atau Vertex AI.
   `[verifikasi]` ID model persis yang tersedia saat lomba. **Jangan tebak dari
   dokumen ini**; cek dokumentasi resmi sebelum menulis ke env var.
2. **Minimal satu Google Agent Framework** — Google ADK, GenAI SDK,
   Antigravity SDK, atau GenKit.
3. **Minimal satu layanan infrastruktur Google Cloud** — Cloud Run, Cloud SQL,
   Firestore, GKE, Pub/Sub, dan sejenisnya.

Disediakan panitia: trial Google Cloud tanpa biaya + **$150 credit** per peserta.

## 4. Kategori — pilih satu

| Kategori | Inti | Hadiah |
|---|---|---|
| **The Taskmaster** | Otomasi workflow multi-langkah. Agent **bertindak**, bukan sekadar bercakap; merapikan proses berantakan dan me-routing informasi | $20.000 |
| **The Collaborative Partner** ← **pilihan kita** | Agent adaptif terhadap user: mengajukan pertanyaan klarifikasi, memberi panduan bertahap, terus berkembang dari feedback | $20.000 |
| **The Fortified Enterprise Fleet** | Jaringan agent skala institusi: Agent Registry, Agent Runtime, Memory Bank, Agent Identity (zero-trust), Agent Gateway, Model Armor, Agent Observability | $20.000 |

Alasan memilih Collaborative Partner: [`01-PRD.md`](01-PRD.md) bagian 2.

## 5. Struktur hadiah lengkap

| Kategori hadiah | Nilai | Pemenang | Bonus |
|---|---|---|---|
| Grand Prize | $50.000 | 1 | $5K credit, virtual coffee, promo sosmed |
| The Taskmaster | $20.000 | 1 | $2K credit + promo |
| Collaborative Partner | $20.000 | 1 | $2K credit + promo |
| Fortified Enterprise Fleet | $20.000 | 1 | $2K credit + promo |
| Startup Excellence | $20.000 | 1 | $5K credit + promo |
| **Individual / Hobbyist** | $10.000 | **2** | $1K credit + promo |
| Best Architectural Design | $5.000 | 2 | $1K credit |
| Best Multimodal UX | $5.000 | 2 | $1K credit |
| Honorable Mention | $2.000 | 5 | $500 credit |

Startup Excellence butuh badan usaha terdaftar — tidak relevan.

## 6. Kriteria penilaian

| Bobot | Kriteria | Artinya buat kita |
|---:|---|---|
| **40%** | Innovation & Operational Utility — seberapa banyak friksi dunia nyata yang dihilangkan agent **secara mandiri** | Kata kuncinya *independently*. Tool request-response akan kalah di sini |
| **30%** | Architectural Discipline & Tech Stack — kualitas engineering, decoupling, state management, security | Pemisahan AI/kalkulasi, isolasi data, idempotensi, test |
| **30%** | Demo & Production Readiness — kualitas video & repo, reproducibility, bukti deploy di Google Cloud | README + diagram + video 4 menit |

**Strategi:** 60% bobot ada di arsitektur dan kualitas demo/dokumentasi, bukan
jumlah fitur. Jangan tambah fitur. Perdalam agent-nya dan rapikan buktinya.

## 7. Deliverable submission

- [ ] Pilihan kategori
- [ ] URL project yang di-host (kalau ada)
- [ ] Deskripsi teks: fitur, teknologi, sumber data, temuan
- [ ] Repo kode (GitHub/GitLab/Bitbucket). Kalau private, **wajib** di-share ke
      `testing@devpost.com` dan `cloudhackathons@google.com`
- [ ] `README.md` berisi setup instruction yang reproducible
- [ ] **Diagram arsitektur** — komponen sistem + integrasi Google Cloud
- [ ] **Video demo ~4 menit** — masalah, value proposition, aplikasi berjalan,
      bukti deploy Google Cloud

Bonus opsional (menambah nilai):
- [ ] Blog post / podcast / video di Medium, YouTube, dsb.
- [ ] Post sosmed di X, LinkedIn, Instagram, atau Facebook
- [ ] Integrasi model Google lain: Gemma, Veo, atau Lyria

Project **tidak wajib live** saat submit — bukti deploy lewat video/repo cukup.

## 8. Aturan yang relevan

- **"Projects must be newly created during the Submission Period."**
  DealReady lahir **24 Agustus 2026**, di dalam periode 3–31 Agustus.
  Terpenuhi tanpa perdebatan — dan git history repo baru jadi buktinya.
- Kode pre-existing yang dipakai **wajib di-disclose**. Karena itu **jangan
  menyalin kode dari Baseline** — supaya tidak ada yang perlu didisclose dan
  tidak ada pertanyaan kepemilikan.
- Boleh ikut sebagai individu, tim, atau atas nama organisasi. Tidak ada batas
  maksimum anggota tim yang disebutkan.
- Peserta harus di atas usia dewasa menurut hukum negaranya.
- **Void** untuk penduduk: Italia, Quebec, Crimea, Kuba, Iran, Suriah, Korea
  Utara, Sudan, Belarus, Rusia, dan negara yang kena embargo/sanksi AS.
  **Indonesia tidak termasuk — kita eligible.**
- Karyawan penyelenggara dan keluarga intinya tidak eligible.
