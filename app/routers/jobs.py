"""Jobs router for managing asynchronous tasks.

This module provides endpoints for submitting backtest jobs and
retrieving their status and results.
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from celery.result import AsyncResult
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.tasks.backtest import run_backtest
from app.database import get_db
from app.models.backtest_result import BacktestResult
from app.schemas.job_schema import BacktestHistoryItem


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
    responses={404: {"description": "Not found"}},
)


class BacktestRequest(BaseModel):
    """Model for backtest job request."""
    portfolio: Dict[str, Any] = Field(
        ...,
        example={
            "initial_value": 10000,
            "assets": ["AAPL", "GOOGL"],
            "weights": [0.6, 0.4],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
    )


class JobResponse(BaseModel):
    """Model for job submission response."""
    job_id: str


class JobStatus(BaseModel):
    """Model for job status response."""
    job_id: str
    status: str
    progress: Optional[float] = None
    error: Optional[str] = None


class JobResult(BaseModel):
    """Model for job result response."""
    job_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post(
    "/backtest",
    response_model=JobResponse,
    summary="Submit a backtest job",
    description="Enqueues a new portfolio backtest task and returns a job ID"
)
async def create_backtest_job(request: BacktestRequest) -> JobResponse:
    """Create a new backtest job."""
    try:
        task = run_backtest.delay(request.portfolio)
        return JobResponse(job_id=task.id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create backtest job: {str(e)}"
        )


@router.get(
    "/status/{job_id}",
    response_model=JobStatus,
    summary="Get job status",
    description="Retrieve the current status of a job"
)
async def get_job_status(job_id: str) -> JobStatus:
    """Get the status of a job by ID."""
    try:
        result = celery_app.AsyncResult(job_id)
        response = JobStatus(
            job_id=job_id,
            status=result.status
        )
        
        if result.failed():
            response.error = str(result.info)
        
        return response
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.get(
    "/results/{job_id}",
    response_model=JobResult,
    summary="Get job results",
    description="Retrieve the results of a completed job"
)
async def get_job_results(job_id: str) -> JobResult:
    """Get the results of a completed job."""
    try:
        result = celery_app.AsyncResult(job_id)
        
        if result.ready():
            if result.successful():
                return JobResult(
                    job_id=job_id,
                    status=result.status,
                    result=result.get()
                )
            else:
                return JobResult(
                    job_id=job_id,
                    status="FAILED",
                    error=str(result.info)
                )
        else:
            return JobResult(
                job_id=job_id,
                status=result.status
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get job results: {str(e)}"
        )


@router.get(
    "/history",
    response_model=List[BacktestHistoryItem],
    summary="List recent backtests",
    description="Retrieve recently completed backtest summaries ordered by most recent first",
)
async def list_backtest_history(
    db: Session = Depends(get_db),
) -> List[BacktestHistoryItem]:
    """Return a list of recent backtest summaries."""
    try:
        records: List[BacktestResult] = (
            db.query(BacktestResult)
            .order_by(BacktestResult.created_at.desc())
            .limit(50)
            .all()
        )
        return [
            BacktestHistoryItem(
                job_id=record.job_id,
                portfolio_name=record.portfolio_name,
                final_value=record.final_value,
                created_at=record.created_at,
            )
            for record in records
        ]
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch backtest history: {exc}",
        )
