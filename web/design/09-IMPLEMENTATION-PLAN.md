# Implementation Plan

## Phase 1 — Foundations

1. Load Geist/Inter variable font; define tokens from [02-DESIGN-SYSTEM.md](02-DESIGN-SYSTEM.md).
2. Build `AppShell`, `Sidebar`, `PaperSurface`, `SourceRef`, `Status`, `DataTable`, `DecisionBar`, and focus/error states.
3. Install only the 21st components that accelerate primitives, then restyle them to the tokens. Do not copy a catalog component’s visual identity wholesale.
4. Build source/record data adapters against the canonical schemas in the root specs.

## Phase 2 — Demo-critical flow

1. Workspace queue.
2. New record intake and source review.
3. Question priority and secure client baseline review.
4. Baseline activation and change request route.
5. Evidence attachment and criterion-level client review.
6. Activity timeline.

Build this before settings, preference suggestions, filters, or animations. It is the exact sequence judges should see.

## Phase 3 — Landing

1. Build static DOM version of every landing scene.
2. Verify responsive/keyboard/reduced-motion version.
3. Add GSAP scenes one by one, starting with source rail then change path. Never start motion before static hierarchy is good.
4. Use real product data/screens or accurate local demo state in the landing visuals.

## Phase 4 — Proof for judges

- Show Gemini 3.5 extraction with source-linked structured output.
- Show the ADK workflow asking/continuing—not a generic chat response.
- Show client response resuming cloud work and changing UI state.
- Show a new request routed to Change Request without changing the baseline.
- Show evidence + client acceptance.
- Show deployed Google Cloud proof separately in the 4-minute video, repository, and architecture diagram.

## Non-goals

Do not add marketplace, payments, invoicing, e-signature claims, percentage acceptance, auto-resolved client conflict, or a generic in-app chat assistant. They weaken the story and violate the domain scope.

