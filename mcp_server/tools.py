from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .jobs import JobStatus, job_registry
from .server import mcp
from krpc_index import KRPCSearchIndex, load_dataset


_INDEX: KRPCSearchIndex | None = None


def _get_index() -> KRPCSearchIndex:
    global _INDEX
    if _INDEX is None:
        base = Path(__file__).resolve().parents[1]
        data_path = base / "data" / "krpc_python_docs.jsonl"
        docs = load_dataset(data_path)
        _INDEX = KRPCSearchIndex(docs)
    return _INDEX


@mcp.tool()
def search_krpc_docs(query: str, limit: int = 10) -> str:
    """
    Search the kRPC Python docs (plus Welcome/Getting Started/Tutorials) and return the top results.
    When to use:
        - Explore kRPC APIs, examples, or concepts before implementing a call.
    Args:
        query: Free-text query
        limit: Max results to return (default 10)
    Returns:
        A newline-delimited list of formatted results with title and URL and a short snippet.
    """
    idx = _get_index()
    results = idx.search(query, top_k=max(1, min(limit, 25)))
    if not results:
        return "No results found."
    lines: List[str] = []
    for doc, score, snippet in results:
        title = doc.title or "(untitled)"
        lines.append(f"- {title} — {doc.url}\n  {snippet}")
    return "\n".join(lines)


@mcp.tool()
def get_krpc_doc(url: str, max_chars: int = 5000) -> str:
    """
    Retrieve a kRPC doc page by URL and return its text content. Use with URLs from search_krpc_docs.
    When to use:
        - Pull the full text of a doc page to inspect details and examples.
    Args:
        url: Exact page URL from the dataset
        max_chars: Truncate returned content to this many characters (default 5000)
    Returns:
        Title, URL, and cleaned page text (truncated) with basic headings metadata.
    """
    idx = _get_index()
    doc = idx.get(url)
    if not doc:
        return "Not found. Ensure the URL matches a search result."
    heads = ", ".join(h for h in doc.headings[:10])
    body = (doc.content_text or "").strip()
    if len(body) > max_chars:
        body = body[: max_chars - 1].rstrip() + "…"
    return f"{doc.title}\n{doc.url}\n\nHeadings: {heads}\n\n{body}"


@mcp.tool()
def get_job_status(job_id: str) -> str:
    """
    Poll the status of a background job started by tools such as start_part_tree_job.

    Usage pattern:
        1. Call the job-starting tool (e.g., start_part_tree_job) which returns a job_id.
        2. Poll get_job_status(job_id) until "status" == "SUCCEEDED".
        3. If "status" == "FAILED", inspect the logs and error message to diagnose.

    Returns:
        JSON string with fields:
            - job_id: the requested identifier
            - status: PENDING | RUNNING | SUCCEEDED | FAILED (or UNKNOWN when not found)
            - created_at / started_at / finished_at timestamps (ISO 8601, UTC) when available
            - logs: accumulated stdout/stderr/log entries
            - result_resource: resource URI containing the job output, if produced
            - error: error description when failed or unknown
            - metadata: any job-specific metadata stored at creation time
            - ok: boolean convenience flag (false when FAILED or UNKNOWN)
    """
    state = job_registry.get_state(job_id)
    if state is None:
        payload = {
            "job_id": job_id,
            "status": "UNKNOWN",
            "error": "Job not found. Ensure you called a job-starting tool first.",
            "logs": [],
            "result_resource": None,
            "metadata": {},
            "ok": False,
        }
        return json.dumps(payload)

    payload = state.as_dict()
    payload["ok"] = state.status != JobStatus.FAILED
    return json.dumps(payload)
