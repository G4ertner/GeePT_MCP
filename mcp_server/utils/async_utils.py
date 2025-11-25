from __future__ import annotations

import asyncio
from typing import Any, Callable, TypeVar

T = TypeVar("T")


async def run_blocking(
    fn: Callable[..., T],
    *args: Any,
    timeout_sec: float | None = 60.0,
    cancel_cleanup: Callable[[], None] | None = None,
    **kwargs: Any,
) -> T:
    """
    Run a blocking callable in a worker thread with an optional hard timeout.

    Args:
        fn: Callable to execute.
        timeout_sec: Hard timeout for the work (None to disable).
        cancel_cleanup: Optional cleanup invoked if the task is cancelled/timeout.
        *args/kwargs: Passed to fn.
    """
    task = asyncio.to_thread(fn, *args, **kwargs)
    try:
        if timeout_sec is None:
            return await task
        return await asyncio.wait_for(task, timeout_sec)
    except Exception:
        if cancel_cleanup:
            try:
                cancel_cleanup()
            except Exception:
                pass
        raise
