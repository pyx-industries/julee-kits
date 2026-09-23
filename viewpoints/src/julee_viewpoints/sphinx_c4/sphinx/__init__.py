"""Sphinx application layer for sphinx_c4.

Contains Sphinx-specific code:
- context.py: C4Context, one SyncRepositoryAdapter per C4 element
- directives/: Sphinx directive implementations
"""

from .context import C4Context, ensure_c4_context, get_c4_context, set_c4_context

__all__ = [
    "C4Context",
    "ensure_c4_context",
    "get_c4_context",
    "set_c4_context",
]
