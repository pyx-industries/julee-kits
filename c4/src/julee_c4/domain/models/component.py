"""Component domain model.

A grouping of related functionality within a container.
"""

from julee.core.entities.entity import Entity
from julee.core.utils import normalize_name, slugify
from pydantic import Field, computed_field, field_validator


class Component(Entity):
    """Component entity.

    A component is a grouping of related functionality encapsulated
    behind a well-defined interface. Components exist within containers
    and are NOT separately deployable units.
    """

    slug: str
    name: str
    container_slug: str
    system_slug: str
    description: str = ""
    technology: str = ""
    interface: str = ""
    code_path: str = ""
    tags: tuple[str, ...] = Field(default_factory=tuple)
    docname: str = ""

    @field_validator("slug", mode="before")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Validate and normalize slug."""
        if not v or not v.strip():
            raise ValueError("slug cannot be empty")
        return slugify(v.strip())

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty."""
        if not v or not v.strip():
            raise ValueError("name cannot be empty")
        return v.strip()

    @field_validator("container_slug", mode="before")
    @classmethod
    def validate_container_slug(cls, v: str) -> str:
        """Validate container_slug is not empty."""
        if not v or not v.strip():
            raise ValueError("container_slug cannot be empty")
        return v.strip()

    @field_validator("system_slug", mode="before")
    @classmethod
    def validate_system_slug(cls, v: str) -> str:
        """Validate system_slug is not empty."""
        if not v or not v.strip():
            raise ValueError("system_slug cannot be empty")
        return v.strip()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def name_normalized(self) -> str:
        """Normalized name for case-insensitive matching."""
        return normalize_name(self.name)

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
        return self.model_copy(update={"tags": (*self.tags, tag)})
