# Shot-list rekaman — Delividence

Panduan klik-per-detik untuk rekam naskah video di `docs/05-SUBMISSION-CHECKLIST.md`
§4. Disusun 28 Agu 2026. Label penting di tiap beat:

- **[PRE-STAGE]** — kerjakan SEBELUM tekan Record, di luar kamera. Boleh lama/berulang.
- **[LIVE]** — inilah yang direkam, harus rapi sekali take (latihan dulu kalau perlu).
- **[JUMP CUT]** — titik potong; stop record → lakukan langkah cepat → start record baru.

**Update final (28 Agu, malam):** seluruh pipeline sudah direhearsal
end-to-end sungguhan (bukan dry-run parsial) — Handshake, Guardrail,
Evidence, Delivery Review, semua terbukti jalan lancar dengan nama
tombol/section persis seperti tertulis di bawah. Rehearsal ini memakai run
`59b44ab7106b469bab294a5d54667de3` yang **statusnya sekarang sudah lanjut
(baseline confirmed, ada CHANGE_REQUEST, evidence attached, review
accepted)** — run itu SUDAH TERPAKAI untuk rehearsal, jangan dipakai lagi
untuk take asli. Untuk take sungguhan, **buat run baru dari awal** ikuti
langkah PRE-STAGE di bawah (sudah terbukti jalan mulus, ~1 menit).

