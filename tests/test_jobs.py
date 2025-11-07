from __future__ import annotations

import sys

from mcp_server.jobs import JobRegistry, JobStatus


def test_job_lifecycle_success():
    registry = JobRegistry(max_workers=1)

    def job(handle):
        handle.log("starting work")
        print("hello from stdout")
        handle.set_result_resource("resource://demo/result.json")

    job_id = registry.create_job(job, metadata={"kind": "demo"})
    registry.wait_for(job_id, timeout=5)
    state = registry.get_state(job_id)
    assert state is not None
    assert state.status is JobStatus.SUCCEEDED
    assert state.result_resource == "resource://demo/result.json"
    assert state.started_at is not None
    assert state.finished_at is not None
    assert any("stdout" in line for line in state.logs)
    assert any("starting work" in line for line in state.logs)
    assert state.metadata["kind"] == "demo"
    registry.shutdown()


def test_job_failure_captures_error_and_stderr():
    registry = JobRegistry(max_workers=1)

    def job(_handle):
        print("things went boom", file=sys.stderr)
        raise RuntimeError("kaboom")

    job_id = registry.create_job(job)
    registry.wait_for(job_id, timeout=5)
    state = registry.get_state(job_id)
    assert state is not None
    assert state.status is JobStatus.FAILED
    assert "kaboom" in (state.error or "")
    assert any("stderr" in line and "things went boom" in line for line in state.logs)
    registry.shutdown()
