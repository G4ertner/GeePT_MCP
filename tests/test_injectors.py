from __future__ import annotations

import logging
import math as stdlib_math
import pytest

import mcp_server.executors.injectors as injector_module
from mcp_server.executors.injectors import build_globals, restore_after_exec


class DummySpaceCenter:
    def __init__(self, vessel):
        self._vessel = vessel
        self.raise_on_access = False

    @property
    def active_vessel(self):
        if self.raise_on_access:
            raise RuntimeError("vessel handle invalid")
        return self._vessel


class DummyConn:
    def __init__(self, vessel):
        self.space_center = DummySpaceCenter(vessel)


def _build_with_cleanup(conn):
    glb, cleanup = build_globals(conn, timeout_sec=None, allow_imports=True)
    return glb, cleanup


def test_check_time_aborts_when_active_vessel_disappears():
    conn = DummyConn(object())
    glb, cleanup = _build_with_cleanup(conn)
    check_time = glb["check_time"]
    try:
        check_time()
        conn.space_center._vessel = None
        check_time()
        check_time()
        with pytest.raises(RuntimeError, match="Active vessel disappeared"):
            check_time()
    finally:
        restore_after_exec(cleanup)


def test_check_time_ignores_missing_vessel_when_none_initially():
    conn = DummyConn(None)
    glb, cleanup = _build_with_cleanup(conn)
    check_time = glb["check_time"]
    try:
        for _ in range(5):
            check_time()
    finally:
        restore_after_exec(cleanup)


def test_check_time_handles_krpc_exceptions_as_loss():
    conn = DummyConn(object())
    glb, cleanup = _build_with_cleanup(conn)
    check_time = glb["check_time"]
    try:
        conn.space_center.raise_on_access = True
        check_time()
        check_time()
        with pytest.raises(RuntimeError, match="Active vessel disappeared"):
            check_time()
    finally:
        restore_after_exec(cleanup)


def test_import_stdlib_module_when_imports_restricted():
    conn = DummyConn(object())
    glb, cleanup = build_globals(conn, timeout_sec=None, allow_imports=False)
    try:
        exec("import math\nresult = math.sqrt(25)", glb, glb)
        assert stdlib_math.isclose(glb["result"], 5.0, rel_tol=1e-9)
    finally:
        restore_after_exec(cleanup)


def test_log_handles_unencodable_characters(monkeypatch):
    class DummyStream:
        def __init__(self):
            self.encoding = "cp1252"
            self.writes: list[str] = []
            self._raised = False

        def write(self, text: str) -> int:
            self.writes.append(text)
            if "→" in text and not self._raised:
                self._raised = True
                raise UnicodeEncodeError("cp1252", "→", 0, 1, "cannot encode")
            return len(text)

        def flush(self) -> None:
            pass

    dummy_stream = DummyStream()
    monkeypatch.setattr(injector_module._sys, "stdout", dummy_stream)
    conn = DummyConn(object())
    glb, cleanup = build_globals(conn, timeout_sec=None, allow_imports=True)
    try:
        glb["log"]("STAGE: arrow → next stage")
        assert dummy_stream._raised, "Expected UnicodeEncodeError to be raised once"
        assert any("→" not in entry for entry in dummy_stream.writes[-2:]), "Sanitized output should drop the arrow"
    finally:
        restore_after_exec(cleanup)
