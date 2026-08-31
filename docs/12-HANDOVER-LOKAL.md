# Menjalankan Delividence di mesin sendiri — daftar serah-terima

Ditulis 30 Agustus 2026, setelah seluruh langkah di bawah dijalankan sungguhan
di satu mesin Windows 11 (bukan disalin dari ingatan).

Seluruh **kode** sudah ada di repo. Yang tidak ikut ke repo hanya **dua file
env**, karena keduanya gitignored. Itulah yang perlu dikirim.

---

## 1. Dua file yang harus dikirim

### `web/.env` — aman dikirim apa adanya

Config web Firebase memang **public**: nilai yang sama sudah tertanam di bundle
JavaScript `delividence.vercel.app` dan bisa dibaca siapa pun. Bukan rahasia.

```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8080

NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyDCGeIu-5cje1oHa-X8edYSMB5BYQvWdlM
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=gen-lang-client-0104798459.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=gen-lang-client-0104798459
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=gen-lang-client-0104798459.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=798836649371
NEXT_PUBLIC_FIREBASE_APP_ID=1:798836649371:web:97acf8c2adbed64475853e
```

Tanpa keenam baris `NEXT_PUBLIC_FIREBASE_*` itu, halaman sign-in/register
melempar `Firebase is not configured: apiKey, authDomain, ...` begitu tombolnya
diklik.

### `backend/.env` — kirim strukturnya, JANGAN kirim API key-nya

```
ROLE=api
GOOGLE_CLOUD_PROJECT=
PUBSUB_TOPIC=delividence-runs
GEMINI_MODEL=gemini-3.6-flash
GOOGLE_CLOUD_LOCATION=asia-southeast2
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GEMINI_API_KEY=<partner isi sendiri>
FIREBASE_PROJECT_ID=gen-lang-client-0104798459
WORKER_URL=http://127.0.0.1:8081
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001
```

Dua catatan penting:

- **`GEMINI_API_KEY` sebaiknya digenerate sendiri oleh partner**, gratis di
  <https://aistudio.google.com/apikey>. Key itu terikat ke akun Google
  pemiliknya dan berbagi kuota free tier — kalau dipakai berdua, panggilan
  ekstraksi/Guardrail bisa saling mendorong ke `429 Too Many Requests`.
- **`GOOGLE_CLOUD_PROJECT` sengaja dikosongkan** untuk mode lokal. Kosong =
  `config.LOCAL=True`: antrean jadi panggilan HTTP langsung ke worker dan
  state ditulis sebagai file JSON di `backend/.localdata/`, tanpa Firestore
  maupun Pub/Sub sungguhan. Isi hanya kalau memang mau menyambung ke data
  produksi (lihat bagian 5).

---

## 2. Yang harus dipasang lebih dulu

| Kebutuhan | Kenapa |
|---|---|
| Python 3.11 + `backend/requirements-dev.txt` | backend & test |
| Node + **pnpm** | frontend |
| Google Cloud SDK (`gcloud`) | hanya untuk `application-default login` di bawah |

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
cd web; pnpm install
```

**`gcloud auth application-default login` wajib dijalankan sekali**, walaupun
mode lokal. Penyebabnya `backend/app/auth.py`: verifikasi Firebase ID token
memakai `firebase_admin` dengan Application Default Credentials, dan Firebase
Auth adalah layanan hosted yang tetap dipakai meski Firestore/Pub-Sub tidak.
Tanpa ADC, semua endpoint owner gagal walau brief-nya sudah benar.

> Catatan kejujuran: verifikasi token secara kode tidak memanggil API milik
> project (hanya mencocokkan tanda tangan JWT dengan sertifikat publik Google),
> jadi seharusnya akun Google mana pun bisa. **Belum diuji dengan akun selain
> pemilik project.** Kalau partner kena error kredensial di sini, jalan
> tercepatnya adalah menambahkan akunnya ke project Firebase.

---

## 3. Menjalankan — tiga terminal

```powershell
# Terminal 1 — API di :8080
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8080 --env-file .env

# Terminal 2 — worker di :8081
cd backend
$env:ROLE = "worker"
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8081 --env-file .env

# Terminal 3 — web di :3000
cd web
pnpm dev
```

API dan worker adalah **satu aplikasi yang sama** dengan peran berbeda
(`app/main.py` memilih berdasarkan `ROLE`). `ROLE` dari environment **menang**
atas isi `--env-file`, jadi worker tidak butuh file env kedua — sudah diuji:
instance dengan `$env:ROLE="worker"` menjawab `POST /pubsub/push` 204 dan
`GET /runs` 404.

### Cek cepat bahwa semuanya benar

```powershell
curl.exe -s -o NUL -w "%{http_code}`n" http://127.0.0.1:8080/runs   # 401
curl.exe -s -o NUL -w "%{http_code}`n" http://127.0.0.1:3000/       # 200
```

`401 Missing or malformed Authorization header` dari `/runs` adalah jawaban
yang **sehat** tanpa token — tanda auth owner hidup, bukan error.

---

## 4. Tiga jebakan yang paling sering makan waktu

1. **Ubah `.env` → wajib restart `pnpm dev`.** Next.js membaca
   `NEXT_PUBLIC_*` saat proses start; reload browser saja tidak cukup.
2. **Popup Google Sign-In diblokir di browser yang dikendalikan otomasi.**
   Di browser normal tidak masalah. Kalau `window.open` mengembalikan `null`,
   itu keterbatasan environment, bukan bug aplikasi.
3. **Port 3000 dipakai project lain** → Next.js pindah ke 3001 sendiri.
   `ALLOWED_ORIGINS` di `backend/.env` sudah memuat 3001 supaya CORS tidak
   mendadak menolak.

---

## 5. Opsional: menyambung ke data produksi

Isi `GOOGLE_CLOUD_PROJECT=gen-lang-client-0104798459` di `backend/.env`. Mulai
saat itu backend lokal membaca/menulis Firestore produksi sungguhan, jadi
perlu akses IAM ke project itu.

Push subscription produksi tetap mengirim job ke Cloud Run worker, bukan ke
worker lokal. Supaya worker lokal ikut kebagian, jalankan forwarder:

```powershell
cd backend
..\.venv\Scripts\python.exe local_pubsub_forwarder.py
```

Job akan diproses **dua kali** (Cloud Run + lokal). Itu disengaja, bukan bug.

---

## 6. Test

```powershell
cd backend; ..\.venv\Scripts\python.exe -m pytest -q     # 227 hijau
cd web; pnpm test                                        # 19 unit + 5 e2e
```

Seluruh test backend berjalan di mode LOCAL (file JSON) dan **tidak pernah
menyentuh Firestore sungguhan** — hijau di sini bukan bukti jalur Firestore
aman. Itu pelajaran dari bug produksi 29 Agustus (composite index).
