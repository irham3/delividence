# Backend and Cloud Handoff

This file lists the integration work that must be completed outside the web UI. The web implementation should stay honest: it can show the workflow, but the demo must also prove the cloud services are actually running.

## Required hackathon proof

- Gemini 3.5 or newer is called through Vertex AI or the approved Gemini API path.
- Google ADK owns the agent workflow for extraction, clarification, resume, guardrail classification, and proof review.
- At least one Google Cloud service runs in production. For the planned demo, use Cloud Run plus Firestore. Pub/Sub is recommended for async worker proof.

## Backend endpoints the web expects

- `POST /runs`
- `GET /runs/:runId`
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

## Environment variables

- `NEXT_PUBLIC_API_URL`: public API base URL used by the web app.
- `GOOGLE_CLOUD_PROJECT`: project ID for backend runtime.
- `GOOGLE_CLOUD_LOCATION`: Vertex AI location.
- `GOOGLE_GENAI_USE_VERTEXAI=true` if using Vertex AI.
- Firebase client config values for the web app.
- Service account permissions for Vertex AI, Firestore, Pub/Sub, and Cloud Storage if used.

## Demo video checklist

- Show a hosted web URL.
- Show Google sign-in for the freelancer.
- Create a record from messy brief material.
- Show Gemini extraction with source-linked output.
- Send client link and approve baseline without client login.
- Submit a new request and show it does not mutate the baseline.
- Attach evidence and submit client proof review.
- Open Cloud Run logs or Google Cloud console briefly to prove the backend is running on Google Cloud.

## Do not claim

- Do not call the output a legal contract.
- Do not claim e-signature compliance.
- Do not say the AI verifies acceptance. It assists review; the client accepts or requests changes.
- Do not introduce marketplace, payment, escrow, or freelancer discovery features before the demo-critical workflow is complete.
