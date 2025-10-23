from types import SimpleNamespace
from unittest.mock import MagicMock

import pandas as pd
import pytest
from app.routers import jobs as jobs_router

# Run tests using AnyIO with the asyncio backend only
pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def test_health(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


@pytest.mark.anyio
async def test_data_price_success(async_client, monkeypatch):
    index = pd.date_range("2024-01-01", periods=3, freq="D")
    df = pd.DataFrame({"Close": [100.0, 101.0, 102.0]}, index=index)

    def fake_download(ticker, start=None, end=None, progress=False, auto_adjust=True):
        assert ticker == "AAPL"
        return df.copy()

    monkeypatch.setattr("app.routers.data.yf.download", fake_download)

    response = await async_client.get("/data/price/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["close"] == pytest.approx(100.0)


@pytest.mark.anyio
async def test_data_price_invalid(async_client, monkeypatch):
    monkeypatch.setattr("app.routers.data.yf.download", lambda *args, **kwargs: pd.DataFrame())

    response = await async_client.get("/data/price/INVALID")
    assert response.status_code == 400


@pytest.mark.anyio
async def test_jobs_backtest_submit(async_client, monkeypatch):
    payload = {
        "name": "My Portfolio",
        "initial_value": 10000,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "assets": [
            {"ticker": "AAPL", "weight": 0.6},
            {"ticker": "MSFT", "weight": 0.4},
        ],
    }

    mock_delay = MagicMock(return_value=SimpleNamespace(id="mock-task-id"))
    monkeypatch.setattr(jobs_router.run_backtest, "delay", mock_delay)

    response = await async_client.post("/jobs/backtest", json={"portfolio": payload})

    assert response.status_code == 200
    assert response.json() == {"job_id": "mock-task-id"}
    mock_delay.assert_called_once_with(payload)


@pytest.mark.anyio
async def test_jobs_backtest_invalid_payload(async_client):
    response = await async_client.post("/jobs/backtest", json={})
    assert response.status_code == 422


def _patch_async_result(monkeypatch, *, status, ready=None, successful=None, result=None, info=None):
    class DummyResult:
        def __init__(self):
            self.status = status
            self.info = info

        def failed(self):
            return self.status == "FAILURE"

        def ready(self):
            if ready is not None:
                return ready
            return self.status in ("SUCCESS", "FAILURE")

        def successful(self):
            if successful is not None:
                return successful
            return self.status == "SUCCESS"

        def get(self, *args, **kwargs):
            return result

    dummy = DummyResult()
    monkeypatch.setattr(jobs_router.celery_app, "AsyncResult", lambda _job_id: dummy)
    return dummy


@pytest.mark.anyio
@pytest.mark.parametrize(
    "status,info,expected_error",
    [
        ("PENDING", None, None),
        ("SUCCESS", None, None),
        ("FAILURE", "boom", "boom"),
    ],
)
async def test_jobs_status(async_client, monkeypatch, status, info, expected_error):
    _patch_async_result(monkeypatch, status=status, info=info)

    response = await async_client.get("/jobs/status/test-id")
    assert response.status_code == 200
    body = response.json()
    assert body["job_id"] == "test-id"
    assert body["status"] == status
    if expected_error:
        assert body.get("error") == expected_error
    else:
        assert body.get("error") in (None, "")


@pytest.mark.anyio
async def test_jobs_results_success(async_client, monkeypatch):
    result_payload = {"final_value": 12000}
    _patch_async_result(
        monkeypatch,
        status="SUCCESS",
        ready=True,
        successful=True,
        result=result_payload,
    )

    response = await async_client.get("/jobs/results/test-id")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SUCCESS"
    assert body["result"] == result_payload
    assert body["error"] is None


@pytest.mark.anyio
async def test_jobs_results_pending(async_client, monkeypatch):
    _patch_async_result(monkeypatch, status="PENDING", ready=False)

    response = await async_client.get("/jobs/results/test-id")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PENDING"
    assert body["result"] is None


@pytest.mark.anyio
async def test_jobs_results_failure(async_client, monkeypatch):
    _patch_async_result(
        monkeypatch,
        status="FAILURE",
        ready=True,
        successful=False,
        info=RuntimeError("kaput"),
    )

    response = await async_client.get("/jobs/results/test-id")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "FAILED"
    assert body["error"] == "kaput"
