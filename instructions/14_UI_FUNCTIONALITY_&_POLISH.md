# PRYSM --- FINAL UI, UX, FUNCTIONALITY & PRODUCTION POLISH

Continue from the current Prysm repository and the previous finalization
work.

This is a **real implementation and verification task**, not a request
for generic generated UI.

Inspect the existing application first. Understand what is already
there, preserve working functionality, and then make the changes below.
Do not blindly rewrite everything.

## 1. Core Visual Direction

Apply this visual foundation across the entire application:

``` css
--background: #050505;
--surface: #0D0D0D;
--hover: #141414;
--text: #F2F2F2;
--text-muted: #888888;
```

Use these as the primary application tone.

The UI should feel:

-   premium
-   technical
-   intelligent
-   clean
-   modern
-   structured
-   human
-   presentation-ready
-   easy to read from a projector
-   visually spacious rather than cramped

Increase typography sizes where the current interface is too small.

Improve:

-   headings
-   body text
-   labels
-   navigation
-   buttons
-   cards
-   form text
-   status messages
-   dashboard information

Do not make everything huge. Establish a clear visual hierarchy with
comfortable spacing and readable sizes.

Avoid the current overly compact, cramped, hard-to-read feeling.

------------------------------------------------------------------------

# 2. Theme System --- Only Light and Dark

The current application has three themes.

Remove the middle/beige-night theme completely.

The application must have exactly:

-   Light
-   Dark

Remove:

-   beige/night theme
-   third theme selector
-   unused theme variables
-   third-theme components/styles
-   references to the removed theme

Make sure theme switching works throughout the entire application.

Do not leave broken theme state or unused theme code behind.

------------------------------------------------------------------------

# 3. Restore the Hero GNN Visualization

The current hero-section GNN maze/preview is too small and visually
weak.

Restore the stronger previous concept.

The hero should show a **clear, larger network visualization**
containing:

-   several visible nodes
-   visible connections
-   clear graph structure
-   enough scale to immediately communicate "graph intelligence"
-   subtle movement where appropriate

Do not turn it into a giant distracting animation.

Keep the GNN visualization **centered within the home/hero section**.

It should be large enough to understand immediately on a projector.

Make it visually clean rather than maze-like.

The visualization should support the Prysm identity: financial
intelligence, relationships, anomaly detection, and network analysis.

------------------------------------------------------------------------

# 4. Hero Background --- Real Square Grid Texture

The previous implementation misunderstood the request.

Do NOT create only two or three large squares.

Create a genuine **grid of many squares** across the hero background.

Requirements:

-   many evenly structured squares
-   visible borders/outlines
-   very low opacity
-   transparent fill / fill effectively set to `0`
-   subtle enough to remain background texture
-   responsive to screen size
-   no distracting solid blocks

The result should resemble a sophisticated technical/coding environment.

The grid should add depth without competing with the hero content.

Think:

**technical intelligence dashboard + coding environment + financial
intelligence lab**

rather than decorative random shapes.

------------------------------------------------------------------------

# 5. Hero CTA / Route to Get Started

Keep the GNN visualization centered.

Build a clear visual route from the hero into the application.

The hero should have a strong:

**Get Started**

action.

Make the CTA visually obvious and appropriately contrasted.

Create a natural visual hierarchy:

Hero message → GNN intelligence preview → Get Started → clear next
section / application entry point

Use smooth hover and transition effects.

Do not make the animation excessive.

------------------------------------------------------------------------

# 6. Restore the Default Cursor

The application currently uses a custom cursor.

Remove it.

Return the application to the normal browser/default cursor behavior.

Remove unnecessary custom cursor components, styles, event listeners,
and assets if they are no longer used.

------------------------------------------------------------------------

# 7. Buttons and Action Controls

The current buttons, especially Get Started, use colors that are too
light and lack contrast.

Fix the entire button/action system.

All important actions must be:

-   clearly visible
-   strongly contrasted
-   readable
-   visually consistent
-   accessible
-   polished
-   responsive

