"""
CloudRoute AI — Main FastAPI Application Entrypoint.
Provides RESTful APIs for simulating virtual cloud resource allocation,
workload distribution, and algorithm performance evaluation.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base, init_db
from .api.routes import api_router

# Initialize and migrate SQLite database tables automatically
init_db()

app = FastAPI(
    title="CloudRoute AI API",
    description="Intelligent Cloud Resource Allocation and Workload Optimization System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local React/Vite development server
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router)


@app.get("/")
def root():
    """Root redirect message pointing to API documentation."""
    return {
        "project": "CloudRoute AI",
        "description": "Intelligent Cloud Resource Allocation and Workload Optimization System",
        "documentation": "/docs",
        "health_check": "/api/health"
    }
