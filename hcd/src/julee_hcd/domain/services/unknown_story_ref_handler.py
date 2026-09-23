"""Handler protocol for epics referencing unknown stories."""

from typing import Protocol, runtime_checkable

from julee.core.entities.acknowledgement import Acknowledgement

from julee_hcd.domain.models.epic import Epic


@runtime_checkable
class UnknownStoryRefHandler(Protocol):
    """Handler for epics referencing unknown stories.

    Called when an epic's story_refs contains titles not found in StoryRepository.
    The handler decides what to do: warn, suggest corrections, etc.
    """

    async def handle(self, epic: Epic, unknown_refs: list[str]) -> Acknowledgement:
        """Handle an epic with unknown story references."""
        ...
