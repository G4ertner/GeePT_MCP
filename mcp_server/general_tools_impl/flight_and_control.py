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
      - Pair with set_sas_mode to adjust navball hold behaviors.

    Returns:
      JSON: { sas, sas_mode, rcs, throttle, autopilot_state, autopilot_target_pitch,
      autopilot_target_heading, autopilot_target_roll, speed_mode? }.
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


def set_sas_mode(address: str, mode: str, enable_sas: bool = True, rpc_port: int = 50000, stream_port: int = 50001, name: str | None = None, timeout: float = 5.0) -> str:
    """
    Set SAS on/off and select an SAS hold mode.

    Args:
      mode: One of the SAS modes (stability_assist, prograde, retrograde, normal, anti_normal,
        radial, anti_radial, target, anti_target, maneuver). Case- and dash/underscore-insensitive.
      enable_sas: If true, toggle SAS on before setting the mode.

    Returns:
      Human-readable status string (success or error).
    """
    conn = open_connection(address, rpc_port, stream_port, name, timeout)
    try:
        sc = conn.space_center
        ctrl = sc.active_vessel.control

        key = mode.strip().lower().replace("-", "_")
        aliases = {
            "antinormal": "anti_normal",
            "anti_normal": "anti_normal",
            "antiradial": "anti_radial",
            "anti_radial": "anti_radial",
            "antitarget": "anti_target",
            "anti_target": "anti_target",
            "stability": "stability_assist",
            "stabilityassist": "stability_assist",
            "maneuver": "maneuver",
        }
        key = aliases.get(key, key)

        options = {attr.lower(): getattr(sc.SASMode, attr) for attr in dir(sc.SASMode) if not attr.startswith("_")}
        sas_enum = options.get(key)
        if sas_enum is None:
            available = ", ".join(sorted(options))
            return f"Unknown SAS mode '{mode}'. Available: {available}"

        try:
            if enable_sas is not None:
                ctrl.sas = bool(enable_sas)
        except Exception:
            pass

        ctrl.sas_mode = sas_enum
        return f"SAS mode set to {getattr(sas_enum, 'name', key)} (sas={getattr(ctrl, 'sas', enable_sas)})."
    except Exception as e:
        return f"Failed to set SAS mode: {e}"
    finally:
        try:
            conn.close()
        except Exception:
            pass
