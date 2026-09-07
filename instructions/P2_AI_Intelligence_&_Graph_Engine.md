# PHASE 2 — AI INTELLIGENCE ENGINE + GRAPH EVIDENCE

## ROLE

You are implementing Phase 2 of Prysm Intelligence.

Phase 1 has been completed successfully.

A dataset/data manifest was created during Phase 1. **Read that manifest first. It is the source of truth for the current dataset structure.**

Do not assume the schema from this prompt.

Your task is to rebuild/refine the Prysm AI Engine around the actual Phase 1 data and produce a clean, explainable intelligence pipeline.

---

# 1. PRIMARY OBJECTIVE

Turn the Phase 1 dataset into a working intelligence system capable of producing:

```text
raw data
   ↓
features
   ↓
rule intelligence
   +
anomaly intelligence
   +
graph/GNN intelligence
   +
family/network analysis
   ↓
signal fusion
   ↓
structured evidence
```

The system must be understandable enough that a developer can trace **why an entity was flagged** from the final result back to the underlying data.

Keep the implementation simple and measurable.

Do not add complexity just to make the architecture look advanced.

---

# 2. FIRST — INSPECT BEFORE MODIFYING

Read:

1. The Phase 1 data manifest.
2. The current AI Engine.
3. Existing feature-generation code.
4. Existing rule/anomaly code.
5. Existing graph/GNN code.
6. Existing relationship/graph construction logic.
7. Existing AI outputs consumed by other parts of Prysm.

Trace the current flow:

```text
dataset
→ loader
→ features
→ detection
→ graph
→ result
```

Determine what can be retained and what should be replaced.

Do not assume the current AI architecture is correct.

---

# 3. AI ENGINE BOUNDARY

The AI Engine should focus on **intelligence only**.

It should not become responsible for:

* authentication
* users
* PostgreSQL application management
* HTTP/API implementation
* frontend state
* RAG conversations
* UI logic
* unrelated application functionality

The engine receives data and produces intelligence.

Keep its interface clear enough that the backend can consume it later without understanding how the models work internally.

---

# 4. RULE ENGINE

Implement/refine a deterministic rule layer for the suspicious scenarios represented in the Phase 1 dataset.

Rules should be:

* explicit
* readable
* independently testable
* configurable where appropriate
* explainable

A rule result should preserve enough information to answer:

```text
What rule triggered?
Why did it trigger?
Which entity/transaction caused it?
What data supported it?
```

Do not bury rule logic inside model code.

Do not create dozens of artificial rules.

Implement only rules that correspond to meaningful Prysm investigation scenarios.

---

# 5. ANOMALY ENGINE

Build/refine a simple behavioral anomaly detection layer.

The model should identify behavior that differs significantly from an entity's expected/historical behavior.

Use the Phase 1 data to determine appropriate features.

Potential signals may include things such as:

```text
transaction amount
transaction frequency
velocity
historical deviation
counterparty behavior
geographic deviation
```

Do not blindly use every available column.

Feature selection must have a reason.

Start with the simplest suitable model and establish a clear baseline.

The anomaly engine should return:

```text
entity
anomaly score
important contributing features/signals
supporting evidence
```

Do not make the LLM responsible for calculating anomaly scores.

---

# 6. GRAPH INTELLIGENCE

Use the actual Phase 1 relationships to construct Prysm's financial/entity graph.

Determine from the dataset what the correct:

```text
nodes
edges
edge attributes
node attributes
```

should be.

Do not duplicate the dataset unnecessarily just to construct the graph.

The graph should allow Prysm to investigate relationships such as:

```text
person
account
organization
transaction
family/network relationships
```

where those relationships actually exist in the Phase 1 data.

---

# 7. GNN REQUIREMENT

Prysm must contain a genuine Graph Neural Network component where the graph problem justifies it.

Choose the model and task based on the actual data and labels.

Possible tasks include:

```text
node classification
link/relationship analysis
subgraph classification
```

Do not select a GNN architecture merely because it sounds impressive.

Keep the first implementation simple enough to:

* train
* evaluate
* explain at a high level
* experiment with
* demonstrate live

The exact architecture is your implementation decision after inspecting the data.

---

# 8. FAMILY / NETWORK ANALYSIS

Use the family/household and relationship information available from Phase 1 to identify meaningful connected behavior.

The objective is investigation, not automatic accusation.

Look for useful signals such as:

```text
shared financial activity
connected accounts
shared organizations
unusual money movement across connected entities
geographic relationships
coordinated behavior
```

Determine the appropriate implementation from the actual dataset.

Do not force a specific field or algorithm if the Phase 1 representation supports the requirement differently.

---

# 9. TAX-EVASION INVESTIGATION SIGNALS

Prysm should be able to generate **potential tax-evasion indicators**, particularly using the combination of:

```text
transaction
+
geographic context
+
business/organization context
+
financial behavior
+
relationships
```

Do not implement:

```text
transaction near business = tax evasion
```

That is not sufficient evidence.

Instead construct meaningful combinations of signals that can become an investigation lead.

The result must be phrased and represented as an indicator/lead, not as proof of criminal activity.

---

# 10. SIGNAL FUSION

Create a clear mechanism for combining intelligence outputs.

The final result should preserve the individual sources.

Conceptually:

```text
Rule signal
Anomaly signal
Graph/GNN signal
Family/network signal
        ↓
      Fusion
        ↓
Overall risk
```

Do not hide all model outputs behind one unexplained number.

The investigator must be able to see **where the risk came from**.

The exact scoring/fusion method is an implementation decision.

