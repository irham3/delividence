# Delividence backend

FastAPI API plus a private async worker for the Delividence deal-record domain.

## What it owns

- Firebase ID-token verification and owner isolation.
- Async run creation, extraction, retry, and append-only audit events.
- Source-linked ledger, readiness, immutable baseline versions, client links, evidence, proof, and Guardrail classification.
- Local JSON mode for tests/development; Firestore and Pub/Sub in Cloud Run.

## Local verification

```powershell
python -m venv ..\.venv
..\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
..\.venv\Scripts\python.exe -m pytest -q
```

For two-process manual verification:

```powershell
# terminal 1
$env:ROLE = "worker"
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8081

# terminal 2
$env:ROLE = "api"
$env:WORKER_URL = "http://127.0.0.1:8081"
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8080
```

Copy `.env.example` into `.env` to select model runtime and Firebase project. In local mode, do not set `GOOGLE_CLOUD_PROJECT`; state is kept under `.localdata/` and messages go directly to the local worker.

## Production

Use the scripts in `../deploy`. API and worker receive distinct Cloud Run service accounts. Developer API keys are injected from Secret Manager; Vertex mode uses Cloud Run ADC and `roles/aiplatform.user`.

The complete hosted deployment contract is [web/design/13-BE-CLOUD-HANDOFF.md](../web/design/13-BE-CLOUD-HANDOFF.md).
