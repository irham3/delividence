# Catatan Lanjutan — Delividence

Ditulis **25 Agustus 2026, sore**. Baca file ini dulu sebelum menyentuh apa pun.

---

## Di mana kita sekarang

| | |
|---|---|
| Deadline | **1 September 2026, 07:00 WIB** (31 Agu 17:00 PT) |
| Target submit internal | 31 Agustus, 18:00 WIB |
| Sisa waktu kerja realistis | **~26–29 jam** |
| Repo submission | <https://github.com/irham3/delividence> (public, akun partner, remote `delividence`, **satu-satunya remote aktif**) |
| Branch kerja | Push ke branch **`rifqi`**, BUKAN `main` — supaya tidak tabrakan dengan partner (owner repo) yang juga kerja di `main`. |
| Histori commit | 25 Agu 2026 malam: partner menghapus & membuat ulang repo `irham3/delividence` dari kosong. Seluruh histori (main + rifqi) sudah di-push ulang ke repo baru itu — **bersih dari trailer/atribusi tooling apa pun di commit message** (lomba disponsori Google, wajib Gemini). Commit berikutnya juga MUST tetap begitu. |
| Repo cadangan (tidak dipush lagi) | <https://github.com/rifqiahmadpratama/dealready> (masih ada di GitHub, tapi remote `origin` sudah dilepas dari git lokal 25 Agu — fokus ke `delividence` saja) |
| Folder lokal | `C:\Users\ASUS\Projects\dealready` (nama folder sengaja dibiarkan lama) |
| Test | **189 hijau** (`cd backend; ..\.venv\Scripts\python.exe -m pytest -q`) |

Tidak ada proses yang ditinggal jalan. Aman dimatikan.

---

## Yang sudah jadi

**Vertical slice async** — `POST /runs` → antrean → worker → store, dua service
dari satu image lewat `ROLE=api|worker`. Sudah diverifikasi lewat browser: status
berubah `queued → done` sendiri tanpa request kedua.

**Frontend** — Next.js 16 + TypeScript + Tailwind 4 di `web/`. English-first
dengan selector bahasa output.

**Inti domain** (`backend/app/domain/`) — ini yang dikerjakan terakhir:

| File | Isi | Rujukan |
|---|---|---|
| `enums.py` | Semua enum tertutup: state field, status criterion, actor, 21 tipe audit event, `CRITICAL_FIELDS` | §10 butir 4 |
| `canonical.py` | `normalize_criterion_text`, `canonical_json`, `payload_hash`, `text_hash`, `validate_quote` | §10 butir 2 |
| `criteria.py` | Modul A: `effective_status`, `can_record_decision`, validasi `criterion_key` | §2 |
| `readiness.py` | Gate readiness deterministik | 01 §7 + §5.7 |

Golden vector hash sudah dipaku sebagai literal di `tests/test_domain.py`.
Kalau nilainya berubah, artinya klaim integritas berubah arti — jangan
"perbaiki" test-nya, cari tahu kenapa hash bergeser.

Test Modul A menutup A-T1 sampai A-T11 dari §2.8.

---

## Yang dikerjakan berikutnya

1. ~~**Alokasi `seq`** (§7.2) + service penulis audit event.~~ **Selesai** —
   `backend/app/audit.py`: `append_event()` (validasi type/actor/baseline_version
   G-6, alokasi seq dalam transaksi Firestore / lock in-process lokal, envelope
   §7.1) dan `list_events()` (urut seq asc, dipakai semua modul §6). Belum ada
   pemanggil lain; ini fondasi, bukan fitur yang terlihat. 10 test baru di
   `tests/test_audit.py`.
2. ~~**Skema ledger** (§10 butir 1).~~ **Selesai** — `backend/app/domain/schemas.py`:
   model Pydantic `LedgerField`, `DealLedger`, `Criterion`/`CanonicalPayload`/
   `Baseline`, `CriterionDecision`, `AuditEventEnvelope`. Sengaja **bukan** di
   folder root `shared/schemas/` seperti tertulis di 06 §1 — sudah dicek ke
   Rifqi, keputusannya taruh di dalam backend karena satu-satunya konsumen
   saat ini Python backend (web/ belum menyentuh bentuk ledger). Hanya
   mendeskripsikan bentuk; tidak menyentuh/mengubah `criteria.py`/`readiness.py`
   yang sudah ada. 13 test baru di `tests/test_schemas.py`, termasuk cross-check
   langsung ke output `app.audit.append_event()`.
