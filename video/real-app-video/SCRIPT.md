# Narration script

## 00:00–00:14

A brief should not disappear into a chat. Delividence turns it into a shared project record that both sides can come back to.

## 00:14–00:45

The freelancer pastes a client brief. Gemini extracts the working ledger, while the app preserves the source material, the criteria, and the run activity. The result is not a chat answer; it is durable project state with provenance.

## 00:45–01:11

The client receives a secure, no-account link to review the plan. A baseline becomes active only after that client confirmation. The freelancer can create and revoke scoped links, but cannot silently turn an AI draft into an agreement.

## 01:11–01:45

When the client asks for three vertical TikTok visuals, Guardrail compares that request with the approved baseline. Gemini can propose a cited classification, but the freelancer makes the final decision. Here it is a change request because the original deliverable was one responsive landing page.

## 01:45–02:16

Delivery evidence is attached to the exact criterion it supports. The client can accept one item and request changes on another in the same review, while the Proof Manifest remains exportable as JSON or Markdown.

## 02:16–02:40

The owner workspace stays deliberately small: Workspace for the next decision, Records for the index, Sources for provenance, Review for acceptance, Activity for the audit trail, and Policies for confirmed freelancer defaults. Every view points back to the same versioned record.

## 02:40–03:07

Behind the live workflow, Cloud Run hosts a public FastAPI service and a private worker. Firestore stores the state and audit trail; Pub/Sub hands jobs to the worker; Google ADK calls Gemini. The service screen and live request metrics here are from the deployed Google Cloud project.

## 03:07–03:19

Delividence keeps scope clear, change controlled, and accepted work provable.
