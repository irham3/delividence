# Delividence — backend

FastAPI + Google ADK. Freelancer submit brief mentah → Gemini ekstrak jadi
deal ledger bersitasi → klien konfirmasi lewat portal token (tanpa akun) →
baseline versi tersimpan → Guardrail (Gemini lagi) klasifikasi setiap
scope request baru → delivery review → Proof Manifest. Lihat `docs/` untuk
spesifikasi domain lengkap.

## Satu image, dua service

`ROLE` menentukan app mana yang di-serve dari image yang sama:

| `ROLE` | App | Contoh endpoint |
|---|---|---|
| `api` (default) | `app.api` | `GET /health`, `POST /runs`, `GET/POST /client/{token}/...`, `POST /runs/{id}/requests` |
| `worker` | `app.worker` | `GET /health`, `POST /pubsub/push` |

Ini yang membuat `delividence-api` dan `delividence-worker` bisa di-deploy dari satu
sumber tanpa keduanya boot app yang sama. Daftar endpoint lengkap ada di
`app/api.py` — terlalu banyak untuk dicantumkan semua di sini (client-links,
evidence, change-proposal, retry-extraction, citable-refs, dst).

## Setup `.env`

```powershell
Copy-Item .env.example .env
```

Isi minimal untuk fitur inti benar-benar jalan (bukan cuma antrean kosong):

- `GEMINI_API_KEY` — dari https://aistudio.google.com/apikey, punya kamu
  sendiri, gratis tanpa kartu. Tanpa ini, ekstraksi & Guardrail akan gagal
  dengan pesan jujur di `audit_trail`, bukan crash diam-diam.
- `FIREBASE_PROJECT_ID` — proyek Firebase dengan Google Sign-In aktif.
  **Wajib diisi kalau mau tes endpoint owner** (`POST /runs` dst) — lihat
  bagian Auth di bawah. Boleh dikosongkan kalau cuma menyentuh
  `/client/{token}/...` (portal klien, tidak butuh akun sama sekali).

`GOOGLE_CLOUD_PROJECT` boleh tetap kosong untuk mode lokal (lihat di bawah) —
ini terpisah dari dua variabel di atas.

**Jangan pakai/minta `GEMINI_API_KEY` atau kredensial Firebase/GCP milik
rekan tim untuk kerja lokal.** Tiap developer generate key Gemini sendiri
(gratis, tanpa kartu) supaya kuota terpisah, dan boleh pakai project
Firebase sendiri untuk tes auth lokal — tidak perlu minta akses ke project
produksi siapa pun. Kredensial project produksi (kalau ada yang sudah
di-deploy) tidak pernah dibutuhkan untuk kerja lokal sama sekali.

## Mode lokal

Tanpa `GOOGLE_CLOUD_PROJECT`, backend jalan lokal: antrean lewat HTTP langsung ke
worker, state ke file JSON di `.localdata/`. Bentuk envelope dan semantik klaim
job dibuat identik dengan produksi, jadi handler yang diuji lokal adalah handler
yang sama yang dipakai di Cloud Run. Ini **tidak memengaruhi** Gemini atau
Firebase Auth — keduanya layanan hosted yang selalu dipanggil sungguhan,
lokal maupun produksi.

```powershell
python -m venv ..\.venv
..\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt

# terminal 1 — worker
$env:ROLE = "worker"
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8081 --env-file .env

# terminal 2 — api
$env:ROLE = "api"; $env:WORKER_URL = "http://127.0.0.1:8081"
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --env-file .env
```

`--env-file .env` wajib di kedua terminal — tanpa itu `.env` tidak pernah
terbaca sama sekali (tidak ada `load_dotenv()` di kode manapun, ini
disengaja: uvicorn CLI sudah punya flag bawaan untuk itu).

## Auth untuk tes lokal

`POST /runs` dan endpoint owner lain butuh `Authorization: Bearer <Firebase
ID token>` — bukan token sembarangan, harus asli dari project di
`FIREBASE_PROJECT_ID`. Dua cara dapat token untuk tes manual:

1. **Lewat frontend** (`web/`) — sign in dengan Google, buka DevTools →
   Network, salin header `Authorization` dari request mana pun ke API.
