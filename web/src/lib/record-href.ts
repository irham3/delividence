// Satu sumber kebenaran untuk section detail record: dipakai route
// app/records/[runId]/[section]/page.tsx untuk memvalidasi URL, dan dipakai
// recordHref() untuk merakit URL dari halaman daftar. Sebelum ini keduanya
// terpisah, sehingga halaman Records merakit /records/{id}/records -- section
// yang tidak pernah ada, dan setiap baris berakhir 404.
export const DETAIL_SECTIONS = ["sources", "questions", "baseline", "evidence", "activity", "requests"] as const;
export type DetailSection = (typeof DETAIL_SECTIONS)[number];

export function isDetailSection(value: string): value is DetailSection {
  return (DETAIL_SECTIONS as readonly string[]).includes(value);
}

/** Tujuan klik satu baris di halaman daftar owner. "records" tidak punya
 *  section sendiri -- halaman record utamanya yang dituju. */
export function recordHref(mode: "records" | "sources" | "review" | "activity", runId: string) {
  if (mode === "records") return `/records/${runId}`;
  return `/records/${runId}/${mode === "review" ? "evidence" : mode}`;
}
