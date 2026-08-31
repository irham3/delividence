import { NextRequest, NextResponse } from "next/server";
import { API } from "@/lib/api";
import { OWNER_SESSION_COOKIE } from "@/lib/firebase-session";

type SessionResponse = { session_cookie?: unknown; expires_in?: unknown; detail?: unknown };

function sessionFailure(status: number, payload: SessionResponse) {
  if (status === 404) {
    return "The authentication service is running an older release. Restart or redeploy the backend, then try again.";
  }
  if (status === 401 && payload.detail === "A recent sign-in is required") {
    return "Google needs a fresh sign-in. Choose your account again to continue.";
  }
  if (status === 401 && payload.detail === "Could not create owner session") {
    return "The server could not create a secure session. Please try signing in again.";
  }
  if (status === 401) {
    return "Google could not verify this sign-in. Choose your account again to continue.";
  }
  return "The sign-in session could not be established. Please try again.";
}

function sameOrigin(request: NextRequest) {
  const origin = request.headers.get("origin");
  return !origin || origin === request.nextUrl.origin;
}

function isSecureRequest(request: NextRequest) {
  return request.nextUrl.protocol === "https:" || request.headers.get("x-forwarded-proto") === "https";
}

export async function POST(request: NextRequest) {
  if (!sameOrigin(request)) {
    return NextResponse.json({ error: "Cross-origin session request rejected." }, { status: 403 });
  }

  const authorization = request.headers.get("authorization");
  if (!authorization?.startsWith("Bearer ")) {
    return NextResponse.json({ error: "Missing Firebase ID token." }, { status: 401 });
  }

  try {
    const backendResponse = await fetch(`${API}/auth/session`, {
      method: "POST",
      headers: { Authorization: authorization },
      cache: "no-store",
      signal: AbortSignal.timeout(10_000),
    });
    const payload = (await backendResponse.json().catch(() => ({}))) as SessionResponse;
    if (
      !backendResponse.ok ||
      typeof payload.session_cookie !== "string" ||
      typeof payload.expires_in !== "number"
    ) {
      return NextResponse.json(
        { error: sessionFailure(backendResponse.status, payload) },
        { status: backendResponse.status >= 400 ? backendResponse.status : 502 },
      );
    }

    const response = NextResponse.json({ ok: true });
    response.headers.set("Cache-Control", "no-store");
    response.cookies.set(OWNER_SESSION_COOKIE, payload.session_cookie, {
      httpOnly: true,
      secure: isSecureRequest(request),
      sameSite: "lax",
      maxAge: payload.expires_in,
      path: "/",
      priority: "high",
    });
    return response;
  } catch {
    return NextResponse.json(
      { error: "The authentication service is temporarily unavailable." },
      { status: 502 },
    );
  }
}

export async function DELETE(request: NextRequest) {
  if (!sameOrigin(request)) {
    return NextResponse.json({ error: "Cross-origin session request rejected." }, { status: 403 });
  }

  const response = new NextResponse(null, { status: 204 });
  response.cookies.set(OWNER_SESSION_COOKIE, "", {
    httpOnly: true,
    secure: isSecureRequest(request),
    sameSite: "lax",
    maxAge: 0,
    path: "/",
  });
  return response;
}
