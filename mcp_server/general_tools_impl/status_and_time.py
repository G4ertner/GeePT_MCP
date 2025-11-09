from __future__ import annotations

import json

from ..utils.krpc_utils import readers
from ..utils.krpc_helpers import open_connection


def get_status_overview(address: str, rpc_port: int = 50000, stream_port: int = 50001, name: str | None = None, timeout: float = 5.0) -> str:
    """
    Combined snapshot of core vessel/game status in a single call.

    When to use:
      - Summarize state for planning, logging, or sanity checks.

    Returns:
      JSON: { vessel, environment, flight, orbit, time, attitude, aero, maneuver_nodes }.
    """
    conn = open_connection(address, rpc_port, stream_port, name, timeout)
    try:
        out = {
            "vessel": readers.vessel_info(conn),
            "environment": readers.environment_info(conn),
            "flight": readers.flight_snapshot(conn),
            "orbit": readers.orbit_info(conn),
            "time": readers.time_status(conn),
            "attitude": readers.attitude_status(conn),
            "aero": readers.aero_status(conn),
            "maneuver_nodes": readers.maneuver_nodes_basic(conn),
        }
        return json.dumps(out)
    finally:
        try:
            conn.close()
        except Exception:
            pass


def get_vessel_info(address: str, rpc_port: int = 50000, stream_port: int = 50001, name: str | None = None, timeout: float = 5.0) -> str:
    """
    Basic vessel info for the active craft.

    When to use:
      - High-level status summaries and sanity checks prior to planning.

    Args:
      address: LAN IP/hostname of the KSP PC
      rpc_port: kRPC RPC port (default 50000)
      stream_port: kRPC stream port (default 50001)
      name: Optional connection name shown in kRPC UI
      timeout: Connection timeout in seconds

    Returns:
      JSON string: { name, mass_kg, throttle, situation }
    """
    conn = open_connection(address, rpc_port, stream_port, name, timeout)
    try:
        return json.dumps(readers.vessel_info(conn))
    finally:
        try:
            conn.close()
        except Exception:
            pass


def get_time_status(address: str, rpc_port: int = 50000, stream_port: int = 50001, name: str | None = None, timeout: float = 5.0) -> str:
    """
    Time context for the current save.

    When to use:
      - Scheduling burns, warp decisions, or synchronizing UT across tools.

    Returns:
      JSON: { universal_time_s, mission_time_s }.
    """
    conn = open_connection(address, rpc_port, stream_port, name, timeout)
    try:
        return json.dumps(readers.time_status(conn))
    finally:
        try:
            conn.close()
        except Exception:
            pass
