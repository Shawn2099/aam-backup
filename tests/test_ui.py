"""Tests for the FastAPI status UI."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from ui.server import app
    return TestClient(app)


def _make_async_mock(return_value=None, side_effect=None):
    """Create an async mock that returns the given value."""
    async def mock_method(*args, **kwargs):
        if side_effect:
            raise side_effect
        return return_value
    return mock_method


def test_index_returns_html(client):
    """GET / returns HTML status page."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=Exception("Prefect unavailable")
        )
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Backup Status" in response.text
        assert "AAM Associates" in response.text


def test_index_shows_no_runs_message(client):
    """GET / shows 'No backup runs yet' when Prefect has no data."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = MagicMock()
        mock_instance.post = AsyncMock(return_value=MagicMock(status_code=200, json=lambda: []))
        mock_client.return_value.__aenter__.return_value = mock_instance
        response = client.get("/")
        assert response.status_code == 200
        assert "No backup runs yet" in response.text


def test_index_shows_last_run_status(client):
    """GET / shows last run status when available."""
    mock_run = [{
        "id": "test-run-id",
        "state_name": "Completed",
        "start_time": "2026-05-18T17:30:00Z",
        "end_time": "2026-05-18T18:00:00Z",
    }]
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = MagicMock()
        mock_instance.post = AsyncMock(
            side_effect=[
                MagicMock(status_code=200, json=lambda: mock_run),
                MagicMock(status_code=200, json=lambda: []),
            ]
        )
        mock_client.return_value.__aenter__.return_value = mock_instance
        response = client.get("/")
        assert response.status_code == 200
        assert "Completed" in response.text


def test_trigger_backup_success(client):
    """POST /trigger returns ok when deployment found."""
    mock_deployments = [{"id": "test-deployment-id"}]
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = MagicMock()
        mock_instance.post = AsyncMock(
            side_effect=[
                MagicMock(status_code=200, json=lambda: mock_deployments),
                MagicMock(status_code=201)
            ]
        )
        mock_client.return_value.__aenter__.return_value = mock_instance
        response = client.post("/trigger")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


def test_trigger_backup_deployment_not_found(client):
    """POST /trigger returns error when deployment not found."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = MagicMock()
        mock_instance.post = AsyncMock(return_value=MagicMock(status_code=200, json=lambda: []))
        mock_client.return_value.__aenter__.return_value = mock_instance
        response = client.post("/trigger")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "not found" in data["message"]


def test_trigger_backup_prefect_unavailable(client):
    """POST /trigger returns error when Prefect is unavailable."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = MagicMock()
        mock_instance.post = AsyncMock(side_effect=Exception("Connection refused"))
        mock_client.return_value.__aenter__.return_value = mock_instance
        response = client.post("/trigger")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