2. **Lewat REST langsung** (tanpa browser) — aktifkan provider
   Email/Password *sementara* di Firebase Console project kamu, lalu:
   ```powershell
   curl.exe -s -X POST "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=<WEB_API_KEY>" `
     -H "Content-Type: application/json" `
     -d "{\"email\":\"test@example.com\",\"password\":\"Test1234!\",\"returnSecureToken\":true}"
   ```
   `idToken` di response itu yang dipakai sebagai Bearer token. Matikan
   lagi provider Email/Password setelah selesai, dan hapus user tesnya
   (`accounts:delete`) — jangan tinggalkan aktif di project produksi.

Verifikasi (pakai `curl.exe`, bukan alias `curl` bawaan PowerShell):

```powershell
$TOKEN = "<idToken dari salah satu cara di atas>"
curl.exe -s http://127.0.0.1:8080/health
curl.exe -s -X POST http://127.0.0.1:8080/runs -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "{\"brief\":\"need an edit for our IG content\"}"
curl.exe -s http://127.0.0.1:8080/runs/<run_id> -H "Authorization: Bearer $TOKEN"
```

Run yang berhasil berubah `queued → processing → done` **tanpa** request kedua.
Kalau `GEMINI_API_KEY` terisi benar, `audit_trail` akan berisi baris
"Brief diekstrak lewat Gemini -- N field ledger terisi." dan `ledger` di
response terisi dengan kutipan verbatim dari brief.

## Nyambung backend lokal ke Firestore/Pub-Sub produksi (opsional)

Kalau butuh backend lokal baca/tulis data produksi sungguhan (bukan cuma
mode LOCAL file JSON) — misal debug data asli — isi `GOOGLE_CLOUD_PROJECT`
di `.env` dengan project ID produksi. Konsekuensinya:

- **`GOOGLE_CLOUD_PROJECT` boleh sama** dengan production, tapi
  **`GEMINI_API_KEY` tetap harus punya sendiri** (lihat larangan di atas).
- Butuh IAM role `roles/datastore.user` + `roles/pubsub.editor` di project
  itu, minta owner project untuk grant ke akun Google kamu.
- Subscription push yang sudah ada tetap mengirim job ke Cloud Run worker
  seperti biasa — job tidak otomatis mampir ke worker lokal kamu.
- Untuk worker lokal ikut kebagian job, jalankan
  `local_pubsub_forwarder.py` di terminal ketiga, dengan subscription pull
  **milikmu sendiri** (jangan pakai punya developer lain, nanti rebutan
  pesan alih-alih dapat salinan masing-masing):

  ```powershell
  gcloud pubsub subscriptions create delividence-runs-local-pull-<nama-kamu> `
    --topic=delividence-runs --project=<PROJECT_ID>

  $env:GOOGLE_CLOUD_PROJECT = "<PROJECT_ID>"
  $env:LOCAL_PULL_SUBSCRIPTION_ID = "delividence-runs-local-pull-<nama-kamu>"
  ..\.venv\Scripts\python.exe local_pubsub_forwarder.py
  ```

  Job akan diproses **dua kali** (Cloud Run + worker lokalmu) — ini
  disengaja, bukan bug, keduanya independen lewat subscription terpisah.

## Deploy ke Cloud Run

Lihat `../deploy/01-setup-gcp.ps1` (provision Firestore/Pub-Sub/service
account) dan `../deploy/02-deploy.ps1` (deploy API + worker, wiring
CORS/Firebase/secret Gemini). Kedua script idempotent, aman dijalankan
ulang.

## Test

```powershell
..\.venv\Scripts\python.exe -m pytest -q
```

## Keputusan yang sudah tertanam di kode

- **Idempotensi** ditegakkan dokumen job create-only berkunci `{run_id}:{round}`
  (`store.claim_job`), bukan field `idempotency_key`. Pub/Sub at-least-once, jadi
  pengiriman ganda pasti terjadi. Kunci menyertakan `round` supaya jawaban klien
  di putaran berikutnya tidak ikut tertekan sebagai duplikat.
- **Pesan rusak permanen di-ack** (`204`), tidak diulang selamanya. Yang layak
  diulang adalah kegagalan sementara — itu urusan retry + dead-letter topic.
- **`output_language` default `en`.** Aturan hackathon mewajibkan aplikasi
  mendukung bahasa Inggris minimal; Bahasa Indonesia adalah pilihan tambahan.
- **Jejak audit menyimpan keputusan dan hasil tool**, bukan prompt atau reasoning
  mentah.