> **Gotcha penting yang ketemu pas rehearsal:**
> 1. **Selalu baca URL client link dari accessibility tree** (`read_page`),
>    jangan dari screenshot — huruf besar `O` gampang kebaca sebagai angka
>    `0` dan sebaliknya `l`/`I`, linknya jadi 403 kalau salah.
> 2. Di client portal, tombol **Confirm project plan** tetap disabled
>    ("Resolve all blockers first") sampai **Save changes** diklik dulu —
>    isi field lalu Save, baru tombol Confirm aktif.
> 3. Field bawaan **"Unresolved questions"** ("Required input/materials
>    needed from client") harus di-**remove** dulu (dianggap blocker),
>    kecuali memang mau dijawab.
> 4. Klasifikasi Guardrail terkonfirmasi (CHANGE_REQUEST) **tidak otomatis**
>    membuat baseline v2 — itu perlu langkah terpisah **"Propose a scope
>    change"** (form: deliverable id, new criterion key, verbatim
>    acceptance text) kalau mau ditunjukkan di video.
> 5. Tombol **View Markdown**/**View JSON** pada Proof membuka file lewat
>    blob URL (langsung ke mata penonton saat direkam, tapi tidak bisa
>    di-screenshot otomatis oleh tool saya — tidak masalah untuk rekaman
>    manual).

**Update 29 Agu:** ditambahkan Beat 6 "Persistent preference" (fitur baru
dari partner, `POST/GET /preferences`, sudah terverifikasi live lewat API —
lihat `docs/10-KEPUTUSAN-DAN-VERIFIKASI.md` §4b). Belum ada UI-nya di
frontend yang live sekarang (Vercel belum redeploy kerjaan partner),
cek dulu sebelum rekam beat ini.

---

## Persiapan sekali di awal sesi rekam (sebelum semua takes)

1. Buka OBS, scene **Display Capture** (bukan Window Capture).
2. Buka `delividence.vercel.app` di tab bersih, **Sign in with Google**.
3. Siapkan tab kedua: GCP Console → Cloud Run → `delividence-api` (untuk beat
   Google Cloud proof nanti) dan tab ketiga: Firestore data viewer.
4. Matikan notifikasi sistem (Focus Assist / Do Not Disturb) — biar tidak ada
   popup nyelonong pas Display Capture jalan.
5. Siapkan teks berikut di Notepad supaya tinggal copy-paste (jangan ngetik
   panjang live, sesuai aturan produksi di naskah):
   - Brief: `Hi! Can you edit a few short videos for our Instagram? Should look modern and responsive, done by Friday. We're okay with a few rounds of revisions. Budget is around 2 million rupiah. Let us know what you need from us.`
   - Guardrail request: `Please also create three vertical TikTok visuals.`

---

## [PRE-STAGE] Sebelum beat Handshake — siapkan run sampai ledger siap

Tujuannya: pas mulai rekam, ledger + pertanyaan klarifikasi sudah muncul,
tidak perlu nunggu Gemini di depan kamera. Sudah dicoba langsung 28 Agu,
langkah di bawah ini akurat:

1. Dashboard → paste brief di textarea **"Create a project record"** →
   klik **Analyse brief**.
2. Card **"Run activity"** muncul, status **queued** → **done** (beberapa
   detik, worker + Gemini asli). Kalau gagal, dashboard punya tombol
   **Retry extraction** di baris status.
3. Scroll ke **"Freelancer actions"** (di bawah "Owner controls") → klik
   **Create clarification link** → URL muncul di sebelah tombol (ada juga
   link **Revoke** kalau perlu batalkan). Copy URL itu, simpan di Notepad,
   **jangan dibuka dulu**.
4. (Opsional, cek saja) Buka client link itu sekali untuk pastikan ledger
   sudah terisi — halaman **"Review the project plan"**: brief text,
   banner oranye **"A few things still need your input"** (daftar field
   yang masih kosong), section **Deliverables**, **Acceptance criteria**,
   **Out of scope**, **Final deadline**, **Revision rounds included**,
   **Additional context** (In scope / Dependencies / Assumptions /
   **Unresolved questions**). Tombol **Confirm project plan** ada di
   paling bawah, disabled sampai field wajib terisi — **jangan diklik**,
   itu bagian live.

---

## Beat 1 — 0:00–0:12 Outcome dulu

**[LIVE]** Rekam cepat scroll-through dashboard yang SUDAH matang (hasil
run dari sesi lain yang statusnya sudah lengkap sampai Proof, kalau ada) —
kalau belum ada run selengkap itu, lewati beat ini dulu dan syuting belakangan
setelah semua tahap lain selesai sekali (baru ada materi buat "highlight
reel" pembuka). Alternatif: susun beat ini terakhir dari potongan beat 3, 4,
5 yang sudah direkam.

---

## Beat 2 — 0:12–0:35 Masalah dan pembeda

**[LIVE]** Tampilkan teks brief mentah (bisa di Notepad atau di textarea
sebelum ditekan Analyse) dengan kata-kata ambigu — "modern", "responsive",
"done Friday", "a few revisions" — kalau bisa di-highlight/underline manual
saat editing nanti. Tidak perlu interaksi apa pun di app untuk beat ini,
cukup gambar diam brief-nya (voice-over yang bicara).

---

## Beat 3 — 0:35–1:10 Handshake

**[LIVE] Bagian A (15 detik) — ledger + citation:**
1. Buka run yang sudah di-PRE-STAGE di atas (status **done**).
2. Tunjukkan card **"Run activity"** → log **extraction**: "Brief
   diekstrak lewat Gemini -- N field ledger terisi."
3. Scroll ke **Freelancer actions**, tunjukkan link Clarification yang
   sudah dibuat (atau buat baru di sini kalau mau kelihatan live).

**[LIVE] Bagian B (15 detik) — client portal:**
4. Buka tab baru → paste URL client link.
5. Halaman **"Review the project plan"** — tunjukkan brief asli + banner
   **"A few things still need your input"** (ini yang berperan sebagai
   "pertanyaan klarifikasi" di naskah — field kosong yang wajib diisi,
   misal `out_of_scope` dan `revision_policy.rounds_total`).
6. Isi field yang diminta: **Out of scope** (+add, siapkan 1 kalimat di
   Notepad), **Revision rounds included** (angka, atau centang "No limit
   set"), **Final deadline** kalau mau lebih lengkap.
7. Scroll ke bawah, klik **Confirm project plan** (tombol jadi aktif
   begitu field wajib terisi).

**[JUMP CUT]**

**[LIVE] Bagian C (5 detik) — balik ke owner:**
7. Balik ke tab dashboard, refresh.
8. Tunjukkan readiness sudah lulus, baseline **v1**, version, dan hash
   tampil.

---

## Beat 4 — 1:10–2:00 Guardrail

**[LIVE] Seluruhnya (baseline v1 harus sudah aktif dari beat 3):**
1. Di dashboard owner, scroll ke section **"New requests (Guardrail)"**
   (di bawah "Propose a scope change") — textbox **"What did the client
   ask for?"** + tombol **Log request**.
2. Paste teks: `Please also create three vertical TikTok visuals.`
3. Klik **Log request**, tunggu ~5-9 detik (Gemini `agent.guardrail_agent`
   memproses).
4. Hasil muncul di kartu bawahnya: **"Model suggested: CHANGE_REQUEST --
   review before confirming."** + dropdown classification + tombol
   **Confirm classification** + daftar citation (misal
   `out_of_scope[0]: "..."`) — zoom ke citation itu.
5. Klik **Confirm classification**. Kartu berubah jadi ringkasan final:
   "Classification: CHANGE_REQUEST" + citation yang dipakai.

**[JUMP CUT]**

6. **(Opsional, kalau mau tunjukkan baseline v2 beneran terbentuk)** scroll
   ke section **"Propose a scope change"** (di atas Guardrail) — isi
   **deliverable id**, **new criterion key**, **verbatim acceptance text**
   → **Propose change**. Ini yang benar-benar membuat baseline v2 dan
   memicu jalur SUPERSEDED — konfirmasi classification saja TIDAK otomatis
   bikin v2.

---

## [PRE-STAGE] Sebelum beat Proof — attach evidence (di luar kamera)

Setelah selesai take Guardrail, **stop record dulu**, lalu di luar kamera:
1. Di dashboard, scroll ke form **"Attach evidence to an acceptance
   criterion"** — dropdown **criterion key** (pilih `modern-responsive`
   atau criterion lain), dropdown tipe **url**/**text**, field URL,
   **caption (optional)**, tombol **Attach**. Contoh yang sudah dites:
   URL `https://drive.google.com/preview-video-v1`, caption "First cut,
   mobile-responsive preview" → pesan **"Evidence attached."** muncul.
