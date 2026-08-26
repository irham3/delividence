# Responsive, Accessibility & Performance

## Responsive decisions

| Range | Landing | Product |
| --- | --- | --- |
| ≥ 1280px | 12-column editorial composition; pinned scenes enabled. | 224px sidebar; right rail available. |
| 768–1279px | 8-column; source rail becomes a 3+2 staggered cluster; no fake horizontal scroll if it clips. | Collapsible sidebar; right rail moves below queue. |
| < 768px | Single column; scene narrative becomes vertical; no pinned long scroll. | Bottom/slide-over navigation; tables become labeled row cards. |

Never hide a source, decision, criterion, or client action merely to fit a smaller screen. Reflow it.

## Accessibility requirements

- Use landmarks: `header`, `nav`, `main`, `section`, `footer`; skip link targets main content.
- Every action has a visible label. Icons are supplementary; decorative SVGs use `aria-hidden="true"`.
- Source IDs link to source detail with meaningful labels, for example `Open source S-02: call transcript from Apr 29`.
- Inputs have labels; required/invalid/error semantics use `required`, `aria-invalid`, and `aria-describedby`.
- Tables have real `<th scope="col">`, appropriate row labels, and responsive alternatives—not divs pretending to be tables.
- Dialogs trap focus, restore focus on close, and expose a clear accessible name.
- Focus is visible: 2px ink/saffron ring, 2px offset, never removed without replacement.
- Body text meets WCAG AA 4.5:1. Saffron is never the only way to convey current, warning, or selected state.
- Review decisions announce success/error in a polite live region and preserve the user’s selected context.
- Motion respects system reduced-motion preference; no non-essential flash more than three times per second.

## Performance budget

| Area | Budget / choice |
| --- | --- |
| Landing LCP | Hero is DOM/CSS, not an autoplay video. Do not lazy-load hero content. |
| Preview/media | Explicit `width`/`height` and `aspect-ratio`; lazy-load below fold. |
| Motion | GSAP only on four landing scenes; transform/opacity only; no per-frame React state. |
| Images | Use AVIF/WebP derivatives for screenshots; source originals stay in Cloud Storage, not shipped as page assets. |
| Fonts | One variable sans and optional mono subset; `font-display: swap`; preload only used weights. |
| JS | Defer GSAP scene modules until their section approaches the viewport. |
| Dashboard | Virtualize long activity/evidence lists; do not animate every queue row on initial load. |

## Validation checklist

- Keyboard walkthrough: nav → upload → question → client review → change → proof decision.
- Test 320px, 375px, 768px, 1024px, 1440px.
- Test reduced motion, 200% zoom, high contrast, screen reader labels, expired review link, error state, and empty queue.
- Audit with Lighthouse after real images/fonts are present; check CLS from every preview image.

