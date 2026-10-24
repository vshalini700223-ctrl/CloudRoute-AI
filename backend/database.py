"""
Database configuration for CloudRoute AI.
Uses SQLite for local, serverless data persistence without any paid cloud accounts.
"""

from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Resolve absolute path to cloudroute.db in the backend directory
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "cloudroute.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

# connect_args={"check_same_thread": False} is required for SQLite in multi-threaded FastAPI apps
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency provider that creates a fresh database session for each request
    and safely closes it when the request is complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(target_engine=None):
    """
    Initializes database tables and performs lightweight migrations
    to ensure all simulation history and metric columns exist.
    """
    active_engine = target_engine or engine
    Base.metadata.create_all(bind=active_engine)

    # Lightweight column migration for existing SQLite databases
    with active_engine.connect() as conn:
        try:
            result = conn.execute(text("PRAGMA table_info(simulation_runs)"))
            existing_cols = {row[1] for row in result.fetchall()}

            new_columns = [
                ("simulation_id", "VARCHAR(64)"),
                ("algorithm_key", "VARCHAR(50) DEFAULT 'round_robin'"),
                ("avg_waiting_time", "FLOAT DEFAULT 0.0"),
                ("load_imbalance", "FLOAT DEFAULT 0.0"),
                ("workload_config", "TEXT"),
                ("server_results", "TEXT"),
                ("task_results", "TEXT"),
                ("metrics_summary", "TEXT"),
            ]
            for col_name, col_def in new_columns:
                if col_name not in existing_cols:
                    conn.execute(text(f"ALTER TABLE simulation_runs ADD COLUMN {col_name} {col_def}"))
            conn.commit()
        except Exception:
            # If table doesn't exist yet or engine is in-memory fresh, create_all already created it
            pass
