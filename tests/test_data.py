"""Tests for data loading."""

from pathlib import Path

import pandas as pd
import pytest
from rapidkl.config import CSV_PATH, PARQUET_PATH, TARGET
from rapidkl.data import load_csv, load_data, load_parquet


@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    return load_data()


def test_data_file_exists() -> None:
    assert PARQUET_PATH.exists() or CSV_PATH.exists()


def test_load_parquet_returns_dataframe() -> None:
    if not PARQUET_PATH.exists():
        pytest.skip("parquet file not found")
    df = load_parquet()
    assert isinstance(df, pd.DataFrame)
    assert TARGET in df.columns


def test_load_csv_returns_dataframe() -> None:
    if not CSV_PATH.exists():
        pytest.skip("csv file not found")
    df = load_csv()
    assert isinstance(df, pd.DataFrame)
    assert TARGET in df.columns


def test_loaded_data_has_datetime_index(df: pd.DataFrame) -> None:
    assert isinstance(df.index, pd.DatetimeIndex)


def test_loaded_data_is_sorted(df: pd.DataFrame) -> None:
    assert df.index.is_monotonic_increasing


def test_loaded_data_has_no_duplicate_dates(df: pd.DataFrame) -> None:
    assert not df.index.has_duplicates


def test_loaded_data_has_target_column(df: pd.DataFrame) -> None:
    assert TARGET in df.columns


def test_load_data_supports_explicit_path(tmp_path: Path) -> None:
    if not PARQUET_PATH.exists():
        pytest.skip("parquet file not found")
    df = load_data(PARQUET_PATH)
    assert TARGET in df.columns
