# 21st.dev Component Map

21st components are accelerators, not the visual direction. Start with behavior/accessibility, then apply the Field Notes tokens and remove incompatible gradients, radii, shadows, and colorful defaults.

| Need | 21st search result | Use / adaptation |
| --- | --- | --- |
| Sidebar shell | `Dashboard Sidebar` — arunjdass, ID `14941` | Use structure only; replace styling with 224px paper sidebar and saffron active rule. |
| Source upload | `File Dropzone` — joyco, ID `19201` | Use accessible drop mechanics; rebuild surface as paper intake field. |
| Upload alternative | `File Upload Multi-File Dropzone` — ephraimduncan, ID `18111` | Evaluate if multi-file progress is needed. |
| Activity log | `Timeline` — nyxbui, ID `1074` | Use vertical sequencing pattern; add actor, source, version and event semantics. |

Search before installing and inspect code before importing. Do not install components automatically into this repository until the implementation stack exists. Avoid “animated sidebar” defaults and catalog themes; they conflict with the selected design.

