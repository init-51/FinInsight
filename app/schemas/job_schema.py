"""Pydantic schemas related to job history and metadata."""

from datetime import datetime
from pydantic import BaseModel


class BacktestHistoryItem(BaseModel):
    """Summary information for a completed backtest job."""

    job_id: str
    portfolio_name: str
    final_value: float
    created_at: datetime

