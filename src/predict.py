"""Prediction utilities for the trained ridership model."""

from __future__ import annotations

import mlflow
import pandas as pd
from rapidkl.config import FEATURE_COLUMNS, TARGET
from xgboost import XGBRegressor


def load_model(
    model_name: str = "rapidkl-ridership-xgb",
    alias: str = "Production",
    tracking_uri: str | None = None,
) -> XGBRegressor:
    """Load the latest MLflow-registered XGBoost model."""
    if tracking_uri is not None:
        mlflow.set_tracking_uri(tracking_uri)

    model_uri = f"models:/{model_name}@{alias}"
    return mlflow.xgboost.load_model(model_uri)


def predict(
    model: XGBRegressor,
    df: pd.DataFrame,
    feature_columns: list[str] | None = None,
) -> pd.Series:
    """Generate ridership predictions for the given feature dataframe."""
    features = feature_columns or FEATURE_COLUMNS
    predictions = model.predict(df[features])
    return pd.Series(predictions, index=df.index, name=f"predicted_{TARGET}")
