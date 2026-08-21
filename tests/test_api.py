"""Tests for the FastAPI ridership API."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_returns_ridership(client: TestClient) -> None:
    response = client.post(
        "/predict",
        json={"target_date": "2026-07-01", "target": "rail_mrt_kajang"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["target_date"] == "2026-07-01"
    assert data["target"] == "rail_mrt_kajang"
    assert isinstance(data["predicted_ridership"], float)
    assert data["predicted_ridership"] > 0


def test_predict_rejects_past_date(client: TestClient) -> None:
    response = client.post(
        "/predict",
        json={"target_date": "2025-01-01", "target": "rail_mrt_kajang"},
    )
    assert response.status_code == 400


def test_predict_rejects_existing_date(client: TestClient) -> None:
    response = client.post(
        "/predict",
        json={"target_date": "2026-06-30", "target": "rail_mrt_kajang"},
    )
    assert response.status_code == 400
