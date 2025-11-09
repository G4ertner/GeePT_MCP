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
