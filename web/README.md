# Delividence web

Next.js 16 frontend for the Delividence public story, authenticated freelancer workspace, and no-account client review flow.

## Run locally

1. Copy `.env.example` to `.env`.
2. Set `NEXT_PUBLIC_API_URL` to the API (normally `http://127.0.0.1:8080`).
3. Create a Firebase Web App and fill every `NEXT_PUBLIC_FIREBASE_*` value.
4. Enable Google sign-in in Firebase Authentication.

```powershell
pnpm install
pnpm lint
pnpm build
pnpm dev
```

## Route map

- `/` — public landing; Workflow, Review, and About are anchors, not duplicate marketing pages.
- `/workspace` — authenticated work queue and working record.
- `/records`, `/sources`, `/review`, `/activity`, `/settings/policies` — owner read models.
- `/records/new`, `/records/[runId]/[section]` — record actions and traceability views.
- `/sign-in`, `/register` — Google sign-in.
- `/client/[token]`, `/client/[token]/review`, `/client/[token]/request` — client links without Firebase login.

The app deliberately renders real state through the API; visual preview slices in `design/previews/slices/` are reference artifacts only and are never shipped as screenshots masquerading as UI.

## Design implementation

The product uses the Field Notes system: Geist for functional copy, Caveat only for small handwritten annotations, off-white paper surfaces, hairline rules, and a single amber action color. The landing uses scoped GSAP `useGSAP` + `ScrollTrigger`, progressive enhancement, and reduced-motion fallback.

See [design/README.md](design/README.md) and [design/13-BE-CLOUD-HANDOFF.md](design/13-BE-CLOUD-HANDOFF.md).