Do not use pale green backgrounds with white text when that produces
poor contrast.

Create a coherent action hierarchy:

-   primary action
-   secondary action
-   destructive action
-   ghost/subtle action
-   status/action controls

Use appropriate hover, focus, pressed, and disabled states.

Buttons should feel premium rather than generic.

------------------------------------------------------------------------

# 8. Shadcn + Lucide UI System

Use the existing project stack where available and standardize the
interface around **shadcn/ui** and **Lucide icons**.

Use them throughout the application for appropriate:

-   buttons
-   dialogs
-   dropdowns
-   forms
-   cards
-   menus
-   tabs
-   tooltips
-   alerts
-   navigation
-   icons
-   action controls
-   confirmation interfaces

Do not add duplicate custom components when an appropriate existing
shadcn component already solves the problem.

Use Lucide icons consistently instead of random icon sources or text
symbols.

Keep the result cohesive.

------------------------------------------------------------------------

# 9. Box / Border / Luxury Structure

Use a clear box-model visual language.

Important content can use:

-   subtle borders
-   structured panels
-   surface backgrounds
-   restrained shadows
-   rounded corners where appropriate
-   clear grouping
-   generous spacing

Use:

``` text
#050505  background
#0D0D0D  surface
#141414  hover
#F2F2F2  primary text
#888888  muted text
```

Do not make every element a card.

Use borders strategically so important information feels organized and
premium.

The goal is:

**luxurious technical intelligence platform**

not:

**generic dashboard made entirely of cards**.

------------------------------------------------------------------------

# 10. Ethiopian Birr / Financial Intelligence Identity

Introduce subtle Ethiopian financial identity throughout appropriate
parts of the application.

Use Ethiopian Birr references/patterns in tasteful places.

Possible uses:

-   financial dashboard decoration
-   transaction visualization
-   currency indicators
-   subtle background motifs
-   financial-intelligence illustrations
-   transaction cards
-   money-flow visualizations

Do NOT turn the interface into a national-flag-themed design.

Keep it sophisticated.

Use money/financial animations where they actually communicate
intelligence, such as:

-   flowing transaction paths
-   subtle currency movement
-   money-flow visualization
-   network transaction pulses
-   anomaly highlights

Animations must remain smooth and purposeful.

------------------------------------------------------------------------

# 11. Smooth Scrolling and Motion

Improve the application's motion system.

Use smooth:

-   page transitions
-   section reveals
-   hover states
-   button interactions
-   navigation transitions
-   graph movement
-   card interactions
-   dropdown animations

Avoid excessive animation.

The application should feel polished and alive without becoming
distracting.

Respect reduced-motion accessibility where appropriate.

------------------------------------------------------------------------

# 12. RAG UI

The RAG section currently has poor/failing presentation.

Redesign the RAG interface so it matches the rest of the application.

Use:

-   the Prysm dark visual foundation
-   clear contrast
-   readable typography
-   structured panels
-   clear input/output areas
-   obvious actions
-   useful loading states
-   useful empty states
-   useful error states
-   shadcn components
-   Lucide icons

Fix the current RAG background and color treatment.

Do not use weak low-contrast colors.

Make the RAG interface look like a serious intelligence tool.

------------------------------------------------------------------------

# 13. RAG Failure --- Give the Developer an Exact Startup Guide

The current RAG functionality is failing.

Do not hide the problem behind a UI message.

First determine the actual dependency/startup chain.

Inspect the repository and identify exactly what RAG requires.

Then update the README with a clear startup sequence.

For example, if the actual repository requires:

1.  Start PostgreSQL/pgAdmin
2.  Create a specific database
3.  Configure environment variables
4.  Start the AI Engine with the actual command
5.  Start the backend with the actual command
6.  Start the frontend with the actual command

document those exact steps.

Use the real database name and real commands found in the repository.

Do NOT invent commands.

The README should explicitly answer:

> "I cloned Prysm. What do I start first, what database do I create,
> what commands do I run, and in what order?"

Include RAG-specific requirements and API keys.

If RAG depends on another service, explain that dependency.

