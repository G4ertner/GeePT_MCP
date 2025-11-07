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
