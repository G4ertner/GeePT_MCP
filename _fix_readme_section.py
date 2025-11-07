from pathlib import Path
path = Path('README.md')
text = path.read_text(encoding='utf-8')
start = text.index('- get_part_tree')
end = text.index('#### ?? Orbit & Navigation Info', start)
new = '''- get_part_tree - Hierarchical part tree with resources.
- get_stage_plan - Stock-like stage plan (thrust, Isp, \u0394v).
- get_staging_info - Per-stage \u0394v/TWR estimates.
- export_blueprint_diagram - Exports a 2D blueprint diagram (SVG/PNG).
- start_part_tree_job / start_stage_plan_job - Kick off background jobs that produce the same JSON artifacts without hitting tool timeouts.
- get_job_status - Polls job state/logs and exposes the esult_resource URI once the artifact is ready.

**Background job workflow (long-running tooling)**
1. Call a start_*_job tool with the usual kRPC address/ports; it responds with { job_id, status, note }.
2. Poll get_job_status(job_id) until status becomes "SUCCEEDED" (or "FAILED" for troubleshooting). Logs accumulate while the job runs.
3. When the job succeeds, call read_resource on the reported esult_resource (e.g., esource://jobs/<id>.json) to download the artifact.
4. Use the artifact in your planning loop. If the job failed, read the logs/error, fix the underlying issue, and restart the job.

'''
text = text[:start] + new + text[end:]
path.write_text(text, encoding='utf-8')
