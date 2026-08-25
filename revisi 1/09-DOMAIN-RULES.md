# 09-DOMAIN-RULES.md — Aturan Domain ScopeHandshake

Versi: 1.0 · Dibuat: 25 Agustus 2026 · Status: NORMATIF
Melengkapi: 01-PRD.md, 02-ARCHITECTURE.md
Mengganti: perlakuan criteria sebagai collection terpisah di 02 §6, dan definisi implisit "field kritis" di 01 §7

## 0. Cara memakai dokumen ini

Dokumen ini ditulis untuk dieksekusi oleh beberapa agent/pengembang yang bekerja paralel dan tidak saling berbicara. Karena itu:

- **MUST** / **MUST NOT** = wajib, tidak boleh ditafsirkan ulang.
- **SHOULD** = default yang benar; menyimpang harus dicatat di `07-RISKS-DECISIONS.md`.
- Semua enum di dokumen ini adalah himpunan tertutup. Jangan menambah nilai baru.
- Kalau ada situasi yang tidak tercakup di sini: berhenti dan tanya. Jangan improvisasi aturan domain. Aturan yang ditebak oleh dua agent berbeda akan menghasilkan dua sistem berbeda yang dua-duanya “lulus test” masing-masing.
- Empat modul di bawah (A, B, C, D) boleh dikerjakan paralel setelah §10 dibekukan. Keempatnya hanya bergantung pada §7 (event log) dan §8 (authority), bukan satu sama lain.

### Peta modul

| Modul | Nama | Menutup lubang |
| --- | --- | --- |
| A | Criterion Identity & Baseline Versioning | Apa yang terjadi pada acceptance saat baseline naik ke v2 |
| B | Revision Rounds | Counter revisi yang tidak pernah dihitung siapa pun |
| C | Drift Ledger | Scope creep bertahap yang lolos karena dinilai satu per satu |
| D | Conflict Resolution | CONFLICTING memblokir approval tapi tak punya jalan keluar |

## 1. Invariant global (berlaku di seluruh sistem)

| ID | Invariant |
| --- | --- |
| G-1 | Model tidak boleh menghasilkan state kesepakatan. Model tidak pernah menulis AGREED, tidak pernah menyetujui, tidak pernah mengonsumsi ronde revisi, tidak pernah menyelesaikan konflik. Ini dijamin oleh tidak adanya tool, bukan oleh instruksi prompt. |
| G-2 | Append-only. Semua keputusan manusia disimpan sebagai audit event yang tidak pernah di-update dan tidak pernah dihapus. |
| G-3 | Status turunan, bukan status tersimpan. Semua status di dokumen ini (effective_status, rounds_consumed, agregat drift) dihitung dari event log. Boleh di-cache, tidak boleh dijadikan sumber kebenaran. |
| G-4 | Tidak ada resolusi otomatis berbasis kebaruan. Sistem tidak pernah menyimpulkan "yang lebih baru berarti yang benar". |
| G-5 | Tidak ada inheritance implisit. Tidak ada status yang menular ke versi, criterion, atau ronde berikutnya tanpa aturan eksplisit di dokumen ini. |
| G-6 | Setiap keputusan mencatat konteksnya. Minimal baseline_version + actor + seq. Event tanpa keduanya **MUST** ditolak di layer service. |
| G-7 | Bahasa netral. Tidak ada label yang menyalahkan salah satu pihak. Klien yang minta tambahan bukan "pelanggar"; freelancer yang menerima tambahan bukan "lalai". |

## 2. MODUL A — Criterion Identity & Baseline Versioning

### 2.1 Masalah yang diselesaikan

Criteria menempel pada baseline. Evidence menempel pada criteria. Acceptance klien menempel pada criteria. Ketika change request disetujui dan baseline naik ke v2, tanpa aturan eksplisit ada empat pertanyaan yang tak terjawab: criteria mana yang ikut, apakah acceptance lama masih berlaku, apa yang terjadi pada criterion yang dihapus, dan apakah criterion baru mewarisi apa pun.

Kesalahan implementasi yang paling mungkin terjadi dan paling merusak: menganggap naik versi berarti semua acceptance hangus dan semuanya kembali PENDING. Itu membuat produk terasa rusak — klien yang sudah menerima dua deliverable akan diminta menerima ulang hanya karena timeline berubah. Aturan di bawah sengaja dirancang supaya acceptance hanya batal kalau teks criterion itu sendiri berubah.

### 2.2 Enum

```text
CriterionEffectiveStatus =
  | "PENDING"             // belum ada keputusan untuk teks yang berlaku sekarang
  | "ACCEPTED"            // keputusan terakhir = ACCEPTED, atas teks yang identik dengan versi aktif
  | "CHANGES_REQUESTED"   // keputusan terakhir = CHANGES_REQUESTED, atas teks yang identik
  | "SUPERSEDED"          // ada keputusan, tapi atas teks yang sudah berubah -> tidak berlaku lagi
  | "WITHDRAWN"           // criterion tidak ada di versi aktif, tapi pernah ada di versi sebelumnya
```

SUPERSEDED dan WITHDRAWN bukan kegagalan. Keduanya adalah status sejarah yang ditampilkan apa adanya.

### 2.3 Bentuk data

Criteria **MUST** hidup di dalam `canonical_payload` baseline. Tidak ada collection criteria yang bisa diubah terpisah. Ini bukan sekadar penyederhanaan — collection terpisah membuat teks criterion bisa berubah tanpa naik versi, dan itu membocorkan seluruh jaminan `baseline_version` pada acceptance.

```json
// deals/{deal_id}/baselines/{version_id}
{
  "version": 2,
  "status": "ACTIVE",
  "canonical_payload": {
    "deliverables": [ "..." ],
    "in_scope": [ "..." ],
    "out_of_scope": [ "..." ],
    "timeline": { "final_deadline": "2026-08-28" },
    "revision_policy": { "rounds_total": 2 },
    "criteria": {
      "mobile-breakpoints": {
        "text": "Layout renders correctly at 375px, 768px, and 1440px widths.",
        "text_hash": "sha256:9f2c...",
        "introduced_in_version": 1
      },
      "contact-form-submit": {
        "text": "Contact form sends a valid submission and shows a success state.",
        "text_hash": "sha256:41ab...",
        "introduced_in_version": 1
      }
    }
  },
  "payload_hash": "sha256:7d13...",
  "approved_by": "client",
  "approved_at": "2026-08-26T04:10:00Z",
  "activated_seq": 41
}
```

