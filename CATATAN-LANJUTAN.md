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
| Test | **220 hijau** (`cd backend; ..\.venv\Scripts\python.exe -m pytest -q`) |
| Production | **LIVE** — lihat milestone 27 Agu di bawah untuk URL & detail |

## MILESTONE 30 Agu (lanjutan) — audit produksi ulang sebelum rekaman: 1 bug 404 + 3 perbaikan, SEMUA MASIH LOKAL

**Status: kode sudah diperbaiki & hijau di lokal, TAPI BELUM di-commit dan BELUM di-deploy.**
Produksi saat ini masih memuat bug 404 di bawah.

### Kenapa audit ini dijalankan

Rifqi minta cek ulang total sebelum bikin video ("kalau ada error seperti tadi
sama saja"). Dijalankan tiga lapis: test suite, produksi lewat Chrome, dan
kode.

### Yang terbukti SEHAT di produksi (run baru dari nol, `4614384828ff4458b014c6a21e0fd262`)

Satu run penuh dijalankan di `delividence.vercel.app`, dari brief sampai proof:

| Langkah | Hasil |
|---|---|
| Ekstraksi Gemini | 5 field ledger, semua `CLIENT_STATED · artifact:brief-1` |
| Clarification link | Form klien terisi dari hasil ekstraksi (d1, english-subtitles, logo-placement, assumption raw footage) |
| Confirm plan | "Baseline version 1 is now active" |
| Guardrail | Klien minta versi TikTok 15 detik → Gemini usul **CHANGE_REQUEST** + kutipan verbatim `deliverables[0]` → freelancer konfirmasi |
| Evidence | 2 kriteria terlampir |
| Delivery review | Klien accept keduanya → ACCEPTED |
| Proof | View JSON menghasilkan blob (fetch ber-token sukses) |

Nol console error, semua request 200. Backend 227 test hijau (sebelum
perubahan), `tsc` + eslint bersih.

### BUG 1 (nyata, diperbaiki) — semua baris di halaman Records → 404

Href baris di `/records` adalah `/records/{id}/records`, padahal section yang
sah cuma `sources | questions | baseline | evidence | activity | requests`
(`app/records/[runId]/[section]/page.tsx`). Jadi **setiap klik "Open" dari
halaman Records berakhir 404** — menu pertama di sidebar, paling mungkin
diklik juri duluan. Sources/Review/Activity selamat karena namanya kebetulan
cocok (Review di-remap ke `evidence`). TypeScript tidak menangkapnya karena
URL dirakit sebagai template string.

Perbaikan (bukan tambal sulam): **satu sumber kebenaran** di
`web/src/lib/record-href.ts` — `DETAIL_SECTIONS`, `isDetailSection()`,
`recordHref()` — dipakai DUA-DUANYA: route `[section]/page.tsx` untuk
validasi, dan `owner-routes.tsx` untuk merakit URL. Dulu terpisah, itu
sebabnya bisa melenceng diam-diam.

Diverifikasi di server sungguhan (`pnpm build` + `pnpm start -p 3111`), bukan
cuma unit test:

```
/records/{id}           -> 200   (tujuan baru)
/records/{id}/records   -> 404   (tujuan lama yang rusak)
/records/{id}/sources   -> 200
/records/{id}/evidence  -> 200
/records/{id}/activity  -> 200
/records/{id}/bogus     -> 404   (penjaga section masih utuh)
```

### PERBAIKAN 2 — pesan aktivitas worker jadi Inggris

`backend/app/worker.py:133,148,150` menulis detail audit berbahasa Indonesia
("Brief diekstrak lewat Gemini -- 5 field ledger terisi.") padahal produknya
English-first, dan kalimat itu tampil di kartu "Latest activity" di workspace
— akan terlihat di video. Ketiganya diganti ke Inggris. Satu test MEMANG mengunci
teks lama (`test_slice.py::test_worker_menandai_failed_saat_model_gagal`
meng-assert substring "gagal") -- assert-nya disesuaikan jadi "failed",
maksud test-nya tidak berubah (status kegagalan harus jujur, bukan "done").

**Konsekuensi: butuh redeploy backend Cloud Run** (`deploy/02-deploy.ps1`)
supaya berlaku di produksi.

### PERBAIKAN 3 — tab "Changes" akhirnya menampilkan usulan Guardrail

Sebelumnya tab Changes cuma menulis "Awaiting freelancer classification";
usulan model + kutipan hanya ada di workspace. Jadi fitur Guardrail tidak
terlihat dari halaman yang justru bernama Changes. Sekarang komponen baru
`RequestRow` menampilkan "Model suggested: X · awaiting freelancer
confirmation" atau "Classification: X · confirmed by the freelancer",
lengkap dengan daftar kutipan verbatim.

### PERBAIKAN 4 — empat halaman daftar tidak lagi kembar

Records/Sources/Review/Activity memakai komponen yang sama (`OwnerIndex`,
endpoint `/runs` yang sama), jadi tabelnya identik — Rifqi yang menyadari ini.
Sekarang kolom ketiga menjawab pertanyaan khas tiap halaman, semuanya dari
read model `/runs` yang sudah ada (tanpa endpoint baru):

| Halaman | Header kolom | Isi |
|---|---|---|
| Records | Baseline | `v2` / `Draft` |
| Sources | Extracted | `5 fields` / `Nothing yet` |
| Review | Criteria | `2 criteria` / `None yet` |
| Activity | Last update | `Just now` / `30m ago` / `1d ago` |

Logikanya murni di `web/src/lib/record-columns.ts` supaya bisa diuji tanpa
render React (pola yang sama dengan `ledger-summary.ts`).

### Status test setelah semua perubahan

- Frontend unit test: **9 → 19 hijau** (`record-href.test.ts` 5 baru,
  `record-columns.test.ts` 5 baru), `tsc --noEmit` bersih, eslint bersih,
  `next build` sukses.
- Backend: **227 hijau** setelah perubahan worker.py + penyesuaian assert.

### YANG BELUM DIKERJAKAN — lanjutkan dari sini

1. Commit semua perubahan di atas (TANPA trailer Co-Authored-By/Claude-Session).
2. Push ke branch `rifqi`, lalu **sync manual ke repo clone Vercel**
   `rifqiahmadpratama/delividence` — tanpa langkah ini frontend TIDAK berubah
   di produksi (lihat milestone 29 Agu).
3. Redeploy backend Cloud Run untuk perubahan `worker.py`.
4. Verifikasi ulang di produksi: klik baris di halaman Records (harus buka
   record, bukan 404), cek keempat halaman daftar sudah beda kolom, cek
   pesan aktivitas sudah Inggris.
5. Baru mulai capture video (Remotion + TTS Gemini, lihat milestone di atas).

### Lanjutan — lokal ikut diverifikasi & didokumentasikan (commit `dd7604e`)

Rifqi mengingatkan partner memakai lokal, jadi jalur lokal ikut dijalankan
sungguhan, bukan diasumsikan.

**Dua penyebab lokal patah untuk clone baru, keduanya diperbaiki:**

1. `web/.env.example` **tidak pernah ada di repo**. `.gitignore` bawaan
   Next.js di `web/` berisi `.env*` dan itu mengalahkan `!.env.example` di
   root. Siapa pun yang mengikuti README mencari file yang tidak ada, jalan
   tanpa `NEXT_PUBLIC_FIREBASE_*`, lalu kena `Firebase is not configured`
   persis seperti Rifqi pagi ini. Ditambahkan `!.env.example` + file
   contohnya (placeholder kosong).
2. `docs/06-SETUP.md` §3 masih menjelaskan struktur yang tidak pernah ada di
   repo ini (`apps/web`, `services/api`, `services/worker`, port 8081/8082,
   `npm`, `.env.local`). Ditulis ulang sesuai kenyataan, dan **setiap
   perintahnya dijalankan dulu sebelum ditulis**. README dapat resep tiga
   terminal yang sama.

**Cara menjalankan lokal (terverifikasi 30 Agu):**

| Terminal | Perintah | Port |
|---|---|---|
| API | `..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8080 --env-file .env` (dari `backend/`) | 8080 |
| Worker | `$env:ROLE = "worker"` lalu perintah yang sama dengan `--port 8081` | 8081 |
| Web | `pnpm dev` (dari `web/`) | 3000 |

Temuan kecil yang berguna: **`ROLE` dari environment menang atas isi
`--env-file`** (uvicorn memanggil `load_dotenv` tanpa override), jadi worker
tidak butuh file env kedua. Diuji langsung: instance dengan `ROLE=worker`
menjawab `POST /pubsub/push` 204 dan `GET /runs` 404 — app worker, bukan api.

Mode lokal dipilih dengan **mengosongkan `GOOGLE_CLOUD_PROJECT`** di
`backend/.env` (antrean HTTP langsung ke worker, state ke
`backend/.localdata/`). Owner login tetap butuh `gcloud auth
application-default login` walau mode lokal, karena `app/auth.py` memverifikasi
ID token lewat `firebase_admin` + ADC — ini yang paling gampang bikin mesin
baru mentok tanpa pesan yang jelas.

**Hasil smoke test lokal:**

```
api  GET /runs (tanpa token)  -> 401 {"detail":"Missing or malformed Authorization header"}  (sehat)
web  /  /register  /sign-in  /workspace  /records            -> 200
web  /records/{id}            -> 200      (fix 404 ikut terbukti di lokal)
web  /records/{id}/records    -> 404
```

`/register` dibuka di Chrome: render bersih, **tombol "Sign up with Google"
diklik dan TIDAK lagi melempar `Firebase is not configured`** (popup-nya saja
yang diblokir sandbox otomasi — bukan bug aplikasi). Nol console error.

### DUA PERINTAH YANG MASIH HARUS DIJALANKAN RIFQI SENDIRI

Keduanya diblokir classifier auto-mode, jadi Claude tidak bisa menjalankannya:

```
gh pr merge 4 --repo irham3/delividence --merge
gh workflow run "Sync deployment mirror" --repo rifqiahmadpratama/delividence
```

```
.\deploy\02-deploy.ps1 -ProjectId gen-lang-client-0104798459 -FrontendOrigin https://delividence.vercel.app -FirebaseProjectId gen-lang-client-0104798459 -ModelRuntime developer -GeminiModel gemini-3.6-flash
```

`-GeminiModel gemini-3.6-flash` WAJIB: default skripnya `gemini-3.5-flash`,
sedangkan revisi yang sekarang live memakai 3.6 (sudah dicek langsung ke
Cloud Run). Tanpa flag itu redeploy diam-diam menurunkan model.

**PENTING soal mirror:** `sync-deployment-mirror.yml` menarik dari `main`
repo partner tiap 15 menit dan menimpa isi mirror. Jadi push langsung ke repo
clone Vercel (cara 29 Agu) sekarang JUSTRU akan ditimpa balik selama `main`
belum berisi fix-nya. Jalur yang benar: merge PR ke `main` dulu, mirror
menyusul sendiri.

### Temuan kecil yang SENGAJA dibiarkan

- Field "Final deadline" di form klien tampil kosong padahal ledger punya
  `final deadline: next Wednesday` — inputnya `type="date"`, tidak bisa
  menampung frasa. Bukan crash; nilai aslinya tetap terlihat di tab Sources.
- `web/.gitignore` (`.env*`) masih menutupi `web/.env.example` sehingga file
  itu tidak ada di repo (lihat milestone sebelumnya, fix satu baris).

---

## MILESTONE 30 Agu — sesi siap-rekam: env lokal diperbaiki, rekaman lama dibuang, jalur produksi video dikunci

**Status sesi ini: berhenti di titik "siap mulai capture". Tinggal bilang "lanjutkan".**

### 1. Error `Firebase is not configured` di lokal — SELESAI

Gejala: buka `/register` (atau klik Sign in) di `pnpm dev` lokal → Runtime Error
`Firebase is not configured: apiKey, authDomain, projectId, storageBucket,
messagingSenderId, appId` dari `web/src/lib/firebase.ts:24`.

Akar masalah: `web/.env` lokal isinya **cuma** `NEXT_PUBLIC_API_URL`. Enam
variabel `NEXT_PUBLIC_FIREBASE_*` tidak pernah ada di situ (nilai yang pernah
diisi kemungkinan masuk ke dashboard Vercel, bukan ke file lokal) — makanya
produksi sehat tapi lokal patah.

Fix: config web Firebase diambil langsung dari Firebase Management API pakai
access token gcloud (bukan diketik manual), lalu ditulis ke `web/.env`:

```
GET https://firebase.googleapis.com/v1beta1/projects/gen-lang-client-0104798459/webApps/1:798836649371:web:97acf8c2adbed64475853e/config
```

`web/.env.example` juga diisi placeholder kosong + komentar cara mengambil
config-nya. Tidak ada satu baris kode pun yang diubah, tidak ada commit.

> **Ingat:** Next.js membaca `NEXT_PUBLIC_*` saat proses start. Setelah ini
> `pnpm dev` WAJIB direstart, jangan cuma reload browser. Backend lokal juga
> mati saat sesi ini (port 3000 & 8080 kosong) — nyalakan dengan
> `uvicorn --env-file .env` kalau mau uji lokal penuh.

### 2. TEMUAN BELUM DIPERBAIKI — `web/.env.example` tidak pernah masuk repo

`web/.gitignore` baris 36 berisi `.env*` (bawaan Next.js) dan itu
**mengalahkan** `!.env.example` di `.gitignore` root. `git ls-files` hanya
menemukan `backend/.env.example`. Artinya juri yang clone repo lalu mengikuti
README ("copy `web/.env.example` …") akan mencari file yang tidak ada dan kena
error Firebase yang sama persis seperti di atas.

Nyambung ke dua item checklist yang masih kosong: "spin-up instructions diuji
di environment bersih" dan "environment variable table with placeholders only".

**Fix satu baris (belum dikerjakan, menunggu aba-aba):** tambah
`!.env.example` di `web/.gitignore`, lalu commit `web/.env.example`.

### 3. Tiga rekaman lama di `video/` DIHAPUS

Dibuang ke Recycle Bin (masih bisa dipulihkan beberapa hari):
`2026-08-28 17-51-27.mp4` (2:43), `17-59-29.mp4` (3:52), `22-55-52.mp4` (4:18).

Alasan — ketiganya capture layar penuh, bukan footage produk: panel kanan berisi
terminal Claude Code (instruksi "Klik Create clarification link" terbaca jelas),
browser cuma separuh layar ±960 px, ada tab YouTube terbuka, dan audio di
rekaman 4:18 itu suara video YouTube (dua lainnya senyap total, −91 dB).

### 4. Keputusan produksi video (dikunci sesi ini)

| Aspek | Keputusan |
|---|---|
| Tool | **Remotion** (React → MP4, lokal, gratis, tanpa akun) — BUKAN HeyGen Hyperframes: presenter AI tidak membuktikan "agent bekerja + backend Google Cloud", dan butuh upload materi ke pihak ketiga |
| Visual | **Claude yang menjalankan alur produksi asli** di `delividence.vercel.app`, tangkap frame bersih tiap langkah, lalu Remotion yang menganimasikan (zoom/highlight/caption). Tidak butuh Rifqi merekam OBS |
| Audio | **TTS Gemini** narasi Inggris, pakai `GEMINI_API_KEY` yang sudah ada di `backend/.env` |
| Durasi target | ±3:30, batas keras < 4:00 |

Verifikasi ketersediaan TTS sudah dilakukan (key valid, 53 model terlihat):
- `gemini-3.1-flash-tts-preview` — `generateContent` ✅ (pilihan utama)
- cadangan: `gemini-2.5-flash-preview-tts`, `gemini-2.5-pro-preview-tts`

### 5. Kondisi lingkungan saat sesi ditutup

- Chrome profil Rifqi **sudah login** di produksi sebagai
  `rifqiahmadpratama@gmail.com` — jadi popup Google (yang dulu memblokir
  otomasi) TIDAK jadi masalah selama profil ini tidak sign out.
- Viewport tab: 1540×732, dpr 1.25. Untuk capture 1080p, maksimalkan jendela
  dulu.
- Ada run sisa `f27c898f30ba467790057ac0487db287` berstatus **queued** di
  workspace. Jangan dipakai untuk take — bikin run baru yang bersih.

### 6. Langkah berikutnya saat "lanjutkan"

1. Maksimalkan jendela, buat run baru bersih, jalankan alur penuh sambil
   capture frame: brief → ekstraksi Gemini → clarification link klien →
   confirm baseline → new request + usulan Guardrail → confirm classification →
   evidence → delivery review → proof (md/json) → bukti Cloud Run/Gemini.
   Ikuti gotcha di `docs/shot-list-video.md` (baca URL client link dari
   accessibility tree, hapus blocker "Unresolved questions", dst).
2. Bangun project Remotion di `video/remotion` (jangan di-commit dulu sebelum
   diputuskan; `*.mp4` besar sebaiknya tetap di luar repo).
3. Generate narasi Inggris lewat TTS Gemini, sinkronkan ke beat.
4. Render MP4 < 4 menit, tonton ulang, perbaiki timing.
5. Upload ke YouTube publik, isi item checklist §5 (video ≤4 menit + bukti
   agent & Google Cloud), masukkan linknya ke form Devpost.

---

## MILESTONE 29 Agu — audit penuh setelah merge partner: 3 bug produksi ketemu & diperbaiki

Instruksi Rifqi: cek total aplikasi dari login sampai akhir langsung di
Chrome, perbaiki semua error. Dilakukan terhadap **production**, bukan lokal.

### Bug 1 — Guardrail tidak pernah jalan di portal klien (backend)

`POST /client/{token}/new-request` mencatat request tapi **tidak pernah
memanggil guardrail agent**, beda dari `POST /runs/{run_id}/requests` versi
freelancer. Akibatnya request yang klien kirim sendiri lewat portal
self-service selalu nongkrong tanpa usulan klasifikasi + citation, dan
freelancer harus menebak manual. Fix: panggil `propose_scope_classification`
dengan pola fail-open yang sama. Commit `28051dd`. Test baru:
`test_klien_submit_request_baru_menyimpan_usulan_guardrail`.

### Bug 2 — SEMUA halaman daftar mati di production (backend)

`/records`, `/sources`, `/review`, `/activity` semuanya menampilkan
"Failed to fetch". Bukan CORS (itu dugaan awal yang salah — endpoint balas
401 JSON dengan normal). Akar masalah ada di log Cloud Run:

```
google.api_core.exceptions.FailedPrecondition: 400 The query requires an index.
```

`store.list_runs()` menggabungkan `.where("owner_id", "==", ...)` dengan
`.order_by("updated_at")`. Firestore hanya melayani kombinasi itu lewat
**composite index**, dan index-nya belum pernah dibuat, jadi query gagal
total. Dengan token invalid auth gagal duluan (401) sehingga kode ini tidak
pernah tersentuh — itu sebabnya tes manual dengan token asal-asalan
kelihatan "sehat".

**Fix: sort dipindah ke Python, `order_by` Firestore dihapus** (commit
`5d6a9c3`). Sengaja TIDAK membuat composite index-nya, karena deployment
baru — termasuk juri yang deploy ke project sendiri — tidak akan punya index
itu dan akan patah dengan cara yang sama. Cabang LOCAL memang sudah sort di
Python, jadi keduanya kini konsisten.

> **Pelajaran yang harus diingat:** SELURUH test suite backend jalan di mode
> LOCAL (file JSON) dan tidak pernah menyentuh Firestore sungguhan. "227 test
> hijau" TIDAK membuktikan jalur Firestore aman. Test regresi baru di
> `test_owner_read_models.py` sekarang menjaga jalur Firestore-nya lewat fake
> client (assert `order_by` tidak dipanggil).

### Bug 3 — dua bug tampilan ledger (frontend)

1. **Deliverables tampil `[object Object]`** di halaman Baseline.
   `canonical_payload.deliverables` diketik `unknown[]`, sehingga
   `.map(String)` lolos TypeScript padahal isinya objek `{id, title}`.
   Tipe diperbaiki jadi `Deliverable[]` (mengikuti `schemas.Deliverable` di
   backend) dan dirender `id: title`.
2. **`timeline` dan `revision_policy` selalu tampil "No value"** di halaman
   Source record, padahal datanya ada. Keduanya adalah **wadah berisi
   sub-field** (`final_deadline`, `rounds_total`), bukan field tunggal, tapi
   dibaca sebagai satu field. Ini menyembunyikan deadline hasil ekstraksi
   Gemini DAN revision rounds yang distage dari fitur preference baru.
   Formatter dipindah ke `web/src/lib/ledger-summary.ts` supaya bisa diuji
   tanpa merender React, sekalian memperbaiki nilai numerik `0` yang dulu
   dibaca sebagai kosong. Commit `2331553` + `84cda8d`.

### Status deploy — BACA INI SEBELUM LANJUT

- **Backend: sudah live.** Rev `delividence-api-00003-vdm` +
  `delividence-worker-00003-8lg`. Diverifikasi 14 langkah end-to-end di
  produksi (create run → ekstraksi Gemini → clarification → confirm baseline
  → new-request klien + usulan Gemini → confirm classification → evidence →
  delivery review → proof md/json), semua hijau, log Cloud Run **nol error**.
- **Frontend: sudah live juga** (setelah PR #1 di-merge + sync ke repo clone,
  lihat di bawah). Diverifikasi di produksi: deliverables tampil
  `d1: Editing promo video for online store`, dan Source record menampilkan
  `final deadline: next Wednesday · CLIENT_STATED` +
  `rounds total: 2 · FREELANCER_POLICY` — keduanya sebelumnya salah.

### Cara frontend sampai ke produksi — JANGAN salah lagi

Ini sempat memakan waktu karena dugaan awal salah dua kali:

1. `rifqi` **bukan** branch yang di-deploy Vercel — push ke sana tidak
   mengubah apa pun di produksi.
2. `main` di `irham3/delividence` **juga bukan**. PR #1 sudah di-merge ke
   `main`, ditunggu 15 menit, bundle produksi tetap kode lama.
3. **Yang benar: Vercel deploy dari repo clone privat
   `rifqiahmadpratama/delividence` (branch `main`)** — repo terpisah dengan
   histori sendiri (satu commit "Initial commit" hasil fitur Clone milik
   Vercel), BUKAN fork/mirror. `gh repo view ... --json pushedAt` menyesatkan
   di sini; yang membuktikan adalah isinya (file baru partner ada di sana).

Cara sync yang dipakai (non-destruktif, tanpa menimpa histori clone):

```bash
git remote add vercelclone https://github.com/rifqiahmadpratama/delividence.git
git fetch vercelclone
TREE=$(git rev-parse HEAD^{tree})
NEW=$(git commit-tree "$TREE" -p vercelclone/main -m "sync: ...")
git push vercelclone "$NEW:refs/heads/main"
```

Deploy Vercel jalan otomatis ~60 detik setelah push itu. **Setiap perubahan
frontend ke depan wajib ikut langkah ini**, kalau tidak perubahannya tidak
akan pernah kelihatan di `delividence.vercel.app`.

Status test setelah semua fix: backend **227 hijau**, frontend **9 unit
(vitest)** + **5 e2e (Playwright)** hijau, `tsc --noEmit` bersih,
`next build` sukses.

---

## MILESTONE 27 Agu — deploy production penuh ke Google Cloud + Vercel, diverifikasi end-to-end

Instruksi Rifqi: jalankan seluruh setup deploy dari nol (GCP billing, Firebase,
Vercel, Cloud Run, Gemini API) sampai siap demo, ikuti urutan supaya tidak
kena error CORS/Firebase/billing di tengah.

### Akun & project

- Google account owner: **`rifqiahmadpratama@gmail.com`** — sama untuk GCP,
  Firebase, GitHub, dan Vercel (bukan akun `rifqiahmad234a@gmail.com` yang
  dipakai sesi-sesi sebelumnya untuk `dudepercobaan`).
- Project GCP: **`gen-lang-client-0104798459`** ("Gemini API" di AI Studio) --
  BUKAN project baru custom (`delividence-hackathon` di contoh instruksi)
  karena akun `rifqiahmadpratama` kena **quota limit pembuatan project baru**
  (`gcloud projects create` gagal "exceeded your allotted project quota").
  Menghapus 3 project lama tidak langsung membebaskan quota (GCP
  soft-delete tetap terhitung sampai purge 30 hari) -- solusinya reuse
  project existing yang masih kosong (cuma Gemini API enabled, belum ada
  Cloud Run/Firestore/Pub-Sub).
- Billing: billing account `010843-5311E0-8D874C` (IDR) sudah ada &
  aktif di akun ini, tidak perlu prepayment Rp500rb untuk **GCP Cloud
  Billing** (Cloud Run/Firestore/Pub-Sub). Budget alert Rp50.000/bulan,
  threshold 50/90/100%, dibuat lewat `gcloud billing budgets create`.

### Firebase

- Firebase disambungkan ke project via Firebase Management API
  (`:addFirebase`, `x-goog-user-project` header wajib supaya tidak kena
  `PERMISSION_DENIED` quota project ADC).
- Web app `Delividence Web` dibuat via API, config didapat
  (`gen-lang-client-0104798459.firebaseapp.com`, dst).
- Google Sign-In: **REST API tidak bisa create OAuth client dari nol**
  untuk project yang belum pernah punya provider Google (sama seperti
  temuan sesi `dudepercobaan` sebelumnya) -- Rifqi aktifkan manual lewat
  Console (Authentication > Sign-in method > Google > isi support email >
  Save), Console yang auto-provision OAuth client baru.
- `localhost` otomatis masuk authorized domains; `delividence.vercel.app`
  ditambah manual lewat Identity Toolkit API setelah domain Vercel ada.

### Vercel

- GitHub App Vercel yang terhubung ke akun `rifqiahmadpratama` **tidak bisa
  import langsung** repo `irham3/delividence` (beda owner, GitHub App
  personal cuma lihat repo milik akun sendiri walau Rifqi collaborator).
  Satu-satunya jalur: **"Clone" jadi repo privat baru**
  `rifqiahmadpratama/delividence` (snapshot `main`, di-deploy dari situ) --
  konsekuensinya push ke `irham3/delividence` tidak auto-redeploy, perlu
  redeploy manual dari Vercel dashboard tiap ada update penting.
- Root Directory `web`, tapi **deploy pertama 404** karena Framework Preset
  ke-detect "Other" (root direktori diset SETELAH clone pertama, preset
  tidak auto-refresh). Fix: set manual Framework Preset ke "Next.js" di
  Project Settings, baru redeploy -- baru langsung sukses.
- 7 environment variables (6 Firebase config + `NEXT_PUBLIC_API_URL`
  placeholder), lalu update lagi ke URL Cloud Run asli setelah step deploy
  API + redeploy sekali lagi.
- Live: **`https://delividence.vercel.app`**.

### GCP resource + deploy Cloud Run

- `deploy/01-setup-gcp.ps1` jalan mulus KECUALI langkah publisher DLQ --
  service agent Pub/Sub (`service-{project}@gcp-sa-pubsub...`) belum
  ke-provision di project baru, fix dengan
  `gcloud beta services identity create --service=pubsub.googleapis.com`
  lalu re-run script (idempotent, aman diulang).
- **`deploy/02-deploy.ps1` di repo ternyata TIDAK PERNAH di-update** sejak
  ditulis pertama kali -- tidak ada parameter `-FrontendOrigin`,
  `-FirebaseProjectId`, `-ModelRuntime` yang disebut instruksi, dan tidak
  wire `ALLOWED_ORIGINS`/`FIREBASE_PROJECT_ID`/secret Gemini ke Cloud Run
  sama sekali (dua fitur itu ditulis belakangan setelah script deploy
  terakhir disentuh). **Diperbaiki**: tiga parameter baru ditambahkan,
  worker & API sekarang dapat `GOOGLE_GENAI_USE_VERTEXAI` +
  `--set-secrets GEMINI_API_KEY=...:latest` (kalau `-ModelRuntime
  developer`, default), API juga dapat `FIREBASE_PROJECT_ID` +
  `ALLOWED_ORIGINS`. Script juga sekarang grant
  `roles/secretmanager.secretAccessor` ke SA api & worker sebelum deploy
  (ditaruh di 02, bukan 01, karena urutan kerja: provision dulu baru
  secret baru deploy). **Bug ketemu sambil nulis fix ini**: gcloud
  `--set-env-vars` pakai koma sebagai pemisah key=value, sedangkan
  `ALLOWED_ORIGINS` sendiri berisi banyak origin dipisah koma -- pakai
  delimiter alternatif gcloud (`^;^KEY=VAL;KEY=VAL`) supaya tidak pecah.
- Live: **API `https://delividence-api-3jww7h7koq-et.a.run.app`**, **worker
  `https://delividence-worker-3jww7h7koq-et.a.run.app`**.

### Gemini API key -- dua masalah beruntun

1. Key lama project ini (`...2mv4`, dibuat Feb 2025 dari AI Studio) sudah
   **invalid/revoked** ("API key not valid") -- bukan masalah cara pakai.
2. Key baru yang di-generate AI Studio sekarang pakai **format berbeda**
   (prefix `AQ.` bukan `AIzaSy` lagi) -- signature Google Cloud API key
   generation di AI Studio sempat gagal berkali-kali dengan "The request is
   suspicious" **spesifik lewat browser automation** (percobaan manual
   Rifqi langsung sukses di percobaan pertama, jadi ini deteksi anti-bot
   Google terhadap aksi create-credential, bukan masalah account/project).
   Key baru sempat **dua kali salah tercatat**: pertama field yang di-copy
   salah (Name/Project alih-alih API Key), kedua **salah baca 1 karakter**
   dari screenshot (`I` besar vs `l` kecil di akhir string) -- pelajaran:
   untuk string sepanjang ini SELALU ambil dari accessibility tree
   (`read_page`) bukan baca visual dari screenshot.
