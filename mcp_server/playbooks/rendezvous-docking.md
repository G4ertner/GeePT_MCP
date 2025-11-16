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
