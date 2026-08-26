# Asset Manifest

The selected direction needs very few non-code assets. The interface itself is the visual material; decorative media is intentionally constrained.

## Delivered assets

| File | Use | Delivery rule |
| --- | --- | --- |
| [delividence-mark.svg](assets/delividence-mark.svg) | Small product mark / favicon starting point. | Use `currentColor`; do not rasterize. |
| [evidence-route.svg](assets/evidence-route.svg) | Landing change-route/path motif. | Inline SVG; animate `stroke-dashoffset` only when motion is allowed. |
| [source-index-bracket.svg](assets/source-index-bracket.svg) | Source grouping / hero marker. | Decorative; `aria-hidden`. |
| [waveform-sample.svg](assets/waveform-sample.svg) | Placeholder waveform before real transcript wave data exists. | Decorative only; real audio gets text transcript. |
| [paper-noise.svg](assets/paper-noise.svg) | Optional 3–4% canvas texture. | CSS background only; do not animate. |
| [hero-pencil.svg](assets/hero-pencil.svg) | Hero-only physical editorial pencil. | Decorative; absolute-positioned at desktop only; `aria-hidden`. |
| [hero-paperclip.svg](assets/hero-paperclip.svg) | Hero-only physical editorial paperclip. | Decorative; absolute-positioned at desktop only; `aria-hidden`. |
| [landing-final.png](previews/landing-final.png) | Design preview, not production page media. | Reference only. |
| [dashboard-main.png](previews/dashboard-main.png) | Dashboard reference. | Reference only. |
| Product boards | Screen references. | Reference only. |

## Real content assets required at build time

| Asset class | Origin | Rules |
| --- | --- | --- |
| Source artifact | User upload / pasted content | Store original, source ID, uploader, timestamp, integrity metadata. |
| Screenshot / design proof | Freelancer upload | Preserve intrinsic width/height and object metadata. |
| URL proof | Freelancer supplied URL | Store fetched/check timestamp separately from client decision. |
| Audio / video source | Client/freelancer upload | Always provide transcript or accessible title; never autoplay with sound. |

## Video and GIF decision

Do **not** use a generated GIF/video as proof that the app works. The competition demo must show the real product running. The landing’s source-to-record choreography is native GSAP and has a static fallback, which is sharper, more accessible, and lighter than an autoplay marketing video.

Create a real 12–15 second product loop only after the working application exists. It should be captured from the deployed app: source intake → one priority question → client reply → baseline state update. Export `webm` + `mp4` and a poster image; mute by default; respect reduced motion; never use it as the hero LCP asset.
