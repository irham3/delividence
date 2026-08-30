import { describe, expect, it } from "vitest";
import type { OwnerRun } from "./api";
import { indexColumnHeader, indexColumnValue, relativeTime } from "./record-columns";

const NOW = new Date("2026-08-30T10:00:00Z");

function run(overrides: Partial<OwnerRun> = {}): OwnerRun {
  return {
    run_id: "r1",
    status: "done",
    brief: "brief",
    output_language: "en",
    round: 1,
    created_at: "2026-08-30T09:00:00Z",
    updated_at: "2026-08-30T09:30:00Z",
    ...overrides,
  };
}

describe("kolom daftar per halaman", () => {
  it("tiap halaman punya header sendiri, tidak ada yang kembar", () => {
    const headers = (["records", "sources", "review", "activity"] as const).map(indexColumnHeader);
    expect(new Set(headers).size).toBe(4);
  });

  it("Records menampilkan versi baseline", () => {
    expect(indexColumnValue("records", run({ active_baseline_version: 2 }), NOW)).toBe("v2");
    expect(indexColumnValue("records", run(), NOW)).toBe("Draft");
  });

  it("Sources menghitung field ledger hasil ekstraksi", () => {
    const ledger = { deliverables: { value: [], state: "CLIENT_STATED" }, assumptions: { value: [], state: "CLIENT_STATED" } };
    expect(indexColumnValue("sources", run({ ledger }), NOW)).toBe("2 fields");
    expect(indexColumnValue("sources", run(), NOW)).toBe("Nothing yet");
  });

  it("Review menghitung acceptance criteria", () => {
    const one = { acceptance_criteria: { value: [{ deliverable_id: "d1", criterion_key: "k", text: "t" }], state: "CLIENT_STATED" } };
    expect(indexColumnValue("review", run({ ledger: one }), NOW)).toBe("1 criterion");
    expect(indexColumnValue("review", run(), NOW)).toBe("None yet");
  });

  it("Activity menampilkan jarak waktu update terakhir", () => {
    expect(indexColumnValue("activity", run({ updated_at: "2026-08-30T09:59:30Z" }), NOW)).toBe("Just now");
    expect(indexColumnValue("activity", run({ updated_at: "2026-08-30T09:30:00Z" }), NOW)).toBe("30m ago");
    expect(indexColumnValue("activity", run({ updated_at: "2026-08-29T10:00:00Z" }), NOW)).toBe("1d ago");
    expect(relativeTime(undefined, NOW)).toBe("Unknown");
  });
});
