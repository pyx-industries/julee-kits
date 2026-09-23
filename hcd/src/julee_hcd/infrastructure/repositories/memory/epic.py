"""Memory implementation of EpicRepository."""

import logging

from julee.core.utils import normalize_name

from julee_hcd.domain.models.epic import Epic
from julee_hcd.domain.repositories.epic import EpicRepository

from .base import MemoryHcdRepository

logger = logging.getLogger(__name__)


class MemoryEpicRepository(MemoryHcdRepository[Epic], EpicRepository):
    """In-memory implementation of EpicRepository.

    Epics are stored in a dictionary keyed by slug. This implementation
    is used during Sphinx builds where epics are populated during doctree
    processing and support incremental builds via docname tracking.
    """

    def __init__(self) -> None:
        """Start empty."""
        super().__init__("Epic")

    async def get_with_story_ref(self, story_title: str) -> list[Epic]:
        """Get epics that contain a specific story."""
        story_normalized = normalize_name(story_title)
        return [
            epic
            for epic in self.storage_dict.values()
            if any(normalize_name(ref) == story_normalized for ref in epic.story_refs)
        ]

    async def get_all_story_refs(self) -> set[str]:
        """Get all unique story references across all epics."""
        refs: set[str] = set()
        for epic in self.storage_dict.values():
            refs.update(normalize_name(ref) for ref in epic.story_refs)
        return refs
