from __future__ import annotations

from .server import mcp


PLAYBOOK_TEXT = '''
Maneuver Node Playbook

1) Read status
- get_status_overview (orbit, time, mass), get_stage_plan(env)

2) Navigation
- get_navigation_info (phase angle, AN/DN)

3) Choose goal
- circularize | plane change | raise/lower Ap/Pe | transfer

4) Plan
- Use compute_* helper (burn time, UT anchor, pro/normal/radial)

5) Set and (optionally) warp
- set_maneuver_node(ut, prograde, normal, radial)
- warp_to(ut - burn_time/2)

6) Execute burn (script)
- Point to node vector, throttle to target Δv, feather as Δv approaches 0

Reusable code — execute_next_node (MIT; krpc/krpc-library):
```
def execute_next_node(conn):
    space_center = conn.space_center
    vessel = space_center.active_vessel
    ap = vessel.auto_pilot
    try:
        node = vessel.control.nodes[0]
    except Exception:
        return
    rf = vessel.orbit.body.reference_frame
    ap.reference_frame = rf
    ap.engage()
    ap.target_direction = node.remaining_burn_vector(rf)
    ap.wait()
    m = vessel.mass; isp = vessel.specific_impulse; dv = node.delta_v
    F = vessel.available_thrust; G = 9.81
    burn_time = (m - (m / math.exp(dv / (isp * G)))) / (F / (isp * G))
    space_center.warp_to(node.ut - (burn_time / 2.0) - 5.0)
    while node.time_to > (burn_time / 2.0):
        pass
    ap.wait()
    vessel.control.throttle = thrust_controller(vessel, node.remaining_delta_v)
    while node.remaining_delta_v > 0.1:
        ap.target_direction = node.remaining_burn_vector(rf)
        vessel.control.throttle = thrust_controller(vessel, node.remaining_delta_v)
    ap.disengage(); vessel.control.throttle = 0.0; node.remove()
```

7) Verify orbit; delete any residual nodes

Snippets usage
- Search: snippets_search({"query": "circularize orbit", "k": 5, "mode": "hybrid", "rerank": true})
- Inspect: snippets_get(id, include_code=false); Resolve: snippets_resolve({"id": "<id>"})
- Filter by category (function/class/method) or use exclude_restricted=true per policy.
'''


@mcp.resource("resource://playbooks/maneuver-node")
def get_maneuver_node_playbook() -> str:
    return PLAYBOOK_TEXT


BLUEPRINT_USAGE = (
    "Vessel Blueprint Usage\n\n"
    "Purpose: Provide the agent with a structural understanding of the current vessel to plan safe, effective scripts.\n\n"
    "Recommended Calls:\n"
    "- get_status_overview — confirm scene, body, situation\n"
    "- get_vessel_blueprint — meta, stages (dv/TWR), engines, parts\n"
    "- get_blueprint_ascii — quick human-readable summary (by stage)\n\n"
    "Key Fields:\n"
    "- meta.current_stage — current stage index\n"
    "- stages[] — per-engine-stage Δv/TWR (approximate)\n"
    "- parts[].stage / parts[].decouple_stage — staging order and drop points\n"
    "- engines[] — engine locations (part_id), thrust/Isp\n\n"
    "Checklist Before Staging/Burn:\n"
    "1) Confirm next stage has engines and sufficient propellant (parts with LiquidFuel/Oxidizer/MonoPropellant/SolidFuel).\n"
    "2) Verify TWR > 1 if performing a surface/ascent burn.\n"
    "3) Ensure control capabilities: SAS/Reaction Wheels, RCS if required.\n"
    "4) After staging, refresh blueprint to update structure and dv/TWR.\n\n"
    "Notes:\n"
    "- Stage plan is an approximation; values differ from KSP UI. Use as planning guidance.\n"
    "- Geometry is best-effort; thrust axis and CoM may be unavailable.\n"
    "\nSnippets usage:\n"
    "- For common control patterns (staging, throttle guards, SAS modes), search examples: snippets_search({\"query\": \"throttle stage SAS\", \"k\": 5, \"mode\": \"hybrid\"})\n"
    "- Resolve a minimal helper (function/class) with snippets_resolve and adapt to current vessel blueprint constraints.\n"
)


