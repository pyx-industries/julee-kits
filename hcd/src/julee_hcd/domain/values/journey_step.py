"""One step of a journey, and what kind of step it is.

StepType came with it: it says what a step refers to, so it belongs
with the step rather than with the Journey that holds a sequence of
them. Leaving it behind made journey.py and this module import each
other.

A value, not an entity (ADR 018). A step names a story and says where
it comes in the journey; it has no id of its own and no repository
keeps one. It lived in journey.py beside the Journey that holds it, and
was read as a second aggregate there.
"""

from dataclasses import dataclass
from enum import StrEnum

from julee.core.values.text import NonEmptyText


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


@dataclass(frozen=True, kw_only=True)
class JourneyStep:
    """A step within a journey.

    Steps can be stories (feature references), epics (epic references),
    or phases (grouping labels for subsequent steps).
    """

    step_type: StepType
    """The type of step (story, epic, phase)."""

    ref: NonEmptyText
    """Reference identifier (story title, epic slug, or phase title)."""

    description: str = ""
    """Optional description (primarily for phases)."""

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
