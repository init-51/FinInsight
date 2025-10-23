import sys
import types
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.tasks import backtest as backtest_module


@pytest.fixture
def run_backtest(monkeypatch):
    """Provide helper to run the backtest task using a simple dummy task context."""

    dummy_session_records = []

    class DummySession:
        def __init__(self):
            self.added = []
            self.committed = False
            self.rolled_back = False

        def add(self, obj):
            self.added.append(obj)

        def commit(self):
            self.committed = True
            dummy_session_records.append(self)

        def rollback(self):
            self.rolled_back = True

        def close(self):
            pass

    dummy_session = DummySession()

    def session_factory():
        return dummy_session

    monkeypatch.setattr(backtest_module, "SessionLocal", session_factory)

    dummy_task = types.SimpleNamespace(
        request=types.SimpleNamespace(id="test-job"),
        update_state=lambda *args, **kwargs: None,
    )

    bound_func = backtest_module.run_backtest.__wrapped__.__get__(dummy_task, type(dummy_task))

    def _run(portfolio):
        result = bound_func(portfolio)
        return result, dummy_session

    return _run


def _price_series(values):
    """Helper to build a price series with daily frequency."""
    index = pd.date_range("2024-01-01", periods=len(values), freq="D")
    return pd.DataFrame({"Close": values}, index=index)


def _portfolio(**overrides):
    base = {
        "name": "Test Portfolio",
        "initial_value": 10000,
        "start_date": "2024-01-01",
        "end_date": "2024-01-10",
        "assets": [
            {"ticker": "AAA", "weight": 0.5},
            {"ticker": "BBB", "weight": 0.5},
        ],
    }
    base.update(overrides)
    return base


def _mock_prices(monkeypatch, price_map):
    """Patch _safe_download to return provided price data keyed by ticker."""

    def fake_download(ticker, start, end):
        df = price_map.get(ticker.upper())
        if df is None:
            return pd.DataFrame()
        return df.copy()

    monkeypatch.setattr(backtest_module, "_safe_download", fake_download)


def test_backtest_basic_success(monkeypatch, run_backtest):
    prices = {
        "AAA": _price_series([100, 102, 104, 106]),
        "BBB": _price_series([200, 198, 202, 206]),
    }
    _mock_prices(monkeypatch, prices)

    portfolio = _portfolio(start_date="2024-01-01", end_date="2024-01-04")

    result, session = run_backtest(portfolio)

    price_df = pd.concat(
        [prices["AAA"]["Close"], prices["BBB"]["Close"]],
        axis=1,
        keys=["AAA", "BBB"],
    )
    returns = price_df.pct_change().dropna()
    weights = np.array([0.5, 0.5])
    portfolio_returns = returns.dot(weights)
    cumulative_return = (1 + portfolio_returns).prod() - 1
    final_value = 10000 * (1 + cumulative_return)
    std_ret = portfolio_returns.std(ddof=1)
    risk_free_daily = 0.02 / 252
    volatility = std_ret * (252 ** 0.5)
    sharpe = ((portfolio_returns.mean() - risk_free_daily) / std_ret) * (252 ** 0.5)

    assert result["portfolio"] == "Test Portfolio"
    assert result["final_value"] == pytest.approx(round(final_value, 2))
    assert result["cumulative_return"] == pytest.approx(round(cumulative_return, 6), rel=1e-6)
    assert result["volatility"] == pytest.approx(round(volatility, 6), rel=1e-6)
    assert result["sharpe_ratio"] == pytest.approx(round(sharpe, 6), rel=1e-6)
    assert len(result["timeseries"]) == len(portfolio_returns)
    assert session.committed
    assert len(session.added) == 1


def test_backtest_single_asset(monkeypatch, run_backtest):
    prices = {
        "AAA": _price_series([100, 105, 110]),
    }
    _mock_prices(monkeypatch, prices)

    portfolio = _portfolio(
        assets=[{"ticker": "AAA", "weight": 1.0}],
        start_date="2024-01-01",
        end_date="2024-01-03",
    )

    result, _ = run_backtest(portfolio)

    expected_return = (110 / 100) - 1
    expected_value = 10000 * (1 + expected_return)
    assert result["final_value"] == pytest.approx(round(expected_value, 2))
    assert result["cumulative_return"] == pytest.approx(round(expected_return, 6))


def test_backtest_zero_volatility(monkeypatch, run_backtest):
    prices = {
        "AAA": _price_series([100, 100, 100]),
    }
    _mock_prices(monkeypatch, prices)

    portfolio = _portfolio(
        assets=[{"ticker": "AAA", "weight": 1.0}],
        start_date="2024-01-01",
        end_date="2024-01-03",
    )

    result, _ = run_backtest(portfolio)
    assert result["final_value"] == pytest.approx(10000.0)
    assert result["volatility"] == pytest.approx(0.0)
    assert result["sharpe_ratio"] is None


@pytest.mark.parametrize(
    "portfolio, expected_message",
    [
        (_portfolio(assets=[]), "Portfolio must include at least one asset"),
        (
            _portfolio(assets=[{"ticker": "AAA", "weight": 0.0}, {"ticker": "BBB", "weight": 0.0}]),
            "Sum of weights must be positive",
        ),
    ],
)
def test_backtest_invalid_inputs(monkeypatch, run_backtest, portfolio, expected_message):
    _mock_prices(monkeypatch, {"AAA": _price_series([100, 101]), "BBB": _price_series([200, 201])})

    with pytest.raises(ValueError) as exc:
        run_backtest(portfolio)

    assert expected_message in str(exc.value)


def test_backtest_no_data(monkeypatch, run_backtest):
    _mock_prices(monkeypatch, {"AAA": pd.DataFrame(), "BBB": pd.DataFrame()})
    portfolio = _portfolio()

    with pytest.raises(ValueError) as exc:
        run_backtest(portfolio)

    assert "No price data available for any tickers" in str(exc.value)
