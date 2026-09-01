# PRYSM INTELLIGENCE — PUBLIC FRONTEND UI, DEMO GRAPH, SEARCH, ACCESSIBILITY & CONTENT REFINEMENT

Refine the existing React frontend without unnecessarily rebuilding its working architecture. This task is for the public-facing client and public/demo experience. Preserve good implementation, inspect what already exists, and replace anything that feels generic, artificial, visually inconsistent, shallow, or unfinished. Do not work on the authenticated/admin application itself in this task, but keep the public client structured so it can connect cleanly to the finalized backend contract later.

The overall goal is a polished, human-designed Prysm Intelligence interface that feels smooth, responsive, readable, slightly old-school, highly functional, and distinctive. Take inspiration from the usability discipline of Windows-era interfaces, the information density of Wikipedia, strong technical documentation, polished Apple interaction design, and professional application interfaces, but do not copy any product literally. Avoid generic AI startup aesthetics, excessive glassmorphism, giant rounded cards, excessive gradients, unnecessary floating elements, futuristic typography, meaningless animation, and overly colorful layouts.

## Typography and language

Replace any obviously AI-styled or futuristic fonts with smooth, highly readable human/editorial/technical typography. Use a strong hierarchy for headings, body text, metadata, navigation, tables, references, and documentation.

Do not use emojis or em dashes anywhere in the UI, public content, generated copy, or documentation. Write naturally and professionally.

Keep the product language centered on “Prysm Intelligence” and financial intelligence. Do not describe the product as a “research system” or repeatedly use that wording.

## Themes and visual system

Move away from a heavily green website. Use a restrained monochrome-first visual system. Green remains an accent rather than the dominant visual color.

Provide polished light, warm beige, and deep monochrome dark themes. The dark theme should rely mainly on graphite, charcoal, black, gray, and readable off-white rather than black plus green everywhere. The warm beige theme should feel calm and editorial. Use accent colors only when they communicate interaction, status, or meaning.

Keep theme changes smooth and define colors through centralized theme variables/tokens so the system remains easy to maintain.

## Header behavior

Make the existing header feel like a mature application.

When the user scrolls downward, the header should smoothly hide. As soon as the user scrolls upward, even slightly, the header should return. Do not require the visitor to reach the very top before it returns.

The small top header must blend naturally into the current page/theme rather than looking like a separate white strip. Make desktop navigation polished and stable. Keep the existing category/mega-navigation idea, but make the interaction feel substantial and application-level rather than like a tiny website dropdown.

On mobile, the navigation should become compact, tactile, smooth, highly responsive, and easy to operate with one hand. It should feel almost like a native application interface. Make touch targets comfortable, keep the hierarchy clear, and prevent accidental closing.

## Links

Fix awkward link styling throughout the site. Do not expose ugly raw route paths inside public editorial content. Use meaningful labels instead.

Use refined links with small directional arrows where they help. Align the arrow closely with the text and animate it subtly on hover. Add a smooth underline animation that follows the actual text width without moving the layout.

In technical/documentation contexts, selectively use traditional blue underlined hyperlinks when that improves the Wikipedia/knowledge-base feel. Do not force every link into the same visual pattern. Distinguish clearly between navigation links, article links, and action buttons.

## Hero responsiveness and visual pattern

Make the hero extremely responsive on desktop, tablet, and mobile. Avoid fixed heights that break on phones, overflowing text, awkward wrapping, or oversized graphics. The first viewport must remain understandable and balanced at all screen sizes.

Add a subtle sparse square-grid background inspired by polished technical product sites. Use individual squares rather than a dense full grid. Remove many squares intentionally, leave visible gaps, and use very low-opacity border-area squares so the structure is noticeable only when looking closely. Use this mainly in the hero and selectively in wide informational sections where it improves composition. Keep it performant, responsive, and decorative-only for screen readers.

Introduce subtle Ethiopian/Abyssinian financial-inspired visual patterns in a few wide sections where they naturally fit. Keep them abstract, restrained, and sophisticated rather than turning the website into a cultural-theme site.

## Custom cursor and favicon/logo

Fix the missing cursor on the login/public pages and make cursor behavior consistent across the public website.

Use the shape of `VscCursor` from `react-icons/vsc` as the basis for the cursor, matching the supplied reference image: a small, solid, sharp pointer with a similar silhouette and proportions. Keep it small and unobtrusive. Use a dark-gray/near-black filled version in light themes and an inverted light version in dark themes. It must never be required for usability and must respect reduced-motion/accessibility behavior.

Use `resources/icon.jpg` as the favicon and connect it correctly through the document head for all public routes.

Keep the existing black transparent Prysm logo in light themes. In dark themes, because the black transparent logo can disappear, use `resources/icon.jpg` or an appropriate visible light/inverted brand treatment in the places where the logo needs contrast. Do not redesign the Prysm logo.

## Text selection

Improve the selection styling so highlighted text uses a refined accent treatment appropriate to the active theme. Ensure selected text remains readable in light, dark, and beige themes.

## Search

Make the public search button fully functional.

The search must discover pages, topics, sections, links, and related content, not merely perform crude individual-word matching. Build or improve a centralized topic/content index containing page title, description, category, keywords, aliases, and route.

Results should appear quickly and allow keyboard navigation. Show a meaningful title, category, short description, and destination. Enter should open the highlighted result, Escape should close the search, and mobile search should be comfortable to use.

Cover all meaningful public destinations including Home, About, Research, Documentation, Academy, organization pages, policies, resources, and other pages created during this task.

## Right-click behavior

Do not simply disable the browser context menu.

