from pathlib import Path

import duckdb

from bicing_predict.ingest import data_collect

conn = duckdb.connect(database=":memory:")
root = Path(__file__).resolve().parents[1]
path = root / "data" / "raw"
files = f"{path}/*.csv"
data_collect.fill_table(conn, files)
data_collect.create_parquet(conn, str(root / "data" / "raw"))
