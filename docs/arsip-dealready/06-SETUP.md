# 06 — Setup dari Nol

Untuk menyiapkan project di komputer lain atau di mesin partner.

> **Status per 25 Agustus 2026 — sebagian sudah diverifikasi.**
>
> | Bagian | Status |
> |---|---|
> | Backend lokal (§5, §8) | **Terverifikasi.** 10 test hijau, dua service nyata jalan di 8080/8081. Langkah persisnya ada di [`backend/README.md`](../backend/README.md) |
> | Setup & deploy Google Cloud (§3, §7) | **Digantikan skrip**, lihat kotak di bawah. Belum pernah dijalankan — menunggu billing aktif |
> | Frontend (§6) | Belum ada kodenya |

> ### §3 dan §7 sekarang dijalankan lewat skrip, bukan disalin manual
>
> - [`deploy/01-setup-gcp.ps1`](../deploy/01-setup-gcp.ps1) — aktifkan API
>   (**termasuk Cloud Build**, yang wajib untuk `gcloud run deploy --source` dan
>   tidak ada di §3), Firestore, Artifact Registry, tiga service account dengan
>   hak minimum, topic + **dead-letter topic**, dan binding untuk service agent
>   Pub/Sub yang tanpa itu membuat dead-letter gagal diam-diam.
> - [`deploy/02-deploy.ps1`](../deploy/02-deploy.ps1) — deploy worker dulu (URL-nya
>   dibutuhkan subscription), binding `roles/run.invoker`, push subscription
>   dengan **OIDC + ack deadline 60 detik + retry policy + dead-letter**, baru
>   deploy API.
>
> **Bug di §7 sudah diperbaiki di kode, bukan cuma dicatat:** di sana
> `dealready-api` dan `dealready-worker` sama-sama di-deploy dari
> `--source ./backend` tanpa pemilih entrypoint, jadi kedua service akan boot app
> yang sama. Sekarang ada env `ROLE=api|worker` yang menentukannya, plus
> `Dockerfile` supaya build-nya deterministik.
>
> API di-deploy `--allow-unauthenticated`: aturan mewajibkan juri bisa mengakses
> project tanpa restriksi ([`09`](09-KEPUTUSAN-DAN-VERIFIKASI.md) V-7). Worker
> tertutup, hanya identitas push Pub/Sub yang boleh memanggilnya.

---

## 1. Prasyarat

| Kebutuhan | Versi | Cek |
|---|---|---|
| Python | 3.11 (dipakai & diuji; image `python:3.11-slim`) | `python --version` |
| Node.js | 20+ | `node --version` |
| pnpm | terbaru | `pnpm --version` |
| Google Cloud SDK | terbaru | `gcloud --version` |
| Git | mana saja | `git --version` |
| Akun Google Cloud | dengan billing aktif | Cek di console |

Shell yang diasumsikan: **PowerShell di Windows 11**. Untuk macOS/Linux, ganti
`$env:NAMA = "nilai"` menjadi `export NAMA="nilai"`.

## 2. Ambil kode

```powershell
git clone <URL-REPO>
cd dealready
```

`[verifikasi]` URL repo diisi setelah repo dibuat (Hari 1).

## 3. Setup Google Cloud

Sekali per project, bukan per mesin.

```powershell
# Login dan pilih project
gcloud auth login
gcloud config set project <PROJECT_ID>

# Aktifkan API yang dibutuhkan
gcloud services enable `
  run.googleapis.com `
  pubsub.googleapis.com `
  firestore.googleapis.com `
  secretmanager.googleapis.com `
  artifactregistry.googleapis.com

# Firestore mode Native
gcloud firestore databases create --location=asia-southeast2

