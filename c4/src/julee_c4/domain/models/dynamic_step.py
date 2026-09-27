"""DynamicStep domain model.

A numbered step in a dynamic (sequence) diagram.
"""

from typing import Any

from julee.core.entities.entity import Entity
from julee.core.entities.text import Name, Slug
from pydantic import Field

from .relationship import ElementType


def _name_it_after_its_place(data: dict[str, Any]) -> Slug:
    """Name a step after where it sits in its sequence.

    A step is identified by its sequence and its number, which it
    already carries, so its slug is derivable rather than something a
    caller has to invent.

    This ran in ``model_post_init`` and wrote the slug with
    ``object.__setattr__``, which reaches past validation. As a default
    it is built the same way a given one is.
    """
    return DynamicStep.generate_slug(data["sequence_name"], data["step_number"])


class DynamicStep(Entity):
    """DynamicStep entity.

    Represents a numbered interaction in a dynamic diagram.
    Dynamic diagrams show runtime behavior for specific scenarios
    (user stories, use cases, features).
    """

    sequence_name: Name
    step_number: int = Field(ge=1, description="Steps are numbered from one")
    source_type: ElementType
    source_slug: Slug
    destination_type: ElementType
    destination_slug: Slug
    description: str = ""
    technology: str = ""
    return_value: str = ""
    is_async: bool = False
    docname: str = ""
    slug: Slug = Field(default_factory=_name_it_after_its_place)
    """Derived from the sequence and step number; declared last so it can be."""

    @property
    def step_label(self) -> str:
        """Get formatted step label (e.g., '1. ')."""
        return f"{self.step_number}. "

    @property
    def full_label(self) -> str:
        """Get full step label with description."""
        base = f"{self.step_number}. {self.description}"
        if self.technology:
            base = f"{base} [{self.technology}]"
        return base

    @property
    def is_person_interaction(self) -> bool:
        """Check if this step involves a person."""
        return (
            self.source_type == ElementType.PERSON
            or self.destination_type == ElementType.PERSON
        )

    @classmethod
    def generate_slug(cls, sequence_name: str, step_number: int) -> Slug:
        """The slug a step in this place would have.

        Public because a caller looking a step up by its position needs
        the same answer the entity would give itself.
        """
        return Slug(f"{sequence_name}-step-{step_number}")

    def involves_element(self, element_type: ElementType, element_slug: str) -> bool:
        """Check if step involves a specific element.

        The argument is made a :class:`Slug` before comparison, so
        asking with an element's display name answers the same as
        asking with its slug.
        """
        wanted = Slug(element_slug)
        return (self.source_type == element_type and self.source_slug == wanted) or (
            self.destination_type == element_type and self.destination_slug == wanted
        )
