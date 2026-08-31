import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DELETE, POST } from "./route";

afterEach(() => vi.unstubAllGlobals());

describe("owner session route", () => {
  it("forwards the ID token and sets an HttpOnly same-origin cookie", async () => {
    const backendFetch = vi.fn().mockResolvedValue(
      Response.json({ session_cookie: "signed-cookie", expires_in: 3600 }),
    );
    vi.stubGlobal("fetch", backendFetch);
    const request = new NextRequest("http://localhost:3000/api/auth/session", {
      method: "POST",
      headers: {
        origin: "http://localhost:3000",
        authorization: "Bearer firebase-token",
      },
    });

    const response = await POST(request);

    expect(response.status).toBe(200);
    expect(backendFetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/auth\/session$/),
      expect.objectContaining({
        method: "POST",
        headers: { Authorization: "Bearer firebase-token" },
      }),
    );
    expect(response.headers.get("set-cookie")).toContain("delividence_session=signed-cookie");
    expect(response.headers.get("set-cookie")).toContain("HttpOnly");
    expect(response.headers.get("set-cookie")).toContain("SameSite=lax");
    expect(response.headers.get("set-cookie")).not.toContain("Secure");
  });

  it("marks the session cookie Secure behind HTTPS", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(Response.json({ session_cookie: "signed", expires_in: 3600 })),
    );
    const response = await POST(
      new NextRequest("https://delividence.test/api/auth/session", {
        method: "POST",
        headers: {
          origin: "https://delividence.test",
          authorization: "Bearer firebase-token",
        },
      }),
    );
    expect(response.headers.get("set-cookie")).toContain("Secure");
  });

  it("rejects cross-origin attempts", async () => {
    const response = await POST(
      new NextRequest("https://delividence.test/api/auth/session", {
        method: "POST",
        headers: { origin: "https://evil.test", authorization: "Bearer token" },
      }),
    );
    expect(response.status).toBe(403);
  });

  it("explains when the backend has not been upgraded yet", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(Response.json({ detail: "Not Found" }, { status: 404 })),
    );
    const response = await POST(
      new NextRequest("http://localhost:3000/api/auth/session", {
        method: "POST",
        headers: {
          origin: "http://localhost:3000",
          authorization: "Bearer firebase-token",
        },
      }),
    );
    expect(response.status).toBe(404);
    await expect(response.json()).resolves.toEqual({
      error:
        "The authentication service is running an older release. Restart or redeploy the backend, then try again.",
    });
  });

  it("does not mislabel a server session-creation failure as a Google failure", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        Response.json({ detail: "Could not create owner session" }, { status: 401 }),
      ),
    );
    const response = await POST(
      new NextRequest("http://localhost:3000/api/auth/session", {
        method: "POST",
        headers: {
          origin: "http://localhost:3000",
          authorization: "Bearer firebase-token",
        },
      }),
    );
    expect(response.status).toBe(401);
    await expect(response.json()).resolves.toEqual({
      error: "The server could not create a secure session. Please try signing in again.",
    });
  });

  it("expires the route cookie on logout", async () => {
    const response = await DELETE(
      new NextRequest("http://localhost:3000/api/auth/session", { method: "DELETE" }),
    );
    expect(response.status).toBe(204);
    expect(response.headers.get("set-cookie")).toContain("delividence_session=");
    expect(response.headers.get("set-cookie")).toContain("Max-Age=0");
  });
});
