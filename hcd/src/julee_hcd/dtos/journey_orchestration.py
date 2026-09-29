"""The messages journey orchestration takes and returns.

A request is what a driving adapter hands in and a response is
what it serialises back out, so both are pydantic models. This
is the one package of the bounded context that imports pydantic
(ADR 001).
"""

from typing import Any

from pydantic import BaseModel, Field

from julee_hcd.domain.models.journey import Journey


class JourneyOrchestrationRequest(BaseModel):
    """Request for journey orchestration check."""

    journey: Journey = Field(
        description="The journey to check for orchestration conditions"
    )


class JourneyCondition(BaseModel):
    """A detected domain condition for a journey."""

    condition: str = Field(description="Condition type identifier")
    journey_slug: str = Field(description="The journey's slug")
    details: dict[str, Any] = Field(
        default_factory=dict, description="Condition-specific details"
    )


class JourneyOrchestrationResponse(BaseModel):
    """Response from journey orchestration check."""

    journey: Journey = Field(description="The checked journey")
    conditions: list[JourneyCondition] = Field(
        default_factory=list, description="Detected conditions"
    )

    @property
    def has_unknown_persona(self) -> bool:
        """Check if unknown persona condition was detected."""
        return any(c.condition == "unknown_persona" for c in self.conditions)

    @property
    def has_unknown_story_refs(self) -> bool:
        """Check if unknown story refs condition was detected."""
        return any(c.condition == "unknown_story_refs" for c in self.conditions)

    @property
    def has_unknown_epic_refs(self) -> bool:
        """Check if unknown epic refs condition was detected."""
        return any(c.condition == "unknown_epic_refs" for c in self.conditions)

    @property
    def has_empty_journey(self) -> bool:
        """Check if empty journey condition was detected."""
        return any(c.condition == "empty_journey" for c in self.conditions)