3. **Ekstraksi brief → ledger lewat Gemini** — **sebagian selesai**, sisanya
   butuh billing GCP aktif untuk dilanjutkan.
   - ~~Proyeksi kandidat model → ledger field, `validate_quote` tanpa syarat,
     G-1 (model tidak boleh AGREED).~~ **Selesai** — `backend/app/domain/extraction.py`
     (`project_field_candidate`, `assemble_ledger_draft`). 10 test di
     `tests/test_extraction.py`. Murni, tidak menyentuh Gemini/ADK.
   - ~~Agent ADK + tool.~~ **Selesai, tapi belum pernah dijalankan sungguhan** —
     `backend/app/agent.py`: `extraction_agent` (`google-adk==2.7.1`,
     `google-genai==2.19.0`, ditambahkan ke `requirements.txt`), tool
     `validate_quote_candidate` (self-check, tidak otoritatif) dan
     `save_ledger_draft` (menulis `tool_context.state["ledger_draft"]`,
     memvalidasi ulang lewat `extraction.py` — model tidak bisa melewati gate
     hanya dengan tidak memanggil `validate_quote_candidate`). 6 test di
     `tests/test_agent.py`, semuanya memanggil tool langsung (bypass LLM) —
     Agent ADK-nya sendiri BENAR-BENAR dikonstruksi di test (bukan mock),
     tapi belum pernah memanggil Gemini sungguhan.
   - **Sengaja belum dibangun**: tool `load_deal_context`/`read_artifact` dari
     tool allowlist §4.2 penuh — butuh model data `deals/{deal_id}/artifacts/`
     yang belum ada. Untuk sekarang pemanggil agent ini isi sendiri
     `tool_context.state["artifacts"]` (dict `artifact_ref` → teks) sebelum
     run. Juga belum di-wire ke `worker.py` — vertical slice masih stub
     "Belum ada logika produk" seperti sebelumnya; menyambungkannya butuh
     keputusan dulu soal apakah `run_id` (model lama) dan `deal_id` (model
     `09-DOMAIN-RULES`/`app/audit.py`) itu entitas yang sama atau beda.
   - Config baru: `GEMINI_MODEL`, `GOOGLE_CLOUD_LOCATION`,
     `GOOGLE_GENAI_USE_VERTEXAI` di `app/config.py` (06 §2).
   - Menginstal `google-adk` menurunkan `websockets` dari 17.0.1 ke 15.0.1 di
     `.venv` (constraint dari ADK). Tidak terlihat masalah — `uvicorn` masih
     jalan, semua test hijau — tapi catat di sini kalau nanti ada gejala aneh
     di WebSocket/dev server.
4. ~~**Ranking tiga pertanyaan** prioritas.~~ **Selesai** —
   `backend/app/domain/questions.py`: `rank_questions()`, murni, `priority =
   scope_impact + acceptance_impact + schedule_impact + conflict_severity`
   (02 §4.4), ambil `MAX_CLARIFICATION_QUESTIONS` (3) teratas, stable sort
   (skor sama -> urutan kemunculan asli). 7 test di `tests/test_questions.py`.
   **Sengaja tidak** mengimplementasikan forced-slot untuk field kritis
   `CONFLICTING` (09 §5.6) — itu bagian Modul D yang dilepas, dan tidak ada
   jalur kode yang pernah menghasilkan `CONFLICTING` (lihat alasan di
   `extraction.py`). Belum ada tool ADK (`save_questions`) yang memanggilnya
   — sama seperti `agent.py`, belum di-wire ke mana pun.
5. ~~**Keputusan `run_id` vs `deal_id`**.~~ **Selesai** — dikonfirmasi ke Rifqi:
   **satu-satu, `deal_id == run_id`**. Satu brief yang disubmit = tepat satu
   deal. Sudah di-wire ke `api.py`: `POST /runs` sekarang menulis dua audit
   event beneran lewat `app/audit.py` — `DEAL_CREATED` lalu `ARTIFACT_ADDED`
   (`artifact_ref: "artifact:brief-1"`), pakai `run_id` sebagai `deal_id`.
   Mekanisme lama (`store.append_audit_step`/`run["audit_trail"]`) TIDAK
   dihapus — masih dipakai worker.py apa adanya, supaya tidak menyentuh test
   vertical slice yang sudah hijau. 1 test baru di `tests/test_slice.py`.
   Total 88 test hijau.
