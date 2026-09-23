"""Shared Sphinx directives.

Domain-agnostic directives that can be used by more than one of this kit's
Sphinx extensions.
"""

from .entity_graph import EntityGraphDirective

__all__ = [
    "EntityGraphDirective",
]
