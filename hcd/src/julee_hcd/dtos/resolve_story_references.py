"""The messages resolve story references takes and returns.

A request is what a driving adapter hands in and a response is
what it serialises back out, so both are pydantic models. This
is the one package of the bounded context that imports pydantic
(ADR 001).
"""

from pydantic import BaseModel

from julee_hcd.domain.models.epic import Epic
from julee_hcd.domain.models.journey import Journey
from julee_hcd.domain.models.story import Story


class ResolveStoryReferencesRequest(BaseModel):
    """What a story's references are resolved against."""

    story: Story
    stories: tuple[Story, ...] = ()
    epics: tuple[Epic, ...] = ()
    journeys: tuple[Journey, ...] = ()


class ResolveStoryReferencesResponse(BaseModel):
    """Everything that refers to a story."""

    epics: tuple[Epic, ...] = ()
    journeys: tuple[Journey, ...] = ()
    related_stories: tuple[Story, ...] = ()
