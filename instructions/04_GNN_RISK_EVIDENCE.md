# PRYSM AI — STEP 3

# GRAPH INTELLIGENCE → GNN → SIGNAL FUSION → EVIDENCE

## 1. MISSION

You are continuing development of the **Prysm AI Engine**.

This is the third major AI-engineering phase and one of the most important architectural stages of the project.

Prysm AI is an Ethiopia-first financial intelligence platform designed to analyze interconnected financial entities and identify patterns associated with:

* financial fraud
* AML / money-laundering behavior
* unusual financial activity
* behavioral anomalies
* transaction velocity
* foreign-income anomalies
* suspicious relationships
* network-level financial behavior

The system is intended to help investigators understand **why an entity deserves attention**, not merely produce an unexplained numerical score.

Phase 1 established the canonical and validated data foundation.

Phase 2 established the first intelligence layer:

* transaction intelligence
* behavioral features
* velocity features
* foreign-currency intelligence
* configurable rules
* anomaly detection
* supervised baseline infrastructure
* standardized intelligence signals

Phase 2.5 then discovered a critical limitation:

> The current synthetic ground-truth records do not have valid entity-affiliated predictive transaction provenance.

Therefore the existing supervised labels are **not valid for predictive model evaluation**.

This must NOT be hidden or bypassed.

Your mission is now to build the **graph intelligence and evidence architecture** while respecting that limitation.

The goal is to transform Prysm from:

```text
entity behavior analysis
```

into:

```text
entity + financial network + temporal relationships
```

and ultimately produce a structured investigation result that can explain:

> **What is happening, where it is happening, how the entity is connected, which intelligence signals support concern, and what evidence produced those signals.**

---

# 2. READ THE EXISTING PROJECT BEFORE WORKING

Before implementing anything, read and understand:

* `memory.md`
* `todo.md`
* `ai-engine.md`
* `DATA_CONTRACTS.md`
* `FEATURE_POLICY.md`
* `DATA_READINESS_REPORT.md`
* `PHASE_2_REPORT.md`
* `INTELLIGENCE_CONTRACTS.md`
* `LABEL_ALIGNMENT_REPORT.md`
* `evaluation/evaluation.json`
* `evaluation/alignment_evaluation.json`
* `artifacts/VALIDITY.json`
* the existing Phase 1 and Phase 2 implementation
* existing configuration files
* existing tests

Do not redo completed work.

Treat the existing project documentation and verified artifacts as the current source of truth.

If implementation and documentation disagree, inspect the implementation and correct the documentation or implementation as appropriate.

---

# 3. STRICT SCOPE

Work only inside:

* `ai-engine/`
* its existing source
* processed-data
* graph
* model
* artifact
* configuration
* evaluation
* test
* documentation areas

Do NOT inspect or modify:

* `generator/`
* `resource/`
* `resources/`
* frontend
* mobile
* logos
* PDFs
* unrelated project code

Do not investigate the synthetic-data generator.

The graph must be built from the canonical/processed data already available to the AI engine.

---

# 4. CORE ARCHITECTURAL PRINCIPLE

Preserve these Prysm boundaries:

```text
Database / Processed Data
        =
Source of Truth

AI Engine
        =
Intelligence

Graph
        =
Relationship Intelligence

GNN
        =
Learned Network Representation

Rules / ML / Anomaly Models
        =
Specialist Intelligence

Fusion
        =
Combination of Independent Signals

Evidence
        =
Traceable Reasons Behind Signals

LLM / RAG
        =
Future Explanation / Conversation Layer
```

Do not turn the GNN into the entire AI system.

Do not allow the GNN to replace rules, behavioral intelligence, transaction intelligence, or evidence.

Prysm should ultimately use **multiple complementary intelligence perspectives**.

---

# 5. GRAPH MODEL

Construct a canonical financial graph from the Phase 1 processed data.

## Node domains

Support the entity types already established by the data contracts:

```text
Person
Company
Account
Bank
Device
Invoice
```

Do not invent additional node types unless the actual data and architecture require one.

Every node must have:

* stable typed identity
* node type
* available attributes/features
* provenance where appropriate

