from __future__ import annotations

import json

import pytest
from mcp.types import ContentBlock, TextContent
from mcp.server.fastmcp.tools.tool_manager import ToolManager

from mcp_server.injection import (
    INJECTION_DEFAULT_RUN_ID,
    InjectionAwareToolManager,
    InjectionStore,
    append_injection_to_result,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def test_injection_store_consumes_messages() -> None:
    store = InjectionStore()
    await store.set_message("alpha", "hello")
    await store.set_message("alpha", "world")

    first = await store.pop_message("alpha")
    second = await store.pop_message("alpha")
    third = await store.pop_message("alpha")

    assert first == "hello"
    assert second == "world"
    assert third is None


def test_append_injection_handles_dict_and_tuple() -> None:
    base_structured = {"ok": True}
    updated = append_injection_to_result(base_structured, "note")
    unstructured, structured = updated

    assert isinstance(unstructured[-1], TextContent)
    assert structured == base_structured

    tuple_updated = append_injection_to_result(([TextContent(type="text", text="hi")], {}), "next")
    tuple_unstructured, tuple_structured = tuple_updated

    assert tuple_structured == {}
    assert tuple_unstructured[-1].text.endswith("next")


async def test_tool_manager_appends_injection_once() -> None:
    store = InjectionStore()
    await store.set_message(INJECTION_DEFAULT_RUN_ID, "queued")

    manager = InjectionAwareToolManager(injection_store=store)

    def demo_tool() -> str:
        return json.dumps({"result": "base"})

    manager.add_tool(demo_tool)

    first_result = await manager.call_tool("demo_tool", {}, context=None, convert_result=True)
    first_blocks: list[ContentBlock]
    if isinstance(first_result, tuple):
        first_blocks = list(first_result[0])
    else:
        first_blocks = list(first_result)

    assert any(isinstance(block, TextContent) and "queued" in block.text for block in first_blocks)

    second_result = await manager.call_tool("demo_tool", {}, context=None, convert_result=True)
    second_blocks = list(second_result[0] if isinstance(second_result, tuple) else second_result)
    assert all("queued" not in getattr(block, "text", "") for block in second_blocks)


async def test_call_tool_uses_default_timeout_for_sync(monkeypatch) -> None:
    captured: dict[str, float | None] = {}

    async def fake_run_blocking(fn, *args, timeout_sec=None, **kwargs):
        captured["timeout"] = timeout_sec
        return fn(*args, **kwargs)

    monkeypatch.setattr("mcp_server.injection.run_blocking", fake_run_blocking)

    tm = ToolManager()

    def demo_sync() -> str:
        return "ok"

    tm.add_tool(demo_sync, name="krpc_get_status")
    manager = InjectionAwareToolManager.from_existing(tm, injection_store=InjectionStore())

    await manager.call_tool("krpc_get_status", {}, context=None, convert_result=True)

    assert captured["timeout"] == 60.0


async def test_call_tool_exempts_start_jobs(monkeypatch) -> None:
    captured: dict[str, float | None] = {}

    async def fake_run_blocking(fn, *args, timeout_sec=None, **kwargs):
        captured["timeout"] = timeout_sec
        return fn(*args, **kwargs)

    monkeypatch.setattr("mcp_server.injection.run_blocking", fake_run_blocking)

    tm = ToolManager()

    def job_starter() -> str:
        return "ok"

    tm.add_tool(job_starter, name="start_part_tree_job")
    manager = InjectionAwareToolManager.from_existing(tm, injection_store=InjectionStore())

    await manager.call_tool("start_part_tree_job", {}, context=None, convert_result=True)

    assert captured["timeout"] is None
