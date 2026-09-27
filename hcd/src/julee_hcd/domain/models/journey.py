"""Journey domain model.

Represents a user journey in the HCD documentation system.
Journeys are defined via RST directives and track a persona's path
through the system to achieve a goal.
"""

from enum import StrEnum

from julee.core.entities.entity import Entity
from julee.core.entities.text import NonEmptyText, Slug
from julee.core.utils import normalize_name
from pydantic import Field, computed_field

from .base import Authored


class StepType(StrEnum):
    """Type of journey step."""

    STORY = "story"
    EPIC = "epic"
    PHASE = "phase"

    @classmethod
    def from_string(cls, value: str) -> "StepType":
        """Convert string to StepType."""
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Invalid step type: {value}")


class JourneyStep(Entity):
    """A step within a journey.

    Steps can be stories (feature references), epics (epic references),
    or phases (grouping labels for subsequent steps).
    """

    step_type: StepType = Field(description="The type of step (story, epic, phase)")
    ref: NonEmptyText = Field(
        description="Reference identifier (story title, epic slug, or phase title)"
    )
    description: str = Field(
        default="", description="Optional description (primarily for phases)"
    )

    @classmethod
    def story(cls, title: str) -> "JourneyStep":
        """Create a story step.

        Args:
            title: Story feature title

        Returns:
            JourneyStep with type STORY
        """
        return cls(step_type=StepType.STORY, ref=NonEmptyText(title))

    @classmethod
    def epic(cls, slug: str) -> "JourneyStep":
        """Create an epic step.

        Args:
            slug: Epic slug

        Returns:
            JourneyStep with type EPIC
        """
        return cls(step_type=StepType.EPIC, ref=NonEmptyText(slug))

    @classmethod
    def phase(cls, title: str, description: str = "") -> "JourneyStep":
        """Create a phase step.

        Args:
            title: Phase title
            description: Optional phase description

        Returns:
            JourneyStep with type PHASE
        """
        return cls(
            step_type=StepType.PHASE, ref=NonEmptyText(title), description=description
        )

    @property
    def is_story(self) -> bool:
        """Check if this is a story step."""
        return self.step_type == StepType.STORY

    @property
    def is_epic(self) -> bool:
        """Check if this is an epic step."""
        return self.step_type == StepType.EPIC

    @property
    def is_phase(self) -> bool:
        """Check if this is a phase step."""
        return self.step_type == StepType.PHASE


class Journey(Authored):
    """User journey entity.

    A journey represents a persona's path through the system to achieve
    a goal. It captures the user's motivation, the value delivered, and
    the sequence of steps they follow.
    """

    slug: Slug = Field(description='URL-safe identifier (e.g., "build-vocabulary")')
    persona: str = Field(default="", description="The persona undertaking this journey")
    intent: str = Field(
        default="", description="What the persona wants (their motivation)"
    )
    outcome: str = Field(
        default="", description="What success looks like (business value)"
    )
    goal: str = Field(default="", description="Activity description (what they do)")
    depends_on: tuple[Slug, ...] = Field(
        default_factory=tuple, description="Journey slugs that must be completed first"
    )
    steps: tuple[JourneyStep, ...] = Field(
        default_factory=tuple, description="Sequence of journey steps"
    )
    preconditions: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Conditions that must be true before starting",
    )
    postconditions: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Conditions that will be true after completion",
    )

    @computed_field  # type: ignore[prop-decorator]
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
        return self.model_copy(update={"steps": (*self.steps, step)})

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
