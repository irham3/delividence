# 03 — Build Breakdown dan Cut Line

## 1. Estimasi keseluruhan

| Skenario | Waktu | Asumsi |
|---|---:|---|
| Optimistis | 38–42 jam | kontrak domain benar sejak awal, banyak test dihasilkan dari vector normatif |
| Expected | **46–50 jam** | satu putaran debugging auth/Pub/Sub dan integrasi empat modul domain |
| Pesimistis | 60–70 jam | schema/hash/seq perlu rework atau cloud/model integration bermasalah |

Confidence: **medium-low** karena belum ada codebase, integrasi client portal → Pub/Sub → ADK belum diuji, dan `09-DOMAIN-RULES.md` menambah 45 test serta empat modul korektness. Estimasi 33–35 jam sebelumnya tidak lagi berlaku.

## 2. Breakdown expected

| # | Unit | Output yang dapat diverifikasi | Estimasi |
|---:|---|---|---:|
| 1 | Foundation + first Cloud Run deploy | web/API/worker skeleton, CI/manual deploy, health endpoint | 3.5 jam |
| 2a | Serial core: contracts + Module A | §10 schema/hash/normalization/seq/enum + criterion version semantics | 5.5 jam |
| 2b | Detachable domain modules | Modul D, B, C sebagai unit terpisah dengan test masing-masing | 4.5 jam |
| 3 | ADK brief analysis | text/image → structured ledger, provenance, three questions | 5 jam |
| 4 | Client portal + event resume | answer/edit/approve UI, Pub/Sub job, idempotent worker | 4.5 jam |
| 5 | Baseline integrity | readiness, append-only snapshot, canonical hash, audit | 3 jam |
| 6 | Guardrail/change request | request analysis, citation, drift, human decision, version diff | 5 jam |
| 7 | Proof/acceptance | evidence mapping, criterion versioning, revision sessions, manifest | 5 jam |
| 8 | Memory + hardening | confirmed preference, injection/capability tests, scoped access | 3 jam |
| 9 | Test, polish, README, diagram, video, Devpost | 45-test matrix, reliable demo, complete submission | 7 jam |
|  | **Expected total** |  | **46 jam** |

## 3. Work packages

### WP-1 — Foundation

- Monorepo: `apps/web`, `services/api`, `services/worker`, dan wajib satu `shared/schemas` sebagai source of truth yang menghasilkan validator/model untuk service pemakai.
- Dockerfile terpisah untuk web, API, worker.
- Cloud Run service account minimum dan env configuration.
- `/healthz` untuk tiap service.
- Deploy dummy event ke Pub/Sub pada hari pertama.

**Done:** browser membuka hosted web, API merespons, dan private worker memproses satu test event di Cloud Logging.

### WP-2a — Serial core: kontrak dan Modul A

- Bekukan `shared/schemas/`, enum, state transitions, canonical JSON/hash, criterion text normalization, quote validation, dan audit `seq` sebelum feature work paralel.
- Implementasikan Firestore event/snapshot foundation, satu state-transition service sebagai satu-satunya write path status domain, dan Modul A criterion versioning.
- Satu pemilik; harus mendarat dan lulus golden vectors sebelum WP-2b/feature work bergabung.

**Done:** shared contracts beku; golden hash/normalization/seq dan seluruh test Modul A lulus.

### WP-2b — Detachable modules

- Modul D conflict resolution terpisah dan terikat pada fixture konflik.
- Modul B revision rounds terpisah.
- Modul C drift ledger sebagai read-side aggregate terpisah.
- Masing-masing punya package/test boundary sendiri sehingga C, lalu B, lalu D+fixture dapat dilepas tanpa menyunting Modul A.

**Done:** test D/B/C lulus secara independen dan integration events memakai kontrak WP-2a.

### WP-3 — Handshake agent

- Ingest text dan satu image.
- Gemini structured output schema.
- Deal Ledger fields/state/source references.
- Ambiguity/conflict detection dan maximum-three question ranking.
- Deterministic readiness.

**Done:** golden fixture menghasilkan field bersumber; nilai yang disimpulkan tidak menjadi `CLIENT_STATED`.

### WP-4 — Client collaboration

