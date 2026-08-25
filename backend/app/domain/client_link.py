"""Aturan client link — opaque, scoped, expiring, tanpa akun (02-ARCHITECTURE §8).

Fungsi murni: `now` selalu parameter, tidak pernah dibaca dari jam sistem di
sini, supaya validasi deterministik dan bisa diuji tanpa mocking waktu.
Pembuatan/penyimpanan token (butuh acak dan Firestore) ada di
app/client_links.py, bukan di sini -- modul ini tidak tahu apa-apa soal
penyimpanan.
"""

# 02 §3 "Web": clarification, approval, delivery review, new-request
# submission. Belum ada di 09-DOMAIN-RULES sebagai enum normatif; ini
# himpunan tertutup yang didefinisikan di sini karena harus ada satu.
PURPOSES = frozenset(
    {"CLARIFICATION", "APPROVAL", "DELIVERY_REVIEW", "NEW_REQUEST"}
)


def check(link, now, purpose, action):
    """(valid, reason) -- reason bahasa netral (G-7), tidak menuduh pihak mana pun.

    `link`: {deal_id, purpose, allowed_actions, expires_at, revoked_at,
    completed_at} -- expires_at/revoked_at/completed_at datetime aware atau
    None (kecuali expires_at, selalu ada). `now`: datetime aware.
    """
    if link is None:
        return False, "This link is not valid."
    if link["revoked_at"] is not None:
        return False, "This link has been revoked."
    if link["completed_at"] is not None:
        return False, "This link has already been used for its purpose."
    if now >= link["expires_at"]:
        return False, "This link has expired."
    if link["purpose"] != purpose:
        return False, "This link is not valid for this action."
    if action not in link["allowed_actions"]:
        return False, "This link does not allow this action."
    return True, ""
