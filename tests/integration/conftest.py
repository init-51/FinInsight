import asyncio

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
def async_client():
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://testserver")
    try:
        yield client
    finally:
        asyncio.run(client.aclose())
