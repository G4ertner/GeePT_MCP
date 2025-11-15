from __future__ import annotations

from .mcp_context import mcp
from .general_tools_impl import (
    aerodynamics_and_engines,
    blueprints,
    blueprints_parts_and_staging,
    bodies_and_waypoints,
    connection_and_save,
    diagnostics,
    docking,
    environment_and_surface,
    flight_and_control,
    launch_and_vessel,
    maneuver_nodes,
    orbit_and_navigation,
    planning_helpers,
    power_and_resources,
    status_and_time,
    target_control,
)


# Connection & save ---------------------------------------------------------
@mcp.tool()
def krpc_get_status(*args, **kwargs):
    return connection_and_save.krpc_get_status(*args, **kwargs)


@mcp.tool()
def revert_to_launch(*args, **kwargs):
    return connection_and_save.revert_to_launch(*args, **kwargs)


@mcp.tool()
def save_llm_checkpoint(*args, **kwargs):
    return connection_and_save.save_llm_checkpoint(*args, **kwargs)


@mcp.tool()
def load_llm_checkpoint(*args, **kwargs):
    return connection_and_save.load_llm_checkpoint(*args, **kwargs)


@mcp.tool()
def quicksave(*args, **kwargs):
    return connection_and_save.quicksave(*args, **kwargs)


@mcp.tool()
def quickload(*args, **kwargs):
    return connection_and_save.quickload(*args, **kwargs)


# Status & time -------------------------------------------------------------
@mcp.tool()
def get_status_overview(*args, **kwargs):
    return status_and_time.get_status_overview(*args, **kwargs)


@mcp.tool()
def get_vessel_info(*args, **kwargs):
    return status_and_time.get_vessel_info(*args, **kwargs)


@mcp.tool()
def get_time_status(*args, **kwargs):
    return status_and_time.get_time_status(*args, **kwargs)


# Environment & surface ----------------------------------------------------
@mcp.tool()
def get_environment_info(*args, **kwargs):
    return environment_and_surface.get_environment_info(*args, **kwargs)


@mcp.tool()
def get_surface_info(*args, **kwargs):
    return environment_and_surface.get_surface_info(*args, **kwargs)


# Flight & control ---------------------------------------------------------
@mcp.tool()
def get_flight_snapshot(*args, **kwargs):
    return flight_and_control.get_flight_snapshot(*args, **kwargs)


@mcp.tool()
def get_attitude_status(*args, **kwargs):
    return flight_and_control.get_attitude_status(*args, **kwargs)


def set_sas_mode(*args, **kwargs):
    return flight_and_control.set_sas_mode(*args, **kwargs)


@mcp.tool()
def get_action_groups_status(*args, **kwargs):
    return flight_and_control.get_action_groups_status(*args, **kwargs)


@mcp.tool()
def get_camera_status(*args, **kwargs):
    return flight_and_control.get_camera_status(*args, **kwargs)


# Aerodynamics & engines ---------------------------------------------------
@mcp.tool()
def get_aero_status(*args, **kwargs):
    return aerodynamics_and_engines.get_aero_status(*args, **kwargs)


@mcp.tool()
def get_engine_status(*args, **kwargs):
    return aerodynamics_and_engines.get_engine_status(*args, **kwargs)


# Power & resources --------------------------------------------------------
@mcp.tool()
def get_power_status(*args, **kwargs):
    return power_and_resources.get_power_status(*args, **kwargs)


@mcp.tool()
def get_resource_breakdown(*args, **kwargs):
    return power_and_resources.get_resource_breakdown(*args, **kwargs)


# Blueprints, parts & staging ----------------------------------------------
@mcp.tool()
def get_part_tree(*args, **kwargs):
    return blueprints_parts_and_staging.get_part_tree(*args, **kwargs)


@mcp.tool()
def get_vessel_blueprint(*args, **kwargs):
    return blueprints_parts_and_staging.get_vessel_blueprint(*args, **kwargs)


@mcp.tool()
def get_blueprint_ascii(*args, **kwargs):
    return blueprints_parts_and_staging.get_blueprint_ascii(*args, **kwargs)


@mcp.tool()
def get_stage_plan(*args, **kwargs):
    return blueprints_parts_and_staging.get_stage_plan(*args, **kwargs)


@mcp.tool()
def get_staging_info(*args, **kwargs):
    return blueprints_parts_and_staging.get_staging_info(*args, **kwargs)