#### Aturan `criterion_key`

- Format: `^[a-z0-9]+(-[a-z0-9]+)*$`, maksimal 48 karakter.
- Dibuat sekali saat criterion pertama kali muncul. **MUST NOT** berubah selamanya.
- **MUST NOT** dipakai ulang untuk makna yang berbeda.
- Boleh diusulkan oleh model, **MUST** divalidasi format oleh service, dan **MUST** unik dalam satu deal.
- Dua criterion dengan teks identik tetap punya key berbeda. Status dihitung per key, jadi teks kembar tidak menimbulkan masalah.

### 2.4 Normalisasi teks untuk text_hash

Ini **MUST** satu fungsi, satu pemilik, satu file. Dua implementasi yang berbeda tipis akan menghasilkan hash berbeda, dan seluruh modul A gagal tanpa error apa pun.

```text
normalize_criterion_text(s):
  1. Unicode NFC
  2. ganti semua whitespace (\t \n \r \f \v, NBSP U+00A0) menjadi U+0020
  3. rapatkan runtun spasi menjadi satu spasi
  4. trim depan-belakang
  5. JANGAN lowercase
  6. JANGAN hapus tanda baca
  7. text_hash = "sha256:" + hex(sha256(utf8(hasil)))
```

Alasan tidak lowercase dan tidak membuang tanda baca: sistem ini sengaja memilih bertanya ulang daripada diam-diam menganggap dua teks berbeda itu sama. Perubahan editorial murni (spasi ganda, ganti baris) tidak membatalkan acceptance; perubahan karakter yang terlihat, membatalkan. Jangan "memperbaiki" fungsi ini dengan menambah toleransi.

### 2.5 Algoritma turunan (fungsi murni, wajib deterministik)

```text
effective_status(criterion_key, active_version) -> CriterionEffectiveStatus

  active = baselines[active_version].canonical_payload.criteria

  if criterion_key not in active:
      if criterion_key ada di versi mana pun < active_version:
          return "WITHDRAWN"
      raise DomainError("unknown criterion_key")   // MUST NOT terjadi

  current_hash = active[criterion_key].text_hash

  decisions = audit.filter(
      type == "CRITERION_DECISION" and criterion_key == key
  ).sort_by(seq asc)

  if decisions is empty:
      return "PENDING"

  last = decisions[-1]

  // aturan jeda: kalau criterion pernah hilang setelah keputusan itu, keputusan tidak hidup lagi
  for v in range(last.baseline_version + 1, active_version + 1):
      if criterion_key not in baselines[v].canonical_payload.criteria:
          return "SUPERSEDED"

  if last.criterion_text_hash != current_hash:
      return "SUPERSEDED"

  return last.decision      // "ACCEPTED" | "CHANGES_REQUESTED"
```

Perhatikan: naik versi tidak menyentuh status apa pun. Yang membatalkan acceptance hanyalah (a) teks criterion berubah, atau (b) criterion pernah hilang lalu kembali. Kalau v2 hanya mengubah timeline, semua acceptance tetap ACCEPTED.

### 2.6 Invariant modul A

| ID | Invariant |
| --- | --- |
| A-1 | criterion_key immutable, unik per deal, tidak dipakai ulang untuk makna berbeda. |
| A-2 | Criteria hanya ada di dalam canonical_payload baseline. Tidak ada collection criteria yang mutable. |
| A-3 | Baseline immutable setelah BASELINE_ACTIVATED. Perubahan apa pun **MUST** lewat versi baru. |
| A-4 | Setiap CRITERION_DECISION **MUST** memuat baseline_version dan criterion_text_hash. Kurang satu → tolak write. |
| A-5 | effective_status selalu dihitung. Kalau di-cache, cache **MUST** menyimpan computed_at_seq dan dibuang kalau seq deal berubah. |
| A-6 | WITHDRAWN tidak pernah menghapus evidence, decision, atau audit event apa pun. |
| A-7 | Criterion yang lahir di versi n selalu mulai dari PENDING. Tidak ada pewarisan. |
| A-8 | Naik versi baseline **MUST NOT** dengan sendirinya mengubah status criterion mana pun. |
| A-9 | `ACCEPTED` final untuk pasangan `criterion_key + criterion_text_hash`. Permintaan perubahan berikutnya atas pasangan yang sama **MUST** masuk Guardrail dan **MUST NOT** menulis `CHANGES_REQUESTED` baru. |

### 2.7 Edge case yang sudah diputuskan (jangan diperdebatkan lagi)

| Situasi | Keputusan |
| --- | --- |
| Teks berubah hanya spasi/newline | Hash sama → acceptance tetap berlaku |
| Teks berubah satu kata | SUPERSEDED → kembali perlu keputusan klien |
| v2 mengubah timeline saja, criteria utuh | Semua acceptance tetap berlaku |
| Criterion dihapus di v2 | WITHDRAWN; acceptance & evidence tetap tersimpan sebagai sejarah |
| Criterion dihapus di v2, kembali di v3 dengan teks identik | SUPERSEDED, bukan ACCEPTED. Keluar dari kesepakatan lalu kembali adalah putus makna. |
| Criterion baru di v2 | PENDING |
| Dua criterion berteks identik | Key berbeda, status independen |
| Criterion WITHDRAWN yang pekerjaannya sudah dikerjakan | Di luar cakupan MVP. Tidak ada logika kompensasi/pembayaran. Cukup terlihat di audit. |
| Klien meminta perubahan setelah criterion `ACCEPTED` untuk text hash yang masih aktif | Jangan menimpa keputusan dengan `CHANGES_REQUESTED`; arahkan permintaan ke Guardrail. Acceptance efektif tetap berlaku sampai teks criterion berubah atau criterion keluar dari baseline. |

### 2.8 Test vector modul A

