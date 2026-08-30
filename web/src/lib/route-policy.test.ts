import { describe, expect, it } from "vitest";
import { isOwnerRoute, safeOwnerDestination, signInHref } from "./route-policy";

describe("route policy", () => {
  it.each(["/workspace", "/records", "/records/run-1", "/settings/policies"])(
    "recognizes protected route %s",
    (pathname) => expect(isOwnerRoute(pathname)).toBe(true),
  );

  it.each(["https://evil.test/x", "//evil.test/x", "/client/token", "/sign-in"])(
    "rejects unsafe next destination %s",
    (candidate) => expect(safeOwnerDestination(candidate)).toBe("/workspace"),
  );

  it("preserves protected path, query, and hash", () => {
    expect(safeOwnerDestination("/records/run-1?tab=proof#criterion-2")).toBe(
      "/records/run-1?tab=proof#criterion-2",
    );
    expect(signInHref("/records/run-1?tab=proof")).toBe(
      "/sign-in?next=%2Frecords%2Frun-1%3Ftab%3Dproof",
    );
  });
});