Avoid globally treating IDs from different domains as interchangeable.

For example:

```text
Person:P123
Account:A123
Company:C123
```

must remain distinct entities.

---

# 6. EDGE MODEL

Represent the important financial and relational connections.

At minimum support:

```text
Person ──owns──────────> Account
Company ──owns─────────> Account

Account ──transfers───> Account

Account ──uses────────> Device

Person ──related_to───> Person
Person ──works_for────> Company
Company ──supplier────> Company
Company ──customer────> Company

Person/Company ──party_to──> Invoice
Invoice ──linked_to──> Transaction

Account ──held_at────> Bank
```

Use the actual relationship types from the canonical data.

Preserve:

* timestamps
* relationship type
* confidence
* amount where applicable
* currency where applicable
* transaction/channel information where applicable

Do not flatten all relationships into one generic edge if doing so would destroy important semantics.

---

# 7. TEMPORAL GRAPH REQUIREMENTS

Prysm is a financial intelligence system, not a static social graph.

The graph must preserve time.

A relationship can change.

A transaction happens at a specific moment.

A person may use a device during one period and stop using it later.

A relationship can begin and end.

Therefore support temporal information such as:

* transaction timestamp
* relationship start time
* relationship end time
* invoice dates
* account lifecycle dates
* device observation dates

Open-ended relationships must not be incorrectly treated as having a known end date.

When constructing historical or investigation-time graph views, respect the relevant temporal cutoff.

Never allow future edges to appear in a historical graph representation.

---

# 8. GRAPH VALIDATION

Before training or inference, validate the graph.

Check:

* node counts by type
* edge counts by type
* orphan nodes
* invalid endpoints
* duplicate edges
* self-loops
* disconnected components
* unusually dense entities
* edge-type distributions
* temporal validity
* relationship confidence ranges
* transaction direction
* ownership consistency

Do not automatically delete unusual graph structures.

A highly connected entity may be:

* a legitimate company
* a bank
* a payment hub
* or genuinely suspicious

Graph irregularity itself can be intelligence.

Document unusual structures rather than silently removing them.

---

# 9. GRAPH FEATURES

Create meaningful graph-derived features before relying on a GNN.

Examples include:

### Local structure

* degree
* in-degree
* out-degree
* unique counterparty count
* relationship-type diversity
* connected account count
* connected company count

### Financial network behavior

* network transaction volume
* network transaction count
* incoming/outgoing network ratio
* counterparty concentration
* number of destinations
* number of sources

### Shared infrastructure

* shared-device count
* shared-address count
* shared-identifier count

Only use identifiers that Phase 1 established as valid for the relevant purpose.

### Multi-hop structure

Where computationally practical, derive limited-hop features such as:

* 2-hop entity count
* 3-hop entity count
* reachable account count
* reachable company count

Do not create an enormous feature explosion.

Every graph feature must have a clear reason to exist.

---

# 10. COMMUNITY / NETWORK ANALYSIS

Implement lightweight graph analytics where useful.

Consider:

* connected components
* community structure
* unusually dense local neighborhoods
* high-centrality entities
* concentration hubs
* bridge-like entities
* repeated transaction pathways

Use these as **signals**, not accusations.

For example:

A person with many connections is not automatically suspicious.

A company with many transactions is not automatically suspicious.

The system must consider the type, magnitude, timing, and context of those connections.

---

# 11. SUBGRAPH INVESTIGATION

Implement the ability to construct an investigation-focused subgraph around an entity.

Given:

```text
Person P123
```

the engine should be able to retrieve a bounded neighborhood such as:

```text
P123
 ↓
Account(s)
 ↓
Counterparties
 ↓
Companies
 ↓
Devices
 ↓
Invoices
 ↓
Related entities
```

Support configurable parameters such as:

* maximum hop depth
* maximum nodes
* time window
* edge types
* minimum confidence

The subgraph must remain deterministic and bounded.

Do not allow arbitrary graph traversal to consume unbounded resources.

---

# 12. GNN DATA REPRESENTATION

Prepare a graph representation suitable for a future/actual GNN implementation.

The representation should clearly distinguish:

