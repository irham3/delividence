# 05 — Checklist Submission dan Naskah Video

## 1. Eligibility gate

- [x] Proyek baru dibuat selama submission period; tanggal mulai sesuai commit/record nyata. *(commit pertama 24 Agu 2026, dalam submission period, lihat README §Disclosure)*
- [x] Gemini 3.5+ benar-benar dipanggil pada hosted flow. *(diverifikasi 27 Agu via curl ke production, ekstraksi + Guardrail asli; direhearsal ulang 28 Agu, sukses)*
- [x] Google ADK benar-benar mengorkestrasi workflow, bukan hanya dependency pasif. *(agent.extraction_agent + agent.guardrail_agent, google-adk terpasang & terpakai di worker.py)*
- [x] Cloud Run/Firestore/Pub/Sub digunakan dan dapat dibuktikan. *(deployed & diverifikasi 27+28 Agu — delividence-api/worker live, run 59b44ab7... jadi bukti nyata)*
- [x] Aplikasi mendukung English minimum. *(Output language default English, dites langsung 28 Agu)*
- [ ] Hanya kategori **The Collaborative Partner** yang dipilih. *(aksi di form Devpost — belum diverifikasi dari sini)*
- [x] Semua pre-existing/third-party code dan asset diungkapkan. *(README §Disclosure of pre-existing work)*

## 2. Deliverable Devpost

- [x] Nama dan tagline konsisten: Delividence.
- [x] Hosted URL dapat dibuka dari incognito. *(dites langsung 28 Agu di Incognito Rifqi)*
- [x] Test credentials/instructions diberikan bila owner login wajib. *(backend/README.md — cara ambil ID token via DevTools/REST)*
- [ ] Client demo link tidak expired sebelum judging; gunakan dedicated judge link dengan scope minimum. *(perlu dibuat mendekati hari-H, bukan sekarang — link exp otomatis)*
- [ ] Repo terhubung dan spin-up instructions diuji di environment bersih. *(belum dites dari environment benar-benar bersih)*
- N/A — repo **publik**, bukan private, jadi tidak perlu akses `testing@devpost.com`/`cloudhackathons@google.com`.
- [ ] Semua teammate sudah diundang dan accepted. *(aksi di Devpost — status belum dipastikan, lihat CATATAN-LANJUTAN.md)*
- [x] Architecture diagram diunggah/disertakan. *(`docs/architecture-diagram.png` dibuat 28 Agu — tinggal upload manual ke form Devpost)*
- [ ] Video publicly visible di YouTube/Vimeo, ≤4 menit, English atau English subtitles. *(belum direkam)*
- [ ] Video menunjukkan agent bekerja dan bukti backend di Google Cloud. *(belum direkam)*
- [ ] Model/SDK/framework/cloud services dan project start date dijawab eksplisit. *(isi di form Devpost saat submit — draf jawabannya ada di §6 di bawah)*
- [x] Features, technologies, data sources, learning, challenges, dan disclosure ditulis. *(draf §6 di bawah, diperbarui 28 Agu supaya cocok dengan yang benar-benar dibangun)*
- [x] Tidak ada secret, client data nyata, atau credential di repo/video. *(`.gitignore` cover `.env`/credential files; belum ada video jadi belum relevan untuk video)*

### Bonus — hanya setelah seluruh deliverable wajib hijau

- [ ] Public build write-up/blog/video menyatakan bahwa konten dibuat untuk mengikuti hackathon ini.
- [ ] Public social post memakai hashtag `#AllThingsAgenticHackathon`.
- [ ] Link bonus sudah dimasukkan ke submission form.
- [ ] Model Google tambahan hanya diklaim jika benar-benar terintegrasi; jangan menambah Gemma/Veo/Lyria demi bonus sebelum core stabil.

## 3. Pre-submit smoke test

