# 02 — Arsitektur dan Desain Teknis

## 1. Sasaran arsitektur

Arsitektur harus membuktikan empat hal di demo: Gemini memahami brief multimodal, ADK mengelola workflow stateful, tindakan klien melanjutkan proses secara event-driven, dan semua state penting tersimpan di Google Cloud. Sistem sengaja tidak memakai banyak agent; kompleksitas berada pada state transition dan evidence integrity.

## 2. Bentuk sistem

```text
Owner browser                         Client browser (no account)
     │ Firebase ID token                   │ scoped opaque token
     └──────────────┬───────────────────────┘
                    ▼
          Web UI — Next.js / Cloud Run
                    │ HTTPS
                    ▼
          API — FastAPI / Cloud Run
           │         │          │
           │         │          └── Cloud Storage (images/evidence)
           │         └───────────── Firestore (deal state/audit)
           └─────────────────────── Pub/Sub topic
                                         │ authenticated push
                                         ▼
                                Worker — ADK / Cloud Run
                                   │            │
                                   │            └── Gemini 3.5 Flash
                                   └─────────────── Firestore
```

UI melakukan polling status run setiap 2–3 detik untuk MVP. WebSocket/SSE tidak diperlukan untuk demo.

### Google technology mapping

| Teknologi | Fungsi nyata |
|---|---|
| Gemini 3.5 Flash | ekstraksi text/image, ambiguity detection, question ranking, scope comparison, structured explanation |
| Google ADK | workflow state, orchestration, tool calls, resume setelah event |
| Cloud Run | web, API, dan private worker |
| Firestore | deals, append-only approved snapshots, preferences, jobs, audit events |
| Pub/Sub | queue dan resume ketika artifact/client response masuk |
| Cloud Storage | source screenshot dan evidence image |
| Cloud Logging | bukti run, latency, error, dan Pub/Sub delivery |

Keputusan tetap: model dipanggil melalui Google Gen AI/ADK pada **Vertex AI** menggunakan Application Default Credentials, dengan `GOOGLE_GENAI_USE_VERTEXAI=TRUE`. Verifikasi exact model ID, region, dan quota pada hari pertama; Gemini Developer API/API-key mode bukan fallback MVP.

## 3. Batas layanan

### Web

- Owner attention inbox, deal editor, timeline, dan client portal.
- Tidak pernah membaca Firestore secara langsung.
- Mengirim Firebase ID token ke API untuk route owner.
- Client route hanya membawa opaque token ke API dan mendukung clarification, approval, delivery review, serta new-request submission.

### API

- Memverifikasi owner identity dan ownership setiap deal.
- Memvalidasi client token, expiry, purpose, dan deal binding.
- Menerima upload kecil melalui API, menulis artifact ke Cloud Storage, lalu membuat metadata, job, dan Pub/Sub message. MVP tidak memakai signed upload URL.
- Menjalankan operasi deterministik: readiness, canonicalization/hash, version increment, approval gate.
- Tidak menjalankan model request panjang di request client.

### ADK worker

- Hanya menerima authenticated Pub/Sub push.
- Mengambil job dan deal state dari Firestore.
- Menjalankan satu workflow berdasarkan `job_type`.
- Menulis proposal/analysis, bukan keputusan approval final.
- Aman terhadap redelivery melalui transaction lease dan idempotency key.

## 4. Workflow agent

### 4.1 State machine

```text
DRAFT
  └─ ANALYZE_BRIEF → NEEDS_CLARIFICATION
                         └─ CLIENT_RESPONDED → READY_FOR_BASELINE
                                                   └─ CLIENT_CONFIRMED
                                                          └─ BASELINE_ACTIVATED → ACTIVE
ACTIVE
  ├─ NEW_REQUEST → SCOPE_REVIEW → CHANGE_PROPOSED → CHANGE_APPROVED → ACTIVE(v+1)
  └─ EVIDENCE_ADDED → DELIVERY_REVIEW → PARTIALLY_ACCEPTED / ACCEPTED
                                              └─ OUTSIDE_CRITERION → SCOPE_REVIEW
```

