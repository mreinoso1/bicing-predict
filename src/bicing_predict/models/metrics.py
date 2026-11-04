from pathlib import Path

import duckdb as db
import joblib
import numpy as np
from sklearn.linear_model import Ridge

from bicing_predict.features import feature
from bicing_predict.models import model

root = Path(__file__).resolve().parents[3]
path = root / "data" / "processed" / "feature_bicing.parquet"
X_train, X_val, X_test, y_train, y_val, y_test, col_t = feature.feature_eng(path)

# Training model
weights = np.zeros(X_train.shape[1])
tolerance = 1e-3
epochs = 100000
learning_rate = 0.01
# Search which alpha is better
alpha_cand = [1, 0.1, 0.01, 0.001]
alphas = np.array(alpha_cand, dtype=float)
rmse = model.alphas(
    alphas, X_val, y_val, X_train, y_train, weights, tolerance, learning_rate, epochs
)
print(f"λ Table: {rmse}")
index_param = np.argmin(rmse)
alpha = alphas[index_param]
print(f"Chosen λ: {alphas[index_param]}")
weights = np.zeros(X_train.shape[1])

# Training model
alpha = 0.001
tolerance = 1e-10
print("Training Model:")
w, b, norma, epochs_used = model.Adam(
    X_train,
    y_train,
    weights,
    tolerance,
    learning_rate,
    epochs,
    alpha,
)
# Printing stats of the model
print(f"Model Weights: {w} \nModel Intercept: {b}")
print(f"Norm: {norma} \nEpochs: {epochs_used}")

# Training Oracle
print("Training Oracle")
skmodel = Ridge(alpha=2 * alpha * X_train.shape[0])
skmodel.fit(X_train, y_train)

predict_oracle = skmodel.predict(X_val)
predict_model = model.func(X_val, w, b)
print(f"Oracle weights: {skmodel.coef_}\n Intercept: {skmodel.intercept_}")
print(f"Max diff between weights: {np.max(np.abs(w - skmodel.coef_))}")
print(f"Difference between intercepts: {np.abs(b - skmodel.intercept_)}")
print(
    f"Max diff between validation predicts: {np.max(np.abs(predict_oracle - predict_model))}"
)

# Stats with own weights
avg_test = np.mean(y_test)
predict_test = model.func(X_test, w, b)
R_squared = 1 - np.sum((predict_test - y_test) ** 2) / np.sum((y_test - avg_test) ** 2)
print(f"R^2 with test data: {R_squared}")

sq_error = (model.func(X_test, w, b) - y_test) ** 2
rmse = np.sqrt(np.mean(sq_error))
print(f"RMSE with test data: {rmse}")

# Global Mean RMSE
avg_train = np.mean(y_train)
R_squared_case = 1 - np.sum((y_test - avg_train) ** 2) / np.sum(
    (y_test - avg_test) ** 2
)
sq_error = (avg_train - y_test) ** 2
rmse = np.sqrt(np.mean(sq_error))
print(
    f"Global Mean: {avg_train}\nGlobal Mean R^2:{R_squared_case}\nGlobal Mean RMSE:{rmse}"
)

# AVERAGE TABLE
conn = db.connect()
SQL_REQUEST = """
WITH
data AS (SELECT * FROM read_parquet($path)),
train AS (SELECT * FROM data WHERE hour_start < '2026-06-01'),
eval AS (SELECT * FROM data WHERE hour_start >= $start AND hour_start < $end),
means_table AS (
    SELECT id, hour_report, dow, AVG(avg_bikes) AS pred
    FROM train
    GROUP BY ALL
),
train_mean AS (SELECT AVG(avg_bikes) AS m FROM train),
eval_mean AS (SELECT AVG(avg_bikes) AS m FROM eval)

SELECT
    sqrt(AVG(power(e.avg_bikes - COALESCE(t.pred, tm.m), 2))) AS rmse,
    1 - SUM(power(e.avg_bikes - COALESCE(t.pred, tm.m), 2))
      / SUM(power(e.avg_bikes - em.m, 2))                    AS r2
FROM eval e
LEFT JOIN means_table t
    ON e.id = t.id AND e.hour_report = t.hour_report AND e.dow = t.dow
CROSS JOIN train_mean tm
CROSS JOIN eval_mean em
"""

res_val = db.execute(
    SQL_REQUEST, {"path": str(path), "start": "2026-06-01", "end": "2026-07-01"}
).fetchone()

rmse_val = 0.0
r2_val = 0.0
if res_val is not None:
    rmse_val, r2_val = res_val

res_test = db.execute(
    SQL_REQUEST, {"path": str(path), "start": "2026-08-01", "end": "2026-09-01"}
).fetchone()

rmse_val = 0.0
r2_val = 0.0
if res_val is not None:
    rmse_test, r2_test = res_val

print(f"Means table — val RMSE: {rmse_val}, R^2: {r2_val}")
print(f"Means table — test RMSE: {rmse_test}, R^2: {r2_test}")

save_dict = {"SplineTransformer": col_t, "Weights": w, "Intercept": b}

joblib.dump(save_dict, "components.joblib")