3. Setelah key benar, masih dapat `429 "Your prepayment credits are
   depleted"` -- **Gemini Developer API di project dengan Cloud Billing
   aktif butuh prepayment terpisah** dari GCP Cloud Billing biasa (dua
   wallet berbeda walau satu akun Google). Rifqi top-up manual lewat AI
   Studio billing, baru extraction & Guardrail jalan.

### Verifikasi end-to-end (via API asli, bukan UI klik manual)

Google OAuth popup **diblokir sandbox browser automation** (window.open
null) -- tidak bisa tes lewat klik "Sign in with Google" di browser
otomatis. Solusi: aktifkan **Email/Password sementara** di Firebase Auth
(pola yang sama dipakai sesi `dudepercobaan` 25 Agu), bikin 1 user tes
lewat REST API `accounts:signUp`, dapat ID token Firebase **asli**, lalu
jalankan seluruh alur produksi lewat `curl` pakai token itu:

`POST /runs` (Firestore+Pub/Sub) -> worker proses via push OIDC tanpa
request kedua -> **ekstraksi Gemini asli** (4 field ledger + kutipan
verbatim) -> readiness gate -> client portal isi `out_of_scope` ->
`ready:true` -> confirm -> **baseline v1 ACTIVE** -> log request ->
**Guardrail Gemini asli** propose `CHANGE_REQUEST` + kutipan valid ->
confirm klasifikasi -> attach evidence -> delivery review link -> client
Accept -> **Proof Manifest** lengkap (evidence + keputusan klien). CORS
dari origin Vercel juga dites lewat `curl -X OPTIONS` dan benar
(`access-control-allow-origin: https://delividence.vercel.app`).