```text
Node features
Edge features
Graph connectivity
Node types
Edge types
Temporal information
Labels where legitimately available
```

Use an appropriate graph-learning library already compatible with the project, or introduce one only if justified.

Keep the implementation modular so that the GNN architecture can be changed later without rebuilding the entire graph pipeline.

---

# 13. GNN ARCHITECTURE

Implement a defensible initial GNN architecture rather than an unnecessarily complicated research model.

The architecture should support heterogeneous financial entities and relationships where justified by the data.

A suitable initial direction may include:

* heterogeneous message passing
* relation-aware graph convolution
* GraphSAGE-style aggregation
* relational GCN
* another appropriately justified architecture

Choose based on the actual graph structure.

Do not choose an architecture merely because it sounds advanced.

The initial model should prioritize:

* correctness
* reproducibility
* modularity
* inspectability
* reasonable computational cost

---

# 14. CRITICAL LABEL CONSTRAINT

The current ground-truth labels are NOT valid for predictive supervised graph evaluation.

Phase 2.5 proved that the current ground-truth evidence transactions are not correctly affiliated with their labeled entities/accounts.

Therefore:

## DO NOT

* invent graph labels
* reassign labels without verified provenance
* train a supervised GNN and present its metrics as valid
* manipulate the graph until the labels appear predictive
* use scenario metadata as hidden node/edge features
* claim supervised GNN accuracy from invalid labels

The invalidity must be explicitly represented in the implementation.

If useful, build the GNN training infrastructure so that it can accept valid labels later.

But do not manufacture a training target.

---

# 15. UNSUPERVISED GRAPH INTELLIGENCE

Because supervised labels are currently unavailable for valid predictive evaluation, prioritize graph intelligence that does not depend on those labels.

Implement useful unsupervised or representation-based capabilities where justified.

Potential outputs include:

* node embedding
* graph embedding
* neighborhood similarity
* structural anomaly score
* unusual neighborhood structure
* unusual connectivity
* unusual transaction pathways

Do not claim that these scores represent confirmed fraud or AML.

They are intelligence signals.

---

# 16. INTEGRATE PHASE 2 INTELLIGENCE

Consume the standardized Phase 2 outputs.

The graph intelligence layer should be able to receive or associate:

```text
transaction signals
behavior signals
velocity signals
foreign-income signals
rule findings
anomaly predictions
baseline model predictions
```

with the appropriate entity.

Do not duplicate Phase 2 logic.

Do not rebuild existing features unless graph-specific representation requires it.

The graph layer should add a **new perspective**.

---

# 17. SIGNAL FUSION

Build the first version of the Prysm signal-fusion architecture.

The purpose is to combine independent intelligence sources into a structured assessment.

Conceptually:

```text
Transaction Intelligence
        +
Behavioral Intelligence
        +
Velocity Intelligence
        +
Foreign-Income Intelligence
        +
Rule Signals
        +
Anomaly Signals
        +
Graph Intelligence
        +
GNN Signals
        ↓
Signal Fusion
        ↓
Risk Components
```

Do NOT present the output as ground-truth fraud probability unless it has been properly calibrated and validated.

The first fusion system should instead produce structured components such as:

```text
behavior_signal
transaction_signal
velocity_signal
foreign_income_signal
rule_signal
graph_signal
anomaly_signal
```

and an overall **configurable intelligence/risk assessment** only if defensible.

---

# 18. FUSION MUST BE CONFIGURABLE

Do not hard-code fusion weights throughout the source.

Support configuration such as:

```text
behavior weight
transaction weight
velocity weight
foreign-income weight
rule weight
anomaly weight
graph weight
GNN weight
```

Keep the configuration centralized and easy to change.

Do not assume the initial weights are scientifically optimal.

Document that they are initial engineering parameters unless validated.

---

# 19. CONFIDENCE

Separate:

```text
risk/intelligence signal
```

from:

```text
confidence in the signal
```

For example:

```text
Foreign-income signal:
HIGH

Confidence:
LOW

Reason:
limited geographic coverage
```

This distinction is extremely important for investigator-facing intelligence.

Confidence can consider:

* data completeness
* historical coverage
* identifier availability
* model availability
* rule evidence
* graph coverage
* signal agreement
* provenance quality