Create a compact Prysm-themed contextual menu that follows the active theme while remaining close to normal browser expectations. Where technically appropriate, include useful actions such as Back, Forward, Reload, Copy Link, Open in New Tab, and Search Selected Topic. Keep it sharp, small, smooth, correctly positioned inside the viewport, keyboard-accessible, closable with Escape/outside click, and non-disruptive. Do not fake browser actions that cannot be performed.

## Route transitions

When users navigate to another route, automatically return the page to the top. Preserve normal browser history, back, forward, keyboard navigation, and accessibility behavior. Use restrained transitions to make navigation feel seamless without turning the website into an animation showcase.

## Public homepage GNN/relationship demonstration

Upgrade the homepage GNN/relationship visualization from decorative animation into a convincing interactive demonstration of Prysm’s relationship intelligence.

Use clearly fictional but specific Ethiopian names, companies, banks, accounts, and relationships. Do not use real sensitive people or present demo information as real intelligence.

Nodes should represent people, companies, banks, accounts, and other meaningful entities. When hovering/selecting a person, show a compact information panel with fictional details such as entity name, type, role/category, connected company or institution, and example risk/relationship information.

When hovering an edge, show a normalized relationship/friendship score from 0 to 100 and a short explanation of what the score represents in this demonstration.

The visualization should feel like a realistic preview of the authenticated GNN Maze. Show clear copy around it explaining that visitors are viewing a safe demonstration dataset and that the real relationship intelligence is available only to authorized users in the authenticated application.

Keep the graph easy to understand, visually polished, smooth, responsive, and performant. It must remain usable on phones and small screens. Use the same restrained monochrome visual language as the rest of the site.

## Public content depth

The current public content should become significantly deeper.

Do not add filler paragraphs. For every meaningful subtopic, create substantial, specific information directly related to Prysm Intelligence, its intended workflows, architecture, financial intelligence use cases, and responsible operation.

Especially deepen About, Research, and Documentation.

About should explain why Prysm was conceived, the problem being addressed, why financial intelligence requires multiple analytical perspectives, why transaction and behavioral information matters, why relationships and graph analysis matter, why explainability matters, why responsible AI matters, the project philosophy, architecture reasoning, project evolution, team placeholders, acknowledgements, limitations, and future directions. Do not fabricate credentials, partnerships, customers, certifications, or achievements.

Research should become a serious knowledge area rather than a small marketing section. Deepen ethical AI, responsible AI, fraud detection, AML, transaction intelligence, behavioral intelligence, graph intelligence, GNNs, explainability, model limitations, provenance, privacy, security, human oversight, and responsible use. Explain each topic in Prysm’s context instead of copying generic definitions.

Documentation should feel like a real technical knowledge base. Expand it into readable, interconnected long-form documentation covering what Prysm is, what it does and does not do, architecture, application flow, data flow, backend/frontend relationship, authentication concepts, authorization, security clearance, investigations, AI Engine integration, RAG, graph/GNN intelligence, evidence, provenance, limitations, API concepts, integration, error handling, glossary, FAQ, references, related topics, and further reading.

Use comfortable article widths, headings, metadata, breadcrumbs, tables, callouts, references, related links, “See also,” and “Further reading” sections where they genuinely help.

The Documentation sidebar must remain sticky and stable while the article scrolls. It must not jump around or overlap content. The sticky region should naturally respect the footer boundary so that the footer can terminate or cover the sticky area when the document reaches the end.

Whenever a subtopic such as “Privacy and Minimization” exists, expand it into a genuine, substantial section. Explain why minimization matters, what categories of information should be limited, retention considerations, contextual access, permissions, security clearance, backend enforcement, privacy during investigations, responsible intelligence workflows, and practical implications. Apply the same depth principle to every major subtopic.

## Accessibility

Treat accessibility as a product requirement.

Use semantic HTML, proper heading structure, landmarks, descriptive links, keyboard navigation, visible focus states, accessible navigation, accessible search, screen-reader-friendly content, meaningful alt text, decorative-image handling, readable contrast, reduced-motion support, accessible forms, clear errors, usable loading states, and touch-friendly controls.

Do not make important functionality dependent only on hover.

The custom cursor is decorative and must never be required to use the site.

## SEO

Apply proper public SEO across routes. Give each public page meaningful titles, meta descriptions, semantic headings, canonical handling where appropriate, Open Graph/social metadata, clean URLs, descriptive link text, and centralized route metadata. Do not keyword-stuff the content.

## Public information architecture

The public website should feel interconnected rather than like isolated landing pages. Improve navigation, internal links, related topics, article cross-references, documentation relationships, and footer discovery.

Create additional public pages when a topic deserves its own page, but do not create meaningless pages only to increase the count. Every page must have a clear purpose and useful content.

## Backend contract boundary

Do not fake authenticated backend data. The public/demo experience may use clearly labeled local demonstration data, especially for the homepage graph, but protected intelligence must come from the authenticated backend once the admin application is connected.

Keep the public client structured to integrate with the finalized backend APIs for Dashboard, Search/Case, Users, Activity, RAG, News, GNN Maze, Settings, Bug Reports, Beta Testers, and Contributors.

## Final review

Inspect the entire public client before declaring completion. Check desktop, tablet, mobile, light theme, dark theme, beige theme, header hide/show behavior, mega-navigation, search, right-click, cursor, favicon, logo visibility, text selection, route scroll reset, GNN demo, documentation sidebar/footer interaction, accessibility, SEO, chatbot/public integrations, link behavior, content depth, and overall consistency.

Be critical of your own result. If something still looks generic, too colorful, too futuristic, too artificial, too shallow, too animated, or poorly responsive, improve it. Add sensible refinements when they clearly improve Prysm Intelligence.

The final public experience should feel calm, precise, information-rich, human-designed, highly responsive, and unmistakably Prysm Intelligence.
