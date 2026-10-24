"""
SQLAlchemy ORM Models for CloudRoute AI.
Defines simulated virtual cloud servers, incoming computational tasks,
and simulation run records for workload allocation algorithms.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from .database import Base


def utc_now():
    return datetime.now(timezone.utc)


class VirtualServer(Base):
    """
    Represents a simulated virtual cloud machine.
    No physical hardware needed; metrics represent virtual compute capacity.
    """
    __tablename__ = "virtual_servers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    cpu_cores = Column(Integer, nullable=False, default=4)
    ram_gb = Column(Float, nullable=False, default=8.0)
    processing_power_mips = Column(Float, nullable=False, default=1000.0)  # Million Instructions Per Second
    status = Column(String(20), default="IDLE")  # IDLE, BUSY, OVERLOADED, OFFLINE
    created_at = Column(DateTime, default=utc_now)

    allocations = relationship("SimulationAllocation", back_populates="server")


class TaskWorkload(Base):
    """
    Represents a computational task to be scheduled onto virtual servers.
    """
    __tablename__ = "task_workloads"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(100), nullable=False)
    instruction_length_mi = Column(Float, nullable=False, default=500.0)  # Million Instructions
    required_ram_gb = Column(Float, nullable=False, default=1.0)
    priority = Column(Integer, default=1)  # 1 (Low) to 5 (Critical)
    status = Column(String(20), default="PENDING")  # PENDING, ALLOCATED, COMPLETED
    created_at = Column(DateTime, default=utc_now)

    allocations = relationship("SimulationAllocation", back_populates="task")


class SimulationRun(Base):
    """
    Stores metrics, submitted workloads, and full allocation results
    for each execution of a scheduling algorithm.
    """
    __tablename__ = "simulation_runs"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(String(64), unique=True, index=True, nullable=True)
    algorithm_name = Column(String(50), nullable=False)
    algorithm_key = Column(String(50), nullable=True, default="round_robin")
    total_tasks = Column(Integer, default=0)
    allocated_tasks = Column(Integer, default=0)
    unallocated_tasks = Column(Integer, default=0)
    makespan_seconds = Column(Float, default=0.0)
    avg_cpu_utilization = Column(Float, default=0.0)
    avg_waiting_time = Column(Float, default=0.0)
    load_imbalance = Column(Float, default=0.0)
    execution_time_ms = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=utc_now)
    notes = Column(Text, nullable=True)

    # Structured JSON fields storing configurations and results
    workload_config = Column(JSON, nullable=True)
    server_results = Column(JSON, nullable=True)
    task_results = Column(JSON, nullable=True)
    metrics_summary = Column(JSON, nullable=True)

    allocations = relationship("SimulationAllocation", back_populates="simulation", cascade="all, delete-orphan")

    def to_summary_dict(self):
        sim_code = self.simulation_id or f"sim-{self.id}"
        return {
            "id": self.id,
            "simulation_id": sim_code,
            "algorithm_name": self.algorithm_name,
            "algorithm_key": self.algorithm_key or "round_robin",
            "total_tasks": self.total_tasks or 0,
            "allocated_tasks": self.allocated_tasks or 0,
            "unallocated_tasks": self.unallocated_tasks or 0,
            "makespan_seconds": round(float(self.makespan_seconds or 0.0), 2),
            "avg_server_utilization": round(float(self.avg_cpu_utilization or 0.0), 2),
            "avg_waiting_time": round(float(self.avg_waiting_time or 0.0), 2),
            "load_imbalance": round(float(self.load_imbalance or 0.0), 4),
            "execution_time_ms": round(float(self.execution_time_ms or 0.0), 3),
            "timestamp": self.timestamp,
            "notes": self.notes,
        }

    def to_detail_dict(self):
        res = self.to_summary_dict()
        res["workload_config"] = self.workload_config or {}
        res["server_results"] = self.server_results or []
        res["task_results"] = self.task_results or []
        res["metrics"] = {
            "total_tasks": res["total_tasks"],
            "allocated_tasks": res["allocated_tasks"],
            "unallocated_tasks": res["unallocated_tasks"],
            "makespan_seconds": res["makespan_seconds"],
            "avg_server_utilization": res["avg_server_utilization"],
            "avg_waiting_time": res["avg_waiting_time"],
            "load_imbalance": res["load_imbalance"],
            "execution_time_ms": res["execution_time_ms"],
        }
        res["metrics_summary"] = self.metrics_summary
        return res


class SimulationAllocation(Base):
    """
    Mapping of which task was scheduled on which virtual server in a simulation run.
    """
    __tablename__ = "simulation_allocations"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulation_runs.id"), nullable=False)
    server_id = Column(Integer, ForeignKey("virtual_servers.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("task_workloads.id"), nullable=False)
    completion_time_seconds = Column(Float, default=0.0)

    simulation = relationship("SimulationRun", back_populates="allocations")
    server = relationship("VirtualServer", back_populates="allocations")
    task = relationship("TaskWorkload", back_populates="allocations")
