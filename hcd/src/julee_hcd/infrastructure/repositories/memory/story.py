"""Memory implementation of StoryRepository."""

import logging

from julee.core.utils import normalize_name

from julee_hcd.domain.models.story import Story
from julee_hcd.domain.repositories.story import StoryRepository

from .base import MemoryHcdRepository

logger = logging.getLogger(__name__)


class MemoryStoryRepository(MemoryHcdRepository[Story], StoryRepository):
    """In-memory implementation of StoryRepository.

    Stories are stored in a dictionary keyed by slug. This implementation
    is used during Sphinx builds where stories are populated at builder-inited
    and queried during doctree processing.
    """

    def __init__(self) -> None:
        """Start empty."""
        super().__init__("Story")

    async def get_by_app(self, app_slug: str) -> list[Story]:
        """Get all stories for an application."""
        app_normalized = normalize_name(app_slug)
        return [
            story
            for story in self.storage_dict.values()
            if story.app_normalized == app_normalized
        ]

    async def get_by_persona(self, persona: str) -> list[Story]:
        """Get all stories for a persona."""
        persona_normalized = normalize_name(persona)
        return [
            story
            for story in self.storage_dict.values()
            if story.persona_normalized == persona_normalized
        ]

    async def get_by_feature_title(self, feature_title: str) -> Story | None:
        """Get a story by its feature title."""
        title_normalized = normalize_name(feature_title)
        for story in self.storage_dict.values():
            if normalize_name(story.feature_title) == title_normalized:
                return story
        return None

    async def get_apps_with_stories(self) -> set[str]:
        """Get the set of app slugs that have stories."""
        return {story.app_slug for story in self.storage_dict.values()}

    async def get_all_personas(self) -> set[str]:
        """Get all unique personas across all stories."""
        return {
            story.persona_normalized
            for story in self.storage_dict.values()
            if story.persona_normalized != "unknown"
        }