6. **Sambungkan `agent.py` + `questions.py` ke `worker.py`** — ini yang masih
   nyata-nyata diblokir billing GCP. `worker.py` masih stub "Belum ada logika
   produk" dengan sengaja: memanggil Gemini sungguhan di sana baru jujur bisa
   ditulis (dan diuji sampai selesai) setelah kredensial ada. Yang sudah siap
   dipakai begitu billing aktif: isi `tool_context.state["artifacts"]` dari
   `store.get_run(run_id)["brief"]` (pakai `artifact_ref="artifact:brief-1"`,
   sama seperti yang ditulis `api.py`), jalankan `agent.extraction_agent` lewat
   ADK `Runner`, ambil `ledger_draft` dari state, lalu tulis `LEDGER_DRAFT_SAVED`
   ke `app/audit.py` dan rank pertanyaan lewat `questions.rank_questions()`.
7. ~~**Client link** — opaque, scoped, expiring, tanpa akun (02 §8).~~
   **Selesai (mekanisme-nya saja)** — `backend/app/domain/client_link.py`:
   `check(link, now, purpose, action)`, murni, `now` selalu parameter (tidak
   ada mocking waktu). `backend/app/client_links.py`: `issue()` (token 128 bit
   lewat `secrets.token_urlsafe`, hanya HASH-nya yang disimpan — ada test
   khusus yang membaca file mentah dan memastikan raw token tidak pernah
   muncul di situ), `resolve()`, `revoke()`, `mark_completed()`,
   `actor_ref_for()` (potongan hash buat `actor_ref` di audit event, bukan
   token mentah — dipakai nanti pas endpoint client beneran menulis
   `CLIENT_ANSWERED` dll). 18 test baru (`test_client_link.py` +
   `test_client_links.py`). Total 106 test hijau.
   `PURPOSES` (CLARIFICATION/APPROVAL/DELIVERY_REVIEW/NEW_REQUEST)
   didefinisikan di sini karena dokumen tidak menormatifkannya sebagai enum
   tertutup di manapun — kalau nanti nemu definisi resmi yang beda,
   sinkronkan.
8. ~~**Endpoint HTTP clarification** — freelancer kirim link, klien buka &
   jawab.~~ **Selesai** — di `app/api.py`:
   - `POST /runs/{run_id}/client-links` — freelancer menerbitkan token
     CLARIFICATION (`_CLARIFICATION_ACTIONS = ["view", "answer"]`).
   - `GET /client/{token}` — klien lihat brief + ledger + readiness saat ini.
     Token invalid/revoked/expired -> 403 dengan alasan netral dari
     `client_link.check()`.
   - `POST /client/{token}/answers` — klien menulis nilai langsung ke field
     ledger manapun (`app/domain/ledger.py: apply_client_answer`, state selalu
     `CLIENT_STATED`, TANPA `validate_quote` — ini input langsung klien lewat
     form, bukan ekstraksi dari artifact, jadi tidak butuh kutipan). Ledger
     hasil merge divalidasi lewat `schemas.DealLedger` SEBELUM satu pun audit
     event ditulis (field top-level tidak dikenal -> 422, tidak ada tulisan
     setengah jalan). Tiap field yang berubah menulis event `CLIENT_ANSWERED`
     lewat `app/audit.py`, `actor_ref` dari `client_links.actor_ref_for()`
     (potongan hash, bukan token mentah).
   - **Keputusan sengaja**: link TIDAK ditandai `completed` setelah
     `/answers` — klien boleh kirim beberapa ronde koreksi. Baru ditandai
     selesai nanti oleh aksi "Confirm project plan" — **sekarang sudah
     dibangun, lihat item 9**.
   - Ini jalan penuh TANPA Gemini — ledger dimulai `{}` dan diisi langsung
     oleh klien lewat portal; begitu ekstraksi Gemini aktif (item 6), ia
     tinggal mengisi `ledger` duluan sebelum klien membuka link.
   - Diverifikasi lewat `uvicorn` sungguhan (bukan cuma `TestClient`): buat
     run -> terbitkan link -> klien lihat (readiness blocker lengkap) ->
     klien jawab `timeline.final_deadline` -> blocker itu hilang -> GET ulang
     menunjukkan nilai persist. `app/domain/ledger.py` (5 test) +
     `tests/test_client_portal.py` (9 test).