@mcp.resource("resource://playbooks/vessel-blueprint-usage")
def get_blueprint_usage_playbook() -> str:
    return BLUEPRINT_USAGE


# Additional playbooks

FLIGHT_CONTROL_PLAYBOOK = '''
Flight Control Playbook

1) Establish control state
- get_status_overview; confirm SAS/RCS/throttle

2) Safety checks
- staging readiness, propellant availability, engine status

3) Attitude plan
- target pitch/heading/roll or point to node/target

4) Throttle plan
- TWR targets or specific acceleration profiles; constrain dynamic pressure (max‑Q)

Reusable code — gravity turn pitch program (MIT; krpc/krpc-library):
```
def gravturn(conn, launch_params):
    vessel = conn.space_center.active_vessel
    flight = vessel.flight(vessel.orbit.body.non_rotating_reference_frame)
    progress = flight.mean_altitude / launch_params.grav_turn_finish
    vessel.auto_pilot.target_pitch = 90 - (-90 * progress * (progress - 2))
```

Reusable code — boost apoapsis with gentle throttle (MIT):
```
def boostAPA(conn, launch_params):
    vessel = conn.space_center.active_vessel
    vessel.control.throttle = 0.2
    while vessel.orbit.apoapsis_altitude < launch_params.orbit_alt:
        # optional: staging checks, telemetry logs
        pass
    vessel.control.throttle = 0.0
```

5) Execute control loop (bounded, telemetry-driven); log state
6) Evaluate metrics; adapt or exit with SUMMARY

Snippets usage
- Search (PID hover, ascent control, pitch program): snippets_search({"query": "ascent autopilot PID", "k": 10, "mode": "hybrid", "rerank": true})
- Inspect with snippets_get; resolve focused helpers with snippets_resolve to avoid bloat.
- Filter by category="function" or exclude_restricted=true per policy.
'''


@mcp.resource("resource://playbooks/flight-control")
def get_flight_control_playbook() -> str:
    return FLIGHT_CONTROL_PLAYBOOK


RENDEZVOUS_PLAYBOOK = '''
Rendezvous & Docking Playbook

1) Align planes
- compute_plane_change_nodes; plan burn at AN/DN (execute node)

Reusable code — plane match + execute (MIT):
```
def match_planes(conn):
    sc = conn.space_center; v = sc.active_vessel; t = sc.target_vessel
    if v.orbit.relative_inclination(t) < 0.00436:
        return
    ut_an = v.orbit.ut_at_true_anomaly(v.orbit.true_anomaly_an(t))
    ut_dn = v.orbit.ut_at_true_anomaly(v.orbit.true_anomaly_dn(t))
    time = ut_an if ut_an < ut_dn else ut_dn
    sp = v.orbit.orbital_speed_at(time); inc = v.orbit.relative_inclination(t)
    normal = sp * math.sin(inc); prograde = sp * math.cos(inc) - sp
    if ut_an < ut_dn: normal *= -1
    v.control.add_node(time, normal=normal, prograde=prograde)
    execute_next_node(conn)
```

2) Phase for intercept
- compute_rendezvous_phase_node; set transfer (or use Hohmann transfer helper)

Reusable code — Hohmann transfer (MIT):
```
def hohmann_transfer(vessel, target, time):
    body = vessel.orbit.body; GM = body.gravitational_parameter
    r1 = vessel.orbit.radius_at(time); SMA_i = vessel.orbit.semi_major_axis
    SMA_t = (vessel.orbit.apoapsis + target.orbit.apoapsis) / 2
    v1 = math.sqrt(GM * ((2/r1) - (1 / SMA_i)))
    v2 = math.sqrt(GM * ((2/r1) - (1 / SMA_t)))
    dv = v2 - v1
    return vessel.control.add_node(time, prograde=dv)
```

3) Execute intercept burns; monitor relative speed/distance
4) Approach & docking
- reduce closing speed; align ports; finalize

Snippets usage
- Search rendezvous helpers: snippets_search({"query": "rendezvous docking approach", "k": 10, "mode": "hybrid"})
- Resolve utilities for vector math/approach throttling; prefer minimal functions.
- Use exclude_restricted=true when license policy requires.
'''


