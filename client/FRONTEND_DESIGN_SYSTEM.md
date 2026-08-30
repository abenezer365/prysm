# Frontend Design System

Theme tokens live in `src/styles/index.css`. Light and dark themes define page, surface, elevated surface, text, muted text, border, accent, strong/soft accent, success, warning, danger, info, focus, overlay, and shadow values.

The palette centers on deep green `#00614c`, with quiet neutral backgrounds. The dark theme uses green for meaning rather than glow. Typography uses a system sans stack and monospace for identifiers, timestamps, technical labels, and figures.

Core reusable classes are `.shell`, `.eyebrow`, `.display`, `.page-title`, `.section-title`, `.surface`, `.card`, `.button`, `.button-primary`, `.button-secondary`, `.field`, `.label`, `.muted`, and `.mono`. Cards use modest 12px radii. Buttons and forms use 8px radii. Focus uses a visible three-pixel ring.

Status must always include text or iconography, never color alone. Motion is limited to short hover and menu transitions, and reduced-motion preferences disable it. Dense data uses borders and alignment instead of excessive nested cards.
