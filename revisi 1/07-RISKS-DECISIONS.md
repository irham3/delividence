# 07 — Keputusan Final, Risiko, dan Fallback

## A. Keputusan yang sudah dikunci

| ID | Keputusan | Alasan |
|---|---|---|
| D-01 | Produk: **ScopeHandshake**; core artifact: **Deal Ledger** | nama produk menjelaskan mutual scope; ledger menjelaskan state/provenance |
| D-02 | Target utama: freelancer digital, bukan peserta hackathon | problem berulang, economic pain jelas, dan lebih sulit digantikan chatbot sekali pakai |
| D-03 | Kategori: **The Collaborative Partner** | state lintas sesi dan dua pihak adalah kekuatan utama |
| D-04 | Tiga fase: Handshake, Guardrail, Proof | satu lifecycle koheren dari ambiguity sampai acceptance |
| D-05 | Bukan marketplace/payment/project manager | mencegah produk melebar menjadi Upwork/Fiverr mini |
| D-06 | Approved baseline + change request, bukan legal contract generator | lebih kredibel, implementable, dan aman dari legal overclaim |
| D-07 | Defensible audit trail, bukan legal proof | hash/timestamp memperkuat integrity, tidak membuktikan identitas/kebenaran |
| D-08 | Satu ADK workflow + deterministic domain services | agentic value berasal dari state/actions, bukan jumlah agent |
| D-09 | English-first, Indonesian optional | memenuhi eligibility sekaligus relevan untuk pembuat |
| D-10 | Markdown/JSON export untuk MVP | PDF/e-sign dapat menunggu |
| D-11 | `09-DOMAIN-RULES.md` adalah kontrak normatif | criterion versioning, revision rounds, drift, conflict, event/authority tidak boleh diinterpretasikan ulang |

Keputusan ini hanya dibuka kembali jika ditemukan benturan dengan official rules atau blocker teknis yang terbukti.

## B. Pertanyaan operasional yang harus dijawab hari pertama

- [ ] Solo atau tim; seluruh invite accepted.
- [ ] Google Cloud project, billing, region, budget alert.
- [ ] Exact Gemini model ID/mode/region/quota bekerja.
- [ ] Project start date dan disclosure pre-existing work.
- [ ] Hosted domain/URL dan judge access plan.
- [ ] Repo public atau private; jika private, tester access plan.

## C. Risk register

| ID | Risiko | Peluang | Dampak | Mitigasi / fallback |
|---|---|---:|---:|---|
| R-01 | Scope proyek sendiri terlalu besar | Tinggi | Kritis | patuhi cut line; Handshake cloud gate Jumat; satu golden path saja |
| R-02 | Terlihat seperti proposal chatbot | Sedang | Kritis | demo client event, append-only approved version, cited scope drift, proof acceptance; jangan demo generation saja |
| R-03 | Terlihat seperti Upwork/Fiverr mini | Rendah | Tinggi | larang marketplace/payment/chat/rating; client portal hanya scoped actions |
| R-04 | Legal overclaim merusak trust | Sedang | Tinggi | gunakan “approval record/audit trail”; disclaimer pada UI, README, video, Devpost |
| R-05 | Client link tidak membuktikan identitas | Tinggi | Sedang | actor label, expiry/purpose, optional self-entered name/email; jangan sebut verified signatory |
| R-06 | Screenshot/evidence dimanipulasi | Sedang | Tinggi | checksum + timestamp + provenance; jelaskan bukan ground truth; client acceptance tetap eksplisit |
| R-07 | Gemini salah ekstrak atau klasifikasi | Sedang | Tinggi | schema, source citation, state rules, human confirm, ambiguous fallback |
| R-08 | Prompt injection dari brief | Sedang | Tinggi | artifact as untrusted data, tool allowlist, no secret access, fixture test |
| R-09 | Pub/Sub redelivery membuat duplikat | Sedang | Tinggi | deterministic idempotency key + Firestore transaction lease |
| R-10 | Auth/IAM memakan waktu | Tinggi | Tinggi | dummy cloud slice hari pertama; no client account; role minimum checklist |
| R-11 | Model ID/region berubah/tidak tersedia | Sedang | Kritis | verify hari pertama dari official docs dan live call; catat working config |
| R-12 | Firestore server SDK dianggap dilindungi Security Rules | Sedang | Tinggi | authorization di API/service layer + IAM; cross-owner tests |
| R-13 | Raw reasoning bocor di UI/log | Rendah | Tinggi | hanya structured reasons/events; redact request content/token; no chain-of-thought field |
| R-14 | Video tidak selesai/lebih 4 menit | Sedang | Kritis | dry run Minggu, klip pendek, target 3:40, upload draft lebih awal |
| R-15 | Hosted demo cold start/gagal saat judging | Sedang | Tinggi | health checks, synthetic judge data, repeated smoke test; pertimbangkan min instance dengan budget cap |
| R-16 | Cloud cost/secret leak | Rendah | Tinggi | budget alert, quotas, IAM minimum, ADC, secret scan, no long-lived key |
| R-17 | Memory disalahartikan sebagai fakta deal | Sedang | Sedang | explicit confirmation; label `FREELANCER_POLICY`; client approval tetap wajib |
| R-18 | Change classification memicu konflik dengan klien | Sedang | Sedang | bahasa UI netral: “proposed classification”; tampilkan citation dan pilihan edit/discuss |
| R-19 | Dua service/agent mengimplementasikan schema/hash/seq berbeda | Sedang | Kritis | satu owner, satu shared module, golden vectors; bekukan §10 sebelum coding paralel |

