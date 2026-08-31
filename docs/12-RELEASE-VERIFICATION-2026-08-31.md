# Release verification - 2026-08-31

Commits verified locally and pushed:

- `e35df4a` (`Finalize auth flow and hackathon demo assets`)
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
- Local Firebase session-cookie creation now impersonates the narrow Cloud Run API service account when `FIREBASE_SESSION_COOKIE_SERVICE_ACCOUNT` is configured. This fixes the previously misleading secure-session failure without giving every developer Firebase Auth administration rights.
- Client-plan confirmation is disabled while the preceding save request is still in flight, preventing a stale page reload from racing a successful confirmation.

## Local gates passed

- Backend: `237 passed, 2 warnings`
- Frontend unit: `45 passed`
- Frontend lint: passed
- Frontend build: passed
- Playwright browser E2E: `9 passed`
- Live browser login: Google sign-in redirected to the authenticated local workspace and the owner session bridge returned `200` after ADC was refreshed for `gen-lang-client-0104798459`.
- Live ADK/Gemini extraction smoke: passed with ledger fields `acceptance_criteria`, `deliverables`, `out_of_scope`, `revision_policy`, and `timeline`.
- Live ADK/Gemini guardrail smoke: passed with `CHANGE_REQUEST` and citation `out_of_scope[0] -> payment processing`.

## Production verification after Cloud Run deploy

- Cloud Run project: `gen-lang-client-0104798459`
- Region: `asia-southeast2`
- API revision: `delividence-api-00005-vpb`, serving 100% traffic.
- Worker revision: `delividence-worker-00005-6qg`, serving 100% traffic.
- API health: `GET /health` returns `{"status":"ok","role":"api","local":false}`.
- Session bridge: `POST /auth/session` with an invalid Firebase token returns `401` (`Invalid or expired ID token`), not the stale `404`.
- Frontend session route: `POST https://delividence.vercel.app/api/auth/session` with an invalid token returns the user-safe JSON error `Google could not verify this sign-in. Choose your account again to continue.`
- Frontend logout route: `DELETE https://delividence.vercel.app/api/auth/session` returns `204`.
- CORS preflight from `https://delividence.vercel.app` to `POST /runs` returns `200` with `access-control-allow-origin: https://delividence.vercel.app`.
- Worker privacy: unauthenticated `GET /health` on `delividence-worker` returns `403`, as expected for the private worker.
- Pub/Sub push subscription `delividence-runs-push` is `ACTIVE`, points to `/pubsub/push`, uses OIDC service account `delividence-pubsub@gen-lang-client-0104798459.iam.gserviceaccount.com`, has 60s ack deadline, retry policy, and DLQ.
- Frontend production routing: protected `/records/run-123?tab=evidence` redirects to `/sign-in?next=%2Frecords%2Frun-123%3Ftab%3Devidence`; public `/client/not-a-real-token` is not redirected to owner sign-in.
- Frontend production Google button: one `google-g` image asset is rendered and the old text placeholder `>G<` is absent.
- Full production E2E smoke after the `00005` Cloud Run deploy:
  `PASS production_e2e run_id=553f4280c77b42db81b61bb0a06d66be uid=prod-smoke-owner-1788174226`.
  - Firebase custom-token exchange succeeded.
  - Vercel `/api/auth/session` created the HttpOnly `delividence_session` cookie.
  - Owner API created a run.
  - Pub/Sub pushed to the private worker and Gemini extraction completed.
  - Public client clarification link rendered and confirmed baseline v1.
  - Guardrail proposed `CHANGE_REQUEST` with one citation.
  - Freelancer classification confirmation, change proposal, v2 client confirmation, evidence, delivery review, and proof JSON export all succeeded.
  - Temporary Firebase Auth user was deleted at the end of the smoke.

## Production fixes found during final smoke

The first custom-token smoke proved that `verify_id_token()` worked in Cloud Run (`POST /runs` returned `202`), but `create_session_cookie()` returned `401 Could not create owner session`. The API runtime service account was missing Firebase Auth session-cookie permission.

Fixed by granting:

```powershell
gcloud projects add-iam-policy-binding gen-lang-client-0104798459 `
  --member="serviceAccount:delividence-api@gen-lang-client-0104798459.iam.gserviceaccount.com" `
  --role="roles/firebaseauth.editor" `
  --condition=None
```

`deploy/01-setup-gcp.ps1` now includes the same binding so future GCP setup does not miss it.

Earlier attempts that failed safely before the final smoke:

- Exchanging the Cloud SDK OAuth token through Firebase returned `INVALID_IDP_RESPONSE` because the OAuth audience belongs to Cloud SDK, not this Firebase web app.
- Minting a Firebase custom token via IAM initially returned `403 iam.serviceAccounts.signJwt`; the user then granted `roles/iam.serviceAccountTokenCreator` on the API service account to the deploy/testing account.
- Temporary email/password Firebase sign-up returned `OPERATION_NOT_ALLOWED` because that provider is disabled.
- Manual Vercel mirror sync could not fetch `https://github.com/rifqiahmadpratama/delividence.git` from this machine (`Repository not found`). `deploy/03-sync-vercel-mirror.ps1` now fails hard on that condition instead of printing a false success.

## Demo artifact

Final Devpost demo MP4 created locally from actual local-app and Google Cloud
Console captures:

```text
D:\Work\00\delividence\video\real-app-video\renders\real-app-video_2026-08-31_17-45-21.mp4
```

Properties verified with `ffprobe`: 1920x1080, 30fps, H.264 video, AAC audio,
104.0 seconds, 40.4 MB.

This version replaces the earlier fallback videos under `video/remotion` and
`video/screen-record-demo`. The visual source is the real Delividence UI and
real Google Cloud Run Console proof, with private owner email and billing-banner
details masked before rendering. The composition preserves the full app frame
inside a 1920x1080 canvas so the left and right edges are not cropped.

Video verification gates passed:

- `npm run check` in `video/real-app-video`: lint, runtime, layout, motion, and
  contrast passed.
- Rendered file has both video and audio streams.
- Final proof contact sheet:
  `D:\Work\00\delividence\video\real-app-video\renders\final-proof-contact-sheet.jpg`.
