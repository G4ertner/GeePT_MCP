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


def set_timewarp_rate(address: str, rate: float, mode: str | None = None, rpc_port: int = 50000, stream_port: int = 50001, name: str | None = None, timeout: float = 5.0) -> str:
    """
    Adjust the current timewarp rate (and optionally the warp mode).

    When to use:
      - Change how fast the simulation advances when waiting on long events.
      - Reset the warp speed after a fire-and-forget warp_to call.

    Args:
      rate: Desired timewarp rate; 1.0 is realtime, >1 is warp, 0 stops time.
      mode: Optional warp mode name ('physics', 'rails', 'none').

    Returns:
      Human-readable status string describing the result."""
    conn = open_connection(address, rpc_port, stream_port, name, timeout)
    try:
        sc = conn.space_center
        tw = getattr(sc, "warp", None)
        if tw is None:
            return "Timewarp controls are not supported by this kRPC client."

        if mode is not None:
            warp_mode_enum = getattr(sc, "WarpMode", None)
            if warp_mode_enum is None:
                return "Warp mode selection is unavailable on this client."
            normalized = mode.lower()
            selection = getattr(warp_mode_enum, normalized, None)
            valid_modes = [
                name
                for name in ("physics", "rails", "none")
                if hasattr(warp_mode_enum, name)
            ]
            if selection is None:
                candidate_list = ", ".join(valid_modes) if valid_modes else "physics, rails, none"
                return f"Unsupported warp mode '{mode}'. Valid options: {candidate_list}."
            try:
                tw.mode = selection
            except Exception as exc:
                return f"Failed to set warp mode '{mode}': {exc}"

        try:
            tw.rate = float(rate)
        except Exception as exc:
            return f"Failed to set warp rate to {rate}: {exc}"

        return f"Timewarp rate set to {float(tw.rate)}."
    except Exception as exc:  # pragma: no cover - best-effort helper
        return f"Failed to adjust timewarp: {exc}"
    finally:
        try:
            conn.close()
        except Exception:
            pass
