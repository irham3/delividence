import os

# ROLE menentukan app mana yang di-serve dari image yang sama.
# Ini yang memisahkan dealready-api dan dealready-worker di Cloud Run.
ROLE = os.environ.get("ROLE", "api").strip().lower()

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
PUBSUB_TOPIC = os.environ.get("PUBSUB_TOPIC", "dealready-runs").strip()

# Tanpa GOOGLE_CLOUD_PROJECT, jalan dalam mode lokal: antrean lewat HTTP langsung
# ke worker, state ke file JSON. Bentuk envelope dan semantik klaim job dibuat
# identik dengan produksi supaya yang diuji lokal adalah jalur yang sama.
LOCAL = not PROJECT_ID

WORKER_URL = os.environ.get("WORKER_URL", "http://127.0.0.1:8081").rstrip("/")
LOCAL_DATA_DIR = os.environ.get(
    "LOCAL_DATA_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".localdata"),
)

MAX_BRIEF_CHARS = 20_000
SUPPORTED_OUTPUT_LANGUAGES = ("en", "id")
