"""FastAPI application for ridership forecasting."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from rapidkl.predict import predict

from api.features_service import build_features_for_date
from api.loader import get_model
from api.schemas import PredictRequest, PredictResponse

app = FastAPI(
    title="RapidKL Ridership API",
    description="Forecast Malaysian public transport ridership",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict_ridership(request: PredictRequest) -> PredictResponse:
    """Forecast ridership for a future date."""
    try:
        features = build_features_for_date(request.target_date, request.target)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if features.isna().any().any():
        raise HTTPException(
            status_code=400,
            detail=(
                f"incomplete features for {request.target_date}; "
                "ensure the date is within 1 day after the last known data"
            ),
        )

    model = get_model()
    predictions = predict(model, features)
    return PredictResponse(
        target_date=request.target_date,
        target=request.target,
        predicted_ridership=float(predictions.iloc[0]),
    )
