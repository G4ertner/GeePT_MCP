# Background job + polling workflow for long-running tools

Codex CLI terminates tool calls that run longer than ~60 seconds. To keep `get_part_tree` and `get_stage_plan` usable on large vessels, roll out a background job + polling pattern that lets the CLI fire-and-forget the heavy work and poll for results.

## Step-by-step rollout plan

**Goal:** deliver a background job workflow for `get_stage_plan` and `get_part_tree`, validate it end-to-end, then extend it to `execute_script` once proven.

1. **Lay down shared job infrastructure** (done)
   - Added `mcp_server/jobs.py` with a thread-safe registry (`dict[job_id, JobState]`), UUID generation, stdout/stderr capture, and status enums (`PENDING`, `RUNNING`, `SUCCEEDED`, `FAILED`).
   - Automated test: unit-test the registry lifecycle using a fake executor to cover state transitions, log buffering, and resource URL attachment.
   - Manual test: run a REPL against the registry helper to enqueue a dummy job and verify status/log updates progress as expected.

2. **Define the polling tool contract** (done)
   - Introduced `get_job_status(job_id: str)` in `mcp_server/tools.py` that reads from the registry and returns JSON with status, optional `result_resource`, and accumulated logs. The docstring now instructs agents to poll until `status == "SUCCEEDED"`.
   - Automated test: added a tools test that seeds the registry with synthetic jobs and asserts the serialized payload structure.
   - Manual test: start the MCP server, call `get_job_status` for an unknown ID (expect a clear error), then for a live job to watch status progression.

3. **Wrap the heavy readers in job starters** (done)
   - Created `start_part_tree_job` and `start_stage_plan_job` tools that enqueue callables invoking `readers.part_tree` / `readers.stage_plan_approx`, write outputs to `artifacts/jobs/<job_id>.json`, register the resources, and capture incremental logs.
   - Automated test: added integration tests with stubbed readers confirming job completion yields resource handles and artifacts.
   - Manual test: run both job starters against a sample save, poll via `get_job_status`, and download the JSON to confirm completeness.

4. **Describe the new usage pattern to the LLM** (done)
   - Updated each job tool docstring to emphasize "start -> poll -> read_resource" and documented log semantics.
   - Amended `SCRIBE_Master_Prompt_KSP_MCP.md` with a subsection outlining the workflow and tool names.
   - Manual test: reviewed the updated prompt/docstrings in the repo to confirm clarity and placement.

5. **Revise Codex playbooks / user docs** (done)
   - Updated the vessel blueprint playbook (`resource://playbooks/vessel-blueprint-usage`) and README tooling section with the explicit `start_*_job -> get_job_status -> read_resource` workflow plus failure-handling notes.
   - Manual test: reviewed the rendered playbook resource/README to confirm the steps are visible for agents and operators.

6. **Integration smoke test**
   - Run the MCP server, kick off both jobs, poll them to completion, and fetch the exported JSON via `read_file` to verify the timeout no longer interrupts the flow.
   - Automated test: add a scripted smoke test (e.g., under `scripts/`) that drives the new tools against stubbed readers and asserts end-to-end success within CI time limits.
   - Manual test: replicate the scenario with the Codex CLI to ensure real-world behavior matches expectations and log streaming remains continuous.

7. **Extend to `execute_script`**
   - Introduce `start_execute_script_job` once the pattern stabilizes, reusing shared helpers to stream stdout/stderr into job logs and capture the final result resource.
   - Automated test: cover the script-specific job path with a stub script runner that emits interleaved stdout/stderr, verifying log ordering and resource registration.
   - Manual test: run a long-lived script via the new job starter, observe log updates through polling, and download the final artifacts.

Following these steps keeps the rollout incremental: infrastructure ships first, `get_stage_plan`/`get_part_tree` gain job starters for validation, and only then is `execute_script` migrated.


  1. Map the current script pipeline
      - Audit mcp_server/executor_tools.py and any helper modules (parsers, subprocess runner) to understand how code is
        launched, how stdout/stderr are captured, and where pausing/unpausing occurs.
      - Identify reusable pieces that both the existing synchronous execute_script and the upcoming job version can
        share (e.g., config generation, subprocess invocation, result parsing).
  2. Extend the job infrastructure for cancellation & streaming
      - Enhance JobRegistry (or layer atop it) with optional “termination handles,” so certain jobs can be cancelled
        mid-flight.
      - Define a job_cancellations map storing per-job callbacks/events. When cancel_job(job_id) (new tool) is invoked,
        set a cancellation flag and run the registered callback (for scripts, this will terminate the subprocess).
      - Ensure _LogStream/append_log already provide incremental log lines; verify they’ll handle high-volume script
        output without blocking.
  3. Refactor script execution core for reuse
      - Factor the guts of execute_script into a helper that can either run synchronously (legacy tool) or under a job
        wrapper.
      - The helper should expose hooks for:
        a. Feeding live stdout/stderr lines into job_handle.log(...) as they appear.
        b. Emitting periodic status updates (e.g., “script running…”, “SUMMARY detected”).
        c. Accepting an external cancellation event so we can halt the subprocess cleanly.
  4. Implement start_execute_script_job tool
      - API mirrors execute_script arguments (code, address, timeout flags, etc.) plus optional job_note.
      - Job function spins up the refactored executor helper, wiring stdout/stderr to log-stream callbacks, and saves
        the final JSON result to artifacts/jobs/<job_id>.json (same pattern as other jobs).
      - On any failure/cancellation, mark the job FAILED with error payload so get_job_status reports a clear reason.
  5. Add cancel_job / stop_execute_script_job tool
      - Provide a user-facing MCP tool (likely general-purpose cancel_job(job_id)) that:
        • Validates the job exists and is cancellable.
        • Invokes the stored cancel callback (terminating the script subprocess, pausing KSP if needed).
        log lines, and result_resource once the script completes.
      - Refresh docstrings, SCRIBE prompt, README, and any playbooks to mention the new start_execute_script_job +
        cancel_job flow and reiterate the start→poll→read_resource pattern (plus when to abort).
      - Highlight that for short scripts, the legacy execute_script still exists, but long or risky burns should use the
        job version.
  7. Testing & validation
        • Launch an actual script job against KSP, poll get_job_status to confirm logs stream and artifact is readable.
        • Trigger cancel_job mid-script (e.g., while throttling) to ensure the rocket can be saved and the job reports
        cancellation cleanly.
