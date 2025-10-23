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
            start_date = start.strftime("%Y-%m-%d")
            end_date = end.strftime("%Y-%m-%d")

        # Fetch data from yfinance
        df = yf.download(
            ticker,
            start=start_date,
            end=end_date,
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