## D. Go/no-go gates

### Gate 1 — 25 Agustus malam

**Go:** model request dan Pub/Sub → private worker berhasil di cloud.  
**No-go response:** potong UI, selesaikan cloud path; jangan lanjut feature build.

### Gate 2 — 28 Agustus malam

**Go:** text brief → client response → approved baseline v1 bekerja hosted.  
**No-go response:** Sabtu hanya perbaiki Handshake; Guardrail dipersempit menjadi satu request field, Proof satu URL/criterion.

### Gate 3 — 29 Agustus malam

**Go:** cited scope comparison dan satu evidence acceptance bekerja.  
**No-go response:** hapus image evidence/PDF/memory UI; gunakan seeded preference dan URL evidence.

### Gate 4 — 30 Agustus 18:00 WIB

**Go:** golden path lolos tiga kali, cloud proof dapat direkam.  
**No-go response:** freeze features dan gunakan backup recording dari run stabil yang wajib sudah dibuat Sabtu malam.

## E. Klaim yang dilarang

- “Legally binding agreement” atau “court-proof evidence”.
- “AI prevents all scope creep.”
- “Verified client identity” tanpa identity verification nyata.
- “Immutable” bila record masih dapat di-update/delete oleh application path biasa; sebut “append-only at application layer” sesuai implementasi.
- “Autonomous approval/negotiation” ketika manusia sebenarnya menekan tombol.
- “Google Memory Bank” bila hanya memakai Firestore preference collection.
- “Reasoning trace” untuk raw chain-of-thought.

## F. Fallback demo bila live model lambat

- Gunakan synthetic golden fixture dan pre-warmed hosted run.
- Rekam clip sukses sebelumnya sebagai bagian video; submission video tidak harus live one-take.
- Aplikasi tetap harus benar-benar dapat menjalankan model dan cloud flow; jangan mengganti backend dengan fake response lalu mengklaim live.
- Tampilkan retry/error state secara jujur bila diminta testing instructions.

## G. Setelah MVP stabil, fitur dengan leverage tertinggi

1. Verified email magic link atau integration dengan provider e-sign—setelah legal/security review.
2. GitHub/Figma/Drive evidence adapters yang memverifikasi artifact metadata secara deterministik.
3. Side-by-side scope version diff dan structured impact negotiation.
4. Team/client roles dan multiple approvers.
5. PDF acceptance record yang menyertakan manifest hash dan clear limitation language.

Jangan menambahkan semua ini untuk hackathon. Untuk peluang juara, satu lifecycle yang selesai dan dapat dipercaya lebih bernilai daripada daftar integrasi setengah jadi.
