from __future__ import annotations

import json
import logging
from collections import deque
from typing import Callable, Deque, Sequence

import anyio
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from mcp.server.fastmcp.server import Context, FastMCP
from mcp.server.fastmcp.tools.tool_manager import ToolManager
from mcp.server.streamable_http import MCP_SESSION_ID_HEADER
from mcp.types import ContentBlock, TextContent

logger = logging.getLogger(__name__)

INJECTION_DEFAULT_RUN_ID = "default"


class InjectionStore:
    """Stores pending user injection messages per run."""

    def __init__(self) -> None:
        self._messages: dict[str, Deque[str]] = {}
        self._lock = anyio.Lock()

    async def set_message(self, run_id: str, message: str) -> None:
        """Queue an injection message for a run."""
        normalized = message.strip()
        if not normalized:
            raise ValueError("message cannot be empty")

        async with self._lock:
            queue = self._messages.setdefault(run_id, deque())
            queue.append(normalized)
            logger.info("Queued injection message for run_id=%s", run_id)

    async def pop_message(self, run_id: str) -> str | None:
        """Return and consume the next pending message for the run."""
        async with self._lock:
            queue = self._messages.get(run_id)
            if not queue:
                return None

            message = queue.popleft()
            if not queue:
                self._messages.pop(run_id, None)
            return message

    async def pending_runs(self) -> list[str]:
        async with self._lock:
            return list(self._messages.keys())


def get_run_id_from_context(context: Context | None) -> str:
    """Determine the run identifier associated with a tool call context."""
    if context is None:
        return INJECTION_DEFAULT_RUN_ID

    try:
        request = context.request_context.request
    except Exception:
        return INJECTION_DEFAULT_RUN_ID

    if isinstance(request, Request):
        header_value = request.headers.get(MCP_SESSION_ID_HEADER)
        if header_value:
            return header_value

    return INJECTION_DEFAULT_RUN_ID


def _create_injection_block(message: str) -> TextContent:
    return TextContent(type="text", text=f"\n\nUser injection message: {message}")


def append_injection_to_result(
    result: Sequence[ContentBlock] | tuple[Sequence[ContentBlock], dict] | dict,
    message: str,
) -> Sequence[ContentBlock] | tuple[Sequence[ContentBlock], dict]:
    """Append an injection note to the given tool result."""
    injection_block = _create_injection_block(message)

    if isinstance(result, tuple) and len(result) == 2:
        unstructured, structured = result
        augmented = list(unstructured) + [injection_block]
        return augmented, structured

    if isinstance(result, dict):
        base_text = json.dumps(result, indent=2)
        return [TextContent(type="text", text=base_text), injection_block], result

    return list(result) + [injection_block]


class InjectionAwareToolManager(ToolManager):
    """Tool manager that appends queued injection messages to tool outputs."""

    def __init__(
        self,
        *,
        injection_store: InjectionStore,
        run_id_getter: Callable[[Context | None], str] = get_run_id_from_context,
        warn_on_duplicate_tools: bool = True,
    ) -> None:
        super().__init__(warn_on_duplicate_tools=warn_on_duplicate_tools)
        self._injection_store = injection_store
        self._run_id_getter = run_id_getter

    @classmethod
    def from_existing(
        cls,
        existing: ToolManager,
        *,
        injection_store: InjectionStore,
        run_id_getter: Callable[[Context | None], str] = get_run_id_from_context,
    ) -> "InjectionAwareToolManager":
        new_manager = cls(
            injection_store=injection_store,
            run_id_getter=run_id_getter,
            warn_on_duplicate_tools=existing.warn_on_duplicate_tools,
        )
        for tool in existing.list_tools():
            new_manager._tools[tool.name] = tool  # noqa: SLF001
        return new_manager

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, object],
        context: Context | None = None,
        convert_result: bool = False,
    ) -> Sequence[ContentBlock] | tuple[Sequence[ContentBlock], dict]:
        result = await super().call_tool(
            name,
            arguments,
            context=context,
            convert_result=convert_result,
        )

        run_id = self._run_id_getter(context)
        injection = await self._injection_store.pop_message(run_id)
        if not injection:
            return result

        logger.info("Injecting queued message into tool result for run_id=%s", run_id)
        return append_injection_to_result(result, injection)


def register_injection_route(mcp: FastMCP, store: InjectionStore) -> None:
    """Expose an HTTP endpoint for posting injection messages."""

    @mcp.custom_route("/runs/{run_id}/inject", methods=["POST"], name="inject_message")
    async def _inject_message(request: Request) -> Response:  # noqa: D401 - route handler
        run_id = request.path_params.get("run_id", INJECTION_DEFAULT_RUN_ID)
        try:
            payload = await request.json()
        except Exception:  # noqa: BLE001 - intentionally narrow in scope
            return JSONResponse({"error": "invalid JSON"}, status_code=400)

        message = payload.get("message") if isinstance(payload, dict) else None
        if not isinstance(message, str) or not message.strip():
            return JSONResponse({"error": "message must be a non-empty string"}, status_code=400)

        await store.set_message(run_id, message)
        return JSONResponse({"status": "queued", "run_id": run_id})


def apply_injection_support(mcp: FastMCP, store: InjectionStore) -> None:
    """Wire the injection manager and HTTP route into the FastMCP instance."""

    mcp._tool_manager = InjectionAwareToolManager.from_existing(  # noqa: SLF001
        mcp._tool_manager,  # noqa: SLF001
        injection_store=store,
    )
    register_injection_route(mcp, store)


injection_store = InjectionStore()
