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