- Firebase Auth verification untuk owner.
- Opaque client token hash, purpose, expiry, revoke/completion; cross-owner, expired, dan wrong-purpose tests.
- Freelancer membuat client link.
- Client menjawab/edit field dan approve baseline.
- API publish event; worker resume dan UI owner melihat update.
- Approved baseline v1 tidak pernah di-update; versi baru disimpan terpisah.
- Approval terhadap draft/baseline yang stale (version atau canonical hash tidak lagi cocok) mengembalikan `409` dan tidak menulis approval maupun activation event.

**Done:** alur dapat dijalankan di hosted environment tanpa copy-paste respons; test cross-owner, expired token, wrong-purpose token, dan stale approval lulus.

### WP-5 — Guardrail

- Klien mengirim request melalui portal atau owner mencatat request dari kanal lain.
- Agent menghasilkan classification proposal + cited baseline.
- Owner confirm/override.
- Change request draft menyimpan diff/impact; approval menghasilkan baseline baru.
- Drift ledger menghitung request yang telah diputuskan sejak baseline aktif.

**Done:** contoh TikTok format terklasifikasi dengan citation; v1 tetap dapat dilihat setelah v2.

### WP-6 — Proof

- Evidence item berupa URL, text result, atau satu image upload.
- Mapping evidence ke criterion.
- Client Accept/Request changes dengan alasan.
- Request changes di luar criterion membuat scope-review proposal; tidak mengubah baseline/revision count otomatis.
- Freelancer mengonfirmasi satu rework session untuk mengonsumsi tepat satu revision round; status criterion mengikuti version/hash rules.
- Proof Manifest page + Markdown/JSON export.

**Done:** satu criterion memiliki evidence dan client acceptance yang menunjuk baseline version.

### WP-7 — Memory, audit, observability

- Preference candidate → explicit owner confirmation → reuse pada second deal.
- User-facing audit events dan cloud structured logs.
- Prompt injection fixture dan malformed model output fallback.

**Done:** demo deal kedua menunjukkan memory tanpa mengubahnya menjadi client fact.

### WP-8 — Submission

- English UI/copy pass.
- Seed/demo reset command atau deterministic demo account.
- Architecture diagram, spin-up README, screenshots.
- Public video ≤4 menit dan Devpost form.
- Verify permissions, hosted URL, repository access, disclosure.

## 4. Golden-path fixture

Gunakan fixture normatif Seed + 11 langkah di `09-DOMAIN-RULES.md` §9. Fixture itu sengaja memuat konflik “Friday” versus “Monday” dan membuktikan preservation serta supersession acceptance secara end-to-end.

## 5. Cut line

PDF input/export, email delivery, visual side-by-side diff, dan evidence adapter tambahan sudah berada di SHOULD/WON'T; semuanya bukan slack dari MUST dan tidak dihitung sebagai cut.

Pemotongan nyata pertama:

1. Batasi satu active change request dan satu active client link per purpose.
2. Bahasa Indonesia menjadi input-only; semua UI/demo tetap English.
3. Jika masih perlu turun, gunakan degradasi modul berbasis dependensi di bawah.

Tidak boleh dipotong pada profile yang masih mengklaim fiturnya:

- Modul A serta invariant/test normatif untuk setiap modul yang diaktifkan;
- client portal tanpa akun;
- Pub/Sub resume;
- provenance states;
- deterministic readiness;
- approved baseline yang tidak ditimpa dan hash;
- cited scope comparison;
- evidence-to-criterion acceptance;
- deployment dan cloud proof.

### Degradasi berbasis dependensi

Setelah item non-core di atas dipotong, gunakan urutan ini—bukan menghapus invariant secara acak:

1. Lepas Modul C terlebih dahulu; sembunyikan drift panel dan hapus beat drift dari video.
2. Lepas Modul B; sembunyikan revision counter dan exhausted-round routing.
3. Lepas Modul D hanya bersama fixture konflik Friday/Monday dan beat video konflik. Mempertahankan fixture tanpa D membuat golden path deadlock.
4. Modul A tidak pernah dilepas selama baseline berversi.

Setiap downgrade harus dicatat di known limitations dan semua claim/test/video terkait harus ikut dihapus.

Jika sampai 29 Agustus sore Handshake belum end-to-end di cloud, hilangkan Guardrail UI khusus dan lakukan new request melalui halaman deal yang sama. Jika sampai 30 Agustus siang Proof belum stabil, pertahankan satu evidence URL per criterion dan client acceptance; jangan membangun upload tambahan.