Status berubah melalui fungsi domain deterministik. Model hanya menghasilkan structured candidate output.

### 4.2 Tool allowlist

| Tool | Hak | Catatan |
|---|---|---|
| `load_deal_context` | read | hanya deal yang tercantum di job |
| `read_artifact` | read | text atau Cloud Storage object milik deal melalui server authorization |
| `save_ledger_draft` | write | schema tervalidasi; tidak dapat membuat `AGREED` |
| `save_questions` | write | menyimpan daftar kandidat; tidak menentukan atau mengaktifkan final top-three |
| `save_scope_analysis` | write | proposal + cited baseline references |
| `save_preference_candidate` | write | belum menjadi memory hingga owner confirm |
| `validate_quote_candidate` | compute | memeriksa kutipan verbatim terhadap artifact; tidak menulis domain state |

Agent tidak memiliki tool untuk mengirim uang, mengirim email, mengubah owner, menghapus baseline, menyetujui atas nama manusia, atau membaca deal lain.

### 4.3 Structured model output

Semua output Gemini divalidasi dengan schema. Contoh ekstraksi field:

```json
{
  "field": "revision_policy.rounds",
  "value": 2,
  "state": "FREELANCER_POLICY",
  "source_artifact": "artifact:policy-1",
  "source_quote": "Two revision rounds are included.",
  "confidence": 0.99,
  "needs_confirmation": true
}
```

Model tidak boleh menghasilkan state `AGREED`; hanya domain service yang dapat menetapkannya setelah tindakan client yang valid. Tujuh tool model bersifat tertutup: `load_deal_context`, `read_artifact`, `save_ledger_draft`, `save_questions`, `save_scope_analysis`, `save_preference_candidate`, dan `validate_quote_candidate`.

Setelah structured output selesai, API/worker **selalu** memvalidasi setiap `source_quote` terhadap artifact sebelum draft ditulis, terlepas dari apakah model memanggil `validate_quote_candidate`. Field yang gagal validasi turun ke `PROPOSED` atau `MISSING` dan tidak dapat diatribusikan sebagai `CLIENT_STATED`.

### 4.4 Ranking clarification questions

Agent membuat kandidat berdasarkan missing/conflicting fields lalu memberi skor terstruktur:

`priority = scope_impact + acceptance_impact + schedule_impact + conflict_severity`

Satu fungsi domain service membentuk himpunan final secara atomik: promosikan critical field `CONFLICTING` terlebih dahulu, lalu isi sisa slot dari ranking hingga maksimal tiga pertanyaan aktif. `save_questions` hanya menerima kandidat dan tidak menegakkan limit sendiri. Ini mencegah hasil empat pertanyaan akibat enforcement ganda dan mencegah approval deadlock.

### 4.5 Scope drift analysis

Input model hanya request baru dan approved baseline terbaru. Output wajib berisi:

- proposed classification: `IN_SCOPE`, `AMBIGUOUS`, atau `CHANGE_REQUEST`;
- cited `ledger_field_id`/`criterion_key` dan kutipan verbatim yang lolos `validate_quote`;
- explanation maksimal 80 kata;
- proposed impact fields untuk change request;
- confidence dan `requires_human_confirmation=true`.

Jika tidak ada citation yang relevan, hasil otomatis `AMBIGUOUS`; jangan mengizinkan model menyimpulkan `IN_SCOPE`/`CHANGE_REQUEST` tanpa dasar.

Guardrail selalu menampilkan tiga lapis terpisah: fakta berupa kutipan baseline, inferensi model berlabel proposal, dan keputusan manusia. Drift ledger tidak dihitung model; agregat request dihitung deterministik dari `SCOPE_CLASSIFICATION_DECIDED` sejak `BASELINE_ACTIVATED` terbaru.

## 5. Integrity model

### Approved snapshot

