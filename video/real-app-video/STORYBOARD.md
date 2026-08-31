---
format: 1920x1080
duration: 3m 25s maximum
message: "Delividence turns a vague client brief into a source-linked, human-approved scope record that can handle change and delivery review without losing the original agreement."
arc: Problem → Live workflow → Human control → Delivery proof → Google Cloud proof
audience: hackathon judges and freelance-product evaluators
mode: autonomous
---

## Frame 1 — The brief becomes usable

- status: outline
- duration: 14s
- transition_in: cut
- scene: Live Delividence landing page, then a short authenticated workspace reveal.
- voiceover: "A brief should not disappear into a chat. Delividence turns it into a shared project record that both sides can come back to."
- blueprint: zoom-out-workspace-reveal

The viewer sees the actual public product surface first, then the real authenticated workspace. The value arrives before implementation detail.

## Frame 2 — Gemini extracts a source-linked record

- status: outline
- duration: 31s
- transition_in: cut
- scene: Actual workspace shows a completed Gemini extraction receipt, current run, criteria, and the Sources and Records views.
- voiceover: "The freelancer pastes a client brief. Gemini extracts the working ledger, while the app preserves the source material, the criteria, and the run activity. The result is not a chat answer; it is durable project state with provenance."
- blueprint: prompt-type-submit-generate

The loading period is compressed; only the visible completion receipt is held long enough to read.

## Frame 3 — The client confirms the baseline

- status: outline
- duration: 26s
- transition_in: cut
- scene: Actual no-account client portal confirms baseline version one; owner controls and source record follow.
- voiceover: "The client receives a secure, no-account link to review the plan. A baseline becomes active only after that client confirmation. The freelancer can create and revoke scoped links, but cannot silently turn an AI draft into an agreement."
- blueprint: cursor-ui-demo

The real client-confirmed view is used; no personal account or client-link token is exposed.

## Frame 4 — Guardrail handles scope change

- status: outline
- duration: 34s
- transition_in: cut
- scene: Actual owner workspace shows the request for TikTok visuals, its citation, and the human-confirmed CHANGE_REQUEST decision.
- voiceover: "When the client asks for three vertical TikTok visuals, Guardrail compares that request with the approved baseline. Gemini can propose a cited classification, but the freelancer makes the final decision. Here it is a change request because the original deliverable was one responsive landing page."
- blueprint: panel-edit-live-sync

This is the core autonomy boundary: semantic proposal from Gemini, authoritative state transition from the human-controlled deterministic service.

## Frame 5 — Evidence and granular client review

- status: outline
- duration: 31s
- transition_in: cut
- scene: Actual evidence attachment controls, Proof JSON/Markdown export, and client delivery review with accepted and changes-requested criteria.
- voiceover: "Delivery evidence is attached to the exact criterion it supports. The client can accept one item and request changes on another in the same review, while the Proof Manifest remains exportable as JSON or Markdown."
- blueprint: cursor-ui-demo

The review is the real completed portal state, including the requested change reason.

## Frame 6 — Every product surface remains connected

- status: outline
- duration: 24s
- transition_in: cut
- scene: Fast, readable sequence of the live Sources, Review, Activity, Records, and Policies menu pages.
- voiceover: "The owner workspace stays deliberately small: Workspace for the next decision, Records for the index, Sources for provenance, Review for acceptance, Activity for the audit trail, and Policies for confirmed freelancer defaults. Every view points back to the same versioned record."
- blueprint: grid-card-assemble

This meets the menu-coverage requirement without turning the demo into a feature list.

## Frame 7 — It is running on Google Cloud

- status: outline
- duration: 27s
- transition_in: cut
- scene: Actual signed-in Google Cloud Console shows Delividence API and worker in Cloud Run, then the API detail/metrics page.
- voiceover: "Behind the live workflow, Cloud Run hosts a public FastAPI service and a private worker. Firestore stores the state and audit trail; Pub/Sub hands jobs to the worker; Google ADK calls Gemini. The service screen and live request metrics here are from the deployed Google Cloud project."
- blueprint: agent-progress-theater

The top billing/profile banner is masked. The Console capture remains visibly genuine.

## Frame 8 — Close

- status: outline
- duration: 12s
- transition_in: cut
- scene: Return to the real landing page and records index with a minimal end caption.
- voiceover: "Delividence keeps scope clear, change controlled, and accepted work provable."
- blueprint: titlecard-reveal

No invented claims, external logos, or unverified results appear in the closing.
