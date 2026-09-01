# PRYSM INTELLIGENCE — PUBLIC FRONTEND DEEPENING, REDESIGN & UX OVERHAUL

## ROLE

You are continuing development of the Prysm Intelligence frontend.

The base React application has already been created and the fundamental project structure is working. Do **not** throw away good underlying architecture simply because the visual result is unsatisfactory.

Your job in this phase is to make the public-facing side of Prysm Intelligence feel like a **real, mature research and financial-intelligence organization**, not a generic AI startup landing page.

You are expected to be creative, inspect what already exists, identify weak areas yourself, and improve things beyond the literal instructions below wherever doing so produces a better product.

Do not wait for every page to be manually specified. Make intelligent product decisions.

---

# PRIMARY OBJECTIVE

Rework and greatly expand everything a visitor can experience **before authentication/login**.

The public website should become:

* deeper
* more informative
* more credible
* more readable
* more navigable
* more interconnected
* more human
* more functional
* more accessible
* more search-engine friendly
* more visually distinctive
* more like a mature research organization

The current implementation is too shallow and visually resembles a modern AI-generated website.

That needs to change.

The target visual language is a carefully blended system inspired by:

* Windows 10-era desktop/application UI
* Wikipedia
* technical documentation portals
* serious research organizations
* financial dashboards
* enterprise software
* Apple interface discipline
* classic web hyperlinks and information architecture
* clean institutional websites

Do NOT copy any one product literally.

Combine the strongest principles from those references into a coherent Prysm identity.

---

# IMPORTANT VISUAL DIRECTION

## 1. REMOVE THE "GENERIC AI WEBSITE" LOOK

The current typography, spacing, cards, gradients, floating glassmorphism, excessive rounded containers, and overall visual language feel too AI-generated.

Reduce or eliminate:

* overly futuristic typography
* excessive gradient backgrounds
* excessive glassmorphism
* giant soft cards
* unnecessary floating blobs
* excessive pill-shaped UI
* excessive rounded corners
* unnecessary glowing effects
* meaningless decorative animation
* trendy AI-dashboard aesthetics
* oversized empty hero areas
* repetitive card grids

The product must feel designed by people who care about information architecture.

---

# 2. TYPOGRAPHY

Replace the current overly "AI startup" typography.

Choose typography that feels:

* human
* editorial
* institutional
* highly readable
* professional
* slightly technical
* comfortable for long-form reading

Use a strong typography hierarchy.

The typography system should work equally well for:

* research articles
* documentation
* tables
* headings
* dashboards
* navigation
* metadata
* footnotes
* citations
* links

Do not use strange futuristic fonts simply because they look technological.

Prefer highly readable system/editorial/technical fonts.

The font implementation must be centralized so the entire website can be changed later from a small number of global variables/configuration points.

---

# 3. COLOR SYSTEM

Move toward the LIGHTER GREEN direction.

Primary identity colors should be based around:

#00614c
#1d561a
#317227
#4da53b
#acd1a9

But use them intelligently.

The visual system should contain:

* light backgrounds
* white/off-white surfaces
* monochrome gray hierarchy
* restrained green accents
* dark green for strong headings/actions
* lighter green for selected states
* neutral borders
* subtle success/warning/error colors

Green must NOT cover the entire interface.

The green palette should feel like a financial/research identity.

Use mostly monochrome colors with green providing meaningful emphasis.

---

# 4. GLOBAL DESIGN TOKENS

Everything important must be centralized.

Create a global design-token system for:

* primary colors
* secondary colors
* background colors
* text colors
* muted text
* borders
* shadows
* typography
* spacing
* radii
* transition durations
* focus states
* breakpoints
* theme values

Theme changes should be achievable primarily through variables rather than rewriting components.

---

# HEADER — MAJOR REDESIGN REQUIRED

This is one of the most important parts of this task.

The current header hover behavior is far too simple.

I want a **full-width mega-navigation interaction**.

Think of the quality of a sophisticated application navigation system rather than a conventional website dropdown.

## Behavior

When the user hovers/focuses a major category:

* the navigation expands into a large panel
* the panel spans essentially the full website width
* it should occupy a substantial but controlled vertical area
* target approximately 35–50% of viewport height depending on content
* it should feel like a temporary navigation workspace
* the rest of the page should remain visible but visually deprioritized
* opening and closing must be smooth
* no irritating animation
* keyboard focus should behave correctly
* mouse movement should not cause accidental closing

The interaction should feel similar in spirit to mature application navigation systems.

## Example structure

Top-level navigation categories should be consolidated into meaningful groups such as:

### Research

* Ethical AI
* AI Ethics Framework
* Responsible AI
* Fraud Detection Research
* AML Research
* Financial Intelligence
* Behavioral Analysis
* Transaction Intelligence
* Model Research
* Research Publications

### Intelligence

* Intelligence Overview
* Models
* Data Representation
* GNN Intelligence
* Network Analysis
* Relationship Intelligence
* Analysis Concepts
* Playground
* Investigations Overview

### Academy

* Academy
* Data Science
* Python
* Financial Intelligence
* AML Fundamentals
* Machine Learning
* Opportunities
* Institutions
* Learning Resources
* Rules & Regulations

### Resources

* Documentation
* Architecture
* API
* Data
* Developer Guide
* Integration
* FAQ
* Glossary
* Research Notes
* Knowledge Base

### Organization

* About Prysm
* Our Story
* Team
* Abyssinia Associates
* Contributors
* Beta Program
* Contact
* Partnerships

### Reports

* Bug Reports
* Resolution Guide
* Release Notes
* System Status
* Security
* Privacy
* Terms

Do not blindly use these exact categories. Inspect the project and make the categorization better where appropriate.

Each category should have:

* title
* short explanation
* grouped internal links
* optional featured route
* subtle visual hierarchy

The navigation must feel like an information system.

---

# FOOTER — EXTREME INFORMATION ARCHITECTURE

The footer must become much larger and more comprehensive.

Target approximately **50+ meaningful links/routes** across grouped sections.

Do NOT create meaningless duplicate links solely to hit the number.

Create real pages/routes where necessary.

The footer should resemble the footer of a large research organization.

Possible groups:

### Prysm Intelligence

* Home
* About
* Mission
* Vision
* Research
* Intelligence
* Academy
* Documentation

### Research

* Ethical AI
* Responsible AI
* Fraud Detection
* AML
* Behavioral Intelligence
* Transaction Analytics
* Network Intelligence
* GNN Research
* Model Research
* Research Notes

### Intelligence

* Models
* Data Representation
* Graph Intelligence
* Investigations
* Intelligence Playground
* Search
* Methodology
* Intelligence Concepts

### Academy

* Academy Home
* Data Science
* Python
* Machine Learning
* Financial Intelligence
* AML
* Opportunities
* Institutions
* Resources
* Regulations

### Documentation

* Documentation Home
* Architecture
* API
* Frontend
* Backend
* Data
* Integration
* Chat
* Authentication
* Security
* Glossary
* FAQ

### Organization

* About
* Team
* Contributors
* Beta Testers
* Contact
* Partnerships
* Special Thanks

### Reports & Policies

* Bug Report
* Resolution Guide
* System Status
* Release Notes
* Privacy Policy
* Terms
* Security
* Responsible Disclosure

Also include:

* GitHub
* social links
* contact
* copyright
* product version where appropriate

Every link should correspond to a real route or intentionally meaningful external destination.

---

# ROUTE DEPTH

Do not keep everything as a few giant pages.

Create a proper information architecture.

You are authorized to create additional public pages that make Prysm more coherent.

Aim for a substantial public knowledge system.

Potential pages include:

* Research hub
* Ethical AI
* AML research
* Fraud research
* Behavioral intelligence
* GNN research
* Model methodology
* Intelligence methodology
* Data philosophy
* Responsible AI
* Privacy architecture
* Security philosophy
* Documentation hub
* Architecture
* API documentation
* Data documentation
* Integration guide
* Developer guide
* Glossary
* FAQ
* Academy hub
* Data science
* Python
* Machine learning
* Financial intelligence
* Opportunities
* Institutions
* About
* Story
* Team
* Contributors
* Beta program
* Contact
* Reports
* Bug reporting
* Resolution guide
* Release notes
* Security
* Terms
* Privacy

