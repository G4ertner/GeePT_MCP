from __future__ import annotations


def modulize_rel_path(rel_path: str) -> str:
    """Convert a repo-relative Python path to a dotted module path."""
    p = rel_path.replace("\\", "/")
    if p.endswith("/__init__.py"):
        p = p[: -len("/__init__.py")]
    elif p.endswith(".py"):
        p = p[: -len(".py")]
    return p.replace("/", ".")
