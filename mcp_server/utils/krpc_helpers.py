from __future__ import annotations

from .krpc_utils.client import connect_to_game


def open_connection(
    address: str,
    rpc_port: int = 50000,
    stream_port: int = 50001,
    name: str | None = None,
    timeout: float = 5.0,
):
    """Helper that mirrors the legacy _connect signature but lives in utils."""
    return connect_to_game(
        address,
        rpc_port=rpc_port,
        stream_port=stream_port,
        name=name,
        timeout=timeout,
    )


def best_effort_pause(conn):
    """Internal pause helper shared between executor and general tools."""
    try:
        cur = bool(conn.krpc.paused)
        if not cur:
            conn.krpc.paused = True
        return True
    except Exception:
        pass
    try:
        sc = conn.space_center
    except Exception:
        return None
    for attr in ("set_pause", "set_paused", "pause"):
        try:
            fn = getattr(sc, attr, None)
            if callable(fn):
                fn(True)
                return True
        except Exception:
            continue
    for attr in ("paused", "is_paused"):
        try:
            if hasattr(sc, attr):
                setattr(sc, attr, True)
                return True
        except Exception:
            continue
    return None