Saat client menyetujui baseline/change:

1. API memuat draft pada transaction.
2. Readiness gates dihitung ulang.
3. Data diubah menjadi canonical JSON: key diurutkan, format stabil, field volatile dibuang.
4. Server menghitung SHA-256.
5. Snapshot baru menyimpan criteria di dalam `canonical_payload`, dengan stable `criterion_key` dan `text_hash`.
6. Snapshot disimpan dengan version, actor label, server timestamp, dan hash.
7. Draft berikutnya menunjuk `parent_version`; snapshot lama tidak di-update.

Hash mendeteksi perubahan isi setelah snapshot, tetapi bukan bukti identitas atau kebenaran dunia nyata.

### Evidence item

Evidence menyimpan type, URI/object path, checksum bila berupa file, upload timestamp, uploader role, stable `criterion_key`, dan caption. Acceptance Matrix memisahkan artifact integrity, optional deterministic checks, `AI_ASSISTED` assessment, dan client decision agar model judgment tidak tampil sebagai fakta. Client UI mengumpulkan semua keputusan criterion dan mengirim satu payload; service membuat tepat satu `review_session_id` dan event per criterion dalam transaksi yang konsisten. Status `ACCEPTED`, `CHANGES_REQUESTED`, `SUPERSEDED`, atau `WITHDRAWN` selalu diturunkan menurut `09-DOMAIN-RULES.md` Modul A.

## 6. Model data Firestore

```text
users/{user_id}
  display_name, locale, created_at

users/{user_id}/preferences/{preference_id}
  key, value, source, confirmed_at, active

deals/{deal_id}
  owner_id, title, locale, status, active_baseline_version,
  current_run_id, audit_seq, created_at, updated_at

deals/{deal_id}/artifacts/{artifact_id}
  type, storage_path?, text?, checksum?, uploader_role, created_at

deals/{deal_id}/ledger_drafts/{draft_id}
  parent_version, fields[], readiness, created_by, created_at

deals/{deal_id}/baselines/{version_id}
  canonical_payload{deliverables, in_scope, out_of_scope, timeline,
  revision_policy, criteria{criterion_key{text,text_hash,introduced_in_version}}},
  payload_hash, parent_version, status, approved_by, approved_at,
  activated_seq, activated_at

deals/{deal_id}/questions/{question_id}
  field_refs[], text, priority, status, answer, answered_at

deals/{deal_id}/requests/{request_id}
  raw_text, artifact_ref?, submitted_by, proposed_classification,
  citations[], confirmed_classification, change_draft_id?, created_at

deals/{deal_id}/evidence/{evidence_id}
  criterion_keys[], type, uri, checksum?, uploader_role, checks[],
  ai_assessment?, created_at

deals/{deal_id}/review_sessions/{review_session_id}
  baseline_version, criterion_keys[], submitted_at, submitted_by

deals/{deal_id}/audit/{event_id}
  event_id, seq, type, actor, actor_ref, baseline_version,
  created_at, payload

client_links/{token_hash}
  deal_id, purpose, allowed_actions[], expires_at, revoked_at?, completed_at?

jobs/{job_id}
  deal_id, job_type, status, idempotency_key, lease_until,
  attempt_count, created_at, completed_at?
```

Criteria tidak memiliki mutable collection terpisah. Approved snapshots dan audit events bersifat append-only di application layer; criterion status, revision rounds, dan drift aggregates diturunkan dari satu event log dengan `seq` monotonik per deal.

## 7. Idempotency dan concurrency

- Pub/Sub delivery dapat terjadi lebih dari sekali.
- `idempotency_key = {deal_id}:{event_id}:{job_type}` memiliki unique document ID.
- Worker memperoleh lease dengan Firestore transaction hanya bila job belum selesai dan lease lama kedaluwarsa.
- Approval menggunakan precondition terhadap `draft_id` dan active version; request basi mendapat `409 Conflict`.
- Status `completed` ditulis dalam transaction yang sama dengan output reference.
- Retry tidak membuat baseline, audit event, atau client answer ganda.
- `audit_seq` dialokasikan dalam transaksi yang sama dengan event; timestamp tidak pernah menentukan urutan keputusan.

