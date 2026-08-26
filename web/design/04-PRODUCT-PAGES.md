# Product Pages — Screen Inventory

References: [dashboard-main.png](previews/dashboard-main.png), [intake board](previews/product-board-intake.png), [agreement board](previews/product-board-agreement.png), and [supporting board](previews/product-board-supporting.png).

## Shell

Authenticated freelancer routes use the 224px sidebar. Client review routes do not: they are self-contained, public-link experiences with a small secure-link header and clear freelancer contact. Never require a client account for the MVP review path.

## Core routes

| Route | User | Primary job | Key states |
| --- | --- | --- | --- |
| `/workspace` | Freelancer | See the next decision, not generic metrics. | Queue, empty, loading, error. |
| `/records` | Freelancer | Find a deal and its current moment. | Filtered, empty, archived. |
| `/records/new` | Freelancer | Add source material. | Drop, uploading, processing, validation error. |
| `/records/:id/sources` | Freelancer | Inspect exact source provenance. | Selected source, invalid quote, missing source. |
| `/records/:id/questions` | Freelancer | Review top unresolved questions. | Waiting on client, answer received, blocked. |
| `/records/:id/baseline` | Freelancer | Review and send baseline. | Draft, ready, sent, approved, expired. |
| `/review/:token/baseline` | Client | Resolve/approve in plain language. | Valid, expired, already decided. |
| `/records/:id/request/:requestId` | Freelancer | Compare new request to baseline. | Proposed, classified, change proposed, decided. |
| `/review/:token/proof` | Client | Accept each criterion or request changes. | Awaiting evidence, partial, complete. |
| `/records/:id/evidence` | Freelancer | Attach evidence to criteria. | Missing, attached, ready. |
| `/records/:id/activity` | Freelancer | Inspect chronological audit facts. | Full, filtered, selected event. |
| `/settings/policies` | Freelancer | Manage reusable policy and confirmed preferences. | Default, edited, preference pending confirmation. |

## Page-specific UX rules

### Workspace

The main content is a work queue. Each row shows record, state, source count, deadline, and **one** next action. Never add metric tiles such as revenue, productivity, or “AI score”. The right rail is incoming material and follow-ups.

### New record / source intake

Accept brief text, email export, chat export, meeting audio, image/screenshot, video reference, and file. Explain that the system will look for deliverables, dates, decisions, exclusions, and acceptance detail. Any upload status must be programmatic text, not color alone.

### Source review

Source list → selected source → project record is the canonical three-column relationship. A field labelled `CLIENT STATED` must have a real quote link. Invalid/unsupported text becomes proposed or missing; it must not appear as a client fact.

### Questions and baseline

Show at most three high-impact active questions. A conflict displays the competing quotes side by side. The relevant authority can choose; the freelancer cannot resolve contradictory client statements. Baseline approval remains disabled until all required conditions are met.

### Client review

Use plain language, source citations, and a fixed action bar. Show link expiration. The promise is “choices are recorded in this version,” never “legally binding” or “signed contract”.

### Change request

Show original baseline, raw new request, proposed comparison, and the freelancer’s decision control. The classifier is a recommendation. A new request never edits the active baseline in place.

### Evidence / proof review

Show four layers without collapsing them into “verified”: agreed criterion, artifact metadata/integrity, deterministic or `AI-assisted` checks, and client decision. Each criterion has `Accepted` / `Changes requested`; do not invent a percentage-acceptance workflow.

### Activity and policies

Activity is append-only, ordered by sequence, and filters by actor/type without replacing the raw facts. Working policies are explicitly freelancer-owned. Suggested preferences require confirmation and carry the note: `Policies guide your drafts. They never replace a client’s words.`

