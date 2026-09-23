"""Handler protocol for epics created without any stories."""

from typing import Protocol, runtime_checkable

from julee.core.entities.acknowledgement import Acknowledgement

from julee_hcd.domain.models.epic import Epic


@runtime_checkable
class EmptyEpicHandler(Protocol):
    """Handler for epics created without any stories.

    Called when an epic is created/updated and has no story_refs.
    The handler decides what to do: warn, suggest stories, etc.
    """

    async def handle(self, epic: Epic) -> Acknowledgement:
        """Handle an empty epic."""
        ...