# Orbit & navigation -------------------------------------------------------
@mcp.tool()
def get_orbit_info(*args, **kwargs):
    return orbit_and_navigation.get_orbit_info(*args, **kwargs)


@mcp.tool()
def get_navigation_info(*args, **kwargs):
    return orbit_and_navigation.get_navigation_info(*args, **kwargs)


@mcp.tool()
def get_targeting_info(*args, **kwargs):
    return orbit_and_navigation.get_targeting_info(*args, **kwargs)


# Target control -----------------------------------------------------------
@mcp.tool()
def set_target_body(*args, **kwargs):
    return target_control.set_target_body(*args, **kwargs)


@mcp.tool()
def set_target_vessel(*args, **kwargs):
    return target_control.set_target_vessel(*args, **kwargs)


@mcp.tool()
def clear_target(*args, **kwargs):
    return target_control.clear_target(*args, **kwargs)


# Bodies & waypoints -------------------------------------------------------
@mcp.tool()
def list_bodies(*args, **kwargs):
    return bodies_and_waypoints.list_bodies(*args, **kwargs)


@mcp.tool()
def list_waypoints(*args, **kwargs):
    return bodies_and_waypoints.list_waypoints(*args, **kwargs)


# Launch & vessels ---------------------------------------------------------
@mcp.tool()
def list_launch_sites(*args, **kwargs):
    return launch_and_vessel.list_launch_sites(*args, **kwargs)


@mcp.tool()
def list_launchable_vessels(*args, **kwargs):
    return launch_and_vessel.list_launchable_vessels(*args, **kwargs)


@mcp.tool()
def launch_vessel(*args, **kwargs):
    return launch_and_vessel.launch_vessel(*args, **kwargs)


@mcp.tool()
def list_vessels(*args, **kwargs):
    return launch_and_vessel.list_vessels(*args, **kwargs)


# Maneuver nodes -----------------------------------------------------------
@mcp.tool()
def list_maneuver_nodes(*args, **kwargs):
    return maneuver_nodes.list_maneuver_nodes(*args, **kwargs)


@mcp.tool()
def list_maneuver_nodes_detailed(*args, **kwargs):
    return maneuver_nodes.list_maneuver_nodes_detailed(*args, **kwargs)


@mcp.tool()
def set_maneuver_node(*args, **kwargs):
    return maneuver_nodes.set_maneuver_node(*args, **kwargs)


@mcp.tool()
def update_maneuver_node(*args, **kwargs):
    return maneuver_nodes.update_maneuver_node(*args, **kwargs)


@mcp.tool()
def delete_maneuver_nodes(*args, **kwargs):
    return maneuver_nodes.delete_maneuver_nodes(*args, **kwargs)


@mcp.tool()
def warp_to(*args, **kwargs):
    return maneuver_nodes.warp_to(*args, **kwargs)


# Planning helpers ---------------------------------------------------------
@mcp.tool()
def compute_burn_time(*args, **kwargs):
    return planning_helpers.compute_burn_time(*args, **kwargs)


@mcp.tool()
def compute_circularize_node(*args, **kwargs):
    return planning_helpers.compute_circularize_node(*args, **kwargs)


@mcp.tool()
def compute_plane_change_nodes(*args, **kwargs):
    return planning_helpers.compute_plane_change_nodes(*args, **kwargs)


@mcp.tool()
def compute_raise_lower_node(*args, **kwargs):
    return planning_helpers.compute_raise_lower_node(*args, **kwargs)


@mcp.tool()
def compute_rendezvous_phase_node(*args, **kwargs):
    return planning_helpers.compute_rendezvous_phase_node(*args, **kwargs)


@mcp.tool()
def compute_transfer_window_to_body(*args, **kwargs):
    return planning_helpers.compute_transfer_window_to_body(*args, **kwargs)


@mcp.tool()
def compute_ejection_node_to_body(*args, **kwargs):
    return planning_helpers.compute_ejection_node_to_body(*args, **kwargs)


# Docking ------------------------------------------------------------------
@mcp.tool()
def list_docking_ports(*args, **kwargs):
    return docking.list_docking_ports(*args, **kwargs)


# Diagnostics --------------------------------------------------------------
@mcp.tool()
def get_diagnostics(*args, **kwargs):
    return diagnostics.get_diagnostics(*args, **kwargs)


# Blueprints ---------------------------------------------------------------
@mcp.tool()
def export_blueprint_diagram(*args, **kwargs):
    return blueprints.export_blueprint_diagram(*args, **kwargs)


