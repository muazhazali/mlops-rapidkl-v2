"""Metrics for ridership forecasting evaluation."""

from __future__ import annotations

import numpy as np


def calculate_metrics(actual, predicted) -> dict[str, float]:
    """Return MAE, RMSE, and WMAPE (%) for actual vs predicted arrays."""
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    error = actual - predicted

    mae = float(np.mean(np.abs(error)))
    rmse = float(np.sqrt(np.mean(error**2)))
    wmape = float(np.sum(np.abs(error)) / np.sum(np.abs(actual)) * 100)

    return {"MAE": mae, "RMSE": rmse, "WMAPE (%)": wmape}
