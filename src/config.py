"""Configuration constants for the RapidKL MLOps project."""

from __future__ import annotations

from pathlib import Path

TARGET = "rail_mrt_kajang"
RANDOM_STATE = 42

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PARQUET_PATH = DATA_DIR / "ridership_headline.parquet"
CSV_PATH = DATA_DIR / "ridership_headline.csv"

SPLIT_DATES = {
    "train_end": "2024-12-31",
    "validation_start": "2025-01-01",
    "validation_end": "2025-12-31",
    "test_start": "2026-01-01",
}

FEATURE_COLUMNS = [
    "day_of_week",
    "month",
    "year",
    "is_weekend",
    "is_holiday_kul",
    "is_holiday_sgr",
    "is_holiday_pjy",
    "is_public_holiday",
    "is_day_before_holiday",
    "is_day_after_holiday",
    "lag_1",
    "lag_7",
    "lag_14",
    "lag_28",
    "rolling_mean_7",
    "rolling_mean_28",
    "rolling_std_7",
]

CATEGORICAL_FEATURES = [
    "day_of_week",
    "month",
    "is_weekend",
    "is_holiday_kul",
    "is_holiday_sgr",
    "is_holiday_pjy",
    "is_public_holiday",
    "is_day_before_holiday",
    "is_day_after_holiday",
]
