"""
Pydantic Schemas for Request/Response validation in CloudRoute AI.
Ensures strong typing, strict input boundary validation, and transparent serialization.
Uses Pydantic V2 ConfigDict and field validators.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="API operational status")
    service: str = Field(default="CloudRoute AI Backend")
    version: str = Field(default="1.0.0")
    timestamp: datetime = Field(default_factory=utc_now)
    database: str = Field(default="connected", description="Database health status")


class VirtualServerBase(BaseModel):
    name: str
    cpu_cores: int = Field(ge=1, default=4)
    ram_gb: float = Field(gt=0, default=8.0)
    processing_power_mips: float = Field(gt=0, default=1000.0)
    status: str = "IDLE"


class VirtualServerCreate(VirtualServerBase):
    pass


class VirtualServerResponse(VirtualServerBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TaskWorkloadBase(BaseModel):
    task_name: str
    instruction_length_mi: float = Field(gt=0, default=500.0)
    required_ram_gb: float = Field(gt=0, default=1.0)
    priority: int = Field(ge=1, le=5, default=1)
    status: str = "PENDING"


class TaskWorkloadCreate(TaskWorkloadBase):
    pass


class TaskWorkloadResponse(TaskWorkloadBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SimulationRunResponse(BaseModel):
    id: int
    algorithm_name: str
    total_tasks: int
    allocated_tasks: int
    unallocated_tasks: int
    makespan_seconds: float
    avg_cpu_utilization: float
    execution_time_ms: float
    timestamp: datetime
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class DashboardMetricsResponse(BaseModel):
    total_virtual_servers: int = 0
    total_tasks: int = 0
    allocated_tasks: int = 0
    unallocated_tasks: int = 0
    avg_server_utilization: Optional[float] = None
    latest_makespan: Optional[float] = None
    has_simulations: bool = False


# =========================================================================
# Workload Input and Simulation Engine Schemas (Prompt 2)
# =========================================================================

class ServerInputItem(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, description="Virtual server identifier")
    capacity: float = Field(..., gt=0, description="Processing capacity in compatible resource units (e.g., CU / MIPS)")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Server name cannot be empty or whitespace.")
        return stripped

    @field_validator("capacity")
    @classmethod
    def validate_capacity(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Server processing capacity must be strictly greater than zero.")
        return round(float(v), 2)


class TaskInputItem(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, description="Task workload identifier")
    requirement: float = Field(..., gt=0, description="Processing requirement in compatible resource units")
    priority: Literal["Low", "Medium", "High", "low", "medium", "high"] = Field(
        default="Medium", description="Task scheduling priority"
    )
    arrival_time: float = Field(default=0.0, ge=0, description="Task arrival timestamp in seconds")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Task name cannot be empty or whitespace.")
        return stripped

    @field_validator("requirement")
    @classmethod
    def validate_requirement(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Task processing requirement must be strictly greater than zero.")
        return round(float(v), 2)

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        return v.strip().capitalize()

    @field_validator("arrival_time")
    @classmethod
    def validate_arrival_time(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Task arrival time cannot be negative.")
        return round(float(v), 2)


class SimulationRequest(BaseModel):
    algorithm: str = Field(
        default="round_robin",
        description="Scheduling algorithm: 'round_robin', 'priority', 'best_fit', 'least_loaded', or 'all'"
    )
    servers: List[ServerInputItem] = Field(..., min_length=1, description="List of virtual servers")
    tasks: List[TaskInputItem] = Field(..., min_length=1, description="List of workload tasks to schedule")


class TaskResultItem(BaseModel):
    task_id: str
    task_name: str
    priority: str
    requirement: float
    arrival_time: float
    assigned_server: Optional[str] = None
    assigned_server_id: Optional[str] = None
    start_time: Optional[float] = None
    completion_time: Optional[float] = None
    execution_duration: Optional[float] = None
    waiting_time: Optional[float] = None
    status: str  # "Allocated" or "Unallocated"
    reason: Optional[str] = None


class ServerResultItem(BaseModel):
    server_id: str
    name: str
    total_capacity: float
    used_capacity: float
    remaining_capacity: float
    utilization_percentage: float
    assigned_tasks: List[str]


class SingleAlgorithmResult(BaseModel):
    algorithm_key: str
    algorithm_name: str
    total_tasks: int
    allocated_tasks: int
    unallocated_tasks: int
    makespan_seconds: float
    avg_server_utilization: float
    avg_waiting_time: float
    load_imbalance: float = 0.0
    avg_execution_duration: float
    execution_time_ms: float
    capacity_explanation: str
    tasks: List[TaskResultItem]
    servers: List[ServerResultItem]


class ComparisonSummaryItem(BaseModel):
    algorithm_key: str
    algorithm_name: str
    makespan_seconds: float
    avg_server_utilization: float
    avg_waiting_time: float
    load_imbalance: float = 0.0
    allocated_tasks: int
    unallocated_tasks: int
    execution_time_ms: float


class ComparisonRequest(BaseModel):
    servers: List[ServerInputItem] = Field(..., min_length=1, description="List of virtual servers")
    tasks: List[TaskInputItem] = Field(..., min_length=1, description="List of workload tasks to schedule")


class SimulationResponse(BaseModel):
    simulation_id: Optional[str] = None
    mode: str  # "single" or "comparison"
    result: Optional[SingleAlgorithmResult] = None
    algorithms: Optional[Dict[str, SingleAlgorithmResult]] = None
    summary: Optional[List[ComparisonSummaryItem]] = None
    capacity_explanation: str


class SimulationHistorySummary(BaseModel):
    id: int
    simulation_id: str
    algorithm_name: str
    algorithm_key: Optional[str] = None
    total_tasks: int
    allocated_tasks: int
    unallocated_tasks: int
    makespan_seconds: float
    avg_server_utilization: float
    avg_waiting_time: float = 0.0
    load_imbalance: float = 0.0
    execution_time_ms: float
    timestamp: datetime
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class SimulationHistoryDetail(BaseModel):
    id: int
    simulation_id: str
    timestamp: datetime
    algorithm_name: str
    algorithm_key: Optional[str] = None
    workload_config: Optional[Dict[str, Any]] = None
    server_results: Optional[List[Dict[str, Any]]] = None
    task_results: Optional[List[Dict[str, Any]]] = None
    metrics: Optional[Dict[str, Any]] = None
    metrics_summary: Optional[Any] = None
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class DeleteHistoryResponse(BaseModel):
    message: str
    deleted_id: str

