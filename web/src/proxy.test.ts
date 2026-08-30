import { NextRequest } from "next/server";
import { getRedirectUrl, unstable_doesMiddlewareMatch } from "next/experimental/testing/server";
import { describe, expect, it } from "vitest";
import { config, proxy } from "./proxy";

describe("proxy route guard", () => {
  it("matches owner and auth routes but skips public/client routes", () => {
    expect(unstable_doesMiddlewareMatch({ config, nextConfig: {}, url: "/records/run-1" })).toBe(true);
    expect(unstable_doesMiddlewareMatch({ config, nextConfig: {}, url: "/sign-in" })).toBe(true);
    expect(unstable_doesMiddlewareMatch({ config, nextConfig: {}, url: "/" })).toBe(false);
    expect(unstable_doesMiddlewareMatch({ config, nextConfig: {}, url: "/client/token" })).toBe(false);
  });

  it("redirects an unauthenticated deep link and retains its query", async () => {
    const response = await proxy(
      new NextRequest("https://delividence.test/records/run-1?tab=evidence"),
    );
    expect(getRedirectUrl(response)).toBe(
      "https://delividence.test/sign-in?next=%2Frecords%2Frun-1%3Ftab%3Devidence",
    );
  });

  it("allows the sign-in page without a session", async () => {
    const response = await proxy(new NextRequest("https://delividence.test/sign-in"));
    expect(getRedirectUrl(response)).toBeNull();
  });
});