You do not need to build every possible page with the same amount of detail, but the public architecture should clearly feel expandable and intentional.

---

# HOME PAGE — REBUILD FOR DEPTH

The homepage must not simply be a collection of marketing cards.

It needs to explain Prysm progressively.

Suggested structure:

1. Hero
2. What Prysm Intelligence is
3. The problem it addresses
4. Why financial intelligence requires more than conventional rules
5. How Prysm works
6. Transaction intelligence
7. Behavioral intelligence
8. Graph/network intelligence
9. AI-assisted explanation
10. Investigation workflow
11. Ethical AI
12. Data and provenance
13. Security and authorization
14. GNN relationship demonstration
15. Research methodology
16. Academy
17. Documentation
18. Beta/testing
19. Testimonials
20. FAQ
21. Strong final CTA

Do not use identical cards for every section.

Use:

* diagrams
* text blocks
* timelines
* metadata
* comparison tables
* callouts
* inline links
* technical notes
* expandable sections
* small interactive demonstrations
* editorial layouts

---

# HOME PAGE HERO

The hero needs a strong short pitch.

The previously mentioned approximately 57-character constraint is not strict.

Write a strong concise statement describing what Prysm actually does.

The phrase should be clear enough for a non-technical person while still sounding credible to researchers and professionals.

Do not write generic lines such as:

"Unlock the future of AI."

The visitor should understand the category of product.

"Prysm Intelligence" should remain the primary identity.

---

# "PRYSM INTELLIGENCE" BRANDING

Use "Prysm Intelligence" prominently.

Contextually, other references such as:

* Prysm AI
* Prysm
* Prysm IO

may appear where technically or editorially appropriate.

Do not constantly repeat the full company/product name.

---

# GN GRAPH / GNN DEMONSTRATION

The homepage should include a meaningful visual demonstration of relationship intelligence.

Use demo data only.

It should communicate:

* entities
* transactions
* relationships
* clusters
* suspicious connections
* network structure

This should look like an intelligence visualization, not a decorative animation.

Allow controlled interaction where useful.

Do not sacrifice performance.

---

# ABOUT SECTION — MASSIVE DEPTH INCREASE

The current About content is too shallow.

Build an actual institutional story.

Cover:

## Origin

Explain:

* why the project was conceived
* what problem motivated it
* why financial intelligence was selected
* why conventional systems are insufficient
* why explainability matters
* why graph intelligence matters
* why ethical AI matters

## Problem Statement

Clearly explain:

* financial fraud
* money laundering
* suspicious activity
* fragmented transaction information
* behavioral anomalies
* network relationships
* investigation burden
* explainability

Avoid overstating capabilities.

Clearly distinguish:

* research/demo capabilities
* implemented capabilities
* future capabilities

## Project Philosophy

Explain principles such as:

* responsible AI
* human oversight
* evidence
* provenance
* explainability
* privacy
* access control
* security
* transparency
* research discipline

## Team

Create professional profiles for the project creators.

Use image placeholders.

Include editable areas for:

* name
* role
* contribution
* interests
* biography
* project responsibilities

Do not fabricate credentials.

## Special Thanks

Create a meaningful acknowledgements section.

## Project Evolution

Add a timeline showing the evolution of the project.

## Architectural Philosophy

Explain why the system separates:

* backend
* AI engine
* RAG
* graph intelligence
* ML data
* frontend

Use diagrams where helpful.

---

# RESEARCH SECTION — MAJOR EXPANSION

The existing Research section is far too small.

Turn Research into one of the site's largest knowledge areas.

Create a proper Research hub.

Topics should include at minimum:

* Ethical AI
* Responsible AI
* Fraud Detection
* AML
* Behavioral Intelligence
* Transaction Analytics
* Network Intelligence
* Graph Neural Networks
* Model Evaluation
* Explainability
* Data Provenance
* Financial Intelligence
* Human Oversight
* Security and Trust

Create individual pages or well-organized subsections where justified.

---

# ETHICAL AI PAGE

This needs substantial editorial depth.

Discuss:

