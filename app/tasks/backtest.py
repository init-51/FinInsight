"""Backtest tasks module for portfolio analysis.

This module contains a Celery task for running portfolio backtests.
The task downloads historical prices for the portfolio assets using
`yfinance`, computes daily returns, aggregates them according to the
provided weights, and returns portfolio-level metrics and a daily
time series of cumulative portfolio value.
"""

from typing import Dict, Any, List

import numpy as np
import pandas as pd
import yfinance as yf
from celery import Task
from celery.utils.log import get_task_logger

from app.celery_app import celery_app
# Import DB session and model after Celery app is defined
from app.database import SessionLocal
from app.models.backtest_result import BacktestResult

# Configure module logger using Celery's logger
logger = get_task_logger(__name__)


class BacktestTask(Task):
    """Custom Celery Task for backtests to provide failure logging."""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.exception(f"Task {task_id} failed: {exc!r}\n{einfo}")
        super().on_failure(exc, task_id, args, kwargs, einfo)


def _safe_download(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Download OHLCV data for a single ticker and return DataFrame.

    Returns an empty DataFrame if download fails or no data found.
    """
    try:
        # Note: Added auto_adjust=True explicitly based on FutureWarning
        df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
        if df is None or df.empty:
            logger.warning("No data returned for ticker %s", ticker)
            return pd.DataFrame()
        # Ensure index is datetime
        df.index = pd.to_datetime(df.index)
        return df
    except Exception:
        logger.exception("Failed to download data for %s", ticker)
        return pd.DataFrame()


@celery_app.task(bind=True, base=BacktestTask, name="app.tasks.backtest.run_backtest")
def run_backtest(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
    """Run a simple portfolio backtest.

    Expected portfolio structure:
    {
        "name": "My Portfolio",
        "initial_value": 10000,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "assets": [
            {"ticker": "AAPL", "weight": 0.5},
            {"ticker": "GOOGL", "weight": 0.5}
        ]
    }

    Returns a JSON-serializable dict with portfolio metrics and timeseries.
    """
    job_id = getattr(self.request, "id", "unknown")
    try:
        logger.info(f"Job {job_id}: starting backtest for portfolio '{portfolio.get('name')}'")

        name = portfolio.get("name", "portfolio")
        initial_value = float(portfolio.get("initial_value", 10000.0))
        start_date = portfolio.get("start_date")
        end_date = portfolio.get("end_date")

        assets = portfolio.get("assets", [])
        if not assets:
            raise ValueError("Portfolio must include at least one asset")

        logger.info(f"Job {job_id}: validating and normalizing asset weights")
        # Build dict of ticker -> weight
        weights: Dict[str, float] = {}
        for a in assets:
            ticker = a.get("ticker")
            weight = float(a.get("weight", 0))
            if not ticker or weight < 0: # Ensure weight is non-negative
                logger.warning(f"Job {job_id}: Skipping invalid asset entry: {a}")
                continue
            weights[ticker.upper()] = weight

        if not weights:
            raise ValueError("No valid tickers provided in portfolio.assets")

        # Normalize weights
        total_w = sum(weights.values())
        if total_w <= 1e-9: # Use tolerance for floating point comparison
            raise ValueError("Sum of weights must be positive")
        for t in list(weights.keys()):
            weights[t] = weights[t] / total_w

        tickers = list(weights.keys())
        logger.info(f"Job {job_id}: starting data fetch for tickers {tickers}")

        # Download data for each ticker
        price_frames: Dict[str, pd.Series] = {} # Change DataFrame to Series
        for t in tickers:
            df = _safe_download(t, start_date, end_date)
            if df.empty:
                logger.warning(f"Job {job_id}: Skipping ticker with no data: {t}")
                weights.pop(t, None) # Remove ticker if no data
                continue

            # yfinance auto_adjust=True uses 'Close' which is adjusted
            if "Close" in df.columns:
                price = df["Close"].copy()
                # --- THIS IS THE FIX ---
                price.name = t # Set the name attribute of the Series
                # -----------------------
                price_frames[t] = price
            else:
                logger.warning(f"Job {job_id}: No close prices for {t}, skipping")
                weights.pop(t, None) # Remove ticker if no data
                continue

        if not price_frames:
            raise ValueError("No price data available for any tickers")

        # Renormalize weights if some tickers were skipped
        tickers = list(price_frames.keys()) # Update tickers list
        final_weights = {t: weights[t] for t in tickers}
        total_w = sum(final_weights.values())
        if total_w <= 1e-9:
             raise ValueError("Sum of weights became zero after removing tickers with no data")
        for t in tickers:
            final_weights[t] = final_weights[t] / total_w


        logger.info(f"Job {job_id}: data fetch complete, beginning calculations")
        # Merge price series into single DataFrame aligned by date
        price_df = pd.concat(price_frames.values(), axis=1, join="outer")
        price_df.sort_index(inplace=True)

        # Forward-fill and drop rows that still contain NaNs
        price_df = price_df.ffill().dropna(how="any") # Change 'all' to 'any' for stricter cleaning

        if price_df.empty:
             raise ValueError("No common date range found for provided tickers after cleaning.")

        # Compute daily returns per asset
        returns_df = price_df.pct_change().dropna(how="all")
        if returns_df.empty:
            raise ValueError("Not enough price data to compute returns")

        # Ensure weights align with columns present after potential drops/cleaning
        aligned_weights = np.array([final_weights[col] for col in returns_df.columns])

        # Compute portfolio daily returns: dot product of returns and weights
        portfolio_returns = returns_df.fillna(0).dot(aligned_weights)

        logger.info(f"Job {job_id}: calculations complete, building results")
        # Metrics
        cumulative_return = float((1 + portfolio_returns).prod() - 1)
        mean_ret = float(portfolio_returns.mean())
        std_ret = float(portfolio_returns.std(ddof=1)) # Use sample std dev (ddof=1)
        if std_ret < 1e-9: # Handle zero volatility case
            volatility = 0.0
            sharpe_ratio = float("inf") if mean_ret > 0 else float("-inf") if mean_ret < 0 else float("nan")
        else:
            volatility = float(std_ret * (252 ** 0.5))
            # Use a small risk-free rate annualized (2%) converted to daily
            risk_free_daily = 0.02 / 252
            sharpe_ratio = float((mean_ret - risk_free_daily) / std_ret * (252 ** 0.5)) # Annualize Sharpe

        final_value = float(initial_value * (1 + cumulative_return))

        # Build timeseries of cumulative portfolio value
        cumulative_value = (1 + portfolio_returns).cumprod() * initial_value
        timeseries: List[Dict[str, Any]] = []
        # Use .items() for Series iteration
        for idx, val in cumulative_value.items():
            # Check if index is Timestamp before formatting
            if isinstance(idx, pd.Timestamp):
                 date_str = idx.strftime("%Y-%m-%d")
                 timeseries.append({"date": date_str, "value": round(float(val), 2)})

        result = {
            "portfolio": name,
            "final_value": round(final_value, 2),
            "cumulative_return": round(cumulative_return, 6),
            "volatility": round(volatility, 6),
            "sharpe_ratio": round(sharpe_ratio, 6) if not np.isnan(sharpe_ratio) and np.isfinite(sharpe_ratio) else None, # Handle NaN/Inf Sharpe
            "timeseries": timeseries,
        }

        # Persist result to PostgreSQL
        session = SessionLocal()
        logger.info(f"Job {job_id}: attempting to persist results to database")
        try:
            db_obj = BacktestResult(
                job_id=job_id, # Use job_id captured at the start
                portfolio_name=name,
                final_value=result["final_value"],
                cumulative_return=result["cumulative_return"],
                volatility=result["volatility"],
                sharpe_ratio=result["sharpe_ratio"],
                timeseries=result["timeseries"] # Store the list of dicts directly
            )
            session.add(db_obj)
            session.commit()
            logger.info(f"Job {job_id}: Results saved successfully")
        except Exception as db_exc:
            session.rollback()
            # Log the exception specifically for DB errors
            logger.exception(f"Job {job_id}: Failed to save backtest result: {db_exc}")
            # Reraise to mark the task as failed if DB save is critical
            raise
        finally:
            session.close()

        logger.info(f"Job {job_id}: completed backtest for '{name}'")
        return result

    except Exception as exc:
        # Log the full traceback using logger.exception
        logger.exception(f"Job {job_id}: backtest failed")
        # Update Celery state with error message for frontend polling
        try:
            self.update_state(
                state="FAILURE",
                meta={
                    "exc_type": exc.__class__.__name__,
                    "exc_module": exc.__class__.__module__,
                    "exc_message": [str(exc)],
                    "error": str(exc),
                },
            )
        except Exception as state_exc:
            logger.exception(f"Job {job_id}: Failed even to update Celery task state: {state_exc}")
        # Reraise the exception so Celery marks the task as failed internally
        raise
