from __future__ import annotations

import sys

from .mcp_context import mcp
from .executor_impl.core import (
    execute_script_impl,
    start_execute_script_job_impl,
    _run_execute_script as core_run_execute_script,
)

# Import implementation modules so their resources are registered
from .executor_impl import job_artifacts as _job_artifacts
from .executor_impl import job_tools as _job_tools
from .executor_impl import jobs as _jobs
from .executor_impl import script_jobs as _script_jobs

# Expose implementation modules under the historical mcp_server.executor_tools.*
job_artifacts = _job_artifacts
job_tools = _job_tools
jobs = _jobs
script_jobs = _script_jobs

sys.modules[__name__ + ".job_artifacts"] = _job_artifacts
sys.modules[__name__ + ".job_tools"] = _job_tools
sys.modules[__name__ + ".jobs"] = _jobs
sys.modules[__name__ + ".script_jobs"] = _script_jobs


@mcp.tool()
def execute_script(
    code: str,
    address: str,
    rpc_port: int = 50000,
    stream_port: int = 50001,
    name: str | None = None,
    *,
    timeout_sec: float | None = None,
    pause_on_end: bool = True,
    unpause_on_start: bool = True,
    allow_imports: bool = False,
    hard_timeout_sec: float | None = None,
) -> str:
    return execute_script_impl(
        code=code,
        address=address,
        rpc_port=rpc_port,
        stream_port=stream_port,
        name=name,
        timeout_sec=timeout_sec,
        pause_on_end=pause_on_end,
        unpause_on_start=unpause_on_start,
        allow_imports=allow_imports,
        hard_timeout_sec=hard_timeout_sec,
    )


execute_script.__doc__ = execute_script_impl.__doc__


@mcp.tool()
def start_execute_script_job(
    code: str,
    address: str,
    rpc_port: int = 50000,
    stream_port: int = 50001,
    name: str | None = None,
    *,
    timeout_sec: float | None = None,
    pause_on_end: bool = True,
    unpause_on_start: bool = True,
    allow_imports: bool = False,
    hard_timeout_sec: float | None = None,
) -> str:
    return start_execute_script_job_impl(
        code=code,
        address=address,
        rpc_port=rpc_port,
        stream_port=stream_port,
        name=name,
        timeout_sec=timeout_sec,
        pause_on_end=pause_on_end,
        unpause_on_start=unpause_on_start,
        allow_imports=allow_imports,
        hard_timeout_sec=hard_timeout_sec,
    )


start_execute_script_job.__doc__ = start_execute_script_job_impl.__doc__

# Expose the low-level runner for tests (monkeypatched in unit tests)
_run_execute_script = core_run_execute_script
