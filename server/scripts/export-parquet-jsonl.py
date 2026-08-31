"""Stream canonical raw Parquet rows as database-ready JSON lines."""
from __future__ import annotations
import argparse, json
from datetime import date, datetime
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

IDS = {"persons":"person_id","accounts":"account_id","companies":"company_id","banks":"institution_id","devices":"device_id","invoices":"invoice_id","relationships":"relationship_id","transactions":"transaction_id","ground_truth":"ground_truth_id"}
EVENTS = {"persons":"created_at","accounts":"opened_at","companies":"registration_date","invoices":"issue_date","relationships":"start_time","transactions":"timestamp","ground_truth":"pattern_start"}
def clean(value):
    if isinstance(value, (list, tuple, np.ndarray)): return [clean(x) for x in value]
    if isinstance(value, dict): return {str(k):clean(v) for k,v in value.items()}
    if isinstance(value, (pd.Timestamp, date, datetime)): return value.isoformat()
    if isinstance(value, np.generic): return value.item()
    if value is None or (not isinstance(value,(list,dict)) and pd.isna(value)): return None
    return value
def entity_key(name, row):
    kinds={"persons":"Person","accounts":"Account","companies":"Company","banks":"Bank","devices":"Device","invoices":"Invoice"}
    return f"{kinds[name]}:{row[IDS[name]]}" if name in kinds else None
def main():
    parser=argparse.ArgumentParser();parser.add_argument("raw",type=Path);args=parser.parse_args()
    for path in sorted(args.raw.glob("*.parquet")):
        name=path.stem
        if name not in IDS: continue
        for batch in pq.ParquetFile(path).iter_batches(batch_size=10000):
            for row in batch.to_pylist():
                event=clean(row.get(EVENTS.get(name,"")))
                print(json.dumps({"dataset":name,"sourceId":str(row[IDS[name]]),"entityKey":entity_key(name,row),"eventAt":event,"payload":clean(row),"sourceRef":f"data/raw/{path.name}"},separators=(",",":")),flush=True)
if __name__=="__main__": main()
