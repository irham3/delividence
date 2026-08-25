# Delividence — backend

Vertical slice: `POST /runs → antrean → worker → store`. Belum ada logika produk
di dalamnya; yang dibuktikan di tahap ini adalah **eksekusi terpisah dari
request** dan **idempotensi**.

## Satu image, dua service

`ROLE` menentukan app mana yang di-serve dari image yang sama:

| `ROLE` | App | Endpoint |
|---|---|---|
| `api` (default) | `app.api` | `GET /health`, `POST /runs`, `GET /runs/{run_id}` |
| `worker` | `app.worker` | `GET /health`, `POST /pubsub/push` |

Ini yang membuat `delividence-api` dan `delividence-worker` bisa di-deploy dari satu
sumber tanpa keduanya boot app yang sama.

## Mode lokal

Tanpa `GOOGLE_CLOUD_PROJECT`, backend jalan lokal: antrean lewat HTTP langsung ke
worker, state ke file JSON di `.localdata/`. Bentuk envelope dan semantik klaim
job dibuat identik dengan produksi, jadi handler yang diuji lokal adalah handler
yang sama yang dipakai di Cloud Run.

```powershell
python -m venv ..\.venv
..\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt

# terminal 1 — worker
$env:ROLE = "worker"
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8081

# terminal 2 — api
$env:ROLE = "api"; $env:WORKER_URL = "http://127.0.0.1:8081"
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8080
```

Verifikasi (pakai `curl.exe`, bukan alias `curl` bawaan PowerShell):

```powershell
curl.exe -s http://127.0.0.1:8080/health
curl.exe -s -X POST http://127.0.0.1:8080/runs -H "Content-Type: application/json" -d "{\"brief\":\"need an edit for our IG content\"}"
curl.exe -s http://127.0.0.1:8080/runs/<run_id>
```

Run yang berhasil berubah `queued → processing → done` **tanpa** request kedua,
dan `audit_trail` berisi satu langkah.

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
