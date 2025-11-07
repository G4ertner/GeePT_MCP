from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Callable, Dict

from .job_artifacts import job_resource_uri, save_job_artifact
from .jobs import job_registry
from .krpc import readers
from .krpc.client import KRPCConnectionError, connect_to_game
from .server import mcp


def _utc_timestamp() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _start_reader_job(
    *,
    kind: str,
    params: Dict[str, Any],
    reader: Callable[..., Dict[str, Any]],
    reader_kwargs: Dict[str, Any] | None = None,
) -> str:
    reader_kwargs = reader_kwargs or {}

    def job_fn(handle):
        job_id = handle.job_id
        handle.log(
            f"[{kind}] Connecting to kRPC at {params['address']}:{params['rpc_port']}/{params['stream_port']}"
        )
        try:
            conn = connect_to_game(
                params["address"],
                rpc_port=params["rpc_port"],
                stream_port=params["stream_port"],
                name=params.get("name"),
                timeout=params["timeout"],
            )
        except KRPCConnectionError as exc:
            handle.log(f"[{kind}] Connection failed: {exc}")
            raise

        try:
            handle.log(f"[{kind}] Reader running...")
            data = reader(conn, **reader_kwargs)
            artifact_payload = {
                "job_id": job_id,
                "kind": kind,
                "requested_at": _utc_timestamp(),
                "params": params,
                "result": data,
            }
            save_job_artifact(job_id, artifact_payload)
            handle.log(f"[{kind}] Artifact saved; exposing as resource.")
            handle.set_result_resource(job_resource_uri(job_id))
        finally:
            try:
                conn.close()
            except Exception:
                pass

    metadata = {"kind": kind, "params": params}
    job_id = job_registry.create_job(job_fn, metadata=metadata)
    return json.dumps(
        {
            "job_id": job_id,
            "status": "PENDING",
            "note": "Job started. Poll get_job_status(job_id) until it completes.",
        }
    )


@mcp.tool()
def start_part_tree_job(
    address: str,
    rpc_port: int = 50000,
    stream_port: int = 50001,
    name: str | None = None,
    *,
    timeout: float = 5.0,
) -> str:
    """
    Start a background job that captures the full vessel part tree via kRPC readers.part_tree.

    Usage pattern:
        1. Call start_part_tree_job(...) to enqueue the work; it returns a job_id immediately.
        2. Poll get_job_status(job_id) until status is SUCCEEDED.
        3. Call read_resource on the returned result_resource (resource://jobs/<id>.json) to download the JSON artifact.
        4. Use the downloaded part tree for planning, then continue with other tools/scripts as needed.
    """
    params = {
        "address": address,
        "rpc_port": rpc_port,
        "stream_port": stream_port,
        "name": name,
        "timeout": timeout,
    }
    return _start_reader_job(kind="part_tree", params=params, reader=readers.part_tree)


@mcp.tool()
def start_stage_plan_job(
    address: str,
    rpc_port: int = 50000,
    stream_port: int = 50001,
    name: str | None = None,
    *,
    timeout: float = 5.0,
    environment: str = "current",
) -> str:
    """
    Start a background job that computes the per-stage delta-v/TWR plan via readers.stage_plan_approx.

    Usage pattern:
        1. Call start_stage_plan_job(...) (optionally choose environment) to enqueue the work.
        2. Poll get_job_status(job_id) until status is SUCCEEDED.
        3. Call read_resource on the result_resource (resource://jobs/<id>.json) to download the stage plan JSON.
        4. Incorporate the staging data into your burn planning workflow (e.g., playbooks, scripts).
    """
    params = {
        "address": address,
        "rpc_port": rpc_port,
        "stream_port": stream_port,
        "name": name,
        "timeout": timeout,
        "environment": environment,
    }
    reader_kwargs = {"environment": environment}
    return _start_reader_job(
        kind="stage_plan",
        params=params,
        reader=readers.stage_plan_approx,
        reader_kwargs=reader_kwargs,
    )
