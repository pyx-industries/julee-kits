"""Handler protocol for stories created without an epic assignment."""

from typing import Protocol, runtime_checkable

from julee.core.entities.acknowledgement import Acknowledgement

from julee_hcd.domain.models.story import Story


@runtime_checkable
class OrphanStoryHandler(Protocol):
    """Handler for stories created without an epic assignment.

    Called when a story is created/updated and has no epic_slug.
    The handler decides what to do: suggest epics, auto-assign, notify, etc.
    """

    async def handle(self, story: Story) -> Acknowledgement:
        """Handle an orphan story."""
        ...
