# Perfect Reentry Playbook

## Mission Summary
- **Target:** Operate the trimmed vessel out of its ~220×223 km Kerbin orbit and land the heat-shielded capsule near KSC (0° lat/0° lon).
- **Propellant budget:** The remaining vacuum stage (RE-L10 Poodle) sports roughly 876 LF/1 071 Ox and ~2 553 m/s Δv, sufficient for the retro burn plus a short adjustment. Your extra surface booster has already been removed.
- **Readiness:** SAS remains enabled; always call `set_sas_mode('retrograde', reference_frame=vessel.orbital_reference_frame)` before burns/entry so the navball’s retrograde marker matches the actual vector.

## Vessel Snapshot
- Mass ~29.7 t; only the vacuum engine/tank stage and the capsule with heat shield/parachute stack remain thanks to the latest quicksave.
- Reaction wheels/RCS units are ready for attitude corrections; ~30 units of monopropellant stay available for fine alignment nudges.
- Only the capsule’s stage 0 plus the engine stage are left, so staging down before the atmosphere automatically exposes the heat shield and parachutes.

## Pre-Burn Checklist
1. Use the set_sas_mode helper to align SAS in the orbital reference frame on the retrograde hold, and wait for it to finish rotating.
2. Confirm the stage plan shows stage 2 as the active engine stage with propellant and that stage 1 is empty or staged; record `current_stage` so the burn is fired in the right stage.
3. Ensure throttle is zero, RCS is off, and heat shield/parachute decouplers (stage 1 and stage 0) are armed.
4. Record the heading and pitch differences relative to the retrograde vector so the next step can show we are nose-forward.

## Reentry Procedure
1. **Retro Burn (target periapsis 25–35 km).**
   - Keep SAS locked via set_sas_mode in the orbital reference frame, keep throttle low (0.18–0.35) until heading/pitch error is within 10 degrees of the retrograde vector, and throttle down to about 0.12 if the error grows.
   - Log orientation errors approximately every five seconds using check_time in the loop.
   - When periapsis reads between 25 and 35 km, cut throttle and stage down to the capsule immediately by firing any remaining stages above stage 0.

2. **Entry Prep (80–90 km, we want ~3–4 minutes lead).**
   - Warp to roughly 220 seconds before periapsis, keep SAS locked in vessel.orbital_reference_frame, and reestablish the retrograde heading.
   - Confirm the heat shield is the only leading surface and only stage 0 remains active.
   - Log heading/pitch error values and ensure they stay under about 10 degrees before hitting the atmosphere.

3. **Atmospheric Capture (70–30 km).**
   - Keep throttle at zero and maintain the retrograde hold by persistently calling set_sas_mode in the orbital frame.
   - Monitor dynamic pressure and g-force; if either spikes, verify the orientation error and relax the target if needed to keep from tumbling.
   - At about 9 km, stage the heat shield decoupler once heating dies down and log that event.

4. **Chute Sequence (<4 km).**
   - After the heat shield is off and nose is retrograde, activate stage 0 once vertical speed is manageable for parachute deployment.
   - Allow drogue and main chutes to deploy sequentially through staging and confirm each deployment via log output.
   - Keep SAS on briefly to keep the nose upward as the chutes catch the airflow.

5. **Landing & Recovery.**
   - Time the entry corridor to fly over KSC, log touchdown latitude and longitude, and compute the surface distance back to 0° lat/0° lon.
   - After touchdown, close off decouplers and produce a SUMMARY block stating the periapsis, touchdown coordinates, distance to KSC, and any anomalies.

## Safeguards & Lessons
- Always call set_sas_mode('retrograde', reference_frame=vessel.orbital_reference_frame) before burns or entry; the default frame may interpret retrograde as a normal or radial axis.
- Compare heading and pitch directly to flight.retrograde rather than to flight.prograde so the guard cannot see a 180-degree difference.
- Stage off every booster above the capsule immediately after the retro burn so the heat shield faces the flow.
- Log heading error, pitch error, periapsis, apoapsis, and current stage at key events so the next LLM can determine the ship’s state precisely.

## Iterations & Refinements
1. **Import lockdown:** The initial script failed because imports were disabled; enabling imports solved that.
2. **Burn timing:** Waiting for a perfect ground track meant no burn; limit the wait to about 60 seconds.
3. **Burn guard:** Without a max-burn guard the craft tumbled into a long ellipse; add clamps on throttle/time and log the periapsis.
4. **Omega math:** The omega_rel divider hit zero for certain orbits; validate the period and fallback to defaults before dividing.
5. **Retro discipline:** Early burns fired prograde and pushed the craft away; force the autopilot to hold the retrograde vector before throttle.
6. **Throttling:** Orientation logs trimmed periapsis to ~31.7 km, but the max-burn guard triggered; consider multi-pass burns with heat warnings.
7. **Frame alignment:** Targeting pitch/heading now proves the craft is aligned; autopilot maintains flight.retrograde before the burn.
8. **Stage drop:** Every attempt now stages down so only the capsule and heat shield remain before entry.
9. **Descent automation (in progress):** The entry script must use the orbital frame for both the autopilot and logs; the previous attempt canceled before touchdown.
10. **Burn retry:** The latest burn stalled with repeated heading errors; set a shorter max burn (~40 seconds) and log key metrics every 6 seconds to know if the run should be restarted.

## Next Steps
- **Burn test:** Rerun the retro burn script with these rules, confirm periapsis lands between 25–35 km, and verify only the capsule remains.
- **Entry test:** Once the burn is clean, execute the aligned entry/descent script, log each event, and capture a final SUMMARY showing touchdown coordinates and distance to KSC.
