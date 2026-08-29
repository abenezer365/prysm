<!-- You don't touch this, cuz the this is the AI's tracking system -->

# Project Memory

## Current state

- Phases 1, 2, 2.5, and 3 of the Prysm AI engine are implemented under `ai-engine/`; raw Parquet files in `data/raw/` remain immutable.
- Canonical identity is always `EntityType:entity_id`. Polymorphic references must be joined with both entity type and ID; raw IDs are not globally unique.
- Source temporal inconsistencies are preserved and surfaced with validity flags. Historical computation must use as-of logic and must never silently repair or drop conflicting source facts.
- Ground-truth metadata and related-entity lists are label provenance only. They are excluded from model features and operational graph construction.

## Label and model validity

- Step 4 integrates the scenario-augmented dataset through the existing engine at `ai-engine/runs/scenario-v1/`: 747,582 transactions, 7,000 aligned observations, 3,500 positive and 3,500 negative, with 46,094 affiliated post-cutoff evidence references. Source schemas and raw datasets remain unchanged.
- The aligned synthetic benchmark is valid and leakage-audited, but predictive performance is weak: supervised test ROC-AUC 0.470444, PR-AUC 0.467240, precision 0.487884, recall 0.575238, and F1 0.527972. Rules rank better (ROC-AUC 0.816098) but have recall 0.245714 at the existing threshold; anomaly ROC-AUC is 0.487010.
- Supervised GNN evaluation was not run: full-graph embeddings are retrospective, and a batched cutoff-safe training head is required to prevent future-edge leakage. Self-supervised link-reconstruction ROC-AUC is 0.515043 and has no predictive-risk meaning.

- Phase 2.5 established that the supplied ground truth is retrospective synthetic metadata, not a valid predictive entity-event dataset. All 16,634 referenced transactions are unaffiliated with their labeled entity, and the predictive-eligible population is zero.
- An isolated repair now exists at `generator/ground-truth-repair/`. It preserves the 5,000-row source schema and replaces random references only when existing completed, in-window transactions satisfy direct account affiliation and behavior-specific rules. The original generator and source Parquet files remain unchanged.
- The repaired artifact supports 647 scenarios with 2,356 valid transaction references and zero invalid affiliations, temporal violations, or fabricated IDs. Coverage is honest but not training-ready: 646 supported scenarios are normal and only one is anomalous; 4,353 remain explicitly unsupported, including 611 labels whose entity has no account.
- The legacy Phase 2 supervised model and its metrics are diagnostic only and invalid for predictive use. `ai-engine/artifacts/VALIDITY.json` is the consumption gate.
- No Prysm output is a calibrated fraud probability. The new supervised result is valid only for the aligned synthetic future-scenario benchmark and does not establish real-world performance.
- The current GNN is a self-supervised structural representation. Its held-out link-reconstruction ROC-AUC is 0.521; this modest structural metric has no fraud/AML meaning.

## Phase 3 architecture

- Canonical graph `prysm-financial-graph-v1` contains 549,947 typed nodes and 3,036,895 typed temporal edges. Transactions remain source provenance on edges rather than a separate node domain.
- Full-graph features and embeddings are retrospective caches only. Predictive/historical investigations recompute graph features and GNN representations from a cutoff-valid bounded subgraph to prevent future-edge leakage.
- Fusion produces an `uncalibrated_attention_assessment`. Signal strength, confidence, availability, coverage, evidence, and limitations remain distinct; unavailable components are excluded and weights renormalized, never zero-imputed.
- Evidence may reference only source-backed entities, transactions, relationships, graph edges, derived measurements, and versioned artifacts. `InvestigationResult` is the stable Phase 4 consumption boundary.

## Preserved limitations

- The graph retains 20 isolated Person nodes. High degree, centrality, volume, structural novelty, rules, and anomaly scores are not proof of risk.
- Current geography supports foreign-currency analysis, not defensible foreign-geography or cross-border inference.
- Company, bank, and device attributes are limited to canonical links and observed IDs where source masters were not materialized.
- Account/invoice lifecycle chronology includes known synthetic inconsistencies.
- Disk-backed neighborhood scans are reproducible but require indexing, predicate pushdown, or caching before interactive production use.
- Fusion weights/scales are initial engineering parameters and are not empirically calibrated.
- No Phase 4 API, frontend, LLM, RAG, persistence, or service boundary has been implemented.

## Phase 4 starting point

- Build a typed application/service boundary around `InvestigationEngine` and the stable `InvestigationResult` contract.
- Optimize bounded neighborhood retrieval before promising interactive latency, then add deterministic schema validation plus investigation persistence/versioning.
- Expose availability, confidence, provenance, and limitations; keep raw data and model internals behind the engine and do not present the assessment as a probability.
- Preserve the label-validity gate and synthetic-only scope. Improve scenario causal precursors and implement cutoff-safe batched GNN evaluation before making predictive graph claims.
