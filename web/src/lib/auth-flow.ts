type TokenUser = { getIdToken: (forceRefresh?: boolean) => Promise<string> };

export async function establishOwnerSession(user: TokenUser) {
  const idToken = await user.getIdToken(true);
  const response = await fetch("/api/auth/session", {
    method: "POST",
    headers: { Authorization: `Bearer ${idToken}` },
  });
  if (!response.ok) {
    const payload = (await response.json().catch(() => ({}))) as { error?: string };
    throw new Error(payload.error || "The sign-in session could not be established.");
  }
}

export async function signOutAndEndSession(signOut: () => Promise<void>) {
  const response = await fetch("/api/auth/session", { method: "DELETE" });
  if (!response.ok) throw new Error("Could not clear the browser session. Please try again.");
  await signOut();
}
