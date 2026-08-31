# Building Delividence for the All Things Agentic Hackathon

I created this piece of content for the purposes of entering the All Things Agentic Hackathon.

## Summary

Delividence is a two-party scope and acceptance workflow for freelance work. It turns a vague client brief into a shared, versioned project record, keeps the client involved through no-account review links, and uses Gemini to classify later requests against the accepted baseline before scope changes.

The goal is not to replace human judgment. The goal is to remove the manual chasing around brief interpretation, change requests, delivery evidence, and acceptance decisions while keeping the human in control of every approval that matters.

## The Problem

Freelance scope problems usually start quietly. A client asks for "a responsive landing page" or "something modern," the freelancer starts work, and later everyone discovers that the original request, the follow-up message, and the delivery proof all live in different places.

Chat alone is not enough here. A chatbot can summarize a brief, but it does not automatically create durable shared state, freeze an accepted baseline, resume work when the client responds, or map proof back to the exact acceptance criteria.

## What Delividence Does

Delividence starts from a typed client brief. Gemini extracts structured project state, including deliverables, acceptance criteria, out-of-scope boundaries, timeline, and revision policy. The app records the source material and the activity trail so the result is not just an answer in a chat window.

The client receives a no-account portal to review and confirm the baseline. Once the plan is confirmed, the accepted baseline becomes the reference point for later work.

When a new request arrives, Delividence runs a guardrail step. Gemini compares the request against the accepted baseline and proposes a classification such as `CHANGE_REQUEST`, with citations. The model proposes; the human confirms.

For delivery, evidence is mapped to the exact criterion it supports. The client can accept one item and request changes on another, so review becomes specific instead of emotional.

## Architecture

The shipped demo uses:

- Next.js for the web UI.
- Firebase Auth for owner sign-in.
- FastAPI on Cloud Run for the API.
- A private Cloud Run worker for background workflow execution.
- Pub/Sub for asynchronous resume after client events.
- Firestore for durable run, baseline, evidence, and audit state.
- Google ADK for workflow orchestration.
- Gemini Developer API with `gemini-3.5-flash` and a `gemini-3.6-flash` fallback for structured extraction and scope classification.

The current submission accepts typed brief material and text/URL evidence. Direct binary upload and automatic image/audio/video analysis are intentionally treated as future work, not as a shipped claim.

## Why It Is Agentic

Delividence does not simply answer a user prompt. It maintains state across the owner, client, model, and worker. It makes progress after external events, prioritizes clarification, classifies new scope requests against the accepted baseline, and creates durable records that survive beyond one chat session.

The architectural discipline is that Gemini handles semantic interpretation, while deterministic services keep authority over approval, versioning, readiness, idempotency, and hashes. The model has no capability to approve a baseline, spend revision rounds, change ownership, or silently mutate accepted scope.

## What I Learned

The hard part was not calling Gemini. The hard part was deciding where the model should stop.

For this type of product, trust comes from separating semantic help from authoritative state. Gemini can identify likely meaning and propose a classification, but the system still needs deterministic gates, explicit human confirmation, and a durable audit trail.

That separation made the demo stronger: the agent removes operational friction, but it does not pretend to be a lawyer, a marketplace, or a final dispute judge.

## Demo Notes

The final demo video is under four minutes and shows the real application flow: landing page, Google sign-in route, owner workspace, Gemini extraction, client baseline confirmation, guardrail classification, delivery review, all main sidebar menus, and Google Cloud Run proof.

The backend proof is shown from Google Cloud Console: Cloud Run services for the public API and private worker, plus the API service detail page with live metrics.
