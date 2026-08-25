# 05 — Checklist Submission dan Naskah Video

## 1. Eligibility gate

- [ ] Proyek baru dibuat selama submission period; tanggal mulai sesuai commit/record nyata.
- [ ] Gemini 3.5+ benar-benar dipanggil pada hosted flow.
- [ ] Google ADK benar-benar mengorkestrasi workflow, bukan hanya dependency pasif.
- [ ] Cloud Run/Firestore/Pub/Sub digunakan dan dapat dibuktikan.
- [ ] Aplikasi mendukung English minimum.
- [ ] Hanya kategori **The Collaborative Partner** yang dipilih.
- [ ] Semua pre-existing/third-party code dan asset diungkapkan.

## 2. Deliverable Devpost

- [ ] Nama dan tagline konsisten: ScopeHandshake.
- [ ] Hosted URL dapat dibuka dari incognito.
- [ ] Test credentials/instructions diberikan bila owner login wajib.
- [ ] Client demo link tidak expired sebelum judging; gunakan dedicated judge link dengan scope minimum.
- [ ] Repo terhubung dan spin-up instructions diuji di environment bersih.
- [ ] Jika repo private, akses telah diberikan ke `testing@devpost.com` dan `cloudhackathons@google.com`.
- [ ] Semua teammate sudah diundang dan accepted.
- [ ] Architecture diagram diunggah/disertakan.
- [ ] Video publicly visible di YouTube/Vimeo, ≤4 menit, English atau English subtitles.
- [ ] Video menunjukkan agent bekerja dan bukti backend di Google Cloud.
- [ ] Model/SDK/framework/cloud services dan project start date dijawab eksplisit.
- [ ] Features, technologies, data sources, learning, challenges, dan disclosure ditulis.
- [ ] Tidak ada secret, client data nyata, atau credential di repo/video.

### Bonus — hanya setelah seluruh deliverable wajib hijau

- [ ] Public build write-up/blog/video menyatakan bahwa konten dibuat untuk mengikuti hackathon ini.
- [ ] Public social post memakai hashtag `#AllThingsAgenticHackathon`.
- [ ] Link bonus sudah dimasukkan ke submission form.
- [ ] Model Google tambahan hanya diklaim jika benar-benar terintegrasi; jangan menambah Gemma/Veo/Lyria demi bonus sebelum core stabil.

## 3. Pre-submit smoke test

- [ ] Owner login → create deal.
- [ ] Golden text + screenshot → ledger dengan provenance.
- [ ] Maksimal tiga pertanyaan muncul.
- [ ] Client link dapat dibuka incognito dan salah purpose ditolak.
- [ ] Client response memicu Pub/Sub/worker dan owner melihat update.
- [ ] Incomplete deal tidak dapat di-approve.
- [ ] Approved baseline v1 memiliki version/hash/timestamp.
- [ ] New request menunjukkan classification proposal + citation.
- [ ] Override manusia tercatat.
- [ ] Evidence terhubung ke criterion.
- [ ] Client dapat Accept/Request changes.
- [ ] Request changes di luar criterion masuk ke Guardrail, bukan mengubah baseline diam-diam.
- [ ] Baseline version baru mempertahankan acceptance untuk criterion dengan hash identik dan menandai criterion yang berubah sebagai `SUPERSEDED`.
- [ ] Satu review session mengonsumsi maksimal satu revision round setelah konfirmasi freelancer.
- [ ] Drift ledger menampilkan jumlah addition sejak baseline aktif.
- [ ] Seed script menghasilkan empat decided in-scope events; request kelima live mengubah drift counter 4 → 5 tanpa edit database manual.
- [ ] Client-answer injection hanya tersimpan sebagai data dan tidak dapat mengubah status/approval.
- [ ] Deal kedua menunjukkan confirmed preference dengan label yang benar.
- [ ] Cloud logs tidak mengandung raw token/brief/secret.
- [ ] Demo dijalankan tiga kali tanpa manual database edit.

## 4. Naskah video — target 3:40

Gunakan English voice-over atau English subtitles. Jangan mulai dengan logo panjang.

### 0:00–0:12 — Outcome dulu

**Visual:** owner Attention Inbox → conflict found → confirmed plan → accumulated drift → evidence acceptance + revision counter.

**Voice-over:**

> “ScopeHandshake turns vague freelance briefs into a shared, versioned agreement—then detects scope drift and records delivery acceptance with evidence.”

### 0:12–0:35 — Masalah dan pembeda

**Visual:** brief “modern, responsive, done Friday, a few revisions” dengan ambiguity markers.

> “A chatbot can rewrite this brief, but it cannot create shared state with the client, preserve an approved baseline, resume when the client responds, or prove which acceptance criteria were met.”

