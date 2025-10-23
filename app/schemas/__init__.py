# Pydantic schemas package for FinInsight
from pydantic import BaseModel

from .job_schema import BacktestHistoryItem


class HealthCheck(BaseModel):
    status: str = "ok"


__all__ = ["HealthCheck", "BacktestHistoryItem"]
