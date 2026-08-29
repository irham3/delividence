# Backend and Cloud Handoff

This file lists the integration work that must be completed outside the web UI. The web implementation should stay honest: it can show the workflow, but the demo must also prove the cloud services are actually running.

## Required hackathon proof

- Gemini 3.5 or newer is called through Vertex AI or the approved Gemini API path.
- Google ADK owns the agent workflow for extraction, clarification, resume, guardrail classification, and proof review.
- At least one Google Cloud service runs in production. For the planned demo, use Cloud Run plus Firestore. Pub/Sub is recommended for async worker proof.

## Backend endpoints the web expects

- `POST /runs`
- `GET /runs`
- `GET /preferences`
- `POST /preferences`
- `GET /runs/:runId`
- `GET /runs/:runId/activity`
- `GET /runs/:runId/baseline`
- `POST /runs/:runId/retry-extraction`
- `POST /runs/:runId/client-links`
- `POST /runs/:runId/client-links/:token/revoke`
- `POST /runs/:runId/evidence`
- `GET /runs/:runId/proof?format=json`
- `GET /runs/:runId/proof?format=md`
- `POST /runs/:runId/change-proposal`
- `GET /runs/:runId/requests`
- `POST /runs/:runId/requests`
- `GET /runs/:runId/citable-refs`
- `POST /runs/:runId/requests/:requestId/classify`
- `GET /client/:token`
- `POST /client/:token/answers`
- `POST /client/:token/confirm`
- `GET /client/:token/review`
- `POST /client/:token/review`
- `GET /client/:token/new-request`
- `POST /client/:token/new-request`

## Google Cloud setup

- Cloud Run service for the API.
- Cloud Run worker for long-running extraction and review jobs.
- Firestore for runs, ledger versions, client links, requests, evidence, and activity events.
- Pub/Sub topic for async extraction and resume events.
- Cloud Storage only if uploaded files are stored directly by the app.
- Cloud Logging with request IDs and run IDs included in structured logs.

The repository scripts provision the Cloud Run, Firestore, Pub/Sub, Artifact Registry, and service-account parts. They intentionally do not activate billing, create Firebase UI resources, or create a secret from a pasted key.

## Environment variables

- `NEXT_PUBLIC_API_URL`: public API base URL used by the web app.
- `NEXT_PUBLIC_FIREBASE_API_KEY`
- `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
- `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
- `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`
- `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`
- `NEXT_PUBLIC_FIREBASE_APP_ID`
- `GOOGLE_CLOUD_PROJECT`: project ID for backend runtime.
- `GOOGLE_CLOUD_LOCATION`: Vertex AI location.
- `GOOGLE_GENAI_USE_VERTEXAI=true` if using Vertex AI.
- Firebase client config values for the web app.
- Service account permissions for Vertex AI, Firestore, Pub/Sub, and Cloud Storage if used.

## Hosted deployment: exact operator steps

1. In Google Cloud Console, attach an active billing account to the chosen project and create a budget alert. Cloud Run/Firestore/Pub/Sub require billing even if free-tier usage is expected.
2. Install and authenticate the Google Cloud CLI:

   ```powershell
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project <PROJECT_ID>
   ```

3. Create a Firebase project or add Firebase to the same Google Cloud project. In Firebase Authentication, enable **Google** provider; then add the final web hostname under **Authorized domains**. Create a Web App and copy its six public config values into the web host environment.
4. Provision the backend foundations:

   ```powershell
   .\deploy\01-setup-gcp.ps1 -ProjectId <PROJECT_ID>
   ```

5. Pick one model path.

   - **Developer API:** create a Gemini API key in Google AI Studio, then create a Secret Manager secret without committing the key:

     ```powershell
     gcloud secrets create delividence-gemini-api-key --replication-policy=automatic
     Read-Host "Paste Gemini API key" -AsSecureString | ConvertFrom-SecureString -AsPlainText | gcloud secrets versions add delividence-gemini-api-key --data-file=-
     ```

     If the installed PowerShell does not support `ConvertFrom-SecureString -AsPlainText`, use the Google Cloud Console’s **Add secret version** field instead. Do not put the key in git or the Cloud Run environment directly.

   - **Vertex AI:** no Gemini API-key secret is required. The setup script gives both Cloud Run service accounts `roles/aiplatform.user`.

6. Deploy Cloud Run. Pass the exact production browser origin, without a trailing slash:

   ```powershell
   .\deploy\02-deploy.ps1 -ProjectId <PROJECT_ID> `
     -FrontendOrigin https://<YOUR_FRONTEND_HOST> `
     -FirebaseProjectId <PROJECT_ID> `
     -ModelRuntime developer
   ```

   For Vertex, replace the final parameter with `-ModelRuntime vertex`.
7. Deploy `web/` to the selected Next.js host. Set `NEXT_PUBLIC_API_URL` to the printed `delividence-api` URL and all six Firebase web values. Redeploy after changing `NEXT_PUBLIC_*` variables; Next.js bakes them into the browser bundle.
8. Verify `/health` is reachable publicly. Owner routes need an authenticated Firebase session, so use the deployed browser app—not an unauthenticated `curl`—to create a record. Then inspect the private worker’s Cloud Run logs for the matching run ID.

## Demo video checklist

- Show a hosted web URL.
- Show Google sign-in for the freelancer.
- Create a record from messy brief material.
- Show Gemini extraction with source-linked output.
- Send client link and approve baseline without client login.
- Submit a new request and show it does not mutate the baseline.
- Attach evidence and submit client proof review.
- Open Cloud Run logs or Google Cloud console briefly to prove the backend is running on Google Cloud.
- Show the response/status transition from queued to done (or the honest retry state if the model is temporarily unavailable).

## Do not claim

- Do not call the output a legal contract.
- Do not claim e-signature compliance.
- Do not say the AI verifies acceptance. It assists review; the client accepts or requests changes.
- Do not introduce marketplace, payment, escrow, or freelancer discovery features before the demo-critical workflow is complete.
