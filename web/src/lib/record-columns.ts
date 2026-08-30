import type { OwnerRun } from "./api";

// Keempat halaman daftar owner memakai tabel yang sama. Supaya tidak terlihat
// sebagai empat halaman duplikat, kolom ketiga menjawab pertanyaan khas
// halamannya masing-masing -- semuanya dari read model /runs yang sudah ada,
// tanpa endpoint baru.
export type IndexColumnMode = "records" | "sources" | "review" | "activity";

const HEADERS: Record<IndexColumnMode, string> = {
  records: "Baseline",
  sources: "Extracted",
  review: "Criteria",
  activity: "Last update",
};

export function indexColumnHeader(mode: IndexColumnMode) {
  return HEADERS[mode];
}

export function indexColumnValue(mode: IndexColumnMode, record: OwnerRun, now: Date = new Date()) {
  if (mode === "records") return record.active_baseline_version ? `v${record.active_baseline_version}` : "Draft";
  if (mode === "sources") {
    const fields = Object.keys(record.ledger ?? {}).length;
    return fields ? `${fields} field${fields === 1 ? "" : "s"}` : "Nothing yet";
  }
  if (mode === "review") {
    const criteria = record.ledger?.acceptance_criteria?.value?.length ?? 0;
    return criteria ? `${criteria} criteri${criteria === 1 ? "on" : "a"}` : "None yet";
  }
  return relativeTime(record.updated_at, now);
}

export function relativeTime(iso: string | undefined, now: Date) {
  if (!iso) return "Unknown";
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "Unknown";
  const minutes = Math.floor((now.getTime() - then) / 60000);
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}