2. Scroll ke **Freelancer actions** → klik **Create delivery review link**,
   copy URL-nya dari accessibility tree (bukan screenshot!).
3. Baru start record lagi untuk beat berikutnya.

---

## Beat 5 — 2:00–2:40 Proof

**[LIVE]**
1. Buka dashboard, tunjukkan sekilas evidence yang sudah terpasang ke
   masing-masing criterion (dari pre-stage di atas).
2. Buka tab baru → paste URL client link Delivery review (halaman judulnya
   **"Delivery review"**, subjudul "Review the evidence for each agreed
   criterion. Acceptance stays with the client.").
3. Per criterion ada badge **PENDING** + tombol **Accept** / **Request
   changes**. Pilih Accept untuk sebagian, Request changes untuk 1 (kalau
   pilih Request changes, field alasan wajib muncul — siapkan 1 kalimat di
   Notepad).
4. Klik **Submit review** di paling bawah (baru aktif setelah minimal satu
   keputusan dipilih).
5. Halaman refresh sendiri: pesan **"Your review was submitted."** +
   badge tiap criterion berubah jadi **ACCEPTED**/**CHANGES_REQUESTED**.

**[JUMP CUT]**

6. Balik ke dashboard owner, scroll ke card **"Acceptance Record,
   exportable as JSON or Markdown"** → klik **View Markdown** (atau View
   JSON). Ini buka file baru (blob URL) berisi Proof Manifest lengkap.
7. Tampilkan teks disclaimer di layar (kalau tidak ada built-in, tambahkan
   sebagai on-screen text pas editing): *"Defensible audit trail, not a
   certified legal signature"*.

---

## Beat 6 — 2:40–3:00 Persistent preference

**Belum pernah dites lewat UI** (fitur baru dari partner, 29 Agu, dites
lewat API langsung malam ini — belum ada tombol di frontend yang live
sekarang karena Vercel belum redeploy). Kalau UI-nya belum ada pas rekam,
opsi: (a) tunggu Vercel redeploy dulu, atau (b) demo lewat DevTools/curl
dengan tetap menunjukkan hasilnya di ledger (opsi b kurang ideal untuk
video, usahakan opsi a).

**[PRE-STAGE]**
1. Cek dulu apakah frontend sudah redeploy dan ada UI untuk confirm
   preference (kemungkinan di halaman Settings/Policies).

**[LIVE]**
1. Confirm preference "2 revision rounds" sebagai default (`POST
   /preferences {"revision_rounds": 2}` — sudah dites, response `status:
   CONFIRMED`).
2. Buat **run/deal baru** dari awal (brief apa saja).
3. Tunjukkan ledger run baru itu — field `revision_policy.rounds_total`
   sudah otomatis terisi `2` dengan state **FREELANCER_POLICY** (dites
   lewat `GET /runs/{id}`, field `ledger.revision_policy.rounds_total`).

---

## Beat 7 — 3:00–3:25 Google Cloud proof

**[PRE-STAGE]** Sebelum take ini, cari dulu (di luar kamera) log entry Pub/Sub
push untuk run yang barusan dipakai, dan dokumen baseline-nya di Firestore —
biar pas live tinggal scroll ke titik yang benar, tidak nyari-cari di depan
kamera.

**[LIVE]**
1. Tampilkan diagram arsitektur (siapkan gambar statis — bisa dari
   `README.md` bagian Architecture, digambar ulang jadi slide).
2. Tab Cloud Run: tunjukkan service `delividence-api` dan
   `delividence-worker` sama-sama status hijau/serving.
3. Tab Pub/Sub atau Cloud Logging: tunjukkan log entry push dengan job ID
   yang cocok dengan run yang dipakai di beat 3-5.
4. Tab Firestore: tunjukkan dokumen baseline (blur project identifier kalau
   perlu, sesuai naskah).

---

## Beat 8 — 3:25–3:35 Penutup

**[LIVE]** Cukup frame diam dashboard/logo Delividence sambil voice-over
penutup — tidak perlu interaksi.

---

## Setelah semua take selesai

- Susun ulang urutan: Beat 1 (outcome) sebenarnya paling enak di-edit
  TERAKHIR dari potongan-potongan beat 3/5 yang sudah direkam (supaya
  benar-benar representasi hasil, bukan rekaman terpisah).
- Cek total durasi tiap beat vs target di naskah, potong bagian yang
  kelamaan (terutama loading/klik yang tidak perlu).
- Tambahkan voice-over sesuai teks persis di `docs/05-SUBMISSION-CHECKLIST.md`
  §4 atau `docs/naskah-video-delividence.pdf`.