@mcp.resource("resource://playbooks/rendezvous-docking")
def get_rendezvous_playbook() -> str:
    return RENDEZVOUS_PLAYBOOK


LAUNCH_ASCENT_CIRC_PLAYBOOK = '''
Launch → Ascent → Circularize Playbook

Purpose: guide GeePT through the SCRIBE loop—observe, plan, execute, and adapt—while delivering a low-Kerbin orbit injection.

Core Loop (see master prompt)
- Check vessel makeup & state.
- Draft a step-by-step plan (gravity turn + circularization).
- Fetch any snippets/docs that de-risk the script.
- Execute one deterministic script with logs + SUMMARY.
- Review telemetry; decide next mission phase or retry.

0) Preflight & Safety
- Tooling warm-up: krpc_get_status; get_status_overview; get_vessel_blueprint (optionally export blueprint diagram).
- Verify staging tree, engine availability, and propellant; throttle=0, SAS/RCS as required.
- Capture baseline telemetry (dynamic_pressure_pa, g_force, current TWR). Abort if anomalies detected.

1) Telemetry Sweep & Mission Plan
- Call get_status_overview to snapshot vessel/environment/orbit/aero/time.
- Use get_engine_status and get_resource_breakdown if staging or propellant margins look uncertain.
- Optional: search_ksp_wiki("gravity turn") or snippets_search for ascent helpers when you need references.
- Draft plan bullets for Commander: launch heading, turn start/end altitudes, target apoapsis/periapsis, throttle envelopes, abort gates.

2) Script Preparation
- Keep loops bounded; call check_time(); add structured log lines.
- Rely on injected globals (`conn`, `vessel`, `sleep`, `math`, `logging`, etc.).
- Pull snippets when useful (e.g., Art Whaley autostage helpers). Respect license filters.
- Decide which constants belong in-script (target altitudes, gains) versus values read live (gravity, thrust, resources).

3) Example GeePT Execution (150 km target)

**Commander prompt**: “Computer, get me to an orbit of 150 km!”

**GeePT thinking**  
- Phase assess: LKO ascent within single script scope.  
- Data request: get_status_overview → confirm we are on pad, mass, available thrust, staging depth.  
- Plan: two-point gravity turn (start 7 km, finish 60 km), throttle feedback via dynamic pressure, reactive circularization burn that hugs apoapsis arrival.  
- Safety: stage only when dry; keep loops under 220 s (ascent) and 180 s (circularize); log every ~2 s.  
- Snippets: leverage stage-dry pattern (adapted from Art Whaley demo); no license conflicts.

**GeePT script**:
```python
log("BEGIN: streamlined 150 km ascent demo")

if vessel is None:
    print("SUMMARY: aborted — no active vessel in scene")
else:
    sc = conn.space_center
    orbit = vessel.orbit
    flight_surface = vessel.flight(vessel.surface_reference_frame)

    TARGET_ALT = 150_000.0
    TURN_START = 7_000.0
    TURN_END = 60_000.0
    TERMINAL_STAGE = 0
    KP_PE = 0.00018  # throttle gain for circularization
    STAGE_FUELS = ("LiquidFuel", "Oxidizer", "SolidFuel")

    def stage_dry():
        if vessel.control.current_stage <= TERMINAL_STAGE:
            return False
        try:
            resources = vessel.resources_in_decouple_stage(
                vessel.control.current_stage - 1,
                cumulative=False,
            )
        except Exception:
            return False
        saw_fuel = False
        for name in STAGE_FUELS:
            try:
                if resources.max(name) > 0.1:
                    saw_fuel = True
                    if resources.amount(name) > 0.5:
                        return False
            except Exception:
                continue
        return saw_fuel

    def maybe_stage(label: str):
        if stage_dry() or vessel.available_thrust < 0.5:
            log(f"STAGE: {label}")
            vessel.control.activate_next_stage()
            sleep(0.5)

    def turn_pitch(alt: float) -> float:
        if alt <= TURN_START:
            return 90.0
        if alt >= TURN_END:
            return 5.0
        fraction = (alt - TURN_START) / (TURN_END - TURN_START)
        return 90.0 - fraction * 85.0

    ap = vessel.auto_pilot
    ap.reference_frame = vessel.surface_reference_frame
    ap.engage()
    ap.stopping_time = (1, 1, 1)
    ap.target_pitch_and_heading(90, 90)

    vessel.control.sas = False
    vessel.control.rcs = False
    vessel.control.throttle = 1.0
    log("ASCENT: throttle up, gravity turn armed")

    ascent_t0 = sc.ut
    while orbit.apoapsis_altitude < TARGET_ALT and sc.ut - ascent_t0 < 220:
        check_time()
        alt = flight_surface.mean_altitude
        ap.target_pitch_and_heading(turn_pitch(alt), 90)
        maybe_stage("ascent burnout")
        if sc.ut % 2 < 0.2:
            log(
                f"ASCENT: alt={alt:.0f}m Ap={orbit.apoapsis_altitude:.0f}m "
                f"stage={vessel.control.current_stage} throttle={vessel.control.throttle:.2f}"
            )
        sleep(0.2)

    vessel.control.throttle = 0.0
    if orbit.apoapsis_altitude < TARGET_ALT - 2_000:
        print(
            f\"\"\"SUMMARY:
phase: streamlined 150km orbit
achieved: false
apoapsis_m: {orbit.apoapsis_altitude:.1f}
periapsis_m: {orbit.periapsis_altitude:.1f}
note: Apoapsis short—Commander, add thrust or flatten the turn sooner.
next_step: Adjust ascent profile and retry.
\"\"\"
        )
        raise SystemExit

    log("COAST: apoapsis reached, throttling down")
    try:
        lead = max((orbit.time_to_apoapsis or 0) - 4.0, 0.0)
        if lead > 0.5:
            sc.warp_to(sc.ut + lead)
    except Exception as exc:
        log(f"WARN: warp skipped ({exc})")

    ap.reference_frame = vessel.orbital_reference_frame
    ap.target_direction = (0, 1, 0)
    try:
        ap.wait()
    except Exception:
        pass

    log("CIRC: prograde burn with reactive throttle")
    burn_t0 = sc.ut
    while sc.ut - burn_t0 < 180:
        check_time()
        pe_error = TARGET_ALT - orbit.periapsis_altitude
        if pe_error <= 0:
            break
        tta = orbit.time_to_apoapsis or 0.0
        throttle_cmd = max(0.2, min(0.95, KP_PE * pe_error))
        if tta > 6.0:
            throttle_cmd = min(throttle_cmd, 0.4)
        elif tta < 2.0:
            throttle_cmd = min(throttle_cmd, 0.25)
        vessel.control.throttle = throttle_cmd
        log(
            f"CIRC: Pe={orbit.periapsis_altitude:.0f}m Ap={orbit.apoapsis_altitude:.0f}m "
            f"tta={tta:.1f}s thrtl={throttle_cmd:.2f}"
        )
        maybe_stage("circularization burnout")
        sleep(0.2)

    vessel.control.throttle = 0.0
    vessel.control.sas = True
    try:
        ap.disengage()
    except Exception:
        pass

    achieved = (
        abs(orbit.apoapsis_altitude - TARGET_ALT) < 4_000
        and abs(orbit.periapsis_altitude - TARGET_ALT) < 4_000
    )
    tta = orbit.time_to_apoapsis or float("nan")
    next_step = (
        "Commander, set transfer node or payload actions."
        if achieved
        else "Commander, re-run ascent with tweaks or add Δv margin."
    )
    print(
        f\"\"\"SUMMARY:
phase: streamlined 150km orbit
achieved: {str(achieved).lower()}
apoapsis_m: {orbit.apoapsis_altitude:.1f}
periapsis_m: {orbit.periapsis_altitude:.1f}
time_to_ap_s: {tta:.1f}
next_step: {next_step}
\"\"\"
    )
```

4) Post-Script Analysis
- Review SUMMARY and log transcript; confirm Δv balance and staging behavior.
- If achieved: tee up maneuver planning (compute_transfer_window_to_body, etc.).
- If shortfall: inspect telemetry (log altitudes, throttle responses). Adjust TURN_START/TURN_END or KP_PE; consider snippets_search for alternate throttle/TWR controllers.
- Optionally save state (save_llm_checkpoint) before iterating.

5) Useful Follow-up Resources
- compute_circularize_node(at='apoapsis') for analytical burn targeting.
- compute_burn_time(dv_m_s) to time warp-to-node precisely.
- get_stage_plan / get_staging_info for deeper Δv accounting.

Notes
- Always respect licensing when ingesting snippets (exclude_restricted=true if needed).
- If MechJeb or other automation mods expose kRPC APIs, consider delegating ascent or circularization but still wrap with GeePT logging and SUMMARY.
'''


