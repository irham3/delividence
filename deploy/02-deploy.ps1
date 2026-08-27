<#
    Delividence - deploy ke Cloud Run + sambungkan push subscription.

    Urutannya penting: worker di-deploy lebih dulu karena URL-nya dibutuhkan
    untuk membuat push subscription, baru API di-deploy terakhir.

    Pemakaian:
        .\02-deploy.ps1 -ProjectId delividence-xxxx `
          -FrontendOrigin https://delividence.example `
          -FirebaseProjectId delividence-xxxx
#>

param(
    [Parameter(Mandatory = $true)][string]$ProjectId,
    [string]$Region = "asia-southeast2",
    [string]$Topic = "delividence-runs",
    [Parameter(Mandatory = $true)][string]$FrontendOrigin,
    [Parameter(Mandatory = $true)][string]$FirebaseProjectId,
    [ValidateSet("developer", "vertex")][string]$ModelRuntime = "developer",
    [string]$GeminiSecretName = "delividence-gemini-api-key",
    [string]$GeminiModel = "gemini-3.6-flash"
)

$ErrorActionPreference = "Stop"

$DlqTopic = "$Topic-dlq"
$PushSub = "$Topic-push"
$Backend = Join-Path $PSScriptRoot "..\backend"

$SaApi = "delividence-api@$ProjectId.iam.gserviceaccount.com"
$SaWorker = "delividence-worker@$ProjectId.iam.gserviceaccount.com"
$SaPush = "delividence-pubsub@$ProjectId.iam.gserviceaccount.com"

function Step($text) { Write-Host "`n==> $text" -ForegroundColor Cyan }

function Exists([scriptblock]$probe) {
    & $probe | Out-Null
    return ($LASTEXITCODE -eq 0)
}

function Must([string]$what, [scriptblock]$cmd) {
    & $cmd
    if ($LASTEXITCODE -ne 0) { throw "GAGAL: $what" }
}

$UseVertex = if ($ModelRuntime -eq "vertex") { "TRUE" } else { "FALSE" }
$BaseEnv = "GOOGLE_CLOUD_PROJECT=$ProjectId,PUBSUB_TOPIC=$Topic,GOOGLE_CLOUD_LOCATION=$Region,GEMINI_MODEL=$GeminiModel,GOOGLE_GENAI_USE_VERTEXAI=$UseVertex,FIREBASE_PROJECT_ID=$FirebaseProjectId"
$WorkerEnv = "ROLE=worker,$BaseEnv"
$ApiEnv = "ROLE=api,$BaseEnv,ALLOWED_ORIGINS=$FrontendOrigin"
$SecretArgs = @()

if ($ModelRuntime -eq "developer") {
    if (-not (Exists { gcloud secrets describe $GeminiSecretName --format="value(name)" })) {
        throw "Secret '$GeminiSecretName' belum ada. Buat dulu: gcloud secrets create $GeminiSecretName --replication-policy=automatic; lalu tambahkan GEMINI_API_KEY sebagai versi secret."
    }
    $SecretArgs = @("--set-secrets=GEMINI_API_KEY=$GeminiSecretName`:latest")
}

Step "Deploy worker (tertutup - hanya Pub/Sub yang boleh memanggil)"
Must "deploy worker" {
    $deployArgs = @("run", "deploy", "delividence-worker", "--source=$Backend", "--region=$Region", "--service-account=$SaWorker", "--no-allow-unauthenticated", "--set-env-vars=$WorkerEnv", "--timeout=300", "--concurrency=10", "--quiet") + $SecretArgs
    & gcloud @deployArgs
}

$WorkerUrl = (gcloud run services describe delividence-worker --region=$Region --format="value(status.url)")
if (-not $WorkerUrl) { throw "URL worker tidak terbaca" }
Write-Host "worker: $WorkerUrl"

Step "Izin: hanya identitas push Pub/Sub yang boleh memanggil worker"
Must "run.invoker" {
    gcloud run services add-iam-policy-binding delividence-worker `
        --region=$Region `
        --member="serviceAccount:$SaPush" `
        --role="roles/run.invoker" `
        --quiet | Out-Null
}

Step "Push subscription (OIDC, ack deadline, dead-letter, retry)"
# ack-deadline 60 detik: worker memanggil model, jadi 10 detik bawaan terlalu
# pendek dan akan memicu pengiriman ulang yang tidak perlu.
if (Exists { gcloud pubsub subscriptions describe $PushSub --format="value(name)" }) {
    Must "update subscription" {
        gcloud pubsub subscriptions update $PushSub `
            --push-endpoint="$WorkerUrl/pubsub/push" `
            --push-auth-service-account=$SaPush `
            --ack-deadline=60 `
            --dead-letter-topic=$DlqTopic `
            --max-delivery-attempts=5 `
            --min-retry-delay=10s `
            --max-retry-delay=600s `
            --quiet | Out-Null
    }
} else {
    Must "create subscription" {
        gcloud pubsub subscriptions create $PushSub `
            --topic=$Topic `
            --push-endpoint="$WorkerUrl/pubsub/push" `
            --push-auth-service-account=$SaPush `
            --ack-deadline=60 `
            --dead-letter-topic=$DlqTopic `
            --max-delivery-attempts=5 `
            --min-retry-delay=10s `
            --max-retry-delay=600s `
            --quiet | Out-Null
    }
}

Step "Deploy API (terbuka - juri harus bisa mengaksesnya tanpa restriksi)"
Must "deploy api" {
    $deployArgs = @("run", "deploy", "delividence-api", "--source=$Backend", "--region=$Region", "--service-account=$SaApi", "--allow-unauthenticated", "--set-env-vars=$ApiEnv", "--timeout=60", "--quiet") + $SecretArgs
    & gcloud @deployArgs
}

$ApiUrl = (gcloud run services describe delividence-api --region=$Region --format="value(status.url)")

Write-Host "`nSELESAI." -ForegroundColor Green
Write-Host "api   : $ApiUrl"
Write-Host "worker: $WorkerUrl"
Write-Host @"

Verifikasi (pakai curl.exe, bukan alias curl bawaan PowerShell):

  curl.exe -s $ApiUrl/health

  curl.exe -s -X POST $ApiUrl/runs -H "Content-Type: application/json" ``
    -d "{\"brief\":\"need an edit for our IG content\"}"

  curl.exe -s $ApiUrl/runs/<run_id>

Lulus kalau run berubah jadi "done" tanpa request kedua - artinya Pub/Sub
benar-benar memanggil worker, bukan API yang mengerjakannya sendiri.

Kalau macet, urutan pemeriksaan:
  gcloud pubsub subscriptions describe $PushSub
  gcloud run services logs read delividence-worker --region=$Region --limit=50
  gcloud pubsub subscriptions pull $DlqTopic-sub --limit=5    # pesan yang mati
"@
