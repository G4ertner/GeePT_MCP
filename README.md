# KSP Mission‑Control Protocol (MCP) Server

![Kerbal mission chaos](readme-banner.png)

## Introduction

"Computer, fly me to Orbit!"
- a Kerbal's last words

You always dreamed of having an agent autonomously control your spaceship? No more need to fly boring standard maneuvers like ascent to orbit, rendezvous, landings? Let the AI do them! 

The **KSP Mission‑Control Protocol (MCP) server** transforms Kerbal Space Program into a remote‑controlled playground for AI agents and human operators.  By combining [kRPC](https://krpc.github.io/krpc/) with a rich set of mission tools, it lets your LLM:

- write and execute kRPC Python scripts inside your live KSP game, effectively taking control of your flight*.
- Inspect your vessel’s blueprint, part tree, stages and engines, to have an overview of what kind of bent bird you're flying.
- Conveniently search and retrieve pages from the KSP Wiki, as well as the official kRPC documentation, and kRPC community code snippets for best practices.
- Access playbooks and guides that teach agents how to read blueprints and plan safe staging and burns.

*Successful flights cannot be guaranteed

## Quick start

1. **Install dependencies**

   This project requires Python 3.10+ and [uv](https://github.com/astral-sh/uv) for running scripts and managing dependencies.  Optionally install the `krpc` extras to enable kRPC connectivity and `Pillow` if you want PNG diagram export.

   ```sh
   # Clone the repository
   git clone https://github.com/G4ertner/kRPC_docs_MCP.git
   cd kRPC_docs_MCP

   # Use uv to run the MCP server
   curl -LsSf https://astral.sh/uv/install.sh | sh  # install uv
   uv pip install -e .[krpc]  # install dependencies with krpc extras
   uv pip install pillow     # optional, for PNG diagram export
   ```

2. **Launch the MCP server**

   In one terminal, start Kerbal Space Program and enable the kRPC server (Protobuf over TCP).  Note the address and ports shown in the kRPC window.  In another terminal, run:

   ```sh
   # from the repo root
   uv run -m mcp_server.main
   ```

   The server will listen for incoming requests over stdio (for Codex integration) and handle script execution and tool calls.

3. **Register with Codex CLI (optional)**

   If you use [Codex CLI](https://github.com/openai/openai-codex-cli), add the MCP server so it can be launched on demand:

   ```sh
   codex mcp add krpc_docs -- uv run -m mcp_server.main --with krpc
   ```

4. **Connect to your game**

   When calling tools that interact with the game (execute scripts, fetch blueprints, etc.), provide the address and ports of your running KSP instance.  For example:

   ```
   Use krpc_docs to execute_script with code "print('hello'); print('SUMMARY: done')" and address "192.168.1.10" rpc_port 50000 stream_port 50001
   ```

## Core capabilities

### 🛰️ Live script execution

The `execute_script` tool allows your LLM to run kRPC Python code against your running game. with its pre-setup there is no need to worry your LLM will successfully connect to your game. The MCP server automatically injects useful globals:

- `conn`: your live kRPC connection
- `vessel`: the active vessel (or `None` if you’re not in flight)
- `time`, `math`, `sleep`, `deadline` and `check_time()` helpers
- a preconfigured `logging` module and a `log(msg)` convenience function
- A status summary of flight variables after successful execution or catastrophic failure

Additionally, the game will automatically pause after the execution of each script, ensuring that nothing unforeseen happens while your LLM keeps on planning the next step.

### 🛠️ Vessel blueprints & diagrams

Need your LLM to inspect your craft? The blueprint tools expose:

- `get_vessel_blueprint`: returns a JSON blueprint with metadata, stages, engines and parts.
- `get_part_tree`: returns a hierarchical list of all parts with parent/child relationships, modules and resources.
- `get_blueprint_ascii`: produces a LLM-readable per‑stage summary of the vessel.
- `get_stage_plan`: provides a stock-like stage plan (thrust, Isp, Δv).
- `get_staging_info`: returns per-stage Δv/TWR estimates.
- `export_blueprint_diagram`: generates a diagram (SVG or PNG) of your vessel’s staging and structure.  

These tools let your LLM understand the craft’s structure, plan staging and fuel usage to generate vessel specific flight plans and mission profiles

### 📚 KSP Wiki, kRPC docs search, and community example snippets search

The MCP server wraps the MediaWiki API and the locally indexed kRPC documentation.  Tools include:

- `search_ksp_wiki(query, limit)`, `get_ksp_wiki_page(title, max_chars)` and `get_ksp_wiki_section(title, heading, max_chars)` for looking up game concepts (e.g. delta‑v, maneuver nodes, ISRU).  Perfect for agents that need domain knowledge.
- `search_krpc_docs(query, k)` and `get_krpc_doc(url, max_chars)` for searching and retrieving the kRPC Python API reference without leaving chat.
- `snippets_search`, `snippets_get`, `snippets_resolve`, and `snippets_search_and_resolve` allows your LLM to get the best examples for kRPC code from 11 most popular kRPC public repos.

### 📖 Playbooks & guidance

The server ships with severeal playbooks to give your LLM a headstart on how to use the MCP's tools and execute common maneuvers:

get_maneuver_node_playbook — (resource://playbooks/maneuver-node)
get_blueprint_usage_playbook — (resource://playbooks/vessel-blueprint-usage)
get_flight_control_playbook — (resource://playbooks/flight-control)
get_rendezvous_playbook — (resource://playbooks/rendezvous-docking)
get_launch_ascent_circ_playbook — (resource://playbooks/launch-ascent-circularize)
get_state_checkpoint_playbook — (resource://playbooks/state-checkpoint-rollback)
get_scribe_master_prompt_resource — (resource://prompts/scribe-master)
get_latest_blueprint — (resource://blueprints/latest)
get_last_svg — (resource://blueprints/last-diagram.svg)
get_last_png — (resource://blueprints/last-diagram.png)
get_snippets_usage — (resource://snippets/usage)

### Additional Tools

On top of that, the MCP server comes with a whole set of hardcoded tools your LLM can easily call to interact with the game. This avoids your LLM having to write out code for simple commands.

#### 🧭 Connection & Save Management
- `krpc_get_status` — Checks connectivity to kRPC and reports version.
- `save_llm_checkpoint` — Creates a namespaced save (non-quicksave).
- `load_llm_checkpoint` — Loads a named save (LLM-prefixed by default).
- `quicksave`, `quickload`, `revert_to_launch` — Manage flight and revert states.

#### 🚀 Launch & Vessels
- `launch_vessel` — Launches a craft from VAB/SPH at a site.
- `list_launchable_vessels` — Lists craft available in VAB/SPH.
- `list_launch_sites` — Lists available launch sites.
- `list_vessels` — Lists vessels in the save.

#### 🌍 Bodies & Waypoints
- `list_bodies` — Lists celestial bodies with key metadata.
- `list_waypoints` — Lists waypoints with location and range/bearing.


#### 🧾 Status & Time
- `get_status_overview` — Combined snapshot of vessel/game state.
- `get_vessel_info` — Basic vessel info (name, mass, throttle, situation).
- `get_time_status` — Universal and mission time.

#### 🌡️ Environment & Surface
- `get_environment_info` — Body/environment data including gravity and atmosphere.
- `get_surface_info` — Surface coords, terrain height, slope, ground speed.

#### 🛩️ Flight & Control
- `get_flight_snapshot` — Flight parameters (altitude, speeds, AoA, attitude).
- `get_attitude_status` — SAS/RCS/throttle and autopilot targets.
- `get_action_groups_status` — Action group toggles.
- `get_camera_status` — Camera mode and parameters.

#### 🌬️ Aerodynamics & Engines
- `get_aero_status` — Dynamic pressure, Mach, density, drag/lift.
- `get_engine_status` — Per-engine thrust, Isp, throttle, flameout.

#### ⚡ Power & Resources
- `get_power_status` — EC totals, production/consumption, notes.
- `get_resource_breakdown` — Vessel and stage resource totals.

#### 🧱 Blueprints, Parts & Staging
- `get_vessel_blueprint` — Idealized craft blueprint (stages, engines, parts).
- `get_blueprint_ascii` — Compact ASCII stage summary with Δv/TWR.
- `get_part_tree` — Hierarchical part tree with resources.
- `get_stage_plan` — Stock-like stage plan (thrust, Isp, Δv).
- `get_staging_info` — Per-stage Δv/TWR estimates.
- `export_blueprint_diagram` — Exports a 2D blueprint diagram (SVG/PNG).

#### 🪐 Orbit & Navigation Info
- `get_orbit_info` — Orbital elements and periods.
- `get_navigation_info` — Navigation context relative to target.
- `get_targeting_info` — Current target summary.

#### 🎯 Target Control
- `set_target_body` — Sets target body.
- `set_target_vessel` — Sets target vessel by name.
- `clear_target` — Clears current target.

#### 🔭 Maneuver Nodes
- `list_maneuver_nodes` — Lists basic maneuver nodes.
- `list_maneuver_nodes_detailed` — Detailed node vectors and burn estimate.
- `set_maneuver_node` — Creates a node at UT with vector.
- `update_maneuver_node` — Edits an existing node.
- `delete_maneuver_nodes` — Removes all maneuver nodes.
- `warp_to` — Warps to a UT with optional lead time.

#### 🧠 Planning Helpers (Burns & Transfers)
- `compute_burn_time` — Estimates burn time for Δv.
- `compute_circularize_node` — Proposes circularization at Ap/Pe.
- `compute_raise_lower_node` — Proposes Ap/Pe change to a target altitude.
- `compute_transfer_window_to_body` — Computes Hohmann transfer window.
- `compute_ejection_node_to_body` — Coarse ejection burn from parking orbit.
- `compute_plane_change_nodes` — Plane-change burns at AN/DN.
- `compute_rendezvous_phase_node` — Phasing orbit for rendezvous.

#### ⚓ Docking
- `list_docking_ports` — Lists docking ports and states.

---

> 🥪 **Experimental**: This project is under active development.  Use at your own risk and feel free to open issues or PRs if you encounter problems or have suggestions.
