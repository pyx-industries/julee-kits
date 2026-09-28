"""Epic domain model.

Represents an epic in the HCD documentation system.
Epics are defined via RST directives and group related stories together.
"""

from dataclasses import dataclass, replace

from julee.core.entities.text import Slug
from julee.core.utils import normalize_name

from .base import Authored


@dataclass(frozen=True, kw_only=True)
class Epic(Authored):
    """Epic entity.

    An epic represents a collection of related stories that together
    deliver a larger piece of functionality or business value.
    """

    slug: Slug
    """URL-safe identifier (e.g., "credential-creation")."""

    description: str = ""
    """Human-readable description of the epic."""

    story_refs: tuple[str, ...] = ()
    """List of story feature titles in this epic."""

    def with_story(self, story_title: str) -> "Epic":
        """The epic with a story reference added.

        An entity is immutable, so this returns a new epic rather than
        changing this one. A title already present is not added twice.

        Args:
            story_title: Feature title of the story to add
        """
        if story_title in self.story_refs:
            return self
        return replace(self, story_refs=(*self.story_refs, story_title))

    def has_story(self, story_title: str) -> bool:
        """Check if this epic contains a specific story.

        Args:
            story_title: Feature title to check (case-insensitive)

        Returns:
            True if the story is in this epic
        """
        story_normalized = normalize_name(story_title)
        return any(normalize_name(ref) == story_normalized for ref in self.story_refs)

    def get_story_refs_normalized(self) -> list[str]:
        """Get normalized story references.

        Returns:
            List of normalized story titles
        """
        return [normalize_name(ref) for ref in self.story_refs]

    @property
    def display_title(self) -> str:
        """Get formatted title for display."""
        return self.slug.replace("-", " ").title()

    @property
    def story_count(self) -> int:
        """Get number of stories in this epic."""
        return len(self.story_refs)

    @property
    def has_stories(self) -> bool:
        """Check if epic has any stories."""
        return len(self.story_refs) > 0