User tes dan provider Email/Password **sudah dibersihkan/dimatikan lagi**
setelah verifikasi selesai (login production tetap Google-only).

**Tidak ada perubahan kode aplikasi di sesi ini** (backend/frontend) --
murni infrastruktur & satu fix di `deploy/02-deploy.ps1`. Test suite tetap
220 hijau (tidak dijalankan ulang, tidak ada yang berubah).

### Lanjutan sesi yang sama -- README diperbarui, local dev disambungkan ke production, partner dikasih akses

**`backend/README.md` ternyata usang parah** (masih dari fase "vertical
slice" sebelum Firebase Auth/Gemini/Guardrail ada) -- dua hal di dalamnya
sudah aktif salah, bukan cuma kurang jelas: (1) command `uvicorn` di situ
TIDAK punya `--env-file .env`, persis bug yang sudah didokumentasikan di
atas; (2) contoh `curl POST /runs` tanpa header Authorization, padahal
endpoint itu sekarang wajib Firebase ID token. Diperbaiki -- README sekarang
juga jelaskan setup `.env` (`GEMINI_API_KEY`/`FIREBASE_PROJECT_ID`), cara
dapat ID token untuk tes manual (lewat frontend DevTools atau REST
`accounts:signUp` sementara), dan larangan eksplisit pakai/minta
`GEMINI_API_KEY`/kredensial produksi milik rekan tim.

**`.env` lokal Rifqi sekarang SUNGGUH nyambung ke Firestore/Pub-Sub
PRODUKSI** (`GOOGLE_CLOUD_PROJECT=gen-lang-client-0104798459`,
`FIREBASE_PROJECT_ID` sama) -- sebelumnya `FIREBASE_PROJECT_ID` masih
`dudepercobaan` (proyek lama, ketinggalan dari sesi lain), sudah disamakan.
Ini keputusan sadar Rifqi (bukan default yang disarankan) supaya backend
lokal bisa lihat/tulis data produksi asli, bukan cuma mode LOCAL file JSON.

Konsekuensi teknis yang tidak trivial: subscription push yang sudah ada
(`delividence-runs-push`) tetap mengirim job ke Cloud Run worker seperti
biasa -- job TIDAK otomatis mampir ke worker lokal (push subscription
target-nya fixed ke satu URL). Dibuatkan **`backend/local_pubsub_forwarder.py`**
(baru, bukan bagian dari app FastAPI) -- pull dari subscription pull
terpisah (`LOCAL_PULL_SUBSCRIPTION_ID` env var, default
`delividence-runs-local-pull`) lalu forward ke `/pubsub/push` worker lokal
dengan envelope yang sama persis. Efeknya: **setiap run diproses DUA KALI**
(Cloud Run + worker lokal), disengaja, dua-duanya independen lewat
subscription terpisah, idempotency (`claim_job`) yang sudah ada mencegah
efek samping ganda di level ledger.

**Partner (Irham, `irhamtria@gmail.com`) diberi akses IAM** ke
`gen-lang-client-0104798459`: `roles/datastore.user` +
`roles/pubsub.editor` (BUKAN owner/editor project, tidak bisa ubah
billing/secret/deploy). Subscription pull terpisah dibuatkan untuknya:
`delividence-runs-local-pull-irham` (subscription pull tidak boleh dipakai
bareng dua orang sekaligus -- pesan di-load-balance antar consumer, bukan
disalin ke semuanya). `GEMINI_API_KEY` **TIDAK** dibagikan ke Irham --
dia generate sendiri, tetap isi `GOOGLE_CLOUD_PROJECT`/`FIREBASE_PROJECT_ID`
yang sama. Instruksi lengkap ada di `backend/README.md` bagian "Nyambung
backend lokal ke Firestore/Pub-Sub produksi".

Proses lokal yang jalan di laptop Rifqi saat catatan ini ditulis (mati
kalau laptop restart, TIDAK auto-start lagi -- perlu dijalankan ulang manual
sesuai README kalau mau lanjut sesi ini):
- `uvicorn` ROLE=worker port 8081 (`--env-file .env`, PID berubah tiap restart)
- `uvicorn` ROLE=api port 8080 (`--env-file .env`)
- `local_pubsub_forwarder.py` (subscription `delividence-runs-local-pull`)

Firestore koleksi tes lama (`client_links`, `deals`, `jobs`, `runs`) sudah
**dibersihkan semua** (dihapus manual satu-satu, bukan bulk-delete) supaya
Cloud Console bersih untuk screenshot/rekaman demo video.

**Project GCP di-rename** (display name saja, Project ID tidak bisa
diganti): "Gemini API" -> **"Delividence"**, biar rapi di screenshot Cloud
Console.

Commit sesi ini (branch `rifqi`, sudah di-push): `7834f86` (fix deploy
script), `788a42a` (forwarder + README).

## MILESTONE 26 Agu (lanjutan #7) — Gemini akhirnya sukses sungguhan, dan Guardrail sekarang model-assisted

Sesi baru setelah "penutup sesi" sebelumnya. Tiga hal sekaligus, saling
bergantung satu sama lain.

### 1. Root cause ekstraksi Gemini gagal ditemukan — bukan kuota, env tidak pernah ke-load

Waktu server dinyalakan ulang sesi ini (`uvicorn app.main:app ...` persis
seperti instruksi README), ekstraksi langsung gagal dengan
`ValueError: No API key was provided`. Ditelusuri: **proyek ini tidak
pernah punya `load_dotenv()` di kode manapun** — `backend/.env` selama ini
dianggap harus di-*source* manual ke environment sebelum start (itu
sebabnya instruksi lama pakai `$env:GEMINI_API_KEY = ...` per variabel,
bukan file). Command README/CATATAN sebelumnya yang cuma
`uvicorn app.main:app --host ... --port ...` tanpa apa-apa lagi TIDAK
pernah benar-benar membaca `.env`.

**Fix**: tambahkan `--env-file .env` ke command uvicorn (paket
`python-dotenv` kebetulan sudah ke-install sebagai dependency transitif,
uvicorn CLI punya flag ini bawaan, tidak ada kode aplikasi yang diubah
sama sekali). Command lokal yang benar sekarang:

```powershell
$env:ROLE = "worker"; ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8081 --env-file .env
$env:ROLE = "api"; $env:WORKER_URL = "http://127.0.0.1:8081"; ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --env-file .env
```

Diverifikasi lewat "Retry extraction" di run test: worker log bersih tanpa
exception, audit trail tertulis "Brief diekstrak lewat Gemini -- 2 field
ledger terisi." — ekstraksi ASLI, bukan stub. **Item 13 & blocker
GEMINI_API_KEY di bawah sekarang benar-benar selesai**, bukan lagi
"tinggal tunggu demand mereda".

### 2. Guardrail — classification+citation otomatis lewat Gemini (item 12/14, akhirnya selesai)

Instruksi Rifqi setelah fix di atas: "coba fix biar Gemini extraction bisa
jalan" lalu "lanjutkan" — diteruskan ke item yang sejak awal dicatat
"baru dikerjakan setelah ekstraksi sukses sekali secara nyata".

- `app/agent.py`: agent ADK baru `guardrail_agent` + tool
  `propose_classification` — pola PERSIS `save_ledger_draft`: usulan model
  divalidasi tanpa syarat lewat `guardrail.classify()` yang sudah ada
  sejak lama (IN_SCOPE/CHANGE_REQUEST tanpa kutipan yang benar-benar valid
  turun AMBIGUOUS), tidak pernah dipercaya mentah-mentah.
- `app/api.py`: `POST /runs/{id}/requests` sekarang memanggil agent ini
  SEKALI setelah request tercatat, hasilnya disimpan sebagai
  `proposed_classification`/`proposed_citations` -- terpisah dari
  `confirmed_classification` (freelancer tetap satu-satunya yang berwenang
  konfirmasi, 09-DOMAIN-RULES §8, model tidak pernah otomatis
  memutuskan). Kegagalan Gemini tidak menggagalkan pencatatan request itu
  sendiri, non-fatal, pola sama dengan worker ekstraksi. Menulis
  `SCOPE_ANALYSIS_PROPOSED` -- enum ini sudah dicadangkan sejak
  `enums.py` pertama kali ditulis, baru sekarang benar-benar dipakai.
- `app/scope_requests.py`: field baru `proposed_classification`/
  `proposed_citations` + `save_proposal()`, tidak menyentuh
  `mark_classified()`.
- Frontend (`page.tsx`, `RequestCard`): form klasifikasi pre-fill dari
  usulan model + hint "Model suggested: ..." -- tombol "Confirm
  classification" tetap wajib diklik manual.
- Test baru: 3 bypass-LLM di `test_agent.py` (pola sama
  `test_agent.py` yang sudah ada), 2 di `test_guardrail_endpoint.py`
  (sukses + kegagalan Gemini tidak menggagalkan submit). **220 test
  hijau.**

**Diverifikasi dengan Gemini ASLI (bukan stub test suite)** lewat Chrome
sungguhan: run baru -> baseline v1 dikonfirmasi -> log request "Does the
fix also need to survive a full VM reboot, not just a process restart?"
-> Gemini balas **IN_SCOPE** dengan kutipan verbatim `deliverables[0]`
yang benar-benar cocok -> freelancer confirm -> tersimpan sebagai
keputusan final. Tidak ada exception di log API maupun worker.

Ini menutup **satu-satunya item fitur (non-deploy) yang masih "sengaja
belum"** di seluruh catatan ini. Sisa cuma deploy Cloud Run (blocker
billing, lihat di bawah, tidak berubah).

