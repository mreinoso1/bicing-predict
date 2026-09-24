import duckdb as db
import pandas as pd
import pytest

from bicing_predict.features import feature


def csv_hour(path):
    aux = pd.DataFrame(
        [[1, "2026-02-02 13:15:00", "NOT_IN_SERVICE", 1,0,1,20],[520,"2026-02-02 13:18:00","IN_SERVICE",1,1,0,12],
        [520,"2026-02-02 13:34:00","IN_SERVICE",1,1,0,10],[120,"2026-02-02 13:34:00","IN_SERVICE",1,1,0,5]
        ,[160,"2026-02-02 13:54:00","MAINTENANCE",1,1,0,16],],
        columns = ["id", "reported_at", "status", "installed", "renting", "is_returning", "available_bikes"],
    )
    aux.to_csv(path_or_buf=path, index = False)

@pytest.fixture
def connection():
    connect = db.connect(database = ":memory:")
    yield connect
    connect.close()

def test_grouping_rows(connection,tmp_path):
    conn = connection
    temp = tmp_path / "example.csv"
    temp_dest = tmp_path / "bicing.parquet"
    csv_hour(temp)
    feature.create_grouping_parquet(conn,temp, temp_dest)
    row =conn.execute(f"""
        SELECT count(*)
        FROM read_parquet('{temp_dest}')
    """).fetchone()[0]

    assert row == 2