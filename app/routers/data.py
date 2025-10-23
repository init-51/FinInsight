"""Financial data router for fetching stock price information.

This module provides endpoints for retrieving historical stock price data
using the yfinance library. It supports fetching data for specific date
ranges or defaulting to the last 90 days.
"""

from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import yfinance as yf
import pandas as pd

router = APIRouter(
    prefix="/data",
    tags=["Financial Data"],
    responses={404: {"description": "Not found"}},
)


class StockPrice(BaseModel):
    """Model for stock price data point."""
    date: str
    close: float


def _parse_date(value: str) -> datetime:
    """Parse incoming date strings in multiple common formats."""
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(
        f"Invalid date format: {value}. Expected YYYY-MM-DD or MM/DD/YYYY"
    )


@router.get(
    "/price/{ticker}",
    response_model=List[StockPrice],
    summary="Get historical stock prices",
    description="Retrieve historical closing prices for a given stock ticker. "
                "If start_date and end_date are not provided, returns the last 90 days."
)
async def get_stock_price(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[StockPrice]:
    """Fetch historical stock prices for a given ticker.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOG')
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)

    Returns:
        List of StockPrice objects containing date and closing price

    Raises:
        HTTPException: If ticker is invalid or data cannot be fetched
    """
    try:
        # Set default date range if not provided
        if not start_date or not end_date:
            end = datetime.now()
            start = end - timedelta(days=90)
        else:
            start = _parse_date(start_date)
            end = _parse_date(end_date)

        start_date_str = start.strftime("%Y-%m-%d")
        end_date_str = end.strftime("%Y-%m-%d")

        df = yf.download(
            ticker,
            start=start_date_str,
            end=end_date_str,
            progress=False
        )

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail=f"No data available for ticker {ticker}"
            )

        # Convert to list of StockPrice objects
        result = [
            StockPrice(
                date=date.strftime("%Y-%m-%d"),
                close=round(float(row["Close"]), 2)
            )
            for date, row in df.iterrows()
        ]

        return result

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to fetch data for ticker {ticker}: {str(e)}"
        )