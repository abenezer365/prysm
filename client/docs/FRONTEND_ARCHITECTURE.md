# Frontend Architecture

The Vite React application has two deliberate shells. `PublicLayout` owns the institutional header, full-width mega-navigation, editorial routes, public chat, route metadata, and comprehensive footer. `AppLayout` owns the authenticated operational workspace and never renders the public footer.

`config/publicRegistry.js` is the public information architecture. It defines editorial pages, documentation routes, glossary terms, related reading, and mega-navigation groups. `KnowledgePage` renders registered research, intelligence, Academy, organization, report, and policy articles. `DocArticle` renders focused technical references. Tailored Home, About, and Docs hub pages provide deeper layouts.

`services/api.js` remains the single HTTP boundary. `AuthContext` loads live backend identity, permissions, and clearance. Frontend permission gates are UX only. Theme values live in CSS variables. `RouteManager` performs title/description/social metadata updates, scroll restoration, and heading focus management.