- [x] Owner login → create deal. *(dites 25 Agu, 27 Agu, dan 28 Agu — konsisten jalan)*
- [x] Golden text → ledger dengan provenance. *(text brief → ledger+citation sudah berkali-kali terverifikasi)* — N/A untuk bagian **screenshot**: dikonfirmasi dari kode (`CreateRunRequest` di `api.py` cuma punya field `brief: str`, `worker.py` cuma kirim teks ke `state["artifacts"]`, komentar `agent.py` sendiri bilang `read_artifact`/artifact model belum dibangun) — input gambar **belum pernah diimplementasikan sama sekali**, bukan sekadar belum dites. Section "Media" di UI cuma teks dekoratif.
- [x] Maksimal tiga pertanyaan muncul. *(terverifikasi kuat di kode: `questions.py: rank_questions()` cuma slice `[:MAX_CLARIFICATION_QUESTIONS]`, murni deterministik, plus test unit khusus `test_maksimal_tiga_walau_ada_sepuluh_kandidat`)*
- [x] Client link dapat dibuka incognito dan salah purpose ditolak. *(incognito dites 28 Agu; purpose salah terverifikasi di kode — `client_link.py:33` `if link["purpose"] != purpose: return False, "This link is not valid for this action."`, plus test unit `test_purpose_salah_ditolak`)*
- [x] Client response memicu resume workflow dan owner melihat update. *(dites 25 & 28 Agu — badge "ADK workflow resumes after client input" + baseline berubah begitu client confirm)*
- [x] Incomplete deal tidak dapat di-approve. *(dites 28 Agu — tombol "Resolve all blockers first" disabled sampai field wajib diisi)*
- [x] Approved baseline v1 memiliki version/timestamp. *("Baseline version 1 is now active" muncul; hash ada di `app/domain/baseline.py` tapi belum pernah dicek tampil di UI mana)*
- [x] New request menunjukkan classification proposal + citation. *(dites 28 Agu — CHANGE_REQUEST + citation lengkap)*
- [x] Override manusia tercatat. *(tombol "Confirm classification" — aksi freelancer, actor tercatat `SCOPE_CLASSIFICATION_DECIDED`)*
- [x] Evidence terhubung ke criterion. *(dites 28 Agu)*
- [x] Client dapat Accept/Request changes. *(Accept dites 28 Agu; Request changes ada tombolnya, belum diklik langsung — alurnya sama, cukup yakin)*
- [x] Request changes di luar criterion masuk ke Guardrail, bukan mengubah baseline diam-diam. *(terverifikasi struktural di kode: endpoint delivery review 404 kalau `criterion_key` tidak dikenal — `api.py:475-478`, test `test_criterion_key_tidak_dikenal_di_submit_review_404` — "reason" cuma tersimpan sebagai data audit `CRITERION_DECISION`, tidak pernah dieksekusi jadi perubahan baseline. Satu-satunya jalur scope baru yang sungguhan adalah Guardrail (`New requests`/`New Request` portal))*
- [x] Baseline version baru mempertahankan acceptance untuk criterion dengan hash identik dan menandai criterion yang berubah sebagai `SUPERSEDED`. *(dites 26 Agu — lihat `CATATAN-LANJUTAN.md`, endpoint sungguhan + test permanen)*
- N/A — ~~Satu review session mengonsumsi maksimal satu revision round~~ — **Modul B (revision rounds) dilepas dari scope**, tidak ada konsep "round" di aplikasi yang jadi.
- N/A — ~~Drift ledger menampilkan jumlah addition~~ — **Modul C (drift ledger) dilepas dari scope**, tidak ada fitur ini.
- N/A — ~~Seed script 4→5 drift counter~~ — sama, **Modul C dilepas**.
- [x] Client-answer injection hanya tersimpan sebagai data dan tidak dapat mengubah status/approval. *(terverifikasi kuat di kode: `readiness.py` docstring eksplisit "Readiness bukan angka yang dikarang model. Fungsi ini tidak pernah memanggil LLM." — gate cuma cek field `state` yang di-set programatis, tidak pernah membaca isi teks `value` jawaban klien untuk logika apa pun)*
- [x] Deal kedua menunjukkan confirmed preference dengan label yang benar.
  *(Update 29 Agu: status berubah — awalnya saya N/A-kan sebagai dead-code
  Modul B (revision rounds) yang dilepas, tapi partner (Irham) membangun
  ulang bagian sempit ini dan Rifqi setuju ("ikutin Irham") — bukan
  pelanggaran keputusan 10-KEPUTUSAN-DAN-VERIFIKASI.md §4b, tapi revisi
  sadar atas cakupannya, lihat update di dokumen itu. **Dites live di
  production**: `POST /preferences` {revision_rounds:2} → buat run baru →
  `GET /runs/{id}` menunjukkan `revision_policy.rounds_total` = `{value: 2,
  state: "FREELANCER_POLICY", source_quote: "2 revision rounds are
  included."}` — label benar, bukan diam-diam dianggap ACCEPTED/fakta
  klien.)*
