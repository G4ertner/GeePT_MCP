from __future__ import annotations

from datetime import datetime, timezone


def utc_timestamp() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(tz=timezone.utc).isoformat()
