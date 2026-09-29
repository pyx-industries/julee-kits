"""The messages epic orchestration takes and returns.

A request is what a driving adapter hands in and a response is
what it serialises back out, so both are pydantic models. This
is the one package of the bounded context that imports pydantic
(ADR 001).
"""

from typing import Any

from pydantic import BaseModel, Field

from julee_hcd.domain.models.epic import Epic


class EpicOrchestrationRequest(BaseModel):
    """Request for epic orchestration check."""

    epic: Epic = Field(description="The epic to check for orchestration conditions")


class EpicCondition(BaseModel):
    """A detected domain condition for an epic."""

    condition: str = Field(description="Condition type identifier")
    epic_slug: str = Field(description="The epic's slug")
    details: dict[str, Any] = Field(
        default_factory=dict, description="Condition-specific details"
    )


class EpicOrchestrationResponse(BaseModel):
    """Response from epic orchestration check."""

    epic: Epic = Field(description="The checked epic")
    conditions: list[EpicCondition] = Field(
        default_factory=list, description="Detected conditions"
    )

    @property
    def has_empty_epic(self) -> bool:
        """Check if empty epic condition was detected."""
        return any(c.condition == "empty_epic" for c in self.conditions)

    @property
    def has_unknown_story_refs(self) -> bool:
        """Check if unknown story refs condition was detected."""
        return any(c.condition == "unknown_story_refs" for c in self.conditions)
