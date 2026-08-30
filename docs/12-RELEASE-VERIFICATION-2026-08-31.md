# Release verification - 2026-08-31

Commit verified locally: `8a4e2f0` (`Fix auth session flow and demo reliability`).

## Fixed

- Owner auth now exchanges a Firebase ID token for an HttpOnly `delividence_session` cookie through `POST /api/auth/session` -> backend `POST /auth/session`.
- Protected owner routes are guarded by `web/src/proxy.ts`; public client-token routes stay outside owner auth.
- Auth `next` destinations are allowlisted to owner routes only.
- Local auth routes on `127.0.0.1` canonicalize to `localhost` before Firebase initialization, avoiding the stuck "Checking your session..." state.
- Backend session errors are mapped to actionable messages, including the stale-backend `404 /auth/session` case.
- Logout now asks for confirmation and clears both Firebase and the route session.
- Google sign-in uses a real PNG asset at `web/public/assets/google-g.png`, not a text placeholder.
- Gemini defaults to `gemini-3.5-flash` with `gemini-3.6-flash` fallback and a 45s per-model timeout, so high-demand model retries do not hang the demo path indefinitely.

## Local gates passed

- Backend: `235 passed, 2 warnings`
- Frontend unit: `44 passed`
- Frontend lint: passed
- Frontend build: passed
- Playwright browser E2E: `9 passed`
- Live ADK/Gemini extraction smoke: passed with ledger fields `acceptance_criteria`, `deliverables`, `out_of_scope`, `revision_policy`, and `timeline`.
- Live ADK/Gemini guardrail smoke: passed with `CHANGE_REQUEST` and citation `out_of_scope[0] -> payment processing`.

## Production state observed before deploy

- `https://delividence.vercel.app/sign-in` still served the old sign-in button with text `G`.
- `https://delividence-api-3jww7h7koq-et.a.run.app/auth/session` still returned `404`.

Production is therefore not complete until Cloud Run and Vercel are redeployed and a hosted smoke is run.

## Blocking item

`gcloud auth list` returned no active account. A `gcloud auth login --brief` flow was started and is waiting for the browser OAuth callback. After login with an account that can deploy to project `gen-lang-client-0104798459`, run:

```powershell
.\deploy\02-deploy.ps1 `
  -ProjectId gen-lang-client-0104798459 `
  -Region asia-southeast2 `
  -FrontendOrigin https://delividence.vercel.app `
  -FirebaseProjectId gen-lang-client-0104798459 `
  -ModelRuntime developer `
  -GeminiModel gemini-3.5-flash
```

Then verify:

```powershell
curl.exe -s https://delividence-api-3jww7h7koq-et.a.run.app/health
curl.exe -s -o NUL -w "%{http_code}`n" -X POST https://delividence-api-3jww7h7koq-et.a.run.app/auth/session -H "Authorization: Bearer invalid"
```

Expected: health `200`, invalid session token `401` rather than `404`.

## Demo artifact

Fallback MP4 created locally:

```text
D:\Work\00\delividence\video\remotion\out\delividence-demo.mp4
```

Properties: 1920x1080, H.264 video, AAC mono audio, 119 seconds.

Refresh the Cloud proof card after production deploy so it shows the latest Cloud Run revision/log timestamp.
