# 04 — Rencana Eksekusi sampai Deadline

## 1. Realita waktu

Jendela kerja: Selasa 25 Agustus sampai Senin 31 Agustus 2026. Target internal submit adalah **31 Agustus 18:00 WIB**, sekitar 13 jam sebelum deadline 1 September 07:00 WIB. Jangan merencanakan coding setelah target internal kecuali memperbaiki blocker submission.

Budget kerja yang diasumsikan:

| Tanggal | Budget | Fokus |
|---|---:|---|
| Selasa 25 | 3 jam | cloud foundation |
| Rabu 26 | 3 jam | Handshake agent |
| Kamis 27 | 3 jam | client portal + event |
| Jumat 28 | 3 jam | approved baseline |
| Sabtu 29 | 10 jam | Guardrail + Proof |
| Minggu 30 | 10 jam | hardening + submission assets |
| Senin 31 | 3 jam | final recording/upload/submit |
| **Total** | **35 jam personal** | lebih kecil dari estimasi 46–50 jam; perlu pemotongan non-normatif atau parallel code generation setelah kontrak §10 beku |

Karena budget personal lebih kecil daripada effort implementation, setiap hari punya kill condition. Aturan normatif `09` tidak boleh dipotong diam-diam; yang dipotong lebih dahulu adalah polish, PDF, email, memory UI, dan evidence adapter tambahan. Bila memakai beberapa coding agent, pekerjaan baru boleh diparalelkan setelah kontrak §10 selesai dan direview satu pemilik.

## 2. Selasa, 25 Agustus — Cloud skeleton (3 jam)

### Hasil wajib

- `shared/schemas/`, enum tertutup, canonical/hash golden vectors, quote validation, dan audit-seq contract dibekukan sebelum feature coding.
- Struktur web/API/worker dan health endpoints.
- Google Cloud project/billing/region ditetapkan.
- Firestore, Pub/Sub, Cloud Run, Artifact Registry, Cloud Storage aktif.
- Dummy Pub/Sub push mencapai private worker di Cloud Run dan terlihat di logs.
- Model `gemini-3.5-flash`, region, quota, serta ADC diuji dengan satu request.

### Kill condition

Jika web belum jadi, gunakan halaman HTML/Next.js minimal. Jangan menghabiskan hari pertama pada design system. Jika Vertex/model availability bermasalah, putuskan konfigurasi resmi yang bekerja hari itu dan dokumentasikan; jangan menebak ID.

## 3. Rabu, 26 Agustus — Handshake agent (3 jam)

### Hasil wajib

- Golden brief fixture tersimpan.
- Text input menghasilkan structured Deal Ledger.
- Provenance states tervalidasi.
- Konflik “Friday” versus “Monday” terdeteksi dan tidak dapat diselesaikan model/freelancer.
- Deterministic readiness dan maksimal tiga pertanyaan bekerja.
- Satu test memastikan model tidak dapat membuat `AGREED`.

### Cut

Image upload boleh ditunda sampai Sabtu. Selesaikan text path terlebih dahulu.

## 4. Kamis, 27 Agustus — Client loop (3 jam)

### Hasil wajib

- Opaque client link dengan purpose dan expiry.
- Client dapat menjawab/mengoreksi field tanpa akun.
- Client dapat mengirim request baru dari portal yang sama.
- Submit membuat Pub/Sub job.
- Worker idempotently menggabungkan response ke run yang sama.
- Owner melihat updated ledger melalui polling.

### Kill condition

Tidak ada email integration. Copy link manual cukup untuk demo.

## 5. Jumat, 28 Agustus — Baseline integrity (3 jam)

### Hasil wajib

- Readiness gate memblok approval yang belum lengkap.
- Client Approve menghasilkan baseline v1 yang tidak dapat ditimpa melalui application flow.
- Canonical SHA-256, actor label, server timestamp, dan audit event tersimpan.
- Owner A tidak dapat membaca deal owner B; expired token ditolak.

### Gate akhir hari

**Handshake harus end-to-end di hosted environment.** Bila belum, Sabtu pagi hanya memperbaiki ini. Jangan mulai Guardrail.

## 6. Sabtu, 29 Agustus — Guardrail dan Proof (10 jam)

### Blok A — Guardrail (3 jam)

- Input new client request.
- Gemini output classification proposal + baseline citations.
- Human confirm/override tercatat.
- Change request membuat changed-fields list dan baseline v2 setelah approval.

