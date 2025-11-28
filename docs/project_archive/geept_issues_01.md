# geept_mcp Tool Issues



## Issue 1 â Connection reset storm while polling the script job

- **Tool called:** `get_job_status`

- **Arguments:** `{"job_id": "fb67d91d653d431e8f271e1f6b3d2158"}`

- **Return:** JSON payload with `status: "RUNNING"` and log entries such as `ERROR ... ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host` repeated every few seconds while waiting for the job to finish.

- **Observed:** Every poll floods the log with `ConnectionResetError` stack traces, which meant I could not safely monitor progress and had to keep pulling `get_job_status` longer than expected.

- **Expected:** The tool should hold a stable connection long enough to report the job's stdout/stderr without throwing repeated connection resetsâbasically the job status should settle instead of continuously returning low-level socket errors.

- **Screenshot:** `resource://screenshots/ksp_screenshot_20251126T012840Z.png`



## Issue 2 â Hard timeout stops the ascent job before completion

- **Tool called:** `start_execute_script_job`

- **Arguments:** `{"code": "<Stage-1 ascent/circularization script>", "hard_timeout_sec": 150, "timeout_sec": 120, "address": "127.0.0.1", "rpc_port": 50000, "stream_port": 50001}`

- **Return:** Job result JSON with `ok: false`, `paused: true`, `pre_pause_flight` at ~56 km altitude, and `stderr` containing `TimeoutError: Script exceeded timeout budget`. The follow-up recommended calling `get_diagnostics`, which was executed.

- **Observed:** The job was terminated by the 120â¯s soft timeout before the ascent/circularization loops could complete despite the `hard_timeout_sec` being 150â¯s, so the stage could not finish.

- **Expected:** When I provide a longer runtime budget (hard timeout 150), the tool should let the script to keep running beyond 120â¯s or at least warn me that the soft timeout is shorter than the burn expected duration; I need the job to reach orbit before the watchdog aborts it.

- **Screenshot:** `resource://screenshots/ksp_screenshot_20251126T012859Z.png`



## Issue 3 Æ?" Import restrictions even for standard library

- **Tool called:** `start_execute_script_job`

- **Arguments:** `{"code": "<Stage-1a liftoff script that imports math>", "hard_timeout_sec": 120, "timeout_sec": 60, "address": "127.0.0.1", "rpc_port": 50000, "stream_port": 50001}`

- **Return:** Job result JSON where the stdout/stderr block contains `ImportError: Imports are restricted to stdlib/site-packages. Set allow_imports=true to fully enable.` and the `[[[EXEC_META]]]` block reports `ok: false` before the script ran.

- **Observed:** The job aborts immediately because the script tried to `import math`, preventing me from using harmless standard library helpers even though only a tiny, safe piece of Python was required.

- **Expected:** Standard library modules such as `math` should be usable without flipping extra flags, or the restriction should be communicated up front; otherwise the tooling cannot support basic calculation logic.

- **Screenshot:** `resource://screenshots/ksp_screenshot_20251126T013412Z.png`



## Issue 4  Status polling collapses during high-burn job

- **Tool called:** `get_job_status`

- **Arguments:** `{"job_id": "5e13eb60ef684504b43c136ebb58a310"}`

- **Return:** JSON payload showing `status: "RUNNING"` but the log array is dominated by repeated `ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host` stack traces (from `asyncio.base_events`/`proactor_events.py`), with no steady progress entries from the running script.

- **Observed:** Every `get_job_status` call returns only the same connection-reset traces, preventing me from verifying whether the circularization burn is underway, so I had to interrupt the job manually.

- **Expected:** `get_job_status` should return the scripts own stdout/stderr and eventual terminal status without the network channel blinking with repeated socket errors when the job itself is healthy.

- **Screenshot:** `resource://screenshots/ksp_screenshot_20251126T014427Z.png`
 
## Issue 5 – Logging an arrow char trips the stdout logger
- **Tool called:** `start_execute_script_job`
- **Arguments:** `start_execute_script_job` (code: `<Stage 1a continuation with gravity-turn helper>`, `hard_timeout_sec`: 120, `timeout_sec`: 90, `name`: `stage1a_continuation`, `unpause_on_start`: true)
- **Return:** Job finished `ok: false` after 90s with `stderr` showing a `UnicodeEncodeError` from `cp1252` while logging `STAGE: detected low thrust -> activating next stage`, plus the timeout diagnostic (pre-pause flight alt ~93 km, peri still negative).
- **Observed:** Calling `log()` with a single arrow symbol (`->`) makes the MCP logging backend throw `'charmap' codec can't encode character '\u2192'` and floods the transcript with stack traces even though the burn itself remains healthy.
- **Expected:** Logging should sanitize or escape non-encodable characters (or fall back to ASCII) so that harmless symbols like arrows do not crash the logger and pollute the transcript.
- **Screenshot:** `resource://screenshots/ksp_screenshot_20251126T021214Z.png`
