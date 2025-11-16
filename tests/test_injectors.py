from __future__ import annotations

import pytest

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
