# 11 - Testing and Release Gates

## What each layer protects

| Layer | Tool | Purpose | Required gate |
|---|---|---|---|
| Backend domain and API | pytest | Ledger provenance, baseline immutability, client tokens, evidence, guardrail, retries | `python -m pytest backend/tests -q` |
| Frontend unit | Vitest | HTTP auth headers, API errors, empty responses, client-token isolation | `pnpm test:unit` from `web/` |
| Browser E2E | Playwright | Public page, owner CTA, landing navigation, mobile menu, reduced motion | `pnpm test:e2e` from `web/` |
| Static safety | ESLint and Next build | TypeScript, route compilation, bundling | `pnpm lint && pnpm build` from `web/` |
| Hosted smoke | Manual browser plus Cloud Logging | Firebase sign-in, API identity, Pub/Sub worker, Gemini response | Run after each deployed change |

## Local setup

```powershell
cd D:\Work\00\delividence\web
pnpm install
pnpm exec playwright install chromium
pnpm lint
pnpm test:unit
pnpm test:e2e
```

`test:e2e` builds the production frontend and starts it at `http://127.0.0.1:3100`. Stop another process using port 3100 before running it.

## Release gate

Before a demo or deploy, all of these must pass:

1. `python -m pytest backend/tests -q`
2. `pnpm lint`
3. `pnpm test:unit`
4. `pnpm test:e2e`
5. `pnpm build`
6. Hosted smoke path: sign in as owner, create one record, confirm a client plan through a secure link, attach evidence, submit client acceptance, and inspect the related Cloud Run and Pub/Sub logs.

## Boundaries

Automated tests reduce regressions but cannot prove all visual quality, all Google Cloud IAM wiring, or every Gemini answer. Capture one desktop and one mobile screenshot after each major visual change, and run the hosted smoke path after changes to Firebase, Cloud Run, Pub/Sub, or Vertex/Gemini configuration.
