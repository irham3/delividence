import { NextRequest, NextResponse } from "next/server";
import { OWNER_SESSION_COOKIE, verifyOwnerSessionCookie } from "@/lib/firebase-session";
import { AUTH_ROUTES, isOwnerRoute, safeOwnerDestination, signInHref } from "@/lib/route-policy";

export async function proxy(request: NextRequest) {
  const { pathname, searchParams } = request.nextUrl;
  const sessionCookie = request.cookies.get(OWNER_SESSION_COOKIE)?.value;
  const authenticated = sessionCookie ? await verifyOwnerSessionCookie(sessionCookie) : false;

  if (isOwnerRoute(pathname) && !authenticated) {
    const destination = `${pathname}${request.nextUrl.search}`;
    const response = NextResponse.redirect(new URL(signInHref(destination), request.url));
    if (sessionCookie) response.cookies.delete(OWNER_SESSION_COOKIE);
    return response;
  }

  if (AUTH_ROUTES.includes(pathname as (typeof AUTH_ROUTES)[number]) && authenticated) {
    return NextResponse.redirect(
      new URL(safeOwnerDestination(searchParams.get("next")), request.url),
    );
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/workspace",
    "/records/:path*",
    "/sources",
    "/review",
    "/activity",
    "/settings/:path*",
    "/sign-in",
    "/register",
  ],
};
