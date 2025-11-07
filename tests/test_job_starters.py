from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from mcp_server import job_tools
from mcp_server.job_artifacts import job_artifact_path, job_resource_uri
from mcp_server.jobs import JobStatus, job_registry


class DummyConn:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


def _wait_for_completion(job_id: str, timeout: float = 5.0) -> None:
    job_registry.wait_for(job_id, timeout=timeout)
    state = job_registry.get_state(job_id)
    assert state is not None
    assert state.status in (JobStatus.SUCCEEDED, JobStatus.FAILED)


def test_start_part_tree_job_creates_artifact(monkeypatch, tmp_path: Path):
    monkeypatch.setattr("mcp_server.job_artifacts.JOB_ARTIFACTS_DIR", tmp_path, raising=False)
    dummy_conn = DummyConn()

    def fake_connect(address: str, rpc_port: int, stream_port: int, name: str | None, timeout: float) -> DummyConn:
        return dummy_conn

    def fake_part_tree(conn: DummyConn) -> dict[str, Any]:
        return {"parts": [{"id": 1}]}

    monkeypatch.setattr(job_tools, "connect_to_game", fake_connect)
    monkeypatch.setattr(job_tools.readers, "part_tree", fake_part_tree)

    payload = json.loads(
        job_tools.start_part_tree_job("1.2.3.4", rpc_port=1234, stream_port=2345, name="Test", timeout=1.0)
    )
    job_id = payload["job_id"]
    assert payload["status"] == "PENDING"

    _wait_for_completion(job_id)

    state = job_registry.get_state(job_id)
    assert state is not None
    assert state.status is JobStatus.SUCCEEDED
    assert state.result_resource == job_resource_uri(job_id)

    artifact = job_artifact_path(job_id)
    assert artifact.exists()
    data = json.loads(artifact.read_text())
    assert data["kind"] == "part_tree"
    assert data["result"]["parts"] == [{"id": 1}]


def test_start_stage_plan_job_passes_environment(monkeypatch, tmp_path: Path):
    monkeypatch.setattr("mcp_server.job_artifacts.JOB_ARTIFACTS_DIR", tmp_path, raising=False)
    dummy_conn = DummyConn()

    def fake_connect(address: str, rpc_port: int, stream_port: int, name: str | None, timeout: float) -> DummyConn:
        return dummy_conn

    captured_environment: list[str] = []

    def fake_stage_plan(conn: DummyConn, environment: str = "current") -> dict[str, Any]:
        captured_environment.append(environment)
        return {"env": environment, "stages": []}

    monkeypatch.setattr(job_tools, "connect_to_game", fake_connect)
    monkeypatch.setattr(job_tools.readers, "stage_plan_approx", fake_stage_plan)

    payload = json.loads(
        job_tools.start_stage_plan_job(
            "1.2.3.4",
            rpc_port=1111,
            stream_port=2222,
            name=None,
            timeout=2.0,
            environment="vacuum",
        )
    )
    job_id = payload["job_id"]
    _wait_for_completion(job_id)

    artifact = job_artifact_path(job_id)
    data = json.loads(artifact.read_text())
    assert data["kind"] == "stage_plan"
    assert data["params"]["environment"] == "vacuum"
    assert captured_environment == ["vacuum"]
