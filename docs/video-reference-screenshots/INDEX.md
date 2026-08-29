# Referensi screenshot untuk rekam video

Dibuat 28 Agu 2026 dari run sungguhan (`3fba73f541c444e29637413a42bdd215`),
diverifikasi end-to-end. Urutan file sesuai urutan beat di
`docs/shot-list-video.md`. Semua data di sini asli (Gemini extraction +
Guardrail classification sungguhan), bukan mock.

| # | File | Beat naskah | Yang ditunjukkan |
|---|------|-------------|-------------------|
| 01 | `01-handshake-client-plan-confirmed.jpg` | 3 (akhir) | Client portal — "Project plan confirmed", baseline v1 active |
| 02 | `02-handshake-owner-run-activity-extraction-done.jpg` | 3A | Owner dashboard — Run activity, log ekstraksi Gemini |
| 03 | `03-handshake-owner-freelancer-actions-baseline-active.jpg` | 3A/C | Owner dashboard — Freelancer actions, badge "Baseline active", tombol Create clarification link |
| 04 | `04-guardrail-empty-state.jpg` | 4 (awal) | Section "New requests (Guardrail)" sebelum diisi |
| 05 | `05-guardrail-model-suggested-change-request.jpg` | 4 | Setelah Log request — "Model suggested: CHANGE_REQUEST", tombol Confirm classification |
| 06 | `06-guardrail-citation-detail.jpg` | 4 | Detail citation (out_of_scope[0]) yang jadi dasar klasifikasi |
| 07 | `07-guardrail-classification-confirmed.jpg` | 4 (akhir) | Setelah Confirm classification — ringkasan final |
| 08 | `08-evidence-form-filled.jpg` | 5 (pre-stage) | Form "Attach evidence" terisi, sebelum submit |
| 09 | `09-evidence-attached.jpg` | 5 (pre-stage) | Pesan "Evidence attached." |
| 10 | `10-proof-delivery-review-pending.jpg` | 5 | Client — Delivery review, status PENDING, tombol Accept/Request changes |
| 11 | `11-proof-delivery-review-accept-selected.jpg` | 5 | Accept terpilih, tombol Submit review aktif |
| 12 | `12-proof-delivery-review-accepted-submitted.jpg` | 5 (akhir) | "Your review was submitted." — status ACCEPTED |

## Catatan

- **Belum ada** screenshot ledger client portal dalam keadaan KOSONG (sebelum
  diisi) — sempat diambil di sesi rehearsal sebelumnya tapi tidak tersimpan
  ke disk. Kalau perlu, cukup buka client link baru sebelum isi apa pun dan
  screenshot manual — tampilannya sama seperti yang sudah dilihat sebelumnya
  (banner oranye "A few things still need your input").
- Beat 6 (Google Cloud proof) tidak ada screenshot referensi — itu murni dari
  GCP Console (Cloud Run, Pub/Sub, Firestore), bukan dari app Delividence.
- Beat "View Markdown" (Proof Manifest export) tidak bisa di-screenshot
  otomatis oleh Claude (file dibuka lewat blob URL) — cukup klik tombolnya
  langsung saat rekam, hasilnya teks biasa yang gampang dibaca.
- Run yang dipakai di sini (`3fba73f541c...`) sudah "kotor" (terpakai penuh
  sampai Proof) — untuk take video sungguhan, buat run baru dari nol ikuti
  langkah PRE-STAGE di `docs/shot-list-video.md`.
