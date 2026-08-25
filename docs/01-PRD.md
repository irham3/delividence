# 01 — PRD: Delividence

## 1. Ringkasan produk

Delividence adalah collaborative AI agent untuk freelancer yang mengubah komunikasi awal menjadi **Deal Ledger**, menjaga baseline ketika ada permintaan tambahan, dan menghubungkan bukti hasil ke acceptance criteria. Klien berpartisipasi melalui portal ringan tanpa akun; agent melanjutkan workflow secara event-driven ketika respons masuk.

## 2. Pengguna dan job-to-be-done

### Freelancer

> Ketika brief masih kabur, bantu saya memperoleh kesepakatan yang eksplisit. Ketika permintaan berubah, tunjukkan batas yang telah disetujui. Ketika saya selesai, bantu saya menunjukkan bukti bahwa hasil memenuhi kriterianya.

### Klien

> Beri saya cara singkat untuk memperbaiki asumsi, menyetujui apa yang akan dibuat, memahami dampak perubahan, dan menerima hasil tanpa harus mempelajari tool baru.

Target awal adalah freelancer digital dengan deliverable yang dapat ditautkan atau divisualisasikan: web, design, content, automation, dan software. Scope tidak mencakup marketplace atau pembayaran.

## 3. Prinsip produk

1. **Agreement over generation.** Nilai utama adalah mutual clarity, bukan dokumen AI yang terlihat rapi.
2. **Evidence over confidence.** Setiap klaim penting punya sumber atau ditandai belum terbukti.
3. **No silent mutation.** Baseline yang sudah disetujui tidak pernah ditimpa; perubahan membuat versi/change request baru.
4. **Human authority.** AI mengusulkan klasifikasi; manusia menyetujui scope, perubahan, dan acceptance.
5. **Minimal client friction.** Link terbatas dan kedaluwarsa; klien tidak perlu akun.
6. **Memory is not fact.** Preferensi freelancer membantu deal berikutnya, tetapi tidak menjadi fakta klien.
7. **Defensible, not legal theater.** Catatan kuat dan jujur tanpa mengklaim sebagai layanan hukum.

## 4. Model konsep

### 4.1 Deal Ledger

Setiap field penting menyimpan `value`, `state`, provenance berupa `source_artifact` + verbatim `source_quote`, `confidence`, dan `version`. Kutipan harus lolos validasi terhadap artifact; offset karakter buatan model tidak dipakai.

State yang diperbolehkan:

- `CLIENT_STATED` — berasal langsung dari brief/jawaban klien.
- `FREELANCER_POLICY` — aturan eksplisit milik freelancer, misalnya dua ronde revisi.
- `PROPOSED` — usulan agent/manusia yang belum disepakati.
- `AGREED` — telah disetujui klien pada baseline tertentu.
- `MISSING` — belum ada informasi yang cukup.
- `CONFLICTING` — dua sumber memberi nilai yang bertentangan.

Ledger minimum berisi deliverables, in-scope, out-of-scope, acceptance criteria, timeline, dependencies/client responsibilities, revision policy, assumptions, dan unresolved questions.

### 4.2 Tiga fase

**Handshake** menghasilkan baseline yang disetujui.  
**Guardrail** membandingkan request baru dengan baseline.  
**Proof** menghubungkan evidence item dengan acceptance criterion dan menyimpan keputusan klien.

### 4.3 Acceptance Matrix

“Bukti” bukan satu badge `VERIFIED`. Untuk setiap criterion, UI menampilkan empat lapis yang tidak boleh dicampur:

- **Agreement source** — baseline version dan criterion yang disetujui.
- **Artifact integrity** — URI/object, uploader, server timestamp, dan checksum bila berupa file.
- **Checks** — hasil pemeriksaan deterministik yang benar-benar dijalankan, misalnya URL dapat diakses; penilaian visual Gemini harus dilabeli `AI_ASSISTED`, bukan fakta.
- **Client decision** — `ACCEPTED` atau `CHANGES_REQUESTED`, actor label, reason, dan timestamp.

Kekuatan catatan berasal dari rantai ini, bukan dari screenshot saja. Screenshot tetap dapat dimanipulasi dan hash hanya menunjukkan file yang dicatat tidak berubah.

## 5. End-to-end flow

