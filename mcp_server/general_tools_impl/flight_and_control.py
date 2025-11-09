from __future__ import annotations

import json

from ..utils.krpc_utils import readers
from ..utils.krpc_helpers import open_connection


def get_flight_snapshot(address: str, rpc_port: int = 50000, stream_port: int = 50001, name: str | None = None, timeout: float = 5.0) -> str:
    """
    Flight snapshot for the active vessel.

    When to use:
      - Real-time monitoring, ascent/descent guidance, atmosphere checks.

    Returns:
      JSON: { altitude_sea_level_m, altitude_terrain_m, vertical_speed_m_s,
      speed_surface_m_s, speed_horizontal_m_s, dynamic_pressure_pa, mach,
      g_force, angle_of_attack_deg, pitch_deg, roll_deg, heading_deg }.
    """
    conn = open_connection(address, rpc_port, stream_port, name, timeout)
    try:
        return json.dumps(readers.flight_snapshot(conn))
    finally:
        try:
            conn.close()
        except Exception:
            pass


def get_attitude_status(address: str, rpc_port: int = 50000, stream_port: int = 50001, name: str | None = None, timeout: float = 5.0) -> str:
    """
    Attitude/control state for the active vessel.

    When to use:
      - Verify SAS/RCS/throttle state and autopilot targets before burns.

    Returns:
      JSON: { sas, sas_mode, rcs, throttle, autopilot_state, autopilot_target_pitch,
      autopilot_target_heading, autopilot_target_roll }.
    """
    conn = open_connection(address, rpc_port, stream_port, name, timeout)
    try:
        return json.dumps(readers.attitude_status(conn))
    finally:
        try:
            conn.close()
        except Exception:
            pass


def get_action_groups_status(address: str, rpc_port: int = 50000, stream_port: int = 50001, name: str | None = None, timeout: float = 5.0) -> str:
    """
    Action group toggles.

    When to use:
      - Verify control safety and configuration pre‑burn or pre‑entry.

    Returns:
      JSON: { sas, rcs, lights, gear, brakes, abort, custom_1..custom_10 }.
    """
    conn = open_connection(address, rpc_port, stream_port, name, timeout)
    return json.dumps(readers.action_groups_status(conn))


def get_camera_status(address: str, rpc_port: int = 50000, stream_port: int = 50001, name: str | None = None, timeout: float = 5.0) -> str:
    """
    Active camera parameters when available: mode, pitch, heading, distance, and limits.

    Returns:
      JSON: { available, mode?, pitch_deg?, heading_deg?, distance_m?,
      min_pitch_deg?, max_pitch_deg?, min_distance_m?, max_distance_m? }.
    """
    conn = open_connection(address, rpc_port, stream_port, name, timeout)
    return json.dumps(readers.camera_status(conn))