On-screen text: `Not a marketplace · Not legal e-signature · A two-party scope protocol`.

### 0:35–1:25 — Handshake

**Visual:** mulai dari analysis result yang sudah siap; upload/loading dipotong.

- **20 detik:** sorot konflik Friday-versus-Monday dengan dua kutipan verbatim, slot pertanyaan wajib, dan readiness yang terkunci.
- **20 detik:** buka client portal yang langsung merangkum deliverable/timeline/out-of-scope; pilih Monday dan tekan **Confirm project plan**.
- **10 detik:** jump cut kembali ke owner dashboard; readiness, baseline v1, dan hash tampil. Revision limit/breakpoint cukup ditampilkan sebagai on-screen text, bukan diisi live.

> “Gemini found that the screenshot contradicts the original brief. The system refuses to resolve that conflict or freeze the plan until the client chooses. The same ADK workflow then resumes through Pub/Sub.”

### 1:25–2:15 — Guardrail

**Visual:** masukkan “Please also create three vertical TikTok visuals.”

- Mulai dari seeded drift count 4; lakukan request kecil kelima live dan tunjukkan counter berubah menjadi 5.
- Dengan jump cut, tampilkan proposed `CHANGE_REQUEST` untuk request TikTok.
- Zoom citation ke approved deliverables/out-of-scope.
- Tampilkan human confirm dan changed-fields list.
- Flash counter “5 in-scope additions since baseline v1” untuk menunjukkan accumulated drift.
- Tunjukkan v1 tetap ada setelah draft v2; acceptance dengan criterion hash identik tetap berlaku.

> “The model cannot invent the boundary. Facts are verbatim baseline quotes, the classification is clearly labeled as inference, and the human records the decision. Small accepted additions also accumulate in a deterministic drift ledger.”

### 2:15–2:55 — Proof

**Visual:** mulai dari evidence yang sudah terpasang. Client memilih Accept dua dan Request changes satu, lalu menekan satu tombol submit yang membuat satu review session. Jump cut ke freelancer confirmation; counter menjadi `1 of 2 rounds used`.

> “Evidence is mapped to the exact criterion it supports. One review submission consumes at most one round after freelancer confirmation. Once the agreed rounds are exhausted, the next request is routed to the scope guardrail—not silently treated as free revision work.”

On-screen disclaimer: `Defensible audit trail, not a certified legal signature`.

### 2:55–3:15 — Persistent collaboration

**Visual:** owner confirms “two revision rounds” as preference; create second deal; policy appears as `FREELANCER_POLICY`, not `AGREED`.

> “Confirmed preferences carry into the next deal, but memory never becomes a client fact until that client approves it.”

### 3:15–3:35 — Google Cloud proof

**Visual:** architecture diagram, Cloud Run services, Pub/Sub delivery/log entry dengan job ID, Firestore baseline document. Blur project identifiers bila perlu.

> “ScopeHandshake uses Gemini 3.5 Flash, Google ADK, Cloud Run, Firestore, Pub/Sub, Cloud Storage, and Cloud Logging. The client event shown here resumed this exact worker job in Google Cloud.”

### 3:35–3:40 — Penutup

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

ScopeHandshake is a two-party AI scope and acceptance protocol. It converts brief text and screenshots into an evidence-backed Deal Ledger, asks the three highest-impact clarification questions, and gives the client a no-account review link. Once approved, the baseline is versioned and hashed. New requests are compared against that baseline with citations and human-confirmed change classification. Delivery evidence is then mapped to acceptance criteria for granular client acceptance.

### How we built it

Gemini 3.5 Flash performs multimodal extraction and semantic comparison. Google ADK orchestrates the stateful workflow. Cloud Run hosts the web, API, and private worker; Pub/Sub resumes jobs after client events; Firestore stores ledger versions, preferences, and audit events; Cloud Storage stores source/evidence images.

### Why it is agentic

The system maintains deal state across people and sessions, prioritizes clarification based on unresolved risk, resumes autonomously after external events, invokes constrained tools, and adapts to explicitly confirmed freelancer preferences. Deterministic services retain authority over readiness, approvals, versions, and hashes.

### Challenges and learning

The hardest design problem was separating model judgment from authoritative state. We use Gemini for semantic work while keeping approval gates, provenance, criterion versioning, revision accounting, drift aggregation, idempotency, and snapshot integrity deterministic. The model has no tool capable of approving a baseline, resolving a conflict, or consuming a revision round, so prompt injection cannot acquire those capabilities.

### Limitations

ScopeHandshake is not a marketplace, payment platform, legal service, certified e-signature, or automated dispute judge. Its approval records and hashes improve traceability but do not verify a participant’s legal identity or prove that uploaded evidence is truthful.

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
