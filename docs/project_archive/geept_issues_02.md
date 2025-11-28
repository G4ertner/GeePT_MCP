# GeePT Issues

## Issue 1: ConnectionResetError noise while polling job status
- **Summary:** While monitoring a running execute_script job, get_job_status repeatedly reports ConnectionResetError [WinError 10054] in the logs even though the job stays alive and keeps streaming new INFO entries. This makes it unclear whether the job is actually running or if the MCP channel has been severed.
- **Tool:** get_job_status
- **Arguments:** {"job_id": "bbea7ec7f8154654ba7e2d2d612b07d5"}
- **Return:** JSON showing the job is still RUNNING, `ok: true`, `result_resource: null`, plus repeated log lines ending with ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host before additional log entries kept arriving.
- **Screenshot:** artifacts/screenshots/1.png
- **Steps to Reproduce:**
  1. Start any long-running execute_script job (e.g., bbea7ec7f8154654ba7e2d2d612b07d5).
  2. Call get_job_status while the job is still running.
  3. Observe the log stream emitted in the response; the ConnectionResetError message appears even though status stays RUNNING and subsequent logs keep streaming.
- **Observed:** The get_job_status response includes interruptive ConnectionResetError tracebacks from the MCP server, implying the channel dropped even though work continues; the error never appears resolved and floods the log section.
- **Expected:** get_job_status should report clean log output for a running job without ConnectionResetError, or at least surface a structured error flag if the tool cannot reliably report status.
- **Additional Notes:** The job eventually continues streaming INFO Processing request of type CallToolRequest, but the repeated network errors cast doubt on tool reliability and clutter the diagnostics output, complicating issue triage.

## Issue 2: Noisy get_job_status output during live script
- **Summary:** While closely checking the same live execute_script burn, repeated `ConnectionResetError [WinError 10054]` stack traces keep appearing inside `get_job_status` even though the return value is `RUNNING` and subsequent logs continue flowing, making the telemetry dump feel unreliable.
- **Tool:** get_job_status
- **Arguments:** {"job_id": "bbea7ec7f8154654ba7e2d2d612b07d5"}
- **Return:** JSON showing `status: RUNNING`, `ok: true`, `result_resource: null`, and log entries alternating between `INFO ... Processing request of type ...` and `ERROR ... ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host`.
- **Screenshot:** artifacts/screenshots/2.png
- **Steps to Reproduce:**
  1. Launch a long-running execute_script job (this one is still climbing toward apoapsis).
  2. Repeatedly call get_job_status during the active burn.
  3. Watch the log array include intermittent WinError 10054 stack traces even while the job remains RUNNING.
- **Observed:** The MCP log array is flooded with asynchronous connection-close stack traces that coexist with legit INFO entries, which makes it hard to tell if the tool is functional or the job lost contact.
- **Expected:** get_job_status should either suppress the transient network noise or flag it separately so the pumping log stream stays focused on mission telemetry.
- **Additional Notes:** The repeated noise increases during heavy mission phases, so the screenshot records the current game frame for reference while the tool noise keeps spamming logs.