1. Freelancer login dan membuat deal.
2. Ia menempelkan brief English/Indonesian dan opsional mengunggah satu screenshot/image.
3. Agent mengekstrak ledger terstruktur, menautkan tiap klaim ke sumber, menandai ambiguitas/konflik, dan menghitung readiness secara deterministik.
4. Agent memilih maksimal tiga pertanyaan prioritas dengan dampak tertinggi. Pertanyaan ini bukan satu-satunya jalur input; freelancer meninjau lalu mengirim client link.
5. Klien membuka link, menjawab prompt prioritas, dan dapat mengoreksi seluruh critical-field summary—apa yang diterima, kapan, acceptance criteria, revision limit, dan apa yang tidak termasuk. CTA **Confirm project plan** tetap nonaktif sampai semua critical field tuntas.
6. Event klien masuk ke Pub/Sub. ADK worker melanjutkan run, memperbarui ledger, membuat baseline snapshot, hash konten, dan audit event.
7. Setelah proyek berjalan, klien dapat mengirim request baru melalui portal yang sama, atau freelancer dapat mencatat request dari kanal lain. Agent mengusulkan `IN_SCOPE`, `AMBIGUOUS`, atau `CHANGE_REQUEST` disertai kutipan verbatim dari baseline.
8. Untuk change request, sistem membuat diff dan kolom impact pada deliverable/timeline/revision policy; perubahan hanya aktif setelah approval.
9. Freelancer menambahkan evidence item ke tiap acceptance criterion: URL, screenshot/image, file metadata/hash, test result text, atau commit URL.
10. Layar delivery review mengumpulkan **Accept** atau **Request changes** untuk seluruh criterion, lalu klien mengirim semuanya dalam **satu aksi submit**. API membuat tepat satu `review_session_id`; penolakan wajib menunjuk criterion dan alasan.
11. Agent membandingkan alasan perubahan dengan criterion. Jika permintaan tidak ditopang baseline, ia membuat scope-review proposal di Guardrail—bukan diam-diam menghitungnya sebagai revisi biasa.
12. Sistem menghasilkan Proof Manifest/Acceptance Record yang dapat diekspor sebagai Markdown/JSON pada MVP.

## 6. Scope prioritas

### MUST — vertical slice submission

- English-first UI/output; Indonesian input/output toggle.
- Owner authentication dan isolasi data per user.
- Input text plus satu image/screenshot.
- Structured extraction ke Deal Ledger dengan provenance.
- Deterministic readiness gates.
- Maksimal tiga clarification questions yang diprioritaskan agent.
- Scoped, expiring, single-purpose client link tanpa akun.
- Client edit/answer dan baseline approval.
- Pub/Sub-triggered ADK resume; tidak ada copy-paste respons klien.
- Append-only approved baseline version + server timestamp + canonical `payload_hash`.
- New-request comparison dengan cited baseline dan human-confirmed classification.
- Client portal menerima request baru selain clarification/review action.
- Change request sebagai versi/diff terpisah.
- Minimal evidence item mapping ke acceptance criterion.
- Client Accept/Request changes per criterion.
- Request changes yang tidak didukung criterion diteruskan ke scope review dengan human confirmation.
- Stable `criterion_key`, revision-round counter per review session, drift ledger, dan conflict-resolution flow sesuai `09-DOMAIN-RULES.md`.
- Sanitized audit timeline; tidak ada raw chain-of-thought.
- Satu explicit preference disimpan dan tampak digunakan pada deal kedua.
- Deployed Cloud Run + Firestore + Pub/Sub, tests pada rule penting.

### SHOULD — hanya setelah MUST hijau

- PDF input dan downloadable formatted PDF record.
- Cloud Storage object versioning untuk artifact.
- Email delivery untuk client link.
- GitHub commit/test evidence adapter.
- Side-by-side visual diff baseline/change request.
- Reminder saat client link hampir kedaluwarsa.

### WON'T — setelah hackathon

- Marketplace, freelancer discovery, rating, bidding.
- Payment, invoice, escrow, pricing recommendation.
- General-purpose chat atau project management board.
- Legal advice, certified e-signature, dispute arbitration.
- WhatsApp/Upwork/Fiverr API integration.
- Contract clause generation lintas yurisdiksi.
- Video/audio evidence understanding, IoT proof, browser monitoring.
- Autonomous sending/acceptance tanpa human approval.
- Multi-agent theater; satu ADK workflow cukup.

## 7. Readiness dan keputusan deterministik

Readiness bukan angka yang dikarang model. Daftar field kritis bersifat tertutup dan didefinisikan normatif di `09-DOMAIN-RULES.md` §5.7. Baseline dapat disetujui jika:

- ada minimal satu deliverable;
- setiap deliverable punya minimal satu acceptance criterion;
- timeline atau explicit `NOT_SET` telah dikonfirmasi;
- revision policy atau explicit `NOT_SET` telah dikonfirmasi;
- tidak ada field kritis berstatus `CONFLICTING` atau `MISSING`;
- semua nilai baseline yang berasal dari usulan sudah dikonfirmasi manusia.

