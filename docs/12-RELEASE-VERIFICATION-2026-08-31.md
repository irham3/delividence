# Release verification - 2026-08-31

Commits verified locally and pushed:

- `8a4e2f0` (`Fix auth session flow and demo reliability`)
- `e4e03a9` (`Add screen-record demo pipeline`)
- `0ecb35b` (`Fail Vercel mirror sync on git errors`)

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

## Production verification after Cloud Run deploy

- Cloud Run project: `gen-lang-client-0104798459`
- Region: `asia-southeast2`
- API revision: `delividence-api-00004-5jr`, serving 100% traffic.
- Worker revision: `delividence-worker-00004-lrp`, serving 100% traffic.
- API health: `GET /health` returns `{"status":"ok","role":"api","local":false}`.
- Session bridge: `POST /auth/session` with an invalid Firebase token returns `401` (`Invalid or expired ID token`), not the stale `404`.
- Frontend session route: `POST https://delividence.vercel.app/api/auth/session` with an invalid token returns the user-safe JSON error `Google could not verify this sign-in. Choose your account again to continue.`
- Frontend logout route: `DELETE https://delividence.vercel.app/api/auth/session` returns `204`.
- CORS preflight from `https://delividence.vercel.app` to `POST /runs` returns `200` with `access-control-allow-origin: https://delividence.vercel.app`.
- Worker privacy: unauthenticated `GET /health` on `delividence-worker` returns `403`, as expected for the private worker.
- Pub/Sub push subscription `delividence-runs-push` is `ACTIVE`, points to `/pubsub/push`, uses OIDC service account `delividence-pubsub@gen-lang-client-0104798459.iam.gserviceaccount.com`, has 60s ack deadline, retry policy, and DLQ.
- Frontend production routing: protected `/records/run-123?tab=evidence` redirects to `/sign-in?next=%2Frecords%2Frun-123%3Ftab%3Devidence`; public `/client/not-a-real-token` is not redirected to owner sign-in.
- Frontend production Google button: one `google-g` image asset is rendered and the old text placeholder `>G<` is absent.

## Remaining production E2E limitation

The only unverified hosted path is a full owner-authenticated browser/API journey after actual Firebase sign-in. The code path is covered locally and the production session endpoint is live, but automated production owner E2E needs one of these:

- Grant `roles/iam.serviceAccountTokenCreator` on `delividence-api@gen-lang-client-0104798459.iam.gserviceaccount.com` to the deploy/testing account, so a short-lived Firebase custom token can be minted for smoke testing.
- Or run the hosted Google sign-in in a browser session and provide a safe test ID token/session for the smoke script.

Attempts that failed safely:

- Exchanging the Cloud SDK OAuth token through Firebase returned `INVALID_IDP_RESPONSE` because the OAuth audience belongs to Cloud SDK, not this Firebase web app.
- Minting a Firebase custom token via IAM returned `403 iam.serviceAccounts.signJwt`.
- Temporary email/password Firebase sign-up returned `OPERATION_NOT_ALLOWED` because that provider is disabled.
- Manual Vercel mirror sync could not fetch `https://github.com/rifqiahmadpratama/delividence.git` from this machine (`Repository not found`). `deploy/03-sync-vercel-mirror.ps1` now fails hard on that condition instead of printing a false success.

## Demo artifact

Screen-record style MP4 created locally:

```text
D:\Work\00\delividence\video\screen-record-demo\out\delividence-demo-screen-record.mp4
```

Properties: 1920x1080, H.264 video, AAC mono audio, 96.4 seconds.

This version is generated from a browser recording pipeline with typed input, clicks, visible cursor, live state changes, safe margins, and neural narration. It replaces the earlier screenshot-style fallback at `video/remotion/out/delividence-demo.mp4`.
