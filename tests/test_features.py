"""Tests for feature engineering."""

import numpy as np
import pandas as pd
import pytest
from rapidkl.config import FEATURE_COLUMNS, TARGET
from rapidkl.features import build_features


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Build a small synthetic ridership dataframe with 60 daily rows."""
    dates = pd.date_range("2025-01-01", periods=60, freq="D")
    values = np.linspace(100_000, 120_000, 60)
    return pd.DataFrame({TARGET: values}, index=dates)


def test_build_features_returns_dataframe(sample_df: pd.DataFrame) -> None:
    result = build_features(sample_df)
    assert isinstance(result, pd.DataFrame)


def test_build_features_contains_all_feature_columns(
    sample_df: pd.DataFrame,
) -> None:
    result = build_features(sample_df)
    for column in FEATURE_COLUMNS:
        assert column in result.columns, f"missing feature: {column}"


def test_build_features_preserves_target(sample_df: pd.DataFrame) -> None:
    result = build_features(sample_df)
    assert TARGET in result.columns


def test_build_features_lags_create_nan_rows(sample_df: pd.DataFrame) -> None:
    result = build_features(sample_df)
    assert result["lag_28"].isna().sum() == 28


def test_build_features_drops_nan_rows_cleanly(sample_df: pd.DataFrame) -> None:
    result = build_features(sample_df)
    clean = result.dropna()
    assert clean["lag_28"].notna().all()
    assert len(clean) == 60 - 28


def test_build_features_holiday_columns_binary(sample_df: pd.DataFrame) -> None:
    result = build_features(sample_df)
    for column in [
        "is_holiday_kul",
        "is_holiday_sgr",
        "is_holiday_pjy",
        "is_public_holiday",
        "is_weekend",
    ]:
        assert set(result[column].unique()).issubset({0, 1})


def test_build_features_does_not_mutate_input(sample_df: pd.DataFrame) -> None:
    original_columns = sample_df.columns.tolist()
    build_features(sample_df)
    assert sample_df.columns.tolist() == original_columns
