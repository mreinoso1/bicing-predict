# bicing-predict

## Overview
Predicts the number of Bicing bicycles available at a station, depending on the station, the day of the week and the hour.

What differentiates this project is the Ridge regression trained with a hand-written Adam optimizer (NumPy),
which is tested against an oracle built with scikit-learn.
The dataset of ~27M readings, processed with DuckDB, comes from the open data website of the Ajuntament de Barcelona. It uses the months from February to August 2026, excluding July because it was not published when the data was collected.

## Prerequisites
To run the project, you need Python 3.12, uv and 7-Zip.
Download the months listed above from this website: https://opendata-ajuntament.barcelona.cat/data/es/dataset/estat-estacions-bicing

## Local Setup
1. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/mreinoso1/bicing-predict.git
   cd bicing-predict
   uv sync
   ```
2. Download the monthly files (Feb–Jun and Aug 2026) from the link in Prerequisites,
   extract them and place the `.csv` files in `data/raw/`:
   ```bash
   7z x data/raw/2026_02_Febrer_BicingNou_ESTACIONS.7z -odata/raw/   # repeat for each month
   ```
3. Build the clean dataset and the hourly aggregation:
   ```bash
   uv run python scripts/importing.py     # -> data/processed/bicing.parquet
   uv run python scripts/feature_eng.py   # -> data/processed/feature_bicing.parquet
   ```
4. Train the model, compare it with the oracle and print the metrics:
   ```bash
   uv run python src/bicing_predict/models/metrics.py   # also saves models/components.joblib
   ```

## Testing
To run the tests, execute `uv run pytest`.
This is what each test covers:
### features
* **test_feature:** Tests each function of `feature.py`, which creates the features of the dataset and splits it into train, validation and test.
* **test_grouping:** Tests the grouping function of `feature.py` with an `example.csv` and a `bicing.parquet` created only for the test with `tmp_path`.
### ingest
* **test_ingest:** Tests the ingestion functions in `data_collect.py`, used to make the data extraction easier.
### model
* **test_model:** Tests the functions of `model.py`. They are designed to prove that the mathematical basis of the functions is correct: they use manufactured data and compare the results against an oracle. It also tests the λ selection that is later used in `metrics.py`.
It also uses datasets generated directly from known weights, which is a good way to put the math of the NumPy algorithms to the test.
### api
* **test_api:** Tests the functions of `main.py` in the api directory, used to prove that the api only accepts the required data

## Evaluation Metrics

### Oracle check (hand-written Adam vs. scikit-learn `Ridge`)
| Metric | Value |
|---|---|
| Chosen λ | 0.001 |
| Epochs to converge | 13,000 |
| Final gradient norm | 5.3 × 10⁻¹² |
| Max weight difference | 3.5 × 10⁻³ |
| Intercept difference | 1.1 × 10⁻⁵ |
| Max prediction difference (validation) | 3.6 × 10⁻³ bikes |

### Model comparison (test set, August 2026)
| Model | RMSE | R² |
|---|---|---|
| Global mean (9.13 bikes) | 8.11 | 0.000 |
| Ridge (this project) | 6.88 | 0.280 |
| Means table (station × hour × weekday) | 5.87 | 0.475 |

The differences between the weights, intercepts and predictions of both implementations are minimal,
so the hand-written model matches the oracle. Its main weakness is predictive power: its R² is low and it
loses to the means table. This happens because the same hourly curve is applied to every station, even
though stations behave differently depending on their location, and because every day has different
circumstances that a calendar-only model cannot capture.

## Project Structure
```
├── Dockerfile
├── LICENSE
├── README.md
├── data
│   ├── processed        # Clean dataset and hourly aggregated features (parquet)
│   └── raw              # Monthly .csv and .7z files
├── models               # Trained model (components.joblib), created by metrics.py
├── scripts
│   ├── importing.py     # Builds data/processed/bicing.parquet
│   └── feature_eng.py   # Builds data/processed/feature_bicing.parquet
├── env.example
├── pyproject.toml
├── src
│   ├── api
│   │   ├── __init__.py
│   │   └── main.py
│   └── bicing_predict
│       ├── __init__.py
│       ├── features
│       │   ├── __init__.py
│       │   └── feature.py
│       ├── ingest
│       │   ├── __init__.py
│       │   └── data_collect.py
│       └── models
│           ├── __init__.py
│           ├── metrics.py
│           └── model.py
├── tests
│   ├── __init__.py
│   ├── test_api
│   │   ├── conftest.py
│   │   └── test_api.py
│   ├── test_features
│   │   ├── test_feature.py
│   │   └── test_grouping.py
│   ├── test_ingest
│   │   └── test_ingest.py
│   ├── test_model
│   │   └── test_model.py
│   └── test_smoke.py
└── uv.lock
```

## Limitations
- It only uses the calendar to predict: station, hour and day of the week. It does not react to real-time conditions such as weather, events or the bikes currently available.
- It applies the same hourly spline to every station, so it does not take into account that stations in different locations have different availability patterns.
- Data only covers February to August 2026, except July, which was not available when the data was collected.
- The source marks some frozen stations, which repeat the same reading, as `IN_SERVICE`. They were filtered out, but others may remain undetected.

## Future Work
- Interactions between stations and hours, so every station has its own hourly spline.
- Add the current number of available bicycles at the station as a feature, so the model predicts near-future availability.