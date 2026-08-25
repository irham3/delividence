# 06 — Setup Lokal dan Google Cloud

Dokumen ini adalah target spin-up untuk codebase yang akan dibangun. Setiap command wajib diuji dan diperbaiki di README implementasi sebelum submission; jangan mengklaim setup reproducible sebelum tes dari environment bersih.

## 1. Prasyarat

- Node.js 20+ dan npm/pnpm.
- Python 3.12+.
- Docker.
- Google Cloud CLI terbaru.
- Google Cloud project dengan billing aktif.
- Firebase project yang terhubung ke Google Cloud project untuk owner authentication.

Rencana direktori:

```text
apps/web/             Next.js UI
services/api/         FastAPI public API
services/worker/      FastAPI private Pub/Sub target + Google ADK
shared/schemas/       WAJIB: source of truth schema, enum, dan event contracts
infra/                deploy scripts/notes
tests/fixtures/       golden brief, screenshot, injection cases
```

## 2. Environment variables

Gunakan placeholders di `.env.example`; jangan commit nilai nyata.

| Variable | Service | Isi |
|---|---|---|
| `GOOGLE_CLOUD_PROJECT` | API/worker | project ID |
| `GOOGLE_CLOUD_LOCATION` | worker | region model/Vertex AI |
| `GOOGLE_GENAI_USE_VERTEXAI` | worker | wajib `TRUE`; mencegah fallback ke Gemini Developer API/API key |
| `GEMINI_MODEL` | worker | target `gemini-3.5-flash`, setelah diverifikasi |
| `PUBSUB_TOPIC` | API | `scope-events` |
| `STORAGE_BUCKET` | API/worker | bucket artifact |
| `WEB_ORIGIN` | API | hosted web origin untuk CORS |
| `API_BASE_URL` | web | hosted/local API URL |
| `FIREBASE_PROJECT_ID` | web/API | Firebase project ID |
| `NEXT_PUBLIC_FIREBASE_*` | web | public Firebase web config; bukan secret |

Cloud Run memakai Application Default Credentials melalui service account. Hindari long-lived service-account key dan jangan menaruh Gemini/API key di client.

## 3. Local bootstrap

PowerShell example setelah code tersedia:

```powershell
gcloud auth login
gcloud auth application-default login
gcloud config set project PROJECT_ID

Set-Location apps/web
npm install
Copy-Item .env.example .env.local
npm run dev
```

Di terminal kedua:

```powershell
Set-Location services/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8081
```

Di terminal ketiga:

```powershell
Set-Location services/worker
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8082
```

Untuk local-only iteration, API dapat memanggil worker test endpoint yang hanya aktif saat `ENV=local`; hosted demo wajib melewati Pub/Sub.

## 4. Provision Google Cloud

Tetapkan satu region yang kompatibel dengan Cloud Run dan model. Contoh di bawah memakai placeholders:

```powershell
$ScopeProject = "PROJECT_ID"
$ScopeRegion = "REGION"
$ScopeBucket = "$ScopeProject-scopehandshake"

gcloud config set project $ScopeProject
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com firestore.googleapis.com pubsub.googleapis.com storage.googleapis.com aiplatform.googleapis.com logging.googleapis.com

gcloud firestore databases create --location=$ScopeRegion --type=firestore-native
gcloud pubsub topics create scope-events
gcloud storage buckets create "gs://$ScopeBucket" --location=$ScopeRegion --uniform-bucket-level-access
gcloud artifacts repositories create scopehandshake --repository-format=docker --location=$ScopeRegion
```

Jika Firestore database/repository/bucket sudah ada, command create boleh gagal dengan “already exists”; verifikasi konfigurasi, jangan membuat resource duplikat.

## 5. Service accounts dan IAM minimum

```powershell
gcloud iam service-accounts create scope-api
gcloud iam service-accounts create scope-worker
gcloud iam service-accounts create scope-pubsub-invoker
```

Target role:

| Principal | Role minimum |
|---|---|
| `scope-api` | Datastore User, Pub/Sub Publisher, Storage Object User |
| `scope-worker` | Datastore User, Vertex AI User, Storage Object Viewer |
| `scope-pubsub-invoker` | Cloud Run Invoker pada worker saja |

Berikan role pada resource paling sempit yang didukung. Hindari Editor/Owner pada runtime account. Pub/Sub service agent mungkin memerlukan Service Account Token Creator untuk membuat OIDC token; ikuti documented push-auth setup dan catat command final di README.

## 6. Firebase Auth

