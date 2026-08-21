"""Pydantic request/response schemas for the ridership API."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """Request body for the /predict endpoint."""

    target_date: date = Field(..., description="Date to forecast ridership for")
    target: str = Field(
        default="rail_mrt_kajang",
        description="Ridership column to forecast",
    )


class PredictResponse(BaseModel):
    """Response body for the /predict endpoint."""

    target_date: date
    target: str
    predicted_ridership: float


class ForecastPoint(BaseModel):
    """A single actual-vs-predicted data point."""

    date: date
    actual: float | None = None
    predicted: float | None = None


class ForecastResponse(BaseModel):
    """Response body for the /forecast endpoint."""

    target: str
    start_date: date
    end_date: date
    points: list[ForecastPoint]
