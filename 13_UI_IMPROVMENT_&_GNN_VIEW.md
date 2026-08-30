# PRYSM INTELLIGENCE — PUBLIC DEMO GRAPH + LOGIN CURSOR + AUTHENTICATED UI PREPARATION

Refine the existing React frontend without rebuilding working architecture.

First fix the missing custom cursor on the login page and make the cursor behavior consistent across the public website. Use the `VscCursor` shape from `react-icons/vsc`; use a dark-gray filled treatment in light themes and an inverted treatment in dark themes.

Improve the public homepage GNN/relationship demonstration into a convincing interactive demo rather than a decorative animation. Use clearly fictional Ethiopian names, companies, banks, accounts, and relationship data. This is explicitly a demonstration for visitors: communicate that the real relationship intelligence is available to authorized users inside the authenticated application, while the public site intentionally exposes only demonstration data.

Nodes should represent people, companies, banks, and other meaningful entities. When hovering a person, show a compact information panel with fictional but specific details such as name, entity type, role/category, related company, and example risk/relationship information. When hovering an edge, show a normalized relationship/friendship score from `0–100` and explain what the score means in this demonstration. Make the visualization feel like a realistic preview of the future GNN Maze.

Keep the graph easy to understand, smooth, responsive, and performant. It must work on mobile without becoming unreadable. Make the visual language consistent with the rest of Prysm Intelligence: restrained monochrome surfaces, subtle accent colors, clean typography, controlled motion, and no flashy AI-dashboard aesthetic.

Add clear but understated copy around the demonstration explaining that visitors are seeing a safe demonstration dataset and that real relationship intelligence requires authenticated access and appropriate authorization.

Finally, make sure the frontend is structured so that the authenticated application can connect cleanly to the finalized backend APIs for Dashboard, Search/Case, Users, Activity, RAG, News, GNN Maze, Settings, Bug Reports, Beta Testers, and Contributors. Do not fake authenticated backend data where the API does not yet exist; integrate only against the documented contract.
