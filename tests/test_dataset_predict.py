"""Tests for dataset splitting and prediction."""

import numpy as np
import pandas as pd
import pytest
from rapidkl.config import FEATURE_COLUMNS, TARGET
from rapidkl.dataset import make_splits, xy
from rapidkl.features import build_features
from rapidkl.metrics import calculate_metrics
from rapidkl.predict import predict
from xgboost import XGBRegressor

SYNTHETIC_SPLIT_DATES = {
    "train_end": "2024-06-30",
    "validation_start": "2024-07-01",
    "validation_end": "2025-06-30",
    "test_start": "2025-07-01",
}


@pytest.fixture
def model_data() -> pd.DataFrame:
    """Build 1000 days of synthetic ridership data with features."""
    dates = pd.date_range("2023-01-01", periods=1000, freq="D")
    values = (
        100_000
        + np.sin(np.arange(1000) * 2 * np.pi / 7) * 10_000
        + np.linspace(0, 20_000, 1000)
    )
    df = pd.DataFrame({TARGET: values}, index=dates)
    return build_features(df)


def _splits(model_data: pd.DataFrame) -> tuple:
    return make_splits(model_data, split_dates=SYNTHETIC_SPLIT_DATES)


def test_make_splits_returns_three_dataframes(
    model_data: pd.DataFrame,
) -> None:
    train, validation, test = make_splits(model_data, split_dates=SYNTHETIC_SPLIT_DATES)
    assert isinstance(train, pd.DataFrame)
    assert isinstance(validation, pd.DataFrame)
    assert isinstance(test, pd.DataFrame)


def test_make_splits_non_empty(model_data: pd.DataFrame) -> None:
    train, validation, test = make_splits(model_data, split_dates=SYNTHETIC_SPLIT_DATES)
    assert not train.empty
    assert not validation.empty
    assert not test.empty


def test_make_splits_no_nan_after_drop(model_data: pd.DataFrame) -> None:
    train, validation, test = make_splits(model_data, split_dates=SYNTHETIC_SPLIT_DATES)
    for split in (train, validation, test):
        assert split.notna().all().all()


def test_xy_splits_features_and_target(model_data: pd.DataFrame) -> None:
    train, _, _ = make_splits(model_data, split_dates=SYNTHETIC_SPLIT_DATES)
    X, y = xy(train)
    assert list(X.columns) == FEATURE_COLUMNS
    assert y.name == TARGET
    assert len(X) == len(y)


def test_predict_returns_series(model_data: pd.DataFrame) -> None:
    train, validation, _ = make_splits(model_data, split_dates=SYNTHETIC_SPLIT_DATES)
    X_train, y_train = xy(train)
    X_val, _ = xy(validation)

    model = XGBRegressor(n_estimators=10, max_depth=3, n_jobs=1)
    model.fit(X_train, y_train)

    predictions = predict(model, X_val)
    assert isinstance(predictions, pd.Series)
    assert len(predictions) == len(X_val)
    assert predictions.name == f"predicted_{TARGET}"


def test_predict_produces_finite_values(model_data: pd.DataFrame) -> None:
    train, validation, _ = make_splits(model_data, split_dates=SYNTHETIC_SPLIT_DATES)
    X_train, y_train = xy(train)
    X_val, _ = xy(validation)

    model = XGBRegressor(n_estimators=10, max_depth=3, n_jobs=1)
    model.fit(X_train, y_train)

    predictions = predict(model, X_val)
    assert np.isfinite(predictions).all()


def test_calculate_metrics_returns_expected_keys() -> None:
    actual = np.array([100.0, 200.0, 300.0])
    predicted = np.array([110.0, 190.0, 310.0])
    metrics = calculate_metrics(actual, predicted)
    assert set(metrics.keys()) == {"MAE", "RMSE", "WMAPE (%)"}
    assert metrics["MAE"] > 0
    assert metrics["RMSE"] > 0
    assert metrics["WMAPE (%)"] > 0


def test_calculate_metrics_perfect_predictions() -> None:
    actual = np.array([100.0, 200.0, 300.0])
    metrics = calculate_metrics(actual, actual)
    assert metrics["MAE"] == 0.0
    assert metrics["RMSE"] == 0.0
    assert metrics["WMAPE (%)"] == 0.0
