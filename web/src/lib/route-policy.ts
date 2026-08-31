export const OWNER_HOME_PATH = "/workspace";
export const AUTH_ROUTES = ["/sign-in", "/register"] as const;

const OWNER_ROUTE_PREFIXES = [
  "/workspace",
  "/records",
  "/sources",
  "/review",
  "/activity",
  "/settings",
] as const;

export function isOwnerRoute(pathname: string) {
  return OWNER_ROUTE_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`),
  );
}

export function safeOwnerDestination(candidate?: string | null) {
  if (!candidate || !candidate.startsWith("/") || candidate.startsWith("//")) {
    return OWNER_HOME_PATH;
  }

  try {
    const parsed = new URL(candidate, "https://delividence.local");
    if (parsed.origin !== "https://delividence.local" || !isOwnerRoute(parsed.pathname)) {
      return OWNER_HOME_PATH;
    }
    return `${parsed.pathname}${parsed.search}${parsed.hash}`;
  } catch {
    return OWNER_HOME_PATH;
  }
}

export function signInHref(destination: string) {
  const safeDestination = safeOwnerDestination(destination);
  return `/sign-in?next=${encodeURIComponent(safeDestination)}`;
}
