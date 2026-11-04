from pathlib import Path

import duckdb as db

from bicing_predict.features import feature

conn = db.connect(database=":memory:")
root = Path(__file__).resolve().parents[1]
path = root / "data" / "processed" / "bicing.parquet"
destiny = root / "data" / "processed" / "feature_bicing.parquet"

feature.create_grouping_parquet(conn, str(path), str(destiny))
