<#
    Delividence - penyiapan resource Google Cloud.

    Jalankan sekali setelah billing aktif. Aman diulang: setiap resource dicek
    dulu keberadaannya, jadi menjalankan ulang tidak menggandakan apa pun.

    Prasyarat (interaktif, kerjakan sendiri lebih dulu):
        gcloud auth login
        gcloud auth application-default login
        gcloud config set project <PROJECT_ID>

    Pemakaian:
        .\01-setup-gcp.ps1 -ProjectId delividence-xxxx
#>

param(
    [Parameter(Mandatory = $true)][string]$ProjectId,
    [string]$Region = "asia-southeast2",
    [string]$Topic = "delividence-runs"
)

$ErrorActionPreference = "Stop"

$DlqTopic = "$Topic-dlq"
$Repo = "delividence"

function Step($text) { Write-Host "`n==> $text" -ForegroundColor Cyan }

function Exists([scriptblock]$probe) {
    & $probe | Out-Null
    return ($LASTEXITCODE -eq 0)
}

function Must([string]$what, [scriptblock]$cmd) {
    & $cmd
    if ($LASTEXITCODE -ne 0) { throw "GAGAL: $what" }
}

Step "Mengunci project & region"
Must "set project" { gcloud config set project $ProjectId --quiet }
Must "set region" { gcloud config set run/region $Region --quiet }

$ProjectNumber = (gcloud projects describe $ProjectId --format="value(projectNumber)")
if (-not $ProjectNumber) { throw "Tidak bisa membaca project number. Billing sudah aktif?" }
Write-Host "project=$ProjectId number=$ProjectNumber region=$Region"

Step "Mengaktifkan API"
# aiplatform untuk Vertex AI; cloudbuild wajib untuk 'gcloud run deploy --source'.
Must "enable services" {
    gcloud services enable `
        run.googleapis.com `
        pubsub.googleapis.com `
        firestore.googleapis.com `
        secretmanager.googleapis.com `
        artifactregistry.googleapis.com `
        cloudbuild.googleapis.com `
        aiplatform.googleapis.com `
        --quiet
}

Step "Firestore (mode Native)"
if (Exists { gcloud firestore databases describe --database="(default)" --format="value(name)" }) {
    Write-Host "sudah ada, dilewati"
} else {
    Must "create firestore" {
        gcloud firestore databases create --location=$Region --type=firestore-native --quiet
    }
}

Step "Artifact Registry"
if (Exists { gcloud artifacts repositories describe $Repo --location=$Region --format="value(name)" }) {
    Write-Host "sudah ada, dilewati"
} else {
    Must "create repo" {
        gcloud artifacts repositories create $Repo --repository-format=docker --location=$Region --quiet
    }
}

Step "Service account (satu per peran, hak minimum)"
$accounts = @{
    "delividence-api"    = "API: menulis run, menerbitkan pekerjaan"
    "delividence-worker" = "Worker: memproses pekerjaan, memanggil Vertex AI"
    "delividence-pubsub" = "Identitas push Pub/Sub: hanya boleh memanggil worker"
}
foreach ($name in $accounts.Keys) {
    $email = "$name@$ProjectId.iam.gserviceaccount.com"
    $desc = $accounts[$name]
    if (Exists { gcloud iam service-accounts describe $email --format="value(email)" }) {
        Write-Host "$name sudah ada"
    } else {
        Must "create sa $name" {
            gcloud iam service-accounts create $name --display-name="$desc" --quiet
        }
    }
}

$SaApi = "delividence-api@$ProjectId.iam.gserviceaccount.com"
$SaWorker = "delividence-worker@$ProjectId.iam.gserviceaccount.com"

Step "IAM level project"
# API: baca/tulis Firestore dan menjalankan Guardrail/proof review. Worker:
# Firestore + ekstraksi. Keduanya dapat memakai Vertex bila runtime dipilih.
Must "api datastore" {
    gcloud projects add-iam-policy-binding $ProjectId `
        --member="serviceAccount:$SaApi" --role="roles/datastore.user" --condition=None --quiet | Out-Null
}
Must "worker datastore" {
    gcloud projects add-iam-policy-binding $ProjectId `
        --member="serviceAccount:$SaWorker" --role="roles/datastore.user" --condition=None --quiet | Out-Null
}
Must "api vertex" {
    gcloud projects add-iam-policy-binding $ProjectId `
        --member="serviceAccount:$SaApi" --role="roles/aiplatform.user" --condition=None --quiet | Out-Null
}
Must "worker vertex" {
    gcloud projects add-iam-policy-binding $ProjectId `
        --member="serviceAccount:$SaWorker" --role="roles/aiplatform.user" --condition=None --quiet | Out-Null
}
Must "api secret accessor" {
    gcloud projects add-iam-policy-binding $ProjectId `
        --member="serviceAccount:$SaApi" --role="roles/secretmanager.secretAccessor" --condition=None --quiet | Out-Null
}
Must "worker secret accessor" {
    gcloud projects add-iam-policy-binding $ProjectId `
        --member="serviceAccount:$SaWorker" --role="roles/secretmanager.secretAccessor" --condition=None --quiet | Out-Null
}

Step "Topic utama + dead-letter"
foreach ($t in @($Topic, $DlqTopic)) {
    if (Exists { gcloud pubsub topics describe $t --format="value(name)" }) {
        Write-Host "$t sudah ada"
    } else {
        Must "create topic $t" { gcloud pubsub topics create $t --quiet }
    }
}

Step "Izin menerbitkan ke topic"
Must "api publisher" {
    gcloud pubsub topics add-iam-policy-binding $Topic `
        --member="serviceAccount:$SaApi" --role="roles/pubsub.publisher" --quiet | Out-Null
}

# Gotcha yang menghabiskan waktu orang: dead-letter tidak jalan tanpa dua binding
# ini untuk service agent Pub/Sub. Kegagalannya senyap - pesan mati hanya hilang.
$PubsubAgent = "service-$ProjectNumber@gcp-sa-pubsub.iam.gserviceaccount.com"
Must "agent publisher ke dlq" {
    gcloud pubsub topics add-iam-policy-binding $DlqTopic `
        --member="serviceAccount:$PubsubAgent" --role="roles/pubsub.publisher" --quiet | Out-Null
}

Step "Langganan DLQ supaya pesan mati bisa dibaca"
if (Exists { gcloud pubsub subscriptions describe "$DlqTopic-sub" --format="value(name)" }) {
    Write-Host "sudah ada, dilewati"
} else {
    Must "create dlq sub" { gcloud pubsub subscriptions create "$DlqTopic-sub" --topic=$DlqTopic --quiet }
}

Write-Host "`nSELESAI." -ForegroundColor Green
Write-Host "Langkah berikutnya: .\02-deploy.ps1 -ProjectId $ProjectId"
Write-Host "Jangan lupa pasang budget alert di console (R-7) sebelum menjalankan agent berulang."
