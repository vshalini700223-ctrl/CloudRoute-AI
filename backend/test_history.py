"""
CloudRoute AI — Comprehensive Tests for Simulation History, Comparison, and Metrics.

Validates:
1. POST /api/simulate persists simulation to SQLite with all metrics (makespan, waiting time, load imbalance)
2. POST /api/compare runs all 4 algorithms against identical workload and saves comparison audit record
3. GET /api/history returns ordered summaries
4. GET /api/history/{simulation_id} returns complete workload configuration and schedule details
5. GET /api/history/{simulation_id} returns 404 for non-existent IDs
6. DELETE /api/history/{simulation_id} removes record and returns 200
7. DELETE /api/history/{simulation_id} returns 404 when deleting non-existent ID
8. Verification that load_imbalance never raises DivisionByZero
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.simulator import get_default_sample_workload

client = TestClient(app)


def test_history_empty_state():
    """Initial history should be empty in an isolated test environment."""
    response = client.get("/api/history")
    assert response.status_code == 200
    assert response.json() == []


def test_simulate_persists_to_history_and_calculates_metrics():
    """POST /api/simulate should run algorithm, calculate all metrics, and save to SQLite."""
    sample = get_default_sample_workload()
    payload = {
        "algorithm": "round_robin",
        "servers": sample["servers"],
        "tasks": sample["tasks"]
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 200
    sim_data = response.json()
    assert "simulation_id" in sim_data
    sim_id = sim_data["simulation_id"]

    # Verify metrics presence
    res = sim_data["result"]
    assert res["total_tasks"] == 6
    assert res["allocated_tasks"] > 0
    assert res["makespan_seconds"] > 0
    assert "avg_waiting_time" in res
    assert "load_imbalance" in res
    assert isinstance(res["load_imbalance"], float)

    # Verify GET /api/history includes this run
    history_res = client.get("/api/history")
    assert history_res.status_code == 200
    history_list = history_res.json()
    assert len(history_list) >= 1
    matching = [h for h in history_list if h["simulation_id"] == sim_id]
    assert len(matching) == 1
    assert matching[0]["algorithm_name"] == "Round Robin"
    assert matching[0]["total_tasks"] == 6
    assert matching[0]["load_imbalance"] >= 0.0


def test_compare_endpoint_runs_all_four_algorithms():
    """POST /api/compare runs Round Robin, Priority, Best Fit, and Least Loaded on identical input."""
    sample = get_default_sample_workload()
    payload = {
        "servers": sample["servers"],
        "tasks": sample["tasks"]
    }
    response = client.post("/api/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "comparison"
    assert "round_robin" in data["algorithms"]
    assert "priority" in data["algorithms"]
    assert "best_fit" in data["algorithms"]
    assert "least_loaded" in data["algorithms"]

    # Check comparison summary metrics
    summary = data["summary"]
    assert len(summary) == 4
    for item in summary:
        assert item["makespan_seconds"] > 0
        assert "load_imbalance" in item
        assert "avg_waiting_time" in item
        assert "avg_server_utilization" in item

    # Check comparison history record exists
    cmp_id = data["simulation_id"]
    detail_res = client.get(f"/api/history/{cmp_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["simulation_id"] == cmp_id
    assert detail["workload_config"] is not None
    assert len(detail["workload_config"]["servers"]) == len(sample["servers"])


def test_get_history_detail_and_missing_id_404():
    """GET /api/history/{id} returns details for existing run and 404 for unknown ID."""
    # 404 test for non-existent ID
    res_404 = client.get("/api/history/non-existent-simulation-id")
    assert res_404.status_code == 404
    assert "not found" in res_404.json()["detail"].lower()

    # Create a simulation
    sample = get_default_sample_workload()
    payload = {
        "algorithm": "best_fit",
        "servers": sample["servers"][:2],
        "tasks": sample["tasks"][:3]
    }
    sim_res = client.post("/api/simulate", json=payload)
    sim_id = sim_res.json()["simulation_id"]

    # Retrieve full details
    detail_res = client.get(f"/api/history/{sim_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["simulation_id"] == sim_id
    assert detail["algorithm_name"] == "Best Fit"
    assert "server_results" in detail
    assert "task_results" in detail
    assert "metrics" in detail
    assert detail["metrics"]["total_tasks"] == 3


def test_delete_history_record_success_and_404():
    """DELETE /api/history/{id} deletes the record and handles 404 properly."""
    # 404 test on unknown ID
    del_404 = client.delete("/api/history/unknown-sim-id-xyz")
    assert del_404.status_code == 404

    # Create a simulation
    sample = get_default_sample_workload()
    payload = {
        "algorithm": "least_loaded",
        "servers": sample["servers"],
        "tasks": sample["tasks"][:2]
    }
    sim_res = client.post("/api/simulate", json=payload)
    sim_id = sim_res.json()["simulation_id"]

    # Delete it
    del_res = client.delete(f"/api/history/{sim_id}")
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert "deleted successfully" in del_data["message"]
    assert del_data["deleted_id"] == sim_id

    # Verify subsequent GET returns 404
    get_again = client.get(f"/api/history/{sim_id}")
    assert get_again.status_code == 404


def test_metrics_division_by_zero_protection():
    """Ensures load imbalance and average waiting times do not divide by zero on edge cases."""
    # 1 server, 1 task
    payload = {
        "algorithm": "round_robin",
        "servers": [{"name": "Single-Node", "capacity": 1000.0}],
        "tasks": [{"name": "T1", "requirement": 100.0, "priority": "High", "arrival_time": 0.0}]
    }
    res = client.post("/api/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()["result"]
    # Single server has T_max == T_min, so load imbalance is 0.0
    assert data["load_imbalance"] == 0.0
    assert data["avg_waiting_time"] == 0.0
