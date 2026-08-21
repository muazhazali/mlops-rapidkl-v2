"""FastAPI application for ridership forecasting."""

from __future__ import annotations

import math
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from rapidkl.predict import predict

from api.features_service import build_features_for_date, build_forecast
from api.loader import get_model
from api.schemas import (
    ForecastPoint,
    ForecastResponse,
    PredictRequest,
    PredictResponse,
)

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


@app.get("/forecast", response_model=ForecastResponse)
def forecast(
    start_date: date,
    end_date: date,
    target: str = "rail_mrt_kajang",
) -> ForecastResponse:
    """Return actual vs predicted ridership for a date range."""
    if start_date >= end_date:
        raise HTTPException(
            status_code=400, detail="start_date must be before end_date"
        )

    try:
        df = build_forecast(start_date, end_date, target)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    points: list[ForecastPoint] = []
    for dt, row in df.iterrows():
        actual = row["actual"]
        predicted = row["predicted"]
        points.append(
            ForecastPoint(
                date=dt.date(),
                actual=None if math.isnan(actual) else float(actual),
                predicted=None if math.isnan(predicted) else float(predicted),
            )
        )

    return ForecastResponse(
        target=target,
        start_date=start_date,
        end_date=end_date,
        points=points,
    )


_frontend_dist = Path(__file__).resolve().parent / "static"
if _frontend_dist.exists():
    app.mount(
        "/",
        StaticFiles(directory=str(_frontend_dist), html=True),
        name="frontend",
    )
