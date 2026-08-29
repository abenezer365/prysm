"""Export a bounded, cutoff-valid canonical slice for PostgreSQL ingestion."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
import pandas as pd
PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))
from prysm_ai.graph import GraphStore  # noqa: E402

def clean(value):
    if isinstance(value, dict): return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)): return [clean(v) for v in value]
    if isinstance(value, pd.Timestamp): return value.isoformat()
    if isinstance(value, np.generic): return value.item()
    if value is None or (not isinstance(value, (list, dict)) and pd.isna(value)): return None
    return value

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--artifact-root", type=Path, default=PROJECT / "runs" / "scenario-v1"); parser.add_argument("--subject", action="append", required=True); parser.add_argument("--cutoff", required=True); parser.add_argument("--output", type=Path, required=True); parser.add_argument("--max-hops", type=int, default=3); parser.add_argument("--max-nodes", type=int, default=250); args = parser.parse_args()
    root=args.artifact_root.resolve(); cutoff=pd.Timestamp(args.cutoff); store=GraphStore(root/"graph"); node_frames=[]; edge_frames=[]
    for subject in args.subject:
        nodes,edges=store.subgraph(subject,cutoff,args.max_hops,args.max_nodes,365,"predictive",None,0.3); node_frames.append(nodes.reset_index(drop=True)); edge_frames.append(edges.reset_index(drop=True))
    nodes=pd.concat(node_frames).drop_duplicates("node_key").sort_values("node_key"); edges=pd.concat(edge_frames).drop_duplicates("edge_id").sort_values("edge_id")
    embeddings=pd.read_parquet(root/"graph"/"node_embeddings.parquet"); embeddings=embeddings[embeddings.node_key.isin(nodes.node_key)].sort_values("node_key")
    embedding_map={str(r.node_key): clean(r.embedding) for r in embeddings.itertuples()}
    node_records=[]
    for index,row in enumerate(nodes.itertuples()): node_records.append({"nodeKey":str(row.node_key),"nodeType":str(row.node_type),"sourceId":str(row.source_id),"status":clean(row.status),"gnnIndex":index,"embedding":embedding_map.get(str(row.node_key))})
    edge_records=[]
    for row in edges.itertuples(): edge_records.append({"edgeId":str(row.edge_id),"sourceKey":str(row.source_key),"targetKey":str(row.target_key),"edgeType":str(row.edge_type),"eventTime":clean(row.event_time),"endTime":clean(row.end_time),"confidence":clean(row.confidence),"amountEtb":clean(row.amount_etb),"currency":clean(row.currency),"transactionId":clean(row.transaction_id),"relationshipId":clean(row.relationship_id),"sourceTable":clean(row.source_table)})
    manifest=json.loads((root/"graph"/"MANIFEST.json").read_text(encoding="utf-8")); payload={"version":"prysm-operational-slice-v1","artifactRoot":str(root),"graphVersion":manifest["graph_version"],"featureVersion":"prysm-graph-features-v1","embeddingVersion":"relational-graphsage-structural-v1","cutoff":cutoff.isoformat(),"subjects":args.subject,"nodes":node_records,"edges":edge_records}
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(clean(payload),indent=2,sort_keys=True),encoding="utf-8"); print(json.dumps({"output":str(args.output),"nodes":len(node_records),"edges":len(edge_records)}))
if __name__ == "__main__": main()