| # | Skenario | Ekspektasi |
| --- | --- | --- |
| A-T1 | v1 punya k1, klien ACCEPTED, versi aktif v1 | ACCEPTED |
| A-T2 | Lanjut A-T1, v2 aktif, teks k1 identik | ACCEPTED |
| A-T3 | Lanjut A-T1, v2 aktif, teks k1 diubah | SUPERSEDED |
| A-T4 | Lanjut A-T1, v2 aktif, k1 diubah hanya spasi ganda → satu spasi | ACCEPTED |
| A-T5 | Lanjut A-T1, v2 tidak memuat k1 | WITHDRAWN |
| A-T6 | Lanjut A-T5, v3 memuat k1 lagi dengan teks identik v1 | SUPERSEDED |
| A-T7 | k9 baru muncul di v2, belum ada keputusan | PENDING |
| A-T8 | k1 CHANGES_REQUESTED di v1, v1 masih aktif | CHANGES_REQUESTED |
| A-T9 | k1 CHANGES_REQUESTED lalu ACCEPTED (seq lebih besar) | ACCEPTED |
| A-T10 | Query key yang tidak pernah ada di versi mana pun | DomainError |
| A-T11 | k1 sudah ACCEPTED, `rounds_remaining >= 1`, lalu klien meminta perubahan atas text hash aktif yang sama | Request masuk Guardrail karena finalitas acceptance, bukan exhaustion; tidak ada `CRITERION_DECISION` baru, ronde tidak dikonsumsi, dan effective status tetap ACCEPTED |

## 3. MODUL B — Revision Rounds

### 3.1 Masalah yang diselesaikan

revision_policy.rounds muncul di 02 §4.3, "dua ronde revisi" muncul di 01 §4.1, dan US-6 melarang agent memotong revision allowance sendiri — yang mengandaikan ada allowance yang bisa dipotong. Tapi tidak ada satu pun definisi tentang apa yang mengonsumsi satu ronde, siapa yang menghitung, dan apa yang terjadi saat habis.

Untuk vertical freelancer ini bukan detail. Jumlah ronde revisi adalah field yang paling sering diperdebatkan freelancer dengan klien. Mencatat kebijakannya tanpa menghitungnya berarti tidak memberi apa pun di titik paling penting.

### 3.2 Definisi

```text
rounds_total          : integer | "NOT_SET"   -- dari canonical_payload baseline aktif
goodwill_granted      : integer >= 0          -- turunan dari event, TERPISAH dari rounds_total
rounds_consumed       : integer >= 0          -- turunan dari event
rounds_allowance      : rounds_total + goodwill_granted
rounds_remaining      : max(0, rounds_allowance - rounds_consumed)
rounds_exhausted      : (rounds_total != "NOT_SET") and (rounds_remaining == 0)
```

rounds_total **MUST NOT** pernah dimutasi. Kalau freelancer memberi ronde tambahan sebagai itikad baik, itu masuk goodwill_granted lewat event terpisah dan ditampilkan sebagai "1 goodwill round (not part of the agreement)". Angka yang disepakati tetap utuh dan bisa diaudit — itu inti produknya.

### 3.3 Apa yang mengonsumsi satu ronde

Satu ronde dikonsumsi hanya oleh event REVISION_ROUND_CONSUMED, dan event itu hanya boleh ditulis oleh domain service ketika freelancer secara eksplisit mengonfirmasi bahwa hasil review klien akan dikerjakan sebagai rework in-scope.

| Kejadian | Konsumsi ronde? |
| --- | --- |
| Klien mengirim CHANGES_REQUESTED | Tidak. Meminta bukan mengonsumsi. |
| Freelancer mengonfirmasi rework in-scope | Ya, satu ronde. |
| Request dirutekan ke Guardrail sebagai CHANGE_REQUEST | Tidak. Itu scope baru, bukan revisi. |
| Freelancer memperbaiki sesuatu atas inisiatif sendiri | Tidak. |
| Klien ACCEPTED | Tidak. |
| Baseline naik versi | Tidak. Ronde yang sudah terpakai tidak pernah dikembalikan. |

### 3.4 Cakupan satu ronde = satu review session, bukan satu criterion

Ini keputusan yang **MUST** diikuti dan paling mudah salah diimplementasikan.

Satu review_session_id dialokasikan saat klien membuka delivery review dan mengirim keputusannya dalam satu aksi submit. Semua CHANGES_REQUESTED dalam sesi itu, jika dikonfirmasi sebagai rework, mengonsumsi tepat satu ronde.

Alasannya: kalau dihitung per criterion, satu sesi review dengan tiga komentar akan menghabiskan tiga ronde dan allowance dua ronde langsung habis di review pertama. Tidak ada freelancer atau klien yang menghitung revisi seperti itu, dan produk yang menghitungnya begitu akan terasa curang.

```text
rounds_consumed = count(distinct review_session_id
                        in audit where type == "REVISION_ROUND_CONSUMED"
                        and baseline-scope = seluruh umur deal)
```

Idempotency: kunci {deal_id}:{review_session_id}:revision_round. Event kedua dengan kunci sama **MUST** ditolak, bukan ditulis ulang.

### 3.5 Perilaku saat habis

Saat rounds_exhausted == true, CHANGES_REQUESTED berikutnya **MUST** otomatis dirutekan ke Guardrail sebagai request baru.

Perhatikan batas yang tajam di sini:

- Routing-nya otomatis dan deterministik. Tidak ada model yang terlibat.
- Klasifikasinya tetap normal: model mengusulkan `IN_SCOPE` / `AMBIGUOUS` / `CHANGE_REQUEST` dengan kutipan dari baseline, dan manusia mengonfirmasi. Habisnya ronde **MUST NOT** otomatis berarti `CHANGE_REQUEST`.
- Itu perbedaan antara sistem yang jujur dan sistem yang memihak freelancer. Jangan diperpendek.

Kalau rounds_total == "NOT_SET": seluruh mekanisme ronde **MUST** nonaktif, UI menampilkan "revision limit not agreed", dan tidak ada routing otomatis. Sistem **MUST NOT** mengarang angka default. Mengarang angka di field ini persis jenis kebohongan yang dilarang 07 §E.

### 3.6 Invariant modul B

| ID | Invariant |
| --- | --- |
| B-1 | rounds_consumed dan goodwill_granted selalu turunan dari event. |
| B-2 | Model tidak punya tool untuk menulis event ronde apa pun. |
| B-3 | rounds_total == NOT_SET → mekanisme mati total, tanpa default. |
| B-4 | Maksimal satu ronde per review_session_id, dijamin idempotency key. |
| B-5 | rounds_total tidak pernah dimutasi; goodwill aditif dan berlabel terpisah. |
| B-6 | REVISION_ROUND_CONSUMED wajib memuat baseline_version, review_session_id, dan actor == "freelancer". |
| B-7 | Naik versi baseline tidak mengembalikan ronde yang sudah terpakai. |

