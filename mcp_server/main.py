from __future__ import annotations

import sys
from pathlib import Path


def _ensure_repo_root_on_path() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)


if __package__ in (None, ""):
    _ensure_repo_root_on_path()
    from mcp_server.mcp_context import mcp
    from mcp_server import libraries  # noqa: F401 - register documentation/snippet tools
    from mcp_server import playbooks  # noqa: F401 - register playbook resources
    from mcp_server import prompts    # noqa: F401 - register master prompt
    from mcp_server import general_tools  # noqa: F401 - register general supporting tools
    from mcp_server import executor_tools  # noqa: F401 - register execute_script tool
else:
    from .mcp_context import mcp
    from . import libraries  # noqa: F401 - register documentation/snippet tools
    from . import playbooks  # noqa: F401 - register playbook resources
    from . import prompts    # noqa: F401 - register master prompt
    from . import general_tools  # noqa: F401 - register general supporting tools
    from . import executor_tools  # noqa: F401 - register execute_script tool


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
