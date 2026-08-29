// Ringkasan satu baris untuk field ledger di halaman Source record.
//
// Dipisahkan dari owner-routes.tsx supaya bisa diuji tanpa merender React:
// bug yang memicu pemisahan ini (29 Agu) murni soal bentuk data, bukan UI.

export type LedgerLeaf = { value?: unknown; state?: string; source_artifact?: string };

// Sebuah field ledger yang sesungguhnya selalu membawa `state`/`value`.
// `timeline` dan `revision_policy` BUKAN field seperti itu -- keduanya wadah
// berisi sub-field (`final_deadline`, `rounds_total`).
export function isLedgerLeaf(value: unknown): value is LedgerLeaf {
  return !!value && typeof value === "object" && ("state" in value || "value" in value);
}

export function leafSummary(field: LedgerLeaf) {
  const raw = Array.isArray(field.value)
    ? `${field.value.length} item(s)`
    : typeof field.value === "string"
      ? field.value
      : typeof field.value === "number"
        ? String(field.value)
        : field.value
          ? "Value recorded"
          : "No value";
  return `${raw}${field.state ? ` · ${field.state}` : ""}${field.source_artifact ? ` · ${field.source_artifact}` : ""}`;
}

export function fieldSummary(value: unknown) {
  if (!value || typeof value !== "object") return "No extracted value.";
  if (isLedgerLeaf(value)) return leafSummary(value);
  // Wadah bersarang: rangkum tiap sub-field. Sebelum ini seluruh wadah
  // dianggap satu field, sehingga `timeline` dan `revision_policy` selalu
  // tampil "No value" padahal datanya ada -- termasuk rounds_total yang
  // distage dari preference freelancer (ketemu 29 Agu di production).
  const entries = Object.entries(value as Record<string, unknown>).filter(([, sub]) => isLedgerLeaf(sub));
  if (!entries.length) return "No value";
  return entries.map(([key, sub]) => `${key.replaceAll("_", " ")}: ${leafSummary(sub as LedgerLeaf)}`).join(" · ");
}