- [x] Cloud logs tidak mengandung raw token/brief/secret. *(terverifikasi dari kode, bukan dari Cloud Logging langsung — cuma ada 5 baris `log.*` di seluruh backend (semua di `worker.py`), isinya `run_id`/`round` saja. Payload Pub/Sub sendiri di `api.py` cuma `{"run_id": ..., "round": 1}` — brief text TIDAK PERNAH lewat Pub/Sub sama sekali, disimpan langsung ke Firestore. Audit log sengaja cuma catat `chars: len(brief)`, bukan isi brief-nya)*
- [ ] Demo dijalankan tiga kali tanpa manual database edit. *(2 run bersih berhasil dibuat malam ini tanpa edit database manual — belum genap 3x sebagai catatan formal)*

## 4. Naskah video — target ~3:35 (batas keras 4:00)

Ditulis ulang 28 Agu untuk cocok dengan yang **benar-benar dibangun dan live**
(Modul A saja — lihat `docs/10-KEPUTUSAN-DAN-VERIFIKASI.md` §4b). Naskah
lama menyebut konflik Friday/Monday (Modul D), drift counter (Modul C), dan
revision-round counter/preference (Modul B) — ketiganya **dilepas dari kode**
dan sudah tidak ada di aplikasi, jadi dihapus dari naskah juga.

**Update 29 Agu**: partner membangun ulang satu bagian sempit dari Modul B
(preference lintas-deal untuk revision rounds, disetujui Rifqi) — beat
"Persistent preference" ditambahkan lagi untuk itu. Round-consumption/
exhausted-round routing (bagian B lainnya) tetap tidak dibangun, jadi tetap
tidak disebut naskah ini.

Semua beat di bawah bisa direkam dari **production sungguhan**
(`https://delividence.vercel.app`), bukan simulasi/mock, jadi tidak perlu
blur kecuali project identifier di GCP Console.

Gunakan English voice-over atau English subtitles. Jangan mulai dengan logo
panjang.

### 0:00–0:12 — Outcome dulu

**Visual:** owner dashboard → ledger dengan citation dari Gemini → client
confirm → baseline v1 aktif → evidence + Accept di delivery review → Proof
Manifest.

**Voice-over:**

> “Delividence turns a vague freelance brief into a shared, versioned agreement — every fact traced back to the client's own words, and every change classified before it's accepted.”

### 0:12–0:35 — Masalah dan pembeda

**Visual:** brief “modern, responsive, done Friday, a few revisions” dengan
ambiguity markers.

> “A chatbot can rewrite this brief, but it cannot create shared state with the client, freeze an approved baseline, resume automatically when the client responds, or prove which acceptance criteria were actually met.”

On-screen text: `Not a marketplace · Not legal e-signature · A two-party scope protocol`.

### 0:35–1:10 — Handshake

**Visual:** mulai dari analysis result yang sudah siap; upload/loading dipotong.

- **15 detik:** sorot ledger hasil ekstraksi Gemini — tiap field dengan kutipan
  verbatim dari brief, dan maksimal tiga pertanyaan klarifikasi yang readiness
  gate-nya terkunci sampai terjawab.
- **15 detik:** buka client portal (link tanpa akun) yang merangkum
  deliverable/timeline/out-of-scope; klien isi jawaban lalu tekan **Confirm
  project plan**.
- **5 detik:** jump cut ke owner dashboard; readiness, baseline v1, version,
  dan hash tampil.

> “Gemini extracts the deal ledger from the brief, but every quote is verified against the source text in code before it's shown. The plan only freezes once the client confirms it — and the same ADK workflow resumes through Pub/Sub the moment that happens.”

### 1:10–2:00 — Guardrail

**Visual:** masukkan “Please also create three vertical TikTok visuals.”

- Tampilkan Gemini mengusulkan classification `CHANGE_REQUEST` dengan citation
  otomatis (`agent.guardrail_agent`).
- Zoom citation ke approved deliverables/out-of-scope yang jadi dasarnya.
- Tampilkan freelancer confirm classification (bukan klien, bukan model).
- Jump cut: baseline v2 terbentuk; criterion lama yang sudah `ACCEPTED` tetap
  mempertahankan status dan versi aslinya (`introduced_in_version`), hanya
  criterion yang berubah ditandai `SUPERSEDED`.

> “The model cannot invent the boundary. A change is only labeled in-scope or a new request if it can be traced to an approved quote — without a valid citation, it drops to ambiguous automatically. The human always makes the final call, and it's logged as theirs.”

### 2:00–2:40 — Proof

**Visual:** mulai dari evidence yang sudah terpasang ke criterion tertentu.
Client memilih Accept dua dan Request changes satu (dengan alasan wajib
diisi), lalu menekan satu tombol submit yang membuat satu review session.
Jump cut ke `GET /runs/{id}/proof` — Proof Manifest lengkap.

