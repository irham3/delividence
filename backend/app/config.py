import os

# ROLE menentukan app mana yang di-serve dari image yang sama.
# Ini yang memisahkan delividence-api dan delividence-worker di Cloud Run.
ROLE = os.environ.get("ROLE", "api").strip().lower()

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
PUBSUB_TOPIC = os.environ.get("PUBSUB_TOPIC", "delividence-runs").strip()

# 06 §2. Model terverifikasi di 10-KEPUTUSAN-DAN-VERIFIKASI.md: paket revisi
# sempat menulis gemini-3.5-flash, dikoreksi karena Google kini menyebutnya
# legacy Flash model.
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.7-flash").strip()
GOOGLE_CLOUD_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "asia-southeast2").strip()
# Wajib TRUE: mencegah ADK diam-diam fallback ke Gemini Developer API/API key
# (02 §2, "Google technology mapping").
GOOGLE_GENAI_USE_VERTEXAI = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "TRUE").strip()

# Tanpa GOOGLE_CLOUD_PROJECT, jalan dalam mode lokal: antrean lewat HTTP langsung
# ke worker, state ke file JSON. Bentuk envelope dan semantik klaim job dibuat
# identik dengan produksi supaya yang diuji lokal adalah jalur yang sama.
LOCAL = not PROJECT_ID

WORKER_URL = os.environ.get("WORKER_URL", "http://127.0.0.1:8081").rstrip("/")
LOCAL_DATA_DIR = os.environ.get(
    "LOCAL_DATA_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".localdata"),
)

# Origin frontend yang boleh memanggil API. Dipisah koma di env.
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if o.strip()
]

MAX_BRIEF_CHARS = 20_000
SUPPORTED_OUTPUT_LANGUAGES = ("en", "id")
