"""Shared FastMCP instance used across the server modules."""

from mcp.server.fastmcp import FastMCP

from mcp_server.injection import apply_injection_support, injection_store

__all__ = ["mcp"]


# A single FastMCP instance is reused everywhere to avoid circular imports.
mcp = FastMCP("geept_mcp")
apply_injection_support(mcp, injection_store)