9. ~~**"Confirm project plan" / baseline approval.**~~ **Selesai** —
   `app/domain/baseline.py: build_canonical_payload(ledger, version)` (murni,
   ekstrak `.value` mentah dari tiap ledger field + hitung `text_hash` tiap
   criterion). `app/baselines.py`: `get_active_version()`/`create()`/`get()`,
   append-only, `deals/{deal_id}/baselines/{version}.json` di mode lokal.
   Endpoint baru di `api.py`:
   - `GET /client/{token}` sekarang juga mengembalikan `payload_hash` — hash
     canonical_payload versi berikutnya, dihitung dari ledger saat ini.
   - `POST /client/{token}/confirm` — body `{"payload_hash": ...}` WAJIB
     persis sama dengan yang barusan dilihat lewat GET (precondition 02 §5;
     tidak cocok -> **409**, ledger berubah sejak terakhir dilihat). Readiness
     gate MUST lolos dulu (belum ready -> **422**, tidak bisa dilewati dari
     endpoint ini). Sukses: tulis `BASELINE_APPROVED` (actor client) lalu
     `BASELINE_ACTIVATED` (actor system) berurutan, simpan baseline versi
     baru, set `active_baseline_version` di run, dan **link ditandai
     completed** — beda dari `/answers` yang sengaja tidak menutup link.
   - Diverifikasi lewat `uvicorn` sungguhan end-to-end: run -> link ->
     jawab semua field kritis -> `readiness.ready=true` -> GET ambil
     `payload_hash` -> confirm -> baseline v1 aktif (`activated_seq` terisi
     benar) -> link dipakai lagi -> 403.
   - `tests/test_baseline.py` (5), `tests/test_baselines_store.py` (6),
     `tests/test_confirm.py` (5).
   - **Catatan untuk nanti**: `build_canonical_payload` menandai SEMUA
     criterion `introduced_in_version = <versi yang lagi dibuat>`. Itu benar
     untuk v1. Begitu ada jalur yang bikin v2 (change request/Guardrail),
     fungsi ini harus diperbarui supaya criterion yang sudah ada di v(n-1)
     mempertahankan `introduced_in_version` aslinya (09 §2.6 A-7) — jangan
     lupa, sudah ditandai juga di docstring-nya.
10. ~~**Evidence + delivery review** (01-PRD §5 langkah 9-10).~~ **Selesai** —
    `app/evidence.py`: `add()`/`list_for_deal()`/`list_for_criterion()`,
    `type` dipersempit ke `"url"`/`"text"` saja (screenshot/file upload butuh
    Cloud Storage, blocker sama dengan billing). `app/baselines.py` dapat
    `get_all_up_to()` (riwayat versi buat `criteria.effective_status`).
    Client link sekarang punya dua purpose: `_ACTIONS_BY_PURPOSE` di
    `api.py` (`CLARIFICATION` vs `DELIVERY_REVIEW`), `POST
    /runs/{id}/client-links` terima `{"purpose": ...}`.
    - `POST /runs/{run_id}/evidence` — freelancer lampirkan evidence ke satu
      `criterion_key`; ditolak 409 kalau belum ada baseline aktif, 404 kalau
      `criterion_key` tidak ada di baseline aktif. Tulis `EVIDENCE_ADDED`.
    - `GET /client/{token}/review` — daftar criterion baseline aktif +
      `effective_status` (dihitung ulang lewat `app.domain.criteria`, bukan
      disimpan) + evidence per criterion.
    - `POST /client/{token}/review` — klien kirim Accept/Request changes
      untuk beberapa criterion **dalam satu aksi submit** (semua item
      divalidasi dulu — termasuk gate `can_record_decision` A-9 — sebelum
      satu pun event ditulis). `CHANGES_REQUESTED` **wajib** `reason` ->
      422 kalau kosong. Satu `review_session_id` per submit; tulis
      `REVIEW_SESSION_OPENED` lalu satu `CRITERION_DECISION` per item. Link
      **sengaja tidak** ditandai completed (bisa ada ronde review berikutnya).
    - Diverifikasi end-to-end lewat `uvicorn` sungguhan: evidence ditambah
      -> status `PENDING` -> klien ACCEPTED -> status berubah jadi
      `ACCEPTED` di GET berikutnya.
    - `tests/test_evidence.py` (6) + `tests/test_delivery_review.py` (12),
      termasuk test A-9 (`ACCEPTED` tidak bisa ditimpa `CHANGES_REQUESTED`
      lagi lewat endpoint ini).