Agent boleh menjelaskan gate yang gagal, tetapi tidak boleh mengubah hasil gate.

Field kritis `CONFLICTING` otomatis mengambil slot clarification question sebelum ranking biasa. Konflik antara dua pernyataan klien hanya dapat diselesaikan klien; tidak ada auto-resolution berdasarkan kebaruan atau confidence model.

## 8. User stories dan acceptance criteria

### US-1 — Dari brief ke ledger bersumber

**Given** brief kabur dan screenshot chat, **when** analisis selesai, **then** setiap field ledger memiliki state dan source reference; inferensi tidak boleh dilabeli sebagai ucapan klien.

### US-2 — Klarifikasi tanpa copy-paste

**Given** ledger belum siap, **when** client menjawab tiga pertanyaan melalui link, **then** Pub/Sub melanjutkan run yang sama dan UI owner menampilkan state terbaru tanpa menyalin jawaban manual.

### US-3 — Baseline tidak dapat ditimpa diam-diam

**Given** baseline v1 disetujui, **when** ada perubahan, **then** v1 tetap dapat dilihat dan perubahan muncul sebagai v2/change request dengan diff, actor, dan timestamp.

### US-4 — Scope drift dapat dijelaskan

**Given** request baru, **when** agent mengusulkan klasifikasi, **then** ia menyertakan baseline field/criterion yang mendukung keputusan; freelancer dapat override dan override tercatat.

### US-5 — Hasil dapat diterima per criterion

**Given** evidence terpasang pada criterion, **when** klien meninjau, **then** klien dapat Accept atau Request changes; penolakan menyimpan alasan dan criterion terkait.

### US-6 — Revisi tidak mengubah scope diam-diam

**Given** alasan Request changes meminta hasil yang tidak tercakup criterion, **when** agent membandingkannya dengan baseline, **then** permintaan masuk ke Guardrail sebagai proposed `AMBIGUOUS`/`CHANGE_REQUEST`; agent tidak memotong revision allowance atau mengubah baseline sendiri.

### US-7 — Memory aman

**Given** freelancer mengonfirmasi preference, **when** deal baru dibuat, **then** preference tampak sebagai freelancer policy/proposal dan tidak pernah dilabeli `CLIENT_STATED` atau `AGREED`.

### US-8 — Prompt injection tidak mengambil alih

**Given** artifact atau jawaban bebas dari client portal berisi instruksi berbahaya, **when** diproses, **then** konten diperlakukan sebagai data; agent tidak mengungkap secret, mengubah owner/status, atau memanggil tool di luar allowlist. Serangan gagal karena kapabilitas penulisan `AGREED`/approval memang tidak tersedia bagi model, bukan hanya karena prompt melarangnya.

### US-9 — Field kritis di luar tiga pertanyaan tetap dapat diselesaikan

**Given** ada field kritis yang tidak masuk tiga pertanyaan berprioritas, **when** klien membuka client portal, **then** seluruh critical-field summary tetap terlihat dan dapat diedit; `Confirm project plan` tetap nonaktif sampai semua field kritis tidak lagi `MISSING` atau `CONFLICTING`.

## 9. Ukuran keberhasilan demo

- Waktu dari input ke initial ledger <60 detik pada contoh demo.
- 100% field kritis mempunyai provenance atau state `MISSING`.
- Baseline tidak dapat disetujui saat gate gagal.
- Client response mengubah run melalui event cloud yang dapat ditunjukkan di log.
- Request tambahan menghasilkan citation ke baseline, bukan opini generik.
- UI memisahkan fakta baseline verbatim, inferensi model, dan keputusan manusia.
- Override rate klasifikasi dapat dihitung dari event log.
- Revision rounds dan drift signal diturunkan dari audit events, bukan counter mutable.
- Setiap acceptance action mencatat actor label, server timestamp, version ID, dan content hash.
- Deal kedua menunjukkan satu preference yang telah dikonfirmasi.

## 10. Risiko produk yang sengaja diterima

- Approval link tidak membuktikan identitas legal penerima; MVP menyebut actor sebagai client participant, bukan verified signatory.
- Screenshot dapat dimanipulasi; ia adalah evidence source, bukan ground truth.
- Klasifikasi in/out-of-scope dapat salah; human confirmation dan cited baseline wajib.
- Markdown/JSON record kurang cantik dibanding PDF, tetapi lebih aman untuk deadline.
