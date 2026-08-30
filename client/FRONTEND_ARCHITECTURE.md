# Frontend Architecture

`src/app.jsx` is the route composition root. `PublicLayout` owns the public header, footer, and compact assistant. `AppLayout` owns authenticated sidebar/header navigation and deliberately has no public footer.

`context/AuthContext.jsx` restores live identity, permission codes, and clearance from the backend. UI permission checks are presentation gates only. `ThemeContext.jsx` controls variable-driven light/dark themes.

`services/api.js` supplies the only HTTP client. It configures the base URL, bearer authorization, JSON parsing, request IDs, typed API errors, and friendly status messages. Page code does not call AI Engine or RAG directly.

Page boundaries:

- `Home`, `About`, and `Docs` are tailored editorial experiences.
- `ContentPage` renders expandable first-pass public topics from centralized content.
- `Forms` covers contact, bug, and access-request presentations.
- `AppPages` contains operational pages while the application remains compact. Split these into feature folders as individual workflows grow.

Chat presentation is isolated in `ChatWidget`. It currently uses the public HTTP transport. Future authorized HTTP and WebSocket transports should live under `services/chat/`, selected by investigation context rather than embedded in the UI.
