"""EpicRepository protocol.

Defines the interface for epic data access.
"""

from typing import Protocol, runtime_checkable

from julee_hcd.domain.models.epic import Epic

from .base import HcdRepository


@runtime_checkable
class EpicRepository(HcdRepository[Epic], Protocol):
    """Repository protocol for Epic entities.

    Extends HcdRepository with epic-specific query methods.
    Epics are defined in RST documents and support incremental builds
    via docname tracking.
    """

    async def get_with_story_ref(self, story_title: str) -> list[Epic]:
        """Get epics that contain a specific story.

        Args:
            story_title: Story feature title (case-insensitive)

        Returns:
            List of epics containing this story in story_refs
        """
        ...

    async def get_all_story_refs(self) -> set[str]:
        """Get all unique story references across all epics.

        Returns:
            Set of story titles (normalized)
        """
        ...
