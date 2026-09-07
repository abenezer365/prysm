# Prysm AI Engine — Technical Memory

## Authoritative implementation state

Phases 1, 2, 2.5, and 3 are implemented, and Step 4 scenario integration/retraining is complete under `runs/scenario-v1/`. No Phase 4 API, frontend, LLM/RAG layer, or persistence service exists yet. Raw inputs remain immutable, and generated engine assets remain under `ai-engine/`.

### Step 4 scenario benchmark

- `scripts/retrain_validate.py` and `src/prysm_ai/phase4.py` verify the scenario manifest and schemas, create an explicit isolated data boundary, reuse the existing Phase 1/2/2.5/3 pipelines, and generate reproducible comparison, leakage, scenario, graph, fusion, and evidence results.
- The predictive population contains 7,000 entity-disjoint observations (3,500 per class) backed by 747,582 transactions and 46,094 valid affiliated post-cutoff evidence references. Leakage, graph, evidence, and deterministic retraining checks pass; 19 tests pass.
- Test results: supervised ROC-AUC 0.470444, PR-AUC 0.467240, precision 0.487884, recall 0.575238, F1 0.527972; anomaly ROC-AUC 0.487010; rules ROC-AUC 0.816098 with recall 0.245714 at the unchanged threshold.
- The aligned evaluation is scientifically valid for this synthetic future-scenario benchmark only. It demonstrates weak pre-cutoff predictive separation and is not a calibrated fraud probability or evidence of real-world performance.
- Supervised GNN evaluation remains unrun because stored full-graph embeddings contain post-cutoff structure. The self-supervised link-reconstruction ROC-AUC is 0.515043; a batched cutoff-safe GNN head is the required next scientific implementation.

### Foundation and intelligence inputs

- `src/prysm_ai/data_readiness.py` and `scripts/build_foundation.py` load and audit the nine source Parquet datasets, normalize timestamps to UTC, retain duplicate lineage, and write canonical typed outputs plus checksummed manifests.
- `src/prysm_ai/features.py` creates the normalized 700,000-row transaction fact table and inclusive as-of entity snapshots. `rules.py`, `models.py`, `evaluation.py`, and `pipeline.py` produce separate feature, rule, anomaly, diagnostic model, and evaluation artifacts.
- Typed keys use `EntityType:entity_id`. Temporal/source inconsistencies and semantic nulls are preserved. Identifiers, hashes, label metadata, and `related_entity_ids` are not feature inputs.
- Phase 2 held-out results were weak and are retained only as diagnostics: supervised ROC-AUC 0.522, anomaly ROC-AUC 0.477, and rule ROC-AUC 0.485. No Phase 2 fused risk score exists.

### Phase 2.5 validity gate

- `src/prysm_ai/label_alignment.py` and `scripts/align_labels.py` preserve all 5,000 labels and materialize history, affiliation, timing, overlap, and predictive-eligibility decisions under `data/alignment/`.
- The 16,634 referenced transaction values exist, but none involve the labeled account or an account owned by the labeled Person/Company. Predictive-eligible rows: zero; `predictive_population.parquet` is intentionally empty.
- History classifications are 1,006 `cold_start_no_history`, 1,733 `insufficient_history`, and 2,261 `history_eligible`. History sufficiency does not repair missing event affiliation.
- `evaluation/alignment_evaluation.json`, `LABEL_ALIGNMENT_REPORT.md`, and `artifacts/VALIDITY.json` mark aligned supervised metrics as `not_estimable` and the legacy supervised model/predictions as invalid for predictive use.
- A separate, unconsumed upstream artifact now exists at `generator/ground-truth-repair/output/repaired_ground_truth.parquet`. Its isolated validation reports 647 supported labels (646 normal, one anomalous), 2,356 directly affiliated in-window transaction references, and zero invalid/fabricated references or temporal violations. It has not been copied into the AI engine, passed through Phase 2.5 alignment, or used for features, training, graph construction, scoring, or evaluation. The existing validity gate therefore remains unchanged.

## Phase 3 graph implementation

### Graph contract and artifacts

- Canonical graph version: `prysm-financial-graph-v1`.
- `src/prysm_ai/graph.py` constructs typed nodes and partitioned semantic temporal edges. It also provides the disk-backed `GraphStore`, cutoff/lookback filtering, and deterministic bounded-subgraph traversal.
- Full artifacts are `graph/nodes.parquet`, `graph/edges/*.parquet`, `graph/node_features.parquet`, `graph/node_embeddings.parquet`, `graph/connectivity.npz`, and `graph/MANIFEST.json`.
- Node total: 549,947 — Person 100,000; Company 10,000; Account 150,000; Bank 20; Device 89,927; Invoice 200,000.
- Edge total: 3,036,895 — owns 150,000; held_at 150,000; transfers 700,000; uses_device 631,629; transaction_linked_invoice 505,266; issued_invoice 200,000; received_invoice 200,000; relationship edges 500,000.
- Relationship counts: business_partner 60,179; counterpart 49,757; employer_employee 59,781; family 74,849; guarantor 39,670; joint_account 40,452; referral 25,308; shared_address 50,190; shared_device 50,241; supplier_customer 49,573.
- Transactions remain provenance-bearing transfer edges; they are not modeled as a seventh node type.

### Graph validation and features

