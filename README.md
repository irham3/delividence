# Delividence

Delividence turns scattered client material into a source-linked project record a freelancer and client can return to. It is a submission for the **All Things Agentic Hackathon** in the **Collaborative Partner** category.

The product is deliberately not a marketplace or a chatbot. Gemini reads material; deterministic domain rules preserve what was agreed, route new work through a separate Guardrail path, and leave delivery acceptance with the client.

## What is implemented

- Google ADK + Gemini extraction runs asynchronously after a brief is created.
- Source-linked ledger, client clarification links, readiness checks, confirmed and versioned baselines.
- Append-only activity events, change-request classification with verbatim citations, evidence per criterion, and client delivery review.
- Firebase-authenticated freelancer workspace plus no-account client links.
- Public editorial landing page and responsive product routes for workspace, records, sources, review, activity, policies, sign-in, and registration.
- Cloud Run API + private worker, Firestore, Pub/Sub with dead-letter topic, Secret Manager-aware deployment scripts.

The detailed product contract is in [docs](docs/README.md). The visual system, previews, component decisions, and cloud handoff are in [web/design](web/design/README.md). The submission-ready diagram and Devpost copy are in [docs/ARCHITECTURE-DIAGRAM.md](docs/ARCHITECTURE-DIAGRAM.md), [docs/architecture-diagram.svg](docs/architecture-diagram.svg), and [docs/DEVPOST-SUBMISSION.md](docs/DEVPOST-SUBMISSION.md).

## Architecture

```text
Browser ── Firebase Auth ──> Cloud Run API (public)
                                  │
                         Firestore + audit/event store
                                  │
                               Pub/Sub
                                  │ OIDC push
                        Cloud Run worker (private)
                                  │
                           Google ADK + Gemini
```

Cloud Run is the required Google Cloud proof. The deployed workflow currently uses Gemini through the Gemini Developer API (`gemini-3.5-flash`, with `gemini-3.6-flash` fallback); the deploy script makes a Vertex AI switch explicit if that path is selected later.

## Local development

Backend:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
cd backend
..\.venv\Scripts\python.exe -m pytest -q
```

Frontend (copy `web/.env.example` to `web/.env` and fill the Firebase web values first):

```powershell
cd web
pnpm install
pnpm lint
pnpm build
pnpm dev
```

Running the whole thing locally needs three terminals, because the API and the
worker are the same image under two roles. Leave `GOOGLE_CLOUD_PROJECT` empty
in `backend/.env` for local mode: the queue becomes a direct HTTP call to the
worker and state goes to JSON files under `backend/.localdata/`.

```powershell
# terminal 1 - API on :8080
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8080 --env-file .env

# terminal 2 - worker on :8081 (ROLE from the environment wins over .env)
cd backend
$env:ROLE = "worker"
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8081 --env-file .env

# terminal 3 - web on :3000
cd web
pnpm dev
```

Owner sign-in verifies Firebase ID tokens through Application Default
Credentials, so run `gcloud auth application-default login` once even in local
mode. If your individual developer identity is deliberately not a Firebase Auth
administrator, set `FIREBASE_SESSION_COOKIE_SERVICE_ACCOUNT` to the deployed
API service account after it has granted you `roles/iam.serviceAccountTokenCreator`.
That lets local session-cookie creation impersonate the narrow production API
identity rather than broadening developer permissions. `GET
http://127.0.0.1:8080/runs` answering `401` without a token is the expected
healthy response. Step-by-step setup is in [docs/06-SETUP.md](docs/06-SETUP.md).

## Reproducible testing

The fastest way to verify is the live deployment — no local setup required.

1. Open [https://delividence.vercel.app](https://delividence.vercel.app).
2. Click **Create a record** or **Sign in** and authenticate with Google.
3. On the Workspace page, paste any brief into the **Create a project record** input (e.g. `"Launch one responsive landing page for Northstar Studio. Desktop and mobile. Hero video, three sections, contact form."`).
4. Wait ~10 seconds. The extraction agent runs asynchronously; refresh or watch the work queue status change from `processing` to `done`.
5. Open the created record. You will see the AI-extracted ledger: deliverables, acceptance criteria, in-scope items, assumptions, and unresolved questions — each linked back to the source text.
6. In the **Freelancer actions** panel, click **Create clarification link** and open the generated URL in an incognito window to see the no-account client portal. Confirm the plan to freeze baseline v1.
7. Back in the owner view, click **Create new-request link** and open it. Submit a request that was not in the original brief (e.g. `"Please also create three vertical TikTok visuals"`). The Guardrail agent classifies it against the accepted baseline and cites its reasoning.
8. Attach evidence to a criterion (text or URL), then click **Create delivery review link** and open it to see the client acceptance view with per-criterion status.

To run the backend test suite locally:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest -q
```

## Production handoff

The only manual setup is intentionally documented, not hidden:

1. Activate Cloud Billing and create a budget alert.
2. Enable Firebase Authentication with Google provider and create a Firebase Web App.
3. Add the web app’s `NEXT_PUBLIC_FIREBASE_*` values and production API URL to the frontend host.
4. Run `deploy/01-setup-gcp.ps1` once.
5. Create the Gemini Secret Manager secret if using the Developer API, then run `deploy/02-deploy.ps1` with the frontend origin and Firebase project ID.
6. Add the hosted frontend origin to Firebase authorized domains and deploy the Next.js web app.

Exact commands and the demo proof checklist are in [web/design/13-BE-CLOUD-HANDOFF.md](web/design/13-BE-CLOUD-HANDOFF.md).

## Hackathon disclosure

Built during the submission period. Standard frameworks, libraries, and AI-assisted development tools are used. The project makes no legal-contract, e-signature, marketplace, payment, or automatic-acceptance claim.

## Deliberate submission boundary

The demo-critical text workflow is complete. Direct binary upload/transcription for audio, image, and video is documented as a post-core multimodal stretch; the current UI accepts pasted text and referenced media URLs, and evidence accepts text or URL artifacts. It must not be presented as automatic video/audio analysis until a Cloud Storage adapter and multimodal ingestion worker are added.
