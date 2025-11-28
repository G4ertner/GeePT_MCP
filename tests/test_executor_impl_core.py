from __future__ import annotations

import logging

import pytest

from mcp_server.executor_impl import core


def test_resolve_timeouts_extends_none_soft(caplog):
    caplog.set_level(logging.WARNING)
    soft, hard = core._resolve_timeouts(None, 15.0)
    assert soft == 15.0
    assert hard == 15.0
    assert len(caplog.records) == 1
    assert "extending soft deadline to 15.0s" in caplog.records[0].getMessage()


def test_resolve_timeouts_bumps_short_soft(caplog):
    caplog.set_level(logging.WARNING)
    soft, hard = core._resolve_timeouts(6.0, 12.5)
    assert soft == 12.5
    assert hard == 12.5
    assert len(caplog.records) == 1
    assert "extending soft deadline to 12.5s" in caplog.records[0].getMessage()


def test_resolve_timeouts_keeps_long_soft(caplog):
    caplog.set_level(logging.WARNING)
    soft, hard = core._resolve_timeouts(20.0, 10.0)
    assert soft == 20.0
    assert hard == 10.0
    assert not caplog.records
