import { decodeProtectedHeader, importX509, jwtVerify } from "jose";

export const OWNER_SESSION_COOKIE = "delividence_session";

const FIREBASE_PUBLIC_CERTS =
  "https://www.googleapis.com/identitytoolkit/v3/relyingparty/publicKeys";

type CertificateMap = Record<string, string>;

export async function verifyOwnerSessionCookie(cookie: string) {
  const projectId = process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID;
  if (!projectId) return false;

  try {
    const { kid, alg } = decodeProtectedHeader(cookie);
    if (!kid || alg !== "RS256") return false;

    const response = await fetch(FIREBASE_PUBLIC_CERTS, { cache: "force-cache" });
    if (!response.ok) return false;
    const certificates = (await response.json()) as CertificateMap;
    const certificate = certificates[kid];
    if (!certificate) return false;

    const publicKey = await importX509(certificate, "RS256");
    const { payload } = await jwtVerify(cookie, publicKey, {
      algorithms: ["RS256"],
      audience: projectId,
      issuer: `https://session.firebase.google.com/${projectId}`,
    });
    return typeof payload.sub === "string" && payload.sub.length > 0;
  } catch {
    return false;
  }
}