Do not use confidence merely as another name for risk.

---

# 20. EVIDENCE ENGINE

This is a major deliverable of this phase.

Prysm must not eventually return:

```text
Risk = 87
```

without being able to answer:

> Why?

Build a structured evidence layer.

Each important signal should be traceable to underlying facts.

An evidence item should be able to contain information such as:

```text
evidence_id
entity_id
signal_source
signal_type
description
severity
confidence
supporting_entity_ids
supporting_transaction_ids
supporting_relationship_ids
measurements
timestamps
provenance
```

The exact schema should be designed consistently with existing intelligence contracts.

---

# 21. EVIDENCE EXAMPLE

For an imaginary entity:

```text
Person P123
```

the evidence system might produce:

```text
Finding: Rapid Outflow

Evidence:
- 92,000 ETB received
- 87,500 ETB transferred out
- 91% moved within 18 hours
- 4 destination accounts
- historical outflow ratio: 31%
- current outflow ratio: 95%

Supporting transactions:
T1001
T1002
T1003
```

Another finding could be:

```text
Finding: Network Concentration

Evidence:
- 1 person
- 3 accounts
- 2 companies
- 7 counterparties
- shared device with 2 connected entities
- unusually dense local transaction structure
```

The evidence engine must preserve the connection between:

```text
signal
→ measurement
→ source record
```

---

# 22. EVIDENCE PROVENANCE

Evidence must never be invented by the AI engine.

Every important finding should be traceable to:

* source entity
* source transaction
* source relationship
* derived feature
* model/rule producing the signal

Where a value is derived, identify the derivation conceptually.

For example:

```text
rapid_outflow_ratio
=
outflow within window / inflow within window
```

Do not require the future LLM to reconstruct evidence from raw tables.

The evidence engine should already provide structured facts.

---

# 23. INVESTIGATION RESULT

Create a standardized investigation result capable of representing:

```text
InvestigationResult
│
├── subject
├── investigation_window
├── graph_summary
├── risk/intelligence components
├── confidence
├── rule findings
├── anomaly findings
├── behavioral findings
├── transaction findings
├── foreign-income findings
├── graph findings
├── GNN findings
├── evidence
└── limitations
```

The result must explicitly communicate when a signal is unavailable.

For example:

```text
foreign_geographic_risk:
UNAVAILABLE

reason:
current dataset does not provide sufficient international geography
```

Do not silently convert missing intelligence into zero risk.

---

# 24. GRAPH + EVIDENCE EXAMPLE

The architecture should eventually be capable of representing something like:

```text
                    Company X
                       │
                   supplier
                       │
                       ▼
Person A ── owns ── Account A
    │                    │
    │                    │ sends
    │                    ▼
    │                Account B
    │                    │
shared device            │ sends
    │                    ▼
    └─────────────── Person B
```

Suppose Account A receives:

```text
100,000 ETB
```

and sends:

```text
95,000 ETB
```

within 24 hours to several connected accounts.

Phase 2 may already detect:

```text
rapid outflow
unusual velocity
behavioral deviation
```

Phase 3 should additionally understand:

```text
network structure
counterparty relationships
shared infrastructure
multi-hop connections
```

The final investigation representation should therefore be able to say conceptually:

```text
Behavior Signal:
High

Graph Signal:
Elevated

Rule:
Rapid Outflow Triggered

Evidence:
95% of recent inflow moved within 24h.

Network Evidence:
Funds moved across 3 connected accounts.

Confidence:
Medium

Limitation:
Current supervised labels are unavailable for valid predictive validation.
```

This is the type of structured intelligence future investigators and the frontend should consume.

---

# 25. DO NOT CONFUSE NETWORK CENTRALITY WITH RISK

This is an important modeling rule.

High:

* degree
* transaction volume
* centrality
* number of counterparties

does not automatically mean high risk.

Banks, employers, payment platforms, and large legitimate businesses can naturally have high connectivity.

Graph features must be interpreted with:

* entity type
* transaction behavior
* temporal context
* relationship type
* behavioral baseline
* other intelligence signals

---

