"""Data loading utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from rapidkl.config import CSV_PATH, PARQUET_PATH


def load_parquet(path: Path | None = None) -> pd.DataFrame:
    """Load the ridership parquet file and parse the date column."""
    resolved_path = path or PARQUET_PATH
    df = pd.read_parquet(resolved_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").set_index("date")
    return df


def load_csv(path: Path | None = None) -> pd.DataFrame:
    """Load the ridership CSV file and parse the date column."""
    resolved_path = path or CSV_PATH
    df = pd.read_csv(resolved_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").set_index("date")
    return df


def load_data(path: Path | None = None) -> pd.DataFrame:
    """Load ridership data, preferring parquet over CSV when path is unset."""
    if path is not None:
        suffix = path.suffix.lower()
        if suffix == ".parquet":
            return load_parquet(path)
        if suffix == ".csv":
            return load_csv(path)
        raise ValueError(f"Unsupported file extension: {suffix}")

    if PARQUET_PATH.exists():
        return load_parquet()
    if CSV_PATH.exists():
        return load_csv()
    raise FileNotFoundError(
        f"No ridership data found in {PARQUET_PATH.parent}"
    )