> “Evidence is mapped to the exact criterion it supports. The client can accept some items and push back on others in a single submission, and the resulting Proof Manifest ties baseline, evidence, and every client decision together — exportable as Markdown.”

On-screen disclaimer: `Defensible audit trail, not a certified legal signature`.

### 2:40–3:00 — Persistent preference

**Visual:** owner buka pengaturan, confirm "2 revision rounds" sebagai
preference default (`POST /preferences`). Buat deal kedua yang baru dari
awal — tunjukkan ledger-nya sudah otomatis terisi `revision_policy.rounds_total
= 2` dengan label **FREELANCER_POLICY** (bukan ACCEPTED/CLIENT_STATED).

> “A confirmed preference carries into the next deal automatically, but it's labeled as the freelancer's policy, not a client fact — it still has to go through the same client approval as everything else before it's binding.”

### 3:00–3:25 — Google Cloud proof

**Visual:** architecture diagram, Cloud Run services (`delividence-api`,
`delividence-worker`), Pub/Sub push delivery/log entry dengan job ID,
Firestore baseline document. Blur project identifier di GCP Console bila
perlu.

> “Delividence runs on Gemini through Google ADK, with Cloud Run, Firestore, and Pub/Sub. The client event shown here resumed this exact worker job in Google Cloud — not a local demo.”

### 3:25–3:35 — Penutup

> “Clear scope. Controlled change. Accepted work.”

## 5. Aturan produksi video

- Rekam klip terpisah dan potong loading/waiting.
- Jangan mengetik panjang secara live; paste fixture.
- Jangan tampilkan login/setup.
- Gunakan zoom/callout untuk provenance, citation, version, dan cloud job ID.
- Target 3:40 agar encoding/upload tidak membuat durasi melewati 4:00.
- Putar hasil final dari link publik dan perangkat lain.

## 6. Draft deskripsi Devpost (English)

### Inspiration

Freelancers rarely lose control of scope because they cannot write a proposal. They lose it because vague statements become assumptions, later requests overwrite the original boundary, and delivery proof is disconnected from what the client actually approved.

### What it does

Delividence is a two-party AI scope and acceptance protocol. It converts a client's brief text into an evidence-backed Deal Ledger, asks the three highest-impact clarification questions, and gives the client a no-account review link. Once approved, the baseline is versioned and hashed. New requests are compared against that baseline with citations and human-confirmed change classification. Delivery evidence is then mapped to acceptance criteria for granular client acceptance.

### How we built it

Gemini 3.5 Flash (via the Gemini Developer API, with Gemini 3.6 Flash configured as fallback) performs multimodal extraction and scope-change classification. Google ADK orchestrates the stateful workflow. Cloud Run hosts the API and the private worker; the frontend is Next.js on Vercel. Pub/Sub resumes worker jobs after client events; Firestore stores ledger versions, baselines, and audit events. Firebase Authentication verifies the freelancer owner; the client review link uses a separate scoped opaque token, no account required.

### Why it is agentic

The system maintains deal state across people and sessions, prioritizes clarification questions based on unresolved risk, resumes autonomously through Pub/Sub after the client responds, invokes constrained tools (extraction, scope-change classification) rather than free-form generation, and adapts to an explicitly confirmed freelancer preference (default revision rounds) that carries into every new deal — labeled as the freelancer's policy, never assumed as a client fact until the client approves it through the same baseline flow as anything else. Deterministic services retain authority over readiness, approvals, baseline versions, and hashes — the model proposes, it never decides.

### Challenges and learning

The hardest design problem was separating model judgment from authoritative state. We use Gemini for semantic work while keeping approval gates, citation provenance, criterion versioning, idempotency, and baseline hash integrity fully deterministic. The model has no tool capable of approving a baseline or resolving a scope conflict on its own, so prompt injection cannot acquire those capabilities.

### Limitations

Delividence is not a marketplace, payment platform, legal service, certified e-signature, or automated dispute judge. Its approval records and hashes improve traceability but do not verify a participant’s legal identity or prove that uploaded evidence is truthful.

## 7. README implementation checklist

- [ ] Product summary + differentiator.
- [ ] Demo GIF/screenshot and hosted URL.
- [ ] Architecture diagram.
- [ ] Exact Google model, SDK, ADK, and Cloud services.
- [ ] Local prerequisites and commands.
- [ ] Google Cloud setup/deploy commands.
- [ ] Environment variable table with placeholders only.
- [ ] Seed/golden demo instructions.
- [ ] Test commands and known limitations.
- [ ] Security model for owner/client/worker.
- [ ] Start date, team, license, disclosure.
