# Design System — Field Notes

## Visual premise

Delividence is a working record. The UI should feel considered, legible, and durable: a good project file, not a chat interface or a fintech dashboard.

## Tokens

```css
:root {
  --canvas: #F4F1EA;
  --surface: #FCFBF8;
  --ink: #20211F;
  --muted: #6C6B66;
  --rule: #D9D4CA;
  --saffron: #B98015;
  --saffron-soft: #F3E7CA;
  --accepted: #52755B;
  --conflict: #A64A3B;
  --font-ui: Geist, Inter, ui-sans-serif, system-ui, sans-serif;
  --font-meta: "Geist Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  --ease-out: cubic-bezier(.2, 0, 0, 1);
  --t-quick: 140ms;
  --t-standard: 260ms;
  --t-slow: 640ms;
  --radius-sm: 4px;
  --radius-md: 8px;
  --shadow-paper: 0 1px 2px rgba(32,33,31,.05), 0 8px 22px rgba(32,33,31,.055);
}
```

Use saffron for a current step, an index, one primary action, or a route line. It never decorates an entire section. Green means only accepted/completed. Red means only a conflict or explicit risk. Do not introduce a brand blue, purple, gradient, or neon variant.

## Type and spacing

One neutral sans family carries all display and body text. Metadata alone uses mono and must mean something: a source ID, timestamp, event sequence, checksum, or version.

| Token | Desktop | Mobile | Use |
| --- | --- | --- | --- |
| Display | 80–100px | 48–56px | Landing hero only |
| H1 | 56–72px | 38–44px | Route title / major story beat |
| H2 | 36–48px | 28–34px | Section title |
| Body | 16–18px | 16px | Explanatory copy |
| Metadata | 11px | 11px | Provenance |
| Major section gap | 144–192px | 72–96px | Between landing scenes |

The landing has a `max-width: 1200px`, plus a full-bleed canvas. Interior product surfaces use 24px padding desktop / 16px mobile. A dashboard grid may be dense inside one surface; the surrounding page should remain calm.

## Component recipes

| Component | Rules |
| --- | --- |
| Primary button | Saffron fill, ink text, 44–48px height, radius 4px, no gradient. |
| Secondary button | Transparent with 1px rule or ink outline. |
| Paper surface | `--surface`, thin rule, `--shadow-paper`; no thick card chrome. |
| Source chip | Metadata only, source icon + ID + time. Not a colorful tag. |
| Status | Text first, color second; include icon and readable label. |
| Data table | Real `<table>`, `<th scope>`, deliberate density; never used for page layout. |
| Sidebar | Stable 224px desktop; selected route uses subtle saffron tint + left rule. |
| Empty state | Explain what is absent, why it matters, and one next action. |

## Anti-slop guardrail

Reject: gradient mesh, aurora, “AI” sparkle icons, animated counters, fake company logos, fake revenue stats, rainbow status palettes, oversized rounded dashboard shells, generic bento feature grids, or a chat box as the product’s main visual.