### 3. Sebelum dua hal di atas: sinkron dengan kerjaan UI partner + dark/light mode + beres-beres desain

- Ditarik 7 commit dari `delividence/main` (partner sudah merge `rifqi`
  lalu menambah redesign penuh: `app-shell.tsx`, `landing.tsx`,
  `client-frame.tsx`, sistem desain "paper" berbasis CSS variable,
  gsap+lucide-react) -- fast-forward bersih, tidak ada konflik, langsung
  di-push balik ke `rifqi` supaya kedua branch sinkron.
- **Instruksi Rifqi**: cek konsistensi desain + tambahkan dark/light mode.
  Temuan: shell baru sudah pakai token CSS (`--rule`/`--muted`/`--accent`
  dst), tapi banyak panel di dalamnya (Guardrail, Propose Scope Change,
  form `ListField` portal klien, `ReadinessBanner`, status pill review)
  masih pakai class Tailwind mentah (`neutral-300`, `green-50`,
  `dark:border-neutral-700` dst) peninggalan sebelum redesign -- disatukan
  semua ke token yang sama, termasuk token status baru (`--status-ok-*`,
  `--status-warn-*`, `--status-neutral-*`).
- Dark/light mode dibangun dari nol: token warna dapat varian dark di
  `globals.css`, toggle manual (`ThemeToggle`, ikon sun/moon) di dashboard
  freelancer + landing page + semua halaman portal klien, persist
  `localStorage`, default ke preferensi sistem di kunjungan pertama, tanpa
  flash warna salah (`next/script` `beforeInteractive` +
  `suppressHydrationWarning` di `<html>`).
- Lolos `tsc --noEmit`, `eslint`, `next build`. Diverifikasi visual lewat
  Chrome sungguhan (light & dark, dashboard + portal klien).

**Commit** (branch `rifqi`, di-push): `564355e` (theme + konsistensi
desain), `9744b6e` (Guardrail agent). Total sesi ini: **220 test hijau**,
tidak ada satu pun perubahan yang menyentuh kode deploy/billing.

---

## MILESTONE 25 Agu malam — alur inti terbukti jalan end-to-end di browser

**Ini bukan lagi cuma backend teruji lewat curl — sekarang benar-benar dites
lewat UI sungguhan (Chrome), dan seluruh alur Handshake -> Delivery -> Proof
JALAN**: submit brief -> freelancer bikin clarification link -> klien isi
form ledger (deliverables, acceptance criteria, out of scope, deadline,
rounds) -> readiness gate berubah hijau -> confirm project plan -> baseline
v1 aktif -> freelancer lampirkan evidence -> freelancer bikin delivery
review link -> klien accept criterion -> Proof Manifest (Markdown) keluar
lengkap dengan kutipan, status, dan keputusan klien. **Tidak ada satu langkah
pun yang gagal di jalur ini.**

### Frontend (baru, sebelumnya sama sekali belum ada UI untuk fitur-fitur ini)

