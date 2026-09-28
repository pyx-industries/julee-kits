"""Relationship domain model.

Connections between C4 elements representing interactions.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import cast

from julee.core.entities.text import Slug


class ElementType(StrEnum):
    """Types of elements that can participate in relationships."""

    PERSON = "person"  # References an hcd Persona by its slug
    SOFTWARE_SYSTEM = "software_system"
    CONTAINER = "container"
    COMPONENT = "component"


# FIXME: this is a kludge. A field that lies about its type until
# __post_init__ runs is a hidden turd: the annotation says Slug and the
# value is a bare str for as long as it takes to construct the entity,
# and every reader has to know that to trust the annotation. It stands
# because a pydantic default_factory could read the other fields and a
# dataclass one cannot, and the alternative — making slug a property —
# would take away a caller's right to name one, which several exercise.
# The real fix is to decide whether a derived slug is derived or given,
# and stop letting it be both.
DERIVE_IT = cast("Slug", "")
"""A slug default, meaning "work it out from what the entity carries".

An entity identified by something its author already knows has a
derivable slug rather than one a caller has to invent. A caller may
still name one, and several do.

``Slug`` refuses an empty string, so the default cannot be a real one.
It is a plain ``str`` until ``__post_init__`` replaces it, built there
by :class:`~julee.core.entities.text.Slug` exactly as a given one is,
and nothing observes it in between.
"""


@dataclass(frozen=True)
class Relationship:
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
    :class:`~julee.core.entities.text.Slug` settles which one is
    meant (#70).
    """

    source_type: ElementType
    source_slug: Slug
    destination_type: ElementType
    destination_slug: Slug
    description: str = "Uses"
    technology: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    bidirectional: bool = False
    docname: str = ""
    slug: Slug = DERIVE_IT
    """Derived from the two ends unless given."""

    def __post_init__(self) -> None:
        """Name the relationship after its ends if it was not named."""
        if not self.slug:
            object.__setattr__(
                self,
                "slug",
                Slug(f"{self.source_slug}-to-{self.destination_slug}"),
            )

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
