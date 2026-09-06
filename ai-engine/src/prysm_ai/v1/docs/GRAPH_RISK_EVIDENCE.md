# Phase 3 Graph Intelligence, Fusion, and Evidence

## Canonical graph

`scripts/build_graph_intelligence.py` builds `prysm-financial-graph-v1` from
Phase 1 processed data. It contains 549,947 typed nodes: 100,000 Person, 10,000
Company, 150,000 Account, 20 Bank, 89,927 observed Device, and 200,000 Invoice.
Typed IDs remain globally distinct.

The 3,036,895 partitioned edges preserve ownership, bank membership, directed
transfers, device use, transaction/invoice linkage, invoice parties, and all ten
source relationship types. Timestamps, intervals, confidence, amounts,
currencies, and source IDs remain available. Transactions stay as provenance on
semantic edges rather than becoming an unnecessary seventh node domain.

## Temporal investigation

Predictive views include event edges at or before cutoff and inside lookback;
interval edges must be active at cutoff. Retrospective mode is explicit.
Traversal is deterministic and bounded by hops, nodes, edge types, confidence,
and time. Full-graph features/embeddings are retrospective caches. Historical
investigations recompute graph features and the GNN forward pass from only their
cutoff-valid bounded subgraph, preventing future-edge leakage.

## Validation and features

Verified integrity includes zero invalid endpoints, duplicate edge IDs,
self-loops, and reversed intervals; every account has one ownership edge. There
are 21 components, with 549,927 nodes in the largest, plus 20 retained isolated
persons. Banks dominate degree, an expected institutional structure showing why
centrality is context rather than risk.

Features cover degree/direction, relation diversity, direct and owner-propagated
transaction counts/volumes/direction ratios, counterparty concentration and
diversity, connected accounts/companies, shared device/address relationships,
capped two-hop paths, components, and type-relative structural anomaly.

## GNN representation and status

`relational-graphsage-structural-v1` is a two-layer, 16-dimensional,
relation-aware mean GraphSAGE encoder over robust type-normalized node features
and typed sparse connectivity. A deterministic self-supervised contrastive
projection learns from graph edges and type-matched negative endpoints. Its
held-out link-reconstruction evaluation measures structural representation only
and has no fraud/AML meaning.

No label or scenario metadata is used. Supervised GNN risk metrics remain
`NOT VALID FOR PREDICTIVE CLAIMS`. Weights, preprocessing, relations,
configuration, checksums, loss history, and structural evaluation are stored in
`artifacts/gnn_encoder.json`.

## Fusion, confidence, and evidence

Fusion combines available transaction, behavior, velocity, foreign-currency,
rule, anomaly, graph, and GNN components using centralized weights/scales.
Missing components are excluded and weights renormalized. The result is an
`uncalibrated_attention_assessment`, not a probability or accusation.

Signal strength and confidence are separate. `EvidenceItem` stores a stable ID,
subject, source/type, description, severity, confidence, supporting entity/
transaction/relationship/edge IDs, measurements, timestamps, and derivation.
Supporting identifiers are copied only from source-backed edges or findings.

`InvestigationResult` combines subject/window, bounded graph summary,
independent components, assessment, confidence, findings, ranked evidence,
limitations, and versions. The reproducible example is
`investigations/demo_investigation.json`.

## Evaluation boundary

Valid evaluation covers graph integrity, feature correctness, cutoff/traversal,
GNN determinism and link reconstruction, signal consistency, and evidence
provenance. `evaluation/phase3_evaluation.json` is authoritative. No supervised
graph classification metric exists because Phase 2.5 has zero eligible labels.
The current held-out structural link-reconstruction ROC-AUC is 0.521; this modest
result is reported without optimization or risk interpretation.
