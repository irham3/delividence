# Delividence architecture diagram

```mermaid
flowchart TB
  owner["Freelancer owner\nFirebase Google sign-in"] -->|Firebase ID token| web["Next.js web app\nVercel / local development"]
  client["Client\nno-account scoped link"] -->|opaque, purpose-bound token| web

  subgraph gcp["Google Cloud"]
    api["Cloud Run: delividence-api\nFastAPI public API"]
    fs[("Firestore\nrun state, baselines, audit")]
    ps["Pub/Sub\njob topic + retry/DLQ"]
    worker["Cloud Run: delividence-worker\nprivate OIDC push target"]
    adk["Google ADK workflow\nconstrained tools"]
  end

  web -->|HTTPS + owner/client authorization| api
  api -->|verify ID token| firebase["Firebase Authentication"]
  api <--> fs
  api -->|publish job| ps
  ps -->|OIDC push| worker
  worker --> adk
  adk -->|structured extraction / guardrail proposal| gemini["Gemini Developer API\ngemini-3.5-flash\nwith gemini-3.6-flash fallback"]
  worker <--> fs
```

### Authority boundaries

- Gemini proposes structured ledger fields and scope classifications; deterministic domain services verify source quotes, readiness, versioning, hashes, and every final approval.
- The owner is authenticated with Firebase. Client portals use hashed, expiring, purpose-bound opaque links and do not require a client account.
- The public API publishes work; a private Cloud Run worker receives authenticated Pub/Sub delivery and writes the resulting state and audit events back to Firestore.
- The current submission workflow accepts brief text and URL/text evidence. It does **not** claim automatic binary image, audio, or video analysis.
