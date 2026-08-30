# Delividence — Paket Rencana Hackathon

> Stateful AI partner yang mengubah brief klien yang kabur menjadi scope yang disepakati, menjaga batas scope saat proyek berjalan, dan mengumpulkan bukti penerimaan hasil.

**Hackathon:** All Things Agentic  
**Kategori:** The Collaborative Partner  
**Deadline:** 31 Agustus 2026, 17:00 PT / 1 September 2026, 07:00 WIB  
**Status:** core submission diimplementasi dan lulus test lokal; Firebase,
Cloud Run, Firestore, Pub/Sub, hosted URL, architecture diagram, dan video
masih perlu dikonfigurasi/diuji pada environment produksi.

## Keputusan produk final

Nama produk adalah **Delividence**. Artefak pusatnya bernama **Deal Ledger**: catatan versi yang membedakan hal yang dikatakan klien, kebijakan freelancer, usulan agent, hal yang sudah disepakati, dan hal yang masih hilang.

Produk bekerja dalam tiga fase yang menyambung:

1. **Handshake** — agent membaca brief/chat screenshot dan mengajukan maksimal tiga pertanyaan prioritas; klien juga dapat memperbaiki seluruh field kritis pada editable plan sebelum mengonfirmasi scope.
2. **Guardrail** — permintaan baru dibandingkan dengan baseline. Agent menunjukkan klausul terkait dan mengusulkan `IN_SCOPE`, `AMBIGUOUS`, atau `CHANGE_REQUEST`; manusia tetap membuat keputusan akhir.
3. **Proof** — freelancer menghubungkan bukti hasil ke tiap acceptance criterion dalam Acceptance Matrix. Klien dapat menerima atau meminta perubahan dengan alasan terstruktur; permintaan yang tidak ditopang criterion kembali ke Guardrail.

Bagi klien, portal dibingkai sebagai perlindungan dari menerima hasil yang salah atau ditagih untuk sesuatu yang sudah termasuk. Layar pertama menunjukkan apa yang akan diterima, kapan, dan apa yang tidak termasuk: tiga prompt prioritas dapat dijawab cepat, sementara seluruh critical-field summary tetap bisa dikoreksi sebelum konfirmasi.

Delividence bukan marketplace, contract platform, atau chatbot pembuat proposal. Tidak ada pencarian freelancer, pembayaran, escrow, chat umum, rating, maupun arbitrase. Ia adalah lapisan kesepakatan dan bukti yang dapat dipakai di atas kanal kerja yang sudah ada.

## Demo utama dalam satu kalimat

Masukkan brief yang kabur; agent membuat Deal Ledger dan link klien; klien
mengklarifikasi serta menyetujui scope; permintaan tambahan kemudian ditandai
sebagai change request dengan kutipan baseline; freelancer melampirkan bukti
hasil dan klien memberi acceptance.

## Batas klaim

Snapshot versi, hash konten, timestamp server, provenance, dan tindakan approval membentuk **defensible audit trail**. MVP tidak menyediakan tanda tangan elektronik tersertifikasi dan tidak menjamin kekuatan hukum suatu agreement. Hash membuktikan isi snapshot tidak berubah setelah dicatat, bukan bahwa isinya benar.

## Urutan baca

1. [00-BRIEF.md](./00-BRIEF.md) — syarat acara dan positioning.
2. [01-PRD.md](./01-PRD.md) — pengguna, alur, scope, dan acceptance criteria.
3. [02-ARCHITECTURE.md](./02-ARCHITECTURE.md) — agent, layanan Google Cloud, data, keamanan.
4. [03-BUILD-BREAKDOWN.md](./03-BUILD-BREAKDOWN.md) — unit pekerjaan dan cut line.
5. [04-PLAN-7-DAYS.md](./04-PLAN-7-DAYS.md) — jadwal sampai submission.
6. [05-SUBMISSION-CHECKLIST.md](./05-SUBMISSION-CHECKLIST.md) — deliverable, naskah video, dan copy Devpost.
7. [06-SETUP.md](./06-SETUP.md) — rencana setup lokal dan cloud.
8. [07-RISKS-DECISIONS.md](./07-RISKS-DECISIONS.md) — keputusan tetap, risiko, dan fallback.
9. [09-DOMAIN-RULES.md](./09-DOMAIN-RULES.md) — aturan normatif criterion versioning, revision rounds, drift ledger, conflict resolution, event log, dan authority.
10. [10-KEPUTUSAN-DAN-VERIFIKASI.md](./10-KEPUTUSAN-DAN-VERIFIKASI.md) — keputusan terkunci (nama, repo, stack, profil modul) dan fakta aturan hackathon yang sudah diverifikasi ke halaman resmi. **Baca setelah 00.**
11. [12-HANDOVER-LOKAL.md](./12-HANDOVER-LOKAL.md) — daftar serah-terima untuk menjalankan di mesin sendiri: dua file env yang tidak ikut repo, prasyarat, dan perintah yang sudah diuji.
12. [arsip-dealready/](./arsip-dealready/) — paket rencana DealReady sebelum pivot. Riwayat, bukan rujukan.

## Definition of done hackathon

- Aplikasi mendukung English; Bahasa Indonesia adalah pilihan output tambahan.
- Gemini 3.5+ dipakai untuk ekstraksi teks dan analisis semantik.
- Google ADK menjalankan workflow agent yang stateful.
- Backend benar-benar berjalan di Google Cloud, bukan mock lokal.
- Satu alur lengkap Handshake → Guardrail → Proof dapat didemokan.
- Seluruh invariant dan test wajib pada `09-DOMAIN-RULES.md` lulus.
- Repo, hosted URL, diagram arsitektur, instruksi spin-up, dan video publik ≤4 menit siap sebelum deadline.

## Aturan scope

Jika tertinggal, pertahankan satu vertical slice yang benar-benar bekerja. Potong email otomatis, PDF legal, integrasi Upwork/Fiverr, video input, pricing engine, dan multi-agent. Jangan memotong provenance, client approval, versioned baseline, event-driven resume, atau deployment Google Cloud karena itulah pembeda utama.

## Submission profile yang berlaku

Modul B (penghitungan consumption revision rounds), Modul C (drift ledger), dan
Modul D (conflict-resolution matrix) secara eksplisit **dilepas** oleh
[`10-KEPUTUSAN-DAN-VERIFIKASI.md`](./10-KEPUTUSAN-DAN-VERIFIKASI.md) agar
vertical slice Handshake → Guardrail → Proof selesai dan dapat dibuktikan.
Direct binary upload/transkripsi audio, gambar, video, PDF, email delivery,
dan PDF export juga bukan klaim MVP saat ini. Jangan mendemokan atau menuliskan
fitur itu sebagai sudah tersedia sebelum adapter Cloud Storage/multimodal benar-
benar dibangun.
