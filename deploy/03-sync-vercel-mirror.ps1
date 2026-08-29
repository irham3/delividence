<#
    Delividence - dorong isi repo ini ke mirror deployment Vercel.

    Vercel membangun delividence.vercel.app dari repo privat
    rifqiahmadpratama/delividence, BUKAN dari irham3/delividence. Repo itu
    dibuat lewat fitur "Clone" Vercel sehingga historinya terpisah dan tidak
    pernah menarik perubahan sendiri. Merge ke `main` di repo utama TIDAK
    membuat perubahan frontend muncul di produksi.

    Biasanya kamu tidak perlu menjalankan ini: workflow
    .github/workflows/sync-deployment-mirror.yml sudah menyinkronkan mirror
    setiap 15 menit. Pakai script ini kalau butuh deploy SEKARANG.

    Yang didorong adalah isi commit yang sedang di-checkout (HEAD), jadi
    pastikan branch-nya sudah benar dan commit-nya bersih.

    Pemakaian:
        .\deploy\03-sync-vercel-mirror.ps1
#>

param(
    [string]$MirrorUrl = "https://github.com/rifqiahmadpratama/delividence.git",
    [string]$RemoteName = "vercelclone"
)

$ErrorActionPreference = "Stop"

function Step($text) { Write-Host "`n==> $text" -ForegroundColor Cyan }

Step "Pastikan remote mirror ada"
$existing = git remote
if ($existing -notcontains $RemoteName) {
    git remote add $RemoteName $MirrorUrl
    Write-Host "remote '$RemoteName' ditambahkan"
} else {
    Write-Host "remote '$RemoteName' sudah ada"
}

Step "Ambil kondisi mirror terkini"
git fetch $RemoteName main | Out-Null

$localTree = git rev-parse "HEAD^{tree}"
$mirrorTree = git rev-parse "$RemoteName/main^{tree}"

if ($localTree -eq $mirrorTree) {
    Write-Host "`nMirror sudah sama persis dengan HEAD. Tidak ada yang perlu dideploy." -ForegroundColor Green
    exit 0
}

Step "Buat commit berisi tree HEAD di atas histori mirror"
# commit-tree dipakai supaya histori mirror (termasuk "Initial commit" bawaan
# Vercel) tetap utuh -- tidak pernah ada force-push ke sana.
$short = git rev-parse --short HEAD
$message = "sync: irham3/delividence@$short"
$commit = git commit-tree $localTree -p "$RemoteName/main" -m $message
Write-Host "commit: $commit"

Step "Dorong ke mirror"
git push $RemoteName "${commit}:refs/heads/main"

Write-Host "`nSELESAI. Vercel akan membangun ulang otomatis (~60 detik)." -ForegroundColor Green
Write-Host "Cek: https://delividence.vercel.app"
