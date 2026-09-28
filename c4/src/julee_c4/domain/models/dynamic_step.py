"""DynamicStep domain model.

A numbered step in a dynamic (sequence) diagram.
"""

from dataclasses import dataclass

from julee.core.entities.text import Name, Slug

from .relationship import DERIVE_IT, ElementType


@dataclass(frozen=True)
class DynamicStep:
    """DynamicStep entity.

    Represents a numbered interaction in a dynamic diagram.
    Dynamic diagrams show runtime behavior for specific scenarios
    (user stories, use cases, features).
    """

    sequence_name: Name
    step_number: int
    source_type: ElementType
    source_slug: Slug
    destination_type: ElementType
    destination_slug: Slug
    description: str = ""
    technology: str = ""
    return_value: str = ""
    is_async: bool = False
    docname: str = ""
    slug: Slug = DERIVE_IT
    """Derived from the sequence and step number unless given."""

    def __post_init__(self) -> None:
        """Check the step number and name the step if it was not named.

        Raises:
            ValueError: If step_number is less than one
        """
        if self.step_number < 1:
            raise ValueError(
                f"step_number must be greater than or equal to 1, "
                f"got {self.step_number}"
            )
        if not self.slug:
            object.__setattr__(
                self,
                "slug",
                self.generate_slug(self.sequence_name, self.step_number),
            )

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
