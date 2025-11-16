"""Shared FastMCP instance used across the server modules."""

from mcp.server.fastmcp import FastMCP

__all__ = ["mcp"]


# A single FastMCP instance is reused everywhere to avoid circular imports.
mcp = FastMCP("krpc_docs")
