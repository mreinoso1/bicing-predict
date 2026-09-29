import pandas as pd

from bicing_predict.features import feature


def df_hour_out_of_range() -> pd.DataFrame:
    aux =  pd.DataFrame(
        [[1,'2026-05-31 17:00:00',4,22,8],[1,'2026-06-01 17:00:00',4,22,8],
        [1,'2026-08-01 17:00:00',4,22,8],[1,'2026-11-10 17:00:00',4,22,8]],
        columns = ["id", "hour_start", "dow", "hour", "avg_bikes"],
    )
    aux["hour_start"] = pd.to_datetime(aux["hour_start"])
    return aux


def new_parquet(path):
    aux =  pd.DataFrame(
        [[1,'2026-05-31 17:00:00',4,17,8],[1,'2026-06-01 12:00:00',4,12,8],
        [4,'2026-08-01 17:00:00',5,17,8],[4,'2026-11-10 13:00:00',2,13,8],
        [3,'2026-03-01 15:00:00', 6,17,8], [5, '2026-08-13 15:00:00',4,12,15]],
        columns = ["id", "hour_start", "dow", "hour_report", "avg_bikes"],
    )
    aux["hour_start"] = pd.to_datetime(aux["hour_start"])
    aux.to_parquet(path)
    

def test_hour():
    train,val,test =feature.split(df_hour_out_of_range())
    print(test)
    assert test.shape == (1,5)
    assert val.shape == (1,5)
    assert train.shape == (1,5)


def test_features(tmp_path):
    path = tmp_path / "final.parquet"
    new_parquet(path = path)
    _X_train,_X_val,_X_test,_y_train,_y_val,_y_test = feature.feature_eng(path)
    #If no error is thrown then the test is passed
    assert 1