@mcp.resource("resource://playbooks/launch-ascent-circularize")
def get_launch_ascent_circ_playbook() -> str:
    return LAUNCH_ASCENT_CIRC_PLAYBOOK


STATE_CHECKPOINT_PLAYBOOK = '''
State Checkpoint & Rollback Playbook

Purpose: Create safe restore points during missions and reliably roll back when needed. This complements the execute pipeline (unpause at start, pause at end).

When to checkpoint
- Before irreversible actions: liftoff, circularization, transfer ejection, capture, de‑orbit/landing.
- Before complex sequences or when testing new logic.

Naming & policy
- Use save_llm_checkpoint to create unique, namespaced saves (LLM_YYYYmmddTHHMMSSZ_<tag>_<id>), so gamer saves aren’t touched.
- Only load LLM_ saves (default safeguard); avoid quicksave/quickload unless you know you want to override the single quickslot.

Core tools
- Save: save_llm_checkpoint({"address":"<IP>", "tag":"pre_circ"}) → { ok, save_name }
- Load (auto‑pause): load_llm_checkpoint({"address":"<IP>", "save_name":"LLM_..."})
  • After load, the game is paused; UT won’t advance until you resume. The execute_script tool unpauses on start and pauses again on end.
- Quick save/load (fallback): quicksave({"address":"<IP>"}), quickload({"address":"<IP>"})
  • Caution: these operate on the single quicksave slot; prefer named LLM checkpoints.
- Revert flight to pad: revert_to_launch({"address":"<IP>"})
  • Use to restart quickly after a failed attempt.

Reference sequence
1) Snapshot state:
   - get_status_overview({"address":"<IP>"})
   - export_blueprint_diagram({"address":"<IP>", "format":"svg"})
2) Save checkpoint:
   - save_llm_checkpoint({"address":"<IP>", "tag":"pre_circ"}) → record save_name
3) Proceed with operations or execute_script (auto‑unpause on start).
4) If results are bad, load back:
   - load_llm_checkpoint({"address":"<IP>", "save_name":"LLM_..."})  # auto‑pause after load
   - Verify pause: get_time_status — UT should not advance while paused
   - Resume with execute_script (which unpauses) or continue with interactive steps

Tips
- Use descriptive tags: pre_ascent, pre_circ, pre_transfer, pre_capture, pre_deorbit.
- Keep a small chain of recent checkpoints so you can step back more than one phase.
- For quick resets from flight tests, revert_to_launch is fastest.
'''


@mcp.resource("resource://playbooks/state-checkpoint-rollback")
def get_state_checkpoint_playbook() -> str:
    return STATE_CHECKPOINT_PLAYBOOK