- `web/src/lib/api.ts` — tipe TypeScript + helper fetch bersama.
- `web/src/app/client/[token]/page.tsx` — portal clarification: lihat brief,
  readiness blockers, form dinamis (deliverables/acceptance criteria/out of
  scope sebagai daftar bisa tambah-hapus, deadline, revision rounds + NOT_SET),
  "Save changes" -> `POST .../answers`, "Confirm project plan" (aktif hanya
  kalau `readiness.ready`) -> `POST .../confirm` pakai `payload_hash` dari GET
  terakhir.
- `web/src/app/client/[token]/review/page.tsx` — portal delivery review:
  daftar criterion + evidence + status badge, Accept/Request changes (reason
  wajib), "Submit review" -> `POST .../review`. Criterion yang sudah
  `ACCEPTED` terkunci (pesan A-9 tampil).
- `web/src/app/page.tsx` — panel "Freelancer actions" baru: tombol bikin
  clarification link & delivery review link (link kedua nonaktif sampai ada
  baseline), form lampirkan evidence, link "View JSON"/"View Markdown" ke
  Proof. **`runId` sekarang persist ke `localStorage`** (sebelumnya hilang
  kalau halaman di-reload — freelancer kehilangan akses ke run-nya sendiri;
  ada tombol "Start a new run" buat reset sengaja).
- Semua lolos `tsc --noEmit`, `eslint`, dan `next build`.

### Bug nyata yang ketemu & diperbaiki selagi tes UI sungguhan

1. **`worker.py` tidak pernah benar-benar mengirim teks brief ke model.**
   `tool_context.state["artifacts"]` cuma kebaca dari DALAM tool, model
   sendiri tidak bisa "melihat" state itu — jadi model selalu bilang "tidak
   ada konten untuk dikutip" walau state sudah terisi. **Fix**: teks brief
   sekarang disertakan langsung di pesan awal ke model (`run_extraction` di
   `app/worker.py`). Ini bug yang lolos di commit sebelumnya karena verifikasi
   sebelumnya cuma sampai "berhasil sampai ke Gemini dan gagal dengan baik" —
   belum pernah benar-benar melihat isi ekstraksinya.
2. **Instruksi agent tidak cukup spesifik soal bentuk `value`.** Model
   awalnya menulis `deliverables`/`acceptance_criteria` sebagai satu string
   paragraf, bukan `list of object` sesuai `app/domain/schemas.py`. **Fix**:
   `_INSTRUCTION` di `app/agent.py` sekarang menjabarkan bentuk persis tiap
   field. Hasil re-test: `schemas.DealLedger.model_validate()` lolos.
3. **CORS menolak `:3001`.** Next.js pindah otomatis ke port 3001 kalau 3000
   sedang dipakai project lain di mesin yang sama (di sini: project ARGA).
   `ALLOWED_ORIGINS` di `.env`/`.env.example` sekarang mengizinkan 3000 DAN
   3001 sekaligus untuk localhost dan 127.0.0.1.
4. **HMR Next.js diblokir kalau diakses lewat `127.0.0.1`, bukan
   `localhost`.** Next.js 16 by default menolak dev resource cross-origin;
   `127.0.0.1` dan `localhost` dihitung origin berbeda. Efeknya: klik/ketik
   di halaman jadi tidak konsisten (state ke-reset di tengah interaksi,
   React ref jadi stale) karena client HMR terus retry gagal. **Bukan bug di
   kode aplikasi** — kalau test manual lewat browser lagi, **selalu pakai
   `http://localhost:PORT`, jangan `127.0.0.1:PORT`**.

### Temuan penting soal Gemini — WAJIB dibaca sebelum demo/testing lagi

- **`gemini-3.7-flash` konsisten 503 "high demand"** setiap dipanggil lewat
  `extraction_agent` (tool-calling + system instruction) — tapi panggilan
  SEDERHANA (tanpa tool) ke model yang sama berhasil. Jadi bukan soal API
  key/auth, murni kapasitas Google untuk beban kerja tool-calling di model
  itu saat ini.
