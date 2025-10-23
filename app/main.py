"""Main FastAPI application module for FinInsight.

This module initializes the FastAPI application and includes all routers.
It provides the core API functionality and health check endpoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.logging_config import setup_logging
from app.routers import data, jobs
from app.config import settings

setup_logging()

app = FastAPI(
    title="FinInsight",
    description="Financial data and analysis API with backtesting capabilities",
    version="0.1.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.ALLOWED_ORIGINS.split(",")
        if origin.strip()
    ] or ["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(data.router)
app.include_router(jobs.router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify API is running."""
    return {
        "status": "ok",
        "services": {
            "api": "up",
            "redis": "up",  # We'll enhance this later with actual checks
            "celery": "up"
        }
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "FinInsight API is running",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }
