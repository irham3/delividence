import { describe, expect, it } from "vitest";
import { fieldSummary } from "./ledger-summary";

describe("fieldSummary", () => {
  it("summarises a plain ledger field with its state and source", () => {
    expect(
      fieldSummary({ value: "Thursday", state: "CLIENT_STATED", source_artifact: "artifact:brief-1" }),
    ).toBe("Thursday · CLIENT_STATED · artifact:brief-1");
  });

  it("counts list values instead of dumping them", () => {
    expect(fieldSummary({ value: [{ id: "d1" }, { id: "d2" }], state: "CLIENT_STATED" })).toBe(
      "2 item(s) · CLIENT_STATED",
    );
  });

  it("reports nested groups instead of claiming they hold no value", () => {
    // Ketemu 29 Agu di production: `timeline` dan `revision_policy` adalah
    // wadah berisi sub-field, bukan field tunggal. Versi lama membacanya
    // sebagai satu field dan selalu menulis "No value" walaupun datanya ada.
    expect(
      fieldSummary({
        rounds_total: { value: 2, state: "FREELANCER_POLICY", source_artifact: "artifact:policy-1" },
      }),
    ).toBe("rounds total: 2 · FREELANCER_POLICY · artifact:policy-1");

    expect(
      fieldSummary({ final_deadline: { value: "Thursday", state: "CLIENT_STATED" } }),
    ).toBe("final deadline: Thursday · CLIENT_STATED");
  });

  it("keeps a zero value visible rather than calling it empty", () => {
    expect(fieldSummary({ value: 0, state: "CLIENT_STATED" })).toBe("0 · CLIENT_STATED");
  });

  it("falls back cleanly when there is nothing to describe", () => {
    expect(fieldSummary(null)).toBe("No extracted value.");
    expect(fieldSummary({})).toBe("No value");
  });
});
