# Devpost submission copy

**Category:** The Collaborative Partner  
**Hosted project:** https://delividence.vercel.app  
**Repository:** https://github.com/irham3/delividence  
**Architecture diagram:** `docs/architecture-diagram.svg`  
**Local demo video artifact:** `video/real-app-video/renders/real-app-video_2026-08-31_17-45-21.mp4`  
**Public video URL:** add the YouTube/Vimeo URL after upload.

## Inspiration

Freelance projects often drift because a vague brief becomes an untracked assumption. New requests overwrite the original agreement, and delivery evidence becomes disconnected from what the client actually approved. Delividence turns that friction into a clear, shared decision trail.

## What it does

Delividence is a two-party AI scope and acceptance protocol for freelancers and clients. It extracts a source-linked project ledger from a typed brief, creates a no-account client confirmation flow, freezes a versioned baseline only after client confirmation, and classifies later requests against that baseline with a citation. Delivery evidence is attached to exact acceptance criteria, then the client can accept or request changes per criterion in a single review.

The owner workspace includes Workspace, Records, Sources, Review, Activity, and Policies. The demo walks through each: create and extract a record, inspect provenance, confirm a baseline, classify a scope change, attach evidence, submit client review, inspect the audit trail, and show the configurable policy surface.

## How we built it

- **Next.js** frontend, deployed on Vercel; Firebase Authentication protects owner routes and scoped opaque links provide no-account client access.
- **FastAPI** API and a private **Google Cloud Run** worker.
- **Cloud Firestore** for runs, versioned baselines, preferences, evidence, review sessions, and append-only audit events.
- **Cloud Pub/Sub** to hand off long-running and resumed work to the worker, with authenticated push and a dead-letter path.
- **Google ADK** to structure the agent workflow and narrow its available tools.
- **Gemini Developer API** using `gemini-3.5-flash` with `gemini-3.6-flash` fallback for structured extraction and Guardrail proposals.

The only user data sources are typed project material, client-entered clarification responses, and text/URL evidence supplied in the product. The current scope intentionally does not claim automatic ingestion or analysis of uploaded binary media.

## Why it is agentic

The agent acts over durable project state rather than producing a disposable chat response. It extracts facts, prioritizes unresolved work, resumes through Pub/Sub after client actions, and proposes a cited scope classification. However, it cannot approve a baseline, silently add scope, or accept delivery: those transitions are deterministic and require the appropriate human action. That separation makes the agent useful without making it the authority.

## Challenges and learnings

The central challenge was separating semantic judgment from authoritative state. Gemini is effective at interpreting a brief and comparing a request to it, but agreement, provenance, versioning, hashes, and client acceptance must remain deterministic. Restricting the ADK workflow and validating citations server-side made the flow more resilient to ambiguous input and prompt-injection-style text.

## Production readiness

The repository includes reproducible local setup, deployment scripts, an architecture diagram, an end-to-end smoke script, and automated tests. The most recent local verification passed 237 backend tests, 45 frontend unit tests, 9 Playwright browser tests, production build, and lint. The demo uses real local application and Google Cloud Console captures from the working codebase; loading intervals are compressed while preserving synchronized narration and full-frame UI visibility.

## Known boundary

Delividence is not a marketplace, payment platform, certified e-signature, or legal-service product. Its hashes and audit records improve traceability; they do not independently verify legal identity or the real-world truth of submitted evidence.
