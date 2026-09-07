# PHASE 6 — CONTENT + UI/UX + FINALIZATION

## ROLE

You are implementing the final phase of Prysm Intelligence.

Assume Phases 1–5 are complete.

Before changing anything, read the current technical state/memory files and inspect the actual frontend/backend contracts.

Also read the new **content guide MD** and the accompanying UI/UX requirements provided for this phase.

These are the source of truth for the final product content and interface.

---

# 1. PRIMARY OBJECTIVE

Finish Prysm as a coherent investigator-facing product.

Integrate:

```text
Phase 1 — Dataset
Phase 2 — Intelligence
Phase 3 — Evaluation
Phase 4 — RAG / Local LLM
Phase 5 — Backend / APIs
```

into the final frontend experience.

The goal is not to add new intelligence.

The goal is to make the existing system understandable, usable, consistent and ready for demonstration/client delivery.

---

# 2. FIRST INSPECT THE CURRENT FRONTEND

Trace the actual frontend flow:

```text
API
→ data/state
→ pages/components
→ investigator actions
→ graph
→ evidence
→ reasoning
```

Identify:

* existing working UI
* duplicate/obsolete components
* broken API assumptions
* placeholder/mock data
* outdated content
* inconsistent terminology
* unnecessary UI complexity

Do not redesign blindly.

Preserve useful existing functionality.

---

# 3. CONTENT GUIDE

Read the entire supplied content-guide MD.

Apply its requirements throughout the product.

Ensure terminology and explanations are consistent across:

* dashboards
* suspect/risk views
* graph investigation
* evidence
* anomaly information
* AI explanations
* RAG conversations
* navigation
* labels/help text

Do not invent new product meaning that conflicts with the content guide.

---

# 4. INVESTIGATOR WORKFLOW

The final UI should make the core investigation path obvious:

```text
Top Suspects
↓
Select suspect
↓
Risk overview
↓
Risk breakdown
↓
Evidence
↓
Transaction activity
↓
Graph / relationship investigation
↓
Family/network context where applicable
↓
AI explanation
↓
Investigation/case action
```

Use the APIs implemented in Phase 5.

Do not recreate backend or AI logic in the frontend.

---

# 5. GRAPH / GNN MAZE

Integrate the graph evidence returned by the backend.

The UI should distinguish:

```text
normal relationships
vs
AI-identified suspicious elements
```

The suspicious graph section should be visually obvious and consistent with the project's intended red/highlight treatment.

The graph should allow investigators to understand:

```text
who
→ connected to whom
→ through what
→ which transaction/relationship was suspicious
→ why Prysm flagged it
```

Do not invent graph findings locally.

---

# 6. RISK + EXPLAINABILITY UI

Do not show only:

```text
Risk: 92
```

Expose the useful structure already produced by the intelligence layer.

For example:

```text
overall risk
rule contribution
anomaly contribution
graph contribution
family/network contribution
evidence
```

Use the actual Phase 2 output rather than inventing categories that do not exist.

The investigator should be able to understand why the system considers a case important.

---

# 7. AI REASONING EXPERIENCE

Integrate the Phase 4 reasoning/RAG responses.

Clearly distinguish:

```text
Prysm detection/evidence
```

from:

```text
AI-generated explanation
```

The UI must not make an LLM explanation appear to be raw model ground truth.

Where appropriate, show the evidence behind the explanation.

---

# 8. TOP SUSPECTS

Make the ranked suspicious-entity functionality a primary investigator entry point.

The investigator should be able to:

```text
view ranked suspects
→ select one
→ inspect risk/evidence
→ investigate the graph
→ request/read explanation
```

Do not bury the ranking behind unnecessary navigation.

---

# 9. PERFORMANCE / MODEL RESULTS

Where the project requires model-performance presentation, provide clear views for the actual evaluation outputs from Phase 3.

Show meaningful information such as:

* precision
* recall
* F1
* confusion matrix
* relevant training/performance curves
* model comparison where implemented

Do not fabricate charts or metrics.

Use actual generated results.

---

# 10. UI/UX REFINEMENT

Apply the supplied UI/UX direction consistently.

Focus on:

* clear hierarchy
* readable information density
* consistent terminology
* useful visual emphasis
* predictable navigation
* understandable risk/evidence presentation
* responsive behavior
* removal of placeholder content

Do not add visual complexity merely to make the interface look advanced.

Every major screen should answer:

> What does the investigator need to know or do here?

---

# 11. REAL DATA ONLY

Replace remaining mock/placeholder data where the real API already exists.

The final demonstrated workflow should use actual:

```text
AI results
graph evidence
risk data
transactions
RAG responses
evaluation results
```

Do not fake a successful intelligence flow through frontend constants.

---

# 12. END-TO-END VALIDATION

Test the real user path:

```text
sign in
→ top suspects
→ open suspect
→ inspect evidence
→ inspect transactions
→ inspect graph
→ inspect suspicious graph elements
→ request/read AI explanation
→ investigation/case action
```

Verify that the frontend and backend contracts match.

Fix integration bugs found during this process.

Do not rewrite unrelated systems because of cosmetic issues.

---

# 13. FINAL CLEANUP

Remove:

* obsolete frontend components
* unused API calls
* mock data no longer needed
* duplicate implementations
* dead routes/components
* temporary debugging UI
* inconsistent old terminology

Do this carefully after checking dependencies.

The final repository should have one clear implementation path for each feature.

---

# 14. DEMONSTRATION READINESS

Prepare Prysm so the complete workflow can be demonstrated without manually manipulating internal code.

A demonstration should be able to show:

```text
Top suspect
↓
Why flagged
↓
Supporting evidence
↓
Suspicious graph
↓
Network/family context
↓
AI explanation
```

The system should visibly demonstrate the relationship between detection, evidence and explanation.

---

# 15. DO NOT REDESIGN PHASES 1–5

Do not redesign:

* dataset architecture
* intelligence models
* evaluation methodology
* RAG architecture
* PostgreSQL architecture
* backend API architecture

Only modify those systems when a concrete integration defect prevents the final product from working.

---

# 16. ACCEPTANCE CRITERIA

Phase 6 is complete when:

1. The final content guide has been fully incorporated.
2. UI/UX requirements have been integrated consistently.
3. Frontend uses the real Phase 5 APIs.
4. No critical workflow depends on mock intelligence data.
5. Top suspects are usable.
6. Risk/evidence are understandable.
7. Suspicious graph elements are visibly identifiable.
8. RAG/LLM explanations are integrated correctly.
9. Actual evaluation results can be presented.
10. The complete investigator workflow works end-to-end.
11. Obsolete frontend code and temporary artifacts are removed.
12. Prysm is ready for final demonstration/client delivery.

---

# 17. FINAL STATE UPDATE

Update the root technical state/memory file with the final repository state.

Record actual:

```text
frontend architecture
important pages/components
API integrations
graph integration
RAG integration
content-guide implementation
UI/UX changes
removed legacy components
run/build commands
deployment instructions
known limitations
final demonstration flow
```

Also record any remaining technical debt clearly.

Do not write a generic project summary.

The state file should allow another developer/AI agent to understand the final implementation without repeating the entire repository audit.

---

# FINAL RULE

Read the repository, Phase 1–5 state, API guide, content guide and UI/UX requirements first.

Use the existing implementation as the source of truth.

Integrate and finalize; do not unnecessarily redesign.

Keep detection, backend, reasoning and frontend responsibilities separate.

Use real data and real API results.

Complete the final workflow, verify it end-to-end, update the technical state, and STOP.