- **`gemini-2.5-flash` sudah deprecated** (404, "no longer available to new
  users").
- **`gemini-3.6-flash` terbukti sukses** — ekstraksi asli dengan kutipan
  verbatim tervalidasi, hasil lolos validasi skema. **Sekarang jadi default**
  (`GEMINI_MODEL` di `app/config.py`, `.env`, `.env.example`).
- **Free tier Gemini Developer API punya kuota SANGAT terbatas: 20
  request/hari PER MODEL PER PROJECT** (`GenerateRequestsPerDayPerProjectPerModel-FreeTier`).
  Satu kali ekstraksi lewat `extraction_agent` menghabiskan **beberapa**
  quota sekaligus (multi-turn tool-calling: panggilan awal + tiap balasan
  tool = panggilan terpisah ke API). Kuota `gemini-3.6-flash` project
  `dudepercobaan` **sudah habis untuk hari ini** gara-gara sesi debugging
  ini sendiri (429 RESOURCE_EXHAUSTED). **Implikasi untuk demo**: jangan
  coba-coba ekstraksi berkali-kali di hari H tanpa rencana — kuota reset
  harian, tapi 20 request habis dalam hitungan menit kalau dites berulang.
  Kalau butuh lebih dari itu, generate API key dari akun/project GCP lain
  (masing-masing project dapat kuota gratis sendiri), atau upgrade ke
  billing (balik ke opsi Vertex AI/paid tier).
- Ganti model kapan saja tinggal ubah `GEMINI_MODEL` di `.env` — tidak ada
  kode yang perlu diubah.

Tidak ada proses yang ditinggal jalan. Aman dimatikan.

---

## MILESTONE 25 Agu malam (lanjutan #2) — Firebase Auth (owner login) selesai, dites end-to-end dengan token asli

Instruksi Rifqi: "lanjut ke auth dan New Request UI" — bagian auth-nya.
Sebelum ini TIDAK ADA auth sama sekali: semua endpoint owner (`POST /runs`,
`GET /runs/{id}`, client-links, evidence, proof, requests/classify) terbuka
tanpa proteksi apa pun, dan tidak ada konsep `owner_id`.

**Setup Firebase (proyek `dudepercobaan`, sudah ada Firebase-nya, tinggal
dilengkapi) — lewat REST API Firebase Management/Identity Toolkit, bukan
lewat console manual:**
- Web app baru didaftarkan (`Delividence Web`,
  `1:809536883160:web:6d48fb0ecf49294375caad`), config-nya (public,
  bukan secret) ditaruh langsung di `web/src/lib/firebase.ts`.
- Provider **Google Sign-In diaktifkan** (`defaultSupportedIdpConfigs/google.com`,
  `enabled: true`) — satu-satunya provider aktif di production, sesuai
  06-SETUP.md §6 ("idealnya Google Sign-In"). `authorizedDomains` sudah
  otomatis memuat `localhost` (berlaku semua port).

**Backend (`backend/app/`):**
- `app/auth.py` (baru) — `require_owner()`: dependency FastAPI yang
  memverifikasi header `Authorization: Bearer <Firebase ID token>` lewat
  `firebase_admin.auth.verify_id_token()`, mengembalikan `uid` sebagai
  `owner_id`. 401 kalau header hilang/salah bentuk/token tidak valid.
  `firebase_admin.initialize_app(credentials.ApplicationDefault(), ...)` --
  pakai ADC yang sama dengan `gcloud auth application-default login`
  (sudah ada dari setup sebelumnya), bukan service account key file.
- `app/config.py`: `FIREBASE_PROJECT_ID` (env baru, `.env`/`.env.example`) --
  sengaja terpisah dari `GOOGLE_CLOUD_PROJECT`/`LOCAL` karena Firebase Auth
  layanan hosted, bukan Firestore -- tetap dipakai walau `LOCAL=True`.
- `app/store.py`: `create_run()` sekarang menyimpan `owner_id`.
- `app/api.py`: helper `_owned_run_or_404(run_id, owner_id)` -- 404 kalau
  run tidak ada ATAU milik owner lain (bukan 403, supaya keberadaan deal
  tidak bocor). Dipasang di SEMUA endpoint owner: `POST /runs`,
  `GET /runs/{id}`, `POST /runs/{id}/client-links`,
  `POST /runs/{id}/evidence`, `GET /runs/{id}/proof`,
  `POST /runs/{id}/requests`, `GET /runs/{id}/requests`,
  `POST /runs/{id}/requests/{id}/classify`. Endpoint `/client/{token}/...`
  **TIDAK disentuh** -- itu tetap opaque-token-only, sesuai desain (02 §8:
  client tidak punya akun).
- `requirements.txt`: `firebase-admin==7.2.0`.

**Test (`tests/conftest.py` + `tests/test_auth.py`, baru):**
- Fixture `fake_owner` (autouse) -- override `auth.require_owner` jadi
  owner tetap `"test-owner-1"` lewat `app.dependency_overrides`, supaya
  194 test lain (yang ditulis sebelum auth ada) tidak perlu tahu soal
  token sama sekali. Verifikasi token ASLI diuji terpisah.
- `test_auth.py` (5 test baru): tanpa token -> 401 (semua endpoint owner
  dicoba lewat satu skenario cross-owner), header bukan `Bearer` -> 401,
  owner lain baca run owner lain -> 404 di SEMUA endpoint owner, owner asli
  tetap bisa.

**Frontend (`web/src/lib/firebase.ts` baru, `web/src/lib/api.ts`,
`web/src/app/page.tsx`):**
- `firebase.ts`: init Firebase app (config public), `signInWithGoogle()`
  (`signInWithPopup` + `GoogleAuthProvider`), `signOutOwner()`.
- `api.ts`: `setAuthTokenProvider(fn)` -- `apiFetch` menyisipkan
  `Authorization: Bearer <token>` otomatis kalau provider mengembalikan
  token, no-op kalau tidak (portal klien di `client/[token]/*` TIDAK
  pernah memanggil `setAuthTokenProvider`, jadi tetap unauthenticated
  seperti sebelumnya -- `api.ts` sengaja tidak import `firebase.ts`
  langsung supaya portal klien tidak ikut menyeret dependency Firebase).
  Tambah `openAuthedInNewTab(path)` -- View JSON/View Markdown proof dulu
  `<a href>` polos (tidak bisa bawa header custom), sekarang fetch manual +
  blob URL supaya tetap kebawa token.
- `page.tsx`: `onAuthStateChanged` gate -- belum login menampilkan tombol
  "Sign in with Google" saja (dashboard/form disembunyikan total, bukan
  cuma dinonaktifkan); sudah login menampilkan email + "Sign out" di
  header. Semua panggilan API (`submit`, `poll`) dipindah dari `fetch`
  polos ke `apiFetch` supaya ikut kebawa token -- ini FIX, sebelumnya dua
  tempat ini bypass `apiFetch` dan tidak akan pernah bawa auth header kalau
  tidak diubah.
- Lolos `tsc --noEmit`, `eslint`, `next build`.

**Dites end-to-end dengan token Firebase ASLI (bukan mock), dua cara:**
1. Lewat `curl` langsung: dua user REST (`accounts:signUp`, email/password
   -- provider ini diaktifkan SEMENTARA khusus untuk tes ini, dimatikan
   lagi + kedua akun test dihapus setelah selesai) menghasilkan ID token
   asli. Token owner-a berhasil `POST /runs`; owner-b baca run owner-a ->
   **404** (isolasi kebukti), owner-a baca run sendiri -> 200.
2. Lewat browser sungguhan (Chrome): sign-in real lewat SDK Firebase yang
   sama persis dengan yang dipakai tombol "Sign in with Google" (hanya
   metode sign-in-nya yang beda -- popup Google diblokir oleh sandbox
   otomasi browser ini, `window.open` mengembalikan `null`; klik tombolnya
   sendiri sudah dicoba dan TIDAK error, cuma popup-nya yang tidak bisa
   dibuka karena keterbatasan environment tes, bukan bug aplikasi -- lihat
   catatan di bawah), dashboard render dengan email ter-signed-in, submit
   brief lewat form sungguhan -> run tercipta dengan `owner_id` = uid
   Firebase asli (dicek langsung isi file `.localdata/runs/*.json`), Sign
   out mengembalikan ke gate. Hook debug sementara yang dipakai untuk ini
   (`window.__authDebug`) SUDAH DIHAPUS lagi dari `firebase.ts` setelah
   tes selesai -- tidak ada sisa kode test di commit.
- Commit `d991b39` (branch `rifqi`).
- **Update: Rifqi sudah coba manual di browser normal -- gagal pertama
  kali** dengan `Error 401: deleted_client` dari Google ("The OAuth client
  was deleted"). Root cause: project `dudepercobaan` proyek lama yang
  sudah dipakai belasan eksperimen pribadi Rifqi -- OAuth 2.0 Client ID
  yang tersambung ke `defaultSupportedIdpConfigs/google.com` sudah
  dihapus di suatu titik sebelumnya, tapi Identity Platform masih
  menyimpan referensi ke client ID lama itu (`...cctmnbkp7vvcd89g...`).
  **Tidak ada API publik untuk membuat ulang OAuth Client ID "Web
  application" dari nol** (Firebase Management/Identity Toolkit REST API
  cuma bisa PATCH provider yang sudah ada, POST-create menolak dengan
  "client_id cannot be empty" kalau tidak ada client_id valid). **Fix**:
  dikerjakan lewat Firebase Console UI sungguhan (bukan API mentah) --
  Authentication > Sign-in method > Add new provider > Google > isi
  "Support email for project" (belum pernah diisi) > Save. Console
  meng-auto-provision OAuth client BARU (`...soh32jqn9afqtpdvhv1j...`)
  lewat jalur internal yang tidak tersedia di REST API publik. Setelah
  ini, Rifqi coba lagi dan **berhasil sign-in dengan akun asli**
  (`rifqiahmadpratama@gmail.com`), dashboard render dengan benar.

---

## MILESTONE 26 Agu (lanjutan #6) — criterion key jadi dropdown, dan penutup sesi ini

Perbaikan kecil terakhir sebelum berhenti: field "criterion key" di form
"Attach evidence" tadinya free text -- freelancer harus mengetik ulang key
dari ingatan, salah ketik gagal diam-diam (404, baru ketahuan setelah
submit). Sekarang `<select>` dari `run.ledger.acceptance_criteria`
(sudah tersedia di frontend sejak `ChangeProposalPanel` dibangun). Dites
lewat Chrome sungguhan: dua criteria muncul benar di dropdown, evidence
yang dipilih dari dropdown tersimpan ke criterion yang benar (diverifikasi
lewat proof manifest). Commit `0a8a48e`.

**Sesi ini dihentikan di sini atas keputusan Rifqi** -- 8 gap FE/BE nyata
ditemukan & diperbaiki lewat tiga jalur sisir berbeda (01-PRD step list,
audit event catalog + fungsi yang belum tersambung, 05-SUBMISSION-
CHECKLIST smoke test): ledger field yang tidak tampil, polling run 404
tak berhenti, retry ekstraksi Gemini, Guardrail citable-refs tidak
lengkap, `client_links.revoke()` tidak tersambung, portal New Request
klien, dan dropdown criterion key. **215 test hijau**, semua sudah
di-push ke `rifqi` dan diverifikasi langsung ke GitHub (`gh api`, bukan
cuma git lokal). Sisa yang genuinely diblokir faktor luar (bukan kode):
model-side Guardrail (butuh kuota Gemini yang sudah sering habis di sesi
ini) dan deploy Cloud Run (butuh billing GCP yang belum aktif).

---

## MILESTONE 26 Agu (lanjutan #5) — portal "New Request" untuk klien, purpose yang sudah dicadangkan sejak awal tapi belum pernah dipakai

Instruksi Rifqi: "kerjain aja terus kalau bisa sampai beres" -- disisir
lewat kode langsung (bukan doc): fungsi/purpose apa saja yang SUDAH
didefinisikan lengkap tapi tidak pernah tersambung ke endpoint mana pun,
mengulang pola yang ketemu di `client_links.revoke()` sebelumnya.

**Temuan**: `app.domain.client_link.PURPOSES` sudah lama berisi 4 nilai
(`CLARIFICATION`, `APPROVAL`, `DELIVERY_REVIEW`, `NEW_REQUEST`), tapi
`_ACTIONS_BY_PURPOSE` di `api.py` cuma mengizinkan penerbitan link untuk 2
dari 4 (komentar di kode sendiri sudah mengaku: "portal new-request lewat
client link belum dibangun"). Ini persis 01-PRD §5 langkah 7: "klien dapat
mengirim request baru melalui portal yang sama" -- SEBELUM fix ini, satu-
satunya jalan mencatat request klien adalah freelancer menyalin manual
dari chat/email ke `GuardrailPanel` (endpoint `POST /runs/{id}/requests`
owner-only), bukan klien mengirim sendiri.

**Fix** (pola yang sama persis dengan CLARIFICATION/DELIVERY_REVIEW,
tidak ada endpoint/purpose baru yang diciptakan dari nol -- cuma
melengkapi yang sudah dirancang):
- `_ACTIONS_BY_PURPOSE["NEW_REQUEST"] = ["view", "submit"]`.
- `GET /client/{token}/new-request` (lihat brief untuk konteks) +
  `POST /client/{token}/new-request` (kirim `raw_text`, actor selalu
  `"client"`, `actor_ref` dari hash token -- pola sama dengan endpoint
  client lain, TIDAK PERNAH mempercayai identitas dari body). 409 tanpa
  baseline aktif (sama seperti endpoint requests yang lain). **Link
  sengaja TIDAK ditandai selesai setelah submit** -- beda dari
  `/review` (satu `review_session_id` per submit), klien boleh mengirim
  beberapa request terpisah lewat link yang sama sepanjang umur project,
  sama seperti `/answers` untuk CLARIFICATION.
- Halaman baru `web/src/app/client/[token]/request/page.tsx` (pola sama
  dengan `/review`): tampilkan brief untuk konteks, textarea + "Send
  request", pesan sukses yang tetap membolehkan kirim lagi.
- Dashboard freelancer: `FreelancerActions` di-refactor dari 2 pasang
  state (`clarificationLink`/`reviewLink`) jadi satu `Record<LinkPurpose,
  ...>` supaya nambah purpose ketiga tidak menduplikasi blok JSX/logic --
  tombol ketiga "Create new-request link" + "Revoke" (fitur revoke yang
  baru dibangun tadi otomatis ikut berlaku untuk purpose ini juga, tanpa
  kode tambahan).

**Dites end-to-end lewat Chrome sungguhan** (akun test asli, dihapus lagi
setelah selesai): submit brief -> confirm v1 lewat curl -> reload
dashboard -> klik "Create new-request link" -> buka link itu di tab
terpisah (`/client/{token}/request`, tanpa login sama sekali, sesuai
desain) -> isi & kirim -> `GET /runs/{id}/requests` (lewat token owner
asli) membuktikan `submitted_by: "client"` tersimpan benar dan tampil di
`GuardrailPanel` freelancer, siap diklasifikasi seperti request manapun.

Test baru: `tests/test_client_new_request.py` (5 test) -- termasuk
`test_new_request_link_tidak_bisa_dipakai_untuk_purpose_lain` (token
NEW_REQUEST ditolak di endpoint CLARIFICATION, dan sebaliknya).

Total **215 test hijau**. Commit `31865df` (branch `rifqi`, di-push,
diverifikasi `gh api`).

---

## MILESTONE 26 Agu (lanjutan #4) — client_links.revoke() akhirnya tersambung

Ditemukan sambil menelusuri kode (bukan dari doc): `app/client_links.py`
punya fungsi `revoke(raw_token)` LENGKAP sejak awal proyek ini dibangun
(hash, expiry, semuanya beres) -- tapi tidak ada satu endpoint pun yang
memanggilnya. Satu-satunya tempat itu dipakai adalah test yang memanggil
fungsi domain-nya langsung (`test_klien_membuka_link_yang_sudah_direvoke_403`),
bukan lewat HTTP. Freelancer yang salah kirim link, atau ingin
membatalkan link lama setelah menerbitkan yang baru untuk ronde
berikutnya, **tidak punya cara sama sekali** untuk melakukannya.

**Constraint desain yang penting**: raw token cuma pernah ada SEKALI, di
response `POST .../client-links` -- backend cuma menyimpan hash-nya
(02 §8, sengaja, supaya token bocor dari database tidak berguna). Artinya
revoke HANYA bisa ditawarkan tepat setelah link dibuat (selagi raw token
masih ada di state React), bukan lewat "daftar riwayat link" -- daftar
begitu memang tidak mungkin dibangun tanpa melanggar constraint itu.

**Fix**: `POST /runs/{run_id}/client-links/{token}/revoke` (owner-only,
404 kalau token tidak dikenal ATAU `deal_id`-nya bukan run ini). Frontend:
tombol "Revoke" kecil di sebelah link yang baru dibuat (baik clarification
maupun delivery review) -- state link sekarang `{token, url}`, bukan cuma
url string, supaya token-nya tersedia buat tombol ini.

Dites lewat Chrome sungguhan (sign-in real + klik "Create clarification
link" + klik "Revoke" + verifikasi lewat curl bahwa `GET /client/{token}`
sungguhan berubah dari 200 jadi 403 "This link has been revoked"). Test
baru: `test_freelancer_revoke_lewat_endpoint_bikin_link_403`,
`test_revoke_token_tidak_dikenal_404`,
`test_revoke_token_milik_run_lain_404` di `test_client_portal.py`.

Total **210 test hijau**. Commit `7ea2c06` (branch `rifqi`, di-push,
diverifikasi `gh api`).

---

## MILESTONE 26 Agu (lanjutan #3) — dua verifikasi tambahan sambil sisir 05-SUBMISSION-CHECKLIST.md

Instruksi Rifqi: "lanjut cek gap lain yang belum beres" — kali ini sisirnya
lewat `docs/05-SUBMISSION-CHECKLIST.md` §3 (pre-submit smoke test), bukan
`01-PRD.md`, cari item yang belum pernah benar-benar dites lewat endpoint
sungguhan (bukan cuma unit test domain murni).

1. **"Baseline version baru ... menandai criterion yang berubah sebagai
   SUPERSEDED"** — sebelumnya cuma dites di `test_domain.py` (fungsi murni
   `effective_status`), belum pernah dites lewat rantai endpoint v2 yang
   baru dibangun (`change-proposal` -> confirm). Dicoba manual lewat curl
   + token asli: criterion yang SUDAH `ACCEPTED` di v1, teksnya diubah
   lewat `change-proposal`, confirm jadi v2 -> `effective_status` benar
   balik jadi **SUPERSEDED** (bukan tetap ACCEPTED, bukan PENDING).
   Ditambah test permanen `test_v2_criterion_yang_teksnya_berubah_jadi_superseded`
   di `test_change_proposal.py`.
2. **Guardrail citation hint tidak lengkap** — `GuardrailPanel` di
   `page.tsx` menampilkan daftar ref+teks yang boleh dikutip SEBELUM
   freelancer mengisi citation, tapi sumbernya (`proof.criteria`) cuma
   berisi criterion, sedangkan `guardrail.citable_text()` (yang benar-benar
   memvalidasi citation di endpoint classify) JUGA menerima
   `out_of_scope[i]` dan `deliverables[i]`. Freelancer yang mau mengutip
   item out-of-scope tidak akan tahu format ref-nya sama sekali dari UI --
   citation-nya akan gagal validasi diam-diam (turun AMBIGUOUS) tanpa
   penjelasan. **Fix**: endpoint baru `GET /runs/{id}/citable-refs`
   (owner-only, 409 tanpa baseline) yang langsung mengembalikan hasil
   `guardrail.citable_text()` apa adanya -- satu-satunya sumber kebenaran
   yang sama dipakai baik untuk validasi maupun hint UI, tidak ada dua
   definisi yang bisa berbeda tipis. `page.tsx` diarahkan ke endpoint ini;
   type `ProofManifest` di `api.ts` jadi orphan (satu-satunya pemakainya
   dihapus) dan dibersihkan.

Dites lewat curl+token asli: `citable-refs` mengembalikan ketiga jenis ref
sekaligus (`mobile-breakpoints`, `out_of_scope[0]`, `deliverables[0]`).
Test baru: `test_citable_refs_meliputi_criterion_dan_out_of_scope` +
`test_citable_refs_tanpa_baseline_aktif_409` di `test_guardrail_endpoint.py`.

Total **207 test hijau**. Commit `de8dd4c` + `4579b10` (branch `rifqi`,
di-push, diverifikasi lewat `gh api` langsung ke GitHub bukan cuma git
lokal).

---

## MILESTONE 26 Agu (lanjutan) — retry ekstraksi manual, menutup gap yang sudah lama dicatat

Ini gap yang SUDAH dicatat sejak wiring `worker.py` ke Gemini (lihat item
13 "Gap yang diketahui" sebelumnya): `claim_job(run_id, round)` mengklaim
kunci `{run_id}__{round}` SEBELUM `run_extraction` dicoba. Kalau Gemini
gagal transient (503 "high demand", atau, seperti terbukti nyata di sesi
ini, 429 kuota habis), status ditulis jujur sebagai gagal -- **tapi round
itu tetap terkunci selamanya**. Karena tidak ada mekanisme lain yang
menaikkan `round`, run itu permanen macet di "Ekstraksi Gemini gagal"
tanpa jalan keluar selain bikin run baru dari nol (kehilangan brief-nya).

**Fix**: endpoint baru `POST /runs/{run_id}/retry-extraction`
(owner-only, 409 kalau baseline sudah ada -- retry cuma masuk akal
SEBELUM ledger dijadikan baseline v1). Ambil `run["round"]` (angka yang
terakhir kali BENAR-BENAR ditulis worker setelah memproses, bukan yang
di-publish API), `+1`, publish ulang. Kunci klaim untuk round baru belum
pernah ada, jadi worker memprosesnya dari nol -- bukan didrop sebagai
duplikat seperti kalau Pub/Sub redelivery round lama terjadi.

Frontend: tombol "Retry extraction" kecil di sebelah "Status: done",
muncul hanya kalau `status === "done" && !active_baseline_version`.

**Dites dengan Gemini ASLI** (bukan stub) lewat curl+token asli: run
pertama gagal beneran (429 kuota habis -- kebetulan reproduksi kondisi
paling realistis untuk fitur ini), `retry-extraction` -> round naik ke 2,
worker BENAR-BENAR memproses ulang (audit_trail bertambah entry baru
dengan timestamp baru, bukan di-drop), gagal lagi (kuota masih habis,
diharapkan) tapi terbukti prosesnya jalan dari awal, bukan macet. 409
setelah baseline dikonfirmasi juga terbukti benar.

Test: `tests/test_retry_extraction.py` (baru, 4 test, pakai `TestClient`
worker+api sungguhan, bukan cuma mock -- supaya `claim_job`/`round`
diuji lewat jalur yang sama persis dengan produksi). Total **204 test
hijau**. Commit `56588bf` (branch `rifqi`, di-push).

---

## MILESTONE 26 Agu — polling run yang 404/403 tidak pernah berhenti

Ditemukan sendiri (bukan dilaporkan Rifqi) selagi verifikasi manual auth
sebelumnya: kalau `localStorage` menyimpan `runId` yang basi -- run
kedaluwarsa, run milik owner lain (habis ganti akun sign-in), atau
sekadar tidak pernah ada -- `GET /runs/{id}` di `page.tsx` balas 404/403,
tapi `catch` di `poll()` menelan semua error tanpa pandang bulu dan
membiarkan `setInterval` jalan terus **setiap detik, selamanya**, dengan
UI diam-diam nyangkut di "Status: queued" tanpa pesan apa pun.

**Fix**: `api.ts` sekarang punya `class ApiError extends Error` yang
membawa `status` -- `apiFetch` melempar ini, bukan `Error` polos. `poll()`
di `page.tsx` membedakan 404/403 (permanen -- run memang bukan milik akun
ini atau sudah hilang) dari yang lain (transient -- retry jalan terus
seperti biasa): pada 404/403, `clearInterval`, `runId`/`run` di-reset
(otomatis membersihkan localStorage lewat effect yang sudah ada), dan
pesan error ditampilkan ("That run is no longer available...").

Dites lewat Chrome sungguhan: sign-in real (akun test REST, dihapus lagi
setelah selesai), suntik `runId` acak yang tidak pernah ada ke
localStorage, reload -- hasilnya pesan error tampil, `localStorage`
terbukti kosong lagi, tidak ada section "Run" nyangkut. Commit `b8e8871`
(branch `rifqi`, di-push).

---

## MILESTONE 25 Agu malam (lanjutan #4) — ledger field yang terekstrak tapi tidak pernah ditampilkan

Instruksi Rifqi: "fokus beresin BE dan FE nya saja dulu yang masih belum
beres" — sisir ulang PRD vs kode untuk cari gap nyata yang TIDAK diblokir
Gemini/billing.

**Temuan**: `app/domain/schemas.py: DealLedger` (dan ekstraksi Gemini di
`app/agent.py`, lihat instruksi field-nya) sudah lama punya empat field
`in_scope`, `dependencies`, `assumptions`, `unresolved_questions` — persis
disebut di 01-PRD §4 sebagai bagian "ledger minimum". Tapi
`web/src/app/client/[token]/page.tsx` (portal klien) TIDAK PERNAH
menampilkan atau membiarkan klien mengedit keempatnya — cuma
deliverables/acceptance_criteria/out_of_scope/timeline/revision_policy
yang ada UI-nya. Nilai yang berhasil diekstrak Gemini (atau yang mestinya
bisa diisi manual klien) diam-diam hilang dari pandangan pengguna.

**Fix**: seksi baru "Additional context" di bawah field kritis (bukan
readiness-gating, jadi sengaja dipisah visual dari field yang wajib) —
4 `ListField` baru pakai komponen yang sama persis dengan "Out of scope"
yang sudah ada. `web/src/lib/api.ts`: tipe `Ledger` ditambah keempat field
ini (`LedgerField<string[]>`). Tidak ada perubahan backend sama sekali --
`DealLedger` sudah menerima field ini sejak awal (`extra="forbid"` cuma
menolak nama field yang TIDAK dikenal, dan keempatnya sudah dikenal),
`readiness.evaluate` sudah benar tidak menganggapnya critical field.

Dites lewat curl (payload tersimpan & round-trip lewat `/client/{token}`)
DAN lewat Chrome sungguhan (nilai tampil benar di masing-masing input).
Commit `2916b4a` (branch `rifqi`, di-push).

---

## MILESTONE 25 Agu malam (lanjutan #3) — CHANGE_REQUEST -> baseline v2 selesai, dites end-to-end

Instruksi Rifqi: "lanjutkan yang belum beres ... fokus ke FE/BE yang belum
beres". Gap yang tersisa dari item 12 (Guardrail) — CHANGE_REQUEST yang
dikonfirmasi Guardrail belum bisa jadi baseline v2 sungguhan.

**Temuan penting**: endpoint `POST /client/{token}/confirm` **SUDAH
version-agnostic sejak awal** (`next_version = get_active_version + 1`) --
tidak perlu endpoint baru untuk "aktivasi v2". Yang benar-benar hilang cuma
dua hal:

1. **Bug di `build_canonical_payload`** (`app/domain/baseline.py`): selalu
   mencap SEMUA criterion dengan `introduced_in_version = version` yang
   sedang dibuat, termasuk criterion yang teksnya sama sekali tidak
   berubah dari versi sebelumnya. Melanggar 09 §2.6 A-7. **Fix**: parameter
   baru `previous_criteria` (canonical_payload.criteria dari baseline
   aktif) -- criterion dengan `text_hash` identik mempertahankan
   `introduced_in_version` aslinya, criterion baru/berubah dicap versi
   sekarang. `_next_baseline_preview` di `api.py` sekarang mengambil
   baseline aktif dan meneruskan `criteria`-nya.
2. **Tidak ada jalur bagi freelancer mengedit ledger setelah v1** --
   `apply_client_answer` cuma bisa dipanggil lewat client link. Endpoint
   baru `POST /runs/{run_id}/change-proposal` (owner-only, 409 tanpa
   baseline aktif): freelancer mengirim field ledger yang diusulkan
   (bentuk sama persis dengan `/client/{token}/answers`), state jadi
   `FREELANCER_POLICY` (bukan `CLIENT_STATED`), audit event
   `CHANGE_PROPOSED` (enum ini sudah lama dicadangkan di `enums.py`,
   belum pernah dipakai). `app/domain/ledger.py`:
   `apply_client_answer(..., state=CLIENT_STATED)` sekarang punya
   parameter `state` supaya bisa dipakai ulang untuk kedua kasus.

**Alur produk lengkapnya** (tidak ada UI diff/impact visual -- itu tetap
di luar cakupan per keputusan awal, lihat "Sengaja belum" di 01-PRD §5
langkah 8): request masuk lewat Guardrail -> freelancer classify jadi
CHANGE_REQUEST -> freelancer buka panel baru "Propose a scope change" di
dashboard, tambah criterion baru untuk request itu -> `change-proposal`
menyimpan usulan ke ledger -> freelancer bikin clarification link BARU
(tombol yang sama persis dengan v1) -> klien buka link, lihat ledger yang
sudah terisi (termasuk criterion lama), "Confirm project plan" -> baseline
v2 aktif lewat endpoint yang SAMA dengan v1.

**Frontend**: `ChangeProposalPanel` baru di `page.tsx` (tampil kalau
`hasBaseline`) -- form deliverable_id/criterion_key/text, "Propose
change" -> `change-proposal` lalu langsung bikin clarification link baru
dan menampilkan URL-nya. Tipe `Run` ditambah `ledger?: Ledger` (ternyata
`GET /runs/{id}` SUDAH mengembalikan ledger mentah sejak awal, cuma
belum dipetakan di tipe TypeScript-nya).

**Dites end-to-end DUA kali** (backend via curl dengan token Firebase asli,
DAN lewat UI browser sungguhan dengan akun asli Rifqi yang sudah sign-in):
criterion `mobile-breakpoints` yang sudah `ACCEPTED` di v1 (teks tidak
berubah) di v2 tetap `introduced_in_version: 1` DAN status `ACCEPTED`
bertahan (09 A-8: naik versi tidak mengubah status apa pun); criterion baru
`hero-video` muncul `introduced_in_version: 2`, status `PENDING`. Sesuai
persis test vector A-T2 dan A-T7.

Catatan proses: dua kali sempat salah diagnosis --  (1) klik tombol lewat
`computer` tool (koordinat/screenshot) sempat tidak konsisten mendaftarkan
klik/ketik di form ini (gotcha lama, lihat memory `gotcha-chrome-tool-
coordinate-scaling`) -- diatasi dengan `javascript_tool` men-set value
lewat native setter + dispatch event `input`, jauh lebih reliable untuk
form React di sesi ini; (2) server API/worker yang jalan di background
sempat berumur lebih tua dari kode terbaru (tidak pakai `--reload`) --
hasil test pertama salah (endpoint 404, `introduced_in_version` tidak
terlindungi) semata gara-gara proses lama, bukan bug -- **restart
server setiap kali `app/` berubah sebelum verifikasi manual lagi.**

Test: `tests/test_baseline.py` (+3), `tests/test_change_proposal.py` (baru,
3). Total **200 test hijau**. Commit `88a964d` (branch `rifqi`, di-push).

---

## MILESTONE 25 Agu malam (lanjutan) — UI New Request (Guardrail) selesai, dites end-to-end di browser

Instruksi Rifqi: "lanjut ke auth dan New Request UI" — New Request UI
dikerjakan duluan (backend-nya sudah lengkap dari item 12, tinggal UI),
Firebase auth menyusul setelah ini.

- `web/src/lib/api.ts` — tambah tipe `Citation`, `ScopeRequest`,
  `ProofManifest`.
- `web/src/app/page.tsx` — `GuardrailPanel` (di dalam `FreelancerActions`,
  hanya tampil kalau `hasBaseline`): textarea "What did the client ask for?"
  + "Log request" -> `POST /runs/{id}/requests`; daftar `RequestCard` per
  request. Request yang belum diklasifikasi tampilkan select
  IN_SCOPE/AMBIGUOUS/CHANGE_REQUEST + daftar `citableRefs` (hint, bukan
  input) + `CitationList` (editor ref/quote tambah-hapus, mulai kosong) +
  "Confirm classification" -> `POST .../requests/{id}/classify`. Request
  yang sudah diklasifikasi jadi ringkasan read-only (classification +
  citations).
- Lolos `tsc --noEmit`, `eslint`, `next build`.
- **Dites lewat Chrome sungguhan** (run `c7f094744f2645949aded9b4dc2f029e`,
  baseline v1 aktif dengan criterion `mobile-breakpoints`): (1) log request
  tanpa citation, pilih IN_SCOPE, confirm TANPA mengisi `CitationList` ->
  hasil **AMBIGUOUS** (02 §4.5, sesuai desain — citable-refs hint yang
  tampil bukan citation yang otomatis terpasang, harus diisi manual lewat
  "+ add citation"); (2) log request kedua, pilih CHANGE_REQUEST, isi
  citation `mobile-breakpoints` dengan quote verbatim persis dari baseline,
  confirm -> hasil **tetap CHANGE_REQUEST**, citation tampil di ringkasan.
  Kedua jalur (tanpa kutipan valid vs dengan kutipan valid) terbukti benar
  sesuai domain rule.
- Commit `7facf8f` (branch `rifqi`, sudah di-push ke remote `delividence`,
  commit message dicek dulu — bersih dari atribusi tooling).
- Test suite backend tetap **189 hijau** (perubahan ini frontend-only, tidak
  menyentuh backend).
- **Belum dikerjakan**: model (Gemini) mengusulkan classification+citation
  otomatis untuk Guardrail — masih manual/freelancer-driven, sama seperti
  dicatat di item 12/14 di bawah.

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
6. ~~**Sambungkan `agent.py` ke `worker.py`.**~~ **CATATAN INI USANG —
   sudah selesai dan terverifikasi sukses lewat Gemini Developer API**
   (bukan lagi diblokir billing GCP, lihat MILESTONE 25 Agu malam paling
   atas dan blocker #1 di bawah: pindah ke Gemini Developer API). Baris
   ini sengaja dibiarkan sebagai jejak sejarah, jangan dikerjakan ulang —
   `app/worker.py: run_extraction()` sudah jalan pakai `gemini-3.6-flash`.
   `questions.rank_questions()` belum disambungkan ke worker (belum ada
   UI yang menampilkan pertanyaan terrank) — dicatat apa adanya, bukan
   prioritas karena readiness gate & clarification portal sudah menutup
   kebutuhan intinya tanpa itu.
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
    AMBIGUOUS/CHANGE_REQUEST).~~ **Selesai penuh, 26 Agu** — bagian
    deterministik (di bawah) dari sesi awal, bagian model
    (`agent.guardrail_agent`, lihat MILESTONE 26 Agu lanjutan #7 di atas)
    menyusul setelah ekstraksi Gemini terbukti sukses sungguhan. Validasi
    & keputusan akhir tetap selalu deterministik di sini — usulan model
    lewat tempat yang sama persis, tidak ada jalur pintas baru.
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
      bentuk data 02 §6 sengaja tidak ada — tidak ada foreign key eksplisit
      dari scope_request ke baseline v2 yang dihasilkannya; keterkaitannya
      tetap terlihat lewat urutan audit log (REQUEST_SUBMITTED ->
      SCOPE_CLASSIFICATION_DECIDED -> CHANGE_PROPOSED -> BASELINE_APPROVED/
      ACTIVATED), bukan lewat kolom tersendiri. Cukup untuk MVP, jangan
      ditambah tanpa alasan baru.
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
    - ~~**Sengaja belum**: model benar-benar mengusulkan
      classification+citation (butuh Gemini, sama seperti item 6).~~
      **SELESAI, 26 Agu** — `agent.guardrail_agent` +
      `propose_classification`, lihat MILESTONE 26 Agu (lanjutan #7) di
      atas. CHANGE_REQUEST -> baseline v2 **SELESAI** duluan, lihat
      MILESTONE 25 Agu malam (lanjutan #3) di atas.
13. ~~**Wiring `worker.py` ke `agent.extraction_agent`, Gemini sungguhan.**~~
    **SELESAI, benar-benar sukses ekstraksi sungguhan, 26 Agu** — root
    cause kegagalan sebelumnya BUKAN kuota/demand seperti dugaan awal,
    tapi `backend/.env` yang tidak pernah ke-load sama sekali (proyek ini
    tidak punya `load_dotenv()` di kode manapun). Fix: jalankan uvicorn
    dengan `--env-file .env`, lihat MILESTONE 26 Agu (lanjutan #7) untuk
    command lengkapnya. Catatan lama di bawah ini (soal 503 "high demand")
    dibiarkan sebagai jejak sejarah — itu observasi asli sebelum root
    cause sebenarnya ketemu, bukan diagnosis final.
    - `app/worker.py`: `run_extraction(run_id, brief)` — `InMemoryRunner`
      + `session_service.create_session(state={"artifacts": {...}})` +
      `run_async(new_message=...)`, baca `ledger_draft` dari
      `session.state` setelah run selesai. Dipanggil dari `push()`,
      dibungkus `try/except` supaya kegagalan Gemini (503 dll) tidak
      menjatuhkan worker — status tetap ditulis jujur ("Ekstraksi Gemini
      gagal"), bukan diam-diam dianggap sukses kosong.
    - ~~**Gap yang diketahui**: round yang gagal karena Gemini transient
      tidak otomatis di-retry.~~ **SELESAI, 26 Agu** — lihat MILESTONE 26
      Agu "retry ekstraksi manual" di atas. `claim_job` memang tetap
      mengklaim round SEBELUM ekstraksi dicoba (arsitektur idempotency-nya
      tidak diubah), tapi sekarang ada `POST /runs/{id}/retry-extraction`
      yang menerbitkan round BARU (bukan mengandalkan redelivery Pub/Sub
      di round lama) — freelancer memicu sendiri, bukan otomatis, dan itu
      cukup: kegagalan Gemini transient bukan kejadian yang perlu retry
      background tanpa sepengetahuan freelancer.
    - `tests/conftest.py`: fixture `stub_extraction` (autouse) — semua 189
      test TIDAK memanggil Gemini sungguhan (cepat, deterministik, tidak
      butuh API key). Wiring sungguhan hanya diverifikasi manual.
    - ~~**Coba lagi nanti**: jalankan ulang verifikasi manual ... begitu
      demand `gemini-3.7-flash` mereda ...~~ **Sudah, 26 Agu** — lihat di
      atas, ternyata bukan soal demand model.
14. ~~Baru setelah ini semua sukses sekali secara nyata: perluas `agent.py`
    untuk juga mengusulkan classification Guardrail (item 12), bukan cuma
    ekstraksi ledger.~~ **SELESAI, 26 Agu** — lihat item 12 dan MILESTONE
    26 Agu (lanjutan #7) di atas.

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

### GEMINI_API_KEY — status: SELESAI TOTAL, ekstraksi & Guardrail sukses sungguhan (26 Agu)

~~1. Isi GEMINI_API_KEY~~ **selesai** — key digenerate dari akun Google lain
(akun pertama, `rifqiahmad234a@gmail.com`, sempat gagal "request is
suspicious" 2x waktu generate key; akun kedua berhasil). Ada di
`backend/.env` (gitignored, tidak ke-commit).

~~2. Wiring worker.py~~ **selesai, dan sekarang benar-benar sukses
memanggil Gemini, lihat item 13 & MILESTONE 26 Agu (lanjutan #7) di
atas** — kegagalan sebelumnya bukan 503 dari Google, tapi
`backend/.env` yang tidak pernah ke-load oleh proses Python sama sekali
(tidak ada `load_dotenv()` di kode manapun). Jalankan `uvicorn` dengan
`--env-file .env` dan panggilan Gemini sungguhan langsung jalan, baik
untuk ekstraksi ledger maupun classification Guardrail.

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