### Blok B — Proof (3 jam)

- Evidence URL/text dan satu image bila stabil.
- Mapping ke criterion.
- Client Accept/Request changes dengan structured reason.
- Alasan di luar criterion diteruskan sebagai scope-review proposal.
- Proof Manifest page dan Markdown/JSON export.

### Blok C — Multimodal + memory (2 jam)

- Satu screenshot brief masuk lewat Cloud Storage dan dianalisis Gemini.
- Satu confirmed preference muncul sebagai freelancer policy pada deal kedua.

### Blok D — Tests dan bug reserve (2 jam)

- Idempotency/redelivery.
- v1 tetap tidak berubah setelah v2.
- criterion status lintas versi, revision session counter, drift aggregate, conflict authority, golden hash, exact tool allowlist, dan client-answer injection mengikuti test matrix `09-DOMAIN-RULES.md` §12.
- Wrong-purpose token.
- Prompt injection fixture.
- Malformed model response fails closed.
- Sebelum berhenti, rekam satu run end-to-end apa adanya sebagai **backup recording**, meskipun belum dipoles.

### Kill conditions

- Upload image gagal setelah 45 menit: pakai preloaded demo artifact.
- Visual diff >45 menit: pakai changed-fields list.
- Export PDF belum dimulai; Markdown/JSON sudah cukup.

## 7. Minggu, 30 Agustus — Stabilkan dan kemas (10 jam)

### Pagi — golden path dan observability (3 jam)

- Seed script wajib membuat empat event `SCOPE_CLASSIFICATION_DECIDED` yang valid; request kelima dilakukan live agar drift counter berubah 4 → 5 di kamera.
- Jalankan satu golden path berurutan dan langsung rekam timed rough cut sebagai alat pencari bug.
- Setelah memperbaiki blocker yang ditemukan, jalankan ulang dari akun/seed bersih dua kali.
- Catat latency dan perbaiki hanya blocker.
- Cloud Logging memiliki satu correlation/job ID yang mudah ditunjukkan.
- Reset/seed harus memakai domain service/event contract, bukan edit Firestore manual.

### Siang — UI dan English pass (2 jam)

- Label provenance, readiness blockers, citation, version, dan client action terbaca jelas.
- Semua layar demo mendukung English.
- Empty/loading/error states minimum.

### Sore — repo dan Devpost (2 jam)

- README implementasi: architecture diagram, tech mapping, spin-up, env vars, test, disclosures.
- Screenshot dan hosted URL.
- Draft deskripsi Devpost English.
- Repo access dan teammate invitation diverifikasi.
- Jika seluruh deliverable wajib sudah hijau, siapkan public build write-up dan social post `#AllThingsAgenticHackathon` untuk bonus; jangan mengambil waktu dari bug blocker.

### Malam — final video assembly (3 jam)

- Rekam klip pendek, bukan one-take.
- Produk bekerja terlihat pada 0:00–0:10.
- Total rough cut ≤3:45.
- Cloud Run/Firestore/Pub/Sub proof tampak tanpa membuka secret.
- Upload draft untuk QA, uji dari incognito, lalu pastikan versi submission menjadi publicly visible sebelum submit.

### Freeze

Setelah 30 Agustus 23:00 WIB, tidak ada fitur baru. Hanya P0 bug, copy, video, dan submission.

## 8. Senin, 31 Agustus — Submit (3 jam)

1. Rekam ulang hanya klip yang gagal; jangan mengubah app kecuali P0.
2. Final video ≤4 menit, publicly accessible sesuai aturan Devpost, English atau English subtitles.
3. Uji hosted URL, client link, video, repo, dan credentials dari incognito.
4. Isi setiap field submission dan disclosure.
5. Submit maksimal **18:00 WIB**.
6. Simpan screenshot confirmation.
7. Setelah official deadline, jangan menyentuh repo/video/material terkait sampai winners diumumkan sesuai instruksi event.

## 9. Aturan kerja harian

- Commit saat satu vertical behavior bekerja; gunakan pesan yang menunjukkan start date dan progres.
- Deploy minimal sekali per hari; local-only progress tidak cukup.
- Tes golden path setelah perubahan domain model.
- Simpan bukti cloud/video saat sistem stabil, jangan menunggu sesi terakhir.
- Jika estimasi meleset >60 menit, ambil pemotongan nyata berikutnya atau turunkan profile modul sesuai dependency ladder; jangan memilih item SHOULD yang memang belum menjadi komitmen.