@mcp.resource("resource://blueprints/latest")
def resource_get_latest_blueprint():
    return blueprints.get_latest_blueprint()


@mcp.resource("resource://blueprints/last-diagram.svg")
def resource_get_last_svg():
    return blueprints.get_last_svg()


@mcp.resource("resource://blueprints/last-diagram.png")
def resource_get_last_png():
    return blueprints.get_last_png()


# Keep docstrings in sync with the implementation modules so updates happen
# in one place (general_tools_impl.*).
_TOOL_DOC_SOURCES = {
    "krpc_get_status": connection_and_save.krpc_get_status,
    "revert_to_launch": connection_and_save.revert_to_launch,
    "save_llm_checkpoint": connection_and_save.save_llm_checkpoint,
    "load_llm_checkpoint": connection_and_save.load_llm_checkpoint,
    "quicksave": connection_and_save.quicksave,
    "quickload": connection_and_save.quickload,
    "get_status_overview": status_and_time.get_status_overview,
    "get_vessel_info": status_and_time.get_vessel_info,
    "get_time_status": status_and_time.get_time_status,
    "get_environment_info": environment_and_surface.get_environment_info,
    "get_surface_info": environment_and_surface.get_surface_info,
    "get_flight_snapshot": flight_and_control.get_flight_snapshot,
    "get_attitude_status": flight_and_control.get_attitude_status,
    "set_sas_mode": flight_and_control.set_sas_mode,
    "get_action_groups_status": flight_and_control.get_action_groups_status,
    "get_camera_status": flight_and_control.get_camera_status,
    "get_aero_status": aerodynamics_and_engines.get_aero_status,
    "get_engine_status": aerodynamics_and_engines.get_engine_status,
    "get_power_status": power_and_resources.get_power_status,
    "get_resource_breakdown": power_and_resources.get_resource_breakdown,
    "get_part_tree": blueprints_parts_and_staging.get_part_tree,
    "get_vessel_blueprint": blueprints_parts_and_staging.get_vessel_blueprint,
    "get_blueprint_ascii": blueprints_parts_and_staging.get_blueprint_ascii,
    "get_stage_plan": blueprints_parts_and_staging.get_stage_plan,
    "get_staging_info": blueprints_parts_and_staging.get_staging_info,
    "get_orbit_info": orbit_and_navigation.get_orbit_info,
    "get_navigation_info": orbit_and_navigation.get_navigation_info,
    "get_targeting_info": orbit_and_navigation.get_targeting_info,
    "set_target_body": target_control.set_target_body,
    "set_target_vessel": target_control.set_target_vessel,
    "clear_target": target_control.clear_target,
    "list_bodies": bodies_and_waypoints.list_bodies,
    "list_waypoints": bodies_and_waypoints.list_waypoints,
    "list_launch_sites": launch_and_vessel.list_launch_sites,
    "list_launchable_vessels": launch_and_vessel.list_launchable_vessels,
    "launch_vessel": launch_and_vessel.launch_vessel,
    "list_vessels": launch_and_vessel.list_vessels,
    "list_maneuver_nodes": maneuver_nodes.list_maneuver_nodes,
    "list_maneuver_nodes_detailed": maneuver_nodes.list_maneuver_nodes_detailed,
    "set_maneuver_node": maneuver_nodes.set_maneuver_node,
    "update_maneuver_node": maneuver_nodes.update_maneuver_node,
    "delete_maneuver_nodes": maneuver_nodes.delete_maneuver_nodes,
    "warp_to": maneuver_nodes.warp_to,
    "compute_burn_time": planning_helpers.compute_burn_time,
    "compute_circularize_node": planning_helpers.compute_circularize_node,
    "compute_plane_change_nodes": planning_helpers.compute_plane_change_nodes,
    "compute_raise_lower_node": planning_helpers.compute_raise_lower_node,
    "compute_rendezvous_phase_node": planning_helpers.compute_rendezvous_phase_node,
    "compute_transfer_window_to_body": planning_helpers.compute_transfer_window_to_body,
    "compute_ejection_node_to_body": planning_helpers.compute_ejection_node_to_body,
    "list_docking_ports": docking.list_docking_ports,
    "get_diagnostics": diagnostics.get_diagnostics,
    "export_blueprint_diagram": blueprints.export_blueprint_diagram,
}

for _tool_name, _impl in _TOOL_DOC_SOURCES.items():
    _tool = globals().get(_tool_name)
    if _tool is not None:
        _tool.__doc__ = getattr(_impl, "__doc__", None)