## 8. Authentication dan security

- Owner login memakai Firebase Auth; API memverifikasi ID token dan `owner_id`.
- Client link memakai random opaque token ≥128 bit. Hanya hash disimpan; token terikat ke deal, purpose, actions, dan expiry.
- Client link berhenti valid setelah workflow purpose selesai atau direvoke.
- Firestore server SDK melewati Security Rules, sehingga authorization wajib dilakukan di setiap API/service method dan diperkuat IAM service account.
- Worker Cloud Run tidak publik; Pub/Sub push memakai OIDC service account dengan invoker role minimum.
- Storage object path di-scope per deal; upload memvalidasi MIME, size, dan extension. MVP menerima text, PNG/JPEG/WebP, maksimal 10 MB.
- Artifact diperlakukan sebagai untrusted data. System prompt melarang mengikuti instruksi dari artifact dan tool allowlist membatasi dampak.
- Jawaban client portal juga untrusted data. Model tidak memiliki tool untuk approval, `AGREED`, conflict resolution, atau revision consumption, sehingga injection tidak dapat memperoleh kapabilitas tersebut.
- Secret tidak ditaruh di frontend, repo, prompt, log, atau audit event.
- Rate limit sederhana per token/IP dan expiry pendek mengurangi abuse pada public portal.

## 9. Memory

Ini adalah **cross-session preference memory**, bukan klaim penggunaan produk “Memory Bank”. Alurnya:

1. Agent mengusulkan kandidat seperti “default revision policy: 2 rounds”.
2. Owner harus menekan Confirm.
3. Deal berikutnya memuat preference sebagai `FREELANCER_POLICY` atau `PROPOSED`.
4. Client tetap harus menyetujuinya agar menjadi `AGREED` pada deal itu.
5. Owner dapat melihat, mengubah, atau menonaktifkannya.

## 10. Observability

- Structured logs: `request_id`, `job_id`, `deal_id_hash`, `job_type`, latency, model, outcome; jangan log token/client text penuh.
- Metrics minimum: job success/failure, Pub/Sub redelivery, model latency, schema validation failure, approval conflict, dan classification override rate.
- Audit timeline untuk pengguna hanya memuat event dan alasan terstruktur, bukan internal chain-of-thought.
- Demo cloud proof: Cloud Run revisions, Firestore documents, Pub/Sub delivery, dan log worker untuk satu `job_id`.

## 11. Keputusan dan alternatif

| Keputusan | Dipilih | Alternatif ditolak | Konsekuensi |
|---|---|---|---|
| Orchestration | satu ADK workflow + deterministic services | banyak role-playing agents | lebih mudah diuji; kurang teatrikal tetapi lebih kredibel |
| Async work | Pub/Sub push ke private worker | synchronous model call | lebih banyak infra; resume dan cloud proof jauh lebih jelas |
| Client access | scoped no-account link | client account wajib | friksi rendah; identitas bukan verified signatory |
| Record | append-only approved snapshot + Markdown/JSON export | legal PDF/e-sign | selesai lebih cepat; klaim hukum dibatasi |
| Updates | polling | WebSocket/SSE | UX sedikit kurang real-time; implementasi stabil |
| Storage | API-only Firestore access | browser direct Firestore | authorization terpusat; API menjadi critical boundary |

## 12. Validasi arsitektur

- Unit: readiness gates, canonical hash, token validation, state transition, idempotency.
- Integration: client answer → Pub/Sub → worker → updated ledger.
- Integration: approved v1 tetap identik setelah change draft dibuat.
- Security: owner A tidak dapat membaca deal B; expired/wrong-purpose token ditolak; worker route tidak publik.
- Model contract: malformed output gagal tertutup dan job dapat di-retry.