### 3.7 Test vector modul B

| # | Skenario | Ekspektasi |
| --- | --- | --- |
| B-T1 | rounds_total=2, klien CHANGES_REQUESTED pada 3 criterion dalam satu submit, freelancer konfirmasi | rounds_consumed == 1, remaining 1 |
| B-T2 | Lanjut B-T1, sesi review kedua dikonfirmasi | rounds_consumed == 2, rounds_exhausted == true |
| B-T3 | Lanjut B-T2, klien CHANGES_REQUESTED lagi | Otomatis jadi request di Guardrail, belum berklasifikasi |
| B-T4 | Klien CHANGES_REQUESTED, freelancer belum konfirmasi | rounds_consumed == 0 |
| B-T5 | Event REVISION_ROUND_CONSUMED dikirim dua kali dengan review_session_id sama | Yang kedua ditolak, counter tetap |
| B-T6 | rounds_total = NOT_SET, klien CHANGES_REQUESTED ×5 | Tidak ada konsumsi, tidak ada routing otomatis, UI menyatakan limit tidak disepakati |
| B-T7 | Model mencoba menulis REVISION_ROUND_CONSUMED | Tidak mungkin — tool tidak ada. Test membuktikan allowlist tidak memuatnya. |
| B-T8 | rounds_exhausted, freelancer memberi goodwill 1 | allowance 3, remaining 1, UI memberi label goodwill secara eksplisit |

## 4. MODUL C — Drift Ledger

### 4.1 Masalah yang diselesaikan

02 §4.5 mengunci input analisis Guardrail: hanya request baru + baseline aktif. Artinya setiap request dinilai terisolasi.

Tapi scope creep nyata hampir tidak pernah berbentuk satu permintaan besar. Bentuknya sepuluh "bisa sekalian..." yang masing-masing wajar dan seluruhnya menambah 40% pekerjaan. Sepuluh request itu akan diklasifikasi IN_SCOPE dengan benar satu per satu, dan tidak ada seorang pun yang pernah melihat totalnya.

Drift ledger adalah lapisan agregat di atas klasifikasi per-request. Seluruhnya deterministik — tidak ada model di jalur ini.

### 4.2 Definisi

Batas reset adalah event BASELINE_ACTIVATED untuk versi aktif, bukan timestamp.

```text
window_start_seq = baselines[active_version].activated_seq

entries = audit.filter(
    type == "SCOPE_CLASSIFICATION_DECIDED" and seq > window_start_seq
).sort_by(seq asc)
```

Setiap entry menampilkan:

```json
{
  "request_id": "req-7",
  "submitted_at": "2026-08-29T02:14:00Z",
  "submitted_by": "client",
  "classification": "IN_SCOPE",
  "decided_by": "freelancer",
  "overridden_model_proposal": false,
  "summary": "Tambah ikon sosial di footer",
  "source_quote": "Footer includes contact details and social links."
}
```

Agregat:

```text
in_scope_additions       = count(entries where classification == "IN_SCOPE")
ambiguous_count          = count(entries where classification == "AMBIGUOUS")
change_request_count     = count(entries where classification == "CHANGE_REQUEST")
days_since_activation    = now - baselines[active_version].activated_at
```

### 4.3 Sinyal

```text
DRIFT_NONE               : in_scope_additions < 5
DRIFT_WATCH              : in_scope_additions >= 5
DRIFT_REVIEW_SUGGESTED   : in_scope_additions >= 8
                           OR (in_scope_additions >= 5 AND days_since_activation >= 14)
```

Konstanta 5, 8, 14 adalah default yang dipilih sembarang dan **MUST** hidup di satu modul config. Angkanya tidak penting; yang penting sinyalnya ada dan bisa disetel. Karena itu:

- UI **MUST** menampilkan angkanya, bukan hanya labelnya. “7 in-scope additions since baseline v1” bisa dinilai sendiri oleh pengguna; `DRIFT_WATCH` tidak.
- Model **MUST NOT** menghitung agregat ini dan **MUST NOT** menyetel ambangnya.

### 4.4 Batasan tegas

- Sinyal drift adalah saran. Ia **MUST NOT** mengubah state deal, memblokir apa pun, atau mengubah klasifikasi yang sudah diputuskan.
- Bahasanya netral. `IN_SCOPE` bukan kesalahan siapa pun. Teks yang benar: “7 additions have accumulated since baseline v1. Consider a scope review.” Teks yang dilarang: apa pun yang menyiratkan klien menyalahgunakan atau freelancer kecolongan.
- Drift ledger **MUST NOT** punya counter tersimpan sendiri. Ironinya nyata: counter tersimpan akan mengalami drift terhadap event log.

### 4.5 Invariant modul C

| ID | Invariant |
| --- | --- |
| C-1 | Agregat 100% turunan dari audit event; tidak ada counter tersimpan. |
| C-2 | Batas jendela adalah activated_seq, bukan timestamp. |
| C-3 | Sinyal tidak pernah mengubah state dan tidak pernah memblokir. |
| C-4 | Ambang ada di satu modul config; model tidak bisa membacanya sebagai instruksi maupun mengubahnya. |
| C-5 | Criterion WITHDRAWN tidak muncul sebagai entry drift. |
| C-6 | Hanya SCOPE_CLASSIFICATION_DECIDED (keputusan manusia) yang masuk hitungan. Usulan model tidak. |

### 4.6 Test vector modul C

| # | Skenario | Ekspektasi |
| --- | --- | --- |
| C-T1 | 4 request IN_SCOPE sejak v1 | DRIFT_NONE, angka 4 tampil |
| C-T2 | 5 request IN_SCOPE | DRIFT_WATCH |
| C-T3 | 8 request IN_SCOPE | DRIFT_REVIEW_SUGGESTED |
| C-T4 | 5 IN_SCOPE, umur baseline 15 hari | DRIFT_REVIEW_SUGGESTED |
| C-T5 | 9 IN_SCOPE, lalu baseline v2 diaktifkan | Kembali DRIFT_NONE, ledger kosong |
| C-T6 | 6 usulan model belum dikonfirmasi manusia | DRIFT_NONE — usulan tidak dihitung |
| C-T7 | Sinyal DRIFT_REVIEW_SUGGESTED aktif | State deal tetap ACTIVE, tidak ada blokir |
| C-T8 | 3 IN_SCOPE + 4 CHANGE_REQUEST | DRIFT_NONE — hanya in-scope yang menumpuk diam-diam |