* purpose
* consent
* human oversight
* explainability
* privacy
* data minimization
* provenance
* model limitations
* bias
* false positives
* false negatives
* responsible investigation
* access control
* auditability
* security
* responsible deployment
* human review

Make clear that Prysm is a research/intelligence system and not an autonomous authority that should determine guilt.

Use language such as:

"indicators"
"signals"
"risk"
"evidence"
"investigation"
"assessment"

rather than pretending the system conclusively determines criminal behavior.

---

# RESEARCH VISUAL LANGUAGE

Research pages should feel like technical articles.

Use:

* article headers
* metadata
* section navigation
* breadcrumbs
* citations/placeholders
* tables
* diagrams
* side notes
* definitions
* references
* related articles
* "read next" links
* inline hyperlinks

Introduce classic web behavior where appropriate.

For example:

> Read the methodology documentation.

Use subtle **blue underlined hyperlinks** in contexts where a traditional documentation/wiki convention makes sense.

Not everything should be green buttons.

A normal blue hyperlink can make the interface feel much more like a serious information repository.

---

# DOCUMENTATION — MAKE THIS EXTREMELY DEEP

The documentation page should become one of the most detailed public pages.

It should feel closer to a serious open technical documentation portal than a marketing page.

Create a Documentation hub and structured subsections.

At minimum cover:

## Introduction

* What Prysm Intelligence is
* Who it is for
* What it does
* What it does not do

## System Overview

* overall architecture
* frontend
* backend
* AI engine
* RAG
* GNN
* data
* PostgreSQL
* Parquet/ML data
* authentication
* authorization

## Application Flow

Explain:

Visitor
→ public website
→ access request
→ administrator review
→ authentication
→ authorization
→ intelligence application
→ investigation
→ analysis
→ evidence
→ explanation

## Data Flow

Explain:

raw data
→ processing
→ storage
→ analysis
→ graph relationships
→ model outputs
→ investigation findings
→ RAG context
→ user-facing explanation

## Backend API

Document the frontend contract from `BACKEND_API.md`.

Include:

* endpoint
* method
* purpose
* access requirement
* expected input
* output
* failure states

Do not expose secrets or credentials.

## Authentication

Explain:

* login
* access request
* sessions/tokens
* protected requests
* logout
* identity
* permissions

## Authorization

Explain that the backend is authoritative.

Explain security clearance conceptually.

Do not expose implementation-sensitive information.

## Chat

Document:

* public chat
* authorized chat
* WebSocket chat
* context behavior
* security expectations
* sources
* evidence
* request IDs
* conversation IDs

## Investigation System

Explain:

* searching
* subject profiles
* investigations
* analysis
* runs
* findings
* evidence
* graph relationships

## GNN

Explain the role of graph intelligence.

## RAG

Explain:

* document ingestion
* retrieval
* source grounding
* contextual answers

## Models

Explain model metadata and how model intelligence fits into the application.

## Data Representation

Explain how data becomes useful intelligence.

## Error Handling

Document standard API errors:

400
401
403
404
409
413
429
502
503

Explain request IDs and troubleshooting.

## Integration

Explain how another application could conceptually integrate with Prysm.

## Glossary

Create a substantial glossary containing relevant terms.

Examples:

* AML
* anomaly detection
* behavioral analysis
* clearance
* evidence
* graph
* GNN
* RAG
* investigation
* subject
* transaction
* provenance
* risk signal

## FAQ

Create a significant FAQ rather than five generic questions.

---

# WIKIPEDIA-LIKE INFORMATION DESIGN

The public website should contain strong information density.

This does NOT mean making everything ugly or cramped.

Instead use:

* readable article widths
* section indexes
* breadcrumbs
* side navigation
* footnotes
* references
* inline links
* related information
* definitions
* tables
* callouts
* structured metadata
* article navigation
* "see also"
* "related research"
* "further reading"

Allow people to discover information naturally.

The site should feel interconnected.

---

# OLD-WEB HYPERLINK LANGUAGE

Use traditional links intentionally.

Examples:

* blue underlined links
* "Read more"
* "See methodology"
* "See related research"
* "View API"
* "Open architecture"
* "See glossary"
* "Read the full report"

