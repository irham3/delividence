# 00 — Brief Hackathon dan Positioning

Dokumen ini adalah source of truth untuk eligibility dan positioning Delividence. Periksa kembali Rules/FAQ Devpost sebelum submit karena materi acara dapat berubah.

## 1. Identitas acara

| Item | Keputusan |
|---|---|
| Event | All Things Agentic Hackathon |
| Submission deadline | 31 Agustus 2026, 17:00 PT |
| Konversi Jakarta | 1 September 2026, 07:00 WIB |
| Kategori | **The Collaborative Partner** |
| Project | **Delividence** |
| Start date yang dilaporkan | Tanggal commit/implementasi pertama; jangan mengaku lebih awal |
| Bahasa aplikasi | English wajib; Bahasa Indonesia opsional |

## 2. Syarat teknis wajib

Submission harus merupakan proyek baru pada submission period dan menggunakan ketiganya:

- **Gemini 3.5 atau lebih baru** — target implementasi `gemini-3.7-flash`; verifikasi ID dan availability pada hari integrasi.
- **Minimal satu Google agent framework** — Google Agent Development Kit (ADK).
- **Minimal satu Google Cloud service** — Cloud Run, Firestore, Pub/Sub, dan Cloud Storage digunakan secara nyata.

Jangan hanya menuliskan layanan di diagram. Video harus memperlihatkan aplikasi bekerja dan bukti backend berjalan di Google Cloud.

## 3. Mengapa The Collaborative Partner

Delividence mempertahankan konteks lintas giliran dan lintas sesi, menggabungkan kontribusi freelancer serta klien, lalu beradaptasi melalui preference memory yang dikonfirmasi pengguna. Nilai agentic-nya terlihat dari:

- state Deal Ledger bertahan setelah request selesai;
- client response memicu Pub/Sub dan melanjutkan workflow tanpa copy-paste manual;
- agent memilih tiga pertanyaan berdampak tertinggi dari state yang belum lengkap;
- permintaan baru dibandingkan dengan baseline yang telah disetujui;
- preference memory digunakan pada deal berikutnya tetapi tidak pernah dianggap sebagai fakta dari klien.

Event-driven orchestration tetap menjadi kekuatan teknis, tetapi kategori submission hanya satu: Collaborative Partner.

Pilihan ini juga strategis: otonomi tetap diperlihatkan melalui event resume, revision routing, dan drift signals, sementara shared state dua pihak memberi diferensiasi yang lebih khas daripada agent penyelesai tugas umum. Jangan pindah kategori hanya untuk terlihat lebih otonom; tambahkan otonomi deterministik ke dalam collaborative lifecycle.

## 4. Masalah yang dipilih

Freelancer sering memulai pekerjaan dari brief singkat atau percakapan yang tersebar. Ambiguitas tersebut baru terlihat setelah pengerjaan, ketika klien meminta revisi berulang atau menambahkan pekerjaan yang tidak pernah disepakati. Percakapan biasa sulit dijadikan rujukan karena:

- tidak ada baseline scope yang terstruktur dan dibekukan;
- istilah seperti “responsive”, “siap”, atau “revisi minor” tidak punya acceptance criteria;
- permintaan baru bercampur dengan scope lama;
- hasil kerja tidak dipetakan langsung ke janji yang disepakati;
- keputusan klien tersebar di chat dan sulit ditelusuri.

Delividence tidak mencoba menyelesaikan pembayaran atau sengketa. Produk ini membuat batas kerja dan bukti penerimaan lebih jelas sebelum konflik muncul.

## 5. Positioning dan pembeda

| Alternatif | Yang dapat dilakukan | Yang tetap hilang |
|---|---|---|
| Chatbot/Codex/coworker | Menganalisis brief dan menulis proposal sekali | shared state dua pihak, approval granular, event resume, versioned baseline, proof-to-criterion mapping |
| Google Docs/form | Mengumpulkan isi dan komentar | klasifikasi provenance, pertanyaan adaptif, scope drift detection, deterministic readiness |
| Upwork/Fiverr | Marketplace, komunikasi, pembayaran, dispute flow | portable evidence layer untuk pekerjaan dari kanal mana pun |
| Contract generator | Menghasilkan dokumen legal | loop klarifikasi aktif dan bukti delivery per acceptance criterion |

Kalimat positioning:

> **Delividence is a two-party AI scope and acceptance protocol—not another proposal chatbot or freelance marketplace.**

## 6. Demo yang membuktikan ide

Demo tunggal harus menunjukkan rangkaian sebab-akibat, bukan daftar fitur:

1. Freelancer memasukkan brief yang kabur dan screenshot chat.
2. Agent membuat Deal Ledger dengan source evidence dan tiga pertanyaan prioritas.
3. Klien membuka link tanpa akun, menjawab, mengedit, lalu menyetujui baseline.
4. Respons klien memicu worker cloud; readiness berubah dan baseline v1 dibekukan.
5. Permintaan “tambahkan juga format TikTok” dibandingkan dengan baseline dan diusulkan sebagai change request.
6. Freelancer melampirkan URL/screenshot hasil ke acceptance criterion.
7. Klien menerima criterion; audit timeline dan proof manifest diperlihatkan.

## 7. Deliverable submission

- Hosted project URL yang tetap hidup selama judging.
- Public YouTube/Vimeo video maksimal 4 menit, English atau English subtitles.
- Link repository; jika private, beri akses ke email penguji yang ditentukan penyelenggara.
- Diagram arsitektur dan spin-up instructions di README.
- Deskripsi features, technologies, data sources, learning, SDK/model, serta tanggal mulai.
- Disclosure untuk pre-existing atau third-party code.
- Satu kategori saja.

## 8. Batas kejujuran

- “Approval” pada MVP adalah tindakan aplikasi dengan timestamp, bukan qualified e-signature.
- Audit trail memperkuat provenance dan chronology, bukan menjamin validitas hukum.
- Klasifikasi scope dari AI adalah rekomendasi yang harus dikonfirmasi freelancer/klien.
- Screenshot dapat menjadi sumber, tetapi tidak otomatis membuktikan identitas atau kebenaran isi.
- Jangan memperlihatkan raw chain-of-thought; tampilkan structured reasons, cited evidence, tool events, dan state transitions.