## 5. MODUL D — Conflict Resolution

### 5.1 Masalah yang diselesaikan

01 §4.1 mendefinisikan CONFLICTING, dan 01 §7 menjadikannya blocker approval. Tapi tidak ada satu pun flow yang menyelesaikannya. Akibatnya jalur bahagia bisa deadlock: field kritis konflik, approval terkunci, dan tidak ada mekanisme untuk membukanya.

Ditambah satu masalah lagi: kalau field konflik tidak masuk top-3 pertanyaan, blocker-nya tidak pernah ditanyakan ke klien. Deadlock sempurna.

### 5.2 Kapan sebuah field boleh berstatus CONFLICTING

Syarat wajib, semuanya:

Ada ≥2 candidate.
Setiap candidate punya source_quote verbatim yang terbukti ada di artifact-nya (lihat §10 — validasi kutipan).
Nilai ter-normalisasi antar candidate berbeda.
Kalau hanya satu candidate punya kutipan valid → bukan konflik. Candidate tanpa kutipan turun menjadi PROPOSED, atau MISSING kalau tak ada kandidat valid sama sekali. Ini mencegah kelas bug paling mahal di sini: model "menemukan" konflik yang tidak ada dan memblokir approval sendiri.

### 5.3 Bentuk data

```json
{
  "field": "timeline.final_deadline",
  "state": "CONFLICTING",
  "candidates": [
    {
      "value": "2026-08-28",
      "source_artifact": "artifact:brief-1",
      "source_quote": "needs to be done Friday",
      "asserted_by": "client"
    },
    {
      "value": "2026-08-31",
      "source_artifact": "artifact:chat-1",
      "source_quote": "eh sebenernya Senin aja gapapa kok",
      "asserted_by": "client"
    }
  ],
  "conflict_severity": 3,
  "resolution": null
}
```

### 5.4 Siapa yang berhak menyelesaikan

| Sumber candidate | Yang berhak memutuskan |
| --- | --- |
| Semua asserted_by: client | Hanya klien. Freelancer tidak boleh memilih di antara dua ucapan kliennya. |
| Klien vs freelancer_policy | Freelancer mengusulkan, klien mengonfirmasi. |
| Semua dari freelancer | Freelancer. |
Baris pertama itu penting dan bukan formalitas: kalau brief bilang Jumat dan screenshot chat bilang Senin, hanya klien yang tahu mana yang berlaku. Sistem yang membiarkan freelancer memilih sudah bukan protokol dua pihak.

### 5.5 Aturan penyelesaian

- Konflik **MUST** ditampilkan sebagai dua candidate bersebelahan, lengkap dengan kutipan dan sumbernya. Klien memilih satu, atau memasukkan nilai ketiga.
- **MUST NOT** ada auto-resolve berbasis kebaruan, panjang teks, urutan artifact, atau confidence model (invariant G-4). Sebuah screenshot chat tidak punya urutan waktu yang bisa dipercaya, dan pesan yang lebih baru belum tentu kesepakatannya.
- Penyelesaian ditulis sebagai event `CONFLICT_RESOLVED`. Candidate asli **MUST** tetap tersimpan selamanya.
- Setelah diselesaikan, state field menjadi `CLIENT_STATED` (kalau klien yang memilih/menyatakan) atau `FREELANCER_POLICY`. Tidak pernah langsung `AGREED` — `AGREED` hanya lewat jalur approval baseline yang normal (invariant G-1).

### 5.6 Anti-deadlock: promosi otomatis ke slot pertanyaan

Ranking pertanyaan yang ada (priority = scope_impact + acceptance_impact + schedule_impact + conflict_severity, ambil top 3) **MUST** ditimpa oleh satu aturan keras:

Setiap field kritis berstatus CONFLICTING **MUST** menempati satu slot pertanyaan, terlepas dari priority hasil hitungan. Kalau field kritis yang konflik lebih dari 3, tampilkan 3 dengan conflict_severity tertinggi dan tandai sisanya sebagai blocker yang menunggu.

Tanpa aturan ini, blocker approval bisa tidak pernah ditanyakan. Batas maksimal 3 pertanyaan aktif tetap berlaku.

### 5.7 Definisi "field kritis" (sebelumnya tidak pernah didefinisikan)

01 §7 memakai istilah "field kritis" sebagai syarat gate tanpa pernah menyebut daftarnya. Gate yang syaratnya tidak terdefinisi akan diimplementasikan tiga cara berbeda. Daftar tertutupnya:

```text
CRITICAL_FIELDS = [
  "deliverables",
  "acceptance_criteria",
  "out_of_scope",
  "timeline.final_deadline",
  "revision_policy.rounds_total"
]
```

`NOT_SET` adalah sentinel **value**, bukan state ketujuh. Field kritis dianggap terpenuhi bila state-nya termasuk `CLIENT_STATED`, `FREELANCER_POLICY`, atau `AGREED`; nilainya boleh `NOT_SET`. `MISSING` berarti informasinya belum ada dan tetap memblokir. `NOT_SET` berarti kedua pihak secara eksplisit sepakat bahwa batas tersebut tidak ditetapkan dan tidak memblokir.

Konflik pada field kritis → memblokir READY_FOR_BASELINE.
Konflik pada field non-kritis → tidak memblokir, tapi **MUST** tampil sebagai peringatan di layar approval dan tercatat di audit.

### 5.8 Konflik yang muncul setelah baseline aktif

Setelah BASELINE_ACTIVATED, kesepakatan sudah beku. Karena itu kontradiksi baru **MUST NOT** menjadi CONFLICTING pada ledger. Ia menjadi request baru yang masuk Guardrail dan diklasifikasi seperti request lain.

CONFLICTING adalah fenomena pra-baseline. Ini menjaga garis batas antara Handshake dan Guardrail tetap tajam, dan mencegah dua modul saling menulis ke state yang sama.

### 5.9 Invariant modul D

