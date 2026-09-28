"""SoftwareSystem domain model.

The highest level of abstraction in C4 - something that delivers value to users.
"""

from dataclasses import dataclass, field, replace
from enum import StrEnum

from julee.core.entities.text import Name, Slug


class SystemType(StrEnum):
    """Classification of software systems."""

    INTERNAL = "internal"  # Owned/developed by the organization
    EXTERNAL = "external"  # Third-party systems
    EXISTING = "existing"  # Legacy systems being integrated


@dataclass(frozen=True)
class SoftwareSystem:
    """Software System entity.

    The highest level of abstraction in C4. Represents something that
    delivers value to its users, whether human or not.
    """

    slug: Slug
    name: Name
    description: str = ""
    system_type: SystemType = SystemType.INTERNAL
    owner: str = ""
    technology: str = ""
    url: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    docname: str = ""

    @property
    def name_normalized(self) -> str:
        """Normalized name for case-insensitive matching."""
        return self.name.normalized

    @property
    def display_title(self) -> str:
        """Formatted title for display."""
        return self.name

    @property
    def is_external(self) -> bool:
        """Check if this is an external system."""
        return self.system_type == SystemType.EXTERNAL

    @property
    def is_internal(self) -> bool:
        """Check if this is an internal system."""
        return self.system_type == SystemType.INTERNAL

    def has_tag(self, tag: str) -> bool:
        """Check if system has a specific tag (case-insensitive)."""
        return tag.lower() in [t.lower() for t in self.tags]

    def with_tag(self, tag: str) -> "SoftwareSystem":
        """The entity with a tag added.

        An entity is immutable, so this returns a new one rather than
        changing this one. A tag already present is not added twice.

        Args:
            tag: Tag to add

        Returns:
            A new SoftwareSystem, or this one if it already had the tag
        """
        if self.has_tag(tag):
            return self
        return replace(self, tags=(*self.tags, tag))
