"""Relationship domain model.

Connections between C4 elements representing interactions.
"""

from enum import StrEnum
from typing import Any

from julee.core.entities.entity import Entity
from pydantic import Field

from julee_c4.domain.models.text import Slug


class ElementType(StrEnum):
    """Types of elements that can participate in relationships."""

    PERSON = "person"  # References an hcd Persona by its slug
    SOFTWARE_SYSTEM = "software_system"
    CONTAINER = "container"
    COMPONENT = "component"


def _name_it_after_its_ends(data: dict[str, Any]) -> Slug:
    """Name a relationship after what it joins.

    A relationship is identified by its two ends, which it already
    carries, so its slug is derivable rather than something a caller
    has to invent.

    This ran in ``model_post_init`` and wrote the slug with
    ``object.__setattr__``, which reaches past validation: the derived
    slug was the one value of the field that nothing checked. As a
    default it is built the same way a given one is, by
    :class:`~julee_c4.domain.models.text.Slug`.
    """
    return Slug(f"{data['source_slug']}-to-{data['destination_slug']}")


class Relationship(Entity):
    """Relationship entity.

    Represents a connection between two C4 elements. Relationships have
    a source, destination, and description of the interaction.

    When source_type or destination_type is PERSON, the corresponding
    slug is an hcd ``Persona.slug``, which hcd derives with the same
    :func:`~julee.core.utils.slugify`.

    This used to say ``normalized_name``, which is the other thing a
    Persona carries: a lowercased name with spaces in it, for comparing
    names by. A reference holding spaces is not a slug, and would never
    have matched the field it is used as a key into. Declaring both ends
    :class:`~julee_c4.domain.models.text.Slug` settles which one is
    meant (#70).
    """

    source_type: ElementType
    source_slug: Slug
    destination_type: ElementType
    destination_slug: Slug
    description: str = "Uses"
    technology: str = ""
    tags: tuple[str, ...] = Field(default_factory=tuple)
    bidirectional: bool = False
    docname: str = ""
    slug: Slug = Field(default_factory=_name_it_after_its_ends)
    """Derived from the two ends when not given; declared last so it can be."""

    @property
    def is_person_relationship(self) -> bool:
        """Check if this relationship involves a person."""
        return (
            self.source_type == ElementType.PERSON
            or self.destination_type == ElementType.PERSON
        )

    @property
    def is_cross_system(self) -> bool:
        """Check if relationship crosses system boundaries."""
        return (
            self.source_type == ElementType.SOFTWARE_SYSTEM
            or self.destination_type == ElementType.SOFTWARE_SYSTEM
        )

    @property
    def is_internal(self) -> bool:
        """Check if relationship is between containers/components only."""
        internal_types = {ElementType.CONTAINER, ElementType.COMPONENT}
        return (
            self.source_type in internal_types
            and self.destination_type in internal_types
        )

    @property
    def label(self) -> str:
        """Get formatted label for diagram rendering."""
        if self.technology:
            return f"{self.description}\\n[{self.technology}]"
        return self.description

    def involves_element(self, element_type: ElementType, element_slug: str) -> bool:
        """Check if relationship involves a specific element.

        The argument is made a :class:`Slug` before comparison, so
        asking with an element's display name answers the same as
        asking with its slug.
        """
        wanted = Slug(element_slug)
        return (self.source_type == element_type and self.source_slug == wanted) or (
            self.destination_type == element_type and self.destination_slug == wanted
        )

    def involves_system(self, system_slug: str) -> bool:
        """Check if relationship involves a specific system."""
        return self.involves_element(ElementType.SOFTWARE_SYSTEM, system_slug)

    def involves_container(self, container_slug: str) -> bool:
        """Check if relationship involves a specific container."""
        return self.involves_element(ElementType.CONTAINER, container_slug)

    def involves_component(self, component_slug: str) -> bool:
        """Check if relationship involves a specific component."""
        return self.involves_element(ElementType.COMPONENT, component_slug)

    def involves_person(self, persona_name: str) -> bool:
        """Check if relationship involves a specific persona."""
        return self.involves_element(ElementType.PERSON, persona_name)

    def has_tag(self, tag: str) -> bool:
        """Check if relationship has a specific tag (case-insensitive)."""
        return tag.lower() in [t.lower() for t in self.tags]