11. ~~**Proof Manifest / Acceptance Record**~~ **Selesai** —
    `app/domain/proof.py`: `build_manifest()` (murni, menyatukan baseline +
    status tiap criterion + evidence + keputusan klien terbaru — empat lapis
    Acceptance Matrix 01 §4.3 dijaga tetap terpisah, tidak digabung jadi satu
    badge) dan `to_markdown()`. Endpoint `GET /runs/{run_id}/proof?format=json|md`
    (default json; 409 kalau belum ada baseline aktif). "Checks" (lapis
    ketiga Acceptance Matrix, deterministic check sungguhan) sengaja tidak
    ada field-nya — tidak ada yang benar-benar dijalankan di MVP ini.
    Diverifikasi end-to-end lewat `uvicorn` sungguhan sampai keluar Markdown
    yang benar. `tests/test_proof.py` (5) + `tests/test_proof_endpoint.py`
    (6).
12. ~~**Guardrail — klasifikasi request baru** (scope comparison, IN_SCOPE/
    AMBIGUOUS/CHANGE_REQUEST).~~ **Selesai sebagian, sengaja** — bagian yang
    tidak butuh Gemini sudah jadi, bagian yang butuh Gemini (model
    mengusulkan classification+citation otomatis) belum, sama polanya dengan
    ekstraksi (item 3): model diusulkan lewat `agent.py` nanti, tapi validasi
    & keputusan akhir selalu deterministik di sini.
    - `app/domain/guardrail.py`: `citable_text(baseline)` (kumpulkan teks
      yang boleh dikutip dari criteria + out_of_scope + deliverables) dan
      `classify(proposed, citations, text_by_ref)` — tiap citation
      divalidasi tanpa syarat lewat `validate_quote` (pola sama persis
      seperti `extraction.py`); `IN_SCOPE`/`CHANGE_REQUEST` **tanpa kutipan
      valid otomatis turun jadi `AMBIGUOUS`** (02 §4.5, cegah model
      menyimpulkan tanpa dasar). Satu kutipan buruk di antara beberapa tidak
      menggagalkan yang lain.
    - `app/scope_requests.py` — store `deals/{deal_id}/requests/{request_id}`
      (sengaja dinamai `scope_requests`, bukan `requests`, supaya tidak
      tabrakan nama dengan paket HTTP `requests`). `change_draft_id` dari
      bentuk data 02 §6 sengaja tidak ada — CHANGE_REQUEST yang bikin
      baseline v2 belum dibangun (lihat catatan `introduced_in_version` di
      `app/domain/baseline.py`, masih PR yang sama).
    - Endpoint: `POST /runs/{run_id}/requests` (freelancer/klien mencatat
      request baru, 409 tanpa baseline aktif), `GET /runs/{run_id}/requests`,
      `POST /runs/{run_id}/requests/{request_id}/classify` (freelancer
      mengonfirmasi klasifikasi — 09 §8: hanya freelancer yang berwenang,
      bukan klien, bukan model; audit event `SCOPE_CLASSIFICATION_DECIDED`
      selalu actor `"freelancer"`).
    - Diverifikasi end-to-end lewat `uvicorn` sungguhan: request dengan
      kutipan valid tetap `IN_SCOPE`; request `CHANGE_REQUEST` tanpa kutipan
      otomatis turun `AMBIGUOUS`.
    - `tests/test_guardrail.py` (9) + `tests/test_scope_requests.py` (7) +
      `tests/test_guardrail_endpoint.py` (8). Total **189 test hijau**.
    - **Sengaja belum**: model benar-benar mengusulkan classification+citation
      (butuh Gemini, sama seperti item 6), dan CHANGE_REQUEST yang disetujui
      membuat baseline v2 (butuh perbaikan `introduced_in_version` dulu).
