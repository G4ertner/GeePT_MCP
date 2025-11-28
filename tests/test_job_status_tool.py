from __future__ import annotations

import json
import time

from mcp_server.executor_tools.jobs import job_registry
from mcp_server.libraries import get_job_status


def _wait_for_status(job_id: str, timeout: float = 5.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        payload = json.loads(get_job_status(job_id))
        if payload["status"] in {"SUCCEEDED", "FAILED"}:
            return payload
        time.sleep(0.05)
    raise AssertionError("Job did not finish in time")


def test_get_job_status_reports_completed_job():
    def job(handle):
        handle.log("ping")
        print("stdout line")
        handle.set_result_resource("resource://demo/result.json")

    job_id = job_registry.create_job(job)
    payload = _wait_for_status(job_id)
    assert payload["status"] == "SUCCEEDED"
    assert payload["job_id"] == job_id
    assert payload["result_resource"] == "resource://demo/result.json"
    assert payload["ok"] is True
    assert any("stdout line" in entry for entry in payload["logs"])


def test_get_job_status_unknown_job_returns_error():
    payload = json.loads(get_job_status("missing-job"))
    assert payload["status"] == "UNKNOWN"
    assert payload["ok"] is False
    assert "Job not found" in payload["error"]


def test_connection_reset_noise_is_suppressed():
    # Create a short job so state exists in the registry.
    job_id = job_registry.create_job(lambda handle: None)
    job_registry.wait_for(job_id)

    noisy = "ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host"
    job_registry.append_log(job_id, noisy, stream="stderr")

    payload = json.loads(get_job_status(job_id))
    assert payload["log_stream_warning"] is True
    assert all("ConnectionResetError" not in line for line in payload["logs"])
