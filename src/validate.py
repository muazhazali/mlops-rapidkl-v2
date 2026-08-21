"""Data validation utilities."""

from __future__ import annotations

import pandas as pd


def validate_dataframe(df: pd.DataFrame, target: str) -> None:
    """Run schema and quality assertions against the ridership dataframe."""
    assert isinstance(df.index, pd.DatetimeIndex), "index must be a DatetimeIndex"
    assert df.index.is_monotonic_increasing, "index must be sorted ascending"
    assert not df.index.has_duplicates, "index must not contain duplicate dates"
    assert target in df.columns, f"target column '{target}' missing"
    assert df[target].notna().all(), f"target column '{target}' contains NaNs"
    assert df[target].ge(0).all(), f"target column '{target}' contains negative values"
