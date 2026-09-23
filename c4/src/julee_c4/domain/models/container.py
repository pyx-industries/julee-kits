"""Container domain model.

A runtime boundary - application or data store within a software system.
"""

from enum import StrEnum

from julee.core.entities.entity import Entity
from julee.core.utils import normalize_name, slugify
from pydantic import Field, computed_field, field_validator


class ContainerType(StrEnum):
    """Classification of containers."""

    WEB_APPLICATION = "web_application"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"
    CONSOLE_APP = "console_app"
    SERVERLESS_FUNCTION = "serverless_function"
    DATABASE = "database"
    FILE_STORAGE = "file_storage"
    MESSAGE_QUEUE = "message_queue"
    API = "api"
    OTHER = "other"


class Container(Entity):
    """Container entity.

    A container is an application or data store - a runtime boundary.
    Something that needs to be running for the overall system to work.

    Note: This has nothing to do with Docker. The term "container" in C4
    predates containerization technology.
    """

    slug: str
    name: str
    system_slug: str
    description: str = ""
    container_type: ContainerType = ContainerType.OTHER
    technology: str = ""
    url: str = ""
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
        """Fully qualified slug including system."""
        return f"{self.system_slug}/{self.slug}"

    @property
    def is_data_store(self) -> bool:
        """Check if this container stores data."""
        return self.container_type in [
            ContainerType.DATABASE,
            ContainerType.FILE_STORAGE,
        ]

    @property
    def is_application(self) -> bool:
        """Check if this container is an application."""
        return self.container_type in [
            ContainerType.WEB_APPLICATION,
            ContainerType.MOBILE_APP,
            ContainerType.DESKTOP_APP,
            ContainerType.CONSOLE_APP,
            ContainerType.SERVERLESS_FUNCTION,
            ContainerType.API,
        ]

    def has_tag(self, tag: str) -> bool:
        """Check if container has a specific tag (case-insensitive)."""
        return tag.lower() in [t.lower() for t in self.tags]

    def with_tag(self, tag: str) -> "Container":
        """The entity with a tag added.

        An entity is immutable, so this returns a new one rather than
        changing this one. A tag already present is not added twice.

        Args:
            tag: Tag to add

        Returns:
            A new Container, or this one if it already had the tag
        """
        if self.has_tag(tag):
            return self
        return self.model_copy(update={"tags": (*self.tags, tag)})
