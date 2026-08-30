# Content Architecture

Public metadata and article bodies are registered in `src/config/publicRegistry.js`. Each article defines title, description, category, ordered sections, and related routes. Documentation pages use a parallel map. Mega-navigation columns and glossary definitions share the same module.

Tailored pages are reserved for content that needs richer composition: Home progressively explains category, problem, analytical lenses, workflow, ethics, provenance, security, graph demonstration, knowledge resources, FAQ, and access. About covers origin, problem, principles, evolution, architecture, builders, acknowledgements, and future direction. Docs acts as the technical index and API overview.

Unknown identities, affiliations, contacts, legal terms, and external references remain explicitly editable rather than fabricated.

`src/config/searchIndex.js` composes a searchable index from registered articles, documentation, glossary definitions, aliases, descriptions, section bodies, categories, and key static routes. Ranking favors complete multi-term matches and title matches. Search results always show meaningful titles and descriptions, never raw route strings.
