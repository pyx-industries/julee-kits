"""Journey domain model.

Represents a user journey in the HCD documentation system.
Journeys are defined via RST directives and track a persona's path
through the system to achieve a goal.
"""

from dataclasses import dataclass, replace

from julee.core.entities.text import Slug
from julee.core.utils import normalize_name

from ..values.journey_step import JourneyStep
from .base import Authored


@dataclass(frozen=True, kw_only=True)
class Journey(Authored):
    """User journey entity.

    A journey represents a persona's path through the system to achieve
    a goal. It captures the user's motivation, the value delivered, and
    the sequence of steps they follow.
    """

    slug: Slug
    """URL-safe identifier (e.g., "build-vocabulary")."""

    persona: str = ""
    """The persona undertaking this journey."""

    intent: str = ""
    """What the persona wants (their motivation)."""

    outcome: str = ""
    """What success looks like (business value)."""

    goal: str = ""
    """Activity description (what they do)."""

    depends_on: tuple[Slug, ...] = ()
    """Journey slugs that must be completed first."""

    steps: tuple[JourneyStep, ...] = ()
    """Sequence of journey steps."""

    preconditions: tuple[str, ...] = ()
    """Conditions that must be true before starting."""

    postconditions: tuple[str, ...] = ()
    """Conditions that will be true after completion."""

    @property
    def persona_normalized(self) -> str:
        """Lowercase persona for matching.

        A stored field until #71, filled by a validator that returned
        any value it was given and recomputed in ``model_post_init`` in
        case the validator had not run — so a caller could write one
        that disagreed with ``persona``, which is what matching reads.

        ``persona`` stays a plain str because a journey may legitimately
        have none, and Name refuses empty. What is derived from it is
        derived either way.
        """
        return normalize_name(self.persona)

    def matches_persona(self, persona_name: str) -> bool:
        """Check if this journey matches the given persona (case-insensitive).

        Args:
            persona_name: Persona name to match against

        Returns:
            True if normalized names match
        """
        return self.persona_normalized == normalize_name(persona_name)

    def has_dependency(self, journey_slug: str) -> bool:
        """Check if this journey depends on another journey.

        Args:
            journey_slug: Slug of potential dependency

        Returns:
            True if this journey depends on the given journey
        """
        return journey_slug in self.depends_on

    def with_step(self, step: JourneyStep) -> "Journey":
        """The journey with a step appended.

        An entity is immutable, so this returns a new journey rather than
        changing this one.

        Args:
            step: JourneyStep to add
        """
        return replace(self, steps=(*self.steps, step))

    def get_story_refs(self) -> list[str]:
        """Get all story references from steps.

        Returns:
            List of story titles referenced in steps
        """
        return [step.ref for step in self.steps if step.is_story]

    def get_epic_refs(self) -> list[str]:
        """Get all epic references from steps.

        Returns:
            List of epic slugs referenced in steps
        """
        return [step.ref for step in self.steps if step.is_epic]

    @property
    def display_title(self) -> str:
        """Get formatted title for display."""
        return self.slug.replace("-", " ").title()

    @property
    def has_steps(self) -> bool:
        """Check if journey has any steps."""
        return len(self.steps) > 0

    @property
    def step_count(self) -> int:
        """Get number of steps."""
        return len(self.steps)
