"""Feature builder for the API.

Builds the full feature row for a single target date by loading the historical
ridership data and computing calendar, holiday, lag, and rolling features up to
that date. The returned dataframe contains a single row (the target date)
ready for prediction.
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
from rapidkl.config import FEATURE_COLUMNS, TARGET
from rapidkl.data import load_data
from rapidkl.features import build_features

_history_cache: pd.DataFrame | None = None


def _load_history() -> pd.DataFrame:
    """Load and cache the full ridership history."""
    global _history_cache
    if _history_cache is None:
        _history_cache = load_data()
    return _history_cache


def build_features_for_date(
    target_date: date,
    target: str = TARGET,
) -> pd.DataFrame:
    """Build the feature row for ``target_date``.

    Loads the ridership history, appends a placeholder row for the target date
    (with NaN target), builds features, and returns the single row matching
    ``target_date``. Raises ValueError if the target date is outside the
    range where all lag/rolling features can be computed (i.e. within the
    known history or at most 1 day after the last known date).
    """
    history = _load_history()

    if target_date in history.index:
        raise ValueError(
            f"target_date {target_date} already exists in history; "
            "prediction is for future dates only"
        )

    last_known = history.index.max().date()
    if target_date <= last_known:
        raise ValueError(
            f"target_date {target_date} must be after the last known "
            f"date {last_known}"
        )

    future_index = pd.date_range(
        start=history.index.max() + pd.Timedelta(days=1),
        end=pd.Timestamp(target_date),
        freq="D",
    )
    future_df = pd.DataFrame(
        {target: pd.Series([float("nan")] * len(future_index), dtype="float64")},
        index=future_index,
    )
    extended = pd.concat([history[[target]].astype("float64"), future_df])
    featured = build_features(extended, target)

    row = featured.loc[[pd.Timestamp(target_date)]]
    return row[FEATURE_COLUMNS]


def build_forecast(
    start_date: date,
    end_date: date,
    target: str = TARGET,
    model=None,
) -> pd.DataFrame:
    """Build actual vs predicted ridership for a date range.

    For dates within the known history, predictions are one-step-ahead (lags
    use actual values). For dates beyond the history, predictions are recursive
    (predicted values feed back as lag inputs for subsequent days).

    Returns a DataFrame indexed by date with columns: actual, predicted.
    ``actual`` is NaN for future dates where no ground truth exists.
    """
    from rapidkl.predict import predict as _predict

    history = _load_history()
    history_series = history[target].astype("float64").copy()

    all_dates = pd.date_range(
        start=pd.Timestamp(start_date), end=pd.Timestamp(end_date), freq="D"
    )
    last_known = history.index.max()

    if model is None:
        from api.loader import get_model
        model = get_model()

    actuals = history_series.reindex(all_dates)

    combined = history_series.copy()
    predictions: dict[pd.Timestamp, float] = {}

    for dt in all_dates:
        ts = pd.Timestamp(dt)

        if ts > last_known:
            temp_series = combined.copy()
            temp_series.loc[ts] = float("nan")
        else:
            temp_series = combined.copy()

        temp_df = pd.DataFrame({target: temp_series})
        featured = build_features(temp_df, target)

        if ts not in featured.index:
            continue

        row = featured.loc[[ts], FEATURE_COLUMNS]
        if row.isna().any().any():
            continue

        pred = float(_predict(model, row).iloc[0])
        predictions[ts] = pred

        if ts > last_known:
            combined.loc[ts] = pred

    result = pd.DataFrame(
        {
            "actual": actuals.values,
            "predicted": [predictions.get(dt, np.nan) for dt in all_dates],
        },
        index=all_dates,
    )
    return result
