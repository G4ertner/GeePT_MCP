from __future__ import annotations

import asyncio
import time

import pytest

from mcp_server.utils.async_utils import run_blocking

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def test_run_blocking_completes() -> None:
    result = await run_blocking(lambda x: x + 1, 1, timeout_sec=1.0)
    assert result == 2


async def test_run_blocking_times_out_and_calls_cleanup() -> None:
    flag = {"cleanup_called": False}

    def slow_call() -> None:
        time.sleep(0.2)

    def cleanup() -> None:
        flag["cleanup_called"] = True

    with pytest.raises(asyncio.TimeoutError):
        await run_blocking(slow_call, timeout_sec=0.05, cancel_cleanup=cleanup)

    assert flag["cleanup_called"] is True
