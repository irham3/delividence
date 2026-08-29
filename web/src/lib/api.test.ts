import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError, apiFetch, setAuthTokenProvider } from "./api";

const fetchMock = vi.fn();

describe("apiFetch", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock);
    setAuthTokenProvider(async () => null);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    fetchMock.mockReset();
  });

  it("adds a Firebase owner token only when the owner is signed in", async () => {
    setAuthTokenProvider(async () => "signed-owner-token");
    fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({ run_id: "run-1" }), { status: 200 }));

    await expect(apiFetch<{ run_id: string }>("/runs", { method: "POST", body: "{}" })).resolves.toEqual({ run_id: "run-1" });
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8080/runs",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          "Content-Type": "application/json",
          Authorization: "Bearer signed-owner-token",
        }),
      }),
    );
  });

  it("keeps tokenless client-link requests tokenless", async () => {
    fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({ ready: true }), { status: 200 }));

    await apiFetch("/client/opaque-link");

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(init.headers).toEqual({ "Content-Type": "application/json" });
  });

  it("preserves HTTP status and backend detail for UI recovery", async () => {
    fetchMock.mockResolvedValueOnce(new Response("The record belongs to another owner.", { status: 403, statusText: "Forbidden" }));

    await expect(apiFetch("/runs/not-yours")).rejects.toEqual(
      expect.objectContaining<ApiError>({
        name: "ApiError",
        status: 403,
        message: "403 Forbidden: The record belongs to another owner.",
      }),
    );
  });

  it("returns undefined for a successful empty response", async () => {
    fetchMock.mockResolvedValueOnce(new Response(null, { status: 204 }));

    await expect(apiFetch<void>("/client/link/revoke", { method: "POST" })).resolves.toBeUndefined();
  });
});
