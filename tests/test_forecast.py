"""Tests for the /forecast endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def test_forecast_returns_points(client: TestClient) -> None:
    response = client.get(
        "/forecast",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-02-01",
            "target": "rail_mrt_kajang",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["target"] == "rail_mrt_kajang"
    assert len(data["points"]) == 32
    first = data["points"][0]
    assert "date" in first
    assert "actual" in first
    assert "predicted" in first


def test_forecast_includes_future_dates(client: TestClient) -> None:
    response = client.get(
        "/forecast",
        params={
            "start_date": "2026-06-29",
            "end_date": "2026-07-03",
            "target": "rail_mrt_kajang",
        },
    )
    assert response.status_code == 200
    points = response.json()["points"]
    assert len(points) == 5

    has_actual = any(p["actual"] is not None for p in points)
    has_future = any(p["actual"] is None for p in points)
    assert has_actual
    assert has_future


def test_forecast_rejects_invalid_range(client: TestClient) -> None:
    response = client.get(
        "/forecast",
        params={
            "start_date": "2026-02-01",
            "end_date": "2026-01-01",
            "target": "rail_mrt_kajang",
        },
    )
    assert response.status_code == 400
