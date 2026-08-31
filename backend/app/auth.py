"""Verifikasi Firebase ID token untuk endpoint owner (02 §8, 06 §6).

Client portal (`/client/{token}/...`) TIDAK lewat sini -- itu diamankan
lewat opaque token sendiri (`app/client_links.py`), bukan akun Firebase.
Modul ini hanya untuk endpoint yang diakses langsung oleh freelancer/owner
dari `web/`.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Header, HTTPException

from app import config

_firebase_app = None


def _firebase_auth_module():
    from firebase_admin import auth as firebase_auth
    return firebase_auth


def _firebase_admin_module():
    import firebase_admin
    return firebase_admin


def _firebase_credential():
    """Return the least-privileged credential allowed to mint sessions.

    Production runs as the Cloud Run API service account. Local development
    can impersonate that same identity instead of granting Firebase Auth admin
    permissions to every developer's personal Google account.
    """
    from firebase_admin import credentials

    target_principal = config.FIREBASE_SESSION_COOKIE_SERVICE_ACCOUNT
    if not target_principal:
        return credentials.ApplicationDefault()

    import google.auth
    from google.auth import impersonated_credentials

    source_credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    # A developer's ADC can retain an unrelated quota project.  Pin the
    # impersonation request to the Firebase project instead, so the IAM
    # Credentials API is consumed by the project that owns this application.
    if config.FIREBASE_PROJECT_ID and hasattr(source_credentials, "with_quota_project"):
        source_credentials = source_credentials.with_quota_project(config.FIREBASE_PROJECT_ID)
    impersonated = impersonated_credentials.Credentials(
        source_credentials=source_credentials,
        target_principal=target_principal,
        target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
        quota_project_id=config.FIREBASE_PROJECT_ID or None,
    )
    # firebase-admin accepts a google.auth credential through this wrapper.
    # It keeps the user ADC out of Firebase Auth administration calls.
    return credentials._ExternalCredentials(impersonated)


def _app():
    global _firebase_app
    if _firebase_app is None:
        _firebase_app = _firebase_admin_module().initialize_app(
            _firebase_credential(), {"projectId": config.FIREBASE_PROJECT_ID}
        )
    return _firebase_app


def _bearer_token(authorization: str) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    token = authorization[len("Bearer "):].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    return token


def verify_owner_token(authorization: str) -> tuple[str, dict[str, Any]]:
    """Verifikasi bearer token sekali dan kembalikan token + claims."""
    token = _bearer_token(authorization)

    try:
        decoded = _firebase_auth_module().verify_id_token(token, app=_app())
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired ID token") from e
    if not decoded.get("uid"):
        raise HTTPException(status_code=401, detail="ID token is missing its owner identity")
    return token, decoded


def require_owner(authorization: str = Header(default="")) -> str:
    """Dependency FastAPI -- mengembalikan `uid` Firebase sebagai `owner_id`.

    401 kalau header hilang/salah bentuk atau token tidak valid/kedaluwarsa.
    `owner_id` yang dikembalikan di sini yang dipercaya untuk isolasi data
    per owner (02 §8) -- endpoint TIDAK PERNAH membaca `owner_id` dari body
    request.
    """
    _, decoded = verify_owner_token(authorization)
    return decoded["uid"]


def create_owner_session_cookie(authorization: str) -> str:
    """Tukar ID token yang baru dipakai login dengan Firebase session cookie.

    Cookie dikirim hanya ke route handler Next.js; browser menerimanya sebagai
    HttpOnly sehingga JavaScript aplikasi tidak bisa membaca atau mengubahnya.
    """
    token, decoded = verify_owner_token(authorization)
    auth_time = decoded.get("auth_time")
    now = datetime.now(timezone.utc).timestamp()
    if not isinstance(auth_time, (int, float)) or now - auth_time > config.SESSION_COOKIE_RECENT_SIGN_IN_SECONDS:
        raise HTTPException(status_code=401, detail="A recent sign-in is required")

    try:
        return _firebase_auth_module().create_session_cookie(
            token,
            expires_in=timedelta(seconds=config.SESSION_COOKIE_MAX_AGE_SECONDS),
            app=_app(),
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail="Could not create owner session") from e