- `src/prysm_ai/graph_features.py` performs streaming integrity checks and derives direct/owner-propagated network financial, counterparty, shared-infrastructure, capped two-hop, component, and type-relative structural anomaly features. It also writes sparse connectivity.
- Verified integrity: zero invalid endpoints, duplicate edge IDs, duplicate semantic edges, self-loops, or intervals ending before start. Confidence range is 0.3–1.0; ownership edges equal the 150,000 accounts.
- The graph has 21 connected components. The largest contains 549,927 nodes; 20 isolated Person nodes are intentionally retained and documented.
- Banks are the highest-degree nodes (approximately 7.3k–7.7k degree), demonstrating that centrality must be interpreted by entity type and is not itself risk evidence.

## Phase 3 GNN state

- `src/prysm_ai/gnn.py` implements `relational-graphsage-structural-v1`: a deterministic two-layer, 16-dimensional relation-aware mean GraphSAGE encoder with robust node-type preprocessing and semantic relation embeddings.
- Training is self-supervised link-contrastive structural projection only: 100,000 training edges, 20,000 validation edges, three epochs, losses `[0.7227650305175781, 0.7177166162109375, 0.7142804858398437]`.
- Held-out link-reconstruction ROC-AUC is 0.520692435. This is a modest structural metric, uses no labels, and has no fraud/AML interpretation.
- `artifacts/gnn_encoder.json` contains model weights, preprocessing, relation types, configuration, checksums, training/evaluation metadata, and validity. `artifacts/VALIDITY.json` records `graph_gnn.status = self_supervised_structural_signal`, `labels_used = false`, and supervised metrics as `not_estimable`.
- Full-graph features/embeddings are retrospective caches only. Historical or predictive investigations recompute local graph features and run GNN inference on the cutoff-valid bounded subgraph; using the full-graph caches for an earlier cutoff would leak future edges.

## Phase 3 fusion, evidence, and investigations

- `src/prysm_ai/fusion.py` combines available transaction, behavior, velocity, foreign-currency, rule, anomaly, graph, and GNN components using configurable weights/scales in `config/intelligence.json`.
- Supervised prediction and foreign-geographic components are explicitly unavailable. Missing components are excluded and weights renormalized; they are never treated as numeric zero.
- The result type is `uncalibrated_attention_assessment` with `is_fraud_probability = false`. Assessment strength and confidence are separate; confidence includes component coverage.
- `src/prysm_ai/evidence.py`, `src/prysm_ai/investigation.py`, and contracts in `src/prysm_ai/contracts.py` implement stable `EvidenceItem`, `SignalComponent`, and `InvestigationResult` structures. Evidence contains source/type, description, severity, confidence, supporting entity/transaction/relationship/edge IDs, measurements, timestamps, provenance, and derivation. IDs are never fabricated.
- `GraphStore` bounds investigations by hops, maximum nodes, cutoff/lookback, allowed types, and confidence. Predictive mode applies event and interval validity at cutoff; retrospective mode is explicit.
- `investigations/demo_investigation.json` is deterministic: `INV:5029b7cc8982ecb6`, subject `Person:P092017`, cutoff `2022-06-08T00:00:00+00:00`, predictive mode, 365-day lookback, 8 nodes, 7 edges, and 9 evidence items. It represents ten components, including explicitly unavailable supervised and geographic signals.

## Verification

- `evaluation/graph_validation.json` records graph integrity and component results.
- `evaluation/phase3_evaluation.json` covers valid integrity, feature, cutoff, bounded-traversal, deterministic/self-supervised structural GNN, evidence-provenance, and signal-consistency checks.
- The verified Phase 3 test suite result is 19 passed.
- Label-based GNN/risk quality, calibration, sensitivity, specificity, and fraud probability are not estimable and must not be inferred from the structural evaluation.

## Known limitations

- No valid predictive risk labels exist; supervised GNN training, calibration, and predictive claims are blocked.
- Link-reconstruction ROC-AUC 0.520692435 indicates limited current structural representation quality.
- Twenty isolated Person nodes remain, and company/bank/device attributes are limited where source master records were not materialized.
- Available geography supports foreign-currency behavior only, not foreign-geography or cross-border claims.
- Known synthetic account/invoice lifecycle chronology conflicts remain evidence flags, not silently corrected facts.
- `GraphStore` scans disk-backed edge partitions for incident lookup. This is deterministic and reproducible but needs indexing, predicate pushdown, and/or caching before interactive production latency is promised.
- Fusion weights and scaling values are initial engineering parameters, not validated or calibrated coefficients.
- Structural novelty, graph centrality, rules, and anomaly scores are attention signals rather than accusations or probabilities.

## Phase 4 starting point

1. Treat `InvestigationResult` as the stable application-facing contract and place a typed service/API boundary around `InvestigationEngine`.
2. Optimize and benchmark bounded-neighborhood retrieval before exposing interactive endpoints.
3. Add deterministic request/response schema validation and investigation persistence/versioning.
4. Return explicit component availability, assessment strength, confidence/coverage, evidence provenance, and limitations while keeping raw source access and model internals behind the engine.
5. Preserve `artifacts/VALIDITY.json` as the supervised-use gate. Supervised calibration or GNN evaluation may begin only after upstream label repair yields affiliated events and a non-empty two-class population with temporal and entity-disjoint partitions.
6. Any representation improvement may benchmark self-supervised structure only until that gate is satisfied; relation-specific trainable message layers are a proposed, not implemented, direction.
