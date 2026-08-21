"""Model loader for the ridership API.

Loads the latest MLflow-registered XGBoost model once at startup and caches it
module-level so request handlers stay fast.
"""

from __future__ import annotations

import os

import mlflow
from xgboost import XGBRegressor

DEFAULT_MODEL_NAME = os.getenv("MLFLOW_MODEL_NAME", "rapidkl-ridership-xgb")
DEFAULT_MODEL_ALIAS = os.getenv("MLFLOW_MODEL_ALIAS", "Production")
DEFAULT_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")

_model: XGBRegressor | None = None


def get_model() -> XGBRegressor:
    """Return the cached model, loading it on first access."""
    global _model
    if _model is None:
        mlflow.set_tracking_uri(DEFAULT_TRACKING_URI)
        _model = mlflow.xgboost.load_model(
            f"models:/{DEFAULT_MODEL_NAME}@{DEFAULT_MODEL_ALIAS}"
        )
    return _model