| ID | Invariant |
| --- | --- |
| D-1 | CONFLICTING butuh ≥2 candidate berkutipan valid dengan nilai ter-normalisasi berbeda. |
| D-2 | Tidak ada auto-resolve, dengan heuristik apa pun. |
| D-3 | Field kritis yang konflik selalu mendapat slot pertanyaan, menimpa ranking. |
| D-4 | Kewenangan penyelesaian mengikuti matriks §5.4. |
| D-5 | CONFLICT_RESOLVED append-only; candidate asli tersimpan selamanya. |
| D-6 | Model boleh mendeteksi dan menjelaskan konflik; hanya manusia yang menyelesaikan. |
| D-7 | Setelah baseline aktif, kontradiksi baru masuk jalur Guardrail, bukan jalur konflik ledger. |

### 5.10 Test vector modul D

| # | Skenario | Ekspektasi |
| --- | --- | --- |
| D-T1 | Brief "Friday", screenshot "Senin aja gapapa", keduanya terkutip | CONFLICTING, 2 candidate, approval terblokir |
| D-T2 | Lanjut D-T1 | Field menempati slot pertanyaan meski priority rendah |
| D-T3 | Lanjut D-T1, freelancer mencoba memilih | Ditolak — hanya klien yang berwenang |
| D-T4 | Lanjut D-T1, klien memilih Senin | State CLIENT_STATED, nilai 2026-08-31, candidate asli tetap ada |
| D-T5 | Hanya satu candidate punya kutipan valid | Bukan konflik; yang tak terkutip jadi PROPOSED |
| D-T6 | Dua candidate, nilai ter-normalisasi identik | Bukan konflik |
| D-T7 | Konflik pada field non-kritis | Approval jalan, peringatan tampil, tercatat di audit |
| D-T8 | 4 field kritis konflik | 3 jadi pertanyaan, 1 tampil sebagai blocker menunggu |
| D-T9 | Kontradiksi ditemukan setelah baseline aktif | Jadi request Guardrail, bukan CONFLICTING |
| D-T10 | Model mencoba menulis resolution | Ditolak — tidak ada tool untuk itu |

## 6. Interaksi antar modul

Bagian ini ada khusus karena keempat modul dikerjakan paralel. Semua kopling di bawah **MUST** diimplementasikan persis seperti tertulis.

| Pasangan | Aturan |
| --- | --- |
| A ↔ B | REVISION_ROUND_CONSUMED mencatat baseline_version. Kalau naik versi membuat acceptance SUPERSEDED, ronde yang sudah terpakai tidak dikembalikan. Criterion yang sudah `ACCEPTED` atas text hash aktif tidak dapat mengonsumsi ronde, berapa pun `rounds_remaining`; permintaan perubahan berikutnya masuk Guardrail sesuai A-9. |
| A ↔ C | Drift ledger reset pada BASELINE_ACTIVATED. Criterion WITHDRAWN tidak muncul sebagai entry drift. |
| A ↔ D | Konflik hanya hidup pra-baseline. Setelah aktif, pintunya adalah Guardrail (D-7). |
| B ↔ C | CHANGES_REQUESTED yang mengonsumsi ronde bukan entry drift — itu revisi in-scope, bukan penambahan scope. |
| B ↔ D | Habisnya ronde memicu routing ke Guardrail; routing itu tidak menyelesaikan konflik apa pun. |
| C ↔ D | AMBIGUOUS pasca-baseline masuk hitungan drift. Konflik pra-baseline tidak. |
| Semua | Semua modul membaca seq yang sama dan menulis ke audit yang sama. Tidak ada modul yang punya event log sendiri. |

## 7. Audit event log (kontrak bersama)

Seluruh sistem memakai satu collection append-only: deals/{deal_id}/audit/{event_id}.

### 7.1 Envelope wajib

```json
{
  "event_id": "evt_01J...",
  "seq": 42,
  "type": "CRITERION_DECISION",
  "actor": "client",
  "actor_ref": "client_link:9c1f...",
  "baseline_version": 1,
  "created_at": "2026-08-29T02:14:00Z",
  "payload": { }
}
```

actor ∈ {"freelancer", "client", "system", "model"}.

### 7.2 seq — urutan monotonik per deal

seq **MUST** berupa integer monotonik per deal, dialokasikan dari deals/{deal_id}.audit_seq dalam transaksi yang sama dengan penulisan event.

**MUST NOT** memakai created_at atau serverTimestamp() untuk mengurutkan keputusan. Timestamp bisa seri dan bisa miring, dan seluruh modul A bergantung pada "keputusan terakhir". Urutan yang salah = status yang salah, secara sporadis, di production saja. Volume event per deal rendah, jadi batas throughput satu dokumen tidak relevan di sini.

### 7.3 Enum type (himpunan tertutup)

```text
DEAL_CREATED
ARTIFACT_ADDED
LEDGER_DRAFT_SAVED
QUESTIONS_SAVED
CLIENT_ANSWERED
CONFLICT_RESOLVED
BASELINE_PROPOSED
BASELINE_APPROVED          -- aksi klien
BASELINE_ACTIVATED         -- transisi domain service; batas reset drift
REQUEST_SUBMITTED
SCOPE_ANALYSIS_PROPOSED    -- usulan model, tidak pernah dihitung sebagai keputusan
SCOPE_CLASSIFICATION_DECIDED
CHANGE_PROPOSED
CHANGE_APPROVED
EVIDENCE_ADDED
REVIEW_SESSION_OPENED
CRITERION_DECISION         -- ACCEPTED | CHANGES_REQUESTED
REVISION_ROUND_CONSUMED
REVISION_ROUND_GRANTED
PREFERENCE_CANDIDATE_SAVED
PREFERENCE_CONFIRMED
```

BASELINE_APPROVED dan BASELINE_ACTIVATED sengaja dipisah. Approval bisa kedaluwarsa (jalur 409 Conflict di 02); aktivasi adalah transisi yang tervalidasi. Batas reset drift memakai aktivasi, bukan approval.

## 8. Matriks kewenangan (tabel terpenting untuk kerja paralel)

