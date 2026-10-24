"""
CloudRoute AI — Unit Tests for Scheduling Algorithms and Simulation Engine.

Validates:
1. Round Robin cyclicity & capacity compliance
2. Priority Scheduling ordering (High > Medium > Low) & deterministic tie-breaking
3. Best Fit tightest-slack placement
4. Least Loaded utilization balancing
5. Strict capacity limit enforcement (never exceed server capacity)
6. Unallocated tasks and explanatory reasons
7. Input validation boundaries (rejecting negative, zero, or missing values)
8. Deterministic repeatability
9. Integration with SimulationEngine and FastAPI endpoint
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.scheduler import (
    ServerState,
    schedule_round_robin,
    schedule_priority,
    schedule_best_fit,
    schedule_least_loaded,
    calculate_execution_duration,
)
from app.services.simulator import (
    SimulationEngine,
    validate_simulation_inputs,
    get_default_sample_workload,
)

client = TestClient(app)


# =========================================================================
# Unit Tests: Execution Duration Formula
# =========================================================================

def test_execution_duration_formula():
    """Duration = max(0.05, round((requirement / capacity) * 10.0, 2))"""
    # 500 req on 1000 cap -> (500 / 1000) * 10.0 = 5.0 seconds
    assert calculate_execution_duration(500.0, 1000.0) == 5.0
    # 250 req on 1000 cap -> 2.5 seconds
    assert calculate_execution_duration(250.0, 1000.0) == 2.5
    # Negative/zero capacity raises ValueError
    with pytest.raises(ValueError):
        calculate_execution_duration(100.0, 0.0)
    with pytest.raises(ValueError):
        calculate_execution_duration(100.0, -500.0)


# =========================================================================
# Unit Tests: Round Robin
# =========================================================================

def test_round_robin_distribution():
    """Verifies Round Robin assigns tasks cyclically among eligible servers."""
    servers = [
        ServerState("s1", "Server-A", capacity=1000.0),
        ServerState("s2", "Server-B", capacity=1000.0),
    ]
    tasks = [
        {"id": "t1", "name": "Task-1", "requirement": 200.0, "priority": "Medium", "arrival_time": 0.0},
        {"id": "t2", "name": "Task-2", "requirement": 200.0, "priority": "Medium", "arrival_time": 0.0},
        {"id": "t3", "name": "Task-3", "requirement": 200.0, "priority": "Medium", "arrival_time": 0.0},
    ]

    results, final_servers = schedule_round_robin(servers, tasks)

    assert results[0]["assigned_server"] == "Server-A"
    assert results[1]["assigned_server"] == "Server-B"
    assert results[2]["assigned_server"] == "Server-A"
    assert all(r["status"] == "Allocated" for r in results)
    assert final_servers[0].used_capacity == 400.0
    assert final_servers[1].used_capacity == 200.0


# =========================================================================
# Unit Tests: Priority Scheduling
# =========================================================================

def test_priority_scheduling_ordering():
    """Verifies that High priority tasks are allocated first, before Medium and Low."""
    servers = [
        ServerState("s1", "Server-Only", capacity=500.0)  # Can only fit 500 total
    ]
    tasks = [
        {"id": "t_low", "name": "Task-Low", "requirement": 300.0, "priority": "Low", "arrival_time": 0.0},
        {"id": "t_high", "name": "Task-High", "requirement": 400.0, "priority": "High", "arrival_time": 0.0},
    ]

    results, final_servers = schedule_priority(servers, tasks)

    # Task-High must be allocated, Task-Low should become Unallocated due to exhausted capacity
    high_res = next(r for r in results if r["task_name"] == "Task-High")
    low_res = next(r for r in results if r["task_name"] == "Task-Low")

    assert high_res["status"] == "Allocated"
    assert high_res["assigned_server"] == "Server-Only"
    assert low_res["status"] == "Unallocated"
    assert "Insufficient capacity" in low_res["reason"]
    assert final_servers[0].used_capacity == 400.0
    assert final_servers[0].remaining_capacity == 100.0


# =========================================================================
# Unit Tests: Best Fit
# =========================================================================

def test_best_fit_selection():
    """Verifies Best Fit chooses the server with the smallest remaining capacity that fits the task."""
    servers = [
        ServerState("s1", "Server-Large", capacity=1000.0),
        ServerState("s2", "Server-Small", capacity=300.0),
    ]
    tasks = [
        {"id": "t1", "name": "Task-Tight", "requirement": 250.0, "priority": "Medium", "arrival_time": 0.0},
    ]

    results, _ = schedule_best_fit(servers, tasks)

    # Server-Small has 300 cap (slack = 50), Server-Large has 1000 cap (slack = 750)
    # Best fit must pick Server-Small
    assert results[0]["assigned_server"] == "Server-Small"
    assert results[0]["status"] == "Allocated"


# =========================================================================
# Unit Tests: Least Loaded
# =========================================================================

def test_least_loaded_selection():
    """Verifies Least Loaded assigns tasks to the server with lowest normalized utilization."""
    servers = [
        ServerState("s1", "Server-A", capacity=1000.0),  # 0% loaded
        ServerState("s2", "Server-B", capacity=1000.0),  # will become 50% loaded
    ]
    # Manually load Server-B
    servers[1].used_capacity = 500.0

    tasks = [
        {"id": "t1", "name": "Task-Test", "requirement": 200.0, "priority": "Medium", "arrival_time": 0.0},
    ]

    results, _ = schedule_least_loaded(servers, tasks)

    # Server-A is 0% loaded vs Server-B at 50% loaded -> must pick Server-A
    assert results[0]["assigned_server"] == "Server-A"
    assert results[0]["status"] == "Allocated"


# =========================================================================
# Unit Tests: Capacity Limits & Unallocated Tasks
# =========================================================================

def test_capacity_limit_never_exceeded():
    """Verifies that no server ever accepts tasks beyond its total capacity."""
    servers = [
        ServerState("s1", "Server-Capped", capacity=500.0),
    ]
    tasks = [
        {"id": "t1", "name": "Task-1", "requirement": 300.0, "priority": "Medium", "arrival_time": 0.0},
        {"id": "t2", "name": "Task-2", "requirement": 300.0, "priority": "Medium", "arrival_time": 0.0},
    ]

    results, final_servers = schedule_round_robin(servers, tasks)

    assert results[0]["status"] == "Allocated"
    assert results[1]["status"] == "Unallocated"
    assert "Insufficient capacity" in results[1]["reason"]
    # Server used capacity must remain exactly 300, not 600
    assert final_servers[0].used_capacity == 300.0
    assert final_servers[0].used_capacity <= final_servers[0].total_capacity


def test_unallocated_task_reason():
    """Verifies impossible assignments are marked Unallocated with descriptive reason."""
    servers = [
        ServerState("s1", "Server-Small", capacity=100.0),
    ]
    tasks = [
        {"id": "t_huge", "name": "Huge-Task", "requirement": 999.0, "priority": "High", "arrival_time": 0.0},
    ]

    results, _ = schedule_best_fit(servers, tasks)

    assert results[0]["status"] == "Unallocated"
    assert results[0]["assigned_server"] is None
    assert results[0]["start_time"] is None
    assert results[0]["completion_time"] is None
    assert "Required: 999.0" in results[0]["reason"]


# =========================================================================
# Unit Tests: Deterministic Repeatability
# =========================================================================

def test_deterministic_repeatability():
    """Verifies that running algorithms multiple times with identical inputs produces identical results."""
    sample = get_default_sample_workload()

    res1 = SimulationEngine.run_single_algorithm("round_robin", sample["servers"], sample["tasks"])
    res2 = SimulationEngine.run_single_algorithm("round_robin", sample["servers"], sample["tasks"])

    assert res1["makespan_seconds"] == res2["makespan_seconds"]
    assert res1["allocated_tasks"] == res2["allocated_tasks"]
    for t1, t2 in zip(res1["tasks"], res2["tasks"]):
        assert t1["assigned_server"] == t2["assigned_server"]
        assert t1["start_time"] == t2["start_time"]
        assert t1["completion_time"] == t2["completion_time"]


# =========================================================================
# Unit Tests: Input Validation Boundaries
# =========================================================================

def test_reject_negative_server_capacity():
    with pytest.raises(ValueError, match="Processing capacity must be greater than zero"):
        validate_simulation_inputs(
            servers_data=[{"name": "Bad-Server", "capacity": -100.0}],
            tasks_data=[{"name": "T1", "requirement": 50.0}]
        )


def test_reject_zero_server_capacity():
    with pytest.raises(ValueError, match="Processing capacity must be greater than zero"):
        validate_simulation_inputs(
            servers_data=[{"name": "Zero-Server", "capacity": 0.0}],
            tasks_data=[{"name": "T1", "requirement": 50.0}]
        )


def test_reject_negative_task_requirement():
    with pytest.raises(ValueError, match="Processing requirement must be greater than zero"):
        validate_simulation_inputs(
            servers_data=[{"name": "S1", "capacity": 1000.0}],
            tasks_data=[{"name": "Bad-Task", "requirement": -50.0}]
        )


def test_reject_empty_names():
    with pytest.raises(ValueError, match="Server name cannot be empty"):
        validate_simulation_inputs(
            servers_data=[{"name": "   ", "capacity": 1000.0}],
            tasks_data=[{"name": "T1", "requirement": 50.0}]
        )
    with pytest.raises(ValueError, match="Task name cannot be empty"):
        validate_simulation_inputs(
            servers_data=[{"name": "S1", "capacity": 1000.0}],
            tasks_data=[{"name": "", "requirement": 50.0}]
        )


def test_reject_negative_arrival_time():
    with pytest.raises(ValueError, match="Arrival time cannot be negative"):
        validate_simulation_inputs(
            servers_data=[{"name": "S1", "capacity": 1000.0}],
            tasks_data=[{"name": "T1", "requirement": 50.0, "arrival_time": -2.0}]
        )


def test_reject_invalid_priority():
    with pytest.raises(ValueError, match="Priority must be 'Low', 'Medium', or 'High'"):
        validate_simulation_inputs(
            servers_data=[{"name": "S1", "capacity": 1000.0}],
            tasks_data=[{"name": "T1", "requirement": 50.0, "priority": "SuperCritical"}]
        )


# =========================================================================
# Integration Tests: FastAPI /api/simulate Endpoint
# =========================================================================

def test_api_simulate_single_endpoint():
    """Tests POST /api/simulate with single algorithm."""
    sample = get_default_sample_workload()
    payload = {
        "algorithm": "best_fit",
        "servers": sample["servers"],
        "tasks": sample["tasks"]
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "single"
    assert data["result"]["algorithm_key"] == "best_fit"
    assert data["result"]["total_tasks"] == 6
    assert data["result"]["allocated_tasks"] > 0
    assert data["result"]["makespan_seconds"] > 0.0
    assert "Resource Capacity vs Execution Duration" in data["capacity_explanation"]


def test_api_simulate_comparison_endpoint():
    """Tests POST /api/simulate with 'all' to compare all four algorithms on identical workloads."""
    sample = get_default_sample_workload()
    payload = {
        "algorithm": "all",
        "servers": sample["servers"],
        "tasks": sample["tasks"]
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "comparison"
    assert "round_robin" in data["algorithms"]
    assert "priority" in data["algorithms"]
    assert "best_fit" in data["algorithms"]
    assert "least_loaded" in data["algorithms"]
    assert len(data["summary"]) == 4


def test_api_simulate_validation_error_response():
    """Tests that POST /api/simulate returns 400 Bad Request with understandable message for invalid inputs."""
    payload = {
        "algorithm": "round_robin",
        "servers": [{"name": "Invalid-Srv", "capacity": -500.0}],
        "tasks": [{"name": "T1", "requirement": 100.0}]
    }
    response = client.post("/api/simulate", json=payload)
    # Pydantic or ValueError returns 400 or 422
    assert response.status_code in [400, 422]