Choose something simple, deterministic and measurable first.

---

# 11. EVIDENCE BUILDER

This is one of the most important outputs of Phase 2.

For every meaningful finding, create structured evidence that can later be consumed by the backend and frontend.

The evidence should identify, where applicable:

```text
entity involved
transaction involved
relationship involved
source engine
reason
supporting features/data
score
related entities
```

The exact schema should follow the actual project architecture.

Do not hardcode a schema from this prompt if a cleaner one exists.

---

# 12. GRAPH EVIDENCE / GNN MAZE

The AI engine must identify **which graph elements are suspicious**.

Example flow:

```text
AI detects unusual transaction
        ↓
identifies transaction/account/entity
        ↓
constructs evidence
        ↓
marks related graph elements
        ↓
backend can send result to frontend
        ↓
GNN Maze highlights suspicious section
```

The frontend should eventually be able to distinguish:

```text
normal network
vs
AI-identified suspicious network/transaction/relationship
```

The suspicious portion should be visually highlighted, including the agreed red representation.

The AI engine must provide the evidence required for this.

The frontend must not independently decide what is suspicious.

---

# 13. TOP SUSPECTS

The engine must produce a ranked investigator view.

Conceptually:

```text
Top N
↓
entity
overall risk
risk level
evidence
score breakdown
```

N should be configurable.

The ranking should be generated from the intelligence system, not manually selected.

This allows investigators to immediately see the highest-priority entities.

---

# 14. EXPLAINABILITY

Every major intelligence result should be traceable.

For example:

```text
Risk = HIGH

Because:
- Rule X triggered
- Transaction velocity exceeded expected behavior
- Amount significantly differed from historical behavior
- Graph relationship connected the entity to suspicious activity
```

The AI engine should produce the underlying structured evidence.

**Do not implement the LLM/RAG explanation layer here.**

Phase 4 will handle the reasoning layer.

Phase 2 must produce the evidence that the reasoning layer will later explain.

---

# 15. MODEL SIMPLICITY

Prefer:

```text
simple baseline
→ measure
→ identify weakness
→ improve
```

over:

```text
complex architecture
→ assume it is better
```

Every model should have:

* clear input
* clear output
* clear purpose
* reproducible execution
* measurable behavior

Do not add models whose outputs overlap without a clear reason.

---

# 16. TESTING

Create focused tests for the intelligence components.

At minimum, verify that known Phase 1 scenarios produce the expected intelligence signals.

Test:

```text
normal scenario
suspicious scenario
edge case
invalid/missing input where relevant
```

Do not claim model performance in this phase without proper evaluation.

Phase 3 is responsible for formal performance evaluation.

---

# 17. DO NOT IMPLEMENT PHASE 3

Do not turn this phase into the full model evaluation project.

You may create the interfaces/hooks needed for evaluation.

But do not spend this phase building:

* final metric dashboards
* extensive hyperparameter experiments
* production benchmark reports
* large-scale datasets

Those belong to Phase 3.

---

# 18. DO NOT IMPLEMENT PHASE 4

Do not implement:

* authentication
* user management
* PostgreSQL redesign
* RAG
* local LLM deployment
* frontend redesign
* content guide
* final UI/UX

Only expose the clean intelligence/evidence interface required for later integration.

---

# 19. CLEAN ARCHITECTURE

Refactor the AI engine so its internal flow is obvious.

A reasonable conceptual structure is:

```text
AI Engine
│
├── feature processing
├── rules
├── anomaly
├── graph
├── GNN
├── family/network analysis
├── fusion
└── evidence
```

But **do not blindly create this exact folder structure**.

Use the existing repository and choose the cleanest implementation.

Delete/move obsolete AI code only after understanding its dependencies.

Avoid leaving two competing implementations of the same intelligence function.

---

# 20. ACCEPTANCE CRITERIA

Phase 2 is complete when:

1. The AI consumes the Phase 1 dataset successfully.
2. Rules produce explicit evidence.
3. Anomaly detection produces explainable anomaly signals.
4. Graph intelligence uses the actual entity relationships.
5. A genuine GNN component exists for a justified graph task.
6. Family/network analysis produces useful investigation signals.
7. Potential tax-evasion indicators can be represented where supported by the data.
8. Intelligence signals can be fused into an overall risk result.
9. Results contain traceable evidence.
10. Suspicious graph entities/transactions/relationships can be identified for the GNN Maze.
11. Top-risk entities can be ranked.
12. AI logic is separated from backend/application concerns.
13. Known benchmark scenarios can be processed reliably.
14. No unnecessary architecture or model complexity was introduced.

---

# 21. STATE UPDATE

When Phase 2 is complete, update the root technical memory/state file.

Record exact implementation details, not a generic summary.

Include:

```text
current phase
AI engine location
important files
models used
model inputs
model outputs
feature pipeline
rule definitions
graph construction
GNN task/model
family/network logic
fusion method
evidence structure
graph-output structure
top-suspect implementation
commands
tests
known limitations
remaining work
next phase entry point
```

Also record how Phase 2 consumes the Phase 1 data manifest.

The state must be detailed enough for another AI agent to continue Phase 3 directly from the repository without repeating the investigation.

---

# FINAL OPERATING RULE

Inspect the actual repository and Phase 1 manifest first.

This prompt defines the **mission and boundaries**, not an implementation you must blindly reproduce.

Use engineering judgment.

Choose the simplest correct solution supported by the actual data.

Do not touch unrelated systems.

Do not invent functionality.

Do not optimize for presentation over correctness.

Complete Phase 2, update the technical state, and STOP.
