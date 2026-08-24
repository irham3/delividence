<#
    DealReady - deploy ke Cloud Run + sambungkan push subscription.

    Urutannya penting: worker di-deploy lebih dulu karena URL-nya dibutuhkan
    untuk membuat push subscription, baru API di-deploy terakhir.

    Pemakaian:
        .\02-deploy.ps1 -ProjectId dealready-xxxx
#>

param(
    [Parameter(Mandatory = $true)][string]$ProjectId,
    [string]$Region = "asia-southeast2",
    [string]$Topic = "dealready-runs"
)

$ErrorActionPreference = "Stop"

$DlqTopic = "$Topic-dlq"
$PushSub = "$Topic-push"
$Backend = Join-Path $PSScriptRoot "..\backend"

$SaApi = "dealready-api@$ProjectId.iam.gserviceaccount.com"
$SaWorker = "dealready-worker@$ProjectId.iam.gserviceaccount.com"
$SaPush = "dealready-pubsub@$ProjectId.iam.gserviceaccount.com"

function Step($text) { Write-Host "`n==> $text" -ForegroundColor Cyan }

function Exists([scriptblock]$probe) {
    & $probe | Out-Null
    return ($LASTEXITCODE -eq 0)
}

function Must([string]$what, [scriptblock]$cmd) {
    & $cmd
    if ($LASTEXITCODE -ne 0) { throw "GAGAL: $what" }
}

Step "Deploy worker (tertutup - hanya Pub/Sub yang boleh memanggil)"
Must "deploy worker" {
    gcloud run deploy dealready-worker `
        --source=$Backend `
        --region=$Region `
        --service-account=$SaWorker `
        --no-allow-unauthenticated `
        --set-env-vars="ROLE=worker,GOOGLE_CLOUD_PROJECT=$ProjectId,PUBSUB_TOPIC=$Topic" `
        --timeout=300 `
        --concurrency=10 `
        --quiet
}

$WorkerUrl = (gcloud run services describe dealready-worker --region=$Region --format="value(status.url)")
if (-not $WorkerUrl) { throw "URL worker tidak terbaca" }
Write-Host "worker: $WorkerUrl"

Step "Izin: hanya identitas push Pub/Sub yang boleh memanggil worker"
Must "run.invoker" {
    gcloud run services add-iam-policy-binding dealready-worker `
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
    gcloud run deploy dealready-api `
        --source=$Backend `
        --region=$Region `
        --service-account=$SaApi `
        --allow-unauthenticated `
        --set-env-vars="ROLE=api,GOOGLE_CLOUD_PROJECT=$ProjectId,PUBSUB_TOPIC=$Topic" `
        --timeout=60 `
        --quiet
}

$ApiUrl = (gcloud run services describe dealready-api --region=$Region --format="value(status.url)")

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
  gcloud run services logs read dealready-worker --region=$Region --limit=50
  gcloud pubsub subscriptions pull $DlqTopic-sub --limit=5    # pesan yang mati
"@