Do not convert everything into giant modern buttons.

Buttons should represent actions.

Links should represent navigation and knowledge.

---

# ANIMATION & SMOOTHNESS

The site should be more animated than the current version, but not overloaded.

Use animation for:

* navigation expansion
* route transitions
* section reveal
* data visualization
* hover state
* loading
* progressive disclosure
* graph demonstration
* menu opening

Do NOT animate:

* every card
* every heading
* every paragraph
* every background
* every scroll movement

Animations must help orientation and feedback.

Prefer short, controlled transitions.

---

# ROUTE TRANSITIONS

Whenever navigation changes route:

* automatically scroll to the top
* preserve expected browser behavior
* avoid jarring content jumps
* ensure focus management is sensible
* ensure loading states are clear

---

# ACCESSIBILITY — SERIOUS REQUIREMENT

Treat accessibility as a first-class engineering requirement.

Implement strong accessibility throughout the public website.

At minimum:

* semantic HTML
* proper heading hierarchy
* landmarks
* nav regions
* descriptive link labels
* keyboard navigation
* visible focus states
* aria labels where necessary
* accessible mega-menu behavior
* keyboard-accessible dropdowns
* screen-reader friendly content
* alt text for meaningful images
* empty alt for decorative imagery
* sufficient color contrast
* reduced-motion support
* accessible form validation
* descriptive errors
* accessible loading states
* accessible modals
* no hover-only essential functionality

A blind user must be able to understand the structure and navigate the site using assistive technology.

Do not use color alone to communicate meaning.

---

# SEO

Perform proper SEO across public routes.

Implement:

* meaningful page titles
* meta descriptions
* canonical URLs where appropriate
* Open Graph metadata
* Twitter/social metadata
* semantic HTML
* structured headings
* clean URLs
* descriptive link text
* sitemap strategy
* robots strategy
* meaningful route metadata
* sensible document titles

Avoid keyword stuffing.

SEO must describe the actual application honestly.

---

# CONTENT DEPTH

This phase specifically requires **content generation and population**.

Do not leave large blank sections labeled:

"Coming soon."

Where the project has enough information to explain something, write it.

Generate substantial original explanatory content about:

* Prysm
* financial intelligence
* fraud
* AML
* behavioral anomalies
* graph intelligence
* GNN
* AI explanation
* RAG
* ethical AI
* system architecture
* data flow
* security
* investigations
* research philosophy
* academy material

The content should feel like it belongs to a real technical organization.

Do not invent real-world facts about Prysm that have not been established.

When information is unknown, use editable placeholders or clearly describe it at the conceptual/project level.

---

# CHATBOT — MUST BE INVESTIGATED AND FIXED

Current public chatbot behavior:

> "Prysm is temporarily unavailable."

Request:

`93965fe9-9e7b-46ea-9974-b45200586270`

You MUST inspect the actual implementation and determine why this occurs.

Do not simply replace the error message.

Trace the complete path:

UI
→ frontend chat service
→ HTTP or WebSocket
→ backend API
→ response parsing
→ state update
→ error handling

Compare the implementation against `BACKEND_API.md`.

Check:

* endpoint URL
* request shape
* public vs authorized endpoint
* authentication handling
* WebSocket protocol
* request IDs
* response types
* timeout handling
* error parsing
* environment variables
* CORS assumptions
* JSON structure
* connection lifecycle

For public users the frontend must use:

`POST /chat/public`

with:

`{question, conversationId?}`

Do not send:

* authenticated
* context
* clearance
* accessScope

The backend explicitly rejects those fields.

For authenticated users use the authorized behavior defined by the backend contract.

Fix the issue at its actual root.

If the frontend is expecting an API that does not exist, document the discrepancy and create the required backend implementation task.

Do NOT fake successful responses.

---

# BACKEND GAP IDENTIFICATION

Inspect `BACKEND_API.md` and compare it to the desired public/admin application.

Where functionality required for the frontend is not implemented, create:

`client/docs/BACKEND_REQUIRED_APIS.md`

For every missing API document:

* proposed endpoint
* HTTP method
* purpose
* frontend feature requiring it
* request body
* response structure
* authorization requirement
* error behavior
* why it is necessary
* suggested backend implementation location

Examples already noted in the backend contract include:

* dashboard data
* application review
* user mutation
* password reset/change
* investigation updates
* investigation timeline
* feedback
* export
* model downloads

Do not silently pretend these features exist.

The frontend can provide graceful placeholders or disabled states where implementation is pending.

---

# IMAGE HANDLING

Where professional photographs or specific illustrations are required but real assets are not available:

use clean image placeholders.

Examples:

* team photos
* organization photography
* research imagery

Make placeholders easy to replace later.

Do not permanently embed fake identities.

---

# ETHIOPIAN / ABYSSINIAN VISUAL DETAIL

Use subtle Ethiopian financial/cultural inspiration.

The goal is sophistication, not decoration.

Possible applications:

* restrained geometric motifs
* subtle patterning
* section dividers
* abstract financial motifs
* very subtle visual references to Ethiopian monetary/history patterns

These should appear selectively in wide sections or special research areas.

Do NOT turn the site into a tourism/cultural website.

Prysm remains a financial-intelligence research system.

---

# PUBLIC APPLICATION STRUCTURE

Maintain a distinction between:

## Public shell

Contains:

* public header
* mega navigation
* page content
* public chatbot
* footer

## Authenticated application shell

Contains:

* dashboard header
* sidebar
* operational navigation
* application workspace
* no public footer

Do not accidentally merge these experiences.

---

# RESPONSIVENESS

Every new route must work on:

* desktop
* laptop
* tablet
* mobile

The mega-menu should gracefully transform on smaller screens.

Do not simply shrink desktop layouts.

Use accessible mobile navigation.

---

# PERFORMANCE

Despite the increased depth, preserve performance.

Avoid:

* unnecessary heavy animation
* huge images
* repeated API calls
* uncontrolled rendering
* giant client-side data payloads
* unnecessary dependencies

Lazy-load heavy sections/pages where appropriate.

---

# ROUTING

Use clean routes.

Examples:

`/`
`/about`
`/research`
`/research/ethical-ai`
`/research/fraud-detection`
`/research/aml`
`/research/graph-intelligence`
`/research/responsible-ai`

`/intelligence`
`/intelligence/models`
`/intelligence/graph`
`/intelligence/playground`

`/academy`
`/academy/data-science`
`/academy/python`
`/academy/machine-learning`

`/docs`
`/docs/architecture`
`/docs/api`
`/docs/data`
`/docs/integration`
`/docs/security`
`/docs/chat`
`/docs/glossary`

etc.

Use your judgment to produce the cleanest architecture.

---

# INFORMATION ARCHITECTURE PRINCIPLE

Every public page should help answer at least one of these questions:

* What is Prysm?
* Why was Prysm created?
* What problem does it solve?
* How does it work?
* Why should I trust its design?
* What research supports it?
* What does the technology mean?
* How can I understand the system?
* How can I learn?
* How can I contribute?
* How can I contact the organization?
* How can I request access?

Pages should link naturally to each other.

Avoid isolated orphan pages.

---

# MICROCOPY

Write practical, human microcopy.

Avoid:

* "Unlock the future"
* "Revolutionize your workflow"
* "AI-powered next-generation intelligence"
* "Seamlessly transform..."
* generic startup language

Prefer:

* specific descriptions
* factual explanations
* useful instructions
* clear terminology

---

# UI DETAILS

Use a mixture of:

* compact headers
* editorial article layouts
* simple cards where appropriate
* tables
* information boxes
* side notes
* tabs
* accordions
* breadcrumbs
* segmented navigation
* classic links
* status badges
* metadata rows
* diagrams
* timelines

Do not make every component a rounded card.

Different information types should visually behave differently.

---

# FOOTER + HEADER CONSISTENCY

The header categorization and footer should reflect the same information architecture.

Users should be able to understand that:

header = major topic discovery

footer = complete site map

The footer should be much more comprehensive than the header.

---

# CREATE PUBLIC CONTENT REGISTRY

Centralize route/page metadata where practical.

Each page should be able to define:

* title
* description
* category
* navigation placement
* SEO metadata
* breadcrumb
* related pages

This will make the large number of routes maintainable.

---

# DOCUMENTATION FOR FUTURE AGENTS

Create/update these files inside `client/docs/`:

## `FRONTEND_ARCHITECTURE.md`

Document:

* architecture
* folders
* components
* state
* routing
* API
* themes

## `PUBLIC_SITE_MAP.md`

Document every public route.

## `DESIGN_SYSTEM.md`

Document:

* typography
* colors
* tokens
* components
* spacing
* interaction principles

## `CONTENT_ARCHITECTURE.md`

Document how public content is structured.

## `ACCESSIBILITY.md`

Document accessibility implementation decisions.

## `SEO.md`

Document SEO implementation.

## `CHATBOT_INTEGRATION.md`

Document:

* public chat
* authorized chat
* WebSocket
* request lifecycle
* errors
* debugging

## `BACKEND_REQUIRED_APIS.md`

Document frontend dependencies on backend APIs that do not exist yet.

## `IMPLEMENTATION_STATUS.md`

Record:

* completed
* partially completed
* known bugs
* pending backend dependencies
* next recommended tasks

These documents are not optional.

They are continuity infrastructure for future coding agents.

---

# DO NOT BREAK THE EXISTING GOOD FOUNDATION

Before changing code:

1. inspect the current application
2. inspect routes
3. inspect components
4. inspect API services
5. inspect theme implementation
6. inspect chatbot
7. inspect current dependencies
8. identify reusable components
9. retain useful abstractions
10. improve rather than blindly rewrite

The goal is a stronger application, not code churn.

---

# QUALITY BAR

When finished, a visitor should be able to spend significant time exploring Prysm without feeling that the website is empty.

The product should communicate:

"These people built an actual intelligence system and took the time to explain how it works."

not:

"This is a template generated for an AI startup."

The interface should feel:

* mature
* trustworthy
* information-rich
* slightly nostalgic
* technical
* calm
* readable
* functional
* deliberate
* distinctive

---

# FINAL SELF-REVIEW

Before declaring this task finished, inspect the entire public website from the perspective of:

### A first-time visitor

Can they understand Prysm within one minute?

### A researcher

Can they find meaningful technical information?

### A developer

Can they find architecture/API/integration information?

### A skeptical professional

Does the site explain limitations and responsible AI?

### A blind user

Can they navigate and understand the site using keyboard and screen reader semantics?

### A search engine

Does every important route have meaningful semantic content and metadata?

### A future coding agent

Can it understand what was built and continue development from the documentation?

### The product owner

Does this look substantially more impressive than the current version?

If the answer to any of these is no, keep improving.

---

# IMPORTANT CREATIVE AUTHORITY

You have permission to make additional improvements that were not explicitly requested when they clearly improve Prysm Intelligence.

Do not interpret this document as a reason to stay narrowly inside the lines.

Think like:

* a senior frontend engineer
* a UX architect
* an information architect
* a technical writer
* an accessibility specialist
* an SEO engineer
* a research-product designer

The final product should feel like the result of all six disciplines working together.

Do not ask for permission to add obvious missing pieces.

Build them.

# COMPLETION CONDITION

The task is complete only when:

* the public visual identity has been substantially redesigned
* the mega-navigation works correctly
* typography feels human and readable
* colors use the lighter green + monochrome direction
* the public site has significantly more content
* About is substantially deeper
* Research is substantially deeper
* Documentation is substantially deeper
* 50+ meaningful public navigation destinations exist or are structurally represented
* footer architecture is comprehensive
* route transitions scroll to top
* accessibility has been addressed seriously
* SEO has been implemented
* the chatbot issue has been investigated and fixed or precisely diagnosed
* backend API gaps have been documented
* future-agent documentation has been updated
* no major public page feels empty
* the overall experience feels like a mature Prysm Intelligence product rather than a generic AI website

Do not stop at "the base implementation is ready."

This task is specifically about pushing the existing implementation much further.

Be creative.
Be critical of your own work.
Inspect what looks weak.
Replace what does not work.
Add what is missing.
Make the result feel finished.
