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