# 26. TEMPORAL INVESTIGATION

Support investigation-time graph construction.

Given:

```text entity + cutoff
```

the graph should only contain information legitimately available by that cutoff when operating in historical/predictive mode.

This must prevent:

```text future transaction
        ↓
historical graph
        ↓
false intelligence
```

For retrospective investigation mode, future information may be included only when explicitly requested and clearly marked.

Keep predictive and retrospective modes conceptually separate.

---

# 27. MODEL ARTIFACTS

Any trained or generated model artifact must be reproducible.

Record:

* model type
* feature contract/version
* graph representation/version
* configuration
* training parameters
* creation time
* data version/checksum where practical
* evaluation status
* validity status

Do not mark an artifact as production-valid if its evaluation target is invalid.

---

# 28. PERFORMANCE AND EFFICIENCY

The graph may contain hundreds of thousands of relationships and must remain computationally practical.

Prefer:

* batch processing
* sparse representations
* bounded neighborhood extraction
* cached reusable graph structures
* vectorized calculations
* deterministic preprocessing
* small fixtures for tests

Avoid repeatedly rebuilding the entire graph when only a subgraph is required.

Do not optimize prematurely, but do not implement obviously quadratic operations over hundreds of thousands of records without justification.

---

# 29. CONFIGURATION

Centralize parameters for:

### Graph

* hop depth
* neighborhood size
* time windows
* edge filtering
* confidence thresholds

### GNN

* hidden dimensions
* layers
* dropout
* learning rate
* epochs
* batch size
* embedding size

### Fusion

* component weights
* thresholds
* confidence requirements

### Evidence

* maximum evidence items
* ranking/priority
* minimum signal strength

Keep configuration simple.

Do not create a complicated configuration framework.

---

# 30. EVALUATION

Because supervised labels are currently invalid, evaluation must distinguish between:

### Valid evaluations

* graph construction integrity
* graph feature correctness
* deterministic graph generation
* subgraph correctness
* temporal cutoff correctness
* rule integration
* signal consistency
* evidence provenance
* model reproducibility
* unsupervised structural analysis

### Currently invalid evaluations

Do not claim valid supervised:

* GNN ROC-AUC
* GNN precision
* GNN recall
* supervised graph classification performance

unless valid upstream labels become available.

If an experiment can technically run but its target is invalid, label the result:

```text
NOT VALID FOR PREDICTIVE CLAIMS
```

---

# 31. DEMONSTRATION / INVESTIGATION QUALITY

The resulting architecture should be suitable for demonstrating Prysm's intelligence to technical reviewers.

The system should be able to take a valid entity identifier and produce a structured representation showing:

```text
Subject
 ↓
Financial context
 ↓
Connected entities
 ↓
Graph structure
 ↓
Behavioral signals
 ↓
Transaction signals
 ↓
Rules
 ↓
Anomaly signals
 ↓
Graph intelligence
 ↓
Evidence
 ↓
Confidence
 ↓
Limitations
```

The result must be understandable to another engineer without reading internal implementation details.

---

# 32. TESTING

Create focused automated tests for:

### Graph

* node creation
* typed identities
* edge creation
* edge typing
* temporal filtering
* invalid endpoint handling
* deterministic construction

### Graph features

* degree
* counterparty counts
* network aggregates
* multi-hop calculations
* shared infrastructure features

### Subgraphs

* hop limits
* node limits
* temporal limits
* deterministic traversal

### GNN

* graph tensor construction
* node/edge feature dimensions
* forward pass
* serialization
* deterministic inference where applicable

### Fusion

* component combination
* configuration changes
* missing signal handling
* confidence separation

### Evidence

* provenance
* supporting identifiers
* timestamps
* deterministic evidence generation
* no fabricated source references

Run the complete relevant test suite.

---

# 33. DOCUMENTATION

Create/update only the documentation that is genuinely useful.

At minimum document:

* graph schema
* graph construction approach
* graph feature groups
* GNN architecture
* GNN limitations
* signal-fusion architecture
* evidence schema
* investigation result schema
* configuration
* evaluation status
* known limitations

Keep the documentation concise enough to remain maintainable.

---

# 34. PROJECT MEMORY

