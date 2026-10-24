"""
Health and basic functionality tests for CloudRoute AI FastAPI backend.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify root endpoint responds with project information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "CloudRoute AI"
    assert "health_check" in data


def test_health_check_endpoint():
    """Verify /api/health reports healthy status and operational database."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "CloudRoute AI Backend"
    assert data["version"] == "1.0.0"
    assert data["database"] == "connected"


def test_initial_dashboard_metrics_empty_state():
    """Verify initial metrics honestly report zero tasks and null utilization when unsimulated."""
    response = client.get("/api/dashboard/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 0
    assert data["allocated_tasks"] == 0
    assert data["unallocated_tasks"] == 0
    # Crucial rule: Never invent performance metrics
    assert data["has_simulations"] is False
    assert data["avg_server_utilization"] is None
    assert data["latest_makespan"] is None
