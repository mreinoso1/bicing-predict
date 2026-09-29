import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, SplineTransformer


def create_grouping_parquet(conn, path: str, destiny):
    conn.sql(f"""
    COPY (
        SELECT id, date_trunc('hour', reported_at AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Madrid') AS hour_start
        ,dayofweek(reported_at AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Madrid') AS dow,
        hour(reported_at AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Madrid') AS hour_report, AVG(available_bikes) as avg_bikes, 
        COUNT(*) AS n_readings
        FROM '{path}'
        WHERE status = 'IN_SERVICE'
        GROUP BY ALL
    ) TO '{destiny}' (FORMAT parquet)
    """)


def split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = df[df["hour_start"] < "2026-06-01"]
    val = df[(df["hour_start"] >= "2026-06-01") & (df["hour_start"] < "2026-07-01")]
    test = df[(df["hour_start"] >= "2026-08-01") & (df["hour_start"] < "2026-09-01")]
    return train, val, test


def feature_eng(path):
    df = pd.read_parquet(path)
    train, val, test = split(df)
    N = 9
    column_trans = ColumnTransformer(
        transformers=[
            ("stations", OneHotEncoder(handle_unknown="ignore"), ["id"]),
            (
                "hour",
                SplineTransformer(
                    extrapolation="periodic",
                    knots=np.linspace(0, 24, N).reshape(-1, 1),
                    degree=3,
                ),
                ["hour_report"],
            ),
            (
                "dow",
                SplineTransformer(
                    extrapolation="periodic",
                    knots=np.linspace(0, 7, 8).reshape(-1, 1),
                    degree=3,
                ),
                ["dow"],
            ),
        ],
        sparse_threshold=1.0,
        verbose_feature_names_out=False,
    )

    X_train = column_trans.fit_transform(train).tocsr()
    X_val = column_trans.transform(val).tocsr()
    X_test = column_trans.transform(test).tocsr()

    y_train = train["avg_bikes"].to_numpy()
    y_val = val["avg_bikes"].to_numpy()
    y_test = test["avg_bikes"].to_numpy()

    return X_train, X_val, X_test, y_train, y_val, y_test
