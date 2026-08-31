# Public Frontend Overhaul Status

## Completed

- [x] Human editorial and institutional typography
- [x] Light green plus monochrome token system with compact radii
- [x] Full-width desktop mega-navigation with pointer, focus, and click behavior
- [x] Native mobile disclosure navigation
- [x] Six-group footer map containing more than 50 meaningful destinations
- [x] Central public content, route metadata, glossary, and navigation registry
- [x] Deep Home, About, Research, Documentation, Intelligence, Academy, Organization, Report, and policy content
- [x] Article contents, breadcrumbs, metadata, tables, side notes, traditional links, related reading, and FAQ
- [x] Route scroll restoration, heading focus, titles, descriptions, Open Graph, Twitter metadata, robots, and sitemap strategy
- [x] Skip navigation, focus treatment, semantic structures, reduced motion, and accessible chat states
- [x] Chat conversation continuity, sources, request IDs, retry, and outage-specific diagnostics
- [x] Root-cause diagnosis for the reported chat outage
- [x] Mandatory future-agent documentation
- [x] Existing authenticated application shell remains separate and intact
- [x] Scroll-direction-aware public header with immediate upward return
- [x] Light neutral and graphite dark themes
- [x] Responsive sparse-grid visual structure and restrained pattern token
- [x] Default browser cursor with visible keyboard focus
- [x] Indexed topic search with aliases, section content, keyboard navigation, and direct routing
- [x] Accessible Prysm context menu with history, reload, copy, new-tab, and selected-topic search
- [x] Meaningful related-reading labels with no raw route fallback text

## Known dependencies and next work

- [x] Configure a matching strong uncommitted `RAG_API_KEY`, start the integrated stack, and verify public chat, sources, request IDs, conversation continuity, and browser CORS.
- [x] Migrate the RAG provider from retired `gemini-1.5-flash` to `gemini-3.5-flash`; live provider health is `ok`.
- [ ] Add authorized investigation chat/WebSocket presentation.
- [ ] Generate absolute sitemap and canonical URLs when the production hostname is selected.
- [ ] Replace team, organizational contact, repository, legal, and citations placeholders with verified information.
- [ ] Run manual NVDA/mobile screen-reader testing and add automated browser accessibility checks.
- [ ] Add static rendering or SSR if search indexing becomes a production requirement.