1. Hubungkan Firebase ke `PROJECT_ID`.
2. Aktifkan satu provider untuk owner demo, idealnya Google Sign-In.
3. Tambahkan localhost dan hosted web domain ke authorized domains.
4. Web mengirim Firebase ID token sebagai Bearer token.
5. API memverifikasi token dan mengambil `uid`; jangan percaya `owner_id` dari request body.

Client tidak memakai Firebase Auth. Client memakai opaque token yang scope/expiry/purpose-nya diverifikasi oleh API.

## 7. Build dan deploy

Build image terpisah agar entrypoint tidak tertukar:

```powershell
$ScopeProject = "PROJECT_ID"
$ScopeRegion = "REGION"
$ScopeRepo = "$ScopeRegion-docker.pkg.dev/$ScopeProject/scopehandshake"

gcloud builds submit services/api --tag "$ScopeRepo/api:latest"
gcloud builds submit services/worker --tag "$ScopeRepo/worker:latest"
gcloud builds submit apps/web --tag "$ScopeRepo/web:latest"

gcloud run deploy scope-api --image "$ScopeRepo/api:latest" --region $ScopeRegion --service-account "scope-api@$ScopeProject.iam.gserviceaccount.com" --allow-unauthenticated
gcloud run deploy scope-worker --image "$ScopeRepo/worker:latest" --region $ScopeRegion --service-account "scope-worker@$ScopeProject.iam.gserviceaccount.com" --no-allow-unauthenticated
gcloud run deploy scope-web --image "$ScopeRepo/web:latest" --region $ScopeRegion --allow-unauthenticated
```

API perlu dapat diakses publik karena browser owner/client memanggilnya, tetapi application authorization tetap wajib pada setiap route. Worker tidak boleh public.

Setelah worker URL tersedia:

```powershell
$WorkerUrl = gcloud run services describe scope-worker --region $ScopeRegion --format="value(status.url)"
$Invoker = "scope-pubsub-invoker@$ScopeProject.iam.gserviceaccount.com"

gcloud run services add-iam-policy-binding scope-worker --region $ScopeRegion --member="serviceAccount:$Invoker" --role="roles/run.invoker"
gcloud pubsub subscriptions create scope-worker-push --topic=scope-events --push-endpoint="$WorkerUrl/events/pubsub" --push-auth-service-account=$Invoker
```

Set Cloud Run environment variables menggunakan `gcloud run services update --set-env-vars` atau deployment configuration; jangan memakai hard-coded project/URL.

## 8. Verification commands

```powershell
gcloud run services list --region $ScopeRegion
gcloud pubsub subscriptions describe scope-worker-push
gcloud logging read 'resource.type="cloud_run_revision"' --limit=20
npm --prefix apps/web test
python -m pytest services/api/tests services/worker/tests
```

Manual integration checks:

1. Create deal sebagai owner.
2. Submit golden brief dan tunggu job complete.
3. Buka client link di incognito.
4. Submit response dan temukan job ID yang sama di Cloud Logging/Firestore.
5. Pada client UI tekan **Confirm project plan**; verifikasi event internal `BASELINE_APPROVED` lalu `BASELINE_ACTIVATED` dan simpan hash.
6. Create change request; pastikan hash baseline lama tetap sama.
7. Add evidence dan lakukan client acceptance.

## 9. Demo/judge environment

- Seed hanya synthetic data; tidak memakai client nyata.
- Seed command wajib memakai domain service/event writer, bukan direct Firestore mutation.
- Untuk video drift beat, seed membuat tepat empat valid `SCOPE_CLASSIFICATION_DECIDED` berklasifikasi `IN_SCOPE` setelah baseline aktif. Request kelima tetap dilakukan live agar derived counter berubah 4 → 5.
- Judge owner account memiliki credentials yang aman dan dibagikan hanya lewat testing instructions.
- Dedicated client link punya expiry melewati judging, scope minimum, dan synthetic deal saja.
- Cloud Run minimum instances 0 untuk biaya, kecuali cold start merusak demo; bila menaikkan minimum instance, pasang budget alert dan turunkan setelah judging sesuai aturan event.
- Jangan menghapus resource atau mengubah linked materials setelah deadline sampai periode lock berakhir.

## 10. Troubleshooting priority

| Gejala | Cek pertama |
|---|---|
| Pub/Sub 401/403 | worker invoker binding, OIDC service account, token creator permission |
| Duplicate outputs | idempotency document/transaction lease |
| Gemini model not found | exact model ID, Vertex vs Developer API mode, region, quota |
| Firestore permission denied | runtime service account role dan project selection |
| Client token selalu invalid | raw token hashing/canonical encoding, expiry timezone, purpose |
| CORS failure | exact hosted `WEB_ORIGIN`; jangan wildcard dengan credentials |
| Image unreadable | MIME/size validation dan Storage IAM |
