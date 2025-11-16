from __future__ import annotations

from functools import wraps

from .mcp_context import mcp
from .library_impl import krpc_docs, ksp_wiki, snippets


@mcp.tool()
@wraps(krpc_docs.search_krpc_docs_impl)
def search_krpc_docs(query: str, limit: int = 10) -> str:
    return krpc_docs.search_krpc_docs_impl(query=query, limit=limit)


@mcp.tool()
@wraps(krpc_docs.get_krpc_doc_impl)
def get_krpc_doc(url: str, max_chars: int = 5000) -> str:
    return krpc_docs.get_krpc_doc_impl(url=url, max_chars=max_chars)


@mcp.tool()
@wraps(krpc_docs.get_job_status_impl)
def get_job_status(job_id: str) -> str:
    return krpc_docs.get_job_status_impl(job_id=job_id)


@mcp.tool()
@wraps(krpc_docs.cancel_job_impl)
def cancel_job(job_id: str, reason: str | None = None) -> str:
    return krpc_docs.cancel_job_impl(job_id=job_id, reason=reason)


@mcp.tool()
@wraps(ksp_wiki.search_ksp_wiki_impl)
def search_ksp_wiki(query: str, limit: int = 10) -> str:
    return ksp_wiki.search_ksp_wiki_impl(query=query, limit=limit)


@mcp.tool()
@wraps(ksp_wiki.get_ksp_wiki_page_impl)
def get_ksp_wiki_page(title: str, max_chars: int = 5000) -> str:
    return ksp_wiki.get_ksp_wiki_page_impl(title=title, max_chars=max_chars)


@mcp.tool()
@wraps(ksp_wiki.get_ksp_wiki_section_impl)
def get_ksp_wiki_section(title: str, heading: str, max_chars: int = 3000) -> str:
    return ksp_wiki.get_ksp_wiki_section_impl(title=title, heading=heading, max_chars=max_chars)


@mcp.tool()
@wraps(snippets.snippets_search_impl)
def snippets_search(query: str, k: int = 10, mode: str = "keyword", and_logic: bool = False, category: str | None = None, exclude_restricted: bool = False, rerank: bool = False) -> str:
    return snippets.snippets_search_impl(query=query, k=k, mode=mode, and_logic=and_logic, category=category, exclude_restricted=exclude_restricted, rerank=rerank)


@mcp.tool()
@wraps(snippets.snippets_get_impl)
def snippets_get(id: str, include_code: bool = False) -> str:
    return snippets.snippets_get_impl(id=id, include_code=include_code)


@mcp.tool()
@wraps(snippets.snippets_resolve_impl)
def snippets_resolve(id: str | None = None, name: str | None = None, max_bytes: int = 25000, max_nodes: int = 25) -> str:
    return snippets.snippets_resolve_impl(id=id, name=name, max_bytes=max_bytes, max_nodes=max_nodes)


@mcp.tool()
@wraps(snippets.snippets_search_and_resolve_impl)
def snippets_search_and_resolve(query: str, k: int = 10, mode: str = "hybrid", rerank: bool = False, and_logic: bool = False, category: str | None = None, exclude_restricted: bool = False, max_bytes: int = 25000, max_nodes: int = 25) -> str:
    return snippets.snippets_search_and_resolve_impl(query=query, k=k, mode=mode, rerank=rerank, and_logic=and_logic, category=category, exclude_restricted=exclude_restricted, max_bytes=max_bytes, max_nodes=max_nodes)


@mcp.resource("resource://snippets/usage")
@wraps(snippets.get_snippets_usage_impl)
def get_snippets_usage() -> str:
    return snippets.get_snippets_usage_impl()
