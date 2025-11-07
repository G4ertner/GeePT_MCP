# Background job + polling workflow for long-running tools

Codex CLI terminates tool calls that run longer than ~60 seconds. To keep `get_part_tree` and `get_stage_plan` usable on large vessels, roll out a background job + polling pattern that lets the CLI fire-and-forget the heavy work and poll for results.

## Step-by-step rollout plan

**Goal:** deliver a background job workflow for `get_stage_plan` and `get_part_tree`, validate it end-to-end, then extend it to `execute_script` once proven.

1. **Lay down shared job infrastructure** (done)
   - Added `mcp_server/jobs.py` with a thread-safe registry (`dict[job_id, JobState]`), UUID generation, stdout/stderr capture, and status enums (`PENDING`, `RUNNING`, `SUCCEEDED`, `FAILED`).
   - Automated test: unit-test the registry lifecycle using a fake executor to cover state transitions, log buffering, and resource URL attachment.
   - Manual test: run a REPL against the registry helper to enqueue a dummy job and verify status/log updates progress as expected.

2. **Define the polling tool contract**
   - Introduce `get_job_status(job_id: str)` in `mcp_server/tools.py` that reads from the registry and returns JSON with status, optional `result_resource`, and accumulated logs. Include a docstring instructing agents to poll until `status == "SUCCEEDED"`.
   - Automated test: add a lightweight tools test that seeds the registry with synthetic jobs and asserts the serialized payload structure.
   - Manual test: start the MCP server, call `get_job_status` for an unknown ID (expect a clear error), then for a live job to watch status progression.

3. **Wrap the heavy readers in job starters**
   - Create `start_part_tree_job` and `start_stage_plan_job` tools that enqueue callables invoking `readers.part_tree` / `readers.stage_plan_approx`, write outputs to `artifacts/jobs/<job_id>.json`, register the resources, and capture incremental logs.
   - Automated test: write a small integration test with stubbed readers to ensure job completion emits a resource handle and log trail.
   - Manual test: run both job starters against a sample save, poll via `get_job_status`, and download the JSON to confirm completeness.

4. **Describe the new usage pattern to the LLM**
   - Update each new tool docstring to emphasize "this call starts a job; poll `get_job_status`" and document log accumulation semantics.
   - Amend `SCRIBE_Master_Prompt_KSP_MCP.md` with a subsection outlining the start -> poll -> download workflow and listing the relevant tool names.
   - Automated test: extend the prompt/doc lint script (or add one) that scans for the job tool docstrings and prompt section to guarantee phrasing is present.
   - Manual test: review the updated prompt in the MCP UI or text editor to confirm clarity and placement.

5. **Revise Codex playbooks / user docs**
   - Update the blueprint retrieval playbook (in `artifacts/` or `knowledge_tools.md`) to show the exact command sequence for fetching staging plans via jobs, including failure-handling guidance.
   - Automated test: run the documentation link checker or markdown linter to ensure references resolve and formatting passes CI.
   - Manual test: follow the playbook instructions locally to confirm the flow works for a large vessel.

6. **Integration smoke test**
   - Run the MCP server, kick off both jobs, poll them to completion, and fetch the exported JSON via `read_file` to verify the timeout no longer interrupts the flow.
   - Automated test: add a scripted smoke test (e.g., under `scripts/`) that drives the new tools against stubbed readers and asserts end-to-end success within CI time limits.
   - Manual test: replicate the scenario with the Codex CLI to ensure real-world behavior matches expectations and log streaming remains continuous.

7. **Extend to `execute_script`**
   - Introduce `start_execute_script_job` once the pattern stabilizes, reusing shared helpers to stream stdout/stderr into job logs and capture the final result resource.
   - Automated test: cover the script-specific job path with a stub script runner that emits interleaved stdout/stderr, verifying log ordering and resource registration.
   - Manual test: run a long-lived script via the new job starter, observe log updates through polling, and download the final artifacts.

Following these steps keeps the rollout incremental: infrastructure ships first, `get_stage_plan`/`get_part_tree` gain job starters for validation, and only then is `execute_script` migrated.
