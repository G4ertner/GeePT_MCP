from __future__ import annotations

import io
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp_server.executors.injectors import build_globals


class _DummySpaceCenter:
    active_vessel = None


class _DummyConn:
    space_center = _DummySpaceCenter()


class _EncodingGuardStream:
    """Stream that raises on non-encodable characters to mimic cp1252 stdout."""

    encoding = "cp1252"

    def __init__(self):
        self._chunks: list[str] = []

    def write(self, s: str) -> int:
        # Simulate the console encoding step; raise on unencodable chars.
        s.encode(self.encoding)
        self._chunks.append(s)
        return len(s)

    def flush(self) -> None:
        return

    def getvalue(self) -> str:
        return "".join(self._chunks)


def test_log_tolerates_non_ascii_without_crashing():
    guard = _EncodingGuardStream()
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level
    original_stdout = sys.stdout
    try:
        sys.stdout = guard
        root.handlers = []
        g, _ = build_globals(_DummyConn(), timeout_sec=0, allow_imports=True)
        g["log"]("arrow \u2192 symbol")
    finally:
        sys.stdout = original_stdout
        root.handlers = original_handlers
        root.setLevel(original_level)

    output = guard.getvalue()
    assert "LOG" in output
    assert "arrow" in output
    # Non-encodable characters should be replaced, not crash the logger.
    assert "?" in output or "\u2192" in output
