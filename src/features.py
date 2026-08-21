"""Feature engineering for ridership forecasting."""

from __future__ import annotations

import holidays
import pandas as pd
from rapidkl.config import TARGET

_HOLIDAY_SUBDIVISIONS = {
    "kul": "KUL",
    "sgr": "SGR",
    "pjy": "PJY",
}


def _add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    df["day_of_week"] = df.index.dayofweek
    df["month"] = df.index.month
    df["year"] = df.index.year
    df["is_weekend"] = (df.index.dayofweek >= 5).astype("int8")
    return df


def _add_holiday_features(df: pd.DataFrame) -> pd.DataFrame:
    years = range(df.index.min().year, df.index.max().year + 1)

    regional_columns: list[str] = []
    dates = pd.Series(df.index.date, index=df.index)

    for region, subdiv in _HOLIDAY_SUBDIVISIONS.items():
        calendar = holidays.country_holidays(
            "MY", subdiv=subdiv, years=years, observed=True
        )
        column = f"is_holiday_{region}"
        df[column] = dates.isin(calendar).astype("int8")
        regional_columns.append(column)

    df["is_public_holiday"] = (
        df[regional_columns].max(axis=1).astype("int8")
    )

    holiday = df["is_public_holiday"].astype(bool)
    df["is_day_before_holiday"] = holiday.shift(-1, fill_value=False).astype("int8")
    df["is_day_after_holiday"] = holiday.shift(1, fill_value=False).astype("int8")
    return df


def _add_lag_features(df: pd.DataFrame, target: str = TARGET) -> pd.DataFrame:
    df["lag_1"] = df[target].shift(1)
    df["lag_7"] = df[target].shift(7)
    df["lag_14"] = df[target].shift(14)
    df["lag_28"] = df[target].shift(28)
    return df


def _add_rolling_features(df: pd.DataFrame, target: str = TARGET) -> pd.DataFrame:
    past_target = df[target].shift(1)
    df["rolling_mean_7"] = past_target.rolling(window=7).mean()
    df["rolling_mean_28"] = past_target.rolling(window=28).mean()
    df["rolling_std_7"] = past_target.rolling(window=7).std()
    return df


def build_features(
    df: pd.DataFrame, target: str = TARGET
) -> pd.DataFrame:
    """Build the full feature set on a single-target ridership dataframe.

    The input dataframe must be indexed by date and contain the target column.
    Returns a new dataframe with calendar, holiday, lag, and rolling features
    appended. The first 28 rows contain NaNs from lag/rolling windows and
    should be dropped before training.
    """
    result = df.copy()
    result[target] = result[target].astype("float64")
    result = _add_calendar_features(result)
    result = _add_holiday_features(result)
    result = _add_lag_features(result, target)
    result = _add_rolling_features(result, target)
    return result
