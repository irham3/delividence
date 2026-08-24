# DealReady

**An asynchronous collaborative agent that turns a messy client brief into an
evidence-backed scope a freelancer can safely quote.**

Submission for the **All Things Agentic Hackathon: Ready, Set, Agent!**
(Google × Devpost) — category **The Collaborative Partner**.

> **Status: work in progress.** This README describes what exists today, not what
> is planned. Anything not listed under "What works today" is not built yet.
> Planning documents live in [`docs/`](docs/).

---

## The problem

A freelancer gets a brief over WhatsApp: *"Can you edit some videos for our IG?
A few clips, deadline next week, budget 2 million."* They quote a price. Only
later does anyone discover how many revision rounds are included, who signs off,
what "a few clips" means, and what happens when the client adds one more. The
project expands; the fee does not.

The freelancer knows which questions to ask. The friction is asking them well,
at the right moment, without sounding difficult — and keeping track of what was
actually agreed across a scattered conversation.

## The principle

**The AI extracts and orchestrates. Deterministic code decides.**

Language models are good at reading a messy conversation and pulling out what
was said. They are not a good place to put the rules that determine whether a
deal is safe to quote. So extraction is probabilistic and every quotation it
produces is verified against the source text in code; readiness is computed by
plain Python rules that never call a model.

## What works today

A thin async vertical slice — the plumbing, deliberately built before any
product logic, so that the risky part fails early instead of on the last day.

- `POST /runs` accepts a brief, persists it, publishes a job, and returns `202`
  immediately.
- A separate worker service consumes the job and processes it **outside the
  request**, writing progress into an audit trail.
- Duplicate deliveries are processed exactly once.

Verified locally: 10 tests pass, and two real services running side by side move
a run from `queued` to `done` with no second request.

**Not built yet:** the extraction agent, the deterministic rule set, the scope
ledger, the frontend, and deployment to Google Cloud.

## Architecture

One container image; the `ROLE` environment variable selects which application
it serves. This is what lets the API and the worker deploy from a single source
without both booting the same app.

```
client ──▶ dealready-api (Cloud Run, public)
               │  writes run
               ▼
           Firestore ◀────────────┐
               ▲                  │ writes result + audit trail
               │ publishes job    │
               ▼                  │
           Pub/Sub ──push OIDC──▶ dealready-worker (Cloud Run, private)
               │                          │
               └──▶ dead-letter topic     └──▶ Vertex AI (Gemini)
```

Design decisions already enforced in code:

| Decision | Why |
|---|---|
| Idempotency is a create-only job document keyed `{run_id}:{round}` | Pub/Sub is at-least-once, so duplicate delivery is certain. An `idempotency_key` field enforces nothing. The key includes the round so a later client reply is not suppressed as a duplicate |
| Permanently malformed messages are acknowledged, not retried forever | Retries are for transient failure; that is what the retry policy and dead-letter topic are for |
| `output_language` defaults to `en` | The application must support English; Indonesian is an additional option, not the only mode |
| The audit trail records decisions and tool results, never raw prompts | It exists to make the agent's behaviour inspectable, not to leak its internals |

## Running it

Local development needs no Google Cloud account — see
[`backend/README.md`](backend/README.md). Without `GOOGLE_CLOUD_PROJECT` the
backend queues over HTTP and stores state as JSON, using an envelope shaped
exactly like a Pub/Sub push so the handler under test is the handler that ships.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
cd backend
..\.venv\Scripts\python.exe -m pytest -q
```

Google Cloud setup and deployment are scripted:

```powershell
.\deploy\01-setup-gcp.ps1 -ProjectId <PROJECT_ID>
.\deploy\02-deploy.ps1    -ProjectId <PROJECT_ID>
```

## Stack

| Layer | Choice |
|---|---|
| Model | `gemini-3.7-flash` (current stable Flash; the rules require Gemini 3.5 or newer) |
| Agent framework | Google ADK |
| Infrastructure | Cloud Run, Pub/Sub, Firestore, Artifact Registry, Cloud Build |

## Disclosure of pre-existing work

The hackathon rules require disclosure of any pre-existing *code or work*
incorporated into a project, so this is stated explicitly rather than left to
inference.

This project was written from scratch, starting 24 August 2026, inside the
submission period; the commit history is the record. The **concept** was
informed by the author's earlier exploration of the same problem domain in a
separate project entered in a different contest. **No code, assets, prompts, or
implementation from that project are reused here**, and nothing in this
repository is derived from it.

Standard frameworks, libraries, and AI coding assistants were used, as the rules
permit.

## Licence

Not yet chosen.
