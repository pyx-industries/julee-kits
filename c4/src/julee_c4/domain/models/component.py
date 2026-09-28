"""Component domain model.

A grouping of related functionality within a container.
"""

from dataclasses import dataclass, field, replace

from julee.core.entities.text import Name, Slug


@dataclass(frozen=True)
class Component:
    """Component entity.

    A component is a grouping of related functionality encapsulated
    behind a well-defined interface. Components exist within containers
    and are NOT separately deployable units.
    """

    slug: Slug
    name: Name
    container_slug: Slug
    system_slug: Slug
    description: str = ""
    technology: str = ""
    interface: str = ""
    code_path: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    docname: str = ""

    @property
    def name_normalized(self) -> str:
        """Normalized name for case-insensitive matching."""
        return self.name.normalized

    @property
    def qualified_slug(self) -> str:
        """Fully qualified slug including container and system."""
        return f"{self.system_slug}/{self.container_slug}/{self.slug}"

    @property
    def has_code(self) -> bool:
        """Check if component has linked code."""
        return bool(self.code_path)

    @property
    def has_interface(self) -> bool:
        """Check if component has interface description."""
        return bool(self.interface)

    def has_tag(self, tag: str) -> bool:
        """Check if component has a specific tag (case-insensitive)."""
        return tag.lower() in [t.lower() for t in self.tags]

    def with_tag(self, tag: str) -> "Component":
        """The entity with a tag added.

        An entity is immutable, so this returns a new one rather than
        changing this one. A tag already present is not added twice.

        Args:
            tag: Tag to add

        Returns:
            A new Component, or this one if it already had the tag
        """
        if self.has_tag(tag):
            return self
        return replace(self, tags=(*self.tags, tag))