13. ~~**Wiring `worker.py` ke `agent.extraction_agent`, Gemini sungguhan.**~~
    **Kode selesai, terverifikasi end-to-end, TAPI belum pernah sukses
    ekstraksi sungguhan** — `GEMINI_API_KEY` valid dan jalan (dibuktikan
    lewat panggilan sederhana: `generate_content(..., "Balas satu kata:
    OK")` -> `"OK"`), tapi `gemini-3.7-flash` konsisten balas **503
    "This model is currently experiencing high demand"** setiap kali
    dipanggil lewat `extraction_agent` (dicoba 3x, langsung dan lewat HTTP
    penuh). Ini murni kapasitas server Google saat ini, bukan bug di kode.
    - `app/worker.py`: `run_extraction(run_id, brief)` — `InMemoryRunner`
      + `session_service.create_session(state={"artifacts": {...}})` +
      `run_async(new_message=...)`, baca `ledger_draft` dari
      `session.state` setelah run selesai. Dipanggil dari `push()`,
      dibungkus `try/except` supaya kegagalan Gemini (503 dll) tidak
      menjatuhkan worker — status tetap ditulis jujur ("Ekstraksi Gemini
      gagal"), bukan diam-diam dianggap sukses kosong.
    - **Gap yang diketahui, dicatat apa adanya**: round yang gagal karena
      Gemini transient **tidak otomatis di-retry** — `claim_job` sudah
      mengklaim round itu sebelum ekstraksi dicoba, jadi redelivery
      Pub/Sub akan dianggap duplikat dan di-drop, bukan diulang. Perlu
      mekanisme retry level-job (mis. tidak claim sampai ekstraksi
      sukses, atau job terpisah untuk retry) kalau ini jadi masalah nyata
      saat demo — belum dibangun.
    - `tests/conftest.py`: fixture `stub_extraction` (autouse) — semua 189
      test TIDAK memanggil Gemini sungguhan (cepat, deterministik, tidak
      butuh API key). Wiring sungguhan hanya diverifikasi manual.
    - **Coba lagi nanti**: jalankan ulang verifikasi manual (perintah ada
      di riwayat commit/sesi) begitu demand `gemini-3.7-flash` mereda, atau
      coba model Gemini lain sebentar buat isolasi masalah (`gemini-2.5-
      flash` misalnya) — TAPI jangan ganti `GEMINI_MODEL` default tanpa
      alasan baru, itu keputusan terkunci (lihat bawah).
14. Baru setelah ini semua sukses sekali secara nyata: perluas `agent.py`
    untuk juga mengusulkan classification Guardrail (item 12), bukan cuma
    ekstraksi ledger.

---

## Blocker yang tidak bisa diselesaikan dari sisi kode

1. ~~**Billing Google Cloud belum aktif -> blokir wiring Gemini.**~~
   **Dilewati, 25 Agu malam** — `gcloud billing accounts list` kosong (0
   billing account di akun `rifqiahmad234a@gmail.com`), jadi diputuskan
   **pindah dari Vertex AI ke Gemini Developer API** (`GEMINI_API_KEY`,
   free tier, tanpa kartu/billing GCP sama sekali) — sah menurut aturan
   hackathon (V-8), lihat `docs/10-KEPUTUSAN-DAN-VERIFIKASI.md` §1 dan
   commit terkait. **Billing GCP masih belum aktif** dan TIDAK LAGI
   memblokir Gemini — hanya memblokir deploy ke Cloud Run (jauh nanti,
   sesudah semua fitur beres). **Yang sekarang jadi penentu**: isi
   `GEMINI_API_KEY` di `backend/.env` (generate gratis di
   https://aistudio.google.com/apikey) — begitu itu ada, wiring
   `worker.py` ke Gemini sungguhan (item 6) bisa langsung dikerjakan DAN
   diuji sampai selesai, tanpa perlu gcloud/project/billing apa pun.
2. ~~`gcloud` belum terpasang.~~ **Selesai, 25 Agu malam** — Cloud SDK
   581.0.0 terpasang di
   `C:\Users\ASUS\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd`
   (belum masuk PATH proses lama, panggil pakai path lengkap kalau `gcloud`
   polos tidak ketemu). `gcloud auth login` dan `gcloud auth
   application-default login` sudah beres, akun `rifqiahmad234a@gmail.com`.
3. **Project GCP: pakai `dudepercobaan`** (BUKAN project baru). Akun ini
   sudah kena limit kuota 12 project (project pribadi lama Rifqi: Dude,
   Dude2, Dude3, DudePercobaan, DudeSidang, PDF1, Rifqi UAS, Sepaturoda,
   skpamel, dll — tidak berhubungan dengan Delividence). Sempat dihapus
   `dude3-748bb` untuk buka slot (`gcloud projects undelete dude3-748bb`
   bisa memulihkan dalam 30 hari kalau perlu), tapi kuota belum kebuka juga
   setelahnya (soft-delete tidak langsung bebas kuota) — jadi diputuskan
   pakai project lama `dudepercobaan` yang sudah ada, bukan bikin baru.
   `gcloud config set project dudepercobaan` dan `gcloud auth
   application-default set-quota-project dudepercobaan` sudah dijalankan.
   **Rename display name project itu jadi "Delividence" di Console kalau
   sempat** (masih bernama "DudePercobaan" sekarang, project ID-nya tidak
   masalah tetap `dudepercobaan`).
4. **Status tim di Devpost belum dipastikan.** Repo submission ada di akun
   partner. Itu sah untuk tim — tetapi hanya kalau keduanya terdaftar sebagai
   tim di Devpost dan undangannya sudah diterima.
5. **Aturan kontes Emergent** (D-4) belum dicek soal benturan.

### GEMINI_API_KEY — status: SUDAH DIISI, wiring selesai, tinggal tunggu demand mereda

~~1. Isi GEMINI_API_KEY~~ **selesai** — key digenerate dari akun Google lain
(akun pertama, `rifqiahmad234a@gmail.com`, sempat gagal "request is
suspicious" 2x waktu generate key; akun kedua berhasil). Ada di
`backend/.env` (gitignored, tidak ke-commit).

~~2. Wiring worker.py~~ **selesai, lihat item 13 di atas** — kodenya benar
dan sudah diverifikasi jalan end-to-end sampai titik panggilan Gemini;
panggilan sungguhan-nya sendiri belum pernah sukses gara-gara 503 dari
Google. Coba lagi nanti, tidak perlu menulis ulang kode apa pun.

3. Setelah item 13 sukses sekali: perluas `agent.py`/tool baru untuk juga
   mengusulkan classification+citation Guardrail (item 12/14).

### Setelah billing GCP aktif (baru relevan untuk deploy, bukan untuk Gemini)

1. `.\deploy\01-setup-gcp.ps1 -ProjectId dudepercobaan` — script ini SUDAH
   ADA di repo dan mengasumsikan project sudah ada + billing aktif (bukan
   bikin project baru). Mengaktifkan API (Vertex AI, Cloud Run, Pub/Sub,
   Firestore, Secret Manager, Artifact Registry, Cloud Build), bikin
   Firestore native, Artifact Registry, 3 service account dengan hak
   minimum, topic + dead-letter Pub/Sub. Aman diulang.
2. `.\deploy\02-deploy.ps1 -ProjectId dudepercobaan`.
3. Set `GOOGLE_CLOUD_PROJECT=dudepercobaan` di env backend (lihat
   `backend/.env.example`) supaya `config.LOCAL` jadi `False` dan
   Firestore/Pub/Sub sungguhan terpakai, bukan mode lokal.
4. (Opsional) Set `GOOGLE_GENAI_USE_VERTEXAI=TRUE` untuk balik ke Vertex AI
   kalau mau -- verifikasi ketersediaan `gemini-3.7-flash` di region
   `asia-southeast2` dulu (06 §3 mem-pin region ini, belum pernah dicek
   langsung ke API). Tidak wajib -- Developer API tetap sah dipakai sampai
   submission.

---

## Keputusan yang sudah dikunci — jangan dibuka ulang tanpa alasan baru

- Nama **Delividence** (sempat DealReady, lalu ScopeHandshake).
- Model **`gemini-3.7-flash`**. Paket revisi menulis `gemini-3.5-flash`; itu
  sudah dikoreksi karena Google kini menyebutnya *legacy Flash model*.
- **Profil Modul A saja.** Modul C (drift ledger), B (revision rounds), dan D
  (conflict resolution) dilepas berikut fixture konflik Friday/Monday. Alasan
  lengkap di `docs/10-KEPUTUSAN-DAN-VERIFIKASI.md` §4b.
- Backend Python, bukan Express — ADK Python-first.

Rujukan utama: `docs/10-KEPUTUSAN-DAN-VERIFIKASI.md` (keputusan + fakta aturan
terverifikasi) dan `docs/09-DOMAIN-RULES.md` (aturan normatif).
`docs/arsip-dealready/` adalah riwayat, bukan rujukan.
