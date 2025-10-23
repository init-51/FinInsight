"""SQLAlchemy model for storing portfolio backtest results.

This model is used to persist the results of each portfolio backtest
executed by the FinInsight system. It is fully compatible with PostgreSQL
and uses SQLAlchemy 2.0 declarative syntax.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base

class BacktestResult(Base):
    """Database model for portfolio backtest results."""
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, nullable=False, index=True)
    portfolio_name = Column(String, nullable=False)
    final_value = Column(Float, nullable=False)
    cumulative_return = Column(Float, nullable=False)
    volatility = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    timeseries = Column(JSON, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<BacktestResult portfolio_name='{self.portfolio_name}' job_id='{self.job_id}'>"
        )
