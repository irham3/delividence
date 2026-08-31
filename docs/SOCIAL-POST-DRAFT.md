# Social Post Draft

## LinkedIn / X

I built Delividence for the All Things Agentic Hackathon.

Delividence turns a vague freelance brief into a shared, versioned project record:

- Gemini extracts structured scope from the brief.
- The client confirms the baseline through a no-account portal.
- New requests are checked against the accepted baseline with citations.
- Delivery evidence maps back to exact acceptance criteria.
- The backend runs on Google Cloud Run with Pub/Sub, Firestore, Firebase Auth, Google ADK, and Gemini.

The design principle: the model proposes, but deterministic services and human confirmation control the decisions that matter.

#AllThingsAgenticHackathon

## Short Version

Delividence is my #AllThingsAgenticHackathon project: an agentic freelance scope workflow where Gemini extracts the brief, Cloud Run/Firestore/Pub/Sub maintain durable state, and humans confirm every baseline and change request.
