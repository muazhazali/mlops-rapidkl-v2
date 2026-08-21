"""Dataset construction and train/validation/test splitting."""

from __future__ import annotations

import pandas as pd
from rapidkl.config import FEATURE_COLUMNS, SPLIT_DATES, TARGET
from rapidkl.features import build_features
from rapidkl.validate import validate_dataframe


def make_dataset(
    df: pd.DataFrame, target: str = TARGET
) -> pd.DataFrame:
    """Select the target, validate, and build features on a raw dataframe."""
    model_data = df[[target]].copy()
    model_data[target] = model_data[target].astype("float64")
    validate_dataframe(model_data, target)
    return build_features(model_data, target)


def make_splits(
    model_data: pd.DataFrame,
    target: str = TARGET,
    feature_columns: list[str] | None = None,
    split_dates: dict[str, str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split model_data into train/validation/test on date boundaries.

    Returns (train, validation, test) dataframes each containing the feature
    columns and the target column, with lag-induced NaN rows dropped.
    """
    features = feature_columns or FEATURE_COLUMNS
    dates = split_dates or SPLIT_DATES

    train = model_data.loc[: dates["train_end"]].copy()
    validation = model_data.loc[
        dates["validation_start"] : dates["validation_end"]
    ].copy()
    test = model_data.loc[dates["test_start"] :].copy()

    assert not train.empty, "train split is empty"
    assert not validation.empty, "validation split is empty"
    assert not test.empty, "test split is empty"

    columns = features + [target]
    train = train[columns].dropna()
    validation = validation[columns].dropna()
    test = test[columns].dropna()
    return train, validation, test


def xy(
    split: pd.DataFrame,
    target: str = TARGET,
    feature_columns: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.Series]:
    """Split a dataframe into (X, y) feature matrix and target series."""
    features = feature_columns or FEATURE_COLUMNS
    return split[features], split[target]
