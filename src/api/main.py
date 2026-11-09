import os
import secrets
from pathlib import Path

import joblib
import pandas as pd
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

load_dotenv()
api_token = os.getenv("API_TOKEN", "")  # Gets api_token from .env
if not api_token:
    raise RuntimeError("API_TOKEN is missing")


class PredictionRequest(BaseModel):
    station: int = Field(..., ge=1, le=614)
    hour: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=1, le=7)  # Monday is 1 and Sunday is 7


class PredictionResponse(BaseModel):
    available_bikes: list[float]


# Variables
app = FastAPI()
root = Path(__file__).resolve().parents[2]
default_path = root / "models" / "components.joblib"
model_path = Path(os.getenv("MODEL_PATH", default_path))
components = joblib.load(model_path)
Transformer = components["SplineTransformer"]
weights = components["Weights"]
intercept = components["Intercept"]
valid_stations = Transformer.named_transformers_["stations"].categories_[0]
api_key_header = APIKeyHeader(name="Token")


@app.post("/predict", status_code=status.HTTP_200_OK, response_model=PredictionResponse)
async def predict(
    request_pred: PredictionRequest, token: str = Depends(api_key_header)
):
    if not secrets.compare_digest(
        token, api_token
    ):  # Compares at the same time rate even if it fails or succeeds
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if not (
        request_pred.station in valid_stations
    ):  # If the station of input does not exist
        raise HTTPException(status_code=404, detail="Unknown station")

    data = pd.DataFrame(
        {
            "id": [request_pred.station],
            "hour_report": [request_pred.hour],
            "dow": [request_pred.day_of_week],
        }
    )

    x = Transformer.transform(
        data
    )  # Transforms all the variables so the weights can read it
    prediction = (x @ weights) + intercept  # Produces the prediction
    print(prediction)

    answer = PredictionResponse(available_bikes=prediction)
    return answer