| Aksi | Model | Domain service | Freelancer | Klien |
| --- | --- | --- | --- | --- |
| Usul nilai field ledger | ✅ | — | ✅ | ✅ |
| Tulis state AGREED | ❌ | ✅ (hanya setelah aksi klien yang valid) | ❌ | ❌ |
| Deteksi & jelaskan konflik | ✅ | — | — | — |
| Selesaikan konflik | ❌ | ✅ (mencatat) | matriks §5.4 | matriks §5.4 |
| Usul klasifikasi scope | ✅ | — | — | — |
| Putuskan klasifikasi scope | ❌ | ✅ (mencatat) | ✅ | ❌ |
| Approve baseline | ❌ | ✅ (mencatat) | ❌ | ✅ |
| Aktivasi baseline | ❌ | ✅ | ❌ | ❌ |
| Keputusan criterion | ❌ | ✅ (mencatat) | ❌ | ✅ |
| Konsumsi ronde revisi | ❌ | ✅ (mencatat) | ✅ (memicu) | ❌ |
| Beri goodwill round | ❌ | ✅ (mencatat) | ✅ | ❌ |
| Hitung agregat drift | ❌ | ✅ | ❌ | ❌ |
| Setel ambang drift | ❌ | config saja | ❌ | ❌ |
| Ubah rounds_total | ❌ | ❌ | ❌ | ❌ (hanya lewat baseline baru) |
| Ubah teks criterion | ❌ | ❌ | ❌ | ❌ (hanya lewat baseline baru) |
Kolom Model harus dijamin oleh tool allowlist, bukan oleh prompt. Setiap ❌ di kolom itu berarti tool-nya tidak ada. Tulis satu test yang mengassert daftar tool persis 7 nama dan tidak lebih.

Allowlist normatif itu adalah: `load_deal_context`, `read_artifact`, `save_ledger_draft`, `save_questions`, `save_scope_analysis`, `save_preference_candidate`, dan `validate_quote_candidate`. Audit events selalu ditulis domain service sebagai konsekuensi output tervalidasi; model tidak menerima generic audit-write tool.

## 9. Golden fixture v2 (menggantikan 03 §4)

Perubahan utama dari fixture lama: ada konflik yang disengaja. Fixture lama tidak pernah mengeksekusi CONFLICTING, artinya fitur headline itu tak pernah teruji sampai hari demo.

### 9.1 Artifact

Brief (teks):

Butuh landing page untuk product launch. Make it modern, responsive, dan kelar Jumat. Ada beberapa revisi mungkin. Isinya hero, fitur, dan footer.

Screenshot chat (gambar): percakapan yang memuat, berurutan:

Klien: desainnya desktop dulu ya
Klien: ada contact form juga
Klien: copy-nya bahasa Inggris semua
Klien: eh soal deadline, Senin aja gapapa kok kalau lebih rapi

### 9.2 Hasil yang diharapkan pada ledger

| Field | State | Catatan |
| --- | --- | --- |
| deliverables | CLIENT_STATED | hero, features, footer, contact form |
| timeline.final_deadline | CONFLICTING | Jumat (brief) vs Senin (chat), dua-duanya terkutip |
| revision_policy.rounds_total | MISSING | "beberapa revisi" bukan angka. **MUST NOT** ditebak jadi 2 atau 3. |
| acceptance_criteria.mobile | MISSING | "responsive" tanpa breakpoint |
| acceptance_criteria.form_success | MISSING | perilaku sukses form tak disebut |
| out_of_scope | MISSING | — |

### 9.3 Tiga pertanyaan yang diharapkan

- Deadline — wajib muncul karena aturan promosi konflik §5.6, ditampilkan sebagai dua pilihan berkutipan.
- Batas ronde revisi — angka, karena `MISSING` pada field kritis.
- Definisi selesai untuk contact form, atau breakpoint mobile.

Tiga pertanyaan tersebut adalah prompt berprioritas, bukan satu-satunya jalur input. Portal juga menampilkan seluruh critical-field summary yang dapat diedit. `Confirm project plan` **MUST** tetap nonaktif sampai acceptance criterion lain yang belum ditanyakan dan `out_of_scope` juga dituntaskan.

### 9.4 Baseline v1 setelah klien menjawab

Klien memilih Senin, menyatakan 2 ronde, menyetujui breakpoint 375/768/1440, melengkapi perilaku sukses form, merinci isi footer sebagai contact details dan social links, serta mengisi out-of-scope melalui editable plan.

```yaml
deliverables:
  - "Hero section."
  - "Features section."
  - "Footer includes contact details and social links."
  - "Contact form."
criteria:
  mobile-breakpoints    : "Layout renders correctly at 375px, 768px, and 1440px."
  contact-form-submit   : "Contact form sends a valid submission and shows a success state."
  copy-english          : "All body copy is in English."
timeline.final_deadline : 2026-08-31
revision_policy.rounds_total : 2
out_of_scope:
  - "No social-media asset exports."
  - "No video or motion assets."
  - "No paid-ad copy."
```

### 9.5 Skenario lanjutan (menguji keempat modul dalam satu alur)

| Langkah | Aksi | Yang diuji | Ekspektasi |
| --- | --- | --- | --- |
| Seed | Seed script menulis 4 keputusan manusia `IN_SCOPE` melalui domain service | C + demo setup | drift 4; tidak ada direct Firestore mutation |
| 1 | Klien kirim live "tambah ikon sosial di footer" | Guardrail + C | `IN_SCOPE` (footer ada di baseline), drift 4 → 5 → `DRIFT_WATCH` |
| 2 | Klien kirim "export 3 visual vertikal TikTok" | Guardrail | `CHANGE_REQUEST` + kutipan verbatim `out_of_scope` |
| 3 | Change dikonfirmasi dan baseline v2 diaktifkan | A + C | Criterion hashes tetap; drift reset ke 0. Belum ada acceptance yang diklaim preserved. |
| 4 | Freelancer unggah evidence; client submit review #1: `mobile-breakpoints` dan `copy-english` `ACCEPTED`, `contact-form-submit` `CHANGES_REQUESTED` | A + B | Satu `review_session_id`; belum mengonsumsi ronde |
| 5 | Freelancer mengonfirmasi rework review #1 | B | `rounds_consumed = 1` (bukan 3) |
| 6 | Client submit review #2: `contact-form-submit` tetap `CHANGES_REQUESTED` setelah hasil rework ditinjau | A + B | Keputusan baru atas criterion yang sama tercatat dalam session kedua; dua criterion yang sudah diterima tidak disentuh |
| 7 | Freelancer mengonfirmasi rework review #2 | B | `rounds_consumed = 2`, `rounds_exhausted = true` |
| 8 | Client submit final review dan menerima `contact-form-submit` | A | Ketiga criterion kini `ACCEPTED`; acceptance final untuk masing-masing text hash aktif |
| 9 | Klien meminta perubahan lagi atas salah satu criterion yang sudah diterima | A + B + Guardrail | Otomatis masuk Guardrail; tidak menulis `CHANGES_REQUESTED` baru dan belum berklasifikasi |
| 10 | Baseline v3 hanya mengubah timeline | A | Ketiga acceptance tetap `ACCEPTED` karena criterion hashes identik |
| 11 | Baseline v4 mengubah teks `contact-form-submit` | A | Hanya criterion itu `SUPERSEDED`; dua lainnya tetap `ACCEPTED` |

Langkah 10 dan 11 adalah pasangan korektness terpenting: perubahan baseline yang tidak menyentuh criterion mempertahankan semua acceptance, sedangkan perubahan teks membatalkan tepat criterion yang berubah.

## 10. Yang harus dibekukan sebelum baris kode pertama

Kalau beberapa agent bekerja paralel, empat hal ini **MUST** punya satu pemilik dan tidak boleh diimplementasikan dua kali:

| # | Artefak | Kenapa tidak boleh diparalelkan |
| --- | --- | --- |
| 1 | shared/schemas/ — schema JSON semua field ledger, criteria, event | Agent lain generate dari sini, tidak menafsirkan dari prosa. 06 §1 wajib menjadikan folder ini source of truth pertama. |
| 2 | canonical_json() + sha256() + normalize_criterion_text() | Perbedaan tipis dalam urutan key, penanganan null, format angka, escaping unicode, atau field volatil yang dibuang → hash berbeda → seluruh klaim integritas mati tanpa error. Wajib disertai golden vector: input tetap → string hash persis, di-commit sebelum kode lain ditulis. |
| 3 | Alokasi seq (§7.2) | Dua implementasi berbeda = urutan keputusan berbeda = status salah secara sporadis. |
| 4 | Enum tertutup: type, semua state, CRITICAL_FIELDS, ambang drift | Satu file konstanta, di-import, tidak diketik ulang. |
### Validasi kutipan verbatim

Validasi ini dipakai modul D dan seluruh provenance. `validate_quote_candidate` boleh tersedia sebagai self-check model, tetapi hasil tool itu tidak pernah menjadi gate otoritatif.

Kontrak provenance ini dipakai oleh 02 §4.3. Offset karakter dari LLM dilarang karena mudah meleset dan merusak klaim provenance persis di titik tempat kepercayaan dibutuhkan.

```text
validate_quote(source_quote, artifact_text) -> bool
  normalisasi whitespace kedua sisi (aturan §2.4 langkah 1-4)
  return normalized_quote in normalized_artifact
```

API/worker **MUST** menjalankan `validate_quote` tanpa syarat pada setiap field dari setiap structured model output sebelum draft ditulis. Model tidak dapat melewati gate ini dengan tidak memanggil tool. Kalau hasilnya false, field **MUST** turun ke `PROPOSED` atau `MISSING` dan **MUST NOT** diatribusikan ke klien. Aturannya memberi satu kalimat kuat untuk video: *if the model cannot quote it, the system will not attribute it.*

### Urutan ketergantungan

- Harus lebih dulu, tidak bisa paralel: §10 seluruhnya + pipa cloud kosong (3 Cloud Run, Pub/Sub OIDC, satu panggilan model berhasil dari Cloud Run).
- Boleh lebar setelah itu: modul A, B, C, D, portal klien, UI owner, test suite — semuanya hanya bergantung pada §7, §8, §10.
- Paling akhir: golden path end-to-end, video, submission.

## 11. Sengaja TIDAK ada di MVP

Daftar ini ada supaya sub-agent tidak "melengkapi" desain atas inisiatif sendiri. Semua di bawah **MUST NOT** diimplementasikan:

- Pembayaran, invoice, escrow, mata uang apa pun.
- Acceptance parsial berpersentase. Hanya `ACCEPTED` / `CHANGES_REQUESTED` per criterion.
- Graf ketergantungan antar criterion.
- Deadline per criterion. Hanya ada satu `final_deadline`.
- Auto-resolve konflik, dengan heuristik apa pun.
- Kalibrasi ambang drift secara adaptif/ML.
- Notifikasi selain satu jalur yang sudah ada di 02.
- Verifikasi identitas klien. 07 §E sudah melarang klaimnya; jangan implementasikan setengah jalan.
- Kompensasi/refund untuk criterion `WITHDRAWN`.
- Ronde revisi per deliverable. Ronde bersifat per deal.

### Urutan degradasi submission

Target normatif tetap Modul A–D. Bila build profile harus diturunkan, degradasi hanya boleh dilakukan secara eksplisit dan fitur/claim terkait harus disembunyikan:

1. Lepas Modul C terlebih dahulu; sembunyikan drift panel dan hapus beat drift dari video. Write-path tetap utuh.
2. Lepas Modul B berikutnya; sembunyikan revision counter dan jangan mengklaim automatic exhausted-round routing.
3. Modul D hanya boleh dilepas bersama fixture konflik Friday/Monday dan seluruh beat konflik; kalau fixture konflik dipertahankan tanpa D, golden path akan deadlock.
4. Modul A tidak boleh dilepas selama baseline berversi. Tanpa A, acceptance lintas versi tidak memiliki semantics yang benar.

## 12. Ringkasan test wajib

Minimum yang harus lulus sebelum Gate 3:

| Kelompok | Jumlah | Referensi |
| --- | --- | --- |
| Modul A | 11 | §2.8 |
| Modul B | 8 | §3.7 |
| Modul C | 8 | §4.6 |
| Modul D | 10 | §5.10 |
| Golden hash vector | ≥3 | §10 #2 |
| Tool allowlist tepat 7 nama | 1 | §8 |
| Injection lewat jawaban klien mendarat sebagai data | 1 | US-8 |
| Readiness sentinel + mandatory server quote gate | 2 | X-T1, X-T2 di bawah |
| Alur fixture Seed + 11 langkah end-to-end | 1 | §9.5 |

- **X-T1:** `rounds_total` dengan state valid dan value `NOT_SET` tidak memblokir readiness; field yang sama berstatus `MISSING` memblokir.
- **X-T2:** simulated model output tidak memanggil `validate_quote_candidate` dan membawa invalid `source_quote`; server tetap menjalankan validation, menurunkan field ke `PROPOSED`/`MISSING`, dan tidak menulis atribusi client.

Total 45 test. Seluruh unit/contract test deterministik dan tidak memerlukan live model; fixture end-to-end tetap menjalankan integrasi model/cloud sesungguhnya.