# Topic Pub/Sub
gcloud pubsub topics create dealready-runs
```

Push subscription dibuat **setelah** worker ter-deploy, karena butuh URL-nya —
lihat bagian 7.

`[verifikasi]` Region `asia-southeast2` (Jakarta) dipilih karena dekat pengguna.
Pastikan seluruh layanan memakai region yang konsisten.

### Kredensial untuk pengembangan lokal

```powershell
gcloud auth application-default login
```

Ini membuat kode lokal bisa mengakses Firestore dan Pub/Sub memakai identitasmu,
tanpa perlu file service account key. **Jangan pernah men-download service
account key ke laptop** — itu kredensial jangka panjang yang gampang bocor lewat
commit.

## 4. Secret

```powershell
# Simpan API key Gemini
"NILAI_API_KEY_ANDA" | gcloud secrets create gemini-api-key --data-file=-
```

Untuk lokal, boleh memakai file `.env` yang **tidak** di-commit:

```
GEMINI_API_KEY=...
GEMINI_MODEL=...          # [verifikasi] ID model Gemini 3.5+ yang benar
GCP_PROJECT_ID=...
PUBSUB_TOPIC=dealready-runs
FIREBASE_PROJECT_ID=...
ENVIRONMENT=development
```

Pastikan `.env` ada di `.gitignore` **sebelum** commit pertama, bukan sesudah.

## 5. Backend lokal

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# API
uvicorn main:app --reload --port 8000
```

Worker dijalankan sebagai proses terpisah di terminal lain:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn worker:app --reload --port 8001
```

Verifikasi:

```powershell
curl http://localhost:8000/health
```

## 6. Frontend lokal

```powershell
cd frontend
pnpm install
pnpm run dev
```

Butuh file `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
```

Buka `http://localhost:3000`.

## 7. Deploy ke Google Cloud

```powershell
# Build dan deploy API
gcloud run deploy dealready-api `
  --source ./backend `
  --region asia-southeast2 `
  --allow-unauthenticated `
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest

# Build dan deploy worker (TIDAK boleh publik)
gcloud run deploy dealready-worker `
  --source ./backend `
  --region asia-southeast2 `
  --no-allow-unauthenticated `
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest

# Build dan deploy frontend
gcloud run deploy dealready-web `
  --source ./frontend `
  --region asia-southeast2 `
  --allow-unauthenticated
```

Setelah worker punya URL, buat push subscription dengan OIDC:

```powershell
gcloud pubsub subscriptions create dealready-runs-push `
  --topic dealready-runs `
  --push-endpoint "https://<URL-WORKER>/pubsub/push" `
  --push-auth-service-account "<SERVICE_ACCOUNT_EMAIL>"
```

**Worker harus `--no-allow-unauthenticated`.** Kalau endpoint worker terbuka ke
publik, siapa pun bisa memicu run dan membakar kuota Gemini — dan itu cacat
security yang akan terlihat oleh juri.

## 8. Test

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -q
```

Semua harus hijau sebelum commit. Salin ringkasan hasilnya ke README.

## 9. Masalah yang kemungkinan besar muncul

Diisi dan dikoreksi **sambil jalan** — bagian ini justru yang paling berguna
untuk partner dan untuk juri.

| Gejala | Kemungkinan penyebab |
|---|---|
| Push subscription mengembalikan 403 | Service account belum punya role `roles/run.invoker` di service worker |
| Worker memproses satu brief dua kali | Idempotensi belum ditegakkan; Pub/Sub menjamin *at-least-once* |
| Firestore menolak dari lokal | `gcloud auth application-default login` belum dijalankan |
| Model menolak / nama model salah | `[verifikasi]` ID model Gemini 3.5+ belum dikonfirmasi ke dokumentasi resmi |
| Deploy Cloud Run gagal saat build | Dockerfile atau deteksi buildpack; cek log build di console |

## 10. Pembagian kerja kalau berdua

Kalau project dikerjakan berdua, ini pembagian dengan tabrakan paling sedikit:

| Orang | Wilayah |
|---|---|
| A | Agent (ADK, tool, loop, trace) + aturan deterministik + test |
| B | Infrastruktur GCP + endpoint API + frontend + video |

Kontrak antar keduanya adalah **bentuk dokumen Firestore** di
[`02-ARCHITECTURE.md`](02-ARCHITECTURE.md) bagian 5. Sepakati itu di Hari 1 dan
jangan diubah sepihak — kalau berubah, dua-duanya harus tahu di hari yang sama.