At completion, update:

* `ai-engine.md`
* `memory.md`
* `todo.md`

Record:

### `ai-engine.md`

Technical state of the AI engine:

* graph implementation
* GNN implementation/status
* fusion implementation
* evidence implementation
* important files
* contracts
* configuration
* evaluation state

### `memory.md`

Important long-term project decisions:

* architectural principles
* major discoveries
* important limitations
* decisions future agents must preserve

### `todo.md`

Only meaningful remaining work:

* unresolved technical tasks
* future model improvements
* label-repair dependency
* next phase

Do not turn these files into verbose activity logs.

---

# 35. ENGINEERING FREEDOM

You are expected to think independently.

If the actual graph structure suggests a better implementation than the examples above, use the better approach.

If you discover:

* unexpected graph topology
* useful network structure
* computational bottlenecks
* problematic edge semantics
* feature leakage
* unsuitable GNN architecture
* evidence-traceability problems

investigate and resolve them where they belong to this phase.

Do not blindly follow examples if the data proves they are inappropriate.

However:

> **Do not expand scope simply because additional technologies are available.**

Prefer a smaller, reliable architecture over an impressive but fragile one.

---

# 36. IMPORTANT: DO NOT FAKE THE AI

This project will be evaluated technically.

Do not optimize the system for impressive-looking numbers.

Do not:

* fabricate labels
* manufacture suspiciousness
* claim fraud from anomaly alone
* claim AML from connectivity alone
* report invalid supervised metrics as scientific results
* hide limitations
* use future information
* create fake evidence
* hard-code outputs for demonstrations

A scientifically honest limitation is better than a fabricated success.

---

# 37. STOPPING BOUNDARY

Do NOT implement:

* RAG
* LLM explanation
* chatbot
* TTS
* frontend
* mobile
* production backend API
* Neo4j migration
* real-time streaming infrastructure
* advanced MLOps
* unrelated infrastructure

Those belong to later stages.

The output of this phase is the **AI intelligence core**, not the user-facing application.

---

# 38. DEFINITION OF DONE

Phase 3 is complete only when:

1. The canonical financial graph is implemented.
2. Nodes and edges have correct typed identities.
3. Important relationship semantics are preserved.
4. Temporal information is preserved.
5. Historical graph construction respects cutoffs.
6. Graph validation is implemented.
7. Useful graph features exist.
8. Bounded investigation subgraphs work.
9. GNN-compatible representations exist.
10. A defensible initial GNN architecture is implemented where technically justified.
11. Invalid supervised labels are not used to make false predictive claims.
12. Unsupervised/structural graph intelligence works where appropriate.
13. Phase 2 signals can be consumed.
14. Signal fusion is implemented in a modular/configurable way.
15. Confidence is separated from risk/intelligence strength.
16. Evidence is structured and traceable to source facts.
17. Investigation results have a stable contract.
18. Model/graph artifacts are reproducible.
19. Tests pass.
20. Documentation is updated.
21. `memory.md`, `todo.md`, and `ai-engine.md` are updated.
22. Remaining limitations are explicit.
23. Phase 4 has a clear starting point.

---

# 39. FINAL ARCHITECTURAL TARGET

At the end of this phase, Prysm should conceptually have:

```text
                    PRYSM AI ENGINE
                          │
                          ▼
                Investigation Context
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
      Behavioral/ML             Financial Graph
      Intelligence                    │
             │                        ▼
             │                  Graph Features
             │                        │
             │                        ▼
             │                       GNN
             │                        │
             └────────────┬───────────┘
                          ▼
                  Intelligence Signals
                          │
                          ▼
                     Signal Fusion
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
         Risk Components         Confidence
              │                       │
              └───────────┬───────────┘
                          ▼
                       Evidence
                          │
                          ▼
                 Investigation Result
```

The most important output is not the GNN itself.

The most important output is:

> **A structured, traceable, temporal financial-intelligence system capable of combining individual behavior with network behavior and showing the evidence behind its conclusions.**

The future RAG/LLM layer should eventually consume this structured result and explain it to investigators.

When all requirements are satisfied, stop.

Do not continue into Phase 4.
