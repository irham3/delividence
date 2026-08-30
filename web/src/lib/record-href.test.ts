import { describe, expect, it } from "vitest";
import { DETAIL_SECTIONS, isDetailSection, recordHref } from "./record-href";

const RUN = "4614384828ff4458b014c6a21e0fd262";

describe("recordHref", () => {
  it("mengirim halaman Records ke halaman record, bukan ke section /records yang tidak ada", () => {
    expect(recordHref("records", RUN)).toBe(`/records/${RUN}`);
  });

  it("memetakan Review ke section evidence", () => {
    expect(recordHref("review", RUN)).toBe(`/records/${RUN}/evidence`);
  });

  it("memakai nama section apa adanya untuk Sources dan Activity", () => {
    expect(recordHref("sources", RUN)).toBe(`/records/${RUN}/sources`);
    expect(recordHref("activity", RUN)).toBe(`/records/${RUN}/activity`);
  });

  it("setiap mode daftar menghasilkan URL yang bisa dilayani route (tidak 404)", () => {
    for (const mode of ["records", "sources", "review", "activity"] as const) {
      const section = recordHref(mode, RUN).slice(`/records/${RUN}`.length).replace(/^\//, "");
      expect(section === "" || isDetailSection(section)).toBe(true);
    }
  });

  it("menolak section yang tidak dikenal", () => {
    expect(isDetailSection("records")).toBe(false);
    expect(DETAIL_SECTIONS).toContain("baseline");
  });
});
