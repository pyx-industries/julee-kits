"""The messages story orchestration takes and returns.

A request is what a driving adapter hands in and a response is
what it serialises back out, so both are pydantic models. This
is the one package of the bounded context that imports pydantic
(ADR 001).
"""

from typing import Any

from pydantic import BaseModel, Field

from julee_hcd.domain.models.story import Story


class StoryOrchestrationRequest(BaseModel):
    """Request for story orchestration check."""

    story: Story = Field(description="The story to check for orchestration conditions")


class StoryCondition(BaseModel):
    """A detected domain condition for a story."""

    condition: str = Field(description="Condition type identifier")
    story_slug: str = Field(description="The story's slug")
    details: dict[str, Any] = Field(
        default_factory=dict, description="Condition-specific details"
    )


class StoryOrchestrationResponse(BaseModel):
    """Response from story orchestration check."""

    story: Story = Field(description="The checked story")
    conditions: list[StoryCondition] = Field(
        default_factory=list, description="Detected conditions"
    )

    @property
    def has_unknown_persona(self) -> bool:
        """Check if unknown persona condition was detected."""
        return any(c.condition == "unknown_persona" for c in self.conditions)

    @property
    def has_orphan_story(self) -> bool:
        """Check if orphan story condition was detected."""
        return any(c.condition == "orphan_story" for c in self.conditions)