If RAG is currently broken because of an actual code/configuration
issue, **fix the underlying issue**, not merely the documentation.

------------------------------------------------------------------------

# 14. Authentication --- Fix the Change Password Loop

There is a serious functional problem:

After login, a user can become stuck on the change-password/preferences
flow.

Even after changing the password, the application may continue showing
the change-password page and prevent normal entry into the application.

Investigate the real authentication state flow.

Check:

-   login response
-   user profile state
-   password-change endpoint
-   password-change response
-   authentication token/session
-   refresh behavior
-   user flags
-   first-login/change-password flags
-   frontend auth context/store
-   routing guards
-   post-password-change navigation
-   backend persistence
-   database state

Fix the actual root cause.

Expected behavior:

1.  User logs in.
2.  If password change is genuinely required, show the change-password
    screen.
3.  User successfully changes the password.
4.  Backend persists the change.
5.  Frontend refreshes the authenticated user state.
6.  The password-required flag is cleared.
7.  User is allowed into the normal application.
8.  Refreshing the browser does not send the user back into the loop.

Test this flow end-to-end.

Do not patch it with a hardcoded frontend redirect.

Fix the underlying state synchronization.

------------------------------------------------------------------------

# 15. Post-Login Information

After login, the application currently gives users too little useful
information.

Add clear, humanized information where appropriate.

Examples:

-   welcome state
-   what the user can do
-   account/profile information
-   current investigation/status information
-   useful empty-state explanations
-   next-step guidance
-   successful action confirmations

Do not fill the dashboard with meaningless statistics.

Information should help the user understand what is happening and what
they can do next.

------------------------------------------------------------------------

# 16. Notifications / Toast System

Admin pages currently provide poor feedback.

Implement a proper notification/toast system using an appropriate modern
library compatible with the existing stack.

Notifications should appear in the **bottom-right corner**, positioned
above the RAG/chat assistant area when necessary.

Use notifications for:

-   successful actions
-   failed actions
-   saved changes
-   deleted items
-   authentication events
-   API failures
-   administrative actions
-   password changes
-   configuration changes

Use clear human language.

Examples of the tone:

**Success**

"User account updated successfully."

**Error**

"Unable to update the account. Please try again."

Avoid developer jargon such as:

"Mutation failed."

"Request returned 500."

Technical details can remain in logs/debug information, not the primary
user-facing message.

------------------------------------------------------------------------

# 17. Admin UI Redesign

The admin UI currently feels rude, harsh, and visually inconsistent.

Redesign it to match the main Prysm system.

Make it:

-   clean
-   calm
-   structured
-   readable
-   professional
-   humanized
-   visually consistent
-   easy to scan

Improve:

-   tables
-   forms
-   filters
-   user management
-   account actions
-   permissions
-   confirmations
-   errors
-   status indicators
-   navigation

Use appropriate shadcn components and Lucide icons.

Do not make the admin interface look like a separate application.

------------------------------------------------------------------------

# 18. Error / Empty / Loading States

Audit the entire application for poor states.

Every important page should have appropriate:

### Loading

Explain that something is being loaded.

### Empty

Explain why the screen is empty and what the user can do.

### Error

Explain the problem in human language and provide a useful next action.

### Success

Clearly confirm completed actions.

Avoid blank screens.

Avoid unexplained spinners.

Avoid raw API errors being shown directly to users.

------------------------------------------------------------------------

# 19. Frontend ↔ Backend Verification

Perform a complete API alignment audit.

Compare:

-   frontend API calls
-   backend routes
-   request payloads
-   response models
-   authentication requirements
-   error responses

Look for:

-   nonexistent endpoints
-   outdated endpoint names
-   incorrect fields
-   stale mock responses
-   broken authentication headers
-   incorrect assumptions about response shapes

Fix genuine mismatches.

------------------------------------------------------------------------

# 20. Real Developer Work --- No Generative Pretending

This is critical.

Do not produce a superficial UI rewrite and claim success.

For every important change:

1.  Inspect the existing implementation.
2.  Identify the actual root cause.
3.  Make the smallest appropriate implementation change.
4.  Run the relevant code.
5.  Test the functionality.
6.  Inspect the result.
7.  Fix issues discovered during verification.
8.  Only then report it as complete.

Do not write:

> "This should work."

Actually test it.

Do not write:

> "The RAG system is fixed."

unless you actually started its dependencies and verified a real RAG
request.

Do not write:

> "Authentication works."

unless you actually tested the login → change password → application
flow.

------------------------------------------------------------------------

# 21. Browser Inspection

If browser inspection is available, use it.

Inspect the actual rendered Prysm application rather than relying
exclusively on source code.

Check:

-   hero section
-   GNN visualization
-   grid background
-   typography
-   buttons
-   navigation
-   hover states
-   animations
-   login
-   change password
-   dashboard
-   admin pages
-   RAG
-   responsive layout
-   console errors
-   failed network requests

After making UI changes, inspect the browser again.

The application must look good at large presentation/projector scale.

------------------------------------------------------------------------

# 22. Presentation-Scale Requirement

Design with the final presentation in mind.

The Prysm interface will be shown on a projector.

Therefore:

-   avoid tiny text
-   avoid tiny graphs
-   avoid low-contrast controls
-   avoid overly subtle important information
-   avoid dense compact layouts
-   use strong visual hierarchy
-   make major visualizations clearly visible
-   make important buttons obvious
-   maintain clean spacing

The UI should remain sophisticated while being easy to understand from a
distance.

------------------------------------------------------------------------

# 23. Final Repository Cleanup

After implementation:

-   remove dead code
-   remove obsolete demo UI
-   remove unused custom cursor code
-   remove the old third theme
-   remove temporary debugging
-   remove stale comments
-   remove unnecessary dependencies where safely possible
-   update `.gitignore`
-   ensure `.env` is not committed
-   ensure no secrets are exposed
-   remove temporary/generated artifacts that do not belong in the
    repository

Do not delete useful data, tests, or development tools without
understanding their purpose.

------------------------------------------------------------------------

# 24. Final Verification

Run the actual project.

Verify:

-   frontend starts
-   backend starts
-   AI Engine starts
-   database connection works
-   RAG works or its exact remaining blocker is identified
-   login works
-   change-password flow works
-   post-login routing works
-   dashboard works
-   admin pages work
-   notifications work
-   major API calls work
-   hero visualization renders correctly
-   themes are only Light/Dark
-   default cursor is restored
-   buttons have clear contrast
-   no obvious browser console errors remain
-   no obvious failed network requests remain
-   production configuration does not depend on one developer's local
    machine

Run the project's real tests/build/lint commands where available.

Do not create fake tests simply to report coverage.

------------------------------------------------------------------------

# 25. README / Project State Finalization

After all implementation and verification is complete:

Update the README so it reflects the actual final system.

Also update:

-   project memory
-   current-state files
-   TODO files
-   phase/task documentation

Remove completed tasks from pending lists.

Document genuine remaining limitations.

The README's setup section must give a new developer the exact order
for:

``` text
Repository
    ↓
Environment
    ↓
Database
    ↓
AI Engine
    ↓
Backend
    ↓
Frontend
    ↓
Browser
```

Use actual commands from the repository.

------------------------------------------------------------------------

# Final Report

When finished, provide a concise but factual report.

Include:

## UI / UX

What changed in:

-   typography
-   theme
-   hero/GNN
-   grid background
-   buttons
-   navigation
-   animations
-   RAG
-   admin
-   notifications

## Functionality

Explain what was actually fixed.

Especially:

-   authentication
-   change-password loop
-   RAG
-   API alignment

## Verification

List the actual commands and flows tested.

Include browser verification if performed.

## Production Readiness

Explain what was improved.

## Remaining Problems

List anything that genuinely remains broken or requires external
configuration.

## Git Status

Report the final working-tree state.

Do not say "everything is perfect" unless it was actually verified.

The priority is:

**real functionality first, visual polish second, documentation third.**
