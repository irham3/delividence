# Motion & GSAP Plan

## Motion personality

**Premium-corporate paper.** Movement is precise and calm: paper surfaces dock, source markers travel, and a request is deliberately rerouted. No bounce, neon pulse, ambient particle field, or endlessly moving background.

| Token | Value |
| --- | --- |
| Signature ease | `cubic-bezier(.2, 0, 0, 1)` / GSAP `power3.out` |
| Quick | 140ms |
| Standard | 260ms |
| Slow scene reveal | 640ms |
| Scroll scrub | `0.6–0.9` |
| Max parallax | 24px |

## Library boundary

- CSS: hover, focus, tooltip, small opacity/color changes.
- Motion/Framer Motion: app-page transitions and layout presence where no scroll link is needed.
- GSAP + ScrollTrigger: landing source rail, question scene, change route, and horizontal evidence reel only.
- Do not use a smooth-scroll library by default. Native scroll gives the most robust accessibility and mobile behaviour. Add one only after performance testing and wire it through `scrollerProxy` correctly.

## Landing choreography

| Scene | Trigger / behaviour | Animation | Fallback |
| --- | --- | --- |
| Hero | Load once | Sources enter 18px upward + opacity; index markers follow 60ms later. | Static sources. |
| Material rail | Pin, 160vh, `scrub: .7` | Five sources fan → align → dock into Project Record; path draws. | Vertical source list and record. |
| Decision | Pin, 140vh, `scrub: .7` | Quote rests; client choice rises 16px; chosen answer writes into record. | Three stacked blocks. |
| Change path | Pin, 130vh, `scrub: .65` | Request moves only 1/3 viewport, touches boundary, then follows SVG route to decision. | Static route line. |
| Proof | Pin, horizontal child tween, `scrub: .8` | Evidence reel travels; criterion rail remains fixed. Parent tween uses `ease: "none"`. | Vertical evidence cards. |
| Provenance | Enter once | Three nodes reveal in a 70ms stagger. | Visible by default. |

## React implementation rules

```tsx
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(ScrollTrigger);

useGSAP(() => {
  const timeline = gsap.timeline({
    scrollTrigger: {
      trigger: railRef.current,
      start: "top top",
      end: "+=150%",
      pin: true,
      scrub: 0.7,
    },
  });
  timeline.to("[data-source]", { x: 0, y: 0, rotation: 0, stagger: 0.08 });
}, { scope: sectionRef });
```

- Create ScrollTriggers top to bottom and call `ScrollTrigger.refresh()` after fonts or media alter layout.
- Use one ScrollTrigger on a timeline, never child tweens within a scroll-driven timeline.
- For horizontal evidence, animate an inner child with `ease: "none"`; do not animate the pinned parent.
- Animate `transform` and `opacity`, never `top`, `left`, `width`, `height`, padding, or margin for motion.
- Use `will-change` only on the paper/source elements that actually animate. Clean up through `useGSAP` on unmount.
- Never send ScrollTrigger `onUpdate` into React state at 60fps; update a DOM ref/CSS variable instead.

## Reduced motion

`prefers-reduced-motion: reduce` disables pinning, scrub, parallax, path draw, and automatic autoplay. All scene content is rendered in final reading order. Provide a “Reduce motion” preference in product settings if feasible; system preference remains authoritative by default.

