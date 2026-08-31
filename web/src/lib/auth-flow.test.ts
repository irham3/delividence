import { afterEach, describe, expect, it, vi } from "vitest";
import { establishOwnerSession, signOutAndEndSession } from "./auth-flow";

afterEach(() => vi.unstubAllGlobals());

describe("establishOwnerSession", () => {
  it("exchanges a fresh Firebase ID token for the server session", async () => {
    const getIdToken = vi.fn().mockResolvedValue("firebase-id-token");
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    await establishOwnerSession({ getIdToken });

    expect(getIdToken).toHaveBeenCalledWith(true);
    expect(fetchMock).toHaveBeenCalledWith("/api/auth/session", {
      method: "POST",
      headers: { Authorization: "Bearer firebase-id-token" },
    });
  });

  it("reports a failed session exchange", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(Response.json({ error: "A recent sign-in is required." }, { status: 401 })),
    );
    await expect(establishOwnerSession({ getIdToken: async () => "stale" })).rejects.toThrow(
      "A recent sign-in is required.",
    );
  });
});

describe("signOutAndEndSession", () => {
  it("clears the server cookie before signing out of Firebase", async () => {
    const calls: string[] = [];
    vi.stubGlobal("fetch", vi.fn(async () => {
      calls.push("cookie");
      return new Response(null, { status: 204 });
    }));
    await signOutAndEndSession(async () => { calls.push("firebase"); });
    expect(calls).toEqual(["cookie", "firebase"]);
  });

  it("keeps the Firebase login when clearing the cookie fails", async () => {
    const signOut = vi.fn();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(null, { status: 500 })));
    await expect(signOutAndEndSession(signOut)).rejects.toThrow("Could not clear");
    expect(signOut).not.toHaveBeenCalled();
  });
});
