"""Model training with XGBoost and MLflow tracking."""

from __future__ import annotations

from pathlib import Path

import mlflow
import mlflow.xgboost
import pandas as pd
import xgboost as xgb
from rapidkl.config import FEATURE_COLUMNS, RANDOM_STATE, TARGET
from rapidkl.data import load_data
from rapidkl.dataset import make_dataset, make_splits, xy
from rapidkl.metrics import calculate_metrics

DEFAULT_EXPERIMENT_NAME = "rapidkl-ridership"
DEFAULT_MODEL_NAME = "rapidkl-ridership-xgb"
DEFAULT_TRACKING_URI = "sqlite:///mlflow.db"
MAX_LAG_ROWS = 28


def train_model(
    df: pd.DataFrame | None = None,
    target: str = TARGET,
    feature_columns: list[str] | None = None,
    experiment_name: str = DEFAULT_EXPERIMENT_NAME,
    model_name: str = DEFAULT_MODEL_NAME,
    tracking_uri: str | Path | None = None,
    params: dict | None = None,
) -> dict:
    """Train an XGBoost regressor and log it to MLflow.

    Returns a dict with the trained model, validation/test metrics, and the
    MLflow run ID.
    """
    features = feature_columns or FEATURE_COLUMNS
    params = params or {
        "n_estimators": 500,
        "max_depth": 6,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 5,
        "random_state": RANDOM_STATE,
        "n_jobs": -1,
    }

    if df is None:
        df = load_data()

    model_data = make_dataset(df, target)
    train, validation, test = make_splits(model_data, target, features)

    X_train, y_train = xy(train, target, features)
    X_val, y_val = xy(validation, target, features)
    X_test, y_test = xy(test, target, features)

    mlflow.set_tracking_uri(str(tracking_uri or DEFAULT_TRACKING_URI))
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run() as run:
        mlflow.log_params({**params, "target": target, "n_features": len(features)})
        mlflow.log_param("feature_columns", features)

        model = xgb.XGBRegressor(**params)
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )

        val_pred = model.predict(X_val)
        test_pred = model.predict(X_test)

        val_metrics = calculate_metrics(y_val, val_pred)
        test_metrics = calculate_metrics(y_test, test_pred)

        for name, value in val_metrics.items():
            metric_key = name.lower().replace(" (%)", "").replace(" ", "_")
            mlflow.log_metric(f"val_{metric_key}", value)
        for name, value in test_metrics.items():
            metric_key = name.lower().replace(" (%)", "").replace(" ", "_")
            mlflow.log_metric(f"test_{metric_key}", value)

        mv = mlflow.xgboost.log_model(
            xgb_model=model,
            artifact_path="model",
            registered_model_name=model_name,
            input_example=X_train.head(1),
        )

        client = mlflow.tracking.MlflowClient()
        version = mv.registered_model_version if mv else None
        if version:
            client.set_registered_model_alias(model_name, "Production", version)

        return {
            "model": model,
            "run_id": run.info.run_id,
            "model_version": version,
            "val_metrics": val_metrics,
            "test_metrics": test_metrics,
            "feature_columns": features,
        }
