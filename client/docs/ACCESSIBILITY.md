# Accessibility

- A keyboard-visible skip link targets the main landmark.
- Mega-navigation opens by pointer, focus, or click; mobile navigation uses native `details` and `summary` controls.
- Route changes scroll to the top and move focus to the page heading without forcing scroll.
- Headings, landmarks, breadcrumbs, navigation labels, article contents, tables, lists, definitions, and form labels use semantic elements.
- Focus uses a high-contrast global ring. Statuses include text, not color alone.
- Chat uses an accessible region, busy state, labeled form control, explicit source disclosure, error request IDs, and retry control.
- Public search opens from its labeled header control or `Ctrl/Cmd+K`, focuses the query, exposes listbox semantics, and supports Up, Down, Enter, and Escape.
- The contextual menu uses menu/menuitem semantics and provides browser-equivalent actions rather than suppressing functionality. Selected text can be passed directly into topic search.
- The normal browser cursor is retained; keyboard focus remains visible and touch interaction does not depend on hover.
- Reduced-motion preferences remove animation and smooth scrolling.
- Public graph SVG carries a meaningful accessible label and public data is explicitly identified as synthetic.

Future verification should include automated axe checks and manual keyboard, NVDA, zoom, contrast, and mobile screen-reader testing.
