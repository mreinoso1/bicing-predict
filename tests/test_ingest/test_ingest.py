from datetime import UTC, datetime

import duckdb
import pandas as pd
import pytest

from bicing_predict.ingest import data_collect


def csv_correct(path):
    aux = pd.DataFrame(
        [[1, "1773144000", "NOT_IN_SERVICE", 1,0,1,20],[1,"1773145000","MAINTENANCE",0,0,0,20]],
        columns = ["station_id", "last_reported", "status", "is_installed", "is_renting", "is_returning", "num_bikes_available"],
    )
    aux.to_csv(path_or_buf=path, index = False)

def csv_with_v1(path):
    aux = pd.DataFrame(
        [[1, "1773144000", "NOT_IN_SERVICE", 1,0,1,20,1],[1,"1773145000","MAINTENANCE",0,0,0,18,1]],
        columns = ["station_id", "last_reported", "status", "is_installed", "is_renting", "is_returning", "num_bikes_available","V1"],
    )
    aux.to_csv(path_or_buf=path, index = False)


def csv_with_NA(path):
    aux = pd.DataFrame(
        [[1, "1773144000", "NOT_IN_SERVICE", 1,0,1,20],[1,"1773145000","MAINTENANCE",0,0,0,18], 
        [1,"NA","MAINTENANCE",0,0,0,18],[1,"5890","NA",0,0,0,18]],
        columns = ["station_id", "last_reported", "status", "is_installed", "is_renting", "is_returning", "num_bikes_available"],
    )
    aux.to_csv(path_or_buf=path, index = False)


def csv_for_utc(path):
    aux = pd.DataFrame(
        [[1,"1773144000","IN_SERVICE",1,1,1,5]],
        columns=["station_id", "last_reported", "status", "is_installed", "is_renting", "is_returning", "num_bikes_available"],
    )
    aux.to_csv(path_or_buf=path, index=False
)


@pytest.fixture()
def connect():
    connect = duckdb.connect(database = ":memory:")
    yield connect
    connect.close()


def test_row_count(connect,tmp_path):
    conn = connect
    temp = tmp_path / "correct.csv"
    csv_correct(temp)
    data_collect.fill_table(conn, temp)
    rows = conn.execute("""SELECT count(*) FROM bicing_6_months""").fetchone()[0]
    assert rows == 2


def test_for_v1(connect, tmp_path):
    conn = connect
    temp = tmp_path / "v1.csv"
    csv_with_v1(temp)
    data_collect.fill_table(conn,temp)
    with pytest.raises(duckdb.BinderException):
        conn.execute("""SELECT V1 FROM bicing_6_months""").fetchall()


def test_for_na(connect, tmp_path):
    conn = connect
    temp = tmp_path / "na.csv"
    csv_with_NA(temp)
    data_collect.fill_table(conn,temp)
    rows = conn.execute("""SELECT count(*) FROM bicing_6_months""").fetchone()[0]
    assert rows == 2


def test_columns(connect, tmp_path):
    conn = connect
    temp = tmp_path / "v1.csv"
    csv_with_v1(temp)
    data_collect.fill_table(conn,temp)
    conn.execute("""SELECT id, reported_at, status, installed, renting, is_returning, available_bikes FROM bicing_6_months""").fetchall()
    #If it does not arises an exception then all columns are in the table and test passes
    assert 1

def test_reported_at_utc(connect, tmp_path):
    conn = connect
    temp = tmp_path / "for_utc.csv"
    csv_for_utc(temp)
    data_collect.fill_table(conn,temp)
    assert conn.sql("SELECT reported_at FROM bicing_6_months").fetchone()[0] == datetime(2026, 3, 10, 12, 0, tzinfo=UTC)