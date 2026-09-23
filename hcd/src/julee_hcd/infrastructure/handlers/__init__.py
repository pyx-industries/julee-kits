"""Handlers: what else should happen when an entity changes.

A repository stores an entity. Anything that must follow from storing it
— rewriting an index, telling another document it has a new member —
belongs to a handler, so the repository does not grow opinions about the
rest of the documentation.
"""

from .base import EntityHandler

__all__ = ["EntityHandler"]
