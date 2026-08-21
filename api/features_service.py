"""Feature builder for the API.

Builds the full feature row for a single target date by loading the historical
ridership data and computing calendar, holiday, lag, and rolling features up to
that date. The returned dataframe contains a single row (the target date)
ready for prediction.
"""

from __future__ import annotations

from datetime import date

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
