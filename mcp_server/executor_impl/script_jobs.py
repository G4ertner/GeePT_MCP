from __future__ import annotations

from typing import Any, Dict

from .jobs import JobRegistry, job_registry, JobHandle


class ScriptJobManager:
    def __init__(self, registry: JobRegistry | None = None) -> None:
        self.registry = registry or job_registry

    def create(self, func, metadata: Dict[str, Any] | None = None) -> str:
        return self.registry.create_job(func, metadata)


manager = ScriptJobManager()

