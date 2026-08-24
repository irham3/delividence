# 06 — Setup dari Nol

Untuk menyiapkan project di komputer lain atau di mesin partner.

> **Status: belum diverifikasi.** Belum ada kode, jadi belum ada satu perintah
> pun di dokumen ini yang pernah dijalankan. Ini rencana setup, bukan panduan
> teruji. **Saat kode benar-benar ada, dokumen ini harus diuji ulang dari mesin
> bersih dan dikoreksi** — lalu isinya disalin ke README repo, karena juri
> menilai reproducibility.

---

## 1. Prasyarat

| Kebutuhan | Versi | Cek |
|---|---|---|
| Python | 3.12+ | `python --version` |
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
