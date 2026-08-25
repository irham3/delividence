"""Verifikasi Firebase ID token untuk endpoint owner (02 §8, 06 §6).

Client portal (`/client/{token}/...`) TIDAK lewat sini -- itu diamankan
lewat opaque token sendiri (`app/client_links.py`), bukan akun Firebase.
Modul ini hanya untuk endpoint yang diakses langsung oleh freelancer/owner
dari `web/`.
"""

from fastapi import Header, HTTPException

from app import config

_firebase_app = None


def _app():
    global _firebase_app
    if _firebase_app is None:
        import firebase_admin
        from firebase_admin import credentials

        _firebase_app = firebase_admin.initialize_app(
            credentials.ApplicationDefault(), {"projectId": config.FIREBASE_PROJECT_ID}
        )
    return _firebase_app


def require_owner(authorization: str = Header(default="")) -> str:
    """Dependency FastAPI -- mengembalikan `uid` Firebase sebagai `owner_id`.

    401 kalau header hilang/salah bentuk atau token tidak valid/kedaluwarsa.
    `owner_id` yang dikembalikan di sini yang dipercaya untuk isolasi data
    per owner (02 §8) -- endpoint TIDAK PERNAH membaca `owner_id` dari body
    request.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    token = authorization[len("Bearer "):].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    from firebase_admin import auth as firebase_auth

    try:
        decoded = firebase_auth.verify_id_token(token, app=_app())
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired ID token") from e
    return decoded["uid"